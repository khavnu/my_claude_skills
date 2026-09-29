---
name: project_prior_removals
description: AudioSeparation xoá hẳn hướng không đạt và ghi lý do — grep repo TRƯỚC khi đề xuất "ý tưởng chưa thử"; GPU delegate và ONNX-làm-backend đều đã bị loại
metadata:
  type: feedback
---

Repo AudioSeparation **xoá hẳn** hướng nào không đạt (không chỉ unwire khỏi DI) và ghi lý do đo được
vào comment + README. Nên trước khi liệt kê "ý tưởng chưa thử", **grep repo tìm dấu vết đã loại**.

**Why:** 2026-09-25 tôi đề xuất GPU delegate như hướng lớn nhất còn lại, user bác ngay: "artifact và
readme đã báo rồi mà". Đúng — `OriginalGpu`/`QuantizeGpu` từng tồn tại, test máy thật, xoá vì **hai**
lý do, trong đó lý do thứ hai (`tensorflow-lite-gpu` **phá 16 KB page-size**, chặn Play với
targetSdk 35+) cứng hơn hẳn thứ tôi tự tìm ra sau một ngày. Ngay sau đó user bác tiếp ONNX: cũng đã
đo, chậm hơn TFLite **3,6–5,6x**, đã loại 2026-09-04.

Tôi đã mở **đúng file** `StemSplitEngineModule.kt` khi rà soát "cái gì đã thử", nhưng cắt cửa sổ
`sed -n '85,98p'` — comment GPU ở dòng **74-77**, trượt 8 dòng. Cùng kiểu lỗi với `head -14` cắt mất
dòng lỗi UI trong cùng session. **Cắt cửa sổ quanh thứ mình đang tìm sẽ giấu mất thứ mình chưa biết
là cần tìm.**

Nguyên nhân gốc: ba chỗ trong code trỏ tới mục README "GPU delegate" mà **mục đó không tồn tại** —
con trỏ chết. Đã viết mục đó vào `audio_stem_split/README.md` và thêm section "ĐÃ LOẠI TỪ TRƯỚC" vào
`docs/PERFORMANCE-EXPERIMENTS.md`.

**How to apply:**
1. Trước khi đề xuất bất kỳ hướng tối ưu nào: `grep -rniE "<từ khoá>" --include=*.kt --include=*.md`
   (bỏ `checkpoints_backup`), và đọc **cả khối comment đầu file** chứ không chỉ dòng khớp.
2. Đọc `docs/PERFORMANCE-EXPERIMENTS.md` mục "ĐÃ LOẠI TỪ TRƯỚC" và README các mục
   `*was removed` / `*was evaluated and rejected`.
3. Khi grep ra dòng khớp, in rộng (`grep -B10 -A10`) thay vì `sed` một cửa sổ hẹp.
4. Khi loại một hướng, **viết mục README mà comment trỏ tới** — con trỏ chết là cách một finding bị
   tìm lại lần hai. Xem [[project_fade_merge_export]] về cùng bài học ở dạng khác.

Đã loại tính tới 2026-09-25: GPU delegate, NNAPI, ONNX làm backend tách nhạc, `onnxruntime-mobile`,
full int8 quantization, PANNs/EfficientAT thay YAMNet, `setUseXNNPACK`.

**Nâng epsilon khi export model float16 — đã build, đã đo, đã bỏ (2026-09-29).** float16 làm
`eps = 1e-10` của Spleeter thành đúng 0 nên frame im lặng tuyệt đối ra NaN. Nâng lên `1e-4` (số
normal nhỏ nhất của float16 là 6,104e-5) đúng là hết NaN, nhưng lệch trung bình so với float32 đi
từ 9,44e-05 lên 2,20e-02 — **tệ gấp 233 lần** — vì 3,0% số bin của nhạc thật nằm dưới ngưỡng đó và
bị kéo về `1/n`. Không có eps nào vừa sống sót float16 vừa nằm dưới các bin đó. Đã chặn ở Kotlin
thay vì ở model: `SpectrogramStemSeparator.applyPatchMask`, mask không hữu hạn → `1/n`. Số đo và
bảng nghiệm thu 2 máy nằm ở `custom_idea.md` mục "Hai cái bẫy khi chọn tier" và `audio_stem_split/README.md`.
