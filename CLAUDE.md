# CLAUDE.md

Đây là repo **control-tower** — nơi giao và theo dõi task cho các dự án khác bằng ngôn ngữ tự nhiên (File-Over-API). Repo này KHÔNG chứa code sản phẩm; nó chỉ quản lý task dưới dạng Markdown.

**Mô hình B (hiện hành):** control-tower chỉ **PLAN + COORDINATE**. Nó KHÔNG bao giờ ghi code, KHÔNG đọc diff, KHÔNG tự chạy test. EXECUTE (viết code) và REVIEW (đọc diff, chạy test) đều nằm **ngoài hệ** — người hoặc AI khác, trong repo code đích, độc lập với nhau (reviewer ≠ executor).

## Trước khi làm bất kỳ việc gì trong phiên này

1. Đọc **`AGENTS.md`** — luật chơi: vai trò PLAN/EXECUTE/REVIEW/COORDINATE, vòng đời task, cú pháp task, quy tắc gọi `code-review-graph`, chuẩn audit log.
2. Đọc **`index.md`** — bản đồ dự án + PROJECT REGISTRY (tra `repo_root` tuyệt đối của dự án đích tại đây).

Không tự ý bỏ qua hai file trên dù task có vẻ đơn giản — chúng là single source of truth cho quyền hạn và quy trình.

## Macro

- `/pm <mô tả task> [--project <tên>]` — Spec Gate → Plan Gate → `ready` → `dispatched`. Tạo file task riêng trong `projects/<tên>/tasks/`, KHÔNG tự viết code (skill `pm`).
- `/ingest` — phân loại `inbox.md` thành task (reconcile vào task có sẵn thay vì tạo trùng), hoặc route thành knowledge file vào `knowledge/`/`projects/<tên>/docs/` nếu không actionable (skill `ingest`).
- `/report` — cập nhật tiến độ trong `<tên-dự-án>.md` + `index.md`, cập nhật `knowledge/_index.md` (skill `report`).
- `/lint [--project <tên>]` — health-check backlog: task trễ hạn, thiếu AC, link file chết, mồ côi, kẹt ở `dispatched`/`in-review` (skill `lint`).
- `/review-order <task> --ref <branch|commit|PR>` — phát phiếu review cho reviewer độc lập (ngoài hệ), không tự review (skill `review-order`).
- `/verdict <task> <pass|changes> --reviewer @id ...` — ghi kết quả review, kiểm four-eyes, `pass` mới đóng task (skill `verdict`).

## Ghi nhớ

- `.mcp.json` trong repo này đăng ký sẵn server `code-review-graph` (dùng chung binary với các repo khác) nên các tool graph khả dụng ngay cả khi cwd là `control-tower`. Tool này CHỈ dùng để phân tích tĩnh (read-only) khi PLAN/COORDINATE — không dùng để đọc diff thực tế hay chạy test.
- Mọi tool `code-review-graph` phải được gọi với `repo_root=<đường dẫn tuyệt đối>` tra từ PROJECT REGISTRY trong `index.md` — cwd của phiên này là `control-tower`, không phải repo đích, nên auto-detect sẽ sai.
- Task phải có Acceptance Criteria, test (`tests:`), và file liên quan (`files:`) lấy từ graph thật — xem `AGENTS.md` mục 2, 6 trước khi dùng `/pm`/`/ingest`.
- `/pm` chỉ đi qua Spec Gate → Plan Gate rồi dừng ở `dispatched` (`AGENTS.md` mục 4) — không nhảy cóc, không tự suy diễn im lặng là đã duyệt, và **không có Code Gate nội bộ**.
- Việc viết code luôn ở ngoài hệ (executor); việc review/verify luôn ở ngoài hệ (reviewer, dùng `/code-review` của repo code đích) — control-tower chỉ phát phiếu (`/review-order`) và ghi lại kết quả (`/verdict`).
- Không bao giờ đóng task (`status: done`) ngoài luồng `/verdict pass`, và `/verdict pass` luôn từ chối nếu `reviewer:` == `executor:` (separation of duties).
- Mỗi task là 1 file riêng trong `projects/<tên>/tasks/<ID>-<slug>.md` với YAML frontmatter — không còn gộp task vào 1 file dùng chung (`AGENTS.md` mục 2).
- Knowledge files (`knowledge/`, `projects/<tên>/docs/`) không có `status`/`executor`/`deadline` — xem `AGENTS.md` mục 11 trước khi tạo/route knowledge.
