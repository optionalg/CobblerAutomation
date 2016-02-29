#!/usr/bin/python

import json
import os
from jinja2 import Template


def create_config(configs, templates="./templates"):
    """ Creates the necessary configuration files for cobbler and services
    rendered by cobbler.
    - Creates the modles.conf file and the settings file for the cobbler.
    - Creates the dhcp.template file
    - Creates the tftpd.template file
    Args:
        configs (JSON   ): Json file containing config parameters.

        templates (string): location of jinja template files. Defaults to templates
                        directory from the current directory
    Returns:
        : None: outputs configuration files in the destination directory
    """

    template_list = os.listdir(templates)
    for template in template_list:
        with open(os.path.join(os.getcwd(), 'templates', template), 'r+') as f:
            tmp_template = Template(f.read())
            f.seek(0)
            f.write(tmp_template.render(configs['cobbler']['files'][template]))


if __name__ == "__main__":
    with open(os.path.join(os.getcwd(), 'config_files.json'), 'r+') as f:
        config = json.loads(f.read())

    create_config(config, templates='./templates')