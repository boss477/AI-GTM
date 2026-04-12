-- ============================================================
-- Supabase SQL Migration  –  Performa Invoice + Furniture
-- Run this in: Supabase Dashboard → SQL Editor → New Query
-- ============================================================


-- ── 1. Add new columns to the existing `orders` table ───────
--    (These are all nullable so existing rows are unaffected)

ALTER TABLE public.orders
  ADD COLUMN IF NOT EXISTS revision             INT        DEFAULT 1,
  ADD COLUMN IF NOT EXISTS customer_contact_person TEXT,
  ADD COLUMN IF NOT EXISTS customer_address     TEXT,
  ADD COLUMN IF NOT EXISTS customer_mobile      TEXT,
  ADD COLUMN IF NOT EXISTS seller_name          TEXT,
  ADD COLUMN IF NOT EXISTS seller_address       TEXT,
  ADD COLUMN IF NOT EXISTS seller_gstin         TEXT,
  ADD COLUMN IF NOT EXISTS contact_person       TEXT,
  ADD COLUMN IF NOT EXISTS contact_mobile       TEXT,
  ADD COLUMN IF NOT EXISTS contact_email        TEXT,
  ADD COLUMN IF NOT EXISTS bank_beneficiary     TEXT,
  ADD COLUMN IF NOT EXISTS bank_name            TEXT,
  ADD COLUMN IF NOT EXISTS bank_account         TEXT,
  ADD COLUMN IF NOT EXISTS bank_ifsc            TEXT,
  ADD COLUMN IF NOT EXISTS logo_path            TEXT,
  ADD COLUMN IF NOT EXISTS line_items           JSONB;  -- array of furniture items


-- ── 2. Furniture items catalogue table ──────────────────────

CREATE TABLE IF NOT EXISTS public.furniture_items (
    id           UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at   TIMESTAMPTZ DEFAULT now(),
    name         TEXT        NOT NULL,
    item_type    TEXT        DEFAULT 'chair',  -- 'chair', 'table', 'sofa', etc.
    description  TEXT,
    size         TEXT,           -- e.g. "W:850 X L:X X H:700 X D:850"
    upholstery_top TEXT,
    base         TEXT,
    leg_polish   TEXT,
    net_price    NUMERIC(12,2),
    image_url    TEXT,
    dimensions   JSONB,          -- { width, depth, height } in mm
    metadata     JSONB
);

-- RLS
ALTER TABLE public.furniture_items ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow public read"  ON public.furniture_items FOR SELECT USING (true);
CREATE POLICY "Allow anon insert"  ON public.furniture_items FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anon update"  ON public.furniture_items FOR UPDATE USING (true);




INSERT INTO public.furniture_items
    (name, item_type, description, size, upholstery_top, base, leg_polish, net_price)
VALUES
    ('REEVES LOUNGE CHAIR', 'chair',
     'Lounge chair with wooden/metal base',
     'W: 850 X L: X X H: 700 X D: 850',
     'COF', 'WOODEN / METAL',
     'WOODEN FINISH TO BE CONFIRMED | METAL BASE FINISH IS BLACK POWDER COATED',
     10960.00),
    ('IBS SS/MS KNIFE EDGE', 'table',
     'Side/Coffee table with laminate top',
     'Top: 800 X H: 450 X Base: ',
     'LAMINATE TO BE CONFIRMED', 'TABLE',
     'BLACK POWDER COATED',
     9700.00)
ON CONFLICT DO NOTHING;
