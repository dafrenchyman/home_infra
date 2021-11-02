from common.helpers import create_pvc
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts


def nzbhydra2(
    config_folder_root: str,
    data_folder_root: str,
    hostname: str,
    timezone,
    uid=1000,
    gid=1000,
):
    _, _, config_map = create_pvc(
        name="nzbhydra2-config",
        path=f"{config_folder_root}/nzbhydra2",
        size="1Gi",
        access_mode="ReadWriteMany",
        mount_path="/config",
    )

    _, _, data_map = create_pvc(
        name="nzbhydra2-data",
        path=f"{data_folder_root}/nzbhydra2",
        size="1Gi",
        access_mode="ReadWriteMany",
        mount_path="/downloads",
    )

    Chart(
        "nzbhydra2",
        config=ChartOpts(
            chart="nzbhydra2",
            version="10.0.1",
            fetch_opts=FetchOpts(
                repo="https://k8s-at-home.com/charts/",
            ),
            values={
                "image": {
                    "repository": "linuxserver/nzbhydra2",
                    "tag": "3.17.3",
                },
                "env": {
                    "TZ": timezone,
                    "PUID": uid,
                    "PGID": gid,
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
                                "host": f"nzbhydra2.{hostname}",
                                "paths": [
                                    {
                                        "path": "/",
                                        "service": {"name": "nzbhydra2", "port": 5076},
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
