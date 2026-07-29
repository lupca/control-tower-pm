---
type: handoff
project: control-tower-v2
created: 2026-07-27
tags: [autonomous-coordination, wave-1, handoff, session-summary]
---

# Bàn giao phiên 2026-07-27 — lộ trình Autonomous Coordination (CTV2-086..105)

> Đọc file này là đủ để tiếp tục ở session khác. Nguồn gốc:
> `control-tower-v2/docs/research/autonomous-coordination-gap-analysis.md`.

## 1. Mục tiêu

Cho coordinator tự chạy hết vòng đời task từ chat global, giảm token và tăng chất
lượng. Doc nghiên cứu đã verify 12/13 claim; phiên này phân rã lộ trình thành task
và chạy wave 1.

## 2. Trạng thái task (chốt lúc bàn giao)

| Task | Status | Executor | Reviewer | result_ref | Rejections |
|:---|:---|:---|:---|:---|:---|
| CTV2-086 AgentRun.kind + agent_role | todo | @claude-sonnet-medium | — | — | 0 |
| CTV2-087 request_review + Review Run | todo | @claude-sonnet-medium | — | — | 0 |
| **CTV2-088 idempotency** | **done** | @claude-sonnet-high | @claude-opus | `da3ba47` | 2 |
| CTV2-089 Orchestration Driver | todo | @claude-sonnet-medium | — | — | 0 |
| CTV2-090 research tools (graph/MCP) | todo | @gpt-5.6-luna | — | — | 0 |
| CTV2-091 Spec/Plan step | todo | @claude-sonnet-medium | — | — | 0 |
| CTV2-092 create_task scope + ID | todo | @claude-sonnet-medium | — | — | 0 |
| CTV2-093 autonomy policy | todo | @gpt-5.6-luna | — | — | 0 |
| CTV2-094 task_dependencies DAG | todo | @claude-sonnet-medium | — | — | 0 |
| **CTV2-095 context/token** | **done** | @claude-sonnet-high | @claude-opus | `be276d4` | 2 |
| CTV2-096 LLM compaction | todo | @gpt-5.6-luna | — | — | 0 |
| CTV2-097 sub-session per task | todo | @gpt-5.6-luna | — | — | 0 |
| CTV2-098 gate notification | todo | @gpt-5.6-luna | — | — | 0 |
| CTV2-099 result_ref accuracy | todo | @gpt-5.6-luna | — | — | 0 |
| CTV2-100 bỏ LangGraph | todo | @gpt-5.6-luna | — | — | 0 |
| CTV2-101 tool-iteration budget | todo | @gemini-3.6-flash | — | — | 0 |
| **CTV2-102 review result schema** | **done** | @gpt-5.6-luna | @claude-opus | `0bb2834` | 0 |
| CTV2-103 kill switch + budget | todo | @gpt-5.6-luna | — | — | 0 |
| CTV2-104 compact_context orphan | todo | — | — | — | 0 |
| CTV2-105 git worktree per dispatch | todo | — | — | — | 0 |

**Không còn process nào đang chạy.** Wave 1 kết thúc: **3/3 task đã `done`**
(CTV2-088 `da3ba47`, CTV2-095 `be276d4`, CTV2-102 `0bb2834`). CTV2-092, 099, 101,
103 thuộc wave 1 mở rộng nhưng **chưa dispatch**.

## 3. Thứ tự phụ thuộc (đã sửa 3 lỗi so với bản đầu)

```
088 ✔ ──► 086 ──┐
099 ─────────────┼──► 087 ──┐
102 ✔ ───────────┘          │
090 ──► 091 ────────────────┼──► 089 ──► 093, 094, 097, 098
103 ────────────────────────┘
095 ✔ ──► 096, 097
092, 100, 101, 104, 105 : nhánh độc lập
```

Ba sửa quan trọng, **đừng đảo lại**:
1. **088 trước 086/087** — 087 tạo review run đi qua đúng `_request_gate` từng
   hỏng; làm trước sẽ viết test trên nền hành vi sai.
2. **099 là prerequisite của 087** — review run cần cặp `base..head` do 099 sinh.
   Chạy 087 trước ⇒ review diff rỗng ⇒ verdict pass giả ngay lần tự chủ đầu tiên.
