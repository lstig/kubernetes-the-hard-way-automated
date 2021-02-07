# -*- mode: ruby -*-
# vi: set ft=ruby :

require 'erb'
require 'yaml'
require 'ipaddr'

C = YAML.load(File.read("settings.yaml"))

$internal_net = IPAddr.new C['private_address_cidr']
$internal_net = $internal_net.succ # burn off the first ip ending in .1
$external_net = IPAddr.new C['public_address_cidr']
$external_net = $external_net.succ # burn off the first ip ending in .1

def next_ip(net)
  case net
  when "internal"
    $internal_net = $internal_net.succ
    return $internal_net
  when "external"
    $external_net = $external_net.succ
    return $external_net
  end
end

Vagrant.configure("2") do |config|

  # docs: https://github.com/cogitatio/vagrant-hostsupdater
  config.vagrant.plugins = [ "vagrant-hostsupdater" ]

  config.vm.box = "ubuntu/bionic64"

  config.vm.provider "virtualbox" do |vb|
    # This moves an annoying log file that gets created when the VMs
    # are provisioned. I tried setting 'uartmode1' to 'disconnected' but
    # that caused the VMs to boot reeeaaallly slow.
    vb.customize [ "modifyvm", :id, "--uartmode1", "file", "/dev/null" ]
  end

  ANSIBLE_PLAYBOOK = "site.yml"
  ANSIBLE_TAGS     = [ "download" ] # run all tasks related to downloading required artifacts
  ANSIBLE_GROUPS   = {
    "controllers"   => [ "controller-[1:#{C['controllers']}]" ],
    "workers"       => [ "worker-[1:#{C['workers']}]" ],
    "k8s:children"  => [ "controllers", "workers" ],
    "loadbalancers" => [ "traefik" ]
  }

  $lb_external_ip = next_ip("external")
  $lb_internal_ip = next_ip("internal")

  $controller_ips = (1..C['controllers']).map { |i| next_ip("internal") }
  $worker_ips = (1..C['workers']).map { |i| next_ip("internal") }

  config.vm.define "traefik" do |this|
    this.vm.hostname = "traefik.#{C['domain']}"
    this.vm.network "private_network", ip: "#{$lb_internal_ip}", hostsupdater: "skip"
    this.vm.network "private_network", ip: "#{$lb_external_ip}"
    this.hostsupdater.aliases = ["k8s.example.com"]

    this.vm.provider "virtualbox" do |vb|
      vb.memory = C['memory']['loadbalancer']
    end
  end

  (1..C['controllers']).each do |n|
    config.vm.define "controller-#{n}" do |this|
      this.vm.hostname = "controller-#{n}.#{C['domain']}"
      this.vm.network "private_network", ip: "#{$controller_ips[n - 1]}", hostsupdater: "skip"

      this.vm.provider "virtualbox" do |vb|
        vb.memory = C['memory']['controller']
      end
    end
  end

  (1..C['workers']).each do |n|
    config.vm.define "worker-#{n}" do |this|
      this.vm.hostname = "worker-#{n}.#{C['domain']}"
      this.vm.network "private_network", ip: "#{$worker_ips[n - 1]}", hostsupdater: "skip"

      this.vm.provider "virtualbox" do |vb|
        vb.memory = C['memory']['worker']
      end

      if n == C['workers']
        this.vm.provision "ansible" do |a|
          a.limit    = "all,localhost"
          a.playbook = ANSIBLE_PLAYBOOK
          a.groups   = ANSIBLE_GROUPS
          a.tags     = ANSIBLE_TAGS
        end
      end
    end
  end
end
