from agno.agent import Agent, RunResponse
from agno.utils.log import logger
from tools import InvoiceSystemTools
from agno.workflow import Workflow

# This Workflow acts as an interface that can orchestrate agents or just functions.
# For now, without LLM, we just use the methods directly.
class InvoiceSystemWorkflow(Workflow):
    description: str = "Manages invoices and reminders"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tools = InvoiceSystemTools()

    def create_invoice(self, order_id: int):
        logger.info(f"Starting invoice generation for order {order_id}")
        # Direct tool execution
        result = self.tools.generate_invoice_tool(order_id)
        logger.info(f"Invoice generation complete: {result}")
        return result

    def execute_overdue_check(self):
        logger.info("Starting overdue invoice check")
        self.tools.check_overdue_tool()
        logger.info("Overdue check complete")


# Instantiate the workflow (singleton-like usage here)
invoice_workflow = InvoiceSystemWorkflow()
