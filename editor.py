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

songs = [c for c in content if c.Title is not None and c.FolderPath is not None and 'soundcloud:' not in c.FolderPath]
for song in songs:
    if 'Users/Shared' in song.FolderPath and song.DeviceID == deviceid:
        continue
    org_path = song.OrgFolderPath
    if org_path:
        song.FolderPath = song.OrgFolderPath
    else:
        mp3_name = song.FolderPath.split("/")[-1]
        new_path = f"/Users/Shared/DJ_Tracks/{mp3_name}"
        song.FolderPath = new_path
    song.DeviceID = deviceid
success = False
try:
    db.commit()
    success = True
except:
    print("rekordbox is probably running, killing it and trying again")
    subprocess.call(["osascript -e 'quit app \"rekordbox\"'"], shell=True)
    # sleep for a bit to ensure the app has time to close
    for i in range(10):
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