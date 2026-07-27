---
pattern_id: fixture-dependent-metric
category: process
severity: medium
created: 2026-07-27
updated: 2026-07-27
---

# fixture-dependent-metric

## Problem Signature

Một task tối ưu (token, latency, bộ nhớ, số query) báo cáo **một con số duy nhất** làm bằng chứng đạt AC — *"giảm 46%"*, *"nhanh gấp 3"*, *"từ 5072 xuống 2733"*. Con số đó đo trên **một fixture do chính executor dựng**. Nó được trích lại trong review sheet, log, báo cáo cho user, rồi dần được đối xử như **hằng số của hệ thống** — trong khi nó chỉ là một điểm đo trên một hình dạng dữ liệu cụ thể.

Hậu quả không phải là code sai. Hậu quả là **cam kết sai**: con số đi vào tài liệu và kỳ vọng, rồi khi production không đạt thì không ai biết là do fixture khác hay do hồi quy thật.

## Detection

- AC yêu cầu "có số đo trước/sau" nhưng không nói đo trên **hình dạng dữ liệu nào**.
- Báo cáo chỉ có một cặp số, không có khoảng, không nói kích thước/thành phần fixture.
- Người thứ hai đo lại trên fixture khác ra **cùng chiều nhưng khác độ lớn** — đây là lúc phát hiện, và thường là quá muộn vì con số đầu đã lan.
- Con số được viết vào phần "kết quả" mà không kèm câu điều kiện.

## Solution Template

1. **Tách hai loại khẳng định.** *Chiều* (giảm/tăng, không mất mát) là bất biến — phải đúng trên mọi fixture và đáng đưa vào AC. *Độ lớn* là quan sát trên một fixture — chỉ được báo cáo kèm mô tả fixture.
2. **AC viết theo bất biến, không theo con số**: thay *"giảm ≥40% token"* bằng *"prefix token giảm đơn điệu khi số turn tăng, và số message không đổi trước/sau"* — cái sau kiểm được, cái trước phụ thuộc dữ liệu.
3. **Bắt buộc mô tả fixture cạnh mọi con số**: bao nhiêu turn/row/message, thành phần ra sao. Không có mô tả thì con số vô nghĩa.
4. **Reviewer đo lại trên fixture của mình**, và ghi nhận nếu độ lớn lệch — không coi lệch là finding, nhưng phải chặn việc con số của executor được trích như hằng số.
5. Trong log/báo cáo, viết *"−46% trên fixture 20 turn của executor; −32.9% trên fixture của reviewer"* thay vì *"−46%"*.

## Past Instances

- [[CTV2-095-snapshot-last-tool-result-pruning]] (control-tower-v2, 2026-07-27) — executor báo prefix 5072 → 2733 token (−46%) trên session 20 turn. Reviewer `@claude-opus-5-medium` đo lại trên fixture riêng: 4581 → 3075 (−32.9%). Cùng chiều, khác độ lớn. Ngược lại, phần *không mất message* thì tái lập **chính xác** 82/82 — đúng là bất biến. Coordinator đã suýt trích −46% như cam kết trong báo cáo cho user trước khi reviewer đính chính. Bài học: đại lượng nào tái lập chính xác thì mới là bất biến, đại lượng nào chỉ đúng chiều thì là quan sát.
