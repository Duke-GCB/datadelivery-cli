from __future__ import absolute_import
from unittest import TestCase
from mock import MagicMock, patch, call
from datadelivery.commands import Commands
from datadelivery.datadelivery import NotFoundException


class CommandsTestCase(TestCase):
    def setUp(self):
        self.config = MagicMock()

    @patch('datadelivery.commands.ConfigFile')
    @patch('datadelivery.commands.DataDeliveryApi')
    def test_deliver_bucket(self, mock_data_delivery_api, mock_config_file):
        mock_data_delivery_object = mock_data_delivery_api.return_value
        mock_to_user = MagicMock()
        mock_bucket = MagicMock()
        mock_delivery = MagicMock()
        mock_config_file.return_value.read_or_create_config.return_value = self.config
        mock_data_delivery_object.get_s3user_by_email.return_value = mock_to_user
        mock_data_delivery_object.get_or_create_bucket.return_value = mock_bucket
        mock_data_delivery_object.create_delivery.return_value = mock_delivery

        commands = Commands(version_str='1.0')
        commands.deliver(bucket_name='some_bucket', email='joe@joe.com', user_message='Test', resend=False)

        mock_data_delivery_api.assert_called_with(self.config, user_agent_str='datadelivery/1.0')
        mock_data_delivery_object.get_s3user_by_email.assert_called_with('joe@joe.com')
        mock_data_delivery_object.get_or_create_bucket.assert_called_with('some_bucket')
        mock_data_delivery_object.create_delivery.assert_called_with(mock_bucket, mock_to_user, 'Test')
        mock_data_delivery_object.send_delivery.assert_called_with(mock_delivery, False)

    @patch('datadelivery.commands.ConfigFile')
    @patch('datadelivery.commands.DataDeliveryApi')
    def test_deliver_bucket_resend(self, mock_data_delivery_api, mock_config_file):
        mock_data_delivery_object = mock_data_delivery_api.return_value
        mock_to_user = MagicMock()
        mock_bucket = MagicMock()
        mock_delivery = MagicMock()
        mock_config_file.return_value.read_or_create_config.return_value = self.config
        mock_data_delivery_object.get_s3user_by_email.return_value = mock_to_user
        mock_data_delivery_object.get_or_create_bucket.return_value = mock_bucket
        mock_data_delivery_object.create_delivery.return_value = mock_delivery

        commands = Commands(version_str='1.0')
        commands.deliver(bucket_name='some_bucket', email='joe@joe.com', user_message='Test', resend=True)

        mock_data_delivery_api.assert_called_with(self.config, user_agent_str='datadelivery/1.0')
        mock_data_delivery_object.get_s3user_by_email.assert_called_with('joe@joe.com')
        mock_data_delivery_object.get_or_create_bucket.assert_called_with('some_bucket')
        mock_data_delivery_object.create_delivery.assert_called_with(mock_bucket, mock_to_user, 'Test')
        mock_data_delivery_object.send_delivery.assert_called_with(mock_delivery, True)
