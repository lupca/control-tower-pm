---
id: CTV2-095
title: "Token: đưa snapshot xuống cuối prefix + prune tool result cũ khỏi replay"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@claude-sonnet-high"
reviewer: "@claude-opus"
result_ref: "be276d4"
depends_on: []
files:
  - backend/app/services/context_hierarchy.py
  - backend/app/services/coordinator.py
  - backend/app/graph/context.py
  - backend/app/core/config.py
  - backend/app/api/stats.py
flows: []
tests:
  - backend/tests/test_context_hierarchy.py
  - backend/tests/unit/test_context_snapshot.py
  - backend/tests/integration/test_chat_context.py
  - backend/tests/test_token_telemetry.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.7
  deductions:
    - "hub node: build_context_snapshot (39), CoordinatorService (43) (-0.2)"
    - "CTV2-078 đã chạm vùng này, rủi ro xung đột thấp (-0.1)"
created: 2026-07-27
updated: 2026-07-27
rejections: 2
---

# CTV2-095: Hai rò rỉ token lớn nhất — vị trí snapshot và tool result tích luỹ

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Nguồn: `docs/research/autonomous-coordination-gap-analysis.md` §2 (G9.1, G9.3), §3.6, lộ trình #6
> Nối tiếp CTV2-078 (đã tách snapshot khỏi Tier-1 nhưng vẫn đặt **trước** history)

Layout hiện tại `[global][project][snapshot][history]`: snapshot đổi mỗi lần có mutation nên **toàn bộ history phía sau rớt khỏi cached prefix** — history dài gấp nhiều lần snapshot nên đây là khoản re-bill lớn nhất. Song song, `_persist_tool_exchange` ghi mọi tool result JSON vào `session.messages` và `get_task_context` replay tất cả ở mọi turn.

## Tiêu chí nghiệm thu (AC)

- [x] Thứ tự mới: `[global][project][history][snapshot][user_msg]` — history append-only nằm trong prefix ổn định
- [x] Có test khẳng định prefix trước snapshot **không đổi** giữa hai turn khi chỉ có mutation task (không phụ thuộc mắt người đọc log)
- [x] Chỉ replay tool result đầy đủ của N turn gần nhất (N cấu hình được); cũ hơn thay bằng 1 dòng tóm tắt giữ được ID/kết quả then chốt
- [x] Không mất thông tin quyết định: ID task, verdict, ràng buộc vẫn còn sau khi prune
- [x] Đo được: telemetry ghi cached vs uncached token mỗi turn, có số liệu trước/sau trong phần review

## Verification

- `pytest backend/tests/test_context_hierarchy.py backend/tests/unit/test_context_snapshot.py backend/tests/integration/test_chat_context.py backend/tests/test_token_telemetry.py -v` → xanh
- Test: 2 turn liên tiếp có mutation → prefix hash trước snapshot giống hệt nhau
- Test: hội thoại 20 turn → prompt chỉ chứa tool result đầy đủ của N turn cuối

## Plan

1. Đổi thứ tự lắp context sang `[global][project][history][snapshot][user_msg]`; snapshot thành block cuối cùng trước message mới.
2. Test prefix ổn định: hash phần prompt trước snapshot ở 2 turn có mutation → phải giống hệt. Đây là test chống hồi quy chính, không dựa vào đọc log bằng mắt.
3. Tool-result pruning: `get_task_context` chỉ replay đầy đủ N turn gần nhất (N vào config); turn cũ hơn thay bằng 1 dòng tóm tắt giữ tool name + ID/kết quả then chốt. Dữ liệu gốc vẫn nằm trong DB, chỉ không vào prompt.
4. Telemetry: ghi cached/uncached token mỗi turn để so trước–sau; số liệu đưa vào review.
5. Tests theo AC + đo baseline trước khi sửa để có con số đối chiếu.

## Sub-tasks

- [ ] Đổi thứ tự block context + test prefix ổn định
- [ ] Tool-result pruning + dòng tóm tắt
- [ ] Telemetry cached/uncached
- [ ] Tests per AC

## Ghi chú vòng 2

Executor đổi từ `@gpt-5.6-luna` sang `@claude-sonnet-high` (chỉ định của user, 2026-07-27).
Lý do: lỗi vòng 1 là hiểu sai ràng buộc protocol (cặp assistant `tool_calls` ↔ `tool` message theo
`tool_call_id`) và viết test không kiểm chứng được điều gì — lỗi phán đoán, không phải lỗi ẩu.

