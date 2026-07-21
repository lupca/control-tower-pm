---
type: research
scope: general
created: 2026-07-22
updated: 2026-07-22
tags: [pricing, discount, promotion, architecture, e-commerce]
related: []
---

# Nghien cuu Kien truc He thong Giam gia / Khuyen mai (Discount & Promotion)

## 1. Hien trang TopVNSport (chi tiet)

### 1.1. Frontend Web (web/)
- Co hien thi `salePrice`, badge "SALE", tinh `discountPercent`
- UI san sang: `ProductCard.tsx`, `ProductPurchaseSection.tsx`, `HomePage.tsx` ("XA KHO CUC HAN - GIAM GIA 30%")
- **Van de:** `salePrice` hien tai = `minPrice` (placeholder), chua co logic giam gia that

### 1.2. Backend PMI - Cau truc gia hien tai

```
Product
└── variants[]
    └── price                    # Gia goc (master price)
    └── channel_listings[]
        └── price_override       # Gia rieng per channel (NULL = ke thua master)
```

**Channels trong DB:** Dynamic (fetch tu `/api/channels`)
- `webstore` (default)
- `shopee_vn`
- `tiktok_shop`
- (co the them Lazada, Tiki...)

### 1.3. Van de UI/UX hien tai

**BUG: Channels hardcoded trong ProductForm**

```typescript
// ProductForm.tsx - line 49-52: HARDCODED!
channel_listings: [
  { channel_code: "shopee_vn", ... },
  { channel_code: "tiktok_shop", ... }
]

// ChannelConfig.tsx - line 48-51: HARDCODED type!
interface ChannelConfigProps {
  channelCode: "shopee_vn" | "tiktok_shop";  // <-- Union type fix cung
  channelName: string;
}

// ChannelConfigSection - line 154-157: HARDCODED tabs!
activeTab: "shopee" | "tiktok"
```

**Hau qua:**
- Them channel moi trong Settings → khong tu dong hien trong Product Form
- Phai sua code moi khi them channel moi
- Khong scale duoc

### 1.4. Flow hien tai (UX)

```
Product Form Sidebar:
├── 📦 Thong tin co ban (Basic)
├── 🔧 Thong so ky thuat (Specs)  
├── 🛒 Thong tin ban hang (Sales) ← Variants + Price
├── 🚚 Van chuyen (Logistics)
├── 📄 Khac (Other)
└── 🌐 Cau hinh da kenh (Channels) ← Hardcoded Shopee/TikTok tabs
```

**Channel Config cho phep:**
- Toggle "Niem yet tren [Channel]" (Published/Draft)
- Override: Title, Description
- Override: Gia per variant (price_override)
- Auto-map: Category → Channel Category
- Fill: Channel-specific attributes

## 2. Cac mo hinh kien truc pho bien

### Mo hinh A: Discount trong PIM (Don gian)
```
Product
├── price (gia goc)
├── sale_price (gia sau giam)
├── discount_percent
├── sale_start_date
└── sale_end_date
```
**Uu diem:** Don gian, it thay doi code
**Nhuoc diem:** Khong linh hoat, kho quan ly nhieu loai khuyen mai

### Mo hinh B: Promotion Service rieng (Trung binh)
```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│   Product   │────▶│ Promotion Engine │────▶│  Cart/Order │
│   Service   │     │   (rules-based)  │     │   Service   │
└─────────────┘     └──────────────────┘     └─────────────┘
```
**Uu diem:** Tach biet, linh hoat, marketing tu quan ly rules
**Nhuoc diem:** Phuc tap hon, can API moi

### Mo hinh C: Pricing Engine (Phuc tap - Enterprise)
```
┌─────────────┐     ┌─────────────────┐     ┌──────────────┐
│   Catalog   │     │  Pricing Engine │     │   Analytics  │
└──────┬──────┘     └────────┬────────┘     └──────┬───────┘
       │                     │                     │
       └─────────────────────┼─────────────────────┘
                             ▼
                    ┌─────────────────┐
                    │ Dynamic Pricing │
                    │ (ML-powered)    │
                    └─────────────────┘
```
**Uu diem:** Toi uu loi nhuan, ca nhan hoa
**Nhuoc diem:** Qua phuc tap cho quy mo nho

## 3. Kien truc doi thu / Open-source

### Shopify
- Built-in discount codes, automatic discounts
- Discount types: percentage, fixed amount, buy X get Y, free shipping
- Tiered discounts (mua nhieu giam nhieu)
- Scheduled promotions

### Magento/Adobe Commerce
- Cart Price Rules (ap dung khi checkout)
- Catalog Price Rules (ap dung tren listing)
- Coupon management
- Customer segment targeting

### Medusa (Open-source, recommend tham khao)
- **Promotion Module** rieng biet
- Cau truc: Campaign → Promotion → Rules → Actions
- Rules: dieu kien ap dung (customer group, region, currency, sales channel)
- Actions: `addItemAdjustment`, `addShippingMethodAdjustment`
- Ho tro: bundled discounts, buy-get, spend-get, temporary campaigns

### WooCommerce
- Plugin-based: Smart Coupons, Dynamic Pricing
- Flexible nhung phu thuoc ecosystem

## 4. Cac loai Discount can ho tro

| Loai | Mo ta | Do uu tien |
|------|-------|------------|
| **Percentage off** | Giam X% | Cao |
| **Fixed amount off** | Giam X dong | Cao |
| **Sale price** | Gia co dinh trong thoi gian | Cao |
| **Buy X Get Y** | Mua 2 tang 1 | Trung binh |
| **Tiered/Volume** | Mua nhieu giam nhieu | Trung binh |
| **Bundle discount** | Combo san pham | Thap |
| **Free shipping** | Mien phi van chuyen | Thap |
| **Coupon code** | Ma giam gia | Trung binh |

## 5. De xuat cho TopVNSport (chi tiet)

### 5.1. Phan loai van de can giai quyet

| # | Van de | Muc do | Giai phap |
|---|--------|--------|-----------|
| 1 | Channels hardcoded trong ProductForm | **Bug** | Refactor thanh dynamic |
| 2 | Chua co Promotion/Discount | Feature | Them Promotion module |
| 3 | UX phuc tap khi co nhieu channel | UX | Redesign Channel Config |
| 4 | Chuan bi cho AI-Agent quan ly | Future | Schema AI-friendly |

### 5.2. Giai doan 1: Fix Channel Hardcode (uu tien cao)

**Truoc:**
```typescript
// HARDCODED
channel_listings: [
  { channel_code: "shopee_vn", ... },
  { channel_code: "tiktok_shop", ... }
]
```

**Sau:**
```typescript
// DYNAMIC - fetch tu API
const { data: channels } = useSWR('/api/channels');
const defaultChannelListings = channels?.map(ch => ({
  channel_code: ch.code,
  channel_id: ch.id,
  status: "Draft",
  ...
})) || [];
```

**File can sua:**
- `ProductForm.tsx`: `getDefaultValues()`, `ChannelConfigSection`
- `ChannelConfig.tsx`: Bo union type, nhan `channelCode: string`
- `useProductLoad.ts`: Merge channels tu API voi existing listings

### 5.3. Giai doan 2: Them Promotion Module (sau khi fix channels)

**Option A: Sale Price per Variant (Don gian nhat)**

Them vao `VariantChannelListing`:
```sql
ALTER TABLE variant_channel_listings ADD COLUMN sale_price DECIMAL(12,2);
ALTER TABLE variant_channel_listings ADD COLUMN sale_start TIMESTAMP;
ALTER TABLE variant_channel_listings ADD COLUMN sale_end TIMESTAMP;
```

UI trong Channel Config:
```
Bảng giá riêng trên sàn
┌─────────────┬──────────┬───────────┬─────────────┬────────────────────┐
│ Biến thể    │ SKU      │ Giá gốc   │ Giá bán sàn │ Giảm giá (optional)│
├─────────────┼──────────┼───────────┼─────────────┼────────────────────┤
│ Đỏ / 4U     │ YX-AX99R │ 3,500,000 │ [3,200,000] │ [2,800,000] 📅     │
│ Xanh / 4U   │ YX-AX99B │ 3,500,000 │ [        ]  │ [        ]         │
└─────────────┴──────────┴───────────┴─────────────┴────────────────────┘
                           ↑ Master     ↑ Override    ↑ Sale + Date picker
```

