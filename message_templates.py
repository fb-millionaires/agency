# -*- coding: utf-8 -*-
# list of agencies
# list of agency services
# response proper


LIST_TEMPLATE = {
    'recipient': {
        'id': None
    },
    'message': {
        'attachment': {
            'type': 'template',
            'payload': {
                'template_type': '',
                'elements': []
            }
        }
    }
}


BUTTON_TEMPLATE = {
    'type': '',
    'title': '',
}


ELEMENT_TEMPLATE = {
    'title': '',
    'image_url': '',
    'subtitle': '',
    'buttons': []
}


AGENCY_LIST_TEMPLATE_HINT = {
    'title': ('Hint: Use your keyboard to type short '
              'queries for quick results.'),
    'image_url': '',
    'subtitle': ('For example, type: renew international passport. '
                 'Remember you can always access this view by tapping the '
                 'menu below. Enjoy!')
}
