# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/bionic64"

  config.vm.provider "virtualbox" do |vb|
    # This moves an annoying log file that gets created when the VMs
    # are provisioned. I tried setting 'uartmode1' to 'disconnected' but
    # that caused the VMs to boot reeeaaallly slow.
    vb.customize [ "modifyvm", :id, "--uartmode1", "file", "/dev/null" ]
  end

  LB_MEM = 256
  WORKER_MEM = 640
  CONTROLLER_MEM = 640

  CONTORLLERS = 3
  WORKERS = 3

  ANSIBLE_PLAYBOOK = "vagrant.yml"
  ANSIBLE_GROUPS = {
    "controllers" => [ "controller-[0:#{CONTORLLERS - 1}]" ],
    "workers" => [ "worker-[0:#{WORKERS - 1}]" ],
    "k8s:children" => [ "controllers", "workers" ],
    "loadbalancers" => [ "lb-0" ]
  }

  config.vm.define "lb-0" do |this|
    this.vm.hostname = "lb-0"
    this.vm.network "private_network", ip: "10.240.0.2"
    this.vm.network "private_network", ip: "172.16.0.2"

    this.vm.provider "virtualbox" do |vb|
      vb.memory = LB_MEM
    end
  end

  (0...CONTORLLERS).each do |n|
    config.vm.define "controller-#{n}" do |this|
      this.vm.hostname = "controller-#{n}"
      this.vm.network "private_network", ip: "10.240.0.1#{n}"
      this.vm.network "private_network", ip: "172.16.0.1#{n}"

      this.vm.provider "virtualbox" do |vb|
        vb.memory = CONTROLLER_MEM
      end
    end
  end

  (0...WORKERS).each do |n|
    config.vm.define "worker-#{n}" do |this|
      this.vm.hostname = "worker-#{n}"
      this.vm.network "private_network", ip: "10.240.0.2#{n}"
      this.vm.network "private_network", ip: "172.16.0.2#{n}"

      this.vm.provider "virtualbox" do |vb|
        vb.memory = WORKER_MEM
      end

      if n + 1 == WORKERS
        this.vm.provision "ansible" do |ansible|
          ansible.limit = "all,localhost"
          ansible.playbook = ANSIBLE_PLAYBOOK
          ansible.groups = ANSIBLE_GROUPS
        end
      end
    end
  end
end
