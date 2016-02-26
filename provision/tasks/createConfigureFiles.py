#!/usr/bin/python

import json
import shutil
import jinja2


def create_config(configs="config_files.json", templates="./templates"):
    """ Creates the necessary configuration files for cobbler and services
    rendered by cobbler.

    - Creates the modles.conf file and the settings file for the cobbler.
    - Creates the dhcp.template file
    - Creates the tftpd.template file

    Args:
        configs (string): location of json file containing config parameters.
                        Defaults to a config_files.json file in the current directory
        templates (string): location of jinja template files. Defaults to templates
                        directory from the current directory
    Returns:
        : None: outputs configuration files in the destination directory
    """


    pass
