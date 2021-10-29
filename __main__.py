"""
Creating a Kubernetes Deployment
"""
import json

import pulumi
from pulumi_kubernetes.apps.v1 import Deployment
from pulumi_kubernetes.batch.v1 import JobSpecArgs
from pulumi_kubernetes.batch.v1beta1 import (
    CronJob,
    CronJobSpecArgs,
    JobTemplateSpecArgs,
)
from pulumi_kubernetes.core.v1 import (
    ContainerArgs,
    Namespace,
    PersistentVolume,
    PersistentVolumeClaim,
    Pod,
    PodSpecArgs,
    PodTemplateSpecArgs,
    Secret,
    Service,
    ServicePortArgs,
    ServiceSpecArgs,
)
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts
from pulumi_kubernetes.networking.v1 import (
    HTTPIngressPathArgs,
    HTTPIngressRuleValueArgs,
    Ingress,
    IngressBackendArgs,
    IngressRuleArgs,
    IngressServiceBackendArgs,
    IngressSpecArgs,
    ServiceBackendPortArgs,
)

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


def create_pvc(name, path, access_mode="ReadWriteMany", size="1Gi", mount_path=""):
    clean_name = name.lower().replace("_", "-")
    volume = PersistentVolume(
        clean_name,
        metadata={
            "name": f"{clean_name}-pv",
            "labels": {"type": "local"},
        },
        spec={
            "persistentVolumeReclaimPolicy": "Retain",
            "storageClassName": "normal",  # f"{name}-sc",
            "capacity": {"storage": size},
            "accessModes": [
                access_mode,
            ],
            "hostPath": {"path": f"{path}"},
        },
    )

    claim = PersistentVolumeClaim(
        clean_name,
        metadata={
            "name": f"{clean_name}-pvc",
        },
        spec={
            "storageClassName": "normal",  # f"{name}-sc",
            "accessModes": [access_mode],
            "resources": {
                "requests": {
                    "storage": size,
                }
            },
            "volumeName": f"{clean_name}-pv",
        },
    )

    pre_built_mount = {
        "enabled": "true",
        "type": "pvc",
        "existingClaim": claim.metadata.apply(lambda v: v["name"]),
        "mountPath": mount_path,
    }
    return volume, claim, pre_built_mount


