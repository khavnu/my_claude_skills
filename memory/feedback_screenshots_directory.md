---
name: Screenshots Directory
description: Hai thư mục screenshot khác nhau — desktop và device Android
type: feedback
originSessionId: c80b66f5-f64e-476f-ab9b-7c3a79ff12dc
---
Có 2 thư mục screenshot, dùng cho mục đích khác nhau:

- **`/home/khapv/Screenshots/`** — Screenshot chụp trên máy tính (LibreOffice, browser, desktop apps). File naming: `Screenshot from YYYY-MM-DD HH-MM-SS.png`
- **`/home/khapv/Desktop/screenshots/`** — Screenshot chụp từ thiết bị Android (kết quả conversion, app UI). File naming: `Screenshot_YYYYMMDD_HHMMSS.png`

**Why:** User muốn show kết quả conversion (device screenshot) hoặc expected output (desktop screenshot) — hai nơi lưu khác nhau nên phải check đúng chỗ.

**How to apply:**
- Khi user nói "kết quả" hoặc "đã update screenshot" → `ls -lt /home/khapv/Desktop/screenshots/ | head -3` rồi Read file mới nhất
- Khi user nói "screenshot mong muốn" hoặc LibreOffice/desktop reference → `ls -lt /home/khapv/Screenshots/ | head -3` rồi Read file mới nhất
- Không cần hỏi path, tự check cả 2 nếu không rõ context
