import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class EquipmentUnit(Document):
    def autoname(self):
        # if not self.category:
        #     frappe.throw("Category is required")
        category_name = frappe.db.get_value(
            "Equipment Category",
            self.category,
            "category_name"
        )
        prefix = category_name[:3].upper()
        self.name = make_autoname(f"{prefix}-.#####")
    def on_update(self):
        threshold = frappe.db.get_value(
            "RentFlow Settings",
            None,
            "low_availability_threshold"
        )
        frappe.msgprint(
            f"Low availability threshold: {threshold}"
        )