def transmission_chart():
    transmission_config_volume, transmission_config_claim, _ = create_pvc(
        name="transmission-config",
        path="/mnt/8TB_01/kube_config/config/transmission",
        size="1Gi",
        access_mode="ReadWriteMany",
    )

    transmission_data_volume, transmission_data_claim, _ = create_pvc(
        name="transmission-data",
        path="/mnt/8TB_01/kube_config/data/transmission",
        size="200Gi",
        access_mode="ReadWriteMany",
    )

    _ = Secret(
        "private-internet-access",
        metadata={
            "name": "private-internet-access",
        },
        type="kubernetes.io/basic-auth",
        string_data={
            "username": PIA_USERNAME,
            "password": PIA_PASSWORD,
        },
    )

    transmission = Chart(
        "transmission-openvpn",
        config=ChartOpts(
            chart="transmission-openvpn",
            # namespace=media_namespace.metadata.apply(lambda v: v["name"]),
            version="0.1.0",
            fetch_opts=FetchOpts(
                repo="https://bananaspliff.github.io/geek-charts",
            ),
            values={
                "image": {
                    "repository": "haugene/transmission-openvpn",
                    "tag": "latest",
                    "pullPolicy": "IfNotPresent",
                },
                "env": [
                    {"name": "CREATE_TUN_DEVICE", "value": "true"},
                    {"name": "PUID", "value": UID},
                    {"name": "PGID", "value": GID},
                    {"name": "LOCAL_NETWORK", "value": CIDR},
                    {"name": "OPENVPN_PROVIDER", "value": OPENVPN_PROVIDER},
                    {"name": "OPENVPN_CONFIG", "value": OPENVPN_CONFIG},
                    {"name": "OPENVPN_USERNAME", "value": PIA_USERNAME},
                    {"name": "OPENVPN_PASSWORD", "value": PIA_PASSWORD},
                    {
                        "name": "OPENVPN_OPTS",
                        "value": "--inactive 3600 --ping 10 --ping-exit 60 --mute-replay-warnings",
                    },
                    {"name": "TRANSMISSION_DOWNLOAD_QUEUE_SIZE", "value": "400"},
                    {"name": "TRANSMISSION_PREALLOCATION", "value": "0"},
                    {"name": "TRANSMISSION_RATIO_LIMIT", "value": "0.25"},
                    {"name": "TRANSMISSION_RATIO_LIMIT_ENABLED", "value": "true"},
                    {"name": "TRANSMISSION_SPEED_LIMIT_UP", "value": "20"},
                    {
                        "name": "TRANSMISSION_SPEED_LIMIT_UP_ENABLED",
                        "value": "true",
                    },
                    {
                        "name": "TRANSMISSION_ALT_SPEED_TIME_ENABLED",
                        "value": "true",
                    },
                    {"name": "TRANSMISSION_ALT_SPEED_TIME_BEGIN", "value": "420"},
                    {"name": "TRANSMISSION_ALT_SPEED_TIME_END", "value": "1320"},
                    {"name": "TRANSMISSION_ALT_SPEED_UP", "value": "20"},
                    {"name": "TRANSMISSION_ALT_SPEED_DOWN", "value": "3000"},
                    {"name": "TRANSMISSION_SEED_QUEUE_SIZE", "value": "10"},
                    {"name": "TRANSMISSION_SEED_QUEUE_ENABLED", "value": "true"},
                    {"name": "TRANSMISSION_IDLE_SEEDING_LIMIT", "value": "15"},
                    {
                        "name": "TRANSMISSION_IDLE_SEEDING_LIMIT_ENABLED",
                        "value": "true",
                    },
                    {"name": "WEBPROXY_ENABLED", "value": "false"},
                    {"name": "TZ", "value": TIMEZONE},
                ],
                "volumes": [
                    {
                        "name": transmission_config_volume.metadata.apply(
                            lambda v: v["name"]
                        ),
                        "persistentVolumeClaim": {
                            "claimName": transmission_config_claim.metadata.apply(
                                lambda v: v["name"]
                            )
                        },
                    },
                    {
                        "name": transmission_data_volume.metadata.apply(
                            lambda v: v["name"]
                        ),
                        "persistentVolumeClaim": {
                            "claimName": transmission_data_claim.metadata.apply(
                                lambda v: v["name"]
                            )
                        },
                    },
                    {
                        "name": "dev-tun",  # Needed for VPN
                        "hostPath": {
                            "path": "/dev/net/tun",
                        },
                    },
                ],
                "volumeMounts": [
                    {  # Configuration
                        "name": transmission_config_volume.metadata.apply(
                            lambda v: v["name"]
                        ),
                        "mountPath": "/data/transmission-home",
                    },
                    {  # Folder to watch
                        "name": transmission_data_volume.metadata.apply(
                            lambda v: v["name"]
                        ),
                        "mountPath": "/data/watch",
                        "subPath": "watch",
                    },
                    {  # Incomplete Torrents
                        "name": transmission_data_volume.metadata.apply(
                            lambda v: v["name"]
                        ),
                        "mountPath": "/data/incomplete",
                        "subPath": "incomplete",
                    },
                    {  # Completed Torrents
                        "name": transmission_data_volume.metadata.apply(
                            lambda v: v["name"]
                        ),
                        "mountPath": "/data/completed",
                        "subPath": "completed",
                    },
                    {  # Needed for VPN
                        "name": "dev-tun",
                        "mountPath": "/dev/net/tun",
                    },
                ],
                "service": {"type": "ClusterIP", "port": 80},
                "securityContext": {  # Needed for VPN
                    "capabilities": {"add": ["NET_ADMIN"]},
                },
            },
        ),
    )

    Ingress(
        "transmission-ingress",
        metadata={
            "name": "transmission-ingress",
            "annotations": {},
        },
        spec=IngressSpecArgs(
            rules=[
                IngressRuleArgs(
                    host=f"transmission.{KUBE_NODE_HOST}",
                    http=HTTPIngressRuleValueArgs(
                        paths=[
                            HTTPIngressPathArgs(
                                path="/",
                                path_type="Prefix",
                                backend=IngressBackendArgs(
                                    service=IngressServiceBackendArgs(
                                        name=transmission.get_resource(
                                            "v1/Service", "transmission-openvpn"
                                        ).metadata["name"],
                                        port=ServiceBackendPortArgs(number=80),
                                    ),
                                ),
                            ),
                        ]
                    ),
                ),
            ],
        ),
    )
    return


