import argparse
import sys

DESCRIPTION_STR = "datadelivery ({}) Deliver s3 projects to other users"


class ArgParser(object):
    def __init__(self, version_str, target_object):
        """
        Create argument parser with the specified version string that will call the appropriate methods
        in target_object when those commands are selected.
        :param version_str: str: version of datadelivery
        :param target_object: object: object with methods named the same as the commands
        """
        self.version_str = version_str
        self.target_object = target_object

    def parse_and_run_commands(self):
        """
        Parse command line arguments and run the appropriate command or show help.
        """
        argument_parser = self._create_argument_parser()
        parsed_args = argument_parser.parse_args()
        if hasattr(parsed_args, 'func'):
            parsed_args.func(parsed_args)
        else:
            argument_parser.print_help()

    def _create_argument_parser(self):
        argument_parser = argparse.ArgumentParser(description=DESCRIPTION_STR.format(self.version_str))
        subparsers = argument_parser.add_subparsers()
        self._add_deliver_command(subparsers)
        return argument_parser

    def _add_deliver_command(self, subparsers):
        """
        Add 'deliver' command to subparsers
        :param subparsers: subparser to add the command to
        """
        deliver_parser = subparsers.add_parser('deliver', description='Deliver bucket to another user.')
        deliver_parser.set_defaults(func=self._run_deliver)
        deliver_parser.add_argument(
            '-b', '--bucket-name', '-p', '--project-name',
            metavar='BucketName',
            type=str,
            dest='bucket_name',
            help="Name of the bucket to deliver",
            required=True)
        deliver_parser.add_argument(
            '--email',
            metavar='UserEmail',
            type=str,
            dest='email',
            help="Email of the user to deliver the bucket to",
            required=True)
        deliver_parser.add_argument(
            '--msg-file',
            type=argparse.FileType('r'),
            help="Filename containing a message to be sent with the delivery. Pass - to read from stdin."
        )

    def _run_deliver(self, args):
        """
        Method called for running the deliver command.
        """
        user_message = self.read_argument_file_contents(args.msg_file)
        self.target_object.deliver(args.bucket_name, args.email, user_message)

    @staticmethod
    def read_argument_file_contents(infile):
        """
        return the contents of a file or "" if infile is None.
        If the infile is STDIN displays a message to tell user how to quit entering data.
        :param infile: file handle to read from
        :return: str: contents of the file
        """
        if infile:
            if infile == sys.stdin:
                print("Enter message and press CTRL-d when done:")
            return infile.read()
        return ""
