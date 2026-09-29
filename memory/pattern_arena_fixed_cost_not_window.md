---
name: pattern-arena-fixed-cost-not-window
description: "Rút segment xuống dưới 8s KHÔNG trả thêm arena — đã đo 6s, chỉ được 4-12%; ~1GB là chi phí cố định của TFLite+Flex, app đối thủ làm cùng việc ở 400MB"
metadata: 
  node_type: memory
  type: project
  originSessionId: 181345e5-d43e-4a25-872c-cf1d17436e40
  modified: 2026-09-25T06:33:20.587Z
---

> **Sửa 2026-09-29:** chi phí cố định ~1 GB đã biến mất khi sync lib sang mask model (STFT chạy bằng Kotlin,
> không còn Flex/TF runtime). Trên chính A20s: 2-stem Rss ~480–512 MB, 4-stem chạy trọn file ở ~840 MB.
> Nên **test lại #432 sau khi merge**. Kết luận "segment không phải đòn bẩy RAM" vẫn đúng (arena tính theo patch).

Ticket #432 (2026-09-25, A20s SM-A207F 2.86 GB, 2-stem). QC báo "crash khi kéo playhead lúc
waveform đang load". **Không phải crash** — `lmkd` SIGKILL, đúng triệu chứng
[[pattern-unload-model-native-heap]] đã mô tả.

## Segment length KHÔNG phải đòn bẩy nữa

[[project-separation-device-limits]] ghi sweep 15s→8s trả 723 MB (4-stem, Pixel 9). Cám dỗ tự nhiên
là đi tiếp xuống 6s. **Đã đo, không được.** Cùng file `Trim_h.mp3` (00:33), A20s, 2-stem:

| | 8s | 6s |
|---|---:|---:|
| `Alloc` đỉnh | 1 068 047 kB | 1 047 122 kB |
| `Alloc` sàn lúc tách | ~1 022 000 kB | ~899 000–985 000 kB |
| `Rss` đỉnh | 1 212 932 kB | 1 312 480 kB |

Cắt cửa sổ 25% chỉ trả 4–12% arena, đỉnh RSS không nhúc nhích. **Dưới tuyến tính** → phần lớn ~1 GB
là chi phí cố định của interpreter đang nạp, không phải tensor tỉ lệ input. Ngoại suy xuống 3s cũng
chỉ về ~750–800 MB. Đừng thử lại đường này.

## Độ dài file cũng không liên quan

File 00:33 và file 05:07 tốn **y hệt** ~1.07 GB. Loại được `sourceCache` (14.6M frame ≈ 117 MB cho
file 5 phút) khỏi danh sách nghi phạm. Model `2stems.tflite` 52.5 MB được mmap → chỉ 58 MB ở
`.apk mmap`, cũng không phải nó. `dumpsys meminfo` lúc tách: **989/1243 MB = 80% nằm ở Native Heap**.

## Đối thủ làm cùng việc ở 400 MB

Cài trên chính máy này để so (2026-09-25):

| | app mình | `ai.vocal.remover.splitter.karaoke.instrumental` | `io.jkhddev.music_player` |
|---|---|---|---|
| runtime | `libtensorflowlite_flex_jni.so` **12.1 MB** + `libtensorflowlite_jni.so` 2.6 MB | `libSpleeter.so` **0.49 MB** | `libMNN.so` **1.9 MB** |
| peak RSS khi tách | **1 213–1 320 MB** | **476 MB** (dao động 380↔490, có nhả giữa chunk) | chưa đo |

App thứ 2 chạy **đúng họ model Spleeter** mà hết 476 MB. Nó cũng **không stream** — chặn màn hình
"Splitting the track" tới khi xong, nên không có bài toán seek-vào-vùng-chưa-tách.

Nghi phạm còn lại: `TfLiteFlexDelegate`. Log in `Replacing 8 out of 337 node(s) with delegate
(TfLiteFlexDelegate)` mỗi lần dựng interpreter — 8/337 node không convert được sang TFLite thuần,
và để chạy 8 node đó phải kéo nguyên runtime TensorFlow + eager context. **Chưa chứng minh** đó là
thủ phạm của ~1 GB; mới là ứng viên duy nhất còn đứng sau khi loại hết cái khác.

## Vì sao chỉ vài lần kéo là chết

Không phải rò bộ nhớ dồn — `Alloc` rơi 1 068 MB → 33 MB khi run xong, `unloadModel()` chạy đúng.
App đơn giản là chạy nền ở 1.0–1.2 GB trên máy 2.86 GB (`MemAvailable` còn ~700 MB), và RSS **tự**
dao động 945–1175 MB không cần ai đụng. Seek vào vùng chưa tách → `requestSegment` preempt →
`SpleeterStemSeparator.kt:118` `needsRebuildAfterCancel` → đóng interpreter cũ, dựng cái mới (một
lần dựng = +854 MB). Nền đã sát trần nên một cú là đủ.

## Cách đo lại trong 10 giây

```bash
PID=$(adb shell pidof com.tmedilab.sounditor.music.audio.editor)
adb shell dumpsys meminfo $PID | awk '/^  Native Heap/ {print "Rss="$7, "Size="$8, "Alloc="$9}'
```
Cột dễ đọc nhầm: `$7`=Rss, `$8`=Heap Size, `$9`=Heap Alloc. `Alloc` mới đáng tin — `Rss` nhiễu vì
allocator giữ page sau khi free (sau `unloadModel` Alloc về 33 MB mà Rss còn 544–991 MB).

Bằng chứng lmkd: `grep "Reclaim 'com.tmedilab" logcat.txt` → `oom_adj 0, state 2, to free 1321228kB;
reason: min2x watermark is breached even after kill`, sau khi đã giết 24 process khác từ oom_adj 999.

Liên quan: [[pattern-unload-model-native-heap]], [[project-separation-device-limits]],
[[project-separation-open-items]]
