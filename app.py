# -*- coding: utf-8 -*-
import json
import os
import sys

from flask import Flask, jsonify, request
from pymongo import MongoClient
import requests

import constants
import message_parser
import utils


def connect():
    """Substitute the 5 pieces of information you got when creating
    the Mongo DB Database (underlined in red in the screenshots)
    """
    # REMEMBER TO SAVE USERNAME AND PASSWORD IN AN ENVIRONMENT VARIABLE
    connection = MongoClient('ds143030.mlab.com', 43030)
    handle = connection['agency']
    handle.authenticate('agency_user', 'notsecret')
    return handle


app = Flask(__name__)
handle = connect()


@app.route('/', methods=['GET'])
def verify():
    """when the endpoint is registered as a webhook, it must echo back
    the 'hub.challenge' value it receives in the query arguments
    """
    is_subscribe = request.args.get('hub.mode') == 'subscribe'
    challenge = request.args.get('hub.challenge')
    is_valid_verify_token = (
        request.args.get('hub.verify_token') == os.environ['VERIFY_TOKEN']
    )
    if is_subscribe and challenge:
        if not is_valid_verify_token:
            return 'Verification token mismatch', 403

        return challenge, 200
    return "Don't know how to deal with this yet", 200


@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events
    data = request.get_json()

    # you may not want to log every incoming message in production
    # but it's good for testing
    log(data)
    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                # the facebook ID of the person sending you the message
                sender_id = messaging_event['sender']['id']

                # the recipient's ID, actually Agency's page facebook ID
                # recipient_id = messaging_event['recipient']['id']

                # someone sent us a message
                if 'message' in messaging_event:
                    message = messaging_event.get('message')
                    template = message_parser.text_parser(sender_id, message)

                    for packet in template:
                        send_message(sender_id, packet)

                # delivery confirmation
                if messaging_event.get('delivery'):
                    pass

                # delivery confirmation
                if messaging_event.get('optin'):
                    pass

                # user clicked/tapped 'postback' button in earlier message
                if messaging_event.get('postback'):
                    # send typing indicator to acknowledge receipt while we
                    # process
                    payload = messaging_event.get('postback').get('payload')

                    if (payload == 'GET_STARTED_PAYLOAD'):
                        message = message_parser.prepare_text_message(
                            sender_id,
                            'Here are a list of government agencies we '
                            'provide services for:'
                        )
                        send_message(sender_id, message)
                        # get specific fields from database
                        # agencies = query to db
                        template_elements = (
                            message_parser.prepare_agencies_list_elements()
                        )
                        template = message_parser.create_agencies_list_template(
                            sender_id, template_elements)
                        send_message(sender_id, template)
                    else:
                        postback_components = utils.deconstruct_postback(
                            payload)
                        # the first index indicates level (i.e. Agency or Service)
                        # the last indicates what information
                        if postback_components['prefix'] == 'AGENCY':
                            template = handle_agency_level_requests(
                                sender_id, postback_components)
                            for section in template:
                                send_message(sender_id, section)
                        elif postback_components['prefix'] == 'SERVICE':
                            log(postback_components)
                            template = handle_service_level_requests(
                                sender_id, postback_components)
                            for section in template:
                                send_message(sender_id, section)
    return 'ok', 200


def handle_agency_level_requests(sender_id, postback_components):
    """Deals with all requests at the agency level

    Args:
        postback_components -- a dictionary of postback broken down
                               into component parts
    Returns:
        proper template
    """
    template = []
    agency_name = postback_components['search_param1'].replace('_', ' ')
    agency = utils.get_one_agency_from_db(agency_name.lower())
    if not agency:
        message_text = "Oops, sorry we don't have a record for that agency"
        template.append(
            message_parser.prepare_text_message(sender_id, message_text))
        return template

    if postback_components['suffix'] == constants.DETAIL:
        template = message_parser.get_agency_detail(sender_id, agency)
    elif postback_components['suffix'] == constants.OFFICES:
        template = message_parser.get_show_location_template(
            sender_id, agency)
        # save to db a show_location to sender_id link
        lrh_table = handle.location_request_history
        data = {
            'sender_id': sender_id,
            'agency_name': agency_name
        }
        lrh_table.insert_one(data)
    elif postback_components['suffix'] == constants.CONTACT:
        template = message_parser.get_contact(sender_id, agency)
    elif postback_components['suffix'] == constants.SERVICES:
        service_name = postback_components['search_param2']
        template = message_parser.get_service_detail_view(
            sender_id, agency, service_name)
    return template


def handle_service_level_requests(sender_id, postback_components):
    """Handles all requests that begin with Service
    Args:
        sender_id: the ID of the facebook user making the request
        postback_components: a dictionary of postback broken down
                             into component parts
                             prefix - 'SERVICE'
                             search_param1 - type of service
                             search_param2 - target service item
                             suffix - 'agency_name'
    Returns:
        a text message template
    """
    message_texts = []
    service_type = postback_components['search_param1'].replace(
        '_', ' ').lower()
    query = postback_components['search_param2'].lower()

    # get agency
    agency_name = postback_components['suffix'].replace('_', ' ').lower()
    agency = utils.get_one_agency_from_db(agency_name)
    # get info: for db that would be query agency table for an agency with
    # a particular service and name of service
    # for now
    # get service
    service = utils.get_specific_service(agency['services'], service_type)
    result = service[query]

    if query == 'fee':
        message_texts.append(
            '{service_type} costs {amount} {currency}.'.format(
                service_type=service_type.capitalize(),
                amount=result['amount'],
                currency=result['currency']
            )
        )
    elif query == 'validity_period':
        type_suffix = 's' if result['duration'] > 1 else ''
        message_texts.append(
            '{service_type} is valid for {duration} '
            '{type}{type_suffix}.'.format(
                service_type=service_type.capitalize(),
                duration=result['duration'],
                type=result['type'],
                type_suffix=type_suffix,
            )
        )
    else:
        # for now we consider other things to be in form of lists
        message_texts.append(utils.get_service_requests_start_message(
            query, agency_name, service_type))
        for each in result:
            message_texts.append(each)

    template = []
    for message_text in message_texts:
        template.append(
            message_parser.prepare_text_message(sender_id, message_text))

    return template


def send_message(recipient_id, message):
    """Sends message to facebook messenges api

    Args:
        recipient_id -- int
        message -- a dictionary
    """
    log('sending message to {recipient}: {text}'.format(
        recipient=recipient_id,
        text=message
    ))
    params = {
        'access_token': os.environ['PAGE_ACCESS_TOKEN']
    }
    headers = {
        'Content-Type': 'application/json'
    }
    data = json.dumps(message)
    r = requests.post(
        'https://graph.facebook.com/v2.6/me/messages',
        params=params,
        headers=headers,
        data=data
    )
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):
    """Simple wrapper for loggin to stdout on heroku"""
    print str(message)
    sys.stdout.flush()


def home_page():
    test_data = [x for x in handle.tests.find(
        {},
        {"name": True, "content": True, "_id": False, "requirements": True}
    )]
    return jsonify(results=test_data)


def decode_message(message):
    """Detects the type of message and initiates proper reply"""
    pass


if __name__ == '__main__':
    app.run(debug=True)
