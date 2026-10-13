"""Per-command product switches; unrelated runtime configuration is untouched."""
import lines


def validate(values, layer, *, legacy=False):
    schema = lines.catalogue('settings')
    if not isinstance(values, dict):
        raise ValueError('Settings must be an object')
    for key, value in values.items():
        field = schema['keys'].get(key)
        if field is None or layer not in field['layers']:
            raise ValueError('Unknown setting or forbidden layer: ' + key)
        if type(value) is not {'boolean': bool, 'string': str, 'integer': int}[field['type']]:
            raise ValueError('Invalid setting type: ' + key)
        compatible = legacy and key == 'critic.provider' and value == 'codex-subagent'
        if ('choices' in field and value not in field['choices'] and not compatible
                or 'minimum' in field and value < field['minimum']):
            raise ValueError('Invalid setting value: ' + key)
        if key == 'critic.model' and value and not value.strip():
            raise ValueError('Critic model must be empty or a nonblank provenance label')
    return values


def effective(state, user=None):
    line = lines.frozen(state)
    fallback = {'direction_approval': True, 'critic.provider': 'off', 'critic.model': '', 'critic.max_rounds': 1}
    defaults = {**fallback, **(line.get('settings_defaults') or {})} if line else fallback
    result = {key: {'value': value, 'source': 'line' if line else 'legacy'} for key, value in defaults.items()}
    # New memory settings do not rebind an existing Variant or alter legacy switches.
    schema = lines.catalogue('settings')['keys']
    for key in ('samples.max_references', 'samples.frames_per_reference'):
        result.setdefault(key, {'value': schema[key]['default'], 'source': 'release'})
    for layer, values in (('user', user or {}), ('variant', state.get('settings', {}))):
        allowed = values if line else {key: value for key, value in values.items() if key.startswith('samples.')}
        for key, value in validate(allowed, layer, legacy=True).items():
            result[key] = {'value': value, 'source': layer}
    return result
