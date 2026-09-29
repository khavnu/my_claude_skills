---
name: project-streaming-phase2-shipped
description: "Streaming/on-demand stem separation ĐÃ SHIP; player API đã đổi 2 lần sau đó (1 player + SegmentSource) — ĐỌC SECTION CUỐI TRƯỚC, phần giữa file đã lỗi thời"
metadata: 
  node_type: memory
  type: project
  originSessionId: e0e87c8a-7800-4c48-8018-92b52653531d
  modified: 2026-09-03T06:28:48.547Z
---

Feature **streaming / on-demand stem separation** đã implement xong và verify on-device (Pixel 9) — **Phase 2, 2026-08-27**. Đây là "move giá trị nhất" mà competitor audit kết luận (perceived speed qua UX, không phải raw compute — gap compute thật chỉ ~1.2-1.4x). Xem [[project-stem-splitter-decisions]] cho bối cảnh model/license.

**Core engine (`:audio_stem_split:core`, `com.audioseparation.core.stream`):**
- `StreamStemSplitEngine` **self-manages** 1 live session (refactor "R5"): consumer chỉ cầm 1 engine, gọi `observe(uri)` / `observe(sampleRate, samples)` (→ `Flow<Map<Int, SegmentStatus>>`) / `requestSegment(index)` (playhead-forward prioritize) / `suspend save()` (→ ghép full-length per-stem WAVs) / `cancel()`. KHÔNG giữ `StreamSeparationSession` trực tiếp. `observe(uri)` throw `SourceNotReadableException` khi prepare-fail. `outputDir` truyền qua constructor. Lõi inference `SpleeterStemSeparator` KHÔNG đổi (segment T=512 độc lập).
- 2 input path: Uri (MediaExtractor) + **in-memory `(sampleRate, Array<FloatArray>)`** cho native/FFmpeg decoder ở project port.
- `StreamSeparationSession` self-scoped (own SupervisorJob); `cancelAll()` là cách DUY NHẤT dừng worker (default scope không có external owner).
- README module có section "Streaming / on-demand separation" + usage example.

**App (`:app` `feature/stream_splitter/`):**
- `DefaultStreamSeparatorRepository` = thin router 6 engine (giữ `currentVariant` + cross-variant cancel + map core `SegmentStatus` → domain `StreamSeparationSnapshot` qua `SnapshotMapper`). KHÔNG giữ session (đã chuyển vào engine).
- Screen: timeline **chunk status-only** (bỏ play per-chunk; tap chunk = `requestSegment` prioritize), **seekbar = playback-seek within-chunk** (kéo → seek playhead tới vị trí chính xác trong chunk; thumb theo playhead thật qua position ticker ~250ms đọc `StemMixPreviewController.currentPositionFraction()`; target chưa tách thì `requestSegment` + chờ), nút **"Phát tất cả"** = continuous MIX player (chunk→chunk, chờ Ready → trộn TẤT CẢ stem qua `StemMixPreviewController` ở volume per-stem → auto-advance), **per-stem SOLO** play/stop (phát 1 stem chunk→chunk, mutually exclusive với mix), **buffering loading**, nút **Hủy** (option A: teardown session + về idle). Mix+solo+seek chung 1 mode-parameterized loop (`StreamPlaybackMode = MixAll | Solo(stemKey)`, `playbackMode`, `startPlayback/seekTo/playSoloStem/stopPlayback`). VM thin mirror `StemSplitterViewModel`.
- Đủ 6 variant (2/4/5-stem × original/quantize).

