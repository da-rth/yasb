DEFAULTS = {
    'label': "{media[title]} - {media[artist]}",
    'label_alt': "{media[title]} - {media[artist]}",
    'update_interval': 1000,
    'keep_thumbnail_aspect_ratio': False,
    'layout': ["thumbnail", "label", "close"],
    'icons': {
        'shuffle': "\uf074",
        'play': "\uf04b",
        'pause': "\uf04c",
        'repeat_off': "\uf2f9",
        'repeat_track': "\uf2f9 (T)",
        'repeat_list': "\uf2f9 (L)",
        'next': "\uf051",
        'prev': "\uf048",
        'close': "\uf00d"
    }
}

VALIDATION_SCHEMA = {
    'label': {
        'type': 'string',
        'default': DEFAULTS['label']
    },
    'label_alt': {
        'type': 'string',
        'default': DEFAULTS['label_alt']
    },
    'update_interval': {
        'type': 'integer',
        'default': DEFAULTS['update_interval'],
        'min': 0
    },
    'keep_thumbnail_aspect_ratio': {
        'type': 'boolean',
        'default': DEFAULTS['keep_thumbnail_aspect_ratio']
    },
    'layout': {
        'type': 'list',
        'schema': {
            'type': 'string',
            'allowed': ["thumbnail", "label", "close", "prev", "play_pause", "next", "shuffle", "repeat"]
        },
        'default': DEFAULTS['layout']
    },
    'icons': {
        'type': 'dict',
        'schema': {
            'shuffle': {
                'type': 'string',
                'default': DEFAULTS['icons']['shuffle']
            },
            'play': {
                'type': 'string',
                'default': DEFAULTS['icons']['play']
            },
            'pause': {
                'type': 'string',
                'default': DEFAULTS['icons']['pause']
            },
            'repeat_off': {
                'type': 'string',
                'default': DEFAULTS['icons']['repeat_off']
            },
            'repeat_track': {
                'type': 'string',
                'default': DEFAULTS['icons']['repeat_track']
            },
            'repeat_list': {
                'type': 'string',
                'default': DEFAULTS['icons']['repeat_list']
            },
            'next': {
                'type': 'string',
                'default': DEFAULTS['icons']['next']
            },
            'prev': {
                'type': 'string',
                'default': DEFAULTS['icons']['prev']
            },
            'close': {
                'type': 'string',
                'default': DEFAULTS['icons']['close']
            }
        },
        'default': DEFAULTS['icons']
    }
}