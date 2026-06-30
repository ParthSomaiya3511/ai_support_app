# docs_store.py

DOCUMENTATION = {
    "refund_policy": (
        "Our standard refund policy allows customers to request a full refund within 30 days of purchase. "
        "Refunds usually take 5 to 10 business days to clear and show up on your statement."
    ),
    "shipping_details": (
        "We offer standard shipping (3-5 business days) and express shipping (1-2 business days). "
        "International shipping is available, but delivery times vary based on custom checks and regional carriers."
    ),
    "account_reset": (
        "To reset your account password, navigate to the login page and click 'Forgot Password'. "
        "An email containing a secure password reset link will be sent to your registered address within 5 minutes."
    ),
    "pricing_plans": (
        "We offer three subscription tiers: Basic ($10/month), Pro ($30/month), and Enterprise (custom pricing). "
        "Selecting an annual payment cycle discounts your subscription costs by 20%."
    )
}

def get_all_docs() -> str:
    formatted_docs = []
    for category, content in DOCUMENTATION.items():
        formatted_docs.append(f"Category: {category.replace('_', ' ').title()}\nContent: {content}\n")
    return "\n---\n".join(formatted_docs)