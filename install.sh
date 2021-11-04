#!/usr/bin/env bash

# Setup Nvidia
helm repo add nvdp https://nvidia.github.io/k8s-device-plugin

# Setup transmission helm chart repo
helm repo add bananaspliff https://bananaspliff.github.io/geek-charts

# Setup the k8s@home repo (most charts come from here)
helm repo add k8s-at-home https://k8s-at-home.com/charts/

# Setup the Kube dashboard repo
helm repo add kubernetes-dashboard https://kubernetes.github.io/dashboard/

# Setup Prometheus
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts

# Setup MLFlow
# helm repo add minio https://operator.min.io/
helm repo add bitnami https://charts.bitnami.com/bitnami
#helm repo add cetic https://cetic.github.io/helm-charts
#helm repo add larribas https://larribas.me/helm-charts
helm repo add deliveryhero https://charts.deliveryhero.io/

helm repo update

CIDR=$(kubectl cluster-info dump | grep -m 1 cidr | grep -Po "cidr=\K(.*) ")
