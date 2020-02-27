Kubernetes the Hard Way (Automated)
===

This project was a personal exercise to learn more about the internals of kubernetes. These ansible playbooks are derived from the steps in Keylsey Hightower's [Kubernetes the Hard Way](https://github.com/kelseyhightower/kubernetes-the-hard-way) tutorial.

> THIS IS NOT INTENDED FOR PRODUCTION USE. I TAKE NO RESPONSIBILITY FOR THE MAYHEM CAUSED BY USING THIS IN A PRODUCTION ENVIRONMENT.

One of the hardest parts of setting up kubernetes from scratch is the sheer number of certificates and configurations required to _just_ get the cluster up and running. I'm using ansible in order to automate the more tedious aspects of bootstrapping kubernetes, and I've replaced VMs and loadbalancer on GCP with vagrant and traefik running locally.

Requirements
---

TODO

Setup
---

TODO

Testing
---

```shell
# create kubeconfig for accessing the kubernetes cluster from
# your host and deploy required cluster resources
ansible-playbook k8s.yaml
```

```shell
# fetch service account token and update traefik configuration
KUBECONFIG=local/admin.kubeconfig
NAMESPACE=kube-system

TRAEFIK_TOKEN=$(kubectl -n ${NAMESPACE} describe secret $(kubectl -n ${NAMESPACE} get secret | (grep traefik-ingress-controller || echo "$_") | awk '{print $1}') | grep token: | awk '{print $2}')

ansible-playbook site.yml --tags traefik_static_config,traefik_dynamic_config -e traefik_k8s_token=${TRAEFIK_TOKEN}
```