**Option B: Promotion Table (Linh hoat hon)**

```sql
CREATE TABLE promotions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Scope
    channel_id INT REFERENCES channels(id),  -- NULL = all channels
    
    -- Type & Value
    discount_type VARCHAR(20) NOT NULL,  -- 'percentage' | 'fixed_amount' | 'fixed_price'
    discount_value DECIMAL(12,2) NOT NULL,
    
    -- Time
    start_at TIMESTAMP NOT NULL,
    end_at TIMESTAMP NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'draft',  -- draft | scheduled | active | ended
    
    -- Audit
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE promotion_variants (
    promotion_id INT REFERENCES promotions(id) ON DELETE CASCADE,
    variant_id INT REFERENCES product_variants(id) ON DELETE CASCADE,
    
    -- Cached computed price
    original_price DECIMAL(12,2),
    final_price DECIMAL(12,2),
    
    PRIMARY KEY (promotion_id, variant_id)
);
```

### 5.4. Giai doan 3: UX Optimization

**Hien tai (phuc tap):**
```
Product Form → Scroll xuong → Channel Config → Tab Shopee → Fill
                                            → Tab TikTok → Fill (lap lai)
```

**De xuat: Channel-first hoac Bulk Edit**

**Option 1: Channel Summary Card**
```
┌─ Cấu hình kênh bán ──────────────────────────────────────────────┐
│                                                                   │
│  [✓] Shopee VN        [✓] TikTok Shop      [ ] Lazada           │
│      12 variants           12 variants          Chưa cấu hình    │
│      3 có giá riêng        0 có giá riêng                        │
│      [Chỉnh sửa]           [Chỉnh sửa]         [Bật]             │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

**Option 2: Bulk Price Matrix**
```
┌─ Bảng giá tổng hợp ──────────────────────────────────────────────┐
│                                                                   │
│  Biến thể     │ Master    │ Shopee    │ TikTok    │ Lazada      │
│  ─────────────┼───────────┼───────────┼───────────┼─────────────│
│  Đỏ / 4U      │ 3,500,000 │ 3,200,000 │ 3,500,000 │ -           │
│  Xanh / 4U    │ 3,500,000 │ 3,500,000 │ 3,500,000 │ -           │
│  ─────────────┼───────────┼───────────┼───────────┼─────────────│
│  [Áp dụng tất cả: _______ ] [Theo %: ___ %]                      │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

**Option 3: Promotion Wizard (cho marketing team)**
```
Bước 1: Chọn sản phẩm → Bước 2: Chọn kênh → Bước 3: Đặt giảm giá → Bước 4: Đặt lịch
```

## 6. Cau hoi can tra loi truoc khi implement

1. **Ai quan ly khuyen mai?** Marketing hay Admin?
2. **Khuyen mai theo product hay variant?** (VD: chi giam mau do?)
3. **Co can coupon code?** Hay chi auto-apply?
4. **Co can theo customer segment?** (VIP, khach moi, etc.)
5. **Hien thi o dau?** Listing, detail, cart, hay tat ca?
6. **Stack khong trung nhau?** 1 san pham co the chiu nhieu khuyen mai?

## 7. Thiet ke cho AI-Agent quan ly (TUONG LAI - chua ap dung)

> **Luu y:** Phan nay la thiet ke cho tuong lai khi muon AI-Agent tu dong quan ly khuyen mai. Hien tai chua can implement ngay - uu tien fix channel hardcode va them Promotion module truoc.

### 7.1. Hien trang he thong

```
Channel (Shopee, Lazada, Tiki, Web)
    └── ProductChannelListing (product → channel)
            └── VariantChannelListing
                    └── price_override (gia goc per channel)
```

**Van de:** `price_override` la gia co dinh, khong phai discount. Can them Promotion layer.

### 7.2. De xuat: Promotion schema AI-friendly

```sql
-- Bang chinh: Promotion (chien dich khuyen mai)
CREATE TABLE promotions (
    id SERIAL PRIMARY KEY,
    
    -- Metadata (AI doc/ghi)
    name VARCHAR(255) NOT NULL,
    description TEXT,
    intent TEXT,  -- "Giam 20% tat ca vot Yonex tren Shopee thang 8"
    
    -- Loai & gia tri
    type VARCHAR(50) NOT NULL,  -- 'percentage' | 'fixed_amount' | 'fixed_price'
    value DECIMAL(12,2) NOT NULL,
    
    -- Thoi gian
    start_at TIMESTAMP NOT NULL,
    end_at TIMESTAMP NOT NULL,
    
    -- Trang thai
    status VARCHAR(20) DEFAULT 'draft',  -- draft | scheduled | active | paused | ended
    is_active BOOLEAN DEFAULT true,
    
    -- Audit
    created_by VARCHAR(100),  -- '@ai-agent' | '@admin-tung'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- AI reasoning (giai thich tai sao tao promotion nay)
    ai_reasoning JSONB
);

-- Dieu kien ap dung (rules)
CREATE TABLE promotion_rules (
    id SERIAL PRIMARY KEY,
    promotion_id INT REFERENCES promotions(id) ON DELETE CASCADE,
    
    -- Rule type
    rule_type VARCHAR(50) NOT NULL,  
    -- 'channel' | 'category' | 'brand' | 'product' | 'variant' | 'min_qty' | 'min_value'
    
    -- Operator & value
    operator VARCHAR(20) NOT NULL,  -- 'in' | 'not_in' | 'eq' | 'gte' | 'lte'
    value JSONB NOT NULL,  -- [1,2,3] for IDs, "Yonex" for brand, 100000 for min_value
    
    INDEX idx_promo_rules_promo (promotion_id)
);

-- San pham/variant bi anh huong (de-normalized for performance)
CREATE TABLE promotion_applied_items (
    id SERIAL PRIMARY KEY,
    promotion_id INT REFERENCES promotions(id) ON DELETE CASCADE,
    
    -- Target
    product_id INT REFERENCES products(id) ON DELETE CASCADE,
    variant_id INT REFERENCES product_variants(id) ON DELETE CASCADE,
    channel_id INT REFERENCES channels(id) ON DELETE CASCADE,  -- NULL = all channels
    
    -- Gia tinh san (cached)
    original_price DECIMAL(12,2),
    discounted_price DECIMAL(12,2),
    discount_amount DECIMAL(12,2),
    
    -- Unique constraint
    UNIQUE(promotion_id, variant_id, channel_id)
);
```

### 7.3. Cach AI-Agent tuong tac

**Input (natural language):**
```
"Giam 20% tat ca vot Yonex tren Shopee tu 1/8 den 15/8"
```

**AI phan tich va tao Promotion:**
```json
{
  "name": "Yonex Shopee Aug Sale",
  "intent": "Giam 20% tat ca vot Yonex tren Shopee tu 1/8 den 15/8",
  "type": "percentage",
  "value": 20,
  "start_at": "2026-08-01T00:00:00",
  "end_at": "2026-08-15T23:59:59",
  "status": "scheduled",
  "created_by": "@ai-agent",
  "ai_reasoning": {
    "extracted_brand": "Yonex",
    "extracted_channel": "Shopee",
    "extracted_discount": "20%",
    "confidence": 0.95
  }
}
```

**Rules:**
```json
[
  {"rule_type": "channel", "operator": "eq", "value": 2},
  {"rule_type": "brand", "operator": "eq", "value": "Yonex"},
  {"rule_type": "category", "operator": "in", "value": [1, 5]}  // Vot cau long
]
```

### 7.4. API Endpoints cho AI-Agent