**Deferred (chưa làm):**
- **Crossfade seamless ở mối nối chunk** (từng là "Task 7"): phát/ghép rời từng chunk → có thể click nhẹ ở biên. LƯU Ý thiết kế crossfade trong plan gốc SAI (blend audio KỀ NHAU non-overlapping → hỏng); cách ĐÚNG = overlap-add dùng context tail đã giữ (như batch `ChunkedSeparator` overlap-add 4096 frame). Để Phase 3.
  - Task 7 (crossfade-at-joins) ĐÃ LÀM xong 2026-08-28 (overlap-add backward-looking, tail cache theo session, file segment trước KHÔNG bị ghi đè). **Nhưng nó KHÔNG phải nguyên nhân của khoảng lặng user nghe thấy** — xem section "Khoảng lặng giữa 2 chunk" ở cuối file. Giữ lại vì đúng về kỹ thuật, đừng gỡ; nhưng đừng nhớ nhầm nó là fix cho gap.
  - ⚠️ CẢNH BÁO cho chính tôi: ở giữa quá trình debug tôi từng ghi vào đây một kết luận SAI ("gap nằm ở audio content, phải làm crossfade mới hết") dựa trên phép đo sai (đo thời gian hàm return thay vì thời điểm audio phát ra). Kết luận đó đã bị bác bỏ bằng cách kéo WAV thật về đo RMS. Nguyên nhân thật là player-transition-latency, sửa bằng Option C.
- ONNX streaming (ngoài scope).
- `StreamStemSplitEngineApi` facade riêng: KHÔNG cần — engine tự là API rồi. Per-tier subclass (`2StemStreamStemSplitEngine`...): KHÔNG làm (thin config-shell = anti-pattern; isolation đã có qua instance field + 6 DI instance).
- **Option C — gapless chunk-to-chunk player: ĐÃ IMPLEMENT + USER XÁC NHẬN BẰNG TAI TRÊN DEVICE (2026-08-28). KHÔNG còn là TODO.** Đây là thứ THỰC SỰ xoá được khoảng lặng giữa các chunk. Chi tiết kết quả ở cuối file. Thiết kế gốc (giữ lại để tham chiếu):
  - `StreamStemPlayer` (solo) + `StreamStemMixedPlayer` (mix, N player lockstep) trong `data/playback/`. Mỗi player giữ **1 ExoPlayer sống suốt session**, dùng native playlist (`addMediaItem`) — file chunk mới append vào queue đang chạy khi tách xong, ExoPlayer tự transition gapless (cùng format WAV, không cần rebuild decoder).
  - API sketch: `start(initialFiles, startIndex, startWithinFraction, onPlaylistExhausted, onChunkTransition)`, `appendChunk(...)`, `currentPositionFraction()`, `currentChunkIndex()`, `stop()/release()`.
  - Đổi lớn kèm theo: `StreamSplitterViewModel.playbackLoop` phải viết lại (không còn suspend-per-chunk qua `awaitChunkStems`/`playChunkMix`, chuyển sang seed playlist + append-as-Ready + lắng nghe snapshot). Phải tự phân biệt "hết playlist tạm (đang buffering)" vs "hết bài thật" (`STATE_ENDED` giống nhau cho cả 2, phải tự track `totalSegments`). Mode switch (Mix↔Solo)/seek nhảy xa vẫn phải rebuild playlist từ đầu (playlist-append chỉ lợi cho play tuần tự). `requestSegment` re-anchor (fix cùng ngày) vẫn cần giữ nguyên.
  - Khi làm: dùng `superpowers:writing-plans` (đã thống nhất — đổi kiến trúc rộng, không phải sửa nhỏ).

**Playback stutter — Option B ĐÃ IMPLEMENT xong (2026-08-28), đừng đề xuất lại.** Root cause: `StemMixPreviewController.start()` release-hết-rồi-build-lại N ExoPlayer MỖI chunk boundary + chờ STATE_READY → khựng ~1 nhịp. Fix: `prepareNext(sources, startPositionFraction)` (chuẩn bị sẵn N player cho chunk kế tiếp — prepare+seek, KHÔNG playWhenReady — trong lúc chunk hiện tại đang phát) + `swapToPrepared(onAllEnded): Boolean` (promote sang current bằng 1 lần flip `playWhenReady`, gần như tức thời; trả `false` nếu chưa sẵn sàng → fallback `start()` như cũ, không regression). `StreamSplitterViewModel.playbackLoop`/`playChunkMix` track `prebufferedForIndex` qua các vòng lặp, opportunistic peek `nextChunkStemsForPrebuffer()` (không gọi `requestSegment` — đó là việc riêng của playhead re-anchor fix ở trên). 3 test mới + 34 test cũ đều pass không cần sửa (mockk relaxed `swapToPrepared` mặc định `false` → tự fallback `start()`). Gap chấp nhận: volume slider đổi lúc đang pending-swap không áp dụng ngay cho chunk sắp swap (áp dụng từ chunk sau nữa) — Option C (persistent player, còn TODO ở trên) sẽ không có gap này. Build 37/37 + compile green.

