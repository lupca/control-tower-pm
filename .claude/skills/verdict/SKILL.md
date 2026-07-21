---
name: verdict
description: Ghi verdict từ reviewer độc lập vào control-tower — pass thì đóng task (cần xác nhận người), changes thì mở lại kèm findings. Kiểm four-eyes (reviewer phải khác executor). Chỉ cập nhật Markdown, không đụng code, không tự chạy test. Kích hoạt khi user gõ /verdict.
argument-hint: "<task path/ID> <pass|changes> --reviewer @id [--commit <hash>] [--notes ...]"
allowed-tools: Read, Edit
---

## Verdict — ghi kết quả review, chặn four-eyes

Skill này **không tự kiểm tra AC, không chạy test, không đọc diff** — nó chỉ ghi lại kết quả mà reviewer (ngoài hệ) đã tự xác định, sau khi kiểm tra ràng buộc four-eyes.

### Bước 1 — Định vị task và parse tham số

1. Đọc `AGENTS.md` mục 1, 3, 4 nếu chưa đọc trong phiên (separation of duties, DoD, vòng đời task).
2. Tìm task theo ID/path trong `$ARGUMENTS`: Glob `projects/*/tasks/<ID>-*.md` nếu User cho ID (vd `PMI-001`), hoặc theo path đầy đủ.
3. Parse: verdict (`pass` hoặc `changes`), `--reviewer @id` (bắt buộc), `--commit <hash>` (bắt buộc nếu `pass`), `--notes "..."` (bắt buộc nếu `changes`).
4. Đọc frontmatter, kiểm tra `status:` hiện tại: chỉ chấp nhận verdict cho task đang `status: in-review`. Nếu khác → dừng lại, báo User (vd task chưa qua `/review-order`, hoặc đã `done` rồi).

### Bước 2 — Kiểm four-eyes (BẮT BUỘC, không được bỏ qua)

So `--reviewer` với `executor:` đã ghi trong frontmatter:
- Nếu **trùng nhau** (cùng người/cùng AI) → **TỪ CHỐI ghi verdict `pass`**. Báo User: vi phạm separation of duties (`AGENTS.md` mục 1) — cần chữ ký của một reviewer khác, độc lập với executor. Không tự động hạ chuẩn để cho qua.
- Nếu **khác nhau** → tiếp tục.

### Bước 3a — Verdict `pass`

1. Yêu cầu có `--commit <hash>` thật (hash commit thực tế của thay đổi, không bịa). Nếu thiếu, hỏi User/reviewer thay vì tự đoán hoặc bỏ trống.
2. **Đây vẫn là quyết định của con người** (`AGENTS.md` mục 3, 4: "Verdict PASS chỉ hợp lệ khi con người xác nhận"). Nếu lệnh `/verdict` này được gõ trực tiếp bởi User trong phiên hiện tại, coi đó là xác nhận. Nếu bạn (agent) tự đề xuất chạy `/verdict pass` mà không phải do User gõ trực tiếp, PHẢI dừng lại và hỏi xác nhận rõ ràng trước khi ghi.
3. Đánh dấu toàn bộ AC và sub-task liên quan trong body thành `- [x]`.
4. Cập nhật frontmatter: `status: done`, `reviewer: "<--reviewer>"`, `result_ref:` (giữ nguyên hoặc cập nhật commit thật), `updated: <hôm nay>`.
5. Nếu task có khai báo `depends_on:` (xem `AGENTS.md` mục 2.2): nêu cho User những task nào có thể mở khóa tiếp theo, vì hiện chưa có cơ chế tự động parse/mở khóa — không tự suy diễn.
6. Ghi 1 entry vào `log.md` (`operation: verdict`, format `AGENTS.md` mục 7), field `Commit:` = hash thật vừa nhận.
7. Báo User tóm tắt: task nào đã đóng, ai review, commit nào.

### Bước 3b — Verdict `changes`

1. Yêu cầu có `--notes` mô tả cụ thể cần sửa gì (không chấp nhận "changes" trống — hỏi lại nếu thiếu).
2. Thêm mục `## Findings từ reviewer` vào body của task (dưới `## Plan` hoặc cuối file), liệt kê từng ý trong `--notes` thành sub-task rework dạng `- [ ]`.
3. Cập nhật frontmatter: `status: changes-requested`, `updated: <hôm nay>`. Giữ nguyên `executor:` (mặc định executor cũ sẽ sửa lại) trừ khi User nói đổi executor.
4. Ghi 1 entry vào `log.md` (`operation: verdict`, `Trạng thái: Chờ duyệt` hoặc mô tả rework, `Commit: n/a`).
5. Báo User: task đã mở lại kèm findings, khi executor sửa xong và báo lại, cần cập nhật `status: dispatched` (giữ hoặc đổi `executor:`) rồi chạy lại `/review-order` với `--ref` mới.

### Lỗi thường gặp cần tránh
- Ghi verdict `pass` khi `reviewer:` == `executor:` — luôn từ chối, không có ngoại lệ.
- Tự bịa commit hash khi User/reviewer không cung cấp.
- Tự chạy test hoặc đọc diff để "xác nhận thêm" AC — không phải việc của `/verdict`, tin vào kết quả reviewer đã báo.
- Đóng task khi `status:` không phải `in-review` (vd task chưa từng qua `/review-order`).
