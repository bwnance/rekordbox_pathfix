import os
from pyrekordbox import Rekordbox6Database
import time
import subprocess

try:
    db = Rekordbox6Database()
except:
    print("getting key")
    subprocess.run(["python -m pyrekordbox download-key"], shell=True)
    print("run me again!")
    exit(1)
deviceid = db.get_device()[0].ID
content = db.get_content()

songs = [
    c
    for c in content
    if c.Title is not None
    and c.FolderPath is not None
    and "soundcloud:" not in c.FolderPath
]
for song in songs:
    if "Users/Shared" in song.FolderPath and '.mp3' in song.FolderPath and '.mp3' in song.OrgFolderPath:
        continue
    org_path = song.OrgFolderPath
    if org_path:
        song.FolderPath = song.OrgFolderPath
    else:
        mp3_name = song.FolderPath.split("/")[-1]
        new_path = f"/Users/Shared/DJ_Tracks/{mp3_name}"
        song.FolderPath = new_path
    song.DeviceID = deviceid
    if not song.FolderPath:
        print(f"song {song.Title} has no folder path!")
    if ".mp3" not in song.FolderPath:
        song_pieces = song.FolderPath.split(".")
        song_pieces[-1] = "mp3"
        new_path = ".".join(song_pieces)
        
        if not os.path.exists(new_path):
            if 'MergeFX' in song.FileNameL or song.Artist.Name in ['rekordbox', 'Loopmasters']:
                db.delete(song)
                continue
            print()
            print(f"song.FolderPath: {song.FolderPath}")
            print(f"title: {song.Title}")
            print(f"non-mp3 doesn't exist: {new_path}")
            print()
        else:
            # pass
            print(f"renamed {song.FolderPath} to {new_path}")
            song.FolderPath = new_path
            song.OrgFolderPath = new_path
            song.ServiceID = 0
            song.DeviceID = deviceid
success = False
try:
    db.commit()
    success = True
except:
    print("rekordbox is probably running, killing it and trying again")
    subprocess.call(["osascript -e 'quit app \"rekordbox\"'"], shell=True)
    # sleep for a bit to ensure the app has time to close
    for i in range(20):
        print(f"Waiting for rekordbox to close...{i}")
        time.sleep(1)
        try:
            db.commit()
            success = True
            break
        except:
            continue
if success:
    print("rewrote all song paths!")
else:
    print("failed to close rekordbox! please retry.")