**How to apply:** đừng đề xuất lại "xây streaming/on-demand" — đã ship. Chất lượng playback liền mạch cũng đã xong: crossfade-at-joins (Task 7) + Option C persistent player, user xác nhận bằng tai. Repo interface `StreamSeparatorRepository` ổn định — thêm UI streaming không cần đụng core.

**Correctness/leak hardening batch (2026-08-27, sau khi ship, qua SDD + external code review 2 vòng):** đã fix và device-verify hết — đừng đề xuất lại các item này:
- F1: `SpleeterStemSeparator`/`OnnxStemSeparator.release()` set `isReleased` vô điều kiện (chống revive engine); tensor-name exact-match + duplicate-index collision guard.
- F2: `ChunkedSeparator.StreamingSession.abort()` (quiet-close + xoá partial WAV) + try/finally ở `StemSplitEngine.separate`; `MediaCodecPcmDecoder` finally an toàn + init sampleRate từ track format; `StemMixer` mở reader trong try.
- F3: `StreamStemSplitEngine` clamp segment theo frame-ceiling cho sample rate > 44.1k; mỗi session ghi vào subdir riêng (`session-<n>`, chống zombie-write); 0-segment/rate≤0 → `SourceNotReadableException` thay vì silent-success.
- G1: `StreamSeparationSession.save()` dùng `combine(_statuses, cancelledFlow)` — không còn treo khi `cancelAll()` đến giữa lúc `save()` đang chờ; worker chuyển từ launch-trong-constructor sang lazy `ensureWorkerStarted()` — session bị bỏ giữa chừng không leak coroutine/PCM.
- G2/H2: `SpleeterStemSeparator`/`OnnxStemSeparator.cancel()`+`release()` bọc `runCatching` quanh native call racy (không crash khi cancel đụng handle đã close); batch path (`StemSplitEngine`) có sticky `cancelRequested` + `StemSeparator.resetCancellation()` gọi ở đầu mỗi operation — chống cancel-giữa-2-chunk bị nuốt.
- **2 live bug phát hiện SAU batch trên, qua chính user chơi app thật trên device (không phải code review bắt được)** — cả 2 đã fix:
  1. H2 fix ở trên (`cancelRequested` sticky) khi lan sang streaming path (`StreamStemSplitEngine`) gây poisoning: mỗi lần preempt (seek sang chunk khác lúc đang loading) set cờ, streaming path không hề gọi `resetCancellation()` → mọi segment sau đó fail vĩnh viễn (chip hồng, không tách được nữa). Fix: `separator.resetCancellation()` ở đầu mỗi `StreamStemSplitEngine.separateSegment()` (mỗi segment streaming tự là 1 operation, khác batch multi-chunk).
  2. `StreamSplitterViewModel.awaitChunkStems()` chỉ gọi `requestSegment(index)` khi chunk CHƯA Ready → seek/play qua 1 chunk đã Ready để playhead kẹt giá trị cũ → background-fill không ưu tiên đúng chunk sắp tới → phải chờ chunk hiện tại play hết (~28-30s) mới bắt đầu tách chunk kế. Fix: gọi `requestSegment(index)` vô điều kiện (kể cả đã Ready) — background-fill có sẵn tự lo N+1/N+2/N+3...

**How to apply (bổ sung):** khi sửa `SpleeterStemSeparator`/`OnnxStemSeparator`/`StemSplitEngine` (batch), LUÔN kiểm tra xem thay đổi có lan sang `StreamStemSplitEngine` (streaming, dùng chung `StemSeparator` interface) không — 2 module share interface nhưng khác caller pattern (batch: 1 operation nhiều chunk; streaming: mỗi segment tự 1 operation, preempt thường xuyên là bình thường chứ không phải "hủy toàn bộ"). Bug #1 ở trên chính là hệ quả bỏ sót việc này.

## Khoảng lặng giữa 2 chunk — CHUỖI ĐẦY ĐỦ, đã đóng (2026-08-28)