def freshrss_chart():
    _, _, config_map = create_pvc(
        name="freshrss-config",
        path="/mnt/8TB_01/kube_config/config/freshrss",
        size="3Gi",
        access_mode="ReadWriteMany",
        mount_path="/config",
    )

    Chart(
        "freshrss",
        config=ChartOpts(
            chart="freshrss",
            version="6.0.1",
            fetch_opts=FetchOpts(
                repo="https://k8s-at-home.com/charts/",
            ),
            values={
                "image": {
                    "repository": "linuxserver/freshrss",
                    "tag": "version-1.18.1",
                    "pullPolicy": "IfNotPresent",
                },
                "env": {
                    "TZ": TIMEZONE,
                    "PUID": UID,
                    "PGID": GID,
                },
                "persistence": {
                    "config": config_map,
                },
                "ingress": {
                    "main": {
                        "enabled": "true",
                        "hosts": [
                            {
                                "host": f"freshrss.{KUBE_NODE_HOST}",
                                "paths": [
                                    {
                                        "path": "/",
                                        "service": {"name": "freshrss", "port": 80},
                                    }
                                ],
                            },
                        ],
                    },
                },
            },
        ),
    )
    return


def ubooquity_chart():
    _, _, config_map = create_pvc(
        name="ubooquity-config",
        path="/mnt/8TB_01/kube_config/config/ubooquity",
        size="1Gi",
        access_mode="ReadWriteMany",
        mount_path="/config",
    )

    _, _, books_map = create_pvc(
        name="ubooquity-books",
        path="/mnt/SnapSsdArray_01/SnapDisk_1TB_01/Books/",
        access_mode="ReadOnlyMany",
        mount_path="/books",
    )

    _, _, comics_map = create_pvc(
        name="ubooquity-comics",
        path="/mnt/SnapSsdArray_01/SnapDisk_1TB_01/Comics",
        access_mode="ReadOnlyMany",
        mount_path="/comics",
    )

    # NOTES: Hijacking the "reg" chart and instead loading the "ubooquity" linuxserver.io container
    Chart(
        "ubooquity",
        config=ChartOpts(
            chart="reg",  # Not really going to use this container
            version="3.0.1",
            fetch_opts=FetchOpts(
                repo="https://k8s-at-home.com/charts/",
            ),
            values={
                "image": {
                    "repository": "ghcr.io/linuxserver/ubooquity",
                    "tag": "2.1.2-ls74",
                    "pullPolicy": "IfNotPresent",
                },
                "env": {
                    "TZ": TIMEZONE,
                    "PUID": UID,
                    "PGID": GID,
                    "MAXMEM": "2048",
                },
                "persistence": {
                    "config": config_map,
                    "books": books_map,
                    "comics": comics_map,
                },
                "service": {
                    "main": {
                        "enabled": "true",
                        "nameOverride": "ubooquity",
                        "ports": {
                            "http": {"enabled": "true", "port": 2202},
                        },
                    },
                    "admin": {
                        "enabled": "true",
                        "nameOverride": "ubooquity-admin",
                        "ports": {
                            "admin": {"enabled": "true", "port": 2203},
                        },
                    },
                },
                "ingress": {
                    "main": {
                        "enabled": "true",
                        "nameOverride": "ubooquity",
                        "hosts": [
                            {
                                "host": f"ubooquity.{KUBE_NODE_HOST}",  # /ubooquity/
                                "paths": [
                                    {
                                        "path": "/",
                                        "service": {
                                            # The "name" is odd because we hijacked the reg helm
                                            "name": "ubooquity-reg-ubooquity",
                                            "port": 2202,
                                        },
                                    }
                                ],
                            },
                            {
                                "host": f"ubooquity-admin.{KUBE_NODE_HOST}",  # /ubooquity/admin
                                "paths": [
                                    {
                                        "path": "/",
                                        "service": {
                                            # The "name" is odd because we hijacked the reg helm
                                            "name": "ubooquity-reg-ubooquity-admin",
                                            "port": 2203,
                                        },
                                    }
                                ],
                            },
                        ],
                    },
                },
            },
        ),
    )
    return


