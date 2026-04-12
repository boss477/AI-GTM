"""
invoice_pdf.py  –  Performa Invoice Generator
Matches the Shearling Skins Pvt Ltd PI format exactly.
"""

import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ─────────────────────────────────────────────
# Colour palette (mirrors invoice images)
# ─────────────────────────────────────────────
HEADER_BG   = colors.HexColor("#D9D9D9")   # light grey band
TABLE_HEAD  = colors.HexColor("#C0C0C0")   # column-header grey
BORDER_CLR  = colors.HexColor("#808080")
WHITE       = colors.white
BLACK       = colors.black

PAGE_W, PAGE_H = A4
LEFT_M = RIGHT_M = TOP_M = BOT_M = 10 * mm
USABLE_W = PAGE_W - LEFT_M - RIGHT_M       # ≈ 190 mm

styles = getSampleStyleSheet()

def _style(name, **kw):
    s = ParagraphStyle(name, **kw)
    return s

# ─────────────────────────────────────────────
# Paragraph style helpers
# ─────────────────────────────────────────────
H1 = _style("H1", fontName="Helvetica-Bold",  fontSize=13, alignment=TA_CENTER, leading=16)
H2 = _style("H2", fontName="Helvetica-Bold",  fontSize=10, alignment=TA_CENTER, leading=13)
H3 = _style("H3", fontName="Helvetica",       fontSize=8,  alignment=TA_CENTER, leading=11)
NL = _style("NL", fontName="Helvetica",       fontSize=8,  alignment=TA_LEFT,   leading=10)
NR = _style("NR", fontName="Helvetica",       fontSize=8,  alignment=TA_RIGHT,  leading=10)
NB = _style("NB", fontName="Helvetica-Bold",  fontSize=8,  alignment=TA_LEFT,   leading=10)
NC = _style("NC", fontName="Helvetica",       fontSize=8,  alignment=TA_CENTER, leading=10)
NBC= _style("NBC",fontName="Helvetica-Bold",  fontSize=8,  alignment=TA_CENTER, leading=10)
SM = _style("SM", fontName="Helvetica",       fontSize=7,  alignment=TA_LEFT,   leading=9)
SMC= _style("SMC",fontName="Helvetica",       fontSize=7,  alignment=TA_CENTER, leading=9)
SML= _style("SML",fontName="Helvetica-Bold",  fontSize=7,  alignment=TA_LEFT,   leading=9)
SMR= _style("SMR",fontName="Helvetica",       fontSize=7,  alignment=TA_RIGHT,  leading=9)


def _p(text, style=NL):
    return Paragraph(str(text) if text else "", style)


# ─────────────────────────────────────────────
# HEADER BLOCK
# ─────────────────────────────────────────────
def _build_header(seller, pi_number, revision, pi_date, logo_path=None):
    """3-column header: logo | title+company+address | PI info"""

    # Left cell – logo or placeholder
    if logo_path and os.path.exists(logo_path):
        logo_cell = Image(logo_path, width=40 * mm, height=20 * mm)
    else:
        logo_cell = _p("<b>COMPANY<br/>LOGO</b>", NBC)

    # Centre cell
    centre = [
        _p("Performa Invoice", H1),
        _p(seller.get("name", ""), H2),
        _p(seller.get("address", ""), H3),
    ]

    # Right cell – PI number block
    right = [
        _p(f"<b>PI#{pi_number}</b>  (Revision {revision}  {pi_date})", NB),
        _p(pi_date, NR),
    ]

    data = [[logo_cell, centre, right]]
    col_w = [40 * mm, USABLE_W - 40 * mm - 45 * mm, 45 * mm]
    t = Table(data, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), HEADER_BG),
        ("BOX",         (0, 0), (-1, -1), 0.8, BORDER_CLR),
        ("INNERGRID",   (0, 0), (-1, -1), 0.5, BORDER_CLR),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",       (2, 0), (2, 0),   "RIGHT"),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0),(-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",(0, 0), (-1, -1), 4),
    ]))
    return t


