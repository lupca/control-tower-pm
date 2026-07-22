---
id: WMS-001
task_path: projects/topvnsport-wms/tasks/WMS-001.md
project: topvnsport-wms
result_ref: git diff
executor: @antigravity
reviewer: null
status: pending
issued: 2026-07-21
verdict: null
verdict_date: null
---

# Phiếu Review: WMS-001 — Nâng cấp DataTable: thêm cột STT và pagination cho toàn bộ WMS

- **Dự án:** topvnsport-wms (`/home/lupca/projects/topvnsport`)
- **Task gốc:** `projects/topvnsport-wms/tasks/WMS-001-table-stt-pagination.md`
- **Result-ref:** local (uncommitted) — xem `git diff` trong repo
- **Executor:** @antigravity
- **Ngày phát phiếu:** 2026-07-21

---

## Files đã thay đổi
```
 M WMS/frontend/src/components/ui/DataTable.tsx
 M WMS/frontend/src/app/(desktop)/inventory/page.tsx
 M WMS/frontend/src/app/(desktop)/transactions/page.tsx
 M WMS/frontend/src/app/(desktop)/barcode-mappings/page.tsx
?? WMS/frontend/src/__tests__/components/DataTable.test.tsx  (new)
```

---

## Acceptance Criteria cần verify

- [ ] **AC1:** `DataTable.tsx` có prop `showRowNumber?: boolean` (default `true`), hiển thị cột STT đầu tiên
- [ ] **AC2:** STT tính đúng theo công thức: `(currentPage - 1) * limit + index + 1` (có pagination) hoặc `index + 1` (không có)
- [ ] **AC3:** Trang `inventory/page.tsx` có pagination hoạt động (dropdown số dòng, nút prev/next, hiển thị "Trang X/Y")
- [ ] **AC4:** Trang `transactions/page.tsx` có pagination hoạt động
- [ ] **AC5:** Trang `barcode-mappings/page.tsx` có pagination hoạt động
- [ ] **AC6:** Filter/Search reset về trang 1 khi thay đổi
- [ ] **AC7:** Test file `WMS/frontend/src/__tests__/components/DataTable.test.tsx` tồn tại và cover các case: render STT, pagination controls, page change

---

## Definition of Done (AGENTS.md mục 3)

- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: `WMS/frontend/src/__tests__/components/DataTable.test.tsx`
- [ ] Không regression (test khác trong WMS frontend vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @antigravity)

---

## Test gợi ý chạy trong repo code

```bash
# Chạy test DataTable mới
cd /home/lupca/projects/topvnsport
npm --prefix WMS/frontend test -- --run DataTable

# Chạy toàn bộ WMS frontend tests
npm --prefix WMS/frontend test -- --run

# Hoặc trong Docker (nếu có)
docker compose -f WMS/docker-compose.yml exec frontend npm test -- --run
```

---

## Luồng bị ảnh hưởng (từ code-review-graph)

| Flow | Entry point | Criticality |
|------|-------------|-------------|
| `InventoryPage` | inventory/page.tsx | 0.67 |
| `TransactionsPage` | transactions/page.tsx | 0.70 |
| `handleAdjustSubmit` | inventory/page.tsx | 0.71 |
| `handleTransferSubmit` | inventory/page.tsx | 0.71 |
| `handleSubmit` | barcode-mappings/page.tsx | 0.71 |
| `handleSync` | barcode-mappings/page.tsx | 0.68 |
| `handleScanSuccess` | barcode-mappings/page.tsx | 0.49 |

**Lưu ý:** Các flow này đều đi qua `DataTable` component — kiểm tra UI không bị vỡ layout sau khi thêm cột STT.

---

## Câu hỏi rủi ro

*(Không có câu hỏi rủi ro đặc thù từ graph cho các file WMS này — các câu hỏi high-priority đều liên quan đến PMI/OMS)*

**Kiểm tra thủ công gợi ý:**
1. Cột STT có render đúng width, alignment không?
2. Khi chuyển trang, STT có tiếp tục đúng (trang 2 bắt đầu từ 11 nếu limit=10)?
3. Empty state (0 rows) có handle đúng colSpan không?
4. Responsive trên mobile có bị vỡ không?

---

## Gợi ý công cụ

Repo code đích có thể có sẵn skill `/code-review` — khuyến khích dùng để đọc diff + chạy test một cách có cấu trúc.

Hoặc review thủ công:
```bash
cd /home/lupca/projects/topvnsport
git diff WMS/frontend/src/
```

---

## Trả kết quả

Sau khi review xong, báo lại cho control-tower bằng lệnh:

```
/verdict WMS-001 pass --reviewer @<tên bạn> --commit <hash sau khi commit>
```

hoặc nếu cần sửa:

```
/verdict WMS-001 changes --reviewer @<tên bạn> --notes "..."
```