def plex_chart():

    # Prep all the shares

    # Shares in the config should be of the form:
    # [
    #   {
    #       "name": "name-of-mount",
    #       "path": "/local/path/to/mount",
    #       "access_mode": "ReadOnlyMany",
    #       "mount_path" "/where/to/mount/in/pod"
    #   },
    #   ...
    # ]
    plex_shares = json.loads(PLEX_SHARES_JSON)
    persistence_volumes = {}
    for share in plex_shares:
        _, _, curr_map = create_pvc(
            name=share["name"],
            path=share["path"],
            access_mode=share["access_mode"],
            mount_path=share["mount_path"],
        )
        key = share["name"].replace("_", "-")
        persistence_volumes[key] = curr_map

    _, _, config_map = create_pvc(
        name="plex-config",
        path="/mnt/8TB_01/kube_config/config/plex-config",
        size="100Gi",
        access_mode="ReadWriteMany",
        mount_path="/config",
    )
    persistence_volumes["plex-config"] = config_map

    _, _, transcode_map = create_pvc(
        name="plex-transcode",
        path="/mnt/8TB_01/kube_config/config/plex-transcode",  # pragma: allowlist secret
        size="5Gi",
        access_mode="ReadWriteMany",
        mount_path="/transcode",
    )
    persistence_volumes["plex-transcode"] = transcode_map

    Chart(
        "plex",
        config=ChartOpts(
            chart="plex",
            version="6.0.2",
            fetch_opts=FetchOpts(
                repo="https://k8s-at-home.com/charts/",
            ),
            values={
                "image": {
                    "repository": "linuxserver/plex",
                    "tag": "latest",
                    "pullPolicy": "IfNotPresent",
                },
                "env": {
                    "TZ": TIMEZONE,
                    "PUID": UID,
                    "PGID": GID,
                    "PLEX_UID": UID,
                    "PLEX_GID": GID,
                    "ALLOWED_NETWORKS": f"{CIDR},192.168.10.0/24",
                },
                "hostNetwork": "true",
                "service": {
                    "main": {
                        "ports": {
                            "http": {
                                "enabled": "true",
                                "servicePort": 32400,
                            }
                        }
                    },
                },
                "ingress": {
                    "main": {
                        "enabled": "true",
                        "hosts": [
                            {
                                "host": f"plex.{KUBE_NODE_HOST}",
                                "paths": [
                                    {
                                        "path": "/",
                                        "service": {"name": "plex", "port": 32400},
                                    }
                                ],
                            },
                        ],
                    },
                },
                "persistence": persistence_volumes,
            },
        ),
    )
    return


def organizr_chart():
    _, _, config_map = create_pvc(
        name="organizr-config",
        path="/mnt/8TB_01/kube_config/config/organizr",
        size="1Gi",
        access_mode="ReadWriteMany",
    )

    Chart(
        "organizr",
        config=ChartOpts(
            chart="organizr",
            version="7.0.1",
            fetch_opts=FetchOpts(
                repo="https://k8s-at-home.com/charts/",
            ),
            values={
                "image": {
                    "repository": "organizr/organizr",
                    "tag": "latest",
                    "pullPolicy": "IfNotPresent",
                },
                "env": {
                    "TZ": TIMEZONE,
                    "PUID": UID,
                    "PGID": GID,
                },
                "persistence": {
                    "config": config_map,
                },
                "ingress": {
                    "main": {
                        "enabled": "true",
                        "hosts": [
                            {
                                "host": f"organizr.{KUBE_NODE_HOST}",
                                "paths": [
                                    {
                                        "path": "/",
                                        "service": {"name": "organizr", "port": 80},
                                    }
                                ],
                            },
                        ],
                    },
                },
            },
        ),
    )
    return