```
POST   /api/promotions              -- Tao promotion moi
GET    /api/promotions              -- List tat ca promotions
GET    /api/promotions/{id}         -- Chi tiet 1 promotion
PATCH  /api/promotions/{id}         -- Cap nhat (pause, extend, etc.)
DELETE /api/promotions/{id}         -- Xoa (soft delete)

POST   /api/promotions/{id}/preview -- Preview san pham bi anh huong truoc khi activate
POST   /api/promotions/{id}/apply   -- Apply & tinh toan gia cho tat ca items

GET    /api/products/{id}/promotions       -- Xem promotions dang ap dung cho product
GET    /api/channels/{id}/promotions       -- Xem promotions theo channel
```

### 7.5. Uu tien & Stack rules

Khi nhieu promotion cung ap dung:
1. **Khong stack (don gian):** Chi lay promotion co `discount_amount` cao nhat
2. **Stack co gioi han (trung binh):** Stack toi da 2 promotions, cap tren `max_discount_percent`
3. **Full stack (phuc tap):** Tinh theo thu tu uu tien, co `is_stackable` flag

**De xuat:** Bat dau voi option 1 (khong stack), sau do nang cap neu can.

### 7.6. Sync voi san thuong mai dien tu

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  PMI/Promo  │────▶│  Sync Service    │────▶│ Shopee/Lazada   │
│  (source)   │     │  (transform)     │     │ Promotion API   │
└─────────────┘     └──────────────────┘     └─────────────────┘
```

- PMI la **source of truth** cho promotion rules
- Sync service chuyen doi sang format cua tung san
- Co the 2-way sync: import Flash Sale tu san ve PMI

### 7.7. Dashboard cho AI monitoring

AI-Agent can biet:
- Promotion nao dang active
- Bao nhieu san pham dang bi giam gia
- Doanh thu/margin bi anh huong (estimate)
- Conflict detection (2 promotions cung target)

```sql
-- View cho AI query
CREATE VIEW v_active_promotions AS
SELECT 
    p.id, p.name, p.type, p.value,
    p.start_at, p.end_at,
    COUNT(DISTINCT pai.product_id) as affected_products,
    COUNT(DISTINCT pai.variant_id) as affected_variants,
    SUM(pai.discount_amount) as total_discount_value
FROM promotions p
LEFT JOIN promotion_applied_items pai ON p.id = pai.promotion_id
WHERE p.status = 'active' AND p.is_active = true
GROUP BY p.id;
```

## 8. THIET KE CHI TIET - PROMOTION MODULE (Hoan chinh)

> **Target:** Marketing team su dung, AI-agent quan ly trong tuong lai.
> **Scope:** Chi web (topvnsport.vn), khong anh huong san TMDT.

### 8.1. Database Schema

```sql
-- =====================================================
-- PROMOTION MODULE - Complete Schema
-- =====================================================

-- 1. Bang chinh: Promotions (chien dich khuyen mai)
CREATE TABLE promotions (
    id SERIAL PRIMARY KEY,
    
    -- === Thong tin co ban ===
    code VARCHAR(50) UNIQUE NOT NULL,           -- Ma KM: "SUMMER2026", "YONEX30"
    name VARCHAR(255) NOT NULL,                 -- "Giam 30% Vot Yonex"
    description TEXT,
    
    -- === AI-Agent fields ===
    intent TEXT,                                -- Cau goc: "Giam 30% tat ca vot Yonex thang 8"
    ai_reasoning JSONB,                         -- {"confidence": 0.95, "extracted_brand": "Yonex"}
    
    -- === Loai giam gia ===
    discount_type VARCHAR(20) NOT NULL,         -- 'percentage' | 'fixed_amount' | 'fixed_price'
    discount_value DECIMAL(12,2) NOT NULL,      -- 30 (cho %), 100000 (cho VND), 2500000 (fixed_price)
    
    -- === Dieu kien ap dung (optional, JSON rules) ===
    conditions JSONB DEFAULT '{}',              
    -- VD: {"min_order_value": 500000, "max_discount": 200000, "usage_limit": 100}
    
    -- === Thoi gian ===
    start_at TIMESTAMP NOT NULL,
    end_at TIMESTAMP NOT NULL,
    
    -- === Trang thai ===
    status VARCHAR(20) DEFAULT 'draft',         -- draft | scheduled | active | paused | ended
    priority INT DEFAULT 0,                     -- Uu tien khi nhieu promo cung target 1 SP
    is_stackable BOOLEAN DEFAULT false,         -- Co cho phep chong voi promo khac?
    
    -- === Audit ===
    created_by VARCHAR(100) NOT NULL,           -- '@marketing-mai' | '@ai-agent'
    updated_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- === Constraints ===
    CHECK (discount_type IN ('percentage', 'fixed_amount', 'fixed_price')),
    CHECK (status IN ('draft', 'scheduled', 'active', 'paused', 'ended')),
    CHECK (start_at < end_at),
    CHECK (discount_value >= 0)
);

-- Index cho query thuong dung
CREATE INDEX idx_promotions_status ON promotions(status);
CREATE INDEX idx_promotions_dates ON promotions(start_at, end_at);
CREATE INDEX idx_promotions_code ON promotions(code);

-- 2. Bang target: Promotion Scope (san pham nao duoc giam)
CREATE TABLE promotion_scope (
    id SERIAL PRIMARY KEY,
    promotion_id INT REFERENCES promotions(id) ON DELETE CASCADE,
    
    -- === Target type ===
    scope_type VARCHAR(20) NOT NULL,            -- 'all' | 'category' | 'brand' | 'product' | 'variant'
    scope_value JSONB NOT NULL,                 -- [1,2,3] for IDs, ["Yonex"] for brands
    
    -- === Exclude (optional) ===
    exclude_type VARCHAR(20),                   -- 'product' | 'variant' | 'category'
    exclude_value JSONB,                        -- [5,6] - exclude product IDs
    
    UNIQUE(promotion_id, scope_type, scope_value)
);

CREATE INDEX idx_promo_scope_promo ON promotion_scope(promotion_id);

-- 3. Bang cache: Computed prices (tinh san de query nhanh)
CREATE TABLE promotion_computed_prices (
    id SERIAL PRIMARY KEY,
    promotion_id INT REFERENCES promotions(id) ON DELETE CASCADE,
    variant_id INT NOT NULL,                    -- FK to product_variants
    
    -- === Gia ===
    original_price DECIMAL(12,2) NOT NULL,
    discount_amount DECIMAL(12,2) NOT NULL,
    final_price DECIMAL(12,2) NOT NULL,
    
    -- === Cache metadata ===
    computed_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(promotion_id, variant_id)
);

CREATE INDEX idx_computed_variant ON promotion_computed_prices(variant_id);
CREATE INDEX idx_computed_promo ON promotion_computed_prices(promotion_id);

