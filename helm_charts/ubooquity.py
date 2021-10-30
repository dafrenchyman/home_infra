from common.helpers import create_pvc
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts


def ubooquity(
    config_folder_root: str, hostname: str, timezone: str, uid=1000, gid=1000
):
    _, _, config_map = create_pvc(
        name="ubooquity-config",
        path=f"{config_folder_root}/ubooquity",
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
                    "TZ": timezone,
                    "PUID": uid,
                    "PGID": gid,
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
                                "host": f"ubooquity.{hostname}",  # /ubooquity/
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
                                "host": f"ubooquity-admin.{hostname}",  # /ubooquity/admin
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
