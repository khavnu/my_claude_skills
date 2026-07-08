---
name: Incremental implementation flow cho feature phức tạp
description: Với feature có nhiều architectural decision, ưu tiên discuss → decide → implement từng layer → compile → next thay vì làm toàn bộ một lần
type: feedback
originSessionId: a0d6b472-0956-4089-a572-98b65a236d42
---
Với feature phức tạp (nhiều layer, nhiều architectural decision), follow flow:

1. **Discuss** — đề xuất approach, nêu trade-off, chờ user quyết định
2. **Decide** — chỉ implement sau khi user confirm
3. **Implement một layer** — Screen, ViewModel, Repository, DataSource riêng từng bước
4. **Compile** — xác nhận xanh trước khi đi tiếp
5. **Next layer**

**Why:** Session PrintPdfScreen là minh chứng — implement toàn bộ một lần dẫn đến rollback vì kiến trúc sai. Từng bước cho phép catch architectural mistake sớm, scope rollback nhỏ, và user có thể redirect trước khi quá muộn.

**How to apply:** Khi nhận feature request phức tạp, KHÔNG implement hết một lần. Hỏi/propose từng bước, compile sau mỗi layer. Defer các thành phần chưa cần (data layer, wiring vào navigation) cho đến khi core layer ổn định.