-- 4. Bang log: Promotion usage history (cho analytics)
CREATE TABLE promotion_usage_log (
    id SERIAL PRIMARY KEY,
    promotion_id INT REFERENCES promotions(id),
    order_id VARCHAR(100),                      -- Ref to OMS order
    variant_id INT,
    quantity INT,
    discount_applied DECIMAL(12,2),
    used_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_usage_promo ON promotion_usage_log(promotion_id);
CREATE INDEX idx_usage_date ON promotion_usage_log(used_at);

-- 5. View: Active promotions voi computed stats
CREATE VIEW v_active_promotions AS
SELECT 
    p.id, p.code, p.name, p.discount_type, p.discount_value,
    p.start_at, p.end_at, p.status, p.priority,
    p.created_by, p.created_at,
    COUNT(DISTINCT cp.variant_id) as affected_variants,
    SUM(cp.discount_amount) as total_potential_discount
FROM promotions p
LEFT JOIN promotion_computed_prices cp ON p.id = cp.promotion_id
WHERE p.status IN ('active', 'scheduled')
  AND NOW() BETWEEN p.start_at AND p.end_at
GROUP BY p.id;
```

### 8.2. API Endpoints

```yaml
# === CRUD Promotions ===
POST   /api/promotions                    # Tao moi
GET    /api/promotions                    # List (filter: status, date range)
GET    /api/promotions/{id}               # Chi tiet
PATCH  /api/promotions/{id}               # Cap nhat
DELETE /api/promotions/{id}               # Xoa (soft delete → status='deleted')

# === Lifecycle ===
POST   /api/promotions/{id}/activate      # draft → active (hoac scheduled neu start_at > now)
POST   /api/promotions/{id}/pause         # active → paused
POST   /api/promotions/{id}/resume        # paused → active
POST   /api/promotions/{id}/end           # any → ended

# === Preview & Compute ===
POST   /api/promotions/{id}/preview       # Tra ve danh sach variants bi anh huong (truoc khi save)
POST   /api/promotions/{id}/compute       # Tinh va cache gia vao promotion_computed_prices

# === Query computed prices (cho Web Frontend) ===
GET    /api/products/{id}/computed-price  # Tra ve gia sau giam (neu co promo active)
GET    /api/variants/{id}/computed-price  # Tuong tu, per variant
GET    /api/computed-prices/bulk          # Bulk query: ?variant_ids=1,2,3,4,5

# === AI-Agent Interface ===
POST   /api/promotions/parse-intent       # Input: natural language → Output: structured promotion draft
# VD: "Giam 20% vot Yonex tu 1/8 den 15/8" → { discount_type: "percentage", discount_value: 20, ... }
```

### 8.3. Business Logic

**Quy tac tinh gia:**
```python
def compute_final_price(variant, active_promotions):
    original_price = variant.price  # Master price
    
    # Loc promotions ap dung cho variant nay
    applicable = [p for p in active_promotions if variant_in_scope(variant, p)]
    
    if not applicable:
        return original_price
    
    # Sap xep theo priority (cao truoc)
    applicable.sort(key=lambda p: -p.priority)
    
    # Mac dinh: chi ap dung 1 promo (highest priority)
    promo = applicable[0]
    
    if promo.discount_type == 'percentage':
        discount = original_price * promo.discount_value / 100
    elif promo.discount_type == 'fixed_amount':
        discount = promo.discount_value
    else:  # fixed_price
        discount = original_price - promo.discount_value
    
    # Apply max_discount constraint neu co
    max_discount = promo.conditions.get('max_discount')
    if max_discount and discount > max_discount:
        discount = max_discount
    
    final_price = original_price - discount
    return max(final_price, 0)  # Khong duoc am
```

**Auto-scheduler (Cron job):**
```python
# Chay moi phut
def update_promotion_statuses():
    now = datetime.now()
    
    # scheduled → active
    db.execute("""
        UPDATE promotions SET status = 'active', updated_at = NOW()
        WHERE status = 'scheduled' AND start_at <= %s
    """, [now])
    
    # active → ended
    db.execute("""
        UPDATE promotions SET status = 'ended', updated_at = NOW()
        WHERE status = 'active' AND end_at < %s
    """, [now])
```

### 8.4. UI/UX cho Marketing Team

**Menu moi trong PMI:**
```
📦 Catalog
🛒 Orders (link to OMS)
📊 Analytics
🏷️ Promotions  ← NEW
⚙️ Settings
```

**Promotion List Page:**
```
┌─ Quản lý Khuyến mãi ─────────────────────────────────────────────────────┐
│                                                                           │
│  [+ Tạo khuyến mãi mới]                    🔍 [Tìm kiếm...]  [Lọc ▾]    │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ 🟢 SUMMER2026        Giảm 30% Vợt Yonex           152 SP │ 01-15/08 │ │
│  │    Percentage: 30%   @marketing-mai               Đang chạy         │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ 🟡 NEWUSER50         Giảm 50k cho khách mới       All SP │ 01-31/08 │ │
│  │    Fixed: 50,000đ    @ai-agent                    Đã lên lịch       │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ ⚫ FLASHSALE01       Flash Sale cuối tuần          45 SP │ 20-21/07 │ │
│  │    Percentage: 40%   @marketing-mai               Đã kết thúc       │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│  ◀ 1 2 3 ▶                                                               │
└───────────────────────────────────────────────────────────────────────────┘
```

**Create/Edit Form (Wizard hoac Single Page):**
```
┌─ Tạo khuyến mãi mới ─────────────────────────────────────────────────────┐
│                                                                           │
│  Bước 1: Thông tin cơ bản                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ Mã KM:        [SUMMER2026        ]                                  │ │
│  │ Tên:          [Giảm 30% Vợt Yonex                                 ] │ │
│  │ Mô tả:        [Chương trình khuyến mãi hè 2026...                 ] │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│  Bước 2: Loại giảm giá                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  (•) Giảm theo %     ( ) Giảm số tiền     ( ) Giá cố định          │ │
│  │                                                                     │ │
│  │  Giá trị:  [30    ] %     Giảm tối đa: [200000   ] đ (optional)    │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│  Bước 3: Áp dụng cho                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  (•) Thương hiệu: [Yonex ▾]                                        │ │
│  │  ( ) Danh mục:    [        ]                                       │ │
│  │  ( ) Sản phẩm cụ thể: [Chọn sản phẩm...]                          │ │
│  │  ( ) Tất cả sản phẩm                                               │ │
│  │                                                                     │ │
│  │  Ngoại trừ: [+ Thêm sản phẩm loại trừ]                             │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│  Bước 4: Thời gian                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  Bắt đầu: [01/08/2026 00:00]     Kết thúc: [15/08/2026 23:59]     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│  ──────────────────────────────────────────────────────────────────────  │
│  Preview: 152 sản phẩm sẽ được giảm giá                [Xem chi tiết]   │
│  ──────────────────────────────────────────────────────────────────────  │
│                                                                           │
│                              [Hủy]  [Lưu nháp]  [Kích hoạt ngay]         │
└───────────────────────────────────────────────────────────────────────────┘
```

### 8.5. Tich hop voi Web Frontend

**Thay doi trong `productMappers.ts`:**
```typescript
// BEFORE: placeholder
salePrice: minPrice > 0 ? minPrice : undefined,

// AFTER: fetch tu API
async function getComputedPrice(variantId: number): Promise<number | null> {
  const res = await fetch(`/api/variants/${variantId}/computed-price`);
  if (!res.ok) return null;
  const data = await res.json();
  return data.has_promotion ? data.final_price : null;
}

// Hoac bulk fetch cho listing page
async function getComputedPrices(variantIds: number[]): Promise<Map<number, number>> {
  const res = await fetch(`/api/computed-prices/bulk?variant_ids=${variantIds.join(',')}`);
  // ...
}
```

**Response format:**
```json
{
  "variant_id": 123,
  "original_price": 3500000,
  "has_promotion": true,
  "promotion": {
    "code": "SUMMER2026",
    "name": "Giảm 30% Vợt Yonex",
    "discount_type": "percentage",
    "discount_value": 30
  },
  "discount_amount": 1050000,
  "final_price": 2450000
}
```

### 8.6. AI-Agent Interface (Tuong lai)

**Parse Intent API:**
```
POST /api/promotions/parse-intent
Content-Type: application/json

{
  "intent": "Giảm 20% tất cả vợt Yonex từ 1/8 đến 15/8, tối đa 500k"
}
```

**Response:**
```json
{
  "parsed": {
    "code": "YONEX20-AUG2026",
    "name": "Giảm 20% Vợt Yonex Tháng 8",
    "discount_type": "percentage",
    "discount_value": 20,
    "conditions": {
      "max_discount": 500000
    },
    "scope": {
      "scope_type": "brand",
      "scope_value": ["Yonex"]
    },
    "start_at": "2026-08-01T00:00:00",
    "end_at": "2026-08-15T23:59:59"
  },
  "confidence": 0.92,
  "preview": {
    "affected_variants": 152,
    "estimated_discount": 45600000
  },
  "clarifications": []
}
```

**Neu can lam ro:**
```json
{
  "parsed": null,
  "confidence": 0.45,
  "clarifications": [
    "Bạn muốn giảm cho 'Vợt cầu lông Yonex' hay 'Tất cả sản phẩm Yonex' (bao gồm cả giày, túi)?",
    "Giảm 20% là tính trên giá gốc hay giá đã có khuyến mãi khác?"
  ]
}
```

## 9. QUYET DINH THIET KE (DA CHOT)

| Cau hoi | Quyet dinh | Ly do |
|---------|------------|-------|
| Ai quan ly? | **Marketing team** (sau nay la AI-agent) | Tach biet voi Admin quan ly SP |
| Scope? | **Chi web (topvnsport.vn)** | San (Shopee/TikTok) co he thong giam gia rieng |
| Approach? | **Lam 1 phat hoan chinh** | AI-agent team code, can on dinh tu dau |
| Sale price o dau? | **Tach rieng Promotion module** | Khong mix vao variant/channel_listing |

### Kien truc tong quan

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PMI (Admin)                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│  │   Products   │  │   Variants   │  │   Channels   │                   │
│  │              │  │   (price)    │  │ (price_override)                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                   │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (read-only, khong sua)
┌─────────────────────────────────────────────────────────────────────────┐
│                      PROMOTION MODULE (Marketing)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│  │  Promotions  │  │   Promo      │  │  Computed    │                   │
│  │  (rules)     │──│   Variants   │──│  Prices API  │──▶ Web Frontend   │
│  └──────────────┘  └──────────────┘  └──────────────┘                   │
│                                                                          │
│  AI-Agent Interface: Natural language → Rules → Preview → Apply         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Web Frontend** goi API `/api/products/{id}/computed-price` de lay gia sau giam (neu co promotion active).
**San TMDT** van dung `price_override` nhu cu, khong bi anh huong.

### 9.2. Task Breakdown (cho AI-agent team)

```
PROMOTION MODULE - Implementation Checklist
============================================

Backend (PMI)
├── [ ] Database migrations (promotions, promotion_scope, promotion_computed_prices, promotion_usage_log)
├── [ ] Pydantic schemas (PromotionCreate, PromotionUpdate, PromotionResponse, ComputedPriceResponse)
├── [ ] CRUD API (/api/promotions)
├── [ ] Lifecycle API (activate, pause, resume, end)
├── [ ] Compute engine (tinh gia, cache vao bang)
├── [ ] Computed price API (/api/variants/{id}/computed-price, /api/computed-prices/bulk)
├── [ ] Auto-scheduler (cron: scheduled→active, active→ended)
├── [ ] Parse intent API (cho AI-agent tuong lai)
└── [ ] Tests

Frontend (PMI Admin - cho Marketing)
├── [ ] Menu item "Promotions"
├── [ ] Promotion List page (filter, search, status badges)
├── [ ] Promotion Create/Edit form (wizard)
├── [ ] Promotion Preview modal (xem SP bi anh huong)
├── [ ] Promotion Detail page (stats, usage log)
└── [ ] Tests

Frontend (Web - topvnsport.vn)
├── [ ] Hook/service goi computed-price API
├── [ ] Cap nhat productMappers.ts dung computed price
├── [ ] Hien thi "Gia goc" va "Gia khuyen mai" trong ProductCard
├── [ ] Badge/tag cho san pham dang giam gia
└── [ ] Tests

Testing (BAT BUOC - khong manual test)
├── Backend Unit Tests
│   ├── [ ] test_promotions_crud.py (create, read, update, delete)
│   ├── [ ] test_promotions_lifecycle.py (activate, pause, resume, end)
│   ├── [ ] test_promotions_compute.py (tinh gia cac loai discount)
│   ├── [ ] test_promotions_scope.py (filter by brand, category, product)
│   ├── [ ] test_promotions_priority.py (chon promo uu tien cao nhat)
│   ├── [ ] test_promotions_scheduler.py (scheduled→active, active→ended)
│   └── [ ] test_promotions_api.py (integration tests cho endpoints)
├── Frontend Unit Tests (PMI)
│   ├── [ ] PromotionList.test.tsx
│   ├── [ ] PromotionForm.test.tsx
│   ├── [ ] PromotionPreview.test.tsx
│   └── [ ] PromotionDetail.test.tsx
├── Frontend Unit Tests (Web)
│   ├── [ ] useComputedPrice.test.ts (hook)
│   ├── [ ] productMappers.test.ts (cap nhat test hien co)
│   └── [ ] ProductCard.test.tsx (hien thi gia giam)
├── E2E Tests
│   ├── [ ] test_promotion_full_flow.py (tao promo → activate → check web)
│   └── [ ] test_promotion_expiry.py (kiem tra auto-end)
└── CI/CD
    ├── [ ] Coverage check: backend >= 85%, frontend >= 80%
    └── [ ] Block merge neu tests fail

Bonus (Phase 2 - Optional)
├── [ ] Promotion Calendar view
├── [ ] Bulk import promotions (CSV)
├── [ ] Promotion analytics dashboard
└── [ ] AI-agent integration (parse intent → auto-create)
```

### 9.3. Ket noi voi he thong hien tai

| He thong | Anh huong | Thay doi |
|----------|-----------|----------|
| **PMI Backend** | Them module moi | Them tables, APIs, khong sua code cu |
| **PMI Frontend** | Them menu Promotions | Khong sua Product Form |
| **Web Frontend** | Goi computed-price API | Sua productMappers.ts |
| **WMS** | Khong anh huong | - |
| **OMS** | Luu promotion_id khi dat hang | Minor: log discount applied |
| **San TMDT** | Khong anh huong | Van dung price_override |

### 9.4. Bug can fix rieng (khong lien quan Promotion)

**BUG: Channel hardcode trong ProductForm** (da mo ta o muc 1.3)

Day la bug rieng, nen tao task rieng de fix:
- Refactor `ProductForm.tsx`, `ChannelConfig.tsx` thanh dynamic
- Fetch channels tu API thay vi hardcode
- Khong block Promotion module (2 viec doc lap)

Task ID: `WEB-001` (tao rieng)

## 10. TEST SPECS (Chi tiet)

> **Quy tac:** Khong manual test. Tat ca phai co automated test truoc khi merge.

### 10.1. Backend Unit Tests (pytest)

**File: `PMI/backend/tests/test_promotions_crud.py`**
```python
"""
Test CRUD operations for Promotions API
"""

class TestPromotionCreate:
    def test_create_percentage_promotion(self, client, db):
        """Tao promotion giam % thanh cong"""
        payload = {
            "code": "TEST20",
            "name": "Test 20%",
            "discount_type": "percentage",
            "discount_value": 20,
            "start_at": "2026-08-01T00:00:00",
            "end_at": "2026-08-15T23:59:59",
            "created_by": "@test"
        }
        res = client.post("/api/promotions", json=payload)
        assert res.status_code == 201
        assert res.json()["code"] == "TEST20"
        assert res.json()["status"] == "draft"
    
    def test_create_fixed_amount_promotion(self, client, db):
        """Tao promotion giam so tien co dinh"""
        payload = {
            "code": "MINUS50K",
            "name": "Giam 50k",
            "discount_type": "fixed_amount",
            "discount_value": 50000,
            "start_at": "2026-08-01T00:00:00",
            "end_at": "2026-08-15T23:59:59",
            "created_by": "@test"
        }
        res = client.post("/api/promotions", json=payload)
        assert res.status_code == 201
    
    def test_create_fixed_price_promotion(self, client, db):
        """Tao promotion gia co dinh"""
        payload = {
            "code": "FLAT2M",
            "name": "Dong gia 2 trieu",
            "discount_type": "fixed_price",
            "discount_value": 2000000,
            "start_at": "2026-08-01T00:00:00",
            "end_at": "2026-08-15T23:59:59",
            "created_by": "@test"
        }
        res = client.post("/api/promotions", json=payload)
        assert res.status_code == 201
    
    def test_create_promotion_duplicate_code_fails(self, client, db, existing_promotion):
        """Tao promotion trung code phai fail"""
        payload = {
            "code": existing_promotion.code,  # duplicate
            "name": "Another",
            "discount_type": "percentage",
            "discount_value": 10,
            "start_at": "2026-08-01T00:00:00",
            "end_at": "2026-08-15T23:59:59",
            "created_by": "@test"
        }
        res = client.post("/api/promotions", json=payload)
        assert res.status_code == 400
        assert "code" in res.json()["detail"].lower()
    
    def test_create_promotion_invalid_dates_fails(self, client, db):
        """start_at > end_at phai fail"""
        payload = {
            "code": "BADDATE",
            "name": "Invalid",
            "discount_type": "percentage",
            "discount_value": 10,
            "start_at": "2026-08-15T00:00:00",
            "end_at": "2026-08-01T00:00:00",  # truoc start!
            "created_by": "@test"
        }
        res = client.post("/api/promotions", json=payload)
        assert res.status_code == 422
    
    def test_create_promotion_negative_value_fails(self, client, db):
        """discount_value < 0 phai fail"""
        payload = {
            "code": "NEGATIVE",
            "name": "Invalid",
            "discount_type": "percentage",
            "discount_value": -10,
            "start_at": "2026-08-01T00:00:00",
            "end_at": "2026-08-15T00:00:00",
            "created_by": "@test"
        }
        res = client.post("/api/promotions", json=payload)
        assert res.status_code == 422
    
    def test_create_promotion_percentage_over_100_fails(self, client, db):
        """percentage > 100 phai fail"""
        payload = {
            "code": "OVER100",
            "name": "Invalid",
            "discount_type": "percentage",
            "discount_value": 150,
            "start_at": "2026-08-01T00:00:00",
            "end_at": "2026-08-15T00:00:00",
            "created_by": "@test"
        }
        res = client.post("/api/promotions", json=payload)
        assert res.status_code == 422


class TestPromotionRead:
    def test_list_promotions(self, client, db, multiple_promotions):
        """List tat ca promotions"""
        res = client.get("/api/promotions")
        assert res.status_code == 200
        assert len(res.json()) >= 3
    
    def test_list_promotions_filter_status(self, client, db, multiple_promotions):
        """Filter theo status"""
        res = client.get("/api/promotions?status=active")
        assert res.status_code == 200
        for p in res.json():
            assert p["status"] == "active"
    
    def test_get_promotion_by_id(self, client, db, existing_promotion):
        """Get 1 promotion theo ID"""
        res = client.get(f"/api/promotions/{existing_promotion.id}")
        assert res.status_code == 200
        assert res.json()["id"] == existing_promotion.id
    
    def test_get_promotion_not_found(self, client, db):
        """Get promotion khong ton tai"""
        res = client.get("/api/promotions/99999")
        assert res.status_code == 404


class TestPromotionUpdate:
    def test_update_promotion_name(self, client, db, existing_promotion):
        """Update ten promotion"""
        res = client.patch(
            f"/api/promotions/{existing_promotion.id}",
            json={"name": "Updated Name"}
        )
        assert res.status_code == 200
        assert res.json()["name"] == "Updated Name"
    
    def test_update_promotion_cannot_change_code(self, client, db, existing_promotion):
        """Khong cho phep doi code"""
        res = client.patch(
            f"/api/promotions/{existing_promotion.id}",
            json={"code": "NEWCODE"}
        )
        # Co the 400 hoac ignore field
        if res.status_code == 200:
            assert res.json()["code"] == existing_promotion.code  # unchanged


class TestPromotionDelete:
    def test_delete_promotion(self, client, db, existing_promotion):
        """Xoa promotion (soft delete)"""
        res = client.delete(f"/api/promotions/{existing_promotion.id}")
        assert res.status_code == 204
        
        # Verify soft deleted
        res = client.get(f"/api/promotions/{existing_promotion.id}")
        assert res.status_code == 404  # hoac 200 voi status='deleted'
```

**File: `PMI/backend/tests/test_promotions_lifecycle.py`**
```python
"""
Test Promotion lifecycle transitions
"""

class TestPromotionLifecycle:
    def test_activate_draft_promotion(self, client, db, draft_promotion):
        """draft → active (neu start_at <= now)"""
        res = client.post(f"/api/promotions/{draft_promotion.id}/activate")
        assert res.status_code == 200
        assert res.json()["status"] in ["active", "scheduled"]
    
    def test_activate_sets_scheduled_if_future(self, client, db, future_promotion):
        """draft → scheduled (neu start_at > now)"""
        res = client.post(f"/api/promotions/{future_promotion.id}/activate")
        assert res.status_code == 200
        assert res.json()["status"] == "scheduled"
    
    def test_pause_active_promotion(self, client, db, active_promotion):
        """active → paused"""
        res = client.post(f"/api/promotions/{active_promotion.id}/pause")
        assert res.status_code == 200
        assert res.json()["status"] == "paused"
    
    def test_resume_paused_promotion(self, client, db, paused_promotion):
        """paused → active"""
        res = client.post(f"/api/promotions/{paused_promotion.id}/resume")
        assert res.status_code == 200
        assert res.json()["status"] == "active"
    
    def test_end_promotion(self, client, db, active_promotion):
        """active → ended"""
        res = client.post(f"/api/promotions/{active_promotion.id}/end")
        assert res.status_code == 200
        assert res.json()["status"] == "ended"
    
    def test_cannot_activate_ended_promotion(self, client, db, ended_promotion):
        """ended → active: FAIL"""
        res = client.post(f"/api/promotions/{ended_promotion.id}/activate")
        assert res.status_code == 400
    
    def test_cannot_pause_draft_promotion(self, client, db, draft_promotion):
        """draft → paused: FAIL (phai activate truoc)"""
        res = client.post(f"/api/promotions/{draft_promotion.id}/pause")
        assert res.status_code == 400
```

**File: `PMI/backend/tests/test_promotions_compute.py`**
```python
"""
Test price computation logic
"""

class TestComputePrice:
    def test_percentage_discount(self, db, active_promo_percentage, variant):
        """Giam 20% tu 3,500,000 = 2,800,000"""
        # promo: 20% off
        # variant.price = 3,500,000
        result = compute_final_price(variant, [active_promo_percentage])
        assert result == 2_800_000
    
    def test_fixed_amount_discount(self, db, active_promo_fixed, variant):
        """Giam 500,000 tu 3,500,000 = 3,000,000"""
        result = compute_final_price(variant, [active_promo_fixed])
        assert result == 3_000_000
    
    def test_fixed_price(self, db, active_promo_fixed_price, variant):
        """Gia co dinh 2,000,000"""
        result = compute_final_price(variant, [active_promo_fixed_price])
        assert result == 2_000_000
    
    def test_max_discount_cap(self, db, variant):
        """Giam 50% nhung max 1,000,000"""
        promo = create_promotion(
            discount_type="percentage",
            discount_value=50,
            conditions={"max_discount": 1_000_000}
        )
        # 50% of 3,500,000 = 1,750,000, nhung cap tai 1,000,000
        result = compute_final_price(variant, [promo])
        assert result == 2_500_000  # 3,500,000 - 1,000,000
    
    def test_discount_cannot_go_negative(self, db, cheap_variant):
        """Giam 500k tu san pham 300k = 0 (khong am)"""
        # cheap_variant.price = 300,000
        promo = create_promotion(discount_type="fixed_amount", discount_value=500_000)
        result = compute_final_price(cheap_variant, [promo])
        assert result == 0
    
    def test_no_promotion_returns_original(self, db, variant):
        """Khong co promo → tra ve gia goc"""
        result = compute_final_price(variant, [])
        assert result == variant.price
    
    def test_expired_promotion_ignored(self, db, expired_promotion, variant):
        """Promo het han khong ap dung"""
        result = compute_final_price(variant, [expired_promotion])
        assert result == variant.price
    
    def test_priority_selects_highest(self, db, variant):
        """Nhieu promo → chon priority cao nhat"""
        promo_low = create_promotion(discount_type="percentage", discount_value=10, priority=1)
        promo_high = create_promotion(discount_type="percentage", discount_value=30, priority=10)
        
        result = compute_final_price(variant, [promo_low, promo_high])
        # 30% off (priority 10) wins
        expected = variant.price * 0.7
        assert result == expected


class TestComputedPriceAPI:
    def test_get_computed_price_with_promo(self, client, db, active_promotion, variant_in_scope):
        """API tra ve gia sau giam"""
        res = client.get(f"/api/variants/{variant_in_scope.id}/computed-price")
        assert res.status_code == 200
        assert res.json()["has_promotion"] == True
        assert res.json()["final_price"] < res.json()["original_price"]
    
    def test_get_computed_price_without_promo(self, client, db, variant_not_in_scope):
        """Variant khong co promo → has_promotion = false"""
        res = client.get(f"/api/variants/{variant_not_in_scope.id}/computed-price")
        assert res.status_code == 200
        assert res.json()["has_promotion"] == False
        assert res.json()["final_price"] == res.json()["original_price"]
    
    def test_bulk_computed_prices(self, client, db, active_promotion, multiple_variants):
        """Bulk query nhieu variants"""
        ids = ",".join(str(v.id) for v in multiple_variants)
        res = client.get(f"/api/computed-prices/bulk?variant_ids={ids}")
        assert res.status_code == 200
        assert len(res.json()) == len(multiple_variants)
```

**File: `PMI/backend/tests/test_promotions_scope.py`**
```python
"""
Test promotion scope filtering (brand, category, product)
"""

class TestPromotionScope:
    def test_scope_all_products(self, db, promo_all, all_variants):
        """scope_type='all' ap dung cho tat ca"""
        for v in all_variants:
            assert variant_in_scope(v, promo_all) == True
    
    def test_scope_by_brand(self, db, promo_yonex, yonex_variant, victor_variant):
        """scope_type='brand', scope_value=['Yonex']"""
        assert variant_in_scope(yonex_variant, promo_yonex) == True
        assert variant_in_scope(victor_variant, promo_yonex) == False
    
    def test_scope_by_category(self, db, promo_rackets, racket_variant, shoe_variant):
        """scope_type='category', scope_value=[1] (rackets)"""
        assert variant_in_scope(racket_variant, promo_rackets) == True
        assert variant_in_scope(shoe_variant, promo_rackets) == False
    
    def test_scope_by_product(self, db, promo_specific, target_variant, other_variant):
        """scope_type='product', scope_value=[123]"""
        assert variant_in_scope(target_variant, promo_specific) == True
        assert variant_in_scope(other_variant, promo_specific) == False
    
    def test_scope_with_exclusion(self, db, promo_all_except, normal_variant, excluded_variant):
        """scope_type='all' + exclude_type='product'"""
        assert variant_in_scope(normal_variant, promo_all_except) == True
        assert variant_in_scope(excluded_variant, promo_all_except) == False
```

**File: `PMI/backend/tests/test_promotions_scheduler.py`**
```python
"""
Test auto-scheduler (cron job)
"""

class TestPromotionScheduler:
    def test_scheduled_becomes_active(self, db, scheduled_promotion_starting_now):
        """scheduled → active khi start_at <= now"""
        update_promotion_statuses()
        
        db.refresh(scheduled_promotion_starting_now)
        assert scheduled_promotion_starting_now.status == "active"
    
    def test_active_becomes_ended(self, db, active_promotion_ending_now):
        """active → ended khi end_at < now"""
        update_promotion_statuses()
        
        db.refresh(active_promotion_ending_now)
        assert active_promotion_ending_now.status == "ended"
    
    def test_paused_not_affected(self, db, paused_promotion):
        """paused khong bi scheduler doi"""
        original_status = paused_promotion.status
        update_promotion_statuses()
        
        db.refresh(paused_promotion)
        assert paused_promotion.status == original_status
```

### 10.2. Frontend Unit Tests (Vitest + React Testing Library)

**File: `PMI/frontend/src/__tests__/promotions/PromotionList.test.tsx`**
```typescript
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import PromotionList from "@/app/promotions/page";

const mockPromotions = [
  { id: 1, code: "SUMMER20", name: "Summer Sale", status: "active", discount_type: "percentage", discount_value: 20 },
  { id: 2, code: "NEWUSER", name: "New User", status: "scheduled", discount_type: "fixed_amount", discount_value: 50000 },
];

describe("PromotionList", () => {
  beforeEach(() => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockPromotions),
    });
  });

  test("renders promotion list with correct data", async () => {
    render(<PromotionList />);
    
    await waitFor(() => {
      expect(screen.getByText("SUMMER20")).toBeInTheDocument();
      expect(screen.getByText("NEWUSER")).toBeInTheDocument();
    });
  });

  test("shows status badges correctly", async () => {
    render(<PromotionList />);
    
    await waitFor(() => {
      expect(screen.getByText("Đang chạy")).toBeInTheDocument();
      expect(screen.getByText("Đã lên lịch")).toBeInTheDocument();
    });
  });

  test("filter by status works", async () => {
    render(<PromotionList />);
    
    const filterButton = await screen.findByRole("button", { name: /lọc/i });
    await userEvent.click(filterButton);
    
    const activeFilter = screen.getByText("Đang chạy");
    await userEvent.click(activeFilter);
    
    // Verify fetch called with status filter
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("status=active")
    );
  });

  test("create button navigates to form", async () => {
    render(<PromotionList />);
    
    const createButton = await screen.findByRole("button", { name: /tạo/i });
    expect(createButton).toHaveAttribute("href", "/promotions/new");
  });
});
```

**File: `PMI/frontend/src/__tests__/promotions/PromotionForm.test.tsx`**
```typescript
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import PromotionForm from "@/app/promotions/new/page";

