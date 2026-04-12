"""
test_performa_invoice.py
Run from invoice_system/ directory:
    python test_performa_invoice.py
Generates a sample PI PDF locally WITHOUT hitting Supabase or sending email.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from invoice_pdf import generate_performa_invoice

seller = {
    "name":    "SHEARLING SKINS PVT LTD",
    "address": "PLOT NO 84 SECTOR 8 IMT MANESAR GURGAON(HR) PINCODE-122052",
    "gstin":   "06AALCS1032L1ZC",
}

customer = {
    "name":           "STUDIONKON VENTURES",
    "contact_person": "BHAVUK",
    "address":        "UDYOG VIHAR GURUGRAM HARYANA 204101",
    "mobile":         "9810915985",
    "email":          "prfactory@studiokon.com",
}

contact = {
    "person": "Ms. TANNU PHOGAT",
    "mobile": "9910088313",
    "email":  "be1@shearling.in",
}

bank_details = {
    "beneficiary_name": "SHEARLING SKINS PVT LTD",
    "bank_name":        "DEUTSCHE BANK",
    "account_no":       "100041596120019",
    "ifsc_code":        "DEUT0784PBC",
}

line_items = [
    {
        "sno":            1,
        "description":    "REEVES LOUNGE CHAIR",
        "picture":        None,            # swap to a real image path to test
        "size":           "W: 850 X L: X H :700 X D :850",
        "upholstery_top": "COF",
        "base":           "WOODEN / METAL",
        "leg_polish":     "WOODEN FINISH TO BE CONFIRMED | METAL BASE FINISH IS BLACK POWDER COATED",
        "units":          4,
        "net_price":      10960.00,
        "total":          43840.00,
        "remark":         "",
    },
    {
        "sno":            2,
        "description":    "PORTO DINING CHAIR",
        "picture":        "https://uiqzkfawnswsrhxkambl.supabase.co/storage/v1/object/public/chairs/sample_chair.jpg",
        "size":           "W: 500 X H: 870 X D: 560",
        "upholstery_top": "FABRIC – BEIGE",
        "base":           "SOLID WOOD",
        "leg_polish":     "WALNUT STAIN",
        "units":          8,
        "net_price":      7500.00,
        "total":          60000.00,
        "remark":         "",
    },
    {
        "sno":            16,
        "description":    "IBS SS/MS KNIFE EDGE",
        "picture":        None,
        "size":           "Top: 800 X H :450 X Base :",
        "upholstery_top": "LAMINATE TO BE CONFIRMED",
        "base":           "TABLE",
        "leg_polish":     "BLACK POWDER COATED",
        "units":          1,
        "net_price":      9700.00,
        "total":          9700.00,
        "remark":         "",
    },
]

pdf_path = generate_performa_invoice(
    pi_number    = "2129",
    revision     = 1,
    pi_date      = "12 Jan 2026",
    seller       = seller,
    customer     = customer,
    contact      = contact,
    line_items   = line_items,
    bank_details = bank_details,
    logo_path    = None,
    output_dir   = "invoices",
)

print(f"\n✅  Performa Invoice generated: {pdf_path}\n")
