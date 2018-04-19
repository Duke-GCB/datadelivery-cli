from __future__ import print_function
import os
import yaml

CONFIG_FILENAME_ENV = 'DATA_DELIVERY_CONFIG'
DEFAULT_CONFIG_FILENAME = '~/.datadelivery.yml'
BASE_DATA_DELIVERY_URL = 'https://datadelivery.genome.duke.edu'
DEFAULT_DATA_DELIVERY_URL = '{}/api/v2/'.format(BASE_DATA_DELIVERY_URL)
DEFAULT_ENDPOINT_NAME = 'default'

ENTER_DATA_DELIVERY_TOKEN_PROMPT = """Please request a token from {}
Enter token (or press enter to quit):""".format(BASE_DATA_DELIVERY_URL)


class ConfigFile(object):
    def __init__(self, filename=os.environ.get(CONFIG_FILENAME_ENV, DEFAULT_CONFIG_FILENAME)):
        self.filename = os.path.expanduser(filename)

    def read_or_create_config(self):
        if os.path.exists(self.filename):
            return self.read_config()
        else:
            token = self._prompt_user_for_token()
            print("Writing new config file at {}".format(self.filename))
            self.write_new_config(token)
            return self.read_config()

    def _prompt_user_for_token(self):
        token = self.prompt_user(ENTER_DATA_DELIVERY_TOKEN_PROMPT)
        if token:
            return token
        else:
            raise ConfigSetupAbandoned()

    @staticmethod
    def prompt_user(message):
        """
        Get command line input from the user
        :param message: str: message to show user
        :return: str: value user entered
        """
        return input(message)

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
        self.data_delivery_url = data.get('data_delivery_url', DEFAULT_DATA_DELIVERY_URL)
        self.endpoint_name = data.get('endpoint_name', DEFAULT_ENDPOINT_NAME)


class ConfigSetupAbandoned(Exception):
    pass
