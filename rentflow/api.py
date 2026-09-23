import frappe
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