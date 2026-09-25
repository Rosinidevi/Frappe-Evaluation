import frappe
def after_install():

    categories = [
        {
            "category_name": "Power Drill",
            "description": "Heavy-duty electric power drill",
            "daily_rate": 500,
            "deposit_amount": 2000
        },
        {
            "category_name": "Generator",
            "description": "Portable diesel generator",
            "daily_rate": 1000,
            "deposit_amount": 5000
        },
        {
            "category_name": "Scaffold Tower Set",
            "description": "Mobile scaffold tower set",
            "daily_rate": 1500,
            "deposit_amount": 7500
        }
    ]
    for category in categories:
        if not frappe.db.exists("Equipment Category",category["category_name"]):
            doc = frappe.get_doc({"doctype": "Equipment Category",**category})
            doc.insert(ignore_permissions=True)
    settings=frappe.get_single("RentFlow Settings")
    settings.shop_name="Anchor Point Equipment Rentals"
    settings.manager_email="manager@anchorpoint.com"
    settings.default_deposit_percent=20
    settings.damage_fee_per_grade_drop=500
    settings.late_fee_per_day=100
    settings.low_availability_alert_enabled=1
    settings.save(ignore_permissions=True)
    frappe.msgprint("RentFlow installed successfully")

