DEFAULTS = {
    'label': "Empty Custom Widget",
    'label_alt': "[Empty Custom Widget]",
    'label_max_length': None,
    'class_name': "custom-widget",
    'exec_options': {
        'run_cmd': None,
        'run_once': False,
        'run_interval': 0,
        'return_format': "json",
        'return_encoding': "utf-8"
    },
    'callbacks': {
        'on_left': "exec explorer.exe",
        'on_middle': "do_nothing",
        'on_right': "do_nothing",
    }
}


VALIDATION_SCHEMA = {
    'label': {
        'type': 'string',
        'required': True
    },
    'label_alt': {
        'type': 'string',
        'default': True
    },
    'class_name': {
        'type': 'string',
        'required': True,
    },
    'label_max_length': {
        'type': 'integer',
        'nullable': True,
        'default': DEFAULTS['label_max_length'],
        'min': 1,
    },
    'exec_options': {
        'type': 'dict',
        'required': False,
    },
    'callbacks': {
        'type': 'dict',
        'schema': {
            'on_left': {
                'type': 'string',
                'default': DEFAULTS['callbacks']['on_left'],
            },
            'on_middle': {
                'type': 'string',
                'default': DEFAULTS['callbacks']['on_middle'],
            },
            'on_right': {
                'type': 'string',
                'default': DEFAULTS['callbacks']['on_right']
            }
        },
        'default': DEFAULTS['callbacks']
    }
}
