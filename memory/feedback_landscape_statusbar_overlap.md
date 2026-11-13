---
name: feedback-landscape-statusbar-overlap
description: "Landscape — luôn kiểm status bar có đè lên icon toolbar (back, Save, Home) không, cả trên Figma lẫn trên máy thật"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 71a8dc64-edac-4386-9060-b65d48abd648
  modified: 2026-10-21T01:58:59.362Z
---

User dặn (2026-10-21, khi làm landscape video tools): "chú ý việc statusbar đè lên, ví dụ các icon ở toolbar".

**Why:** ở landscape, inset của status bar và display cutout không giống portrait, nên top bar mà thiếu inset sẽ để status bar đè lên icon toolbar. Lỗi này không lộ ra ở portrait.

**How to apply:**
- Figma: status bar chiếm y 0–24, icon toolbar bắt đầu từ y≥34. Kiểm bằng `absoluteBoundingBox` so với frame, không chỉ nhìn bằng mắt.
- Code: top bar phải nhận inset `statusBars` + `displayCutout`. Verify trên máy ở cả 2 chiều xoay: chụp screenshot rồi nhìn icon back/Save/Home ở 2 mép.

Liên quan [[feedback-landscape-keep-portrait]], [[reference-video-tools-landscape-figma]].
