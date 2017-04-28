AGENCIES = [
    {
        'id': 1,
        'short_name': 'NIC',
        'name': 'Nigeria Immigration Service',
        'logo': 'http://res.cloudinary.com/andela-troupon/image/upload/v1493017806/nis-logo_ulngmv.png',
        'detail_postback': 'AGENCY_NIGERIA_IMMIGRATION_SERVICE_DETAIL',
        'offices': [
            {
                'address': '9 Obafemi Awolowo Way, Ikeja, Lagos',
                'location': {
                    'lat': '6.6173151',
                    'lng': '3.3565472'
                },
                'type': 'Head Office',
                'img': ''
            },
            {
                'address': 'LCDA Secretariat, Ayobo Road, Ipaja, Lagos',
                'location': {
                    'lat': '6.6089324',
                    'lng': '3.2575533'
                },
                'type': 'Application Center',
                'img': ''
            }
        ],
        'services': [
            {
                'type': 'new international passport',
                'postback_id': 'NEW_DRIVERS_LICENSE',
                'img': '',
                'fee': {
                    'amount': 20000,
                    'currency': 'naira',
                },
                'validity_period': {
                    'duration': 10,
                    'type': 'year'
                },
                'requirements': [
                    '2 passport photographs',
                    'Completed application form',
                    'Birth Certificate',
                ],
                'detail_view': ['fee', 'validity_period', 'requirements']
            },
            {
                'type': 'renew international passport',
                'postback_id': 'NEW_DRIVERS_LICENSE',
                'img': '',
                'fee': {
                    'amount': 200000,
                    'currency': 'naira',
                },
                'validity_period': {
                    'duration': 10,
                    'type': 'year'
                },
                'requirements': [
                    '2 passport photographs',
                    'Completed application form',
                    'Birth Certificate',
                ],
                'detail_view': ['fee', 'validity_period', 'requirements']
            }
        ],
        'website': 'https://immigration.gov.ng/',
        'contact': {
            'phone': ['+234-9-6726457'],
            'fax': ['+234-9-5230637'],
            'email': ['info@nimc.gov.ng']
        }
    },
    {
        'id': 2,
        'short_name': 'FRSC',
        'name': 'Federal Road Safety Corps',
        'logo': 'http://res.cloudinary.com/andela-troupon/image/upload/v1493018773/frsc-logo_s9cn5u.png',
        'detail_postback': 'AGENCY_FEDERAL_ROAD_SAFETY_CORPS_DETAIL',
        'offices': [
            {
                'address': '9 Obafemi Awolowo Way, Ikeja, Lagos',
                'location': {
                    'lat': '6.6173151',
                    'lng': '3.3565472'
                },
                'type': 'Head Office',
                'img': ''
            },
            {
                'address': 'LCDA Secretariat, Ayobo Road, Ipaja, Lagos',
                'location': {
                    'lat': '6.6089324',
                    'lng': '3.2575533'
                },
                'type': 'Application Center',
                'img': ''
            }
        ],
        'services': [
            {
                'type': ' new drivers license',
                'postback_id': 'NEW_DRIVERS_LICENSE',
                'img': '',
                'fee': {
                    'amount': 200000,
                    'currency': 'naira',
                },
                'validity_period': {
                    'duration': 10,
                    'type': 'year'
                },
                'requirements': [
                    '2 passport photographs',
                    'Completed application form',
                    'Birth Certificate',
                ],
                'detail_view': ['fee', 'validity_period', 'requirements']
            },
            {
                'type': 'renew drivers license',
                'postback_id': 'RENEW_DRIVERS_LICENSE',
                'img': '',
                'fee': {
                    'amount': 200000,
                    'currency': 'naira',
                },
                'validity_period': {
                    'duration': 10,
                    'type': 'year'
                },
                'requirements': [
                    '2 passport photographs',
                    'Completed application form',
                    'Birth Certificate',
                ],
                'detail_view': ['fee', 'validity_period', 'requirements']
            }
        ],
        'website': 'https://frsc.gov.ng/',
        'contact': {
            'phone': ['+234-9-6726457'],
            'fax': ['+234-9-5230637'],
            'email': ['info@nimc.gov.ng']
        }
    }
]
