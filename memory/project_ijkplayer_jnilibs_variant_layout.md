---
name: project_ijkplayer_jnilibs_variant_layout
description: ":ijkplayer-java .so nằm per-buildType (debug = bản không license check, release = bản khoá theo cert greenbanana_3); cách phân biệt 2 bản bằng strings/readelf."
metadata: 
  node_type: memory
  type: project
  originSessionId: 65f6c61d-676f-40d0-9fcf-114036fb906e
  modified: 2026-09-03T09:56:18.242Z
---

`:ijkplayer-java` không dùng `src/main/jniLibs` — nó phải **rỗng**. Mỗi build type mang đủ
bộ 3 lib (`libijkplayer.so`, `libijksdl.so`, `libijkffmpeg.so`) × 4 ABI:

- `src/debug/jniLibs/` → bản build **không có license check** → chạy với key nào cũng được
- `src/release/jniLibs/` → bản có license check, chỉ nhận cert keystore `greenbanana_3`
  (SHA256 `F9:13:D4:47:…:7F:B8:A8:C6`, subject `CN=Nguyen, OU=Hao, O=Tower, L=Thanh Xuan, ST=Hanoi, C=84`)

Không cần khai `sourceSets {}` — `src/<buildType>/jniLibs` là srcDir mặc định của AGP.
Lý do main phải rỗng: một lib có mặt ở cả `main` và một build type → jniLibs merge fail
"more than one file with OS independent path". Hai bộ KHÔNG thay thế được nhau: cắm .so
release vào debug APK sign bằng local debug key sẽ fail check lúc runtime.

**Phân biệt .so cần key hay không** (khi nhận set mới từ người build native):

```bash
strings -a libijkplayer.so | grep -cE "license check|app_sign|currentActivityThread|content/pm/Signature"
strings -a libijkplayer.so | grep -cE "^30820[0-9a-f]{3}30820"   # cert X.509 hex nhúng
```

Bản cần key: markers = 3-4, certs >= 1, có hex string ~1742 ký tự. Bản không key: 0/0, max hex ~8.
Check chỉ nằm trong `libijkplayer.so`, `libijksdl`/`libijkffmpeg` luôn sạch.
Luôn chạy kèm **control** trên 2 bản đã biết chắc để loại false negative.

Decode cert nhúng rồi so byte với keystore:
```bash
strings -a x.so | grep -E "^30820[0-9a-f]{3}30820" | head -1 | xxd -r -p > cert.der
openssl x509 -inform DER -in cert.der -noout -subject -fingerprint -sha256
```

Mechanism: `audio_editor/src/main/cpp/license_verify.c` — JNI reflect
`ActivityThread.currentActivityThread().getApplication()` → `PackageInfo.signatures[0].toCharsString()`
→ `strcmp` với hex cert hardcode. (Bản trong `:audio_editor` đang bị disable bằng early
`return LICENSE_OK`, còn TODO — khác với bản compile vào ijkplayer .so.)

Liên quan: [[project_agp_stale_jni_merger_xml]], [[project_ffmpeg_cpp_source_kept]]
