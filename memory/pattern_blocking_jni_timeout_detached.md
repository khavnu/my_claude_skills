---
name: pattern_blocking_jni_timeout_detached
description: "Ticket #273 waveform loading vô hạn — root cause THẬT là WaveformBarsView show WaveformLoading khi samples==null (không phân biệt loading vs failed), KHÔNG phải native hang; kèm pattern timeout blocking JNI (phòng hờ, chưa chắc merge)"
metadata:
  node_type: memory
  type: project
  originSessionId: f4c45403-aff4-46c7-93a2-fffdb2b5885e
---

## Root cause THẬT của #273 (xác định bằng log runtime 2026-08-05, CHƯA FIX — để mai)
Loading vô hạn KHÔNG do native hang. Log: `getWaveformData` trả về **nhanh ~23ms** với `null` → `ProcessingFailed(No audio samples decoded)` → VM set `isLoadingWaveform=false`, `waveformSamples=null`; `WaveformView` nhận `isLoadingWaveform=false` OK (log `View: false`).

Nhưng loading VẪN hiện vì **`WaveformBarsView.kt` (edit_common/component) dòng ~38**:
```kotlin
if (samples == null) { WaveformLoading(modifier); return }
```
`WaveformView` render: `if (isLoadingWaveform) WaveformLoading else WaveformBarsView(waveformSamples)`. Khi decode FAIL: `isLoadingWaveform=false` + `samples=null` → nhảy `else` → `WaveformBarsView(null)` → **lại show `WaveformLoading` mãi mãi**. Component coi `null == đang load`, không phân biệt "load xong nhưng thất bại".

**Hướng fix (để mai)**: phân biệt loading vs failed/empty. `WaveformBarsView` có 3 caller (`WaveformView`, `FadeComponents`, `ResultWaveformPanel`) → cân nhắc:
- sửa tại `WaveformView` (không cho `null` vào `else`, render empty), HOẶC
- đổi contract `WaveformBarsView`: `null` = empty (không tự show loading), để parent lo loading qua `isLoadingWaveform`.
User CHỐT: KHÔNG thêm error text (`isError` đã rollback) — chỉ cần ẩn loading, hiện waveform trống là đủ.
⚠️ Nhớ gỡ log debug `Timber.d("CheckLoadWaveform...")` ở WaveformExtractor / EditTrimViewModel / WaveformView:125 sau khi fix. User đã rollback code branch cuối session.

## Pattern timeout blocking JNI (PHỤ — KHÔNG phải fix của #273; user CHỐT GIỮ LẠI ở WaveformExtractor như lớp phòng thủ, đã apply + 7/7 test pass 2026-08-06)
Vẫn đúng về mặt phòng thủ nếu `getWaveformData` thật sự KẸT (file khác): nó là blocking JNI (không suspend/cancellable) → `withTimeoutOrNull { withContext(io){ blockingCall() } }` KHÔNG unblock được (cancellation cooperative, không có suspension point). Cũng đừng để decode làm child `coroutineScope` (scope join child → treo lại). Cách chạy được: decode **detached** trên `@ApplicationScope externalScope` rồi race `withTimeoutOrNull { deferred.await() }` (await mới cancellable):
```kotlin
val decode = externalScope.async(ioDispatcher) { extractWithFfmpeg(filePath, targetCount) }
return try {
    withTimeoutOrNull(EXTRACT_TIMEOUT_MS) { decode.await() }
        ?: Result.Failure(AudioOperationError.ProcessingFailed("Waveform extraction timed out"))
} finally { decode.cancel() }   // finally chỉ cleanup job, không flip UI state — hợp rule
```
KHÔNG gọi `processor.cancel()`: `AudioProcessor` là `@Singleton` dùng chung, dễ huỷ nhầm render/save. Native thread bỏ rơi leak bounded 1. Xem [[feedback_coroutine_finally_ui_state]].

Note phụ (ngoài scope): 2 `@ApplicationScope` trùng tên ở `di/` (AppModule) và `di/util/` (CoroutineScopesModule) — redundant binding, nên gộp.
