---
name: No hardcoded fix values
description: Don't hardcode fixed values as workarounds — derive values from actual data
type: feedback
---

Không được dùng giá trị cứng (hardcode) để patch behavior.

**Why:** Hardcoded values (như `padding:1%`, `margin:8px`, fixed colors) không phản ánh đúng data thực tế từ file. Mỗi file PPT/DOC/XLS có layout riêng — fix cứng sẽ sai cho các file khác.

**How to apply:**
- Text box padding → đọc từ shape insets (nếu API có), không tự thêm padding
- Text color default → tính từ bg luminance (`contrastColor()`), không hardcode `#fff` hay `#000`
- Font size → tính từ PPT points, không hardcode size
- Position → tính từ Escher anchor records, không adjust thủ công
- Nếu không đọc được một giá trị, dùng CSS default/inherit, đừng dùng magic number
