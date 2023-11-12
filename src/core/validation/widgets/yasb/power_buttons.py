DEFAULTS = {
    'label': "power",
    'layout': ["shutDown", "restart", "lock"]
}

VALIDATION_SCHEMA = {
    'label': {
        'type': 'string',
        'default': DEFAULTS['label']
    },
    'layout': {
        'type': 'list',
        'schema': {
            'type': 'string',
            'allowed': ["shutDown", "restart", "lock"]
        },
        'default': DEFAULTS['layout']
    },
}