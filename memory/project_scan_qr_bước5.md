---
name: Scan QR Refactor - Architecture Completed
description: Trạng thái refactor scan_code thành self-contained library, BarcodeContent đã được loại bỏ hoàn toàn
type: project
originSessionId: 95090af7-b355-4948-8079-bb6847e7acc2
---
## Refactor hoàn tất (feature/scan_qr)

**Why:** Loại bỏ dual-parse risk (ML Kit vs ZXing), `BarcodeContent` trong domain bị xóa, parse logic về `scan_code` module.

### Những gì đã xong

**`:scan_code` module - self-contained library:**
- `ScanBarcodeType.kt` — enum thay cho sealed hierarchy cũ
- `ScanResult.kt` — flat data class (rawValue, barcodeType, bitmaps)
- `ParsedBarcode.kt` — sealed class model hierarchy (QrText, QrUrl, QrContact, ..., LinearBarcode)
- `BarcodeContentParser.kt` — public object, ZXing parsing → `ParsedBarcode`
- `ScanResultParser.kt` — chỉ `quickName()` extension
- Mapper files simplified (MlKitBarcodeMapper, ZXingBarcodeMapper)

**`:domain` module:**
- `FileMetadata.BarcodeMetadata` → `rawValue: String, barcodeType: String` + `fun quickBarcodeTitle(): String = ""`
- `BarcodeContent.kt` đã XÓA
- `QRContent.kt` đã XÓA

**`:data` module:**
- `FileEntity.kt` — dùng `data.rawValue` / `data.barcodeType` trực tiếp, bỏ `barcodeTypeString()`
- `FileWithRelations.kt` — build `BarcodeMetadata(rawValue, barcodeType)` trực tiếp
- `BarcodeContentParser.kt` đã XÓA (đã chuyển sang scan_code)
- `data/build.gradle.kts` — đã bỏ `zxing.core`
- `DefaultMediaDataSources.kt` — cập nhật QR_CODE case

**`:app` module:**
- `ScanResultMapper.kt` — tạo `BarcodeMetadata(rawValue, barcodeType.name)` trực tiếp
- `ManagedFileExtension.kt` — `BarcodeMetadata.getContentLabel()` thay cho `BarcodeContent.getContentLabel()`
- `ScanCodeResultScreen.kt` — dùng `ParsedBarcode` từ `BarcodeContentParser.parse()`
- `strings.xml` — thêm `R.string.event`

**Test files đã fix:**
- `domain/test/FileRepositoryTest.kt`
- `data/test/FileRepositoryTest.kt`
- `data/test/TestDataFactory.kt`

### Build status
- `:scan_code:compileDebugKotlin` — BUILD SUCCESSFUL
- `:domain:compileDebugKotlin` — BUILD SUCCESSFUL
- `:data:compileDebugKotlin` — blocked bởi pre-existing `office_reader:compileDebugJavaWithJavac` lỗi JLink (không liên quan code changes)

**How to apply:** Khi làm việc với scan_code feature, `BarcodeContent` không còn tồn tại. Dùng `ParsedBarcode` từ `:scan_code` và `BarcodeMetadata(rawValue, barcodeType)` từ domain.