# ─────────────────────────────────────────────
# CUSTOMER BLOCK  (3 columns)
# ─────────────────────────────────────────────
def _build_customer_block(customer, seller, contact):
    """
    customer : { name, contact_person, address, mobile, email }
    seller   : { name, address, gstin }
    contact  : { person, mobile, email }
    """
    def _cell(lines):
        return [_p(l, SM) for l in lines]

    left = _cell([
        f"Name : {customer.get('name', '')}",
        f"Contact Person : {customer.get('contact_person', '')}",
        f"Address : {customer.get('address', '')}",
        f"Mob. No. :{customer.get('mobile', '')}",
        f"Email Address :{customer.get('email', '')}",
    ])

    centre = _cell([
        seller.get("name", ""),
        seller.get("address", ""),
        f"GSTIN NO. : {seller.get('gstin', '')}",
    ])

    right = _cell([
        f"Contact Person : {contact.get('person', '')}",
        f"Mobile: {contact.get('mobile', '')}",
        f"Email Address: {contact.get('email', '')}",
    ])

    col_w = [USABLE_W * 0.35, USABLE_W * 0.35, USABLE_W * 0.30]
    data = [[left, centre, right]]
    t = Table(data, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 0.8, BORDER_CLR),
        ("INNERGRID",     (0, 0), (-1, -1), 0.5, BORDER_CLR),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
    ]))
    return t


# ─────────────────────────────────────────────
# LINE ITEMS TABLE
# ─────────────────────────────────────────────
def _build_items_table(line_items):
    """
    Each item dict:
      sno, description, picture (path or None), size,
      upholstery_top, base, leg_polish, units,
      net_price, total, remark
    """
    # Column widths  – must sum to USABLE_W  (≈ 190 mm)
    col_w = [
        7*mm,   # S.No.
        28*mm,  # Description
        22*mm,  # Picture
        23*mm,  # Size
        17*mm,  # Upholstery/Top
        14*mm,  # Base
        18*mm,  # Leg Polish
        9*mm,   # Units
        16*mm,  # Net Price
        17*mm,  # Total
        10*mm,  # Remark - will be given remaining extra space automatically
    ]
    # Adjust last col to fill remaining width
    col_w[-1] = USABLE_W - sum(col_w[:-1])

    headers = [
        _p("S.No.",              NBC),
        _p("Description",        NBC),
        _p("Picture",            NBC),
        _p("Size",               NBC),
        _p("Upholstery\n/Top",   NBC),
        _p("Base",               NBC),
        _p("Leg polish",         NBC),
        _p("Units",              NBC),
        _p("Net Price\n(Rs.)",   NBC),
        _p("Total (Rs.)",        NBC),
        _p("Remark",             NBC),
    ]

    rows = [headers]

    for item in line_items:
        # Picture cell
        pic_path = str(item.get("picture") or "").strip()
        pic_cell = _p("", SMC)
        if pic_path:
            if pic_path.startswith("http") or os.path.exists(pic_path):
                try:
                    pic_cell = Image(pic_path, width=20 * mm, height=18 * mm)
                except Exception:
                    pass

        net_price = float(item.get("net_price", 0))
        units     = int(item.get("units", 1))
        total     = float(item.get("total", net_price * units))

        row = [
            _p(str(item.get("sno", "")),             SMC),
            _p(item.get("description", ""),           SM),
            pic_cell,
            _p(item.get("size", ""),                  SMC),
            _p(item.get("upholstery_top", ""),        SMC),
            _p(item.get("base", ""),                  SMC),
            _p(item.get("leg_polish", ""),            SMC),
            _p(str(units),                            SMC),
            _p(f"{net_price:,.2f}",                   SMR),
            _p(f"{total:,.2f}",                       SMR),
            _p(item.get("remark", ""),                SMC),
        ]
        rows.append(row)

    t = Table(rows, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  TABLE_HEAD),
        ("BOX",           (0, 0), (-1, -1), 0.8, BORDER_CLR),
        ("INNERGRID",     (0, 0), (-1, -1), 0.5, BORDER_CLR),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 2),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 2),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, colors.HexColor("#F5F5F5")]),
    ]))
    return t


