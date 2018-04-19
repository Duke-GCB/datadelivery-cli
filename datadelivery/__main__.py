#!/usr/bin/env python
from datadelivery.commands import Commands, APP_NAME
from datadelivery.argparser import ArgParser
from datadelivery.config import ConfigSetupAbandoned
import pkg_resources


def main():
    version_str = pkg_resources.get_distribution(APP_NAME).version
    arg_parser = ArgParser(version_str, Commands(version_str))
    try:
        arg_parser.parse_and_run_commands()
    except ConfigSetupAbandoned:
        pass


if __name__ == '__main__':
    main()
