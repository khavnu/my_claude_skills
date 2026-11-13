---
name: self-upgrade
description: Use when the user explicitly asks you to research and upgrade your own global CLAUDE.md/skills (e.g. "/self-upgrade", "tự nâng cấp bản thân đi", "research skill mới xem có gì áp dụng được không"). Runs on demand, in the current interactive session — not the Friday cron job (see ~/.claude/scripts/weekly-skill-research.sh for that).
---

# Self-Upgrade (on-demand)

Rà soát xem có nên cập nhật `~/.claude/CLAUDE.md` hoặc một skill trong `~/.claude/skills/` hay không, dựa trên domain công việc thực tế gần đây. Chạy ngay trong session tương tác hiện tại — bạn có quyền ghi bình thường, không cần permission flag đặc biệt nào. Rất bảo thủ — nghiêng về KHÔNG làm gì nếu không chắc.

Đây là phiên bản gọi thủ công của job cron hàng tuần (`~/.claude/scripts/weekly-skill-research.sh`, chạy tự động Thứ 6 17h00). Cả hai dùng chung `~/.claude/skill-research-log.md` — luôn đọc log cũ trước để biết cái gì đã xét rồi (`trigger: cron` hay `trigger: manual` đều tính).

## Bối cảnh cố định

- User là senior Android engineer: Kotlin, Jetpack Compose, Clean Architecture + MVVM, Coroutines/Flow, Hilt, Room, DataStore, Retrofit, Media3. Cũng dùng Figma cho design handoff.
- `~/.claude/CLAUDE.md` và `~/.claude/skills/*` là config GLOBAL dùng cho MỌI project trên máy này — không phải config riêng 1 project. Đừng đưa gì đặc thù 1 project vào đây.
- User đã có sẵn nhiều skill tự viết (`debug`, `long-feature`, `doubt-driven-development`, `edge-cases`, `review`, `orchestra`, `openspec-*`, `clean-architecture`, `new-feature`, `new-module`, `source-driven-development`, `collab`, `figma-reader`, `create-design`, `custom-android-studio`, `switch-figma-account`, `tohsoft-ticket`, `android-context-extensions`) và plugin cài sẵn (`superpowers`, `code-review`, `frontend-design`, `figma`). KHÔNG đề xuất lại cái đã có, không tạo trùng lặp trigger.
- Máy này có **2 account profile** cần giữ đồng bộ: `~/.claude` (profile hiện tại) và `~/.claude-k` (account khác). Mọi file bị patch phải mirror sang `~/.claude-k` ở cuối.

## Việc cần làm — ĐÚNG THỨ TỰ

### Bước 1 — Xác định domain gần đây
- Đọc `~/.claude/skill-research-log.md` để lấy ngày của entry gần nhất (bất kể trigger) — đó là mốc "từ khi nào". Không có log nào → mặc định nhìn lại 7 ngày.
- `find` các `.git` trong `/home/khapv/AndroidStudioProjects/*` và `/home/khapv/Work/*`, `git log --since="<mốc>"` ở mỗi repo tìm được.
- Project không phải git repo (vd AudioSeparation): xem mtime các file trong `~/.claude/projects/*/memory/*.md`.
- Tổng hợp domain thực sự đụng tới từ mốc đó tới nay. Không có hoạt động gì mới → ghi log "không có hoạt động" (Bước 4) và báo user ngắn gọn, dừng ở đây.

### Bước 2 — Research
- Đọc `~/.claude/plugins/plugin-catalog-cache.json` + `~/.claude/plugins/installed_plugins.json` để biết skill/plugin phổ biến/đã cài liên quan domain.
- Đọc skill liên quan đã cài (`~/.claude/skills/*/SKILL.md`) để tìm cơ chế còn thiếu.
- Session này tương tác, có người theo dõi → được phép WebSearch 1-2 query ngắn nếu cần xác nhận gap là pitfall thật hoặc tìm kỹ thuật mới, nhưng không bắt buộc — ưu tiên dữ liệu local trước.

### Bước 3 — Quyết định áp dụng (bảo thủ)
CHỈ sửa file khi TẤT CẢ đúng:
(a) Gap cụ thể, verify được — trỏ thẳng tới 1 cơ chế/rule rõ ràng đang thiếu, không phải "nghe hay" chung chung.
(b) KHÔNG trùng lặp hoặc xung đột trigger với skill/plugin đã cài, đặc biệt `superpowers`/`code-review`/`frontend-design`/`figma`.
(c) Chỉ rút ĐÚNG cơ chế còn thiếu vào skill/CLAUDE.md hiện có — KHÔNG chép nguyên văn nội dung skill nguồn.
(d) Giữ nguyên văn phong/convention đã có (tiếng Việt cho giải thích, tiếng Anh cho code/thuật ngữ kỹ thuật, bullet ngắn, không thêm comment thừa).

Giới hạn:
- KHÔNG tạo skill mới, KHÔNG xoá skill/rule nào đang có, KHÔNG cài thêm plugin.
- Tối đa sửa **1 file duy nhất** mỗi lần gọi (CLAUDE.md HOẶC đúng 1 skill file). Có ≥2 ứng viên hợp lệ → chọn cái mạnh nhất, còn lại ghi log "candidate chưa áp dụng" — user gọi lại `/self-upgrade` lần nữa nếu muốn xử lý tiếp.
- Áp dụng trực tiếp (rule #1 trong CLAUDE.md: auto-apply, không hỏi "có nên áp dụng không").

### Bước 4 — Ghi log + sync
Append vào CUỐI `~/.claude/skill-research-log.md` (tạo mới với header `# Weekly Skill Research Log` nếu chưa có), đúng format:

```
## YYYY-MM-DD
- trigger: manual
- domains: <...>
- action: <no-op | patched>
- file: <đường dẫn tương đối từ ~/.claude/, trống nếu no-op>
- lý do: <1-2 câu, kèm nguồn đối chiếu cụ thể>
- candidates chưa áp dụng: <...>
```

Sau đó, nếu `action: patched`, chạy luôn (Bash, không cần hỏi):
```
rsync -a ~/.claude/<file> ~/.claude-k/<file>
rsync -a ~/.claude/skill-research-log.md ~/.claude-k/skill-research-log.md
```

### Báo cáo lại user
Khác với cron (chạy im lặng), lần này báo ngắn gọn cho user: domain đã xét, đã patch gì (hoặc no-op vì sao), đã sync sang `.claude-k` chưa.
