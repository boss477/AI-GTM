from pydantic import BaseModel
from typing import Optional, List
from agno.tools import Toolkit
from invoice_service import create_invoice
from email_service import send_email
from scheduler import check_overdue_invoices

class InvoiceSystemTools(Toolkit):
    def __init__(self):
        super().__init__(name="invoice_tools")
        self.register(self.generate_invoice_tool)
        self.register(self.send_email_tool)
        self.register(self.check_overdue_tool)

    def generate_invoice_tool(self, order_id: int):
        """Generates an invoice for a given order ID using invoice_service."""
        return create_invoice(order_id)

    def send_email_tool(self, to_email: str, subject: str, body: str):
        """Sends an email using email_service."""
        return send_email(to_email, subject, body)

    def check_overdue_tool(self):
        """Checks for overdue invoices and sends reminders using scheduler logic."""
        return check_overdue_invoices()
