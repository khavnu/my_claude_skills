---
name: reference-separation-debug-toolkit
description: "Cách đo và debug separation — log tag, file test trên máy, lệnh chạy suite; dựng lại phiên đo không mất thời gian"
metadata: 
  node_type: memory
  type: reference
  originSessionId: bdb5dbc3-71e8-4f83-aed4-d682449c6e8a
  modified: 2026-09-22T10:33:10.328Z
---

## Log đã cài sẵn trong app

`SeparationSessionController.logRunTiming()` in 3 mốc, tag **`SeparationTiming`** (mức `Timber.i`):

```
engine ready after 18 ms                  ← prepare() xong, CHƯA inference (model load + probe)
first segment ready after 4270 ms         ← người dùng nghe được tiếng đầu tiên
run finished after 153608 ms for 953182 ms of audio (TwoStems, 64 segments, 161 ms/audio-sec)
```

Đọc: `adb -s <serial> logcat -d | grep SeparationTiming`

## Log của lib (tự có, không cần thêm)

```
MediaCodecPcmDecoder[...]  decodeLoop finished: total=  sinkTime=  pureDecodeTime=
StreamStemSplitEngine[...] sourceCache filled N frames in Xms
StreamStemSplitEngine[...] separateSegment[i] -> N stems
SpleeterStemSeparator[...] separate(N frames): allocateBuffers= runForMultipleInputsOutputs= total=
```

Đối chiếu timestamp giữa `decodeLoop finished` và `separateSegment[0]` là cách phát hiện decode có
đang chặn inference không — xem [[pattern-short-file-hides-serialization]].

**Huawei chặn log ứng dụng** — logcat chỉ ra log hệ thống, không debug bằng logcat trên máy đó được.

## File test trên máy (Pixel 9)

`/sdcard/Music/MusicEditor/AudioMerge/` — KHÔNG phải `Music/AudioMerge` trần:
- `Merge_20260822_133848i.mp3` — **953s (15'53")**, 15.4 MB → file chuẩn để đo throughput
- `Merge_20260824_083734.mp3` — **73 phút**, 76 MB → file cực đại, có giọng hát (dùng cho test tagger)

`/sdcard/Music/MusicEditor/AudioVolume/Volume_large.mp3` — **3221s (53'41")**, 51 MB → file dài QA
hay dùng để bắt lỗi race/timeout. Không nằm chung thư mục với 2 file trên. **CÓ tiếng thật**
(`max_volume -30.6 dB`) — nghe như im lặng trên loa điện thoại nên hay bị báo nhầm là "no audio";
KHÔNG dùng được để test nhánh silence.

`/sdcard/Music/silent_large.mp3` — **3200s (53'20")**, im lặng tuyệt đối (`peak=0.0`) → đúng file để
test nhánh No audio. Tạo lại bằng:
`ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 3200 -c:a libmp3lame -b:a 128k silent_large.mp3`

Đo `getWaveformData` (silence probe của Separation) bằng
`SilenceProbeTimingProbeTest` (androidTest/probe), đọc log tag **`SilenceProbe`**. Pixel 9 đo được
**~310x realtime, tuyến tính theo độ dài**: 4' → 0.7s · 15'53" → 3.0s · 53'41" → 10.5s. Trần
`WaveformExtractor.EXTRACT_TIMEOUT_MS` = 40s ⇒ trên Pixel 9 tương đương 3.4 giờ audio, không chạm
tới được.

Mất file thì tự tạo bằng `RepeatedPcmClip` (androidTest) — nối MP3 thô KHÔNG dùng được, decoder đọc
độ dài từ header đầu nên 8 bản 12s vẫn ra 12s.

## Lệnh hay dùng

```bash
export PATH=$PATH:$HOME/Android/Sdk/platform-tools
./gradlew :app:installDebug && adb -s <serial> logcat -c     # cài + xoá log, rồi bấm tay

# ba source set, luôn đủ cả ba
./gradlew :app:compileDebugKotlin :app:compileDebugUnitTestKotlin :app:compileDebugAndroidTestKotlin

# device test: máy ≤4GB phải chạy TỪNG LỚP, chạy cả package sẽ chết giữa chừng
adb -s <serial> shell am instrument -w -e class <FQCN> \
  com.tmedilab.sounditor.music.audio.editor.test/androidx.test.runner.AndroidJUnitRunner
```

## Máy đã đo (2026-09-11)

Pixel 9 (11.8 GB) · Z Flip 3 (7.4) · Realme RMX3710 (5.7) · Huawei INE-LX2r (3.63) · Samsung M20 (2.7).
Chi tiết ngưỡng: [[project-separation-device-limits]]. Bảng đầy đủ: `docs/benchmark/README.md`.

## Trạng thái nhánh

`feature/separation` đã rebase lên `release/1.1` ngày 2026-09-11. Nhánh cứu hộ
`backup/separation-before-rebase` giữ bản trước rebase — xoá được khi đã yên tâm.

Ba chỗ phải gộp tay khi rebase (nếu rebase lại sẽ gặp lại): proto field number (separation phải
dùng **24**, release/1.1 đã chiếm 22-23), `ToolDestination` đã chuyển sang `domain/model`,
`SelectAudioViewModel` đã thành AssistedInject. `git add -A` giữa lúc rebase sẽ nuốt
`audio_stem_split/native_build/custom/tensorflow_src` thành embedded repo — add từng file.
