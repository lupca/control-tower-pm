---
pattern_id: tool-finding-misattribution
category: process
severity: high
created: 2026-07-27
updated: 2026-07-27
---

# tool-finding-misattribution

## Problem Signature

Một tool review tự động (`/code-review`, linter, static analyzer, OCR) báo một finding nghe rất thuyết phục và **quy nó cho commit đang review**. Không ai kiểm chứng bằng cách chạy lại trên commit cha, nên finding được ghi vào review sheet, verdict thành `changes`, executor mất một vòng đi sửa thứ **vốn đã hỏng từ trước** — hoặc tệ hơn, sửa một thứ không hỏng.

Biến thể nguy hiểm hơn: một khiếm khuyết ở vòng trước **vô tình che** một bug tiền tồn. Vòng sau sửa khiếm khuyết đó, bug tiền tồn lộ ra, và tool quy nó cho chính bản sửa — khiến bản sửa đúng trông như đang gây hồi quy.

## Detection

- Finding của tool không kèm bằng chứng đã chạy trên **commit cha** để đối chứng.
- Finding nằm ở vùng code mà diff **không hề chạm tới**, nhưng vẫn được liệt kê như hệ quả của diff.
- Verdict `changes` được ghi chỉ dựa trên output tool, không có bước reviewer tự tái hiện.
- Bản sửa của vòng trước "gỡ bỏ một hành vi sai" và ngay sau đó xuất hiện lỗi mới ở vùng liên quan — dấu hiệu điển hình của bug bị che nay lộ ra.

## Solution Template

1. **Mọi finding của tool phải được reviewer tái hiện trước khi tính vào commit.** Tool là nguồn gợi ý, không phải nguồn phán quyết.
2. **Đối chứng bắt buộc trên commit cha**: chạy đúng kịch bản đó ở `<ref>^`. Còn ở cha → **tiền tồn**, tách thành task riêng, KHÔNG tính vào verdict của commit hiện tại.
3. **Ghi rõ trong review sheet finding nào do tool nêu và finding nào reviewer tự xác minh** — để vòng sau biết cái nào đã được kiểm.
4. Khi bug tiền tồn lộ ra vì bản sửa gỡ lớp che, ghi nhận **cả hai sự thật**: bản sửa đúng, và bug kia có thật — đừng đổ cho bản sửa, cũng đừng bỏ qua bug.
5. Áp cả chiều ngược lại: tool **không** báo gì không có nghĩa là sạch (xem [[mandatory-tool-preflight]] — tool fail/rate-limit vẫn phải khai báo, không im lặng bỏ qua).

## Past Instances

- [[CTV2-095-snapshot-last-tool-result-pruning]] (control-tower-v2, 2026-07-27) — baseline `/code-review` báo rằng slice `compact_context` **mới** gây lỗi 400 ngược vì summary giữ `role="tool"`, quy cho commit `eb9a8a1`. Reviewer `@claude-opus-5-medium` không chấp nhận mà tự test: orphan xuất hiện ở **cả `eb9a8a1` lẫn `61878d4^`** — tức có trước khi task bắt đầu. Đúng biến thể nguy hiểm: khiếm khuyết vòng 1 (làm mất `tool_call_id`) đã **vô tình che** bug tiền tồn này; vòng 2 sửa đúng thì nó lộ ra và bị tool quy cho bản sửa. Tách thành NB-4 cho task riêng, không tính vào verdict `eb9a8a1`. Cùng phiên, OCR cũng cho 2 comment nhiễu (một cái có `suggestion_code` trùng `existing_code`) — được ghi nhận là nhiễu thay vì thành finding.