describe("PromotionForm", () => {
  test("renders all form fields", () => {
    render(<PromotionForm />);
    
    expect(screen.getByLabelText(/mã km/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/tên/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/loại giảm giá/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/giá trị/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/bắt đầu/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/kết thúc/i)).toBeInTheDocument();
  });

  test("validates required fields", async () => {
    render(<PromotionForm />);
    
    const submitButton = screen.getByRole("button", { name: /lưu/i });
    await userEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/mã km là bắt buộc/i)).toBeInTheDocument();
    });
  });

  test("validates percentage max 100", async () => {
    render(<PromotionForm />);
    
    const valueInput = screen.getByLabelText(/giá trị/i);
    await userEvent.type(valueInput, "150");
    
    const submitButton = screen.getByRole("button", { name: /lưu/i });
    await userEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/không được vượt quá 100/i)).toBeInTheDocument();
    });
  });

  test("validates end date after start date", async () => {
    render(<PromotionForm />);
    
    const startInput = screen.getByLabelText(/bắt đầu/i);
    const endInput = screen.getByLabelText(/kết thúc/i);
    
    await userEvent.type(startInput, "2026-08-15");
    await userEvent.type(endInput, "2026-08-01");
    
    const submitButton = screen.getByRole("button", { name: /lưu/i });
    await userEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/ngày kết thúc phải sau ngày bắt đầu/i)).toBeInTheDocument();
    });
  });

  test("preview shows affected products", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ affected_variants: 152 }),
    });
    
    render(<PromotionForm />);
    
    // Fill form...
    const previewButton = screen.getByRole("button", { name: /xem trước/i });
    await userEvent.click(previewButton);
    
    await waitFor(() => {
      expect(screen.getByText(/152 sản phẩm/i)).toBeInTheDocument();
    });
  });

  test("submits form successfully", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ id: 1, code: "TEST" }),
    });
    
    render(<PromotionForm />);
    
    await userEvent.type(screen.getByLabelText(/mã km/i), "TEST");
    await userEvent.type(screen.getByLabelText(/tên/i), "Test Promotion");
    await userEvent.type(screen.getByLabelText(/giá trị/i), "20");
    await userEvent.type(screen.getByLabelText(/bắt đầu/i), "2026-08-01");
    await userEvent.type(screen.getByLabelText(/kết thúc/i), "2026-08-15");
    
    const submitButton = screen.getByRole("button", { name: /lưu/i });
    await userEvent.click(submitButton);
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/promotions"),
        expect.objectContaining({ method: "POST" })
      );
    });
  });
});
```

### 10.3. Web Frontend Tests

**File: `web/src/__tests__/hooks/useComputedPrice.test.ts`**
```typescript
import { renderHook, waitFor } from "@testing-library/react";
import { useComputedPrice } from "@/hooks/useComputedPrice";

