---
name: project-as-terminal-vietnamese
description: Android Studio terminal gõ tiếng Việt kém — chờ upgrade AS rồi mới thử fix; engine Classic là nước đi đầu tiên
metadata: 
  node_type: memory
  type: project
  originSessionId: e9c88508-b87b-41df-a4b6-c6487ac6ba4e
  modified: 2026-09-08T04:36:51.119Z
---

2026-09-08: User hoãn việc upgrade Android Studio vì terminal của bản mới gõ tiếng Việt
không tốt. Đã thống nhất **đợi upgrade xong mới thử fix** — chưa làm gì.

Tình trạng máy lúc khảo sát:
- AS đang chạy: `~/App/android-studio`, build `AI-251.27812.49.2514.14171003` (2025.1.4)
- Config còn của 2026.1.1 và 2026.1.3 tại `~/.config/Google/AndroidStudio<ver>/`
- `2025.1.4/options/terminal.xml` có `terminalEngine = REWORKED` (user tự chọn, không phải default)
- 2026.1.x không có key `terminalEngine` → chạy default, có cờ `TerminalEngineMigration.2026.1`

**Why:** hai nhầm lẫn dễ mắc lại nếu không ghi — (1) plugin `classic-ui` user đã cài chỉ
đổi UI của IDE, KHÔNG đụng terminal engine; (2) terminal engine vẫn còn `Classic` (xác nhận
bằng enum `TerminalEngine` trong `plugins/terminal/lib/terminal.jar`: `Classic` /
`Reworked 2025` / `Experimental 2024 (deprecated)`), JetBrains chưa gỡ.

**How to apply:** khi user quay lại chủ đề này sau upgrade — thử theo thứ tự:
`Settings → Tools → Terminal → Terminal engine → Classic` (hoặc set
`<option name="terminalEngine" value="CLASSIC" />` vào `options/terminal.xml` khi IDE đã tắt,
IDE ghi đè file lúc thoát). Nếu Classic vẫn gõ tiếng Việt lỗi → vấn đề là IME chứ không phải
engine, chuyển hướng sang external terminal (máy chỉ có `gnome-terminal`, chưa có tmux) gắn
qua `Settings → Tools → External Tools`. Không tự ý áp fix trước khi user báo đã upgrade.
