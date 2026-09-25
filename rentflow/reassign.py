import frappe
@frappe.whitelist()
def reassign_bookings(from_staff, to_staff):
    try:
        frappe.db.sql(
            """
            update `tabRental Booking`
            set handled_by = %(to_staff)s
            where handled_by = %(from_staff)s
            and status NOT IN ('Cancelled', 'Closed')
            """,
            {
                "from_staff": from_staff,
                "to_staff": to_staff
            }
        )
        frappe.db.commit()
        return "Bookings reassigned successfully"
    except Exception:
        frappe.db.rollback()
        frappe.log_error(
            frappe.get_traceback(),
            "Rental Booking Reassignment Error"
        )

        raise