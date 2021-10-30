from common.helpers import create_pvc
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts


def freshrss(config_folder_root: str, hostname: str, timezone: str, uid=1000, gid=1000):
    _, _, config_map = create_pvc(
        name="freshrss-config",
        path=f"{config_folder_root}/freshrss",
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
                                "host": f"freshrss.{hostname}",
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
