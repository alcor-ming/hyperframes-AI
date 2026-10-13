"""Work-local speech candidates; providers never own formal audio or cue adoption."""
from __future__ import annotations

import base64
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from urllib.error import URLError
from urllib.request import Request, build_opener, HTTPRedirectHandler
import uuid
import wave

import explainer
from storage import scoped_path


VERSION = 1
VOLCENGINE_URL = 'https://openspeech.bytedance.com/api/v3/tts/create'
# https://docs.volcengine.com/docs/DoubaoVoice/audio-generation-http?lang=zh
SENSITIVE = {'apikey', 'accesskey', 'secret', 'token', 'authorization', 'password', 'credential'}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def urlopen(request, **kwargs):
    return build_opener(NoRedirect).open(request, **kwargs)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(data):
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode('utf-8')


def configuration(value):
    if not isinstance(value, dict) or set(value) - {'provider', 'model', 'command', 'options', 'anchors', 'key_env', 'versions'}:
        raise ValueError('Invalid TTS configuration fields')
    result = {'provider': 'volcengine', 'model': 'seed-audio-1.0', 'options': {}, 'anchors': {}, **value}
    if result['provider'] not in {'volcengine', 'script'}:
        raise ValueError('TTS provider must be volcengine or script')
    if not isinstance(result['model'], str) or not result['model'].strip():
        raise ValueError('TTS model must be explicit')
    if result['provider'] == 'script':
        if 'model' not in value:
            raise ValueError('Script TTS model must be explicit')
        command = result.get('command')
        if not isinstance(command, list) or not 1 <= len(command) <= 2 or any(not isinstance(v, str) or not v or v.startswith('-') for v in command):
            raise ValueError('Script TTS requires [executable] or [interpreter, script]; options belong in the request')
    elif 'command' in result:
        raise ValueError('A command is only supported by script TTS')
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', result.get('key_env', 'VOLCENGINE_TTS_API_KEY')):
        raise ValueError('Invalid TTS credential environment name')
    if not isinstance(result['options'], dict) or not isinstance(result['anchors'], dict):
        raise ValueError('TTS options and anchors must be objects')
    if any(not re.fullmatch(r'P[0-9]+', k) or not isinstance(v, dict) for k, v in result['anchors'].items()):
        raise ValueError('TTS per-anchor options require P<number> objects')

    def clean(item):
        if isinstance(item, dict):
            for key, child in item.items():
                if any(secret in re.sub('[^a-z]', '', key.lower()) for secret in SENSITIVE):
                    raise ValueError('Pass TTS credentials through environment, never request options')
                clean(child)
        elif isinstance(item, list):
            for child in item:
                clean(child)
    clean(result['options'])
    clean(result['anchors'])
    versions = result.get('versions', {})
    if (not isinstance(versions, dict) or set(versions) - {'tool', 'model'}
            or any(not isinstance(v, str) or not v.strip() for v in versions.values())):
        raise ValueError('TTS versions require nonempty tool/model versions')
    for options in (result['options'], *result['anchors'].values()):
        if 'duration_factor' in options:
            factor = options['duration_factor']
            if type(factor) not in (int, float) or not math.isfinite(factor) or factor <= 0:
                raise ValueError('TTS duration_factor must be finite and positive')
    return result


def segments(text, selected=()):
    """Input already passed through work.script_text(anchors=True)."""
    parts = re.split(r'<!--\s*(P[0-9]+)\s*-->', text)
    if parts[0].strip() or len(parts) == 1:
        raise ValueError('TTS narration needs stable P<number> anchors')
    rows = [{'anchor': parts[i], 'text': parts[i + 1].strip()} for i in range(1, len(parts), 2)]
    if len({row['anchor'] for row in rows}) != len(rows) or any(not row['text'] for row in rows):
        raise ValueError('TTS anchors must be unique and nonempty')
    unknown = set(selected) - {row['anchor'] for row in rows}
    if unknown:
        raise ValueError('Unknown TTS anchors: ' + ', '.join(sorted(unknown)))
    return [row for row in rows if not selected or row['anchor'] in selected]


