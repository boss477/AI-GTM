from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import os


def generate_invoice(invoice_number, customer_name, customer_email, total_amount, due_date):

    # Create invoices folder if not exists
    if not os.path.exists("invoices"):
        os.makedirs("invoices")

    file_name = f"invoices/{invoice_number}.pdf"
    doc = SimpleDocTemplate(file_name)

    elements = []
    styles = getSampleStyleSheet()

    # --------------------------
    # Company Header
    # --------------------------
    elements.append(Paragraph("🚀 NovaTech Solutions Pvt Ltd", styles["Heading1"]))
    elements.append(Spacer(1, 0.3 * inch))

    # --------------------------
    # Invoice Info
    # --------------------------
    elements.append(Paragraph(f"<b>Invoice Number:</b> {invoice_number}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Due Date:</b> {due_date}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    # --------------------------
    # Bill To Section (Dynamic)
    # --------------------------
    elements.append(Paragraph("<b>Bill To:</b>", styles["Normal"]))
    elements.append(Paragraph(customer_name, styles["Normal"]))
    elements.append(Paragraph(customer_email, styles["Normal"]))
    elements.append(Spacer(1, 0.5 * inch))

    # --------------------------
    # Invoice Table
    # --------------------------
    subtotal = total_amount / 1.18
    tax = total_amount - subtotal

    data = [
        ["Description", "Amount (₹)"],
        ["Milestone Payment", f"{subtotal:.2f}"],
        ["GST (18%)", f"{tax:.2f}"],
        ["Total", f"{total_amount:.2f}"]
    ]

    table = Table(data, colWidths=[3 * inch, 2 * inch])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.5 * inch))

    # --------------------------
    # Footer
    # --------------------------
    elements.append(Paragraph("Thank you for your business!", styles["Normal"]))
    elements.append(Paragraph("Payment due within 7 days.", styles["Normal"]))

    doc.build(elements)

    return file_name
