BAR_DEFAULTS = {
    'enabled': True,
    'screens': ['*'],
    'class_name': 'yasb-bar',
    'alignment': {'position': 'top', 'center': False},
    'window_flags': {'always_on_top': False, 'windows_app_bar': False},
    'dimensions': {'width': '100%', 'height': 30},
    'offset': {'x': 0, 'y': 0},
    'widgets': {'left': [], 'center': [], 'right': []}
}

BAR_SCHEMA = {
    'type': 'dict',
    'required': True,
    'schema': {
        'enabled': {
            'type': 'boolean',
            'required': True,
            'default': BAR_DEFAULTS['enabled']
        },
        'screens': {
            'type': 'list',
            'schema': {
                'type': 'string'
            },
            'default': BAR_DEFAULTS['screens']
        },
        'class_name': {
            'type': 'string',
            'default': BAR_DEFAULTS['class_name']
        },
        'alignment': {
            'type': 'dict',
            'schema': {
                'position': {
                    'type': 'string',
                    'allowed': ['top', 'bottom'],
                    'default': BAR_DEFAULTS['alignment']['position']
                },
                'center': {
                    'type': 'boolean',
                    'default': BAR_DEFAULTS['alignment']['center']
                }
            },
            'default': BAR_DEFAULTS['alignment']
        },
        'window_flags': {
            'type': 'dict',
            'schema': {
                'always_on_top': {
                    'type': 'boolean',
                    'default':  BAR_DEFAULTS['window_flags']['always_on_top']
                },
                'windows_app_bar': {
                    'type': 'boolean',
                    'default': BAR_DEFAULTS['window_flags']['windows_app_bar']
                }
            },
            'default': BAR_DEFAULTS['window_flags']
        },
        'dimensions': {
            'type': 'dict',
            'schema': {
                'width': {
                    'anyof': [
                        {'type': 'string', 'minlength': 2, 'maxlength': 4, 'regex': '\d+%'},
                        {'type': 'integer', 'min': 0}
                    ],
                    'default': BAR_DEFAULTS['dimensions']['width']
                },
                'height': {
                    'type': 'integer',
                    'min': 0,
                    'default': BAR_DEFAULTS['dimensions']['height']
                }
            },
            'default': BAR_DEFAULTS['dimensions']
        },
        'offset': {
            'type': 'dict',
            'schema': {
                'x': {
                    'type': 'integer',
                    'min': 0,
                    'default': BAR_DEFAULTS['offset']['x']
                },
                'y': {
                    'type': 'integer',
                    'min': 0,
                    'default': BAR_DEFAULTS['offset']['y']
                }
            },
            'default': BAR_DEFAULTS['offset']
        },
        'widgets': {
            'type': 'dict',
            'schema': {
                'left': {
                    'type': 'list',
                    'schema': {
                        'type': 'string'
                    },
                    'default': BAR_DEFAULTS['widgets']['left']
                },
                'center': {
                    'type': 'list',
                    'schema': {
                        'type': 'string'
                    },
                    'default': BAR_DEFAULTS['widgets']['center']
                },
                'right': {
                    'type': 'list',
                    'schema': {
                        'type': 'string'
                    },
                    'default': BAR_DEFAULTS['widgets']['right']
                }
            },
            'default': BAR_DEFAULTS['widgets']
        }
    },
    'default': BAR_DEFAULTS
}