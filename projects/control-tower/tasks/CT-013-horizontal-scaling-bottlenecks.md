---
id: CT-013
title: "Nghiên cứu bottleneck còn lại cho horizontal scaling + tối ưu hệ thống"
status: todo
priority: high
risk: normal
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - log.md (568 dòng, append-only, mọi skill cùng ghi)
  - projects/control-tower/control-tower.md (next_task_id counter — shared mutable cell)
  - index.md §3 (bảng tiến độ — duplicate state với <name>.md + frontmatter)
  - AGENTS-EXPERIMENTAL.md §18.1 (events.jsonl — định nghĩa nhưng chưa implement)
  - knowledge/metrics/prediction-accuracy.md (single metrics file, shared-write)
  - inbox.md (single shared inbox)
flows: []
tests: []
dispatched: null
in_review: null
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "blast_radius: 6 files khảo sát, deliverable 1 research doc (-0.0)"
    - "hub_bridge: n/a — meta-project không có code graph (-0.0)"
    - "no_tests: true — research task, deliverable là doc không phải code (-0.1)"
confidence_interval: [0.75, 0.95]
created: 2026-07-22
updated: 2026-07-22T19:35
---

# CT-013: Nghiên cứu bottleneck còn lại cho horizontal scaling + tối ưu hệ thống

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh (Context)

Vấn đề đầu tiên — AGENTS.md 636 dòng load mỗi session — đã được xử lý (split thành 4 file, core còn 152 dòng, commit `cf9886f`). Task này nghiên cứu **các vấn đề còn lại** cản trở việc triển khai ngang (nhiều session/agent/project chạy song song) và tối ưu hệ thống.

Khảo sát sơ bộ (2026-07-22, bằng chứng thật từ repo) tìm được 6 ứng viên bottleneck:

1. **`log.md` phình vô hạn + shared-write**: 568 dòng sau ~1 ngày vận hành thật; append-only, mọi skill (`/pm`, `/verdict`, `/lint`...) cùng ghi vào 1 file → (a) git conflict khi nhiều session ghi song song, (b) bước "similar tasks in log.md had <50% success" của prediction score phải đọc file ngày càng dài.
2. **`next_task_id` race condition**: counter nằm trong `<name>.md` — 2 phiên `/pm` song song trên cùng project sẽ cấp trùng ID. Task-per-file đã giải quyết conflict nội dung task, nhưng counter vẫn là shared mutable cell.
3. **`events.jsonl` chưa tồn tại**: `AGENTS-EXPERIMENTAL.md` §18.1 định nghĩa event log machine-readable cho stigmergic coordination, nhưng chưa skill nào ghi nó → agent song song không có state để poll, §18.2 (auto-claiming) không hoạt động được thật.
4. **Không archive task `done`**: 24/27 task đã done vẫn nằm trong `tasks/` — `/lint` và `/report` scan lại toàn bộ mỗi lần chạy, độ phức tạp tăng tuyến tính vĩnh viễn theo lịch sử.
5. **Tiến độ duplicate 3 nơi**: frontmatter từng task + `## Tasks` trong `<name>.md` + bảng §3 `index.md` — sync thủ công qua `/report`, dễ lệch giữa 2 lần chạy.
6. **`inbox.md` + `knowledge/metrics/prediction-accuracy.md` single-file shared-write**: cùng mô hình conflict như log.md khi scale số người/agent đẩy việc vào hệ.

## Tiêu chí nghiệm thu (AC)

> Deliverable là **research doc** (không phải code) — đích: `knowledge/research/horizontal-scaling-bottlenecks.md` (frontmatter chuẩn `AGENTS-PLAYBOOK.md` §11.3, `type: research`, `scope: general`).

