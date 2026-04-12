from unified_toolkit import UnifiedToolkit
import logging

logging.basicConfig(level=logging.INFO)
toolkit = UnifiedToolkit()

print("Testing robust invoice creation tool...")
# We'll simulate a call to create_telegram_invoice
# Since we can't easily send a real photo here, we'll just check if the logic runs
# and handles the DB interactions.

test_url = "https://example.com/test_chair.jpg"
test_price = 9999

print(f"Attempting to create invoice for ${test_price} with URL {test_url}")
try:
    result = toolkit.create_telegram_invoice(test_url, test_price)
    if isinstance(result, dict) and "invoice_number" in result:
        print(f"SUCCESS! Created invoice: {result['invoice_number']}")
        print(f"Auto-assigned ID was likely handled correctly.")
    else:
        print(f"Result: {result}")
except Exception as e:
    print(f"FAILED with error: {e}")
