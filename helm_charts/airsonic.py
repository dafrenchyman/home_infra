from common.helpers import create_pvc
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts


def airsonic(config_folder_root: str, hostname: str, timezone: str, uid=1000, gid=1000):
    _, _, config_map = create_pvc(
        name="airsonic-config",
        path=f"{config_folder_root}/airsonic",
        size="3Gi",
        access_mode="ReadWriteMany",
        mount_path="/var/airsonic",
    )

    _, _, pool_map = create_pvc(
        name="airsonic-music-pool",
        path="/mnt/SnapSsdArray_01/pool/Music",
        size="10Gi",
        access_mode="ReadWriteMany",
        mount_path="/var/music",
    )

    _, _, music_map = create_pvc(
        name="airsonic-music",
        path="/mnt/SnapSsdArray_01/SnapDisk_4TB_05/Music",
        size="10Gi",
        access_mode="ReadWriteMany",
        mount_path="/mnt/SnapSsdArray_01/SnapDisk_4TB_05/Music",
    )

    Chart(
        "airsonic",
        config=ChartOpts(
            chart="airsonic",
            version="6.0.0",
            fetch_opts=FetchOpts(
                repo="https://k8s-at-home.com/charts/",
            ),
            values={
                "env": {
                    "TZ": timezone,
                    "PUID": uid,
                    "PGID": gid,
                },
                "persistence": {
                    "config": config_map,
                    "music": music_map,
                    "pool": pool_map,
                },
                "ingress": {
                    "main": {
                        "enabled": "true",
                        "hosts": [
                            {
                                "host": f"airsonic.{hostname}",
                                "paths": [
                                    {
                                        "path": "/",
                                        "service": {"name": "airsonic", "port": 4040},
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
