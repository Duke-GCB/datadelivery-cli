from __future__ import print_function, absolute_import
import os
import yaml
from six.moves import input


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
        config = Config({})
        if os.path.exists(self.filename):
            config = self.read_config()
        if not config.token:
            config.token = self._prompt_user_for_token()
            print("Writing config file at {}".format(self.filename))
            self.write_config(config)
        return config

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

    def write_config(self, config):
        with open(self.filename, 'w+') as stream:
            yaml.safe_dump(config.to_dict(), stream)


class Config(object):
    def __init__(self, data):
        self.token = data.get('token')
        self._url = data.get('url')
        self._endpoint_name = data.get('endpoint_name')

    @property
    def url(self):
        if not self._url:
            return DEFAULT_DATA_DELIVERY_URL
        return self._url

    @property
    def endpoint_name(self):
        if not self._endpoint_name:
            return DEFAULT_ENDPOINT_NAME
        return self._endpoint_name

    def to_dict(self):
        data = {}
        if self.token:
            data['token'] = self.token
        if self._url:
            data['url'] = self._url
        if self._endpoint_name:
            data['endpoint_name'] = self._endpoint_name
        return data


class ConfigSetupAbandoned(Exception):
    pass