describe("useComputedPrice", () => {
  test("returns computed price when promotion active", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        has_promotion: true,
        original_price: 3500000,
        final_price: 2800000,
        discount_amount: 700000,
        promotion: { code: "SUMMER20", name: "Summer Sale" }
      }),
    });
    
    const { result } = renderHook(() => useComputedPrice(123));
    
    await waitFor(() => {
      expect(result.current.hasPromotion).toBe(true);
      expect(result.current.finalPrice).toBe(2800000);
      expect(result.current.discountAmount).toBe(700000);
    });
  });

  test("returns original price when no promotion", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        has_promotion: false,
        original_price: 3500000,
        final_price: 3500000,
      }),
    });
    
    const { result } = renderHook(() => useComputedPrice(123));
    
    await waitFor(() => {
      expect(result.current.hasPromotion).toBe(false);
      expect(result.current.finalPrice).toBe(3500000);
    });
  });

  test("handles API error gracefully", async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error("Network error"));
    
    const { result } = renderHook(() => useComputedPrice(123));
    
    await waitFor(() => {
      expect(result.current.error).toBeTruthy();
      expect(result.current.finalPrice).toBeUndefined();
    });
  });
});
```

**File: `web/src/__tests__/components/ProductCard.test.tsx`** (cap nhat)
```typescript
// Them test cases cho promotion display

