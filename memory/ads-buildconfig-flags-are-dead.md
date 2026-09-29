---
name: ads-buildconfig-flags-are-dead
description: Trong android_qr5 KHÔNG flag BuildConfig ads nào được đọc (kể cả TEST_ADS, từ 2026-09-16) và mọi ad unit ID production đều rỗng → ads không bao giờ hiện
metadata: 
  node_type: memory
  type: project
  originSessionId: 251b41e3-d059-4932-9857-8baad4a99169
  modified: 2026-09-18T02:49:54.549Z
---

Trong `android_qr5`, các `buildConfigField` về ads khai báo trong `app/build.gradle`
(`ENABLE_ADS`, `ENABLE_BANNER_ADS`, `ENABLE_MEDIUM_BANNER_ADS`, `ENABLE_LIST_BANNER_ADS`, ...)
**không được reference ở bất kỳ file source nào** — vestigial. Nguồn sự thật thực tế:

- `AdsConfig.isTestAdsMode` — **hardcode `false` trở lại từ commit `38716388` "AdsConfig: disable
  test ads mode" (2026-09-16, Dien Ngo)**, huỷ việc wire vào `BuildConfig.TEST_ADS` mà commit
  `3e019220` đã làm. Field là `final`, không setter → `BuildConfig.TEST_ADS` giờ **không được
  reference ở bất kỳ đâu** trong source, kể cả flavor Dev (`TEST_ADS=true`).
- `AdsConfig.isReleaseTestAdsEnable` — toggle in-memory từ `SettingFragment`, không persist, **và
  không bao giờ bật được từ UI**: `SettingFragment:525-528` ẩn luôn switch khi cờ đang `false`
  (`if(!isReleaseTestAdsEnable()) { setVisibility(GONE); return; }`) → chicken-and-egg.
- `ADS_BANNER`, `ADS_APP_OPEN`, `ADS_INSTER_*`, `ADS_*_NATIVE` **vẫn là `final String ""` (rỗng)**
  trong repo. `final` nên Remote Config không thể ghi đè.
- Firebase Remote Config chỉ bật/tắt (`key_enable_banner_ad` → `PREF_KEY_ENABLE_BANNER_ADS`),
  **không** cấp ad unit ID.
- AdMob APPLICATION_ID thì có thật: `ids.xml` → `ca-app-pub-3084906235921708~3400263423`.

**Why:** Ad unit ID rỗng → AdMob trả `Ad failed to load : 1`
(`Cannot determine request type. Is your ad unit id correct?`) cho mọi loại ad. Rất dễ chẩn đoán
lệch sang "Remote Config tắt ads" hoặc "no fill". Dấu hiệu phân biệt: log
`CheckBannerAds StartRequest: 5` vẫn in ra rồi mới `Error: Code 1` → gate đã pass, lỗi nằm ở ID.

**How to apply:** Ads không hiện → check `AdsConfig` ad ID trước, đừng tin CLAUDE.md của project
(nó nói sai rằng BuildConfig flags điều khiển ads). **Không flavor nào hiện ads được** cho tới khi
hoặc bật lại `isTestAdsMode`, hoặc điền ad unit ID thật. Muốn xem UI có ad để verify (ad card của
quit dialog, native ads ở Detail): tạm sửa `AdsConfig:45` thành `true`, build Dev, test, rồi revert
— đã xác nhận cách này chạy (test ad fill ngay, 2026-09-18).
