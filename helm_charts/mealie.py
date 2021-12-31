from common.helpers import create_pvc
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts


def mealie(config_folder_root: str, hostname: str, timezone: str, uid=1000, gid=1000):
    _, _, config_map = create_pvc(
        name="mealie-config",
        path=f"{config_folder_root}/mealie",
        size="3Gi",
        access_mode="ReadWriteMany",
        mount_path="/app/data/",
    )

    Chart(
        "mealie",
        config=ChartOpts(
            chart="mealie",
            version="3.2.0",
            fetch_opts=FetchOpts(
                repo="https://k8s-at-home.com/charts/",
            ),
            values={
                "env": {
                    "TZ": timezone,
                    "PUID": uid,
                    "PGID": gid,
                    "DB_TYPE": "sqlite",
                },
                "persistence": {
                    "config": config_map,
                },
                "ingress": {
                    "main": {
                        "enabled": "true",
                        "hosts": [
                            {
                                "host": f"mealie.{hostname}",
                                "paths": [
                                    {
                                        "path": "/",
                                        "service": {"name": "mealie", "port": 80},
                                    }
                                ],
                            },
                        ],
                    },
                },
                "postgres": {"enabled": "false"},
            },
        ),
    )
    return
