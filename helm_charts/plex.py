import json

from common.helpers import create_pvc
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts


def plex(
    plex_shares_json: str,
    config_folder_root: str,
    cidr: str,
    hostname: str,
    timezone: str,
    uid=1000,
    gid=1000,
):
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
    plex_shares = json.loads(plex_shares_json)
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
        path=f"{config_folder_root}/plex-config",
        size="100Gi",
        access_mode="ReadWriteMany",
        mount_path="/config",
    )
    persistence_volumes["plex-config"] = config_map

    _, _, transcode_map = create_pvc(
        name="plex-transcode",
        path=f"{config_folder_root}/plex-transcode",  # pragma: allowlist secret
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
                    "TZ": timezone,
                    "PUID": uid,
                    "PGID": gid,
                    "PLEX_UID": uid,
                    "PLEX_GID": gid,
                    "ALLOWED_NETWORKS": f"{cidr},192.168.10.0/24",
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
                                "host": f"plex.{hostname}",
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
