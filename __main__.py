"""
Creating a Kubernetes Deployment
"""
import pulumi
from cron_jobs.jobs import cron_job_test
from helm_charts.airsonic import airsonic
from helm_charts.bluecherry import bluecherry
from helm_charts.dropbox import dropbox
from helm_charts.freshrss import freshrss
from helm_charts.games_on_whales import games_on_whales
from helm_charts.kube_dashboard import kube_dashboard
from helm_charts.mariadb import mariadb
from helm_charts.mlflow import ml_flow
from helm_charts.netbootxyz import netbootxyz
from helm_charts.nzbhydra2 import nzbhydra2
from helm_charts.organizr import organizr
from helm_charts.plex import plex
from helm_charts.prometheus import prometheus
from helm_charts.transmission import transmission
from helm_charts.ubooquity import ubooquity
from helm_charts.wiki_js import wiki_js
from pulumi_kubernetes.core.v1 import Namespace
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts
from services.misc import apple_service, nginx_service

config = pulumi.Config()
AMBIENT_WEATHER_API_KEY = config.require("ambient_weather_api_key")
BLUECHERRY_MYSQL_ROOT_PASSWORD = config.require("bluecherry_mysql_root_password")
BLUECHERRY_DB_USER_PASSWORD = config.require("bluecherry_db_user_password")

CIDR = config.require("CIDR")
TIMEZONE = config.require("timezone")
UID = config.require("uid")
GID = config.require("gid")
OPENVPN_PROVIDER = config.require("openvpn_provider")
OPENVPN_CONFIG = config.require("openvpn_config")
OPENVPN_USERNAME = config.require("pia_username")
OPENVPN_PASSWORD = config.require("pia_password")
GRAFANA_PASSWORD = config.require("grafana_password")
KUBE_NODE_HOST = config.require("kube_node_host")
PLEX_SHARES_JSON = config.require("plex_shares_json")

GOV_DOCKER_RUNTIME = "nvidia"
GOW_GPU_UUID = "GPU-b141db0f-29f7-809e-16d5-582f02adb91c"

ENABLE_AIRSONIC = True
ENABLE_BLUECHERRY = True
ENABLE_DASHBOARD = False
ENABLE_DROPBOX = False
ENABLE_FRESH_RSS = True
ENABLE_GOW = False
ENABLE_ML_FLOW = False
ENABlE_NETBOOTXYZ = True
ENABLE_NZBHYDRA2 = True
ENABLE_ORGANIZR = True
ENABLE_PLEX = True
ENABLE_PROMETHEUS = True
ENABLE_TRANSMISSION = True
ENABLE_UBOOQUITY = True
ENABLE_WIKI_JS = True
ENABLE_MARIADB = True

ENABLE_TEST_SERVICES = False
CRON_JOB_TEST = False

# Default folders
SSD_KUBE_CONFIG_PV_LOCATION = "/mnt/500G_SSD/kube_config/config"
SSD_KUBE_DATA_PV_LOCATION = "/mnt/500G_SSD/kube_config/data"
HD_KUBE_DATA_PV_LOCATION = "/mnt/8TB_01/kube_config/data"


