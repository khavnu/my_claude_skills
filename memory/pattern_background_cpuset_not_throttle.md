---
name: pattern-background-cpuset-not-throttle
description: "App nền chậm là do cpuset cgroup giới hạn core, không phải throttle; chỉ foreground service nâng được, đáng 3.5x"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4a4bf1be-1d65-45b5-a7c4-ef9fc8732a6e
  modified: 2026-09-24T06:20:09.196Z
---

Đo trên Pixel 4 XL (Android 13, Snapdragon 855) ngày 2026-09-24, tách stem 2 stems, cửa sổ 60s mỗi kịch bản.

Việc tách chậm lại khi app xuống nền **không phải** thermal throttle hay Doze. Android gán process vào cgroup
cpuset theo process state, và app không có cách nào tự đổi:

| cpuset | cpus | seg/s đo |
|---|---|---|
| `top-app` (màn hình mở) | `0-7` — có prime 2.84 GHz | 0.700 |
| `foreground` (có FGS, ở nền) | `0-3,5-6` — **không có prime** | 0.467 |
| `background` (cached, không FGS) | **`0-1`** — 2 little @1.79 | 0.133 |

Đọc bằng `cat /proc/<pid>/cgroup` và `cat /dev/cpuset/<group>/cpus`. Khi nhấn HOME, **cả 106 thread**
chuyển sang `/background` cùng lúc; `curProcState` 2 → 15 (CACHED_ACTIVITY), oom_adj 700.

**Foreground service đáng 3.5×** (0.467 / 0.133). Nhưng nó vẫn chỉ đạt 67% tốc độ foreground vì
`/foreground` thiếu core prime — FGS không phải là "chạy như bình thường".

**Đừng tốn công chỉnh số thread.** Throughput tỉ lệ gần tuyến tính với tổng GHz-core của cpuset
(17.26/12.00/3.58 → tỉ lệ đo 5.26×/3.51×/1.00×, lệch <10%). Tỉ lệ đo **cao hơn** tỉ lệ CPU, nghĩa là
oversubscription (28 thread `DefaultDispatch` trên 2 core) không gây thrash — không có gì để thu hồi từ
`Interpreter.setNumThreads`.

Không dùng được: `sched_setaffinity` (cpuset là mask cứng của kernel, affinity chỉ giao với nó),
`setThreadPriority` (chỉ đổi nice trong cgroup), `setSustainedPerformanceMode` (hạ trần hiệu năng).
WakeLock giải bài toán khác — chống suspend khi màn hình tắt, không đổi cpuset.

Chưa đo: WorkManager expedited job có lên được `/foreground` cpuset không.

Liên quan: [[project_separation_device_limits]], [[project_separation_open_items]],
[[reference_separation_debug_toolkit]]
