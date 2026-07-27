---
agent_id: "@coordinator"
type: ai
total_tasks_executed: 1
total_tasks_reviewed: 0
success_rate: 1.00
avg_review_rounds: 1.0
coordination_defects: 8
coordination_defects_caught_by_user: 3
strengths: [decomposition, graph-sourcing, audit-logging]
weaknesses: [skips-own-verifier, prescriptive-ACs, assumes-config-is-applied, cwd-leak]
recent_trend: declining
last_active: 2026-07-27
---

# @coordinator

> Hồ sơ của chính control-tower khi đóng vai PLAN + COORDINATE. `success_rate`
> ở trên chỉ nói về task mà coordinator từng tự thực thi (1), **không** phản ánh
> chất lượng điều phối. Chất lượng điều phối đo bằng mục Coordination Defects
> dưới đây — mọi lỗi ở đó đều làm phát sinh vòng review thừa, công thừa của
> executor, hoặc suýt gây hỏng, dù task cuối cùng vẫn đóng được.

## Performance Summary

- **Tasks Executed**: 1
- **Coordination Defects ghi nhận**: 8 (2026-07-27, phiên CTV2-086..103)
- **Trong đó user phát hiện trước tôi**: 3

## Coordination Defects — 2026-07-27 (phiên phân rã autonomous coordination)

Phiên tạo 18 task (CTV2-086..103) và chạy wave 1. Cả 2/2 task được review trong
wave đều phải sửa lại; CTV2-088 mất 3 vòng. Không phải mọi lỗi đều thuộc về
coordinator, nhưng những lỗi dưới đây thì có.

### Nhóm A — bỏ qua công cụ đã có sẵn

1. **Không chạy LLM-Modulo verifier khi tạo task** (`task-creation.md` bước 11,
   bắt buộc). `.claude/verifier-rules.yaml` ĐÃ có rule `no-conflicting-tasks`
   ("no other task with overlapping files: is currently dispatched/in-review").
   Chạy verifier là phát hiện chồng lấn file của wave 1 ngay ở Spec Gate. Thay
   vào đó tôi tự tính ma trận chồng lấn lúc sắp spawn — muộn hơn nhiều vòng.
   *Không phải thiếu công cụ, mà là không dùng công cụ đã có.*
2. **Lặp lại khẳng định của user mà không kiểm chứng.** Bảng wave 1 ghi 7 task
   "đều `depends_on: []`, không đụng file nhau". Vế đầu đúng, vế sau sai hoàn
   toàn — mọi task đều đụng file với ít nhất một task khác. Tôi chuyển tiếp
   khẳng định đó vào kế hoạch thay vì tự kiểm.
3. **Không xác lập baseline repo trước khi dispatch.** Không chạy `git status`
   nên khi thấy 16 file bẩn đã không phân biệt được đâu là của executor, đâu là
   có sẵn từ trước.

### Nhóm B — viết AC sai cách

4. **AC quy định cách sắp xếp dòng lệnh thay vì bất biến** (CTV2-088 AC2:
   "đảo `_assert_status` lên trước khi trả record idempotent"). Reviewer vòng 2
   phán xử là **không implement được theo nghĩa đen**; phải viết lại thành bất
   biến ở vòng 3. Tốn một vòng review đầy đủ.
5. **AC nêu tên test nhưng không nêu dữ liệu và khẳng định** (CTV2-095 AC2:
   "có test khẳng định prefix không đổi"). Executor dựng session `messages=[]`,
   test xanh, không kiểm chứng gì. Đã thành pattern
   [[vacuous-acceptance-test]] — nhưng pattern đó ra đời **từ chính lỗi của
   tôi**, không phải từ quan sát người khác.

### Nhóm C — giả định thay vì kiểm chứng

6. **Giả định `effort:` trong agent profile được áp khi spawn.** Tạo
   `@claude-opus-5-medium` rồi spawn bằng `claude --model claude-opus-5` không
   kèm `--effort`, nên lượt review CTV2-088 vòng 1 chạy ở effort mặc định.
   `ct-dispatch.py` nhánh claude bỏ hẳn effort trong khi nhánh codex thì có —
   tôi không đọc kỹ script trước khi tin vào nó. **User phát hiện, không phải tôi.**
7. **Viết `files:` sai phạm vi cho CTV2-100.** Đưa `app/graph/state.py` vào danh
   sách sẽ gỡ, trong khi nó export `FourEyesViolation` dùng bởi `db/models.py:23`;
   `app/graph/context.py` cũng được import ở 8 chỗ. Gỡ theo danh sách đó là gãy
   `models.py`. **User hỏi mới lộ ra.**

### Nhóm D — cẩu thả thao tác

8. **Để cwd rò rỉ giữa các lệnh Bash**, ghi nhầm một `log.md` lạ vào
   `projects/control-tower-v2/tasks/`. Đã gộp lại và xoá, không mất dòng nào,
   nhưng đây là lỗi không được phép lặp với repo là nguồn sự thật.

## Rút ra

- Ba lỗi (6, 7, và vế sai của 2) do **user phát hiện trước**. Tỉ lệ này quá cao
  cho một vai trò mà cả hệ thống dựa vào để bắt lỗi người khác.
- Nhóm A và C cùng một gốc: **tin vào thứ mình chưa kiểm** — verifier có sẵn
  không chạy, script không đọc, khẳng định của người khác không xác minh. Đúng
  loại lỗi mà `/verdict` bắt executor phải chịu trách nhiệm.
- Nhóm B cho thấy AC là nơi coordinator dễ gây hại nhất: AC lỏng không làm task
  fail ngay, nó làm task **pass sai** — tốn nhiều vòng hơn là AC viết chặt từ đầu.

## Đối chiếu: coordinator soi executor bằng tiêu chuẩn nào

Trong cùng phiên này tôi hạ `recent_trend` của `@claude-sonnet-medium` và
`@gpt-5.6-luna` xuống `declining` vì họ viết test không chứng minh được gì.
Hai AC lỏng khiến chuyện đó xảy ra là do tôi viết. Tiêu chuẩn phải áp cả hai
chiều, nên `recent_trend` của hồ sơ này để `declining`.
