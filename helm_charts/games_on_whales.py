from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts


def games_on_whales(timezone, uid=1000, gid=1000):
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
                    "enabled": True,
                    # "image": {
                    #     "repository": "dafrenchyman/retroarch",
                    #     "tag": "latest",
                    #     "pullPolicy": "IfNotPresent",
                    # },
                },
                "xorg": {
                    "enabled": False,
                    "display": ":0",
                    # "image": {
                    #     "repository": "dafrenchyman/xorg",
                    #     "tag": "latest",
                    #     "pullPolicy": "IfNotPresent",
                    # },
                },
                "sunshine": {
                    "env": {
                        "TZ": timezone,
                        "PUID": uid,
                        "PGID": gid,
                        # "DISPLAY": "${XORG_DISPLAY}",
                        # "NVIDIA_DRIVER_CAPABILITIES": "utility,video,graphics,display",
                        # "NVIDIA_VISIBLE_DEVICES": nvidia_devices,
                    },
                },
            },
        ),
    )
    return
