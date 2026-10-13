"""Production workflow switches and stage-scoped guidance selection."""
from copy import deepcopy

DEFAULTS = {'human_confirmation': {'script': True, 'plan': True, 'draft': True},
            'draft_review': {'enabled': True}}
STAGES = ('script', 'research', 'optimize', 'plan', 'draft', 'export')


def validate(value, layer):
    if not isinstance(value, dict) or set(value) - set(DEFAULTS):
        raise ValueError('Unknown workflow field')
    for group, fields in value.items():
        if not isinstance(fields, dict) or set(fields) - set(DEFAULTS[group]):
            raise ValueError('Unknown workflow field: ' + group)
        for key, setting in fields.items():
            if type(setting) is not bool:
                raise ValueError('Workflow switches require booleans')
            if layer == 'variant' and group == 'human_confirmation' and key == 'script':
                raise ValueError('Shared Script confirmation cannot be changed by a Variant')
    return value


def resolve(work, variant=None):
    values = deepcopy(DEFAULTS)
    sources = {group + '.' + key: 'default' for group, fields in values.items() for key in fields}
    for layer, overrides in (('series', work.get('series_workflow', {})),
                             ('work', work.get('workflow_settings', {})),
                             ('variant', (variant or {}).get('workflow_settings', {}))):
        for group, fields in validate(overrides, layer).items():
            values[group].update(fields)
            sources.update({group + '.' + key: layer for key in fields})
    return {'values': values, 'sources': sources}


def recipes(card, stage, series=None, explicit=None):
    if stage not in STAGES:
        raise ValueError('Unknown workflow stage')
    selected = list(card.get('stages', {}).get(stage, []))
    for layers in (series or {}, explicit or {}):
        if not isinstance(layers, dict) or set(layers) - set(STAGES):
            raise ValueError('Unknown stage recipe')
        for paths in layers.values():
            if (not isinstance(paths, list) or any(not isinstance(p, str) or not p.strip()
                                                  or '\\' in p or p.startswith('/') or '..' in p.split('/')
                                                  for p in paths)):
                raise ValueError('Stage recipes require explicit relative file paths')
        if stage in layers:
            selected = layers[stage]
    return list(dict.fromkeys(selected))
