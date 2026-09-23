import frappe
def rental_booking_query(user=None):
    if not user:
        user = frappe.session.user
    roles = frappe.get_roles(user)
    if "RF Manager" in roles:
        return ""
    if "RF Inspector" in roles:
        staff = frappe.db.get_value("Yard Staff",{"user": user},"name")
        if not staff:
            return "1 = 0"
        staff = frappe.db.escape(staff)
        return f"""
            `tabRental Booking`.`handled_by` = {staff}
        """
    return "1 = 0"