describe("ProductCard with promotions", () => {
  test("shows sale price when promotion active", () => {
    const product = {
      ...mockProduct,
      salePrice: 2800000,  // computed from API
      price: 3500000,
    };
    
    render(<ProductCard product={product} />);
    
    expect(screen.getByText("2,800,000đ")).toBeInTheDocument();
    expect(screen.getByText("3,500,000đ")).toHaveClass("line-through");
  });

  test("shows discount percentage badge", () => {
    const product = {
      ...mockProduct,
      salePrice: 2800000,
      price: 3500000,
    };
    
    render(<ProductCard product={product} />);
    
    expect(screen.getByText("-20%")).toBeInTheDocument();
  });

  test("shows only regular price when no promotion", () => {
    const product = {
      ...mockProduct,
      salePrice: undefined,
      price: 3500000,
    };
    
    render(<ProductCard product={product} />);
    
    expect(screen.getByText("3,500,000đ")).toBeInTheDocument();
    expect(screen.queryByText("line-through")).not.toBeInTheDocument();
  });
});
```

### 10.4. E2E Tests (Playwright)

**File: `e2e_tests/tests/test_promotion_full_flow.py`**
```python
"""
E2E test: Full promotion flow from creation to web display
"""
import pytest
from playwright.sync_api import Page, expect

