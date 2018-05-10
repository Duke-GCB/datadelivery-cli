from __future__ import absolute_import
from unittest import TestCase
from mock import MagicMock, patch, call
from datadelivery.argparser import ArgParser


class ArgParserTestCase(TestCase):
    def test_parser_description_contains_version(self):
        version_str = '1.0'
        target_object = MagicMock()
        arg_parser = ArgParser(version_str, target_object)
        self.assertIn('datadelivery (1.0)', arg_parser.argument_parser.description)

    def test_simple_deliver_command(self):
        version_str = '1.0'
        target_object = MagicMock()

        arg_parser = ArgParser(version_str, target_object)
        command_line_args = 'deliver -b bucket1 --email joe@joe.com'
        arg_parser.parse_and_run_commands(command_line_args.split(' '))
        target_object.deliver.assert_called_with('bucket1', 'joe@joe.com', '', False)

    @patch('datadelivery.argparser.ArgUtil')
    def test_simple_deliver_with_user_message(self, mock_arg_util):
        version_str = '1.0'
        target_object = MagicMock()
        mock_arg_util.read_argument_file_contents.return_value = 'some text'

        arg_parser = ArgParser(version_str, target_object)
        command_line_args = 'deliver -b bucket1 --email joe@joe.com --msg-file setup.py'
        arg_parser.parse_and_run_commands(command_line_args.split(' '))

        target_object.deliver.assert_called_with('bucket1', 'joe@joe.com', 'some text', False)

    def test_simple_deliver_ddsclient_project_flag(self):
        version_str = '1.0'
        target_object = MagicMock()

        arg_parser = ArgParser(version_str, target_object)
        command_line_args = 'deliver -p bucket1 --email joe@joe.com'
        arg_parser.parse_and_run_commands(command_line_args.split(' '))
        target_object.deliver.assert_called_with('bucket1', 'joe@joe.com', '', False)

    def test_simple_deliver_command_resend(self):
        version_str = '1.0'
        target_object = MagicMock()

        arg_parser = ArgParser(version_str, target_object)
        command_line_args = 'deliver -b bucket1 --email joe@joe.com --resend'
        arg_parser.parse_and_run_commands(command_line_args.split(' '))
        target_object.deliver.assert_called_with('bucket1', 'joe@joe.com', '', True)

