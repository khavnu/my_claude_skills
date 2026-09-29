---
name: pattern-short-file-hides-serialization
description: Đo throughput bằng file ngắn giấu mất lỗi tuần tự hoá — decode chặn inference 62s chỉ lộ ra ở file 15 phút
metadata: 
  node_type: memory
  type: project
  originSessionId: bdb5dbc3-71e8-4f83-aed4-d682449c6e8a
  modified: 2026-09-11T09:57:53.081Z
---

`limitedParallelism(1)` truyền cho `StreamStemSplitEngine` khiến decode độc chiếm slot duy nhất, nên
segment 0 phải đợi decode XONG TOÀN BỘ file. Trên file 15'53": chunk đầu 65.3s (62.6s là chờ decode,
2.2s tách thật). Sửa thành 2 slot → chunk đầu 4.3s, tổng 198.7s → 153.6s.

Lib chạy hai loại việc trên cùng dispatcher: decode đổ đầy PCM cache + inference đọc ra. Lib tự tuần
tự hoá inference bằng session worker đơn, nên ép parallelism=1 không mua thêm gì — chỉ chặn decode.
Project mẫu không truyền `dispatcher` nên nhận mặc định `Dispatchers.IO`, không dính.

**Why:** phép đo A/B biện minh cho `parallelism=1` chạy trên file 180s, decode chỉ ~10s nên núp trong
mấy segment đầu và trông như "serialising costs nothing". Kết luận sai tồn tại nhiều tuần.

**How to apply:** đo throughput audio bằng file ≥ 10 phút. Khi một tối ưu "không tốn gì", kiểm tra
xem input đo có đủ dài để chi phí đó lộ ra không. Hệ quả kéo theo: mọi seed trong
[[project-separation-device-limits]] đo trước fix nên thiên cao ~58%.

Nạp model KHÔNG phải chi phí đáng lo: `engine ready` 18-53ms vì model `mmap` lazy từ APK
(`noCompress += "tflite"`); chi phí thật ~780ms page-in vào inference đầu tiên — đó là giá của
[[pattern-unload-model-native-heap]].
