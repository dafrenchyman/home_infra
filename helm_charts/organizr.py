from common.helpers import create_pvc
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts


def organizr(config_folder_root: str, hostname: str, timezone: str, uid=1000, gid=1000):
    _, _, config_map = create_pvc(
        name="organizr-config",
        path=f"{config_folder_root}/organizr",
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
                    "TZ": timezone,
                    "PUID": uid,
                    "PGID": gid,
                },
                "persistence": {
                    "config": config_map,
                },
                "ingress": {
                    "main": {
                        "enabled": "true",
                        "hosts": [
                            {
                                "host": f"organizr.{hostname}",
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
