---
name: reference-emulator-writable-song-file
description: "How to make an adb-pushed song writable by the app on the API 36 emulator (tag/lyrics write tests), and craft tagged mp3s on the host."
metadata:
  node_type: memory
  type: reference
  originSessionId: 3eb82f20-c3e8-4cda-8e47-e6cee19550cd
  modified: 2026-11-05T10:18:37.092Z
---

Tag writes (lyrics, edit tags) go through jaudiotagger on the file path. On the Pixel_9 AVD (API 36) a file pushed with `adb push` is owned by `com.android.shell`, so the app's write fails (`MP3File.save` / `UnableToCreateFileException` in logcat) and the code takes its fallback path.

- `appops set com.amapps.media.music MANAGE_EXTERNAL_STORAGE allow` does NOT work: the app does not declare the permission, appops shows `default; rejectTime=...` (tried 2026-11-05, ticket 2084).
- What works: hand the MediaStore row to the app, then the app can write the file:
  `adb shell "content update --uri content://media/external/audio/media --bind owner_package_name:s:com.amapps.media.music --where \"_id=<id>\""`
  Find the id with `content query --uri content://media/external/audio/media --projection _id:title:owner_package_name`. Verified: after this, deleting lyrics emptied the embedded USLT (checked by pulling the file).
- `run-as ... test -w <path>` still says notwritable after the change; trust the app's behaviour / the pulled file instead.
- Build a test mp3 on the host: `ffmpeg -f lavfi -i "sine=frequency=440:duration=30" x.mp3`, then add tags with python `mutagen` (installed, 1.47): `ID3().add(USLT(encoding=3, lang='eng', desc='', text=...))`. Push to /sdcard/Music; MediaStore picks it up within seconds.
- Changing appops restarts the app (the player state is lost).
- App lyric copies live in `files/lyrics_v2_70/<songId>` (`adb shell run-as com.amapps.media.music ls files/lyrics_v2_70`).
- A 30s test song ends quickly and the player moves to the next song: actions on the Lyrics page then hit another song.
