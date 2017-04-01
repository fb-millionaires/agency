import json
import os
import sys

from flask import Flask, jsonify, request
from pymongo import MongoClient
import requests


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
                # someone sent us a message
                if messaging_event.get('message'):
                    # the facebook ID of the person sending you the message
                    sender_id = messaging_event['sender']['id']
                    # the recipient's ID, actually Agency's page facebook ID
                    recipient_id = messaging_event['recipient']['id']
                    # the message's text
                    message_text = messaging_event['message']['text']

                    send_message(
                        sender_id,
                        'Got it, thanks man!!! -- {original_message}'.format(
                            original_message=message_text
                        )
                    )

                # delivery confirmation
                if messaging_event.get('delivery'):
                    pass

                # delivery confirmation
                if messaging_event.get('optin'):
                    pass

                # user clicked/tapped 'postback' button in earlier message
                if messaging_event.get('postback'):
                    pass

    return 'ok', 200


def send_message(recipient_id, message_text):
    log('sending message to {recipient}: {text}'.format(
        recipient=recipient_id,
        text=message_text
    ))
    params = {
        'access_token': os.environ['PAGE_ACCESS_TOKEN']
    }
    headers = {
        'Content-Type': 'application/json'
    }
    data = json.dumps({
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': message_text
        }
    })
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


if __name__ == '__main__':
    app.run(debug=True)
