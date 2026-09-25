import frappe
from frappe.utils import getdate
def execute(filters=None):
    filters = filters or {}
    from_date = getdate(filters.get("from_date"))
    to_date = getdate(filters.get("to_date"))
    category = filters.get("category")
    if not from_date or not to_date:
        frappe.throw("From Date and To Date are required.")
    if from_date > to_date:
        frappe.throw("From Date cannot be after To Date.")
    category_filters = {}
    if category:
        category_filters["name"] = category
    categories = frappe.get_list(
        "Equipment Category",
        filters=category_filters,
        fields=["name", "category_name"],
        limit_page_length=0
    )
    unit_filters = {
        "is_active": 1
    }
    if category:
        unit_filters["category"] = category
    units = frappe.get_list(
        "Equipment Unit",
        filters=unit_filters,
        fields=["name", "category"],
        limit_page_length=0
    )
    unit_count = {}
    for unit in units:
        unit_count[unit.category] = (
            unit_count.get(unit.category, 0) + 1
        )
    bookings = frappe.get_list(
        "Rental Booking",
        filters={
            "docstatus": 1,
            "start_date": ["<=", to_date],
            "end_date": [">=", from_date]
        },
        fields=["name", "start_date", "end_date"],
        limit_page_length=0
    )
    booking_names = [booking.name for booking in bookings]
    items = []
    if booking_names:
        items = frappe.get_list(
            "Booking Item",
            filters={
                "parent": ["in", booking_names],
                "parenttype": "Rental Booking",
                "parentfield": "items"
            },
            fields=[
                "parent",
                "equipment_unit",
                "category",
                "daily_rate",
                "damage_fee"
            ],
            parent_doctype="Rental Booking",
            limit_page_length=0
        )
    booking_map = {
        booking.name: booking
        for booking in bookings
    }
    data = []
    for cat in categories:
        days_rented = 0
        revenue = 0
        damage_incidents = 0
        for item in items:
            if item.category != cat.name:
                continue
            booking = booking_map.get(item.parent)
            if not booking:
                continue
            start = max(getdate(booking.start_date),from_date)
            end = min(getdate(booking.end_date),to_date)
            if start > end:
                continue
            days = (end - start).days + 1
            days_rented += days
            revenue += (item.daily_rate or 0) * days
            if (item.damage_fee or 0) > 0:
                damage_incidents += 1
        total_units = unit_count.get(cat.name, 0)
        period_days = (to_date - from_date).days + 1
        capacity = total_units * period_days
        utilization = 0
        if capacity:
            utilization = (days_rented / capacity) * 100
        data.append({
            "category": cat.name,
            "total_units": total_units,
            "days_rented": days_rented,
            "utilization_percent": round(utilization, 2),
            "revenue": revenue,
            "damage_incidents": damage_incidents
        })
    columns = [
        {
            "fieldname": "category",
            "label": "Category",
            "fieldtype": "Link",
            "options": "Equipment Category"
        },
        {
            "fieldname": "total_units",
            "label": "Total Units",
            "fieldtype": "Int"
        },
        {
            "fieldname": "days_rented",
            "label": "Days Rented",
            "fieldtype": "Int"
        },
        {
            "fieldname": "utilization_percent",
            "label": "Utilization %",
            "fieldtype": "Percent"
        },
        {
            "fieldname": "revenue",
            "label": "Revenue",
            "fieldtype": "Currency"
        },
        {
            "fieldname": "damage_incidents",
            "label": "Damage Incidents",
            "fieldtype": "Int"
        }
    ]
    total_revenue = sum(
        row["revenue"] for row in data
    )
    total_damage = sum(
        row["damage_incidents"] for row in data
    )
    most_utilized = "-"
    if data:
        highest = max(row["utilization_percent"]for row in data)
        if highest > 0:
            most_utilized = max(data,key=lambda row: row["utilization_percent"])["category"]
    chart = {
        "data": {
            "labels": [
                row["category"]
                for row in data
            ],
            "datasets": [
                {
                    "name": "Revenue",
                    "values": [
                        row["revenue"]
                        for row in data
                    ]
                },
                {
                    "name": "Damage Incidents",
                    "values": [
                        row["damage_incidents"]
                        for row in data
                    ]
                }
            ]
        },
        "type": "bar"
    }
    report_summary = [
        {
            "label": "Total Revenue",
            "value": total_revenue,
            "datatype": "Currency"
        },
        {
            "label": "Total Damage Incidents",
            "value": total_damage,
            "datatype": "Int"
        },
        {
            "label": "Most Utilized Category",
            "value": most_utilized,
            "datatype": "Data"
        }
    ]
    return columns, data, None, chart, report_summary