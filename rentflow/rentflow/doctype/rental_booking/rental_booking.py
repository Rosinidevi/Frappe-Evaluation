import frappe
from frappe.model.document import Document
from frappe.utils import getdate
CONDITION_RANK = {"New": 0, "Good": 1, "Fair": 2, "Poor": 3, "Damaged": 4}
class RentalBooking(Document):

    def get_shop_name(self):
        settings = frappe.get_single("RentFlow Settings")
        return settings.shop_name

    def before_print(self, print_settings=None):
        self.print_summary = (
            f"{self.customer_name} - "
            f"{self.start_date} to {self.end_date}"
        )

    def validate(self):
        self.validate_dates()
        self.validate_overlaps()
        self.calculate_amounts()

    def validate_dates(self):
        if not self.start_date or not self.end_date:
            return
        if getdate(self.start_date) > getdate(self.end_date):
            frappe.throw("Start date cannot be after end date")

    def validate_overlaps(self):
        for item in self.items:
            if not item.equipment_unit:
                continue
            conflicts = frappe.db.sql(
                """
                select distinct rb.name from `tabRental Booking` rb
                inner join `tabBooking Item` bi on bi.parent = rb.name
                    and bi.parenttype = 'Rental Booking' and bi.parentfield = 'items'
                where rb.docstatus = 1
                    and rb.status not in ('Cancelled', 'Returned')
                    and rb.name != %(booking_name)s and bi.equipment_unit = %(equipment_unit)s
                    and rb.start_date <= %(end_date)s and rb.end_date >= %(start_date)s
                """,
                {
                    "booking_name": self.name,
                    "equipment_unit": item.equipment_unit,
                    "start_date": self.start_date,
                    "end_date": self.end_date
                },
                as_dict=True
            )
            if conflicts:
                frappe.throw(
                    f"Equipment Unit {item.equipment_unit} "
                    f"is already booked in {conflicts[0].name}"
                )

    def calculate_amounts(self):
        rental_total = 0
        damage_total = 0
        if not self.start_date or not self.end_date:
            self.rental_total = 0
            self.damage_total = 0
            self.final_amount = 0
            return
        start_date = getdate(self.start_date)
        end_date = getdate(self.end_date)
        line_days = (end_date - start_date).days + 1
        settings = frappe.get_single("RentFlow Settings")
        for item in self.items:
            item.line_days = line_days
            daily_rate = item.daily_rate or 0
            item.line_amount = daily_rate * line_days
            rental_total += item.line_amount
            item.damage_fee = 0
            if item.checkout_condition_grade and item.checkin_condition_grade:
                checkout_rank = CONDITION_RANK.get(item.checkout_condition_grade)
                checkin_rank = CONDITION_RANK.get(item.checkin_condition_grade)
                if (checkout_rank is not None and checkin_rank is not None and checkin_rank > checkout_rank):
                    rank_difference = checkin_rank - checkout_rank
                    item.damage_fee = settings.damage_fee_per_grade_drop * rank_difference
                    damage_total += item.damage_fee
        self.rental_total = rental_total
        self.damage_total = damage_total
        self.final_amount = rental_total + damage_total

    def before_submit(self):
        if self.status != "Confirmed":
            frappe.throw("Rental Booking can be submitted only when Status is Confirmed.")
        if (self.deposit_collected or 0) <= 0:
            frappe.throw("Deposit Collected must be greater than 0 before submission.")
        self.validate_overlaps()

    def on_submit(self):
        for item in self.items:
            if item.equipment_unit:
                frappe.db.set_value("Equipment Unit", item.equipment_unit, "current_status", "Reserved")
        self.create_rental_invoice()
        frappe.enqueue(
            method=send_booking_confirmation_email,
            booking_name=self.name,
            queue="short"
        )
        #webhook
        frappe.enqueue(
         "rentflow.api.send_webhook",
          booking_name=self.name,
          queue="short"
        )

    def create_rental_invoice(self):
        existing_invoice = frappe.db.exists(
            "Rental Invoice",
            {"rental_booking": self.name}
        )
        if existing_invoice:
            return
        invoice = frappe.get_doc({
            "doctype": "Rental Invoice",
            "rental_booking": self.name,
            "customer_name": self.customer_name,
            "invoice_date": getdate(),
            "rental_amount": self.rental_total,
            "damage_amount": self.damage_total,
            "total_amount": self.final_amount,
            "payment_status": "Unpaid"
        })
        invoice.insert(ignore_permissions=True)

    def on_cancel(self):
        self.status = "Cancelled"
        for item in self.items:
            if item.equipment_unit:
                frappe.db.set_value("Equipment Unit", item.equipment_unit, "current_status", "Available")
        invoice_name = frappe.db.get_value(
            "Rental Invoice",
            {"rental_booking": self.name},
            "name"
        )
        if invoice_name:
            invoice = frappe.get_doc("Rental Invoice", invoice_name)
            if invoice.payment_status == "Unpaid":
                if invoice.docstatus == 1:
                    invoice.cancel()
                elif invoice.docstatus == 0:
                    invoice.delete(ignore_permissions=True)

    # def on_trash(self):
    #     if self.status not in ("Cancelled", "Draft"):
    #         frappe.throw("Only Draft or Cancelled Rental Bookings can be deleted.")

def send_booking_confirmation_email(booking_name):
    booking = frappe.get_doc("Rental Booking", booking_name)
    if not booking.customer_email:
        return
    frappe.sendmail(
        recipients=[booking.customer_email],
        subject=f"Rental Booking {booking.name} Confirmed",
        message=f"""
            <h3>Rental Booking Confirmed</h3>
            <p>Booking: {booking.name}</p>
            <p>Customer: {booking.customer_name}</p>
            <p>Start Date: {booking.start_date}</p>
            <p>End Date: {booking.end_date}</p>
            <p>Rental Total: {booking.rental_total}</p>
            <p>Final Amount: {booking.final_amount}</p>
        """
    )
