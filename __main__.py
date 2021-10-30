"""
Creating a Kubernetes Deployment
"""
import pulumi
from cron_jobs.jobs import cron_job_test
from helm_charts.freshrss import freshrss
from helm_charts.kube_dashboard import kube_dashboard
from helm_charts.mlflow import ml_flow
from helm_charts.organizr import organizr
from helm_charts.plex import plex
from helm_charts.transmission import transmission
from helm_charts.ubooquity import ubooquity
from helm_charts.wiki_js import wiki_js
from pulumi_kubernetes.core.v1 import Namespace
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts
from services.misc import apple_service, nginx_service

config = pulumi.Config()
CIDR = config.require("CIDR")
TIMEZONE = config.require("timezone")
UID = config.require("uid")
GID = config.require("gid")
OPENVPN_PROVIDER = config.require("openvpn_provider")
OPENVPN_CONFIG = config.require("openvpn_config")
PIA_USERNAME = config.require("pia_username")
PIA_PASSWORD = config.require("pia_password")
KUBE_NODE_HOST = config.require("kube_node_host")
PLEX_SHARES_JSON = config.require("plex_shares_json")

GOV_DOCKER_RUNTIME = "nvidia"
GOW_GPU_UUID = "GPU-b141db0f-29f7-809e-16d5-582f02adb91c"

ENABLE_FRESH_RSS = True
ENABLE_DASHBOARD = True
ENABLE_ML_FLOW = True
ENABLE_ORGANIZR = True
ENABLE_PLEX = True
ENABLE_TRANSMISSION = True
ENABLE_UBOOQUITY = True
ENABLE_WIKI_JS = True

ENABLE_TEST_SERVICES = False
CRON_JOB_TEST = False


def main():

    Namespace(
        "media",
        metadata={
            "name": "media",
        },
    )

    if False:
        Chart(
            "nvidia-device-plugin",
            config=ChartOpts(
                chart="nvidia-device-plugin",
                # namespace=media_namespace.metadata.apply(lambda v: v["name"]),
                version="0.9.0",
                fetch_opts=FetchOpts(
                    repo="https://nvidia.github.io/k8s-device-plugin",
                ),
            ),
        )

    if ENABLE_TRANSMISSION:
        transmission(
            config_folder_root="/mnt/500G_SSD/kube_config/config",
            data_folder_root="/mnt/8TB_01/kube_config/data",
            vpn_provider=OPENVPN_PROVIDER,
            vpn_username=PIA_USERNAME,
            vpn_password=PIA_PASSWORD,
            vpn_config=OPENVPN_CONFIG,
            cidr=CIDR,
            hostname=KUBE_NODE_HOST,
            timezone=TIMEZONE,
            uid=UID,
            gid=GID,
        )

    if ENABLE_FRESH_RSS:
        freshrss(
            config_folder_root="/mnt/500G_SSD/kube_config/config",
            hostname=KUBE_NODE_HOST,
            timezone=TIMEZONE,
            uid=UID,
            gid=GID,
        )

    if ENABLE_UBOOQUITY:
        ubooquity(
            config_folder_root="/mnt/500G_SSD/kube_config/config",
            hostname=KUBE_NODE_HOST,
            timezone=TIMEZONE,
            uid=UID,
            gid=GID,
        )

    if ENABLE_WIKI_JS:
        wiki_js(
            config_folder_root="/mnt/500G_SSD/kube_config/config",
            data_folder_root="/mnt/500G_SSD/kube_config/data",
            hostname=KUBE_NODE_HOST,
            timezone=TIMEZONE,
            uid=UID,
            gid=GID,
        )

    if ENABLE_DASHBOARD:
        kube_dashboard(hostname=KUBE_NODE_HOST)

    if ENABLE_ORGANIZR:
        organizr(
            config_folder_root="/mnt/500G_SSD/kube_config/config",
            hostname=KUBE_NODE_HOST,
            timezone=TIMEZONE,
            uid=UID,
            gid=GID,
        )

    if ENABLE_PLEX:
        plex(
            plex_shares_json=PLEX_SHARES_JSON,
            config_folder_root="/mnt/500G_SSD/kube_config/config",
            cidr=CIDR,
            hostname=KUBE_NODE_HOST,
            timezone=TIMEZONE,
            uid=UID,
            gid=GID,
        )

    if ENABLE_ML_FLOW:
        ml_flow(
            hostname=KUBE_NODE_HOST,
            uid=UID,
            gid=GID,
        )

    if ENABLE_TEST_SERVICES:
        apple_service(hostname=KUBE_NODE_HOST)
        nginx_service(hostname=KUBE_NODE_HOST)

    if CRON_JOB_TEST:
        cron_job_test()
    return


if __name__ == "__main__":
    main()