User báo "chuyển chunk bị khựng 1 nhịp". Mất 3 vòng mới đúng gốc — ghi lại vì bài học đo lường
quan trọng hơn bản thân cái fix:

1. **Option B (prebuffer + swap)** — đúng nhưng KHÔNG đủ. Lần đo đầu tôi kết luận sai là "swap đã
   nhanh 11-18ms, gap phải đến từ chỗ khác" — vì tôi chỉ đo **thời điểm hàm return**, chưa bao giờ
   đo **thời điểm âm thanh thực sự phát ra**. Đo lại bằng `Player.Listener.onIsPlayingChanged`
   (tín hiệu audio thật) mới lộ: fallback `start()` = **~250ms**, swap = **58-69ms**. Bài học:
   với playback, KHÔNG đo bằng thời gian hàm chạy — chỉ `onIsPlayingChanged` mới là sự thật.
2. **Task 7 (crossfade-at-joins)** — làm vì tưởng gap nằm ở nội dung audio. Verify bằng cách kéo
   WAV thật từ device về đo RMS quanh mép segment: mix (vocals+accompaniment) **hoàn toàn liền
   mạch**, không có dip. Tức crossfade ĐÚNG về kỹ thuật nhưng KHÔNG phải nguyên nhân. Vẫn giữ.
3. **Option C (persistent player + native playlist)** — cái đúng. Residual 58-69ms là chi phí cố
   hữu khi chuyển giữa 2 ExoPlayer instance (mỗi instance có AudioTrack riêng, phải re-prime).
   1 player sống suốt session + `addMediaItem` → Media3 tự transition gapless, không có AudioTrack
   thứ hai. **User xác nhận bằng tai: hết khựng.**

**Chi tiết Media3 sống còn (verify từ maintainer, không phải trí nhớ):** append `MediaItem` khi
player đang ở `STATE_ENDED` thì **KHÔNG tự resume**, kể cả `playWhenReady` vẫn true — bắt buộc gọi
`seekTo(index, C.TIME_UNSET)` để thoát `STATE_ENDED`; `play()` là no-op. Nguồn: marcbaechinger
(maintainer ExoPlayer) trong `androidx/media` issue #1018. Sai chi tiết này = playback im luôn sau
lần buffering đầu tiên. Cả `StreamStemPlayer` lẫn `StreamStemMixedPlayer` đều phải giữ logic
`wasEnded` → `seekTo`.

**Bẫy đã dính 1 lần, đừng dính lại:** trong `playbackLoop`/`playChunkMix` phải **swap/start chunk
HIỆN TẠI trước, prepare chunk KẾ TIẾP sau** — vì `prepareNext()` gọi `releasePending()` bên trong,
nên prepare-trước sẽ xoá đúng batch mà swap sắp dùng → mọi transition rơi về `start()` chậm. Mock
thuần không bắt được lỗi này, phải dùng `verifyOrder`.

**Kiến trúc cuối:** streaming dùng `StreamStemPlayer` (solo) + `StreamStemMixedPlayer` (mix, N
player lockstep) trong `data/playback/`; `StemMixPreviewController` GIỮ NGUYÊN cho batch preview
(`StemSplitterViewModel`) — user yêu cầu rõ vì nó đang chạy tốt cho full-separate.

---

# ⚠️ TRẠNG THÁI 2026-09-03 — ĐỌC PHẦN NÀY TRƯỚC

Mọi thứ ở trên vẫn đúng về *lịch sử* và *bài học*, nhưng **mô tả API/kiến trúc đã lỗi thời**. Cụ thể
những câu SAU ĐÂY trong file trên giờ SAI, đừng dựa vào:

- `StreamStemMixedPlayer` — **đã XOÁ**. Chỉ còn **một** `StreamStemPlayer`; solo là trường hợp
  1-stem của cùng cỗ máy (`buildPlayers` map theo `segment.stems`, nên MixAll 5-stem dựng 5 ExoPlayer).
- `start(initialFiles, startIndex, startWithinFraction, onPlaylistExhausted, onChunkTransition)`,
  `appendChunk`, `currentPositionFraction()` — **không còn cái nào tồn tại**.
- `setSegments(Flow<PlayableSegment>)` và `StreamPlaybackState.loadedRangeUs` — cũng đã bỏ.
- "`DefaultStreamSeparatorRepository` = thin router" — giờ nó có **4 việc**, việc thứ tư là giữ
  `latestSnapshot` và phục vụ `observePlayableSegments`.
