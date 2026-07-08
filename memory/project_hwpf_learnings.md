---
name: HWPF DOC Conversion Learnings
description: Những API pitfalls và discoveries khi dùng Apache POI HWPF 5.2.5 để parse .doc
type: project
originSessionId: c80b66f5-f64e-476f-ab9b-7c3a79ff12dc
---
Accumulated discoveries từ debugging `WordToPdfConverter.kt` với `legacy_Pet resume.doc`.

**Why:** HWPF API có nhiều gotchas không obvious. Ghi lại để không phải debug lại.

**How to apply:** Khi làm việc với .doc conversion, check list này trước khi implement.

---

## Image display size — dùng scaling factors, KHÔNG phải dxaGoal

```kotlin
// SAI — dxaGoal là kích thước gốc của file, có thể rất lớn (600pt)
val widthPt = pic.dxaGoal / 20f

// ĐÚNG — apply scaling factor (1000 = 100%)
val scaleX = pic.horizontalScalingFactor.let { if (it > 0) it / 1000f else 1f }
val widthPt = pic.dxaGoal * scaleX / 20f
```

## Package của PicturesTable

`org.apache.poi.hwpf.model.PicturesTable` — KHÔNG phải `usermodel`.

## getJustification() trả về Int, không phải Byte

```kotlin
// SAI
private fun hwpfJustificationToAlign(jc: Byte): String
// ĐÚNG
private fun hwpfJustificationToAlign(jc: Int): String
```

## Image extraction: per-run, không phải per-paragraph

```kotlin
// ĐÚNG — iterate từng run
for (i in 0 until para.numCharacterRuns()) {
    val run = para.getCharacterRun(i)
    if (picturesTable.hasPicture(run)) {
        val pic = picturesTable.extractPicture(run, false)
    }
}
```

## doc.text vs doc.range

- `doc.text` = raw text từ TextPieceTable, bao gồm TẤT CẢ stories concatenated (main + footnotes + textboxes + headers)
- `doc.range` = chỉ main story
- Khi `doc.range.numParagraphs()` có vẻ ít, check `doc.text` để xác nhận content có tồn tại không

## getMainTextboxRange() là public, nhưng thường rỗng

Nhiều .doc file có layout phức tạp không dùng textbox story. `mainTextboxRange.numParagraphs()` thường = 1 (empty placeholder). Layout 2 cột thường được implement qua paragraph frames (dxaAbs/dxaWidth) hoặc floating OfficeArt objects.

## Paragraph frame detection

```kotlin
val props = para.getProps()
val isFramed = props.dxaWidth > 0  // non-zero = framed paragraph
val xPosTwips = props.dxaAbs
val yPosTwips = props.dyaAbs
```

Tuy nhiên, một số .doc file được tạo bởi LibreOffice/newer Word có thể không encode frame properties theo cách HWPF mong đợi.

## OfficeDrawingsMain — floating shapes

```kotlin
val drawings = doc.officeDrawingsMain.officeDrawings  // Collection<OfficeDrawing>
// Mỗi drawing có: rectangleLeft/Top/Right/Bottom (twips), pictureData, horizontalPositioning
```

Nếu `officeDrawingsMain.officeDrawings.isEmpty()` = true và `dxaWidth=0` cho tất cả paragraphs, document dùng layout mechanism mà HWPF không detect được — thường là case với .doc được save từ LibreOffice.

## doc.range content là đủ

Khi `doc.text` chứa content (PERSONALITY, HEALTH...) nhưng output PDF thiếu → nguyên nhân KHÔNG phải content missing mà là image render size quá lớn (do bỏ qua scaling factor) đẩy text ra ngoài viewport.
