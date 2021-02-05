# -*- mode: ruby -*-
# vi: set ft=ruby :

require 'erb'
require 'ipaddr'
require "./settings"

$internal_net = IPAddr.new INTERNAL_NET
$external_net = IPAddr.new EXTERNAL_NET

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
    "controllers"   => [ "controller-[1:#{CONTROLLERS}]" ],
    "workers"       => [ "worker-[1:#{WORKERS}]" ],
    "k8s:children"  => [ "controllers", "workers" ],
    "loadbalancers" => [ "lb-0" ]
  }

  $lb_external_ip = next_ip("external")
  $lb_internal_ip = next_ip("internal")

  $controller_ips = (0...CONTROLLERS).map { |i| next_ip("internal") }
  $worker_ips = (0...WORKERS).map { |i| next_ip("internal") }

  config.vm.define "lb-0" do |this|
    this.vm.hostname = "lb-0.#{DOMAIN}"
    this.vm.network "private_network", ip: "#{$lb_internal_ip}", hostsupdater: "skip"
    this.vm.network "private_network", ip: "#{$lb_external_ip}"
    this.hostsupdater.aliases = ["k8s.example.com"]

    $template = <<-EOF
      <% $worker_ips.each_with_index do |ip, i| %>
      route add -net 10.200.<%= i + 1 %>.0/24 gw <%= ip %>
      <% end %>
    EOF

    $routes = ERB.new($template.gsub(/^  /, ''), 0, "%<>")

    # This configures routes between nodes for pod networking
    this.vm.provision "shell", run: "always" do |s|
      s.inline = $routes.result(binding)
    end

    this.vm.provider "virtualbox" do |vb|
      vb.memory = LB_MEM
    end
  end

  (0...CONTROLLERS).each do |n|
    config.vm.define "controller-#{n + 1}" do |this|
      this.vm.hostname = "controller-#{n + 1}.#{DOMAIN}"
      this.vm.network "private_network", ip: "#{$controller_ips[n]}", hostsupdater: "skip"

      this.vm.provider "virtualbox" do |vb|
        vb.memory = CONTROLLER_MEM
      end
    end
  end

  (0...WORKERS).each do |n|
    config.vm.define "worker-#{n + 1}" do |this|
      this.vm.hostname = "worker-#{n + 1}.#{DOMAIN}"
      this.vm.network "private_network", ip: "#{$worker_ips[n]}", hostsupdater: "skip"

      this.vm.provider "virtualbox" do |vb|
        vb.memory = WORKER_MEM
      end

      # This templates creates routes to all other worker nodes
      $template = <<-EOF
        <% $worker_ips.each_with_index do |ip, i| %>
        <% if ip != $worker_ips[n] %>
        route add -net 10.200.<%= i + 1 %>.0/24 gw <%= ip %>
        <% end %>
        <% end %>
      EOF

      $routes = ERB.new($template.gsub(/^  /, ''), 0, "%<>")

      # This configures routes between ndoes for pod networking
      this.vm.provision "shell", run: "always" do |s|
        s.inline = $routes.result(binding)
      end

      if n + 1 == WORKERS
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