def wav_info(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_nlink != 1:
        raise ValueError('TTS audio must be an unlinked PCM WAV file')
    try:
        with wave.open(str(path), 'rb') as audio:
            channels, width, rate, frames, codec, _ = audio.getparams()
            if codec != 'NONE' or channels not in (1, 2) or width not in (1, 2, 3, 4) or not 8000 <= rate <= 192000 or frames <= 0:
                raise ValueError('Invalid TTS PCM WAV format')
            expected = frames * channels * width
            if expected > 128 * 1024 * 1024 or len(audio.readframes(frames)) != expected:
                raise ValueError('Truncated or oversized TTS audio')
            return {'duration': frames / rate, 'channels': channels, 'sample_width': width, 'sample_rate': rate}
    except (wave.Error, EOFError) as error:
        raise ValueError('Invalid TTS WAV file') from error


def volcengine(text, model, options, output, key_env):
    allowed = {'instruction', 'speaker', 'speech_rate', 'pitch_rate', 'loudness_rate', 'sample_rate'}
    if set(options) - allowed:
        raise ValueError('Unsupported Volcengine TTS options')
    instruction = options.get('instruction', '')
    if not isinstance(instruction, str) or not isinstance(options.get('speaker', ''), str):
        raise ValueError('TTS instruction and speaker must be strings')
    prompt = (instruction + '\n' + text).strip()
    if not 1 <= len(prompt) <= 3000:
        raise ValueError('Volcengine prompt exceeds 3000 characters; split Script anchors')
    audio_config = {'format': 'wav', 'sample_rate': options.get('sample_rate', 48000)}
    if type(audio_config['sample_rate']) is not int or audio_config['sample_rate'] not in {8000, 16000, 24000, 32000, 40000, 44100, 48000}:
        raise ValueError('Invalid Volcengine sample_rate')
    for key, low, high in [('speech_rate', -50, 100), ('pitch_rate', -12, 12), ('loudness_rate', -50, 100)]:
        value = options.get(key, 0)
        if type(value) is not int or not low <= value <= high:
            raise ValueError('Invalid Volcengine ' + key)
        audio_config[key] = value
    key = os.environ.get(key_env)
    if not key:
        raise ValueError('Missing TTS credential environment: ' + key_env)
    payload = {'model': model, 'text_prompt': prompt, 'audio_config': audio_config}
    if options.get('speaker'):
        payload['references'] = [{'speaker': options['speaker']}]
    request = Request(VOLCENGINE_URL, data=json_bytes(payload), method='POST', headers={
        'Content-Type': 'application/json', 'X-Api-Key': key, 'X-Api-Request-Id': str(uuid.uuid4())})
    try:
        with urlopen(request, timeout=300) as response:
            raw = response.read(64 * 1024 * 1024 + 1)
        if len(raw) > 64 * 1024 * 1024:
            raise ValueError('response too large')
        result = json.loads(raw)
        if not isinstance(result, dict) or result.get('code', 0) not in (0, 20000000):
            raise ValueError('provider error')
        audio = base64.b64decode(result['audio'], validate=True)
    except (URLError, TimeoutError, ValueError, KeyError, TypeError, OSError):
        # Provider bodies and request headers may contain secrets or private text.
        raise ValueError('Volcengine synthesis failed; previous audio is unchanged') from None
    output.write_bytes(audio)


def script_provider(request, command, directory):
    request_path, result_path = directory / 'request.json', directory / 'result.json'
    request_path.write_bytes(json_bytes({**request, 'schema_version': VERSION, 'output': 'audio.wav'}))
    try:
        result = subprocess.run([*command, '--request', str(request_path), '--result', str(result_path)],
                                cwd=directory, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, timeout=300, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise ValueError('TTS script could not complete; previous audio is unchanged') from None
    if result.returncode:
        raise ValueError(f'TTS script failed (exit {result.returncode}); previous audio is unchanged')
    result_path = scoped_path(directory, 'result.json')
    if not result_path.is_file() or result_path.stat().st_nlink != 1:
        raise ValueError('TTS script did not write a regular result.json')
    try:
        result = json.loads(result_path.read_bytes())
    except (ValueError, UnicodeError):
        raise ValueError('Invalid TTS script result JSON') from None
    if (not isinstance(result, dict) or set(result) != {'audio', 'model', 'options'}
            or not isinstance(result.get('audio'), str)):
        raise ValueError('TTS script result requires audio relative path, actual model and options')
    if result['model'] != request['model'] or result['options'] != request['options']:
        raise ValueError('TTS script generated with different model or options')
    return scoped_path(directory, result['audio'])


def generation_basis(config, options):
    basis = {key: config[key] for key in ('provider', 'model')}
    basis['versions'] = config.get('versions', {})
    if config['provider'] == 'script':
        basis['command'] = config['command']
        basis['command_sha256'] = []
        for part in config['command']:
            path = Path(shutil.which(part) or part)
            if not path.is_file():
                raise ValueError('TTS command file is unavailable')
            basis['command_sha256'].append(digest(path.read_bytes()))
    if 'reference_audio' in options:
        value = options['reference_audio']
        if not isinstance(value, str) or not Path(value).is_absolute():
            raise ValueError('TTS reference_audio requires an absolute file path')
        path = Path(value)
        # Reference decoding belongs to the provider; generated output remains PCM WAV.
        if (path.is_symlink() or not path.is_file() or path.stat().st_nlink != 1
                or not 0 < path.stat().st_size <= 128 * 1024 * 1024):
            raise ValueError('TTS reference_audio requires a regular nonempty file up to 128 MiB')
        basis['reference_sha256'] = digest(path.read_bytes())
    return basis


def cached_segment(variant, row, config, basis):
    from component_harness import package_write_lock
    request = {**row, 'basis': basis}
    identity = digest(json_bytes(request))
    parent = scoped_path(variant, 'materials/tts-segments')
    parent.mkdir(parents=True, exist_ok=True)
    with package_write_lock(scoped_path(parent, identity + '.lock')):
        target = scoped_path(parent, identity)
        if not target.exists():
            with tempfile.TemporaryDirectory(prefix='.generating-', dir=parent) as temp:
                directory = Path(temp)
                if config['provider'] == 'volcengine':
                    path = directory / 'audio.wav'
                    volcengine(row['text'], config['model'], row['options'], path, config.get('key_env', 'VOLCENGINE_TTS_API_KEY'))
                else:
                    path = script_provider({'text': row['text'], 'anchor': row['anchor'], 'model': config['model'],
                                            'options': row['options']}, config['command'], directory)
                info = wav_info(path)
                if generation_basis(config, row['options']) != basis:
                    raise ValueError('TTS tool or reference changed during synthesis')
                if path != directory / 'audio.wav':
                    shutil.copyfile(path, directory / 'audio.wav')
                manifest = {'request': request, 'sha256': digest(path.read_bytes()), **info}
                (directory / 'manifest.json').write_bytes(json_bytes(manifest))
                directory.rename(target)
        manifest_path = scoped_path(target, 'manifest.json')
        if manifest_path.stat().st_nlink != 1:
            raise ValueError('Linked TTS segment manifest')
        manifest = json.loads(manifest_path.read_bytes())
        audio = scoped_path(target, 'audio.wav')
        info = wav_info(audio)
        if (manifest.get('request') != request or manifest.get('sha256') != digest(audio.read_bytes())
                or any(manifest.get(k) != v for k, v in info.items())):
            raise ValueError('TTS segment cache changed')
        return audio, identity


def generation_request(rows, config, script_sha256):
    config = configuration(config)
    if (not rows or any(not isinstance(row, dict) or set(row) != {'anchor', 'text'}
                        or not isinstance(row['anchor'], str) or not re.fullmatch(r'P[0-9]+', row['anchor'])
                        or not isinstance(row['text'], str) or not row['text'].strip() for row in rows)
            or len({row['anchor'] for row in rows}) != len(rows)):
        raise ValueError('TTS requires unique nonempty Script anchors')
    if not isinstance(script_sha256, str) or not re.fullmatch(r'[a-f0-9]{64}', script_sha256):
        raise ValueError('TTS requires a Script SHA-256')
    request = {'version': VERSION, 'provider': config['provider'], 'model': config['model'],
               'segments': [{**row, 'options': {**config['options'], **config['anchors'].get(row['anchor'], {})}} for row in rows],
               'script_sha256': script_sha256}
    if config['provider'] == 'script':
        request['command'] = config['command']
    request['generation_basis'] = [generation_basis(config, row['options']) for row in request['segments']]
    return request


def import_batch(variant, rows, config, script_sha256, batch_path):
    """Verify every external result before caching segments and composing a candidate."""
    from component_harness import package_write_lock
    config = configuration(config)
    request = generation_request(rows, config, script_sha256)
    batch_path = Path(batch_path).absolute()
    from windows_runtime import validate_review_path
    validate_review_path(batch_path)
    if not batch_path.is_file() or batch_path.stat().st_nlink != 1:
        raise ValueError('TTS batch requires an unlinked manifest')
    batch = json.loads(batch_path.read_bytes())
    if (not isinstance(batch, dict) or set(batch) != {'version', 'script_sha256', 'segments'}
            or batch['version'] != 1 or batch['script_sha256'] != script_sha256
            or not isinstance(batch['segments'], list) or len(batch['segments']) != len(rows)):
        raise ValueError('TTS batch is incomplete or belongs to a different Script')
    entries = batch['segments']
    if any(not isinstance(entry, dict) or set(entry) != {'anchor', 'text', 'model', 'options', 'basis', 'audio', 'sha256'}
           for entry in entries):
        raise ValueError('Invalid TTS batch result fields')
    if [entry['anchor'] for entry in entries] != [row['anchor'] for row in rows]:
        raise ValueError('TTS batch anchors must exactly match Script order')
    checked = []
    for row, basis, entry in zip(request['segments'], request['generation_basis'], entries):
        if (any(entry[key] != row[key] for key in ('anchor', 'text', 'options'))
                or entry['model'] != config['model'] or entry['basis'] != basis):
            raise ValueError('TTS batch text, model, options or generation basis mismatch')
        audio = scoped_path(batch_path.parent, entry['audio'])
        info = wav_info(audio)
        if digest(audio.read_bytes()) != entry['sha256']:
            raise ValueError('TTS batch audio hash mismatch')
        checked.append((row, basis, entry, audio, info))
    for row, basis, entry, audio, info in checked:
        segment_request = {**row, 'basis': basis}
        identity = digest(json_bytes(segment_request))
        parent = scoped_path(variant, 'materials/tts-segments')
        parent.mkdir(parents=True, exist_ok=True)
        with package_write_lock(scoped_path(parent, identity + '.lock')):
            target = scoped_path(parent, identity)
            if not target.exists():
                with tempfile.TemporaryDirectory(prefix='.importing-', dir=parent) as temporary:
                    stage = Path(temporary)
                    shutil.copyfile(audio, stage / 'audio.wav')
                    if digest((stage / 'audio.wav').read_bytes()) != entry['sha256']:
                        raise ValueError('TTS batch audio changed while copying')
                    manifest = {'request': segment_request, 'sha256': entry['sha256'], **info}
                    (stage / 'manifest.json').write_bytes(json_bytes(manifest))
                    stage.rename(target)
        cached_segment(variant, row, config, basis)
    return generate(variant, rows, config, script_sha256)


def generate(variant, rows, config, script_sha256):
    config = configuration(config)
    request = generation_request(rows, config, script_sha256)
    identity = digest(json_bytes(request))
    parent = scoped_path(variant, 'materials/tts')
    parent.mkdir(parents=True, exist_ok=True)
    target = scoped_path(parent, identity)
    if target.exists():
        return candidate(variant, identity)
    with tempfile.TemporaryDirectory(prefix='.generating-', dir=parent) as temp:
        staging = Path(temp)
        files, entries, offset = {}, [], 0.0
        combined = staging / 'audio.wav'
        with wave.open(str(combined), 'wb') as writer:
            writer.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
            format_key = None
            for row, basis in zip(request['segments'], request['generation_basis']):
                directory = staging / row['anchor']
                directory.mkdir()
                cached, segment_id = cached_segment(variant, row, config, basis)
                path = directory / 'audio.wav'
                shutil.copyfile(cached, path)
                info = wav_info(path)
                key = tuple(info[k] for k in ('channels', 'sample_width', 'sample_rate'))
                if format_key is None:
                    format_key = key
                    writer.setparams((*key, 0, 'NONE', 'not compressed'))
                if key != format_key:
                    raise ValueError('TTS segments require the same PCM format')
                with wave.open(str(path), 'rb') as reader:
                    writer.writeframes(reader.readframes(reader.getnframes()))
                entries.append({'anchor': row['anchor'], 'start': offset, 'end': offset + info['duration'],
                                'text_sha256': digest(row['text'].encode()), 'segment_id': segment_id})
                offset += info['duration']
                files[row['anchor'] + '/audio.wav'] = digest(path.read_bytes())
        info = wav_info(combined)
        files['audio.wav'] = digest(combined.read_bytes())
        manifest = {'id': identity, 'request': request, 'segments': entries, 'files': files,
                    **info, 'status': 'generated', 'alignment': None}
        (staging / 'manifest.json').write_bytes(json_bytes(manifest))
        # Rename only a completed candidate; never replace an existing candidate.
        if target.exists():
            return candidate(variant, identity)
        staging.rename(target)
    return {**manifest, 'path': str(target)}


def candidate(variant, identity):
    if not re.fullmatch(r'[a-f0-9]{64}', identity):
        raise ValueError('TTS candidate ID must be its full SHA-256')
    directory = scoped_path(variant, 'materials/tts/' + identity)
    path = scoped_path(directory, 'manifest.json')
    if path.stat().st_nlink != 1:
        raise ValueError('Linked TTS manifests are not supported')
    data = json.loads(path.read_bytes())
    if (not isinstance(data, dict) or data.get('id') != identity
            or digest(json_bytes(data.get('request'))) != identity
            or not isinstance(data.get('files'), dict) or 'audio.wav' not in data['files']
            or data.get('status') != 'generated' or data.get('alignment') is not None):
        raise ValueError('TTS candidate manifest changed')
    expected = {'audio.wav'}
    if 'generation_basis' in data['request']:
        expected.update(row['anchor'] + '/audio.wav' for row in data['request']['segments'])
    if set(data['files']) != expected:
        raise ValueError('TTS candidate segment files changed')
    for name, sha in data['files'].items():
        path = scoped_path(directory, name)
        wav_info(path)
        if digest(path.read_bytes()) != sha:
            raise ValueError('TTS candidate audio changed')
    audio = scoped_path(directory, 'audio.wav')
    info = wav_info(audio)
    if digest(audio.read_bytes()) != data['files']['audio.wav'] or any(data.get(k) != v for k, v in info.items()):
        raise ValueError('TTS candidate audio changed')
    return {**data, 'path': str(directory)}


def aligned_sections(text, rows, alignment_bytes, duration):
    cues = explainer.validate_cues(explainer.build_cues(text, alignment_bytes))
    if (any(c['char'].isalnum() and (not c['aligned'] or c['end'] <= c['start']) for c in cues['characters'])
            or any(any(c.isalnum() for c in m['script'] + m['alignment']) for m in cues['mismatches'])):
        raise ValueError('Formal TTS requires aligned spoken characters; provider-native timing is missing or does not match the Script')
    if any(c['aligned'] and c['end'] > duration + 0.02 for c in cues['characters']):
        raise ValueError('Alignment extends beyond candidate audio')
    sections, offset = [], 0
    for row in rows:
        start = text.find(row['text'], offset)
        if start < 0:
            raise ValueError('TTS anchors differ from current narration')
        span = cues['characters'][start:start + len(row['text'])]
        timed = [c for c in span if c['aligned']]
        if not timed:
            raise ValueError('TTS anchor has no measured timing')
        sections.append({'anchor': row['anchor'], 'start': timed[0]['start'], 'end': timed[-1]['end']})
        offset = start + len(row['text'])
    return cues, {'sections': sections, 'characters': cues['characters']}
