"""Per-command product switches; unrelated runtime configuration is untouched."""
import lines


def validate(values, layer):
    schema = lines.catalogue('settings')
    if not isinstance(values, dict):
        raise ValueError('Settings must be an object')
    for key, value in values.items():
        field = schema['keys'].get(key)
        if field is None or layer not in field['layers']:
            raise ValueError('Unknown setting or forbidden layer: ' + key)
        if type(value) is not {'boolean': bool, 'string': str, 'integer': int}[field['type']]:
            raise ValueError('Invalid setting type: ' + key)
        if 'choices' in field and value not in field['choices'] or 'minimum' in field and value < field['minimum']:
            raise ValueError('Invalid setting value: ' + key)
        if key == 'critic.model' and schema['critic_models'].get(value, {}).get('image_input') is not True:
            raise ValueError('Critic model must declare image input capability')
    return values


def effective(state, user=None):
    line = lines.frozen(state)
    defaults = line['defaults'] if line else {'direction_approval': True, 'critic.provider': 'off', 'critic.model': 'gpt-6.1-sol', 'critic.max_rounds': 1}
    result = {key: {'value': value, 'source': 'line' if line else 'legacy'} for key, value in defaults.items()}
    # A user switch cannot silently migrate an older Variant.
    if line:
        for layer, values in (('user', user or {}), ('variant', state.get('settings', {}))):
            for key, value in validate(values, layer).items():
                result[key] = {'value': value, 'source': layer}
    return result