class TestPromotionE2E:
    @pytest.fixture
    def promotion_data(self):
        return {
            "code": f"E2E_TEST_{int(time.time())}",
            "name": "E2E Test Promotion",
            "discount_type": "percentage",
            "discount_value": 25,
        }

    def test_create_activate_and_verify_on_web(
        self, 
        pmi_page: Page, 
        web_page: Page, 
        promotion_data,
        test_product
    ):
        """
        1. Tao promotion trong PMI
        2. Activate promotion
        3. Verify gia giam hien thi tren web
        """
        # Step 1: Login PMI va tao promotion
        pmi_page.goto("/promotions/new")
        pmi_page.fill("[name=code]", promotion_data["code"])
        pmi_page.fill("[name=name]", promotion_data["name"])
        pmi_page.select_option("[name=discount_type]", "percentage")
        pmi_page.fill("[name=discount_value]", "25")
        pmi_page.fill("[name=start_at]", "2026-01-01")
        pmi_page.fill("[name=end_at]", "2026-12-31")
        
        # Select target product
        pmi_page.click("[data-testid=scope-product]")
        pmi_page.fill("[data-testid=product-search]", test_product["name"])
        pmi_page.click(f"[data-testid=product-{test_product['id']}]")
        
        # Save
        pmi_page.click("[data-testid=save-draft]")
        expect(pmi_page.locator("[data-testid=success-message]")).to_be_visible()
        
        # Step 2: Activate
        pmi_page.click("[data-testid=activate-button]")
        expect(pmi_page.locator("[data-testid=status-active]")).to_be_visible()
        
        # Step 3: Verify on web
        web_page.goto(f"/product/{test_product['slug']}")
        
        # Original price should be crossed out
        original_price = web_page.locator("[data-testid=original-price]")
        expect(original_price).to_have_class(/line-through/)
        
        # Sale price should be 25% off
        sale_price = web_page.locator("[data-testid=sale-price]")
        expected_sale = test_product["price"] * 0.75
        expect(sale_price).to_contain_text(f"{expected_sale:,.0f}")
        
        # Discount badge
        expect(web_page.locator("[data-testid=discount-badge]")).to_contain_text("-25%")

    def test_ended_promotion_not_shown_on_web(
        self, 
        pmi_page: Page, 
        web_page: Page, 
        active_promotion,
        test_product
    ):
        """
        1. End promotion
        2. Verify web khong con hien gia giam
        """
        # End promotion
        pmi_page.goto(f"/promotions/{active_promotion['id']}")
        pmi_page.click("[data-testid=end-button]")
        pmi_page.click("[data-testid=confirm-end]")
        expect(pmi_page.locator("[data-testid=status-ended]")).to_be_visible()
        
        # Verify web - no sale price
        web_page.goto(f"/product/{test_product['slug']}")
        web_page.reload()  # Force refresh
        
        expect(web_page.locator("[data-testid=sale-price]")).not_to_be_visible()
        expect(web_page.locator("[data-testid=discount-badge]")).not_to_be_visible()


class TestPromotionScheduler:
    def test_scheduled_promotion_activates_on_time(
        self,
        db,
        scheduled_promotion_starting_soon
    ):
        """
        1. Tao promotion scheduled start trong 1 phut
        2. Doi scheduler chay
        3. Verify status = active
        """
        # Wait for scheduler (chay moi phut)
        time.sleep(65)
        
        # Refresh from DB
        promo = db.query(Promotion).get(scheduled_promotion_starting_soon.id)
        assert promo.status == "active"
```

### 10.5. Test Coverage Requirements

| Component | Min Coverage | Critical Paths |
|-----------|--------------|----------------|
| `promotions/` (backend) | 90% | CRUD, lifecycle, compute |
| `PromotionForm.tsx` | 85% | validation, submit |
| `PromotionList.tsx` | 80% | filter, pagination |
| `useComputedPrice.ts` | 90% | fetch, error handling |
| `productMappers.ts` | 85% | price mapping |

**CI Pipeline check:**
```yaml
# .github/workflows/test.yml
- name: Run tests with coverage
  run: |
    pytest --cov=PMI/backend --cov-fail-under=85
    npm run test:coverage -- --coverage.thresholds.lines=80
```

## Sources

- [Omnia Retail - E-commerce Discounts Best Practices](https://www.omniaretail.com/blog/e-commerce-discounts-types-benefits-and-how-to-use-psychology-to-make-them-effective)
- [Grid Dynamics - How to Build a Pricing Engine](https://www.griddynamics.com/blog/how-to-replatform-a-pricing-engine)
- [Medium - Building a Flexible Discount Engine](https://medium.com/@sammyasopa/building-a-flexible-discount-engine-b9f4fba3af51)
- [Codesol Tech - Coupon & Discount Engine Development](https://www.codesoltech.com/blog/coupon-discount-engine-development/)
- [Pimcore - Price Management](https://pimcore.com/en/products/product-information-management/price-management)
- [Medusa Documentation - Promotion Module](https://docs.medusajs.com/resources/commerce-modules/promotion)
- [Medusa - Promotion Concepts](https://docs.medusajs.com/resources/commerce-modules/promotion/concepts)
- [Netguru - Saleor vs Medusa Comparison](https://www.netguru.com/blog/saleor-vs-medusa)