def wiki_js_chart():
    _, _, config_map = create_pvc(
        name="wiki-config",
        path="/mnt/8TB_01/kube_config/config/wiki",
        size="1Gi",
        access_mode="ReadWriteMany",
        mount_path="/config",
    )

    _, _, data_map = create_pvc(
        name="wiki-data",
        path="/mnt/8TB_01/kube_config/data/wiki",
        size="1Gi",
        access_mode="ReadWriteMany",
        mount_path="/data",
    )

    Chart(
        "wikijs",
        config=ChartOpts(
            chart="wikijs",
            version="6.0.1",
            fetch_opts=FetchOpts(
                repo="https://k8s-at-home.com/charts/",
            ),
            values={
                "image": {
                    "repository": "linuxserver/wikijs",
                    "tag": "version-2.5.219",
                    "pullPolicy": "IfNotPresent",
                },
                "env": {
                    "TZ": TIMEZONE,
                    "PUID": UID,
                    "PGID": GID,
                    "DB_FILEPATH": "/data/db.sqlite",
                },
                "persistence": {
                    "config": config_map,
                    "data": data_map,
                },
                "ingress": {
                    "main": {
                        "enabled": "true",
                        "hosts": [
                            {
                                "host": f"wiki.{KUBE_NODE_HOST}",
                                "paths": [
                                    {
                                        "path": "/",
                                        "service": {"name": "wikijs", "port": 3000},
                                    }
                                ],
                            },
                        ],
                    },
                },
            },
        ),
    )
    return


def ml_flow_chart():
    minio_access_key = "minio"
    minio_secret_key = "minio123"  # pragma: allowlist secret

    _, minio_pvc, _ = create_pvc(
        name="mlflow-minio",
        path="/mnt/8TB_01/kube_config/config/mlflow_minio",
        size="8Gi",
        access_mode="ReadWriteOnce",
    )

    _ = Chart(
        "minio",
        config=ChartOpts(
            chart="minio",
            version="8.1.9",
            fetch_opts=FetchOpts(
                repo="https://charts.bitnami.com/bitnami",
            ),
            values={
                "podSecurityContext": {
                    "fsGroup": 1000,
                },
                "containerSecurityContext": {
                    "runAsUser": 1000,
                },
                "nameOverride": "mlflow-minio",
                "accessKey": {
                    "password": minio_access_key,
                },
                "secretKey": {
                    "password": minio_secret_key,
                },
                # "mode": "standalone",
                # "ingress": {
                #     "enabled": "true",
                #     "hostname": f"minio.{KUBE_NODE_HOST}",
                # },
                "persistence": {
                    "enabled": "false",
                    "existingClaim": minio_pvc.metadata.apply(lambda v: v["name"]),
                },
                "statefulset": {
                    "replicaCount": 1,
                },
                # "podAnnotations": {
                #     "prometheus.io/scrape": "true",
                #     "prometheus.io/path": "/minio/v2/metrics/cluster",
                #     "prometheus.io/port": 9000,
                # }
            },
        ),
    )

    # user = pulumi_minio.IamUser("python-user")

    mysql_root_password = "mlflow123"  # pragma: allowlist secret
    mysql_database = "mlflow"
    mysql_username = "mlflow"
    mysql_password = "mlflow123"  # pragma: allowlist secret

    _, mlflow_mysql_pvc, _ = create_pvc(
        name="mlflow-mysql",
        path="/mnt/8TB_01/kube_config/config/mlflow_mysql",
        size="8Gi",
        access_mode="ReadWriteOnce",
    )

    if True:
        _ = Chart(
            "mysql",
            config=ChartOpts(
                chart="mysql",
                version="8.8.10",
                fetch_opts=FetchOpts(
                    repo="https://charts.bitnami.com/bitnami",
                ),
                values={
                    "image": {"debug": True},
                    "nameOverride": "mlflow",
                    "architecture": "standalone",
                    "auth": {
                        "rootPassword": mysql_root_password,
                        "database": mysql_database,
                        "username": mysql_username,
                        "password": mysql_password,
                        "forcePassword": True,
                    },
                    "primary": {
                        "podSecurityContext": {
                            "fsGroup": 1000,
                        },
                        "containerSecurityContext": {
                            "runAsUser": 1000,
                        },
                        # "hostAliases": [
                        #     f"mlflow-mysql.{KUBE_NODE_HOST}"
                        # ],
                        "persistence": {
                            "enabled": True,
                            "existingClaim": mlflow_mysql_pvc.metadata.apply(
                                lambda v: v["name"]
                            ),
                        },
                    },
                    "secondary": {
                        "replicaCount": 0,
                    },
                },
            ),
        )

    if False:
        _ = Chart(
            "mlflow",
            config=ChartOpts(
                chart="mlflow",
                version="1.5.1",
                fetch_opts=FetchOpts(
                    repo="https://cetic.github.io/helm-charts",
                ),
                values={
                    "image": {
                        "repository": "sabman/mlflow",
                        "tag": "latest",
                    },
                    # "db": {
                    #     "host": "mysql",
                    #     "port": 3306,
                    #     "user": mysql_username,
                    #     "password": mysql_password,
                    #     "database": mysql_database,
                    # },
                    "minio": {
                        "accessKey": minio_access_key,
                        "secretKey": minio_secret_key,
                    },
                    "ingress": {
                        "enabled": "true",
                        "hosts": [f"mlflow.{KUBE_NODE_HOST}"],
                    },
                },
            ),
        )
    return