def main():
    Namespace(
        "media",
        metadata={
            "name": "media",
        },
    )

    if ENABLE_BLUECHERRY:
        bluecherry(
            config_folder_root=SSD_KUBE_CONFIG_PV_LOCATION,
            recordings_folder="/mnt/8TB_01/dropbox/data/Security/BlueCherryKube",
            hostname=KUBE_NODE_HOST,
            timezone=TIMEZONE,
            mysql_root_password=BLUECHERRY_MYSQL_ROOT_PASSWORD,
            bluecherry_password=BLUECHERRY_DB_USER_PASSWORD,
            uid=UID,
            gid=GID,
        )

    if ENABLE_PROMETHEUS:
        prometheus(
            config_folder_root=SSD_KUBE_CONFIG_PV_LOCATION,
            hostname=KUBE_NODE_HOST,
            grafana_password=GRAFANA_PASSWORD,
            ambient_weather_api_key=AMBIENT_WEATHER_API_KEY,
            timezone=TIMEZONE,
            uid=UID,
            gid=GID,
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

    if ENABLE_GOW:
        games_on_whales(timezone=TIMEZONE, uid=UID, gid=GID)

    if ENABLE_TRANSMISSION:
        transmission(
            config_folder_root=SSD_KUBE_CONFIG_PV_LOCATION,
            data_folder_root=HD_KUBE_DATA_PV_LOCATION,
            vpn_provider=OPENVPN_PROVIDER,
            vpn_username=OPENVPN_USERNAME,
            vpn_password=OPENVPN_PASSWORD,
            vpn_config=OPENVPN_CONFIG,
            cidr=CIDR,
            hostname=KUBE_NODE_HOST,
            timezone=TIMEZONE,
            uid=UID,
            gid=GID,
        )

    if ENABLE_AIRSONIC:
        airsonic(
            config_folder_root=SSD_KUBE_CONFIG_PV_LOCATION,
            hostname=KUBE_NODE_HOST,
            timezone=TIMEZONE,
            uid=UID,
            gid=GID,
        )

    if ENABLE_FRESH_RSS:
        freshrss(
            config_folder_root=SSD_KUBE_CONFIG_PV_LOCATION,
            hostname=KUBE_NODE_HOST,
            timezone=TIMEZONE,
            uid=UID,
            gid=GID,
        )

    if ENABLE_DROPBOX:
        dropbox(
            config_folder_root=SSD_KUBE_CONFIG_PV_LOCATION,
            timezone=TIMEZONE,
            uid=UID,
            gid=GID,
        )

    if ENABLE_UBOOQUITY:
        ubooquity(
            config_folder_root=SSD_KUBE_CONFIG_PV_LOCATION,
            hostname=KUBE_NODE_HOST,
            timezone=TIMEZONE,
            uid=UID,
            gid=GID,
        )

    if ENABLE_WIKI_JS:
        wiki_js(
            config_folder_root=SSD_KUBE_CONFIG_PV_LOCATION,
            data_folder_root=SSD_KUBE_DATA_PV_LOCATION,
            hostname=KUBE_NODE_HOST,
            timezone=TIMEZONE,
            uid=UID,
            gid=GID,
        )

    if ENABLE_DASHBOARD:
        kube_dashboard(hostname=KUBE_NODE_HOST)

    if ENABLE_ORGANIZR:
        organizr(
            config_folder_root=SSD_KUBE_CONFIG_PV_LOCATION,
            hostname=KUBE_NODE_HOST,
            timezone=TIMEZONE,
            uid=UID,
            gid=GID,
        )

    if ENABLE_PLEX:
        plex(
            plex_shares_json=PLEX_SHARES_JSON,
            config_folder_root=SSD_KUBE_CONFIG_PV_LOCATION,
            cidr=CIDR,
            hostname=KUBE_NODE_HOST,
            timezone=TIMEZONE,
            uid=UID,
            gid=GID,
        )

    if ENABLE_NZBHYDRA2:
        nzbhydra2(
            config_folder_root=SSD_KUBE_CONFIG_PV_LOCATION,
            data_folder_root=SSD_KUBE_DATA_PV_LOCATION,
            hostname=KUBE_NODE_HOST,
            timezone=TIMEZONE,
            uid=UID,
            gid=GID,
        )

    if ENABlE_NETBOOTXYZ:
        netbootxyz(
            config_folder_root=SSD_KUBE_CONFIG_PV_LOCATION,
            data_folder_root=HD_KUBE_DATA_PV_LOCATION,
            hostname=KUBE_NODE_HOST,
            timezone=TIMEZONE,
            uid=UID,
            gid=GID,
        )

    if ENABLE_MARIADB:
        mariadb(
            config_folder_root=SSD_KUBE_CONFIG_PV_LOCATION,
            # hostname=KUBE_NODE_HOST,
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
