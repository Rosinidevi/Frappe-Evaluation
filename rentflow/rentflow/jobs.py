import frappe
from frappe.utils import today, now_datetime
def flag_overdue_returns():
    last_run = frappe.db.get_value(
        "Audit Log",
        {
            "action": "overdue_check",
            "date": today()
        },
        "name"
    )
    if last_run:
        return
    bookings = frappe.get_list(
        "Rental Booking",
        filters={
            "status": "Checked Out",
            "end_date": ["<", today()]
        },
        fields=["name", "customer_name", "end_date"],
        limit_page_length=0
    )
    for booking in bookings:
        log = frappe.get_doc({
            "doctype": "Audit Log",
            "doctype_name": "Rental Booking",
            "document_name": booking.name,
            "action": "overdue_return",
            "user": frappe.session.user,
            "timestamp": now_datetime(),
            "date": today()
        })
        log.insert(ignore_permissions=True)
    sentinel = frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": "Rental Booking",
        "document_name": "DAILY_JOB",
        "action": "overdue_check",
        "user": frappe.session.user,
        "timestamp": now_datetime(),
        "date": today()
    })
    sentinel.insert(ignore_permissions=True)