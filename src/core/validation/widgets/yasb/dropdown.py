DEFAULTS = {
    'items': {},
    'update_interval': 5000,
    'callbacks': {
        'on_left': "do_nothing",
        'on_middle': "do_nothing",
        'on_right': "do_nothing"
    }
}

VALIDATION_SCHEMA = {
    'items': {
        'type': 'dict',
        'keyschema': {'type': 'string'},
        'valueschema': {'type': 'string'},
        'default': DEFAULTS['items']
    },
    'update_interval': {
        'type': 'integer',
        'default': DEFAULTS['update_interval'],
        'min': 0,
        'max': 60000
    },
    'callbacks': {
        'type': 'dict',
        'schema': {
            'on_left': {
                'type': 'string',
                'nullable': True,
                'default': DEFAULTS['callbacks']['on_left'],
            },
            'on_middle': {
                'type': 'string',
                'nullable': True,
                'default': DEFAULTS['callbacks']['on_middle'],
            },
            'on_right': {
                'type': 'string',
                'nullable': True,
                'default': DEFAULTS['callbacks']['on_right']
            }
        },
        'default': DEFAULTS['callbacks']
    }
}
