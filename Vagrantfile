# -*- mode: ruby -*-
# vi: set ft=ruby :

# Builds single simple Foreman server
# Updated: 20 Jan 2016

# read vm configurations from JSON files
nodes_config = (JSON.parse(File.read("nodes.json")))['nodes']

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  nodes_config.each do |node|
    node_name   = node[0] # name of node
    node_values = node[1] # content of node


    config.vm.box = node_values[':box']

    config.vm.define node_name do |config|
      config.vm.hostname = node_name
      config.vm.network :public_network,
        use_dhcp_assigned_default_route: true,
        bridge: "en1: Wi-Fi (AirPort)"
#       ip: node_values[':ip'],
#       bridge: node_values[':bridge_interface']

      config.vm.provider :virtualbox do |vb|
        vb.customize ["modifyvm", :id,
                      "--name", node_name,
                      "--memory", node_values[':memory'],
                      "--cpus", node_values[':cpus'],
                      "--cpuexecutioncap", node_values[':cpucap'],
                      "--natdnshostresolver1", node_values[':dnsresolver'],
                      "--natdnsproxy1", node_values[':dnsproxy']
                     ]
      end

#      config.vm.provision :shell, path: "bootstrapAnsible.sh"
#
#      config.vm.provision "ansible_local" do |ansible|
#        ansible.playbook = "provision/cobblerServer.yml"
#      end
    end
  end
end


