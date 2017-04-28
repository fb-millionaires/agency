# -*- coding: utf-8 -*-
import copy

import app
import constants
import message_templates
import utils


def prepare_agencies_list_elements():
    """Creates valid generic template elements for each agency in db"""
    elements = []
    agency_to_element_field_mapping = {
        'title': 'short_name',
        'image_url': 'logo',
        'subtitle': 'name',
    }
    agencies = utils.get_agencies_from_db()
    for agency in agencies:
        element = copy.deepcopy(message_templates.ELEMENT_TEMPLATE)
        for element_field, agency_field in agency_to_element_field_mapping.iteritems():
            element[element_field] = agency[agency_field]

        # create button to be used to postback the server for more information
        # on the agency
        postback = utils.construct_postback(
            'agency', 'detail', [agency['name']])
        button = copy.deepcopy(message_templates.BUTTON_TEMPLATE)
        button['type'] = 'postback'
        button['title'] = 'See more'
        button['payload'] = postback
        element['buttons'].append(button)

        elements.append(element)
    return elements


def create_agencies_list_template(recipient_id, elements):
    """Returns a template with supplied elements attached"""
    template = copy.deepcopy(message_templates.LIST_TEMPLATE)
    template['recipient']['id'] = recipient_id
    template['message']['attachment']['payload']['template_type'] = 'generic'
    elements.append(utils.get_hint_element())
    template['message']['attachment']['payload']['elements'] = elements
    return template


def create_list_template(recipient_id, elements, buttons):
    """Returns a list template for detail view"""
    template = copy.deepcopy(message_templates.LIST_TEMPLATE)
    template['recipient']['id'] = recipient_id
    payload_section = template['message']['attachment']['payload']
    payload_section['template_type'] = 'list'
    payload_section['top_element_style'] = 'compact'
    template['message']['attachment']['payload']['elements'] = elements
    template['message']['attachment']['payload']['buttons'] = buttons
    return template


def get_agency_detail(recipient_id, agency):
    """Returns a list of list templates for the agency detail view"""
    # query db for agency with this name
    template = []
    elements = []
    buttons = []
    # get all services
    for service in agency['services']:
        element = copy.deepcopy(message_templates.ELEMENT_TEMPLATE)
        element['title'] = service['type'].title()
        element['image_url'] = service.get('img') or constants.FALLBACK_IMAGE

        # create button to be used to postback the server for more information
        # on the agency
        postback = utils.construct_postback(
            'agency', 'services', [agency['name'], service['type']])
        button = copy.deepcopy(message_templates.BUTTON_TEMPLATE)
        button['type'] = 'postback'
        button['title'] = 'Learn more'
        button['payload'] = postback
        element['buttons'].append(button)

        elements.append(element)

    # get closest office
    element = copy.deepcopy(message_templates.ELEMENT_TEMPLATE)
    element['title'] = 'Get the closest offices to your location'
    element['image_url'] = constants.DEFAULT_BUILDING_IMG

    button = copy.deepcopy(message_templates.BUTTON_TEMPLATE)
    button['type'] = 'postback'
    button['title'] = 'Request'
    button['payload'] = utils.construct_postback(
        'agency', 'offices', [agency['name']])

    element['buttons'].append(button)
    elements.append(element)

    # get contact
    element = copy.deepcopy(message_templates.ELEMENT_TEMPLATE)
    element['title'] = 'Contact Us'
    element['image_url'] = constants.CONTACT_IMAGE

    button = copy.deepcopy(message_templates.BUTTON_TEMPLATE)
    button['type'] = 'postback'
    button['title'] = 'Get contact info'
    button['payload'] = utils.construct_postback(
        'agency', 'contact', [agency['name']])

    element['buttons'].append(button)
    elements.append(element)

    # get website
    button = copy.deepcopy(message_templates.BUTTON_TEMPLATE)
    button['type'] = 'web_url'
    button['title'] = 'View Website'
    button['url'] = agency['website']
    buttons.append(button)

    template.append(create_list_template(recipient_id, elements, buttons))
    return template