# ─────────────────────────────────────────────
# TOTALS + BANK DETAILS BLOCK
# ─────────────────────────────────────────────
def _build_footer_block(total_amount, bank_details):
    """
    Two-column table side-by-side:
    Left: Bank Details  |  Right: Calculated totals
    """
    packaging_amount  = total_amount * 0.03
    subtotal          = total_amount + packaging_amount
    gst               = subtotal * 0.18
    grand_total       = subtotal + gst

    # ── Totals right panel ──────────────────
    totals_data = [
        [_p("<b>Total Amount</b>",   SML), _p(f"Rs. {total_amount:,.2f}",  SMR)],
        [_p("Freight",               SM),  _p("TO BE PAID BY THE CLIENT",  SMR)],
        [_p("Packaging 3 %",         SM),  _p(f"Rs. {packaging_amount:,.2f}", SMR)],
        [_p("Installation 0 %",      SM),  _p("Rs. 0.00",                  SMR)],
        [_p("<b>Sub Total</b>",      SML), _p(f"Rs. {subtotal:,.2f}",      SMR)],
        [_p("GST 18%",               SM),  _p(f"Rs. {gst:,.2f}",           SMR)],
        [_p("<b>Grand Total</b>",    SML), _p(f"Rs. {grand_total:,.2f}",   SMR)],
    ]
    right_w = USABLE_W * 0.50
    tot_col = [right_w * 0.55, right_w * 0.45]
    totals_t = Table(totals_data, colWidths=tot_col)
    totals_t.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 0.8, BORDER_CLR),
        ("INNERGRID",     (0, 0), (-1, -1), 0.4, BORDER_CLR),
        ("BACKGROUND",    (0, 0), (-1, 0),  TABLE_HEAD),
        ("BACKGROUND",    (0, 4), (-1, 4),  colors.HexColor("#EFEFEF")),
        ("BACKGROUND",    (0, 6), (-1, 6),  TABLE_HEAD),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 3),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 3),
    ]))

    # ── Bank details left panel ─────────────
    bd = bank_details or {}
    bank_data = [
        [_p("<b>BANK DETAILS:</b>",         SML), _p("",                                    SM)],
        [_p("BENEFICIARY NAME",             SM),  _p(bd.get("beneficiary_name", ""),         SM)],
        [_p("BANK NAME",                    SM),  _p(bd.get("bank_name", ""),                SM)],
        [_p("ACCOUNT NO.",                  SM),  _p(bd.get("account_no", ""),               SM)],
        [_p("RTGS/NEFT/IFSC CODE",          SM),  _p(bd.get("ifsc_code", ""),                SM)],
    ]
    left_w = USABLE_W - right_w
    bank_col = [left_w * 0.40, left_w * 0.60]
    bank_t = Table(bank_data, colWidths=bank_col)
    bank_t.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 0.8, BORDER_CLR),
        ("INNERGRID",     (0, 0), (-1, -1), 0.4, BORDER_CLR),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 3),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 3),
        ("SPAN",          (0, 0), (-1, 0)),
    ]))

    # Combine side by side
    combined = Table([[bank_t, totals_t]], colWidths=[left_w, right_w])
    combined.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
    ]))
    return combined


# ─────────────────────────────────────────────
# TERMS & CONDITIONS
# ─────────────────────────────────────────────
TERMS = [
    "Lead time: 7-8 Weeks.",
    "Payment terms - 50% Advance & PO and 50% before delivery",
    "All orders must be written, signed with deposit of Advance",
    "Customer is expected to Inspect the Goods before Final Delivery.",
    "No cancellations will be accepted on custom orders once they are in Production.",
    "No returns will be accepted.",
    "No material will be accepted for claim if marked or cut.",
    "All prices are valid for 30 days",
    "Uploading Charges extra at actual.",
]

