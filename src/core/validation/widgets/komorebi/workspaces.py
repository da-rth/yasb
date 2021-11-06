DEFAULTS = {
    'label_offline': 'Komorebi Offline',
    'hide_empty_workspaces': False
}

VALIDATION_SCHEMA = {
    'label_offline': {
        'type': 'string',
        'default': DEFAULTS['label_offline']
    },
    'hide_empty_workspaces': {
        'type': 'boolean',
        'default': DEFAULTS['hide_empty_workspaces']
    }
}
