---
id: WMS-001
title: "Nâng cấp DataTable: thêm cột STT và pagination cho toàn bộ WMS"
status: done
priority: high
risk: normal
deadline: 2026-07-28
executor: "@antigravity"
reviewer: "@claude"
result_ref: "f4a0971"
depends_on: []
files:
  - WMS/frontend/src/components/ui/DataTable.tsx
  - WMS/frontend/src/app/(desktop)/inventory/page.tsx
  - WMS/frontend/src/app/(desktop)/transactions/page.tsx
  - WMS/frontend/src/app/(desktop)/barcode-mappings/page.tsx
  - WMS/frontend/src/app/(desktop)/warehouses/page.tsx
  - WMS/frontend/src/app/(desktop)/inbound/page.tsx
flows: []
tests:
  - "WMS/frontend/src/__tests__/components/DataTable.test.tsx (cần tạo mới, tham khảo PMI)"
dispatched: 2026-07-21
in_review: 2026-07-21
created: 2026-07-21
updated: 2026-07-21
spec_approved: 2026-07-21
plan_approved: 2026-07-21
---

# WMS-001: Nâng cấp DataTable: thêm cột STT và pagination cho toàn bộ WMS

> Dự án: [[projects/topvnsport-wms/topvnsport-wms]]

## Bối cảnh
Hệ thống WMS đang dùng component `DataTable` chung nhưng:
1. **Thiếu cột STT** (số thứ tự) — người dùng khó đếm/tham chiếu dòng
2. **Chưa dùng pagination** — component có sẵn prop `pagination` nhưng các trang không truyền

PMI đã implement đầy đủ (client-side pagination), WMS cần làm tương tự để nhất quán.

## Tiêu chí nghiệm thu (AC)
- [x] **AC1:** `DataTable.tsx` có prop `showRowNumber?: boolean` (default `true`), hiển thị cột STT đầu tiên
- [x] **AC2:** STT tính đúng theo công thức: `(currentPage - 1) * limit + index + 1` (có pagination) hoặc `index + 1` (không có)
- [x] **AC3:** Trang `inventory/page.tsx` có pagination hoạt động (dropdown số dòng, nút prev/next, hiển thị "Trang X/Y")
- [x] **AC4:** Trang `transactions/page.tsx` có pagination hoạt động
- [x] **AC5:** Trang `barcode-mappings/page.tsx` có pagination hoạt động
- [x] **AC6:** Filter/Search reset về trang 1 khi thay đổi
- [x] **AC7:** Test file `WMS/frontend/src/__tests__/components/DataTable.test.tsx` tồn tại và cover các case: render STT, pagination controls, page change

## Plan

### Phase 1: Cập nhật DataTable component
**File:** `WMS/frontend/src/components/ui/DataTable.tsx`

1. Thêm prop trong interface `DataTableProps`:
   ```ts
   showRowNumber?: boolean;  // default: true
   ```

2. Thêm helper function tính STT:
   ```ts
   const getRowNumber = (idx: number) => {
     if (!pagination) return idx + 1;
     return (pagination.currentPage - 1) * pagination.limit + idx + 1;
   };
   ```

3. Trong `<thead>`, thêm cột STT đầu tiên (trước các columns khác):
   ```tsx
   {showRowNumber !== false && (
     <th className="px-4 py-4 font-semibold select-none w-12">STT</th>
   )}
   ```

4. Trong `<tbody>`, thêm cell STT đầu tiên mỗi row:
   ```tsx
   {showRowNumber !== false && (
     <td className="px-4 py-4 text-gray-500 text-center">{getRowNumber(idx)}</td>
   )}
   ```

5. Cập nhật `colSpan` trong empty state để +1 nếu có STT.

### Phase 2: Thêm pagination cho các trang

**Pattern chung** (copy từ PMI `categories/page.tsx`):

```tsx
// Import
import { APP_SETTINGS } from "@/config/settings";

// State (thêm vào đầu component)
const [currentPage, setCurrentPage] = useState(1);
const [limit, setLimit] = useState(APP_SETTINGS.pagination.defaultLimit);

// Tính toán (sau khi filter)
const totalItems = filteredData.length;
const totalPages = Math.ceil(totalItems / limit) || 1;
const paginatedData = filteredData.slice(
  (currentPage - 1) * limit,
  currentPage * limit
);

// Reset page khi filter thay đổi
useEffect(() => {
  setCurrentPage(1);
}, [searchQuery, /* other filters */]);

// Truyền vào DataTable
<DataTable
  data={paginatedData}  // thay filteredData
  pagination={{
    currentPage,
    totalPages,
    limit,
    totalItems,
    onPageChange: setCurrentPage,
    onLimitChange: (newLimit) => {
      setLimit(newLimit);
      setCurrentPage(1);
    }
  }}
/>
```

**2.1. `inventory/page.tsx`:**
- Biến filtered: `filteredInventory`
- Reset khi: `searchQuery`, `selectedWarehouseId`

**2.2. `transactions/page.tsx`:**
- Biến filtered: `filteredTransactions`
- Reset khi: `skuFilter`, `typeFilter`, `locationFilter`

**2.3. `barcode-mappings/page.tsx`:**
- Biến filtered: `filteredMappings`
- Reset khi: `searchQuery`

### Phase 3 (optional): Migrate warehouses locations table
- Hiện dùng HTML table thủ công (dòng 376-424)
- Có thể giữ nguyên vì là sub-table trong context khác

### Phase 4: Viết test
**File:** `WMS/frontend/src/__tests__/components/DataTable.test.tsx`

Copy từ `PMI/frontend/src/__tests__/components/DataTable.test.tsx`, thêm:
- Test render cột STT
- Test STT tính đúng khi có pagination (page 2, limit 10 → STT bắt đầu từ 11)
- Test pagination controls (prev/next, dropdown limit)

## Sub-tasks
- [x] **Phase 1:** Cập nhật `DataTable.tsx` — thêm prop `showRowNumber`, render cột STT
- [x] **Phase 2.1:** `inventory/page.tsx` — thêm state `currentPage`, `limit`, tính `paginatedData`, truyền `pagination` prop
- [x] **Phase 2.2:** `transactions/page.tsx` — tương tự Phase 2.1
- [x] **Phase 2.3:** `barcode-mappings/page.tsx` — tương tự Phase 2.1
- [ ] **Phase 3 (optional):** Migrate `warehouses/page.tsx` locations table sang DataTable (hiện dùng HTML table thủ công)
- [x] **Phase 4:** Viết test `DataTable.test.tsx` cho WMS (copy từ PMI + thêm case STT/pagination)

## References
- PMI DataTable: `PMI/frontend/src/components/ui/DataTable.tsx`
- PMI pagination usage: `PMI/frontend/src/app/catalog/categories/page.tsx` (dòng 124-137)
- PMI test: `PMI/frontend/src/__tests__/components/DataTable.test.tsx`
