import frappe
def show_booking_staff():
    bookings = frappe.get_list(
        "Rental Booking",
        fields=["name", "handled_by"],
        limit_page_length=0
    )
    staff_names = list({
        booking.handled_by
        for booking in bookings
        if booking.handled_by
    })
    staff_list = frappe.get_list(
        "Yard Staff",
        filters={"name": ["in", staff_names]},
        fields=["name", "staff_name", "phone"],
        limit_page_length=0
    )
    staff_map = {
        staff.name: staff
        for staff in staff_list
    }
    for booking in bookings:
        staff = staff_map.get(booking.handled_by)
        if staff:
            print(
                booking.name,
                staff.staff_name,
                staff.phone
            )