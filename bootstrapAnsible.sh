#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Per:  http://docs.ansible.com/ansible/intro_installation.html#latest-releases-via-apt-ubuntu
# the follow four commands install the latest version of Ansible on a box.
apt-get install -y software-properties-common
apt-add-repository -y ppa:ansible/ansible
apt-get update
apt-get install -y ansible

# Ensure SSH both client & server are installed and running
apt-get install -y openssh-client
apt-get install -y openssh-server
service ssh restart