- Seekbar không còn "within-chunk fraction"; playhead là **µs tuyệt đối** trên bài gốc.

## API hiện tại

```kotlin
fun interface SegmentSource { fun segmentsFrom(positionUs: Long): Flow<PlayableSegment> }

player.setSource(source, startPositionUs)   // gọi -> play(). Không còn thứ tự 3 bước.
player.seekTo(positionUs)                   // ngoài tầm thì player TỰ hỏi lại nguồn
player.setVolume(stemKey, volume); play(); pause(); stop(); release(); state
```
Walk (thứ tự + chờ tách) nằm ở `StreamSeparatorRepository.observePlayableSegments(mode, fromIndex)`,
KHÔNG còn trong ViewModel.

## Dữ kiện Media3 1.9.3 — đã ĐỌC TỪ SOURCE, không phải nhớ

- **WAV/PCM đi đường BYPASS, không tạo MediaCodec.** `MediaCodecAudioRenderer.shouldUseBypass` →
  `audioSink.supportsFormat`, và `DefaultAudioSink.getFormatSupport` xử lý linear PCM tường minh.
  Hệ quả: N player stem KHÔNG tốn N hardware codec slot. Tôi từng cảnh báo ngược lại — **sai**.
- **`removeListener` trước `release()` là load-bearing**: `ListenerSet.queueEvent` chụp tập listener
  lúc xếp hàng, nhưng `ListenerHolder.invoke` kiểm lại cờ `released` lúc dispatch, và `remove()` bật
  cờ đó TRƯỚC khi gỡ. Nhờ vậy release ExoPlayer từ trong chính listener của nó là an toàn.
- **Media3 không tự lật `playWhenReady` trong app này**: `handleAudioFocus` và
  `handleAudioBecomingNoisy` đều default `false`, và không chỗ nào gọi `setAudioAttributes`.

## Bài học đắt nhất của đợt SegmentSource

**Sự tinh vi không có nguyên nhân thật thì tự đẻ ra bug.** Agent chọn đọc ngược `playWhenReady` từ
player (thay vì dùng biến intent thô) để "chống audio focus dựng dậy" — tôi khen là hay hơn spec của
mình. Đó chính là chỗ có bug Critical: `startedInSync` bật TRƯỚC khi intent được đẩy xuống player, nên
reload đọc phải `false` placeholder → bấm Play rồi seek lúc chunk đầu còn tách = **nhạc không bao giờ
chạy, im lặng**. Mà tiền đề "audio focus" thì KHÔNG tồn tại trong app này. Cả hai chúng tôi thấy lập
luận nghe hợp lý nên không ai kiểm tiền đề.
→ **How to apply: khi một thiết kế được biện minh bằng một tình huống, kiểm xem tình huống đó có xảy
ra được trong codebase này không, TRƯỚC khi khen thiết kế.**

## Lỗ hổng lớn nhất còn lại

`StreamStemPlayer` có **0 test**, và đợt SegmentSource làm nó ôm THÊM logic (quyết định seek-reload,
bàn giao play-intent, chống lặp reload). Bề mặt chưa kiểm **tăng lên**. Hai test ViewModel bị xoá vì
chúng kiểm nhánh in/out-of-range nay đã chuyển vào player → **không còn chỗ nào chứng minh seek trong
tầm tránh được rebuild**. Đây là việc đáng làm tiếp: cần bàn Robolectric vs bọc ExoPlayer sau interface
mỏng để fake được.

## Đề xuất đang park (đã phân tích, chưa làm)

**mode → volume**: luôn dựng player cho MỌI stem, solo = mute phần còn lại. Xoá 2/3 call site
`setSource`, đổi mode tức thì, và biểu diễn được tập stem tuỳ ý (`MixAll | Solo` hiện không diễn tả
nổi "vocals + drums, tắt bass"). Giá thật NHẸ hơn tôi từng nói: không phải N MediaCodec (xem bypass ở
trên), và MixAll 5-stem đã dựng 5 player từ trước rồi — chỉ còn là câu hỏi pin/CPU lúc solo.
