from unittest import TestCase
from mock import MagicMock, patch, call, mock_open
from datadelivery.config import ConfigFile, Config, ConfigSetupAbandoned, \
    DEFAULT_DATA_DELIVERY_URL, DEFAULT_ENDPOINT_NAME, ENTER_DATA_DELIVERY_TOKEN_PROMPT


class ConfigFileTestCase(TestCase):
    @patch('datadelivery.config.Config')
    def test_read_config(self, mock_config):
        config_file = ConfigFile()
        with patch("__builtin__.open", mock_open(read_data="data")):
            config = config_file.read_config()
            self.assertEqual(config, mock_config.return_value)
            mock_config.assert_called_with("data")

    @patch('datadelivery.config.Config')
    def test_write_new_config(self, mock_config):
        config_file = ConfigFile()
        with patch("__builtin__.open", mock_open()) as mock_file:
            config_file.write_new_config(token='secret')
            write_call_args_list = mock_file.return_value.write.call_args_list
            written = ''.join([write_call_args[0][0] for write_call_args in write_call_args_list])
            self.assertEqual(written.strip(), '{token: secret}')

    @patch('datadelivery.config.os')
    def test_read_or_create_config_when_file_exists(self, mock_os):
        mock_os.path.exists.return_value = True
        mock_read_config = MagicMock()

        config_file = ConfigFile()
        config_file.read_config = mock_read_config
        config = config_file.read_or_create_config()
        self.assertEqual(config, mock_read_config.return_value)

    @patch('datadelivery.config.os')
    def test_read_or_create_config_when_user_enters_token(self, mock_os):
        mock_os.path.exists.return_value = False
        mock_prompt_user = MagicMock()
        mock_prompt_user.return_value = 'secretToken'
        mock_read_config = MagicMock()
        mock_write_new_config = MagicMock()

        config_file = ConfigFile()
        config_file.prompt_user = mock_prompt_user
        config_file.read_config = mock_read_config
        config_file.write_new_config = mock_write_new_config

        config = config_file.read_or_create_config()
        mock_prompt_user.assert_called_with(ENTER_DATA_DELIVERY_TOKEN_PROMPT)
        mock_write_new_config.assert_called_with('secretToken')
        self.assertEqual(config, mock_read_config.return_value)

    @patch('datadelivery.config.os')
    def test_read_or_create_config_when_user_doesnt_enter_token(self, mock_os):
        mock_os.path.exists.return_value = False
        mock_prompt_user = MagicMock()
        mock_prompt_user.return_value = ''
        mock_read_config = MagicMock()
        mock_write_new_config = MagicMock()

        config_file = ConfigFile()
        config_file.prompt_user = mock_prompt_user
        config_file.read_config = mock_read_config
        config_file.write_new_config = mock_write_new_config

        with self.assertRaises(ConfigSetupAbandoned):
            config_file.read_or_create_config()


class ConfigTestCase(TestCase):
    def test_constructor(self):
        config = Config({
            'token': 'secret1',
            'url': 'dataDeliveryURL',
            'endpoint_name': 'goodEndpoint',
        })

        self.assertEqual(config.token, 'secret1')
        self.assertEqual(config.url, 'dataDeliveryURL')
        self.assertEqual(config.endpoint_name, 'goodEndpoint')

    def test_constructor_defaults(self):
        config = Config({
            'token': 'secret1'
        })

        self.assertEqual(config.token, 'secret1')
        self.assertEqual(config.url, DEFAULT_DATA_DELIVERY_URL)
        self.assertEqual(config.endpoint_name, DEFAULT_ENDPOINT_NAME)
