from __future__ import print_function
import os
import yaml

CONFIG_FILENAME_ENV = 'DATA_DELIVERY_CONFIG'
DEFAULT_CONFIG_FILENAME = '~/.datadelivery.yml'
DEFAULT_D4S2_URL = 'http://127.0.0.1:8000/api/v2/'
DEFAULT_ENDPOINT_NAME = 'default'

ENTER_D4S2_TOKEN_PROMPT = """Please request a D4S2 token from ?
Enter D4S2 token (or press enter to quit):"""


class ConfigFile(object):
    def __init__(self, filename=os.environ.get(CONFIG_FILENAME_ENV, DEFAULT_CONFIG_FILENAME)):
        self.filename = os.path.expanduser(filename)

    def read_or_create_config(self):
        try:
            return self.read_config()
        except IOError:
            token = self._prompt_user_for_token()
            print("Writing new config file at {}".format(self.filename))
            self.write_new_config(token)
            return self.read_config()

    @staticmethod
    def _prompt_user_for_token():
        token = input(ENTER_D4S2_TOKEN_PROMPT)
        if token:
            return token
        else:
            raise ConfigSetupAbandoned()

    def read_config(self):
        with open(self.filename, 'r') as stream:
            return Config(yaml.safe_load(stream))

    def write_new_config(self, token):
        with open(self.filename, 'w+') as stream:
            yaml.safe_dump({
                'token': token
            }, stream)


class Config(object):
    def __init__(self, data):
        self.token = data['token']
        self.d4s2_url = data.get('d4s2_url', DEFAULT_D4S2_URL)
        self.endpoint_name = data.get('_endpoint_name', DEFAULT_ENDPOINT_NAME)


class ConfigSetupAbandoned(Exception):
    pass
