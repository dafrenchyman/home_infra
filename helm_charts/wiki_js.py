from common.helpers import create_pvc
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts


def wiki_js(
    config_folder_root: str,
    data_folder_root: str,
    hostname: str,
    timezone,
    uid=1000,
    gid=1000,
):
    _, _, config_map = create_pvc(
        name="wiki-config",
        path=f"{config_folder_root}/wiki",
        size="1Gi",
        access_mode="ReadWriteMany",
        mount_path="/config",
    )

    _, _, data_map = create_pvc(
        name="wiki-data",
        path=f"{data_folder_root}/wiki",
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
                    "TZ": timezone,
                    "PUID": uid,
                    "PGID": gid,
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
                                "host": f"wiki.{hostname}",
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
