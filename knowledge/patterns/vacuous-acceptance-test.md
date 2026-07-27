---
pattern_id: vacuous-acceptance-test
category: process
severity: high
created: 2026-07-27
updated: 2026-07-27
---

# vacuous-acceptance-test

## Problem Signature

An Acceptance Criterion names a test (*"có test khẳng định X"*, *"test bằng hash prefix"*, *"có regression test"*) but **không nói test đó chạy trên dữ liệu nào và assert cái gì**. Executor viết một test đúng tên, đúng chỗ, chạy xanh — nhưng trên dữ liệu suy biến (list rỗng, một phần tử, không có state) nên **nó không thể fail kể cả khi tính chất cần chứng minh bị vi phạm**. Ô AC được tick hợp lệ trên giấy, reviewer thấy "test có, test xanh", và lỗ hổng đi thẳng vào `done`.

Đây **không phải** executor gian dối: AC được thoả đúng theo nghĩa đen. Lỗi nằm ở người viết AC.

## Detection

- AC chứa danh từ "test" nhưng không có mệnh đề *"trên <dữ liệu gì>"* và không có mệnh đề *"assert <cái gì>"*.
- Test mới chạy xanh **ngay cả khi revert phần code mà nó lẽ ra phải bảo vệ** — dấu hiệu chắc chắn nhất. Nếu không ai thử revert thì không ai biết.
- Fixture trong test dùng giá trị suy biến: `messages=[]`, danh sách 1 phần tử, mock trả về hằng số, không có cặp quan hệ nào để phá.
- Test chỉ assert vài phần tử đầu (`before[0] == after[0]`) trong khi tính chất cần chứng minh là về **toàn bộ** tập hợp.
- Test mới trùng nội dung với một test đã tồn tại từ trước task — tức nó không thêm sức phủ nào.

## Solution Template

Viết AC theo bộ ba **hành vi + dữ liệu + khẳng định**, không bao giờ chỉ có vế đầu:

| Thiếu | Đủ |
|:---|:---|
| "Có test khẳng định prefix ổn định" | "Test chạy trên session có ≥4 message, trong đó có ít nhất một cặp assistant `tool_calls` + `tool` result; assert `before[:snapshot_index] == after[:snapshot_index]` trên **toàn bộ** slice" |
| "Có regression test cho re-dispatch" | "Test dựng run ở trạng thái terminal `success`, không chỉ đường `queue-failure`; assert lần dispatch thứ hai tạo AgentRun **mới**" |
| "Có test cho pruning" | "Test dùng turn có **2 tool call**; assert cả hai `tool_call_id` còn trong output" |

Ba quy tắc bổ trợ:

1. **Nêu rõ cái gì KHÔNG được tính là đạt** khi đã có tiền lệ bị lách — ví dụ *"test dựng session với `messages=[]` không được tính đạt AC này"*. Một dòng cấm cụ thể chặn được cả lớp lách.
2. **Yêu cầu test đỏ trước** cho task sửa lỗi: executor phải chứng minh test fail trên code cũ rồi mới pass trên code mới. Test không bao giờ đỏ là test không chứng minh gì.
3. **Ràng dữ liệu vào đúng chỗ dễ vỡ**: nếu tính chất cần bảo vệ là về quan hệ (cặp, thứ tự, tham chiếu chéo) thì fixture bắt buộc phải chứa quan hệ đó, nếu không test chỉ đang xác nhận một trường hợp không có gì để hỏng.

## Past Instances

- [[CTV2-095-snapshot-last-tool-result-pruning]] (control-tower-v2, 2026-07-27) — AC2 viết *"có test khẳng định prefix trước snapshot không đổi giữa hai turn"*. Executor dựng session `messages=[]`, khiến `snapshot_index == 2` và test chỉ assert `before[0]==after[0]`, `before[1]==after[1]` — trùng đúng test đã có từ trước CTV2-078, không hề kiểm chứng luận điểm của task. Reviewer `@claude-opus-5-medium` bắt được, verdict `changes`. Vòng 2 siết AC theo template trên. Cùng commit còn hai AC nữa dính đúng dạng: test pruning chỉ dùng **1** tool call mỗi turn nên không lộ bug mất kết quả ở turn nhiều tool call (AC4), và AC5 không có test nào đụng `test_token_telemetry.py`.
