---
name: feedback-reference-pattern
description: "Khi user nói \"tham khảo X\", phải đọc X trước và replicate structural patterns trung thực — không tự ý đặt tên khác hay bỏ sót cơ chế quan trọng"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a57bc916-11a4-47b4-9e20-bf77f2207f33
---

Khi user nói "tham khảo X" (file, class, pattern), đọc X trước khi viết bất kỳ dòng code nào.

**Why:** Tôi đọc ConvertViewModel rồi implement thiếu structural pattern quan trọng: `save()` không dùng shared job, dẫn đến cancel flow bị broken (preview không cancel được save và ngược lại). Tên biến có thể thay đổi cho phù hợp — nhưng cơ chế phải được giữ đúng.

**How to apply:**
1. Đọc reference file thực sự (không dựa vào memory hay inference).
2. Identify **cơ chế** (mechanisms), không phải tên: job tracking, shared/separate cancellation, loading state ownership, error handling flow.
3. **Trước khi viết code: liệt kê tất cả mechanisms từ reference thành một diff list, check từng item có trong plan chưa.** Implement chỉ sau khi list đã đầy đủ — không implement theo kiểu "nhớ gì làm nấy rồi vá sau".
4. Replicate đúng cơ chế — tên có thể adapt cho context, nhưng không được bỏ cơ chế nếu không có lý do rõ ràng.
5. Nếu cần bỏ hoặc thay đổi một cơ chế, nêu rõ lý do trước khi implement.

Ví dụ: ConvertViewModel dùng một `convertJob` chung cho cả preview lẫn save → cả hai đều cancel job cũ trước khi launch job mới → cancel một thì cancel cả hai. Đây là cơ chế, không phải naming.

Session 2026-07-02: đọc ConvertViewModel rồi vẫn thiếu 3 lần (ensureConverted, convertJob, cancelSave thừa) vì không làm diff list trước — implement piecemeal → user phải chỉ từng cái.