def get_service_detail_view(recipient_id, agency, service_name):
    """Returns a list of questions that deal with information available
    for a service
    postback format: service_{agency_name}_{service_type}_{component}
    sample postback:
        SERVICE_NEW_INTERNATIONAL_PASSPORT_FEE_NIGERIA_IMMIGRATION_SERVICE_FEE
    """
    template = []
    buttons = []
    prefix = 'service'
    suffix = agency['name'].replace(' ', '_')
    service_type = service_name.replace('_', ' ').lower()

    # get the detail_view from the target service in the agency of interest
    service = utils.get_specific_service(agency['services'], service_type)

    for item in service['detail_view']:
        postback = utils.construct_postback(
            prefix, suffix, [service_type, item])
        buttons.append({
            'type': 'postback',
            'title': item.replace('_', ' ').title(),
            'payload': postback
        })
    # TODO: since button template can't take more than three buttons,
    # this would be a great place to split them to groups at most three
    template.append(prepare_service_detail_template(recipient_id, buttons))
    return template


def prepare_service_detail_template(recipient_id, buttons):
    """Returns a button template for the service detail view"""
    template = copy.deepcopy(message_templates.LIST_TEMPLATE)
    template['recipient']['id'] = recipient_id
    payload_section = template['message']['attachment']['payload']
    del payload_section['elements']
    payload_section['template_type'] = 'button'
    payload_section['text'] = 'Tap to get more information'
    payload_section['buttons'] = buttons
    return template


def get_contact(recipient_id, agency):
    """Return the contact information of an agency"""
    template = []
    for key, value in agency[constants.CONTACT.lower()].iteritems():
        if value:
            str_values = ', '.join(value)
            message_text = '{key}:\n {values}'.format(
                key=key, values=str_values)
            template.append(prepare_text_message(recipient_id, message_text))

    # aplogize if we found nothing
    if template:
        template.append(
            "Sorry, I don't have contact details for {0}".format(
                agency['name'])
        )
    else:
        end_message = ('Remember the menu below could be used to quickly '
                       'head to the start menu')
        template.append(prepare_text_message(recipient_id, end_message))
    return template


def get_show_location_template(recipient_id, agency):
    """Prepares a quick reply message to be sent to user
    Returns:
        a list of templates
    """
    template = []
    message_text = 'Please share your location'
    template.append(prepare_text_message(recipient_id, message_text))
    # add content type and postback to the message
    postback = utils.construct_postback(
        'agency', constants.OFFICES, [agency['name']])
    template[-1]['message']['quick_replies'] = [
        {'content_type': 'location', 'payload': postback}
    ]
    return template


def get_offices_response_text(offices):
    """Takes a list of offices
    and returns a message incorporating the addresses
    """
    response_texts = []
    for index, office in enumerate(offices):
        response_text = (
            '{index}.\n'
            'Address: {address}\n'
            'Distance: {distance}\n'
            'Duration: {duration}\n'
        ).format(
            index=index + 1,
            address=office['address'],
            distance=office['distance'],
            duration=office['duration']
        )
        response_texts.append(response_text)
    return response_texts


def prepare_text_message(recipient_id, message_text):
    """Formats text messages for sending"""
    message = {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': message_text
        }
    }
    return message


def text_parser(sender_id, message):
    """
    Decode text messages and returns appropriate response in template form
    """
    response_template = []

    message_type, payload = utils.get_type_and_target_payload(message)

    if message_type is 'coordinates':
        loading_response_template = prepare_text_message(
            sender_id, 'Give me a moment, let me search')
        app.send_message(sender_id, loading_response_template)

        agency_name = utils.get_agency_name_from_local_history(sender_id)

        location = payload
        offices = utils.get_closest_offices(location, agency_name)
        response_texts = get_offices_response_text(offices)
        intro_text = 'So here is what I found'
        response_template.append(prepare_text_message(sender_id, intro_text))
        for response_text in response_texts:
            response_template.append(
                prepare_text_message(sender_id, response_text))

    elif message_type is 'text':
        postback = utils.process_text_through_wit_ai(payload)
        if postback:
            postback_components = utils.deconstruct_postback(postback)
        else:
            postback_components = {}
        response_template = utils.handle_postback(
            sender_id, postback_components)

    return response_template
