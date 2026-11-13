---
name: splash-icon-spec
description: Splash icon geometry for this app (Theme.SplashScreen, no icon background) on Android 12+ and 8–11, verified from core-splashscreen 1.0.1 AAR; QA #7 status
metadata:
  type: project
---

QA #7 (2026-10-06): splash icon blurred + cut. Cause: `themes.xml` `windowSplashScreenAnimatedIcon=@mipmap/ic_launcher` (legacy PNG, max 192 px, full-bleed square).

Geometry (verified by unzipping `~/.gradle/caches/.../core-splashscreen-1.0.1.aar`, `res/values/values.xml` + `res/drawable-v23/compat_splash_screen_no_icon_background.xml`):
- No icon background (our theme): icon canvas 288 dp, visible circle 192 dp. Android 8–11 (minSdk 26) draws it as `windowBackground` layer-list: icon 288 dp + oval ring 410 dp / stroke 109 dp → same 192 dp circle.
- With `Theme.SplashScreen.IconBackground`: canvas 240 dp, circle ≈ 158–160 dp (mask 342 / stroke 92).

Repo has no hi-res icon: `img_app_icon.png` 240 px; `iosApp/.../AppIcon.appiconset/app-icon-1024.png` is the KMP template placeholder (wrong iOS icon). Figma page "7. Splash & app icon" (moved there 2026-10-06 at user request): 7.1 vector redraw + export frames (master 1024, ic_launcher_background/foreground 108 dp, ic_splash 288 dp), 7.2 portrait splash mocks + spec + QA screenshot + asset note, 7.3 landscape/tablet splash. Code fix DONE 2026-10-06 (uncommitted): vector drawables generated from the Figma geometry — `drawable/ic_launcher_background.xml`, `ic_launcher_foreground.xml` (art scale 0.27), `ic_splash.xml` (288 dp; originally its own 192 circle + art 0.72 — changed by QA #50, see below), `mipmap-anydpi-v26/ic_launcher{,_round}.xml`, legacy PNG mipmaps deleted, `src/main/ic_launcher-playstore.png` 512. Verified on Pixel 9 API 37 and AVD `Pixel_2` (API 27, start with `-port 5556`, boots in ~12 s; user allowed it 2026-10-06): splash + App-info icon correct on both. Gotcha: `adb shell am start` on Android 13+ shows the solid-colour splash WITHOUT icon; launch with `monkey -p <pkg> -c android.intent.category.LAUNCHER 1` to see the icon.

**Why:** next session on #7 / app icon must not re-derive the compat sizes or trust the iOS 1024.
**How to apply:** export from Figma (or designer master), add adaptive `mipmap-anydpi-v26/ic_launcher.xml` + a dedicated splash drawable; check on Pixel 9 (API 37) and an API 26–30 device. See [[landscape-design]].

**QA #50 (2026-10-21, uncommitted on fix_bugs/fix_32):** QA wanted the splash art bigger, centred, and without the gradient circle. `ic_splash.xml` now has no circle (the art sits on `windowSplashScreenBackground` #499BE2). Group is scale 0.76 at translate 53.446/49.000, optically centred with the #47 rule (halfway point = source (119.15,125) → canvas 144,144). Hard size limit: the farthest point is the outer bell wave, which reaches 94 dp from the centre at 0.76; 0.78 already touches the 96 dp mask. Verified on AVD Pixel_9 (API 36, 5554) + Pixel_2 (API 27, 5556) via screenrecord: nothing cut. Figma page 7: all splash frames updated (circle instances removed) + note card "QA #50 — splash art" (133:2483) in section 7.2.

**Splash blur on Android 12+ (2026-10-27, branch fix_bugs/fix_ui, uncommitted):** a static `windowSplashScreenAnimatedIcon` is rasterised small by SystemUI and scaled up → edges ~2–3 px soft (obvious on the Pixel_Tablet AVD, 2560×1600). Fix: `drawable/ic_splash_animated.xml` = `animated-vector` over `ic_splash` (group named `art`) with a no-op 1 ms scaleX animator (value = the group's 0.76); theme points to it. Verified: before/after 4× crop on Pixel_Tablet (`~/Tmp/claude/drink_water2/splash/splash-tablet-before-after.png`), API 27 compat splash unchanged. If the art scale changes, update the animator value too. Capture tip: on-device `screencap /sdcard/sN.raw` loop beside `monkey` launch catches the splash (adb exec-out per frame is too slow); delete the raws — 10 of them filled the tablet AVD. Don't judge sharpness on a `wm size` override (scaled display blurs everything).
