---
name: project-combined-player-device-test
description: "Kiểm CombinedStemPlayer trên máy — bài bundled KHÔNG BAO GIỜ được lưu (android.resource:// không có khoá), phải dùng SAF; run-as sh -c không expand glob"
metadata:
  node_type: memory
  type: project
  originSessionId: f3d6b4db-0990-4904-8a79-1c1052bbf9b2
  modified: 2026-10-02T09:57:11.810Z
---

CombinedStemPlayer + CompletedStemsStore xong 2026-10-02 (plan `docs/superpowers/plans/2026-10-02-combined-stem-player.md`, kết quả Task 6 ghi ở cuối plan).

- **Bài bundled ("Mẫu 30s", Lofi...) không bao giờ ra `source=Files`**: Uri là `android.resource://`, `ContentResolver.query` trả null → `SourceKeyResolver.keyFor` null → không lưu. Verify: tách xong "Mẫu 30s", `run-as … find no_backup` vẫn rỗng. Muốn test nhánh Files → chọn file qua SAF picker (vd. Downloads/NhacCuaTui, xem [[project-adb-saf-picker]]).
- **`adb shell run-as <pkg> sh -c 'rm no_backup/stems/*/…'` KHÔNG expand glob** (dính 2 lần: cat manifest, rm stem) → dùng đường dẫn đầy đủ có hash sha256 (`run-as … find no_backup -type f` để lấy).
- Dấu hiệu chạy đúng: logcat `StreamSplitterViewModel$startPlayerSession: Playback source=Files|Segments`; BatchStemPlayer KHÔNG log drift → kiểm liền mạch bằng đồng hồ tường (seek 00:13, 23 s sau phải là 00:36).
- Pixel 9 có thể đang bị user dùng giữa chừng: màn tự xoay / app khác (app nhắc uống nước) lên foreground → dừng thao tác ngay (luật: không đụng máy user đang dùng).
