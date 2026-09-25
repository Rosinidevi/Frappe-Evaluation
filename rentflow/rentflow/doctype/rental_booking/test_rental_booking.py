import frappe
from frappe.tests.utils import FrappeTestCase
class TestRentalBooking(FrappeTestCase):
    def setUp(self):
        pass
    def test_category_factory(self):
        category = make_category()
        self.assertEqual(category.category_name,"Test Generator")
        self.assertEqual(category.daily_rate,1000)
        self.assertEqual(category.deposit_amount,5000)
def make_category(**kwargs):
    data = {
        "doctype": "Equipment Category",
        "category_name": "Test Generator",
        "description": "Test category",
        "daily_rate": 1000,
        "deposit_amount": 5000
    }
    data.update(kwargs)
    return frappe.get_doc(data).insert(ignore_permissions=True)
def make_staff(**kwargs):
    data = {
        "doctype": "Yard Staff",
        "staff_name": "Test Staff",
        "employee_id": "TEST-001",
        "phone": "9876543210",
        "email": "teststaff@example.com",
        "role": "Inspector",
        "status": "Active"
    }
    data.update(kwargs)
    return frappe.get_doc(data).insert(ignore_permissions=True)
def make_equipment_unit(category=None, **kwargs):
    if not category:
        category = make_category()
    data = {
        "doctype": "Equipment Unit",
        "unit_code": "TEST-001",
        "category": category.name,
        "condition_grade": "New",
        "current_status": "Available",
        "purchase_value": 10000,
        "is_active": 1
    }
    data.update(kwargs)
    return frappe.get_doc(data).insert(ignore_permissions=True)
def make_rental_booking(equipment_unit=None,staff=None,**kwargs):
    if not equipment_unit:
        equipment_unit = make_equipment_unit()
    if not staff:
        staff = make_staff()
    data = {
        "doctype": "Rental Booking",
        "customer_name": "Test Customer",
        "customer_phone": "9876500000",
        "customer_email": "customer@example.com",
        "start_date": "2026-09-25",
        "end_date": "2026-09-26",
        "purpose": "Test Rental",
        "handled_by": staff.name,
        "deposit_collected": 1000,
        "payment_status": "Unpaid",
        "status": "Draft",
        "items": [
            {
                "doctype": "Booking Item",
                "equipment_unit": equipment_unit.name,
                "category": equipment_unit.category,
                "daily_rate": 1000,
                "checkout_condition_grade": "New",
                "checkin_condition_grade": "New"
            }
        ]
    }
    data.update(kwargs)
    return frappe.get_doc(data).insert(ignore_permissions=True)