def _build_terms():
    rows = [[_p("<b>Terms & Condition :</b>", SML)]]
    for i, term in enumerate(TERMS, 1):
        rows.append([_p(f"{i}   {term}", SM)])
    t = Table(rows, colWidths=[USABLE_W])
    t.setStyle(TableStyle([
        ("BOX",     (0, 0), (-1, -1), 0.8, BORDER_CLR),
        ("INNERGRID",(0, 0),(-1, -1), 0.3, colors.HexColor("#CCCCCC")),
        ("TOPPADDING",(0, 0),(-1,-1), 2),
        ("BOTTOMPADDING",(0,0),(-1,-1),2),
        ("LEFTPADDING",(0,0),(-1,-1), 4),
        ("RIGHTPADDING",(0,0),(-1,-1),4),
    ]))
    return t


# ─────────────────────────────────────────────
# PUBLIC ENTRY POINT
# ─────────────────────────────────────────────
def generate_performa_invoice(
    pi_number: str,
    revision: int,
    pi_date: str,
    seller: dict,
    customer: dict,
    contact: dict,
    line_items: list,
    bank_details: dict,
    logo_path: str = None,
    output_dir: str = "invoices",
) -> str:
    """
    Generate a Performa Invoice PDF.

    seller   = { name, address, gstin }
    customer = { name, contact_person, address, mobile, email }
    contact  = { person, mobile, email }
    bank_details = { beneficiary_name, bank_name, account_no, ifsc_code }
    line_items = [{ sno, description, picture, size, upholstery_top,
                     base, leg_polish, units, net_price, total, remark }]

    Returns the path to the generated PDF.
    """
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"PI-{pi_number}.pdf")

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        leftMargin=LEFT_M,
        rightMargin=RIGHT_M,
        topMargin=TOP_M,
        bottomMargin=BOT_M,
    )

    # Compute total from line items if not provided separately
    total_amount = sum(
        float(item.get("total", float(item.get("net_price", 0)) * int(item.get("units", 1))))
        for item in line_items
    )

    elements = []
    elements.append(_build_header(seller, pi_number, revision, pi_date, logo_path))
    elements.append(Spacer(1, 1 * mm))
    elements.append(_build_customer_block(customer, seller, contact))
    elements.append(Spacer(1, 1 * mm))
    elements.append(_build_items_table(line_items))
    elements.append(Spacer(1, 1 * mm))
    elements.append(_build_footer_block(total_amount, bank_details))
    elements.append(Spacer(1, 1 * mm))
    elements.append(_build_terms())

    doc.build(elements)
    return file_path


# ─────────────────────────────────────────────
# Legacy shim – keeps old callers working
# ─────────────────────────────────────────────
def generate_invoice(invoice_number, customer_name, customer_email, total_amount, due_date):
    """
    Backward-compatible wrapper used by invoice_service.py for simple milestone invoices.
    Builds a minimal PI with one line-item from the old parameters.
    """
    seller = {
        "name":    "SHEARLING SKINS PVT LTD",
        "address": "PLOT NO 84 SECTOR 8 IMT MANESAR GURGAON(HR) PINCODE-122052",
        "gstin":   "06AALCS1032L1ZC",
    }
    customer = {
        "name":           customer_name,
        "contact_person": "",
        "address":        "",
        "mobile":         "",
        "email":          customer_email,
    }
    contact = {"person": "Ms. TANNU PHOGAT", "mobile": "9910088313", "email": "be1@shearling.in"}
    bank_details = {
        "beneficiary_name": "SHEARLING SKINS PVT LTD",
        "bank_name":        "DEUTSCHE BANK",
        "account_no":       "100041596120019",
        "ifsc_code":        "DEUT0784PBC",
    }
    line_items = [{
        "sno":           1,
        "description":   "Milestone Payment",
        "picture":       None,
        "size":          "",
        "upholstery_top":"",
        "base":          "",
        "leg_polish":    "",
        "units":         1,
        "net_price":     total_amount,
        "total":         total_amount,
        "remark":        "",
    }]

    return generate_performa_invoice(
        pi_number    = invoice_number,
        revision     = 1,
        pi_date      = due_date,
        seller       = seller,
        customer     = customer,
        contact      = contact,
        line_items   = line_items,
        bank_details = bank_details,
    )
