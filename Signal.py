import requests
import json
import logging

class Signal:
    def __init__(self, config):
        self.config = config
        self.headers = {'Content-Type': 'application/json'}
        self.signal_endpoint = f"{self.config['signal_api_ip']}/v2/send"
        self.data = {
            'number': self.config['send_phone_no'],
            'recipients': [self.config['rec_group_id']],
        }
        logging.info("Signal class initialized")

    def send_message(self, message):
        self.data['message'] = message
        data_json = json.dumps(self.data)
        try:
            response = requests.post(self.signal_endpoint, headers=self.headers, data=data_json)
            response.raise_for_status()
            logging.info(f"Message sent successfully: {message}")
            return response
        except requests.RequestException as e:
            logging.error(f"Failed to send message: {e}")
            raise

    def send_image(self, base64_picture, message=""):
        self.data['message'] = message
        self.data['base64_attachments'] =  [base64_picture.decode()]
        data_json = json.dumps(self.data)
        try:
            response = requests.post(self.signal_endpoint, headers=self.headers, data=data_json)
            response.raise_for_status()
            logging.info(f"Image sent successfully with message: {message}")
            return response
        except requests.RequestException as e:
            logging.error(f"Failed to send image: {e}")
            raise