**Siết AC2 cho vòng này:** test prefix-stability BẮT BUỘC chạy trên session có history THẬT
(>= 4 message, trong đó có ít nhất một cặp assistant `tool_calls` + `tool` result), và phải assert
`before[:snapshot_index] == after[:snapshot_index]` trên toàn bộ slice (hoặc so hash của slice đó),
không phải chỉ so vài phần tử đầu. Test dựng session với `messages=[]` KHÔNG được tính là đạt AC2 —
vòng 1 đã tick ô này bằng đúng cách đó và bị bác.

**Siết AC4:** giữ một summary cho mỗi tool MESSAGE (không phải mỗi `turn_id`), và mang theo
`tool_call_id` + `name` vào summary dict. Phải có test cho turn nhiều tool call.

**Siết AC5:** cần metric cached/uncached theo TỪNG TURN + assertion trong `test_token_telemetry.py`
+ số đo trước/sau ghi vào phần báo cáo. Chỉ sửa aggregate endpoint là chưa đạt.

**Bổ sung `files:`** cho `backend/app/core/config.py` và `backend/app/api/stats.py` — vòng 1 sửa hai
file này mà không khai báo.

## Findings từ reviewer — vòng 2 (eb9a8a1, @claude-opus-5-medium, 2026-07-27)

Verdict: **changes**. Cả 5 AC (bản đã siết) đều đạt và cả 4 finding blocking vòng 1 đều đã fix —
reviewer kiểm chứng bằng cách chạy lại test trên code vòng 1 để xác nhận test đỏ thật, không chỉ đọc diff.
Điểm chặn duy nhất là một regression mới, nằm ngoài trọng tâm token-pruning.

### BLOCKING
- [ ] **B-1** `by_turn` không giới hạn (`backend/app/api/stats.py:56-83,203`): `_usage_query` không có
      `limit` và `_turn_breakdown` phát một entry cho MỖI row `llm_usage`, trong khi mọi breakdown khác
      đều group nên bị chặn trên. `Dashboard.tsx:91` và `Tokens.tsx:26` đều gọi `/stats/tokens` không
      filter ⇒ mỗi lần mở dashboard kéo về toàn bộ ledger, payload tăng vô hạn theo thời gian. Thêm nữa
      `grep -rn "by_turn" frontend/src/` không ra kết quả — chưa có gì trong UI dùng field này.
      *Sửa:* chỉ phát `by_turn` khi có `session_id`/`task_id` filter (đúng ngữ nghĩa per-turn mà AC5 cần),
      hoặc cap cứng N row gần nhất. Test AC5 hiện tại đã gọi kèm `?session_id=` nên vẫn xanh sau khi sửa.

### NON-BLOCKING (không chặn verdict, nên xử lý)
- [ ] **NB-1** `TOOL_RESULT_REPLAY_TURNS = 0` tắt prune thay vì prune tất cả (`context_hierarchy.py:241`):
      `tool_turns[-0:]` trả về cả list. Đo thực tế N=0 trên session 20 turn → giữ nguyên 20 tool message
      đầy đủ (kỳ vọng 0). Guard `max(0, ...)` ở dòng 42 khiến giá trị âm cũng rơi vào đây.
- [ ] **NB-2** `turn_index` đếm row đã lọc, và gộp mọi row `session_id is None` thành một pseudo-session
      (`stats.py:66-70`) — cosmetic nhưng nhãn dễ gây hiểu nhầm.
- [ ] **NB-3** `budget_messages` vẫn đục lỗ prefix (`coordinator.py:400-406`) — đã ghi nhận vòng 1,
      executor giữ nguyên có khai báo. Nên tách task riêng: đây là đường tái tạo đúng lỗi 400 vừa sửa.
- [ ] **NB-4** `compact_context` cắt `raw_msgs[-10:]` giữa turn gây orphan tool message. Reviewer đã
      verify đây là **bug có sẵn, KHÔNG phải regression của commit này**: orphan xuất hiện ở cả
      `61878d4^` (trước task) lẫn `eb9a8a1`; vòng 1 chỉ vô tình che nó bằng đúng bug làm mất
      `tool_call_id`. Nên mở task riêng cho việc cắt theo ranh giới turn.

### Ghi chú số đo AC5
Số message trước/sau tái lập chính xác (82/82). Mức giảm prefix token tái lập được về chiều nhưng
không về trị tuyệt đối: executor báo 5072 → 2733 (−46%), reviewer đo trên fixture riêng được
4581 → 3075 (−32.9%). Độ lớn phụ thuộc kích thước payload tool result trong fixture, nên "−46%" là
một phép đo trên fixture cụ thể chứ không phải hằng số hệ thống.

