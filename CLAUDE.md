# CLAUDE.md

Đây là repo **control-tower** — nơi giao và theo dõi task cho các dự án khác bằng ngôn ngữ tự nhiên (File-Over-API). Repo này KHÔNG chứa code sản phẩm; nó chỉ quản lý task dưới dạng Markdown và điều phối subagent đi sửa code ở các repo khác.

## Trước khi làm bất kỳ việc gì trong phiên này

1. Đọc **`AGENTS.md`** — luật chơi: phân quyền HITL, cú pháp task, quy tắc gọi `code-review-graph`, chuẩn audit log.
2. Đọc **`index.md`** — bản đồ dự án + PROJECT REGISTRY (tra `repo_root` tuyệt đối của dự án đích tại đây).

Không tự ý bỏ qua hai file trên dù task có vẻ đơn giản — chúng là single source of truth cho quyền hạn và quy trình.

## Macro

- `/pm <mô tả task> [--project <tên>]` — giao task mới (skill `pm`)
- `/ingest` — phân loại `inbox.md` thành task (skill `ingest`)
- `/report` — cập nhật tiến độ trong `index.md` (skill `report`)

## Ghi nhớ

- `.mcp.json` trong repo này đăng ký sẵn server `code-review-graph` (dùng chung binary với các repo khác) nên các tool graph khả dụng ngay cả khi cwd là `control-tower`.
- Mọi tool `code-review-graph` phải được gọi với `repo_root=<đường dẫn tuyệt đối>` tra từ PROJECT REGISTRY trong `index.md` — cwd của phiên này là `control-tower`, không phải repo đích, nên auto-detect sẽ sai.
- Không tự sửa code ở repo đích khi đang ở cấp độ COLLABORATIVE — viết task, ghi log, dừng chờ duyệt.