def apple_service():
    Pod(
        "apple",
        metadata={"name": "apple-app", "labels": {"app": "apple"}},
        spec={
            "containers": [
                {
                    "name": "apple-app",
                    "image": "hashicorp/http-echo",
                    "args": ["-text=apple"],
                }
            ]
        },
    )

    apple_service = Service(
        "apple-service",
        metadata={"name": "apple-service"},
        spec=ServiceSpecArgs(
            ports=[
                ServicePortArgs(
                    port=80,
                    target_port=5678,
                )
            ],
            selector={
                "app": "apple",
            },
        ),
    )

    Ingress(
        "apple-ingress",
        metadata={
            "name": "apple-ingress",
            "annotations": {},
        },
        spec=IngressSpecArgs(
            rules=[
                IngressRuleArgs(
                    host=f"apple.{KUBE_NODE_HOST}",
                    http=HTTPIngressRuleValueArgs(
                        paths=[
                            HTTPIngressPathArgs(
                                path="/",
                                backend=IngressBackendArgs(
                                    service_name=apple_service.metadata.apply(
                                        lambda v: v["name"]
                                    ),
                                    service_port=80,
                                ),
                            ),
                        ]
                    ),
                ),
            ],
        ),
    )
    return


def nginx_service():
    app_labels = {"app": "nginx"}
    Deployment(
        "nginx",
        metadata={"name": "nginx", "labels": app_labels},
        spec={
            "selector": {"match_labels": app_labels},
            "replicas": 1,
            "template": {
                "metadata": {"labels": app_labels, "name": "nginx"},
                "spec": {"containers": [{"name": "nginx", "image": "nginx"}]},
            },
        },
    )

    nginx_service = Service(
        "nginx-service",
        metadata={"name": "nginx-service"},
        spec=ServiceSpecArgs(
            ports=[ServicePortArgs(port=80, target_port=80)],
            selector={
                "app": "nginx",
            },
        ),
    )

    Ingress(
        "nginx-ingress",
        metadata={
            "name": "nginx-ingress",
            "annotations": {},
        },
        spec=IngressSpecArgs(
            rules=[
                IngressRuleArgs(
                    host=f"nginx.{KUBE_NODE_HOST}",
                    http=HTTPIngressRuleValueArgs(
                        paths=[
                            HTTPIngressPathArgs(
                                path="/",
                                backend=IngressBackendArgs(
                                    service_name=nginx_service.metadata.apply(
                                        lambda v: v["name"]
                                    ),
                                    service_port=80,
                                ),
                            ),
                        ]
                    ),
                ),
            ],
        ),
    )
    return


def kube_dashboard():
    Chart(
        "kubernetes-dashboard",
        config=ChartOpts(
            chart="kubernetes-dashboard",
            version="5.0.0",
            fetch_opts=FetchOpts(
                repo="https://kubernetes.github.io/dashboard/",
            ),
            values={
                "ingress": {"enabled": "true", "hosts": [f"kube-dash.{KUBE_NODE_HOST}"]}
            },
        ),
    )
    return


