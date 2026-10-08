---
name: project-lyrics-speed-next
description: Next feature after stream-resume (done 2026-10-05) — lyrics speed; ideas + baseline numbers in docs/features/lyrics-speed/ideas.md; Q4 "Whisper always full" is lifted by the user
metadata:
  type: project
---

User 2026-10-05: goal is fast AND accurate stem split + lyrics; accuracy is now fine, speed is the issue.
"Thử lần lượt các ý tưởng và đo lại" — to start AFTER stream-resume (done, backup
`checkpoints_backup/code_backup_2026-10-05_133812_stream_resume_done`). This lifts Q4 of the
lyrics-sources checklist (Whisper always runs full).

Everything (6 ideas, corpus early-accept numbers, Realme timeline) is in `docs/features/lyrics-speed/ideas.md`.
Key verified fact: stopping Whisper early is only safe with whole-track VAD — with VAD-so-far, half lyrics
get accepted on ~every corpus song (`CorpusVerificationReport.earlyAcceptance`).
User said: online lyrics architecture stays as is (LyricsProvider interface in lib is enough).
Start with a long-feature checklist for user approval.

User 2026-10-05 (during lyrics-speed): do NOT notify the product side (WMusi, collab HANDOFF) about these
changes yet — improve first, hand over later only when the user asks.

Cập nhật 2026-10-06: nhóm K (wav2vec2 xác minh, Whisper chỉ VAD) + K8–K10 xong trên Realme — lời đã xác minh 222–230 s → 52–55 s,
kết quả cuối akd 621–648 → ~252 s. Số đo và trạng thái ở docs/features/lyrics-speed/checklist.md (K1–K10). Còn mở: N4 (chữ Whisper
đổi khi resampler đổi — chờ user), K7 (mọi ngôn ngữ), M (Moonshine), P (lời thuần trước).
Research (nguồn ngoài, app đối thủ) đã gom vào docs/features/lyrics-speed/research.md — 2026-10-06 user hỏi vì trước đó chỉ nằm trong chat; research mới phải ghi vào đó ngay, không để trong hội thoại.

**TIẾP TỤC NGÀY MAI (user 2026-10-07 "note lại mai làm tiếp")** — đang ở bước chọn hướng thêm ngôn ngữ (đã có 18).
Đề xuất đã gửi, user CHƯA chọn: (1) Vakyansh kn (+ thử ml/pa/as) ~½ ngày cùng quy trình; (2) spike NeMo FastConformer es
(CC-BY-4.0; mở ~15 ngôn ngữ es/fr/it/nl/pl/uk…; cần log-mel Kotlin + SentencePiece + frame 80 ms + export ONNX); (3) large
XLS-R (zh) / (4) tự fine-tune: để sau. Chi tiết: docs/features/lyrics-speed/research.md mục 3a. Hỏi user chọn trước khi làm.
Đang chờ user khác: Jamendo client_id ([[project-jamendo-client-id-pending]]); có sửa vocab blank tiếng Thổ không
(`<s>` id 0, đo chưa thấy lợi); đóng gói model (17 model ở model_assets/lyrics, APK chỉ gói vi).
Danh sách ngôn ngữ tiếp theo (đợt A–D) đã ghi ở checklist K7, mục "DANH SÁCH NGÔN NGỮ TIẾP THEO" (2026-10-07). Bản debug mới nhất đã cài lên Pixel 9 (47231FEAQ001B9) cùng ngày, chỉ gói model vi.
Việc mai thêm (user 2026-10-07): (1) bổ sung API docs về nguồn lời (LyricsSource đủ 5 giá trị gồm Manual, StreamLyrics.source,
StoredLyrics giữ nguồn) — user muốn app biết lời lấy từ đâu; (2) chú ý trường hợp KHÔNG có internet: vẫn dùng nguồn có sẵn
(embedded/file/manual) để AI xác minh + map thời gian; kiểm bằng chế độ máy bay trên máy. Ghi ở checklist K7 "VIỆC MAI".
