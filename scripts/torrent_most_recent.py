"""
Transmission can sometimes crash and will try to download old torrents it
has already downloaded and removed. This script will manually go through
and check a few folders and see if you've already downloaded those
files and manually remove the torrent and it's ability to resume so
you won't run into the problem again.
"""
from datetime import datetime

from transmission_rpc import Client


def main():
    # Connect to transmission
    c = Client(
        # host="localhost",
        # port=9091,
        host="transmission.192.168.10.40.nip.io",
        port=80,
        username="transmission",
        password="password",  # pragma: allowlist secret
        timeout=120,
    )
    torrents = c.get_torrents()
    print(f"Total Torrents: {len(torrents)}")

    # Loop through all the torrents
    torrent_data = []
    for torrent in torrents:
        torrent_data.append(
            [torrent.id, datetime.fromtimestamp(int(torrent.dateCreated))]
        )

    sorted_torrent_data = sorted(torrent_data, key=lambda t: t[1], reverse=True)
    for idx, torrent in enumerate(sorted_torrent_data):
        c.change_torrent(torrent[0], queuePosition=idx)


if __name__ == "__main__":
    main()