- [ ] AC1: Research doc xác nhận/bác bỏ **từng ứng viên** trong 6 bottleneck ở trên, kèm bằng chứng cụ thể (số dòng, đường dẫn, kịch bản conflict tái hiện được) — không chấp nhận khẳng định suông.
- [ ] AC2: Quét thêm **ít nhất 2 góc chưa nằm trong danh sách** (gợi ý: chi phí re-read của skill khi 1 session chạy nhiều macro liên tiếp; giới hạn của mô hình 1-session-1-user khi có nhiều stakeholder; token cost của review sheet; khả năng chia project registry khi số project tăng 5→20) — mỗi góc kết luận rõ "là vấn đề" hay "chưa phải vấn đề, vì sao".
- [ ] AC3: Mỗi vấn đề xác nhận có: mức độ ảnh hưởng đến horizontal scaling (blocker / friction / nice-to-have), độ phức tạp khắc phục (S/M/L), và **hướng khắc phục đề xuất** (chưa cần design chi tiết).
- [ ] AC4: Kết thúc bằng **roadmap ưu tiên**: danh sách task ứng viên (1 vấn đề = 1 task, đúng nguyên tắc "1 task = 1 PR" `AGENTS.md` §2.2), thứ tự triển khai + lý do, ghi rõ task nào đụng AGENTS.md/skill thì cần ADR đi kèm (Project Gate của control-tower).
- [ ] AC5: Task này **chỉ nghiên cứu** — không sửa AGENTS*.md, không sửa skill, không tạo events.jsonl. Mọi thay đổi thật nằm ở các task follow-up sinh từ AC4.

## Plan

> Spec Gate đã được User duyệt (2026-07-22). Deliverable = 1 research doc, KHÔNG sửa AGENTS*.md/skill/config nào (AC5). Executor làm việc ngay trong repo `control-tower` (meta-project, không cần code graph).

### Step 1 — Xác nhận 6 bottleneck ứng viên bằng bằng chứng đo được (→ AC1)

Với từng ứng viên, thu thập số liệu thật thay vì khẳng định suông:

1. **log.md**: đếm số dòng + số entry theo ngày (`grep -c "^## \["`), đo tốc độ tăng trưởng/ngày từ timestamp; liệt kê các skill đọc log.md (grep `log.md` trong `.claude/skills/**`) để chỉ ra chi phí đọc tăng theo thời gian; mô tả kịch bản conflict: 2 session cùng append → git merge conflict ở cuối file.
2. **next_task_id race**: viết kịch bản tái hiện từng bước (session A đọc `next_task_id: 14` → session B đọc 14 → cả hai tạo CT-014 → conflict cả file task lẫn counter); đối chiếu tiền lệ task-per-file (`AGENTS.md` §2) đã giải quyết nửa nào và nửa nào còn lại.
3. **events.jsonl gap**: grep `events.jsonl` trong `.claude/skills/**` để chứng minh không skill nào ghi nó dù `AGENTS-EXPERIMENTAL.md` §18.1 yêu cầu "written by the same skills that already write log.md"; kết luận §18.2 auto-claiming không vận hành được.
4. **Archive**: đếm task theo status (hiện 24 done / 27); ước lượng chi phí `/lint`/`/report` phải đọc frontmatter mọi file mỗi lần chạy; chiếu theo tốc độ tạo task thực tế (27 task / 2 ngày) để ngoại suy 3-6 tháng.
5. **State duplicate 3 nơi**: liệt kê chính xác 3 vị trí lưu cùng thông tin status; tìm ví dụ lệch thật trong lịch sử git (nếu có) hoặc mô tả kịch bản lệch giữa 2 lần `/report`.
6. **inbox.md + prediction-accuracy.md**: xác nhận cùng mô hình shared-write; đánh giá mức nghiêm trọng THẤP HƠN log.md (tần suất ghi thưa hơn) — được phép kết luận "chưa phải blocker" nếu số liệu ủng hộ.

### Step 2 — Quét ≥2 góc mới ngoài danh sách (→ AC2)

