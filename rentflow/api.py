import frappe
from frappe.query_builder import DocType
from frappe.utils import today
def get_overdue_returns():
    RB = DocType("Rental Booking")
    result = (frappe.qb.from_(RB)
        .select(
            RB.name,
            RB.customer_name,
            RB.end_date
        )
        .where((RB.status == "Checked Out")&(RB.end_date < today()))
        .orderby(RB.end_date)
        .run(as_dict=True)
    )
    return result

@frappe.whitelist()
def share_booking(booking_name, user_email):
    if not frappe.db.exists("Rental Booking", booking_name):
        frappe.throw("Rental Booking not found")
    if not frappe.db.exists("User", user_email):
        frappe.throw("User not found")
    frappe.share.add(
        "Rental Booking",
        booking_name,
        user_email,
        read=1
    )
    return {
        "message": "Booking shared successfully",
        "booking": booking_name,
        "user": user_email
    }

@frappe.whitelist()
def rename_yard_staff(old_name, new_name):
    return frappe.rename_doc(
        "Yard Staff",
        old_name,
        new_name,
        merge=False
    )
@frappe.whitelist()
def transfer_handler(booking_name, handled_by):
    booking = frappe.get_doc(
        "Rental Booking",
        booking_name
    )
    booking.handled_by = handled_by
    booking.save()

    return "Handler transferred successfully"
#webhook
def send_webhook(booking_name):
    import requests
    settings = frappe.get_single("RentFlow Settings")
    if not settings.webhook_url:
        return
    doc = frappe.get_doc("Rental Booking",booking_name)
    payload = {
        "event": "booking_confirmed",
        "booking": doc.name,
        "amount": doc.final_amount
    }
    try:
        r = requests.post(settings.webhook_url,json=payload,timeout=5)
        r.raise_for_status()
        frappe.logger("rentflow").info(f"Webhook sent successfully for {doc.name}")
    except Exception as e:
        frappe.log_error(f"Webhook failed: {e}","Webhook Error")