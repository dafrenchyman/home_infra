from common.helpers import create_pvc
from pulumi_kubernetes.core.v1 import Secret
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


def transmission(
    config_folder_root: str,
    watch_folder: str,
    completed_folder: str,
    incomplete_folder: str,
    vpn_provider: str,
    vpn_username: str,
    vpn_password: str,
    vpn_config: str,
    cidr: str,
    hostname: str,
    timezone,
    uid=1000,
    gid=1000,
):
    transmission_config_volume, transmission_config_claim, _ = create_pvc(
        name="transmission-config",
        path=f"{config_folder_root}/transmission",
        size="1Gi",
        access_mode="ReadWriteMany",
    )

    transmission_watch_volume, transmission_watch_claim, _ = create_pvc(
        name="transmission-watch",
        path=watch_folder,
        size="20Gi",
        access_mode="ReadWriteMany",
    )

    transmission_incomplete_volume, transmission_incomplete_claim, _ = create_pvc(
        name="transmission-incomplete",
        path=incomplete_folder,
        size="100Gi",
        access_mode="ReadWriteMany",
    )

    transmission_completed_volume, transmission_completed_claim, _ = create_pvc(
        name="transmission-completed",
        path=completed_folder,
        size="100Gi",
        access_mode="ReadWriteMany",
    )

    clean_vpn_provider = vpn_provider.lower().replace("_", "-")

    Secret(
        f"{clean_vpn_provider}-transmission-secret",
        metadata={
            "name": f"{clean_vpn_provider}-transmission-secret",
        },
        type="kubernetes.io/basic-auth",
        string_data={
            "username": vpn_username,
            "password": vpn_password,
        },
    )

    transmission_chart = Chart(
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
                    "tag": "4.0",
                    "pullPolicy": "IfNotPresent",
                },
                "env": [
                    {"name": "CREATE_TUN_DEVICE", "value": "true"},
                    {"name": "PUID", "value": uid},
                    {"name": "PGID", "value": gid},
                    {"name": "LOCAL_NETWORK", "value": cidr},
                    {"name": "OPENVPN_PROVIDER", "value": vpn_provider},
                    {"name": "OPENVPN_CONFIG", "value": vpn_config},
                    {"name": "OPENVPN_USERNAME", "value": vpn_username},
                    {"name": "OPENVPN_PASSWORD", "value": vpn_password},
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
                    # {
                    #     "name": "TRANSMISSION_WEB_UI",
                    #     "value": "default",
                    # },
                    {"name": "WEBPROXY_ENABLED", "value": "false"},
                    {"name": "TZ", "value": timezone},
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
                        "name": transmission_completed_volume.metadata.apply(
                            lambda v: v["name"]
                        ),
                        "persistentVolumeClaim": {
                            "claimName": transmission_completed_claim.metadata.apply(
                                lambda v: v["name"]
                            )
                        },
                    },
                    {
                        "name": transmission_incomplete_volume.metadata.apply(
                            lambda v: v["name"]
                        ),
                        "persistentVolumeClaim": {
                            "claimName": transmission_incomplete_claim.metadata.apply(
                                lambda v: v["name"]
                            )
                        },
                    },
                    {
                        "name": transmission_watch_volume.metadata.apply(
                            lambda v: v["name"]
                        ),
                        "persistentVolumeClaim": {
                            "claimName": transmission_watch_claim.metadata.apply(
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
                        "name": transmission_watch_volume.metadata.apply(
                            lambda v: v["name"]
                        ),
                        "mountPath": "/data/watch",
                    },
                    {  # Incomplete Torrents
                        "name": transmission_incomplete_volume.metadata.apply(
                            lambda v: v["name"]
                        ),
                        "mountPath": "/data/incomplete",
                    },
                    {  # Completed Torrents
                        "name": transmission_completed_volume.metadata.apply(
                            lambda v: v["name"]
                        ),
                        "mountPath": "/data/completed",
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
                    host=f"transmission.{hostname}",
                    http=HTTPIngressRuleValueArgs(
                        paths=[
                            HTTPIngressPathArgs(
                                path="/",
                                path_type="Prefix",
                                backend=IngressBackendArgs(
                                    service=IngressServiceBackendArgs(
                                        name=transmission_chart.get_resource(
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
