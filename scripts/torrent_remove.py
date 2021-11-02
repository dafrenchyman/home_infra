"""
Transmission can sometimes crash and will try to download old torrents it
has already downloaded and removed. This script will manually go through
and check a few folders and see if you've already downloaded those
files and manually remove the torrent and it's ability to resume so
you won't run into the problem again.
"""
import os
from glob import glob

import libtorrent
from transmission_rpc import Client

FILE_EXTENSIONS = ["mp4"]

FOLDERS_TO_CHECK = [
    "/mnt/8TB_01/docker/volumes/transmission/config/completed/",
]

TORRENT_FOLDER = (
    "/mnt/8TB_01/docker/volumes/transmission/config/transmission-home/torrents/"
)


def main():
    # Connect to transmission
    c = Client(
        host="localhost",
        port=9091,
        username="transmission",
        password="password",  # pragma: allowlist secret
    )
    torrents = c.get_torrents()

    # Get list of files to match on
    all_available_files = []
    for folder in FOLDERS_TO_CHECK:
        curr = [y for x in os.walk(folder) for y in glob(os.path.join(x[0], "*.*"))]
        all_available_files += [x.replace(folder, "") for x in curr]

    # Loop through all the torrents
    total_count_to_stop = 0

    for torrent_id, torrent in enumerate(torrents):
        file_exists_count = 0
        if torrent.status in ["downloading", "check pending"]:
            total_files = len(torrent.files())
            for file in torrent.files():
                if file.name in all_available_files:
                    file_exists_count += 1

            # If we have all files stop the torrent
            if file_exists_count == total_files and total_files > 0:
                torrent.stop()
                print(torrent.name)
                c.remove_torrent(torrent.hashString, delete_data=True)
                total_count_to_stop += 1

                # Get all the torrent files
                torrent_files = glob(os.path.join(TORRENT_FOLDER, "*.torrent"))

                # Remove the associated torrent file
                for torrent_file in torrent_files:
                    info_file_count = 0
                    info = libtorrent.torrent_info(torrent_file)
                    for info_file in info.files():
                        for file in torrent.files():
                            if info_file.path == file.name:
                                info_file_count += 1
                    if total_files == info_file_count and info_file_count > 0:
                        if os.path.exists(torrent_file):
                            os.remove(torrent_file)
                        break

    print(total_count_to_stop)


if __name__ == "__main__":
    main()