3. **089 sau 091 và 103** — driver không được bật khi chưa có Spec/Plan thật và
   chưa có phanh. 089 đã có AC fail-closed: task thiếu AC thì dừng, không dispatch.

## 4. Quyết định của user trong phiên

| Chủ đề | Quyết định |
|:---|:---|
| LangGraph | **Phương án (a)** — gỡ khỏi runtime. Đã ghi vào đầu CTV2-100 |
| Worktree | **Duyệt** — đã tạo **CTV2-105** |
| `agy` flag | **`agy --model`** (không phải `--agent`); guide đã sửa |
| Phân vai model | research → `@claude-opus` (4.5); review → `@claude-opus-5-medium`; code → `@gpt-5.6-luna`; task khó → `@claude-sonnet-medium`; rất khó → `@claude-sonnet-high` |
| Reviewer hiện tại | Đổi **hết** sang `@claude-opus` |
| Process đang chạy sai config | **Không kill** — để chạy xong, sửa tiến lên phía trước |

## 5. Ba việc tồn đọng (mục 3/4/5 đã gộp)

### 5.1. `ct-dispatch.py` đồng bộ reviewer vào review sheet — ĐÃ SỬA, CHƯA VERIFY E2E

`--role review` trước đây chỉ cập nhật `reviewer:` trong task file, không cập nhật
frontmatter review sheet. Reviewer agent đọc sheet để biết mình là ai, nên nó **ký
báo cáo bằng tên reviewer cũ** — nếu ghi verdict theo tên đó thì stats cộng cho
agent không hề review và four-eyes thành hình thức. Đã xảy ra thật ở CTV2-102.

Đã sửa: nhánh review nay ghi cả hai file trong **một transaction**. Nhưng **chưa
verify end-to-end** — hai lần thử test đều vô hiệu (lần 1 phép thay thế không khớp
vì frontmatter có nháy kép; lần 2 CTV2-102 đã `done` nên script từ chối đúng).
**Việc cần làm:** verify ở lần đổi reviewer thật tiếp theo, hoặc dựng task/sheet
throwaway để test.

### 5.2. Bug `compact_context` orphan — ĐÃ TÁCH THÀNH CTV2-104 ✔

Reviewer CTV2-095 vòng 2 chứng minh: slice `compact_context` sinh orphan (assistant
mang `tool_calls` không có `tool` message tương ứng) ở **cả `eb9a8a1` lẫn
`61878d4^`** — tức **tiền tồn**, có trước khi CTV2-095 bắt đầu. Khiếm khuyết vòng 1
của CTV2-095 đã vô tình *che* nó; vòng 2 sửa đúng thì nó lộ ra và baseline tool quy
nhầm cho bản sửa.

**ĐÃ XỬ LÝ:** tách thành **CTV2-104** ngay trước khi đóng CTV2-095, đúng như cảnh
báo trong chính mục này. Task đã có AC yêu cầu tái hiện lỗi trên `61878d4^` để xác
nhận là tiền tồn, và yêu cầu test phải đỏ khi revert.

### 5.3. Chưa chạy LLM-Modulo verifier trên CTV2-086..105 — **CHƯA LÀM, ưu tiên cao nhất**

`task-creation.md` bước 11 bắt buộc chạy verifier trước Spec Gate. Tôi bỏ qua.
`.claude/verifier-rules.yaml` có sẵn rule `no-conflicting-tasks` — chạy nó là phát
hiện chồng lấn file của wave 1 ngay ở Spec Gate thay vì lúc sắp spawn.

**Việc cần làm:** chạy verifier trên **15 task còn `todo`**, đặc biệt hai rule:
- `no-conflicting-tasks` — chồng lấn `files:`
- `ac-tests-name-data-and-assertion` *(rule mới thêm trong phiên)* — nhiều khả năng
  còn AC lỏng kiểu CTV2-095 chưa lộ.

## 6. Ràng buộc vận hành đã học được (quan trọng nhất)

