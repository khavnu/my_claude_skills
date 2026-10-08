---
name: project-combined-player-device-test
description: Kiểm CombinedStemPlayer/StemStore trên máy — bài bundled không bao giờ được lưu; variant reset khi vào lại; quảng cáo đè trên Realme; pgrep -f tự khớp shell; run-as sh -c không expand glob; nhiệt thermalservice là cache; log app xoay mỗi lần khởi động
metadata:
  node_type: memory
  type: project
  originSessionId: f3d6b4db-0990-4904-8a79-1c1052bbf9b2
  modified: 2026-10-02T09:57:11.810Z
---

CombinedStemPlayer + CompletedStemsStore xong 2026-10-02 (plan `docs/superpowers/plans/2026-10-02-combined-stem-player.md`, kết quả Task 6 ghi ở cuối plan).

- **Bài bundled ("Mẫu 30s", Lofi...) không bao giờ ra `source=Files`**: Uri là `android.resource://`, `ContentResolver.query` trả null → `SourceKeyResolver.keyFor` null → không lưu. Verify: tách xong "Mẫu 30s", `run-as … find no_backup` vẫn rỗng. Muốn test nhánh Files → chọn file qua SAF picker (vd. Downloads/NhacCuaTui, xem [[project-adb-saf-picker]]).
- **`adb shell run-as <pkg> sh -c 'rm no_backup/stems/*/…'` KHÔNG expand glob** (dính 2 lần: cat manifest, rm stem) → dùng đường dẫn đầy đủ có hash sha256 (`run-as … find no_backup -type f` để lấy).
- **Realme (ColorOS) ẩn log Timber của app** (`adb shell log -t X` vẫn hiện) và fd không phải tín hiệu (ExoPlayer đóng file giữa các lần nạp chunk) → đọc nguồn bằng màn hình: chip đoạn được tô màu tertiary = Segments (chỉ stream player có `currentSegmentIndex`); seek tới chỗ chưa tách (vd. 4:00) mà đồng hồ vẫn chạy = Files.
- Độ dài kế hoạch (metadata mp3) ≠ độ dài decode: anh_nho_em.mp3 lệch 38 ms → đừng bao giờ kiểm toàn vẹn file lưu bằng độ dài kế hoạch (đã sửa 2026-10-02: manifest ghi `durationUs.<stem>` đo thật).
- Dấu hiệu chạy đúng (Pixel): logcat `StreamSplitterViewModel$startPlayerSession: Playback source=Files|Segments`; BatchStemPlayer KHÔNG log drift → kiểm liền mạch bằng đồng hồ tường (seek 00:13, 23 s sau phải là 00:36).
- Pixel 9 có thể đang bị user dùng giữa chừng: màn tự xoay / app khác (app nhắc uống nước) lên foreground → dừng thao tác ngay (luật: không đụng máy user đang dùng).
- **Màn Streaming reset variant về 2-Stem Quantized mỗi lần vào lại** → thử "mở lại ra Files" phải chọn lại đúng variant đã lưu, nếu không sẽ tưởng find() hỏng (dính 2026-10-02, kiểm bằng screenshot hàng nút variant).
- **Realme: quảng cáo full-screen của app khác (`net.uploss.water_app`, AppLovin) đè lên giữa chừng** → tap rơi vào quảng cáo. Trước mỗi chuỗi tap: `dumpsys window | grep mCurrentFocus` phải là app mình.
- **`pgrep -f <tên script>` / `pkill -f` khớp luôn chính shell đang chạy lệnh đó → exit 144** (dính lần 3). Kill theo PID đã ghi lúc khởi chạy, hoặc pattern không xuất hiện trong dòng lệnh hiện tại.
- (2026-10-05) Thêm bẫy Realme khi đo: `dumpsys thermalservice` trả nhiệt CPU CACHE (đứng 66,1 °C nhiều phút) → dùng `dumpsys battery | grep temperature`; dòng file cuối của SAF picker nằm trên thanh cử chỉ → tap về launcher, cuộn danh sách trước; picker mở dở quay lại cùng task sau force-stop (BACK rồi `am start` lại); popup báo thức/quảng cáo `water` → BACK; toybox grep KHÔNG hiểu `\|` (tưởng thiếu log). Log app debug ra file: `FileLogTree` → `files/logs/app.log`, XOAY MỖI LẦN KHỞI ĐỘNG (script đếm dòng log từ lần trước sẽ không bao giờ khớp). Driver: scratchpad `realme_ui.py`, `n12.py`, `n4_kill.py`, `wav_check.sh` (mất khi reboot).
- Đo dung lượng đỉnh: script `du -sk` mỗi 2 s trên `Android/data/<pkg>/files/stem_splitter/stream` + `run-as du -sk no_backup` (đỉnh 4 stem 4:39: 625 MB cách cũ, 254 MB với StemStore AAC — số ở public_api.md).
