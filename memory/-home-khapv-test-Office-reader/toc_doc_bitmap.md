---
name: WordView ToC bitmap capture for .doc
description: How ToC page thumbnail capture works for .doc files — bugs fixed and current state
type: project
---

## Trạng thái (fix xong 2026-04-16)

ToC bitmap capture cho `.doc` đã hoạt động tốt.

## Các bug đã fix

### 1. findMarker() so sánh sai node (primary bug)
DocReader's `makeSep()` tạo cấu trúc:
```
#doc-content > <div separator>  ← direct child
                  └── <span class="doc-page-num">Page 2 / 5</span>  ← nested
```
`findMarker()` trả về `<span>` nhưng vòng lặp so sánh với direct children → không bao giờ match → page 2+ trả về null bitmap.

**Fix:** Sau khi tìm marker span, walk up DOM đến direct child của container:
```javascript
if (m && m.parentElement !== container) {
    var p = m;
    while (p.parentElement && p.parentElement !== container) p = p.parentElement;
    if (p.parentElement === container) m = p;
}
```

### 2. Không capture toàn page
`h = window.innerHeight` chỉ capture 1 màn hình → foreignObject clip content bên dưới.

**Fix:** Append wrapper off-screen, đo `scrollHeight` thực tế, remove:
```javascript
wrapper.style.cssText = '...position:absolute;left:-9999px;...';
document.body.appendChild(wrapper);
h = Math.max(wrapper.scrollHeight || wrapper.offsetHeight, 100);
document.body.removeChild(wrapper);
```

### 3. img.onerror (page có ảnh lớn)
Base64 image > 30KB trong SVG data URL → vượt limit renderer → toàn bộ thumbnail fail.

**Fix:** Strip trước khi serialize:
```javascript
if (imgSrc.indexOf('data:') === 0 && imgSrc.length > 30000) {
    allImgs[di].removeAttribute('src');
    allImgs[di].style.cssText += ';background:#e8e8e8;';
}
```

### 4. ImageView size
Đổi từ 80×60dp (landscape) → 72×96dp (portrait, ratio ~0.75 gần A4).
`thumbPx` tăng từ 320 → 400 cho bitmap sắc nét hơn.

## Lưu ý kỹ thuật
- `buildPagedHtml()` trong DocReader là dead code — không được gọi từ `read()`
- DOC luôn dùng `buildSimpleHtml()` (simpleDocPreview=true) hoặc `buildRichHtml()` (false)
- Cả hai đều dùng `#doc-content` single container với JS-based pagination
- `.doc-page-num` span là direct child của separator div, không phải của `#doc-content`
