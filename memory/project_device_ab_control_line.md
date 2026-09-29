---
name: project-device-ab-control-line
description: Đo A/B hiệu năng trên máy phải cùng phiên, và dùng `invoke` làm dòng đối chứng vì DSP không đụng tới nó
metadata:
  type: feedback
---

Mọi phép so hiệu năng trên thiết bị phải là **A/B liền mạch trong cùng một phiên**, và phải có một
đại lượng **không bị thay đổi đang đo tác động tới** in ra cùng lúc để làm đối chứng.

Với `separate()` thì đại lượng đó là **`invoke`** — thời gian chạy model. Sửa STFT/iSTFT không đụng
tới nó, nên `invoke` lệch bao nhiêu giữa hai lượt chính là mức nhiễu của phép đo.

**Why:** 2026-09-29, đo tác động của việc gói 2 kênh vào một FFT. Lần đầu lấy số "trước" từ lượt
chạy lúc 10:52 rồi so với lượt 14:0x trên cùng máy cùng file → ra −25%. Nhưng `invoke` lệch **+20%**
giữa hai lượt dù model không hề đổi, nghĩa là máy lúc sau chậm hơn hẳn và con số kia vô nghĩa. Cài
lại bản cũ, đo nối tiếp ngay: `invoke` lệch **+1,2%**, và kết quả thật là **−32,8%**. Không có dòng
đối chứng thì đã báo sai 8 điểm phần trăm mà vẫn trông thuyết phục.

Tỉ lệ phần trăm còn đánh lừa theo hướng ngược lại: trên A20s tỉ lệ STFT bò từ 28,1% lên 37,5% qua 6
lần chạy liên tiếp **trong khi giá trị tuyệt đối đứng yên ~3,9s** — `invoke` tụt từ 9,98s xuống
6,69s khi máy ấm lên, mẫu số co lại. Luôn đọc cả giá trị tuyệt đối trước khi kết luận cái gì đang
xấu đi.

**How to apply:** trước khi so hai build, kiểm tra dòng đối chứng lệch bao nhiêu. Lệch >5% → vứt
phép đo, cài lại và đo nối tiếp. Số "trước" lấy từ phiên khác chỉ dùng để ước lượng, không dùng để
kết luận. Liên quan: [[project-stream-chunk-10s]] (đo khi ĐANG PHÁT mới ra đúng điều kiện),
[[project-fade-merge-export]] (verify audio phải kèm dòng đối chứng).
