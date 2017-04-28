# -*- coding: utf-8 -*-
import os

import googlemaps
from pymongo import MongoClient

import constants


def connect():
    """Substitute the 5 pieces of information you got when creating
    the Mongo DB Database (underlined in red in the screenshots)
    """
    # REMEMBER TO SAVE USERNAME AND PASSWORD IN AN ENVIRONMENT VARIABLE
    connection = MongoClient(os.environ['DB_HOST'], int(os.environ['DB_PORT']))
    handle = connection[os.environ['DB_NAME']]
    handle.authenticate(os.environ['DB_USER'], os.environ['DB_PASSWORD'])
    return handle


handle = connect()


def get_one_agency_from_db(agency_name):
    agency_table = handle.agencies
    agency = agency_table.find_one({'name': agency_name})
    return agency


def get_type_and_target_payload(message_payload):
    """Returns the type of the message and the appropriate message
    the external caller should process

    Args:
        message_payload -- this contains the content of
                           data['entry']['messaging']['message']
    Returns:
        message_type -- string
        output -- I can't guarantee the return type. this depends on the type
        For text -- string;
            coordinates -- dictionary;
    """
    message_type = ''
    payload = None
    if 'text' in message_payload:
        message_type = 'text'
        request_text = message_payload.get('text')
        payload = request_text
    elif 'attachments' in message_payload:
        attachment = message_payload['attachments'][0]
        if ('payload' in attachment and
                'coordinates' in attachment['payload']):
            message_type = 'coordinates'
            coordinates = attachment['payload']['coordinates']
            coordinates['lng'] = coordinates['long']
            del coordinates['long']
            payload = coordinates
    return message_type, payload


def get_closest_offices(origin_location, agency_name):
    """Uses the google Places API to query google for the closest offices
    to the user.
    Simple algorithm:
        - Query db for all the offices
        - Get the distance between the user and the offices saving result in
          a list
        - Sort the list
        - Get the average of the list
        - Return only offices less or equal to that average
    """
    agency = get_one_agency_from_db(agency_name)
    offices = agency.get(constants.OFFICES.lower())
    gmaps = googlemaps.Client(key=os.environ['GOOGLE_CLIENT_KEY'])
    office_locations = [
        office['location'] for office in offices if office['location']['lat'] != '' or office['location']['lng'] != ''
    ]
    distance_matrix = gmaps.distance_matrix(
        origins=origin_location,
        destinations=office_locations,
        mode='driving',
    )

    # get values of duration for each route
    rows = distance_matrix['rows'][0]['elements']
    duration = [
        row['duration']['value'] for row in rows if row['status'] == 'OK'
    ]

    average = sum(duration) / len(duration)

    # prepare result
    result = []
    for count, row in enumerate(rows):
        if row['status'] == 'OK':
            if row['duration']['value'] <= average:
                temp = {
                    'address': distance_matrix['destination_addresses'][count],
                    'distance': row['distance']['text'],
                    'duration': row['duration']['text']
                }
                result.append(temp)

    if not result:
        result.append('Sorry, I found nothing.')

    return result


def construct_postback(prefix, suffix, payload):
    """Constructs a postback that could be used to get specific info

    Args:
        prefix -- the first section of postback before underscore
        suffix -- the last section of postback indicating what information
                  is being requested
        payload -- a list of items to search for on the return trip
    """
    # first replace spaces in payload fields with dash -
    formatted_payload = []
    for field in payload:
        formatted_payload.append('_'.join(field.split(' ')))
    # Here join the payload fields together
    combined_payload_fields = '-'.join(formatted_payload)
    postback = '{prefix}-{combined_payload_fields}-{suffix}'.format(
        prefix=prefix,
        combined_payload_fields=combined_payload_fields,
        suffix=suffix
    )
    return postback.upper()


def deconstruct_postback(postback):
    """Return a dictionary containing the different components of a postback
    Args:
        postback -- string
    """
    result = {}
    components = postback.split('-')
    result['prefix'] = components.pop(0)
    result['suffix'] = components.pop()
    result['search_param1'] = components.pop(0)
    if components:
        result['search_param2'] = components.pop()
    return result


def get_specific_service(services, service_type):
    """Finds target service
    Args:
        services: a list of services search for through
        service_type: a string identity for the service
                      (name is a better name, no pun intended)
    Returns the service dictionary of interest
    """
    for service in services:
        if service['type'] == service_type:
            return service
    return {}


def get_service_requests_start_message(query, agency_name, service_type):
    """Returns a dictionary mapping of items in services to
    appropriate start message
    """
    service_items_to_start_message_mapping = {
        'requirements': (
            'The {agency_name} requires the following items '
            'for {service_type}'.format(
                agency_name=agency_name.title(),
                service_type=service_type
            )
        )
    }
    return service_items_to_start_message_mapping[query]


def get_agencies_from_db():
    """Call db for fields: short_name, logo, name"""
    agency_doc = handle.agencies
    agencies = agency_doc.find(
        {},
        {'short_name': 1, 'logo': 1, 'name': 1, '_id': 0}
    )
    return agencies
