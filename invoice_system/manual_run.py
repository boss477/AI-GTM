from invoice_service import create_invoice
from scheduler import check_overdue_invoices
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manual_run.py create <order_id>")
        print("  python manual_run.py check")
        return

    command = sys.argv[1]

    if command == "create":
        if len(sys.argv) < 3:
            print("Please provide an order_id")
            return
        order_id = int(sys.argv[2])
        print(f"Creating invoice for order {order_id}...")
        result = create_invoice(order_id)
        print(result)

    elif command == "check":
        print("Checking overdue invoices...")
        check_overdue_invoices()
        print("Done.")

    else:
        print("Unknown command. Use 'create' or 'check'.")

if __name__ == "__main__":
    main()
