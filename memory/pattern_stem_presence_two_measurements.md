---
name: pattern-stem-presence-two-measurements
description: Cảnh báo "stem rỗng" cần HAI phép đo bù nhau — StemLevel (dB) không trả lời được cho vocals, YAMNet tagger không trả lời được cho bass
metadata:
  type: project
---

Lib `audio_stem_split` có hai cách trả lời "track này có thiếu nhạc cụ nào không", và chúng
**bù nhau chứ không thay thế nhau**. Phân công đã chốt trong `SeparationResultViewModel.absentStems()`:

| Stem | Nguồn | Lý do (số đo của lib) |
|---|---|---|
| vocals | tagger YAMNet | StemLevel absent/present chỉ cách 1.0 dB — Spleeter chuẩn hoá mask sum-to-one nên stem vocals không bao giờ im |
| drums | StemLevel | 38.8 dB tách biệt; tagger đọc sát noise floor (0.010/0.002), tác giả ghi "provisional" |
| bass | StemLevel | AudioSet chỉ có `Bass guitar`, không bắt synth/electric bass |
| other, instrumental | không ai | nói gì cũng là đoán |

API dùng sẵn, KHÔNG sửa lib: `SegmentStatusSnapshot.stemLevels` + `Map<String, StemLevel>.likelyAbsent()`
(ngưỡng 32 dB dưới stem to nhất, `UNDETECTABLE_STEMS = {vocals, other}`), và
`AudioTagger.tag(context, uri)` từ `:presence:yamnet`.

**Chi phí đã đo:** APK release 233.4 → 374.8 MB. Model YAMNet chỉ 15.4 MB; phần lớn là
`libonnxruntime.so` 125.7 MB cho 4 ABI (x86+x86_64 chiếm 114.1 MB trong tổng native 195.4 MB).
`onnxruntime-mobile` nhỏ hơn 88% nhưng **không đọc được .onnx** (chỉ .ort — verify bằng symbol
`onnx::ModelProto` vắng mặt trong binary) và bản cuối là 1.18.0/2024-05. Quyết định: **để nguyên,
xử lí ABI lúc publish**.

**Bẫy khi test:** file do `mixStems()` tạo nằm trong cache của engine — start run mới sẽ quét sạch
thư mục đó → `SourceNotReadable`. Phải copy ra `cacheDir` trước. Và `first {}` trên
`observeSeparation` đóng collection → engine tear down session → `save()` trả `AssembleFailed`;
phải chạy qua `SeparationSessionController`.

Liên quan: [[project_audio_separation]], [[reference_waveform_data_not_normalized]], [[reference_lib_knowledge_in_repo]]