## Findings từ reviewer — vòng 1 (61878d4) — ĐÃ FIX, đã verify ở vòng 2
- [x] REGRESSION BLOCKING: summary message của pruned turn (context_hierarchy.py:245-250) bỏ mất tool_call_id và name, OpenAIAdapter.render_messages hạ nó xuống role=user, nhưng assistant message phía trước vẫn mang tool_calls — OpenAI từ chối assistant có tool_calls mà không có tool response tương ứng, nên MỌI session vượt quá N tool turn sẽ fail 400
- [x] trước commit này tool_call_id luôn được giữ
- [x] Multi-tool turn mất kết quả, vi phạm AC4: summarized_turns chỉ phát MỘT summary cho mỗi turn_id nên turn có 2 tool call chỉ giữ result đầu tiên, task ID/verdict của call thứ hai biến mất — test mới chỉ dùng 1 tool call mỗi turn nên không phủ
- [x] sửa chung với finding A bằng cách giữ một summary cho mỗi tool MESSAGE và mang theo tool_call_id + name
- [x] AC2 test rỗng nghĩa: test_build_messages_prefix_stable_across_task_mutation dựng session với messages=[] nên chỉ assert before[0]==after[0] và before[1]==after[1], đúng bằng test đã có từ trước CTV2-078, không hề assert toàn bộ slice trước snapshot khi CÓ history — tức không kiểm chứng chính luận điểm của task
- [x] plan yêu cầu so hash, chưa có
- [x] AC5 chưa đạt: stats.py chỉ thêm uncached_tokens ở endpoint tổng hợp, không có metric cached/uncached theo từng turn, test_token_telemetry.py không được đụng tới và không có assertion uncached nào, không có số đo trước/sau ở commit lẫn review sheet
- [x] Non-blocking cần theo dõi: budget_messages ở coordinator.py:400-406 budget prefix theo thứ tự cũ-trước và SKIP entry quá khổ nhưng vẫn tiếp tục vòng lặp, có thể đục lỗ giữa history và bỏ rơi tool result trong khi giữ assistant tool_calls trỏ tới nó, cộng hưởng với finding A
- [x] Non-blocking: thứ tự thực tế là [global][project][history][snapshot][task_header][user_msg], task_header nằm SAU snapshot khác với AC1, chấp nhận được vì nó chứa task.status volatile nhưng phải nói rõ
- [x] config.py và stats.py đều nằm ngoài files: khai báo, cần bổ sung vào task

## Findings từ reviewer
- [ ] 5/5 AC PASS, cả 4 finding vòng 1 đã verify fixed bằng cách chạy lại test trên code cũ và thấy nó đỏ — không chỉ đọc diff
- [ ] BLOCKING B-1: by_turn trả một entry cho MỖI row llm_usage, không giới hạn (stats.py:56-83,203) — mọi breakdown khác đều được group nên bị chặn, riêng cái này là O(tổng số LLM call)
- [ ] Dashboard.tsx:91 và Tokens.tsx:26 đều gọi /stats/tokens KHÔNG filter nên mỗi lần load dashboard kéo về toàn bộ ledger, trong khi grep by_turn trong frontend/src không ra kết quả nào tức chưa có ai tiêu thụ field này
- [ ] đây là regression MỚI của commit này, nằm trên đúng endpoint vừa được nối vào UI
- [ ] fix vài dòng: gate theo session_id/task_id hoặc cap số lượng, test AC5 đã truyền ?session_id= nên vẫn xanh
- [ ] Non-blocking NB-1: N=0 không tắt pruning mà giữ TOÀN BỘ (tool_turns[-0:] trả cả list, đo được 20 tool message đầy đủ được giữ) — ngữ nghĩa ngược với kỳ vọng
- [ ] Non-blocking NB-2: turn_index đếm theo row đã filter
- [ ] Non-blocking NB-3: lỗ budget_messages prefix đã biết từ vòng 1
- [ ] NB-4 tách task riêng: baseline tool báo compact_context slice mới gây 400 ngược do summary giữ role=tool, reviewer test lại thấy orphan xuất hiện ở CẢ eb9a8a1 LẪN 61878d4^ tức có TRƯỚC khi task bắt đầu — bug tiền tồn mà vòng 1 vô tình che bằng chính khiếm khuyết bị bác, không tính vào commit này