def gow_chart():
    Chart(
        "games-on-whales",
        config=ChartOpts(
            chart="games-on-whales",
            # namespace=media_namespace.metadata.apply(lambda v: v["name"]),
            fetch_opts=FetchOpts(
                repo="https://k8s-at-home.com/charts/",
            ),
            values={
                "steam": {
                    "enabled": False,
                },
                "firefox": {
                    "enabled": False,
                },
                "retroarch": {
                    "image": {
                        "repository": "dafrenchyman/retroarch",
                        "tag": "latest",
                        "pullPolicy": "IfNotPresent",
                    },
                },
                "xorg": {
                    "image": {
                        "repository": "dafrenchyman/xorg",
                        "tag": "latest",
                        "pullPolicy": "IfNotPresent",
                    },
                },
                "sunshine": {
                    "env": {
                        "TZ": TIMEZONE,
                        "PUID": UID,
                        "PGID": GID,
                        # "DISPLAY": "${XORG_DISPLAY}",
                        "NVIDIA_DRIVER_CAPABILITIES": "utility,video,graphics,display",
                        "NVIDIA_VISIBLE_DEVICES": GOW_GPU_UUID,
                    },
                },
            },
        ),
    )
    return


def cron_job_test():
    CronJob(
        resource_name="failing-cron",
        metadata={"name": "failing-cron"},
        spec=CronJobSpecArgs(
            schedule="*/5 * * * *",
            job_template=JobTemplateSpecArgs(
                spec=JobSpecArgs(
                    template=PodTemplateSpecArgs(
                        spec=PodSpecArgs(
                            restart_policy="Never",
                            containers=[
                                ContainerArgs(
                                    name="failing-cron",
                                    image="ubuntu",
                                    image_pull_policy="IfNotPresent",
                                    command=["/bin/bash", "-c", "exit 1;"],
                                )
                            ],
                        )
                    )
                )
            ),
        ),
    )

    CronJob(
        resource_name="failing-cron-single",
        metadata={"name": "failing-cron-single"},
        spec=CronJobSpecArgs(
            schedule="*/5 * * * *",
            concurrency_policy="Forbid",
            failed_jobs_history_limit=1,
            job_template=JobTemplateSpecArgs(
                spec=JobSpecArgs(
                    backoff_limit=0,
                    template=PodTemplateSpecArgs(
                        spec=PodSpecArgs(
                            restart_policy="Never",
                            containers=[
                                ContainerArgs(
                                    name="failing-cron-single",
                                    image="ubuntu",
                                    image_pull_policy="IfNotPresent",
                                    command=["/bin/bash", "-c", "exit 1;"],
                                )
                            ],
                        )
                    ),
                )
            ),
        ),
    )

    CronJob(
        resource_name="successful-cron",
        metadata={"name": "successful-cron"},
        spec=CronJobSpecArgs(
            schedule="*/5 * * * *",
            job_template=JobTemplateSpecArgs(
                spec=JobSpecArgs(
                    template=PodTemplateSpecArgs(
                        spec=PodSpecArgs(
                            restart_policy="Never",
                            containers=[
                                ContainerArgs(
                                    name="successful-cron",
                                    image="ubuntu",
                                    image_pull_policy="IfNotPresent",
                                    command=["/bin/bash", "-c", "exit 0;"],
                                )
                            ],
                        )
                    )
                )
            ),
        ),
    )
    return


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
        transmission_chart()

    if ENABLE_FRESH_RSS:
        freshrss_chart()

    if ENABLE_UBOOQUITY:
        ubooquity_chart()

    if ENABLE_WIKI_JS:
        wiki_js_chart()

    if ENABLE_DASHBOARD:
        kube_dashboard()

    if ENABLE_ORGANIZR:
        organizr_chart()

    if ENABLE_PLEX:
        plex_chart()

    if ENABLE_ML_FLOW:
        ml_flow_chart()

    if ENABLE_TEST_SERVICES:
        apple_service()
        nginx_service()

    if CRON_JOB_TEST:
        cron_job_test()
    return


if __name__ == "__main__":
    main()