Chọn tối thiểu 2 trong 4 góc gợi ý (hoặc góc khác nếu phát hiện trong lúc làm Step 1), mỗi góc kết luận rõ "là vấn đề / chưa phải vấn đề, vì sao":
- **Chi phí re-read trong 1 session**: các skill đều có mệnh đề "if not already read this session" — đo tổng số dòng phải đọc khi chạy chuỗi `/pm` → `/review-order` → `/verdict` trong 1 session mới.
- **Mô hình 1-session-1-user**: điều gì xảy ra khi 2 người (hoặc người + cron agent) cùng vận hành control-tower — có cơ chế khóa/nhận biết session khác không?
- **Token cost của review sheet**: phiếu review copy nguyên AC/DoD — đo kích thước trung bình phiếu hiện có trong `projects/*/reviews/`.
- **Project registry ở scale 20 project**: bảng §2 index.md + colorGroups + canvas đều thủ công — bước onboarding nào (AGENTS-PLAYBOOK.md §10) sẽ gãy trước.

### Step 3 — Chấm điểm từng vấn đề đã xác nhận (→ AC3)

Bảng chuẩn: `Vấn đề | Impact (blocker/friction/nice-to-have) | Complexity (S/M/L) | Hướng khắc phục đề xuất`. Hướng khắc phục chỉ cần 1-3 câu định hướng (ví dụ: "log.md → tách log theo tháng hoặc theo project, giữ format §7"), KHÔNG design chi tiết — design là việc của task follow-up.

### Step 4 — Roadmap ưu tiên → danh sách task ứng viên (→ AC4)

- 1 vấn đề xác nhận = 1 task ứng viên (đúng `AGENTS.md` §2.2 "1 task = 1 PR"), mỗi task ghi: tên đề xuất, phạm vi 1 câu, depends_on nếu có, và **cờ "cần ADR"** nếu đụng AGENTS*.md/skill (Project Gate của control-tower).
- Xếp thứ tự: blocker trước, ưu tiên task mở khóa task khác (ví dụ events.jsonl mở khóa auto-claiming §18.2 và Model A CT-012).
- Roadmap là ĐỀ XUẤT — việc tạo task thật vẫn đi qua `/pm` từng cái, User duyệt từng Spec Gate.

### Step 5 — Đóng gói research doc

Viết `knowledge/research/horizontal-scaling-bottlenecks.md` với frontmatter chuẩn `AGENTS-PLAYBOOK.md` §11.3 (`type: research`, `scope: general`, `related:` trỏ [[CT-008-stigmergic-coordination]], [[CT-012-model-a-cli-agent-orchestration]]), cấu trúc: Tóm tắt → Phương pháp khảo sát → 6+2 phát hiện (Step 1-2) → Bảng chấm điểm (Step 3) → Roadmap (Step 4). Tự đối chiếu đủ 5 AC trước khi báo done, rồi handoff qua `/review-order` (reviewer ≠ executor).

## Sub-tasks

- [ ] Xác nhận/bác bỏ 6 bottleneck ứng viên với bằng chứng cụ thể (AC1)
- [ ] Quét ≥2 góc bổ sung ngoài danh sách (AC2)
- [ ] Chấm impact + complexity + hướng khắc phục cho từng vấn đề (AC3)
- [ ] Viết roadmap ưu tiên → danh sách task follow-up ứng viên (AC4)
- [ ] Đóng gói research doc vào `knowledge/research/` với frontmatter chuẩn §11.3

## Research References

- Commit `cf9886f` — split AGENTS.md (vấn đề #0 đã xử lý, làm mốc so sánh cách tiếp cận)
- [[CT-008-stigmergic-coordination]] — POC định nghĩa `events.jsonl` §18.1 nhưng chưa implement
- [[CT-012-model-a-cli-agent-orchestration]] — Model A orchestration; nhiều CLI agent song song sẽ khuếch đại các bottleneck shared-write ở trên
- `AGENTS.md` §2 — task-per-file rationale (tiền lệ giải quyết conflict bằng cách tách file)