1. **Một working tree ⇒ mọi thứ phải tuần tự.** Wave 1 lẽ ra chạy song song nhưng
   không thể: hai executor commit đồng thời sẽ đua `.git/index.lock`; executor commit
   trong lúc reviewer chạy test sẽ làm HEAD dịch chuyển giữa lượt review. Ràng buộc
   này đã chặn 4 lần trong một phiên. CTV2-105 sinh ra để gỡ.
2. **Chồng lấn file phải kiểm TRƯỚC khi dispatch.** Mọi task wave 1 đều đụng file với
   ít nhất một task khác, dù `depends_on` đều rỗng. Batch độc lập đã dùng:
   A = {088, 095, 102}, B = {092, 099, 101}, C = {103}.
3. **Executor không tự commit nếu prompt không bảo.** 3/3 executor batch A hoàn thành,
   test xanh, không ai commit — `git log` đứng yên. Đã vá
   `ct-dispatch.py::build_prompt` để yêu cầu commit + in `RESULT_REF: <hash>`.
4. **`effort:` trong agent profile vô nghĩa nếu lệnh spawn không truyền.** Đã sửa cả
   nhánh claude lẫn agy trong `ct-dispatch.py` (`--effort` + `< /dev/null`).

## 7. Ba pattern mới đúc kết trong phiên

Đều ở `knowledge/patterns/`, đã index:

| Pattern | Nội dung một câu |
|:---|:---|
| [[vacuous-acceptance-test]] | AC nêu tên test mà không nêu **dữ liệu** và **khẳng định** ⇒ executor viết test xanh trên dữ liệu suy biến, không thể fail. Dấu hiệu chắc nhất: revert code, xem test có đỏ không |
| [[fixture-dependent-metric]] | Con số đo trên một fixture không phải hằng số hệ thống. Tách *chiều* (bất biến, vào AC) khỏi *độ lớn* (quan sát, báo cáo kèm fixture) |
| [[tool-finding-misattribution]] | Finding của tool phải tái hiện được và đối chứng ở `<ref>^` trước khi tính vào commit. Bug tiền tồn có thể bị quy cho bản sửa đúng |

Đã nối enforcement: rule `ac-tests-name-data-and-assertion` trong
`.claude/verifier-rules.yaml`, và một Rule mới trong `AGENTS.md` §2.

## 8. Nhận xét chất lượng

- **2/3 task wave 1 bị bác vòng đầu**, và **cả hai lần lỗi thật đều là test chạy ở
  nhánh không có bug** — không phải code sai hiển nhiên. Đây là dạng lỗi mà review
  hời hợt không bắt được.
- CTV2-088 mất **3 vòng, 2 executor, 2 reviewer**. Nguyên nhân gốc: AC2 do
  control-tower viết đã quy định *cách sắp xếp dòng lệnh* thay vì *bất biến*, và
  reviewer vòng 2 phán xử là không implement được ⇒ phải viết lại AC.
- Một lượt review của CTV2-102 **bị bác** vì bỏ qua tool `required: hard` (`ocr`,
  `ruff` đều có sẵn nhưng báo "not available") và tự ký sai danh tính. Verdict `pass`
  trên review đó sẽ đúng là fake-done mà cả lộ trình này sinh ra để chặn.
- Prediction accuracy: 81% → 80% → **82% (59/72)**.
- `@coordinator` đã tự ghi **8 lỗi điều phối** (3 do user phát hiện trước) vào
  `knowledge/agents/@coordinator.md`, trend `declining`.

## 9. Việc tiếp theo, theo thứ tự

1. Đọc kết quả review CTV2-095 vòng 3 (`be276d4`) → `/verdict`.
2. **Trước khi đóng CTV2-095**: tách NB-4 thành CTV2-104 (§5.2).
3. Tạo CTV2-105 — git worktree per dispatch (§6.1). Nên làm sớm vì nó gỡ ràng buộc
   tuần tự cho mọi task còn lại.
4. Chạy verifier trên 13 task `todo` (§5.3), sửa AC lỏng phát hiện được.
5. Dispatch tiếp theo batch: `099` → `092` → `101` (101 phải sau 095 vì cùng chạm
   `coordinator.py`).
6. Đường găng tới autonomy: `086` → `087` → (`090` → `091`) + `103` → `089`.
