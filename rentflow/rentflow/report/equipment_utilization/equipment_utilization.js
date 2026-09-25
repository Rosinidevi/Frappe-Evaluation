frappe.query_reports["Equipment Utilization"] = {
    filters: [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            reqd: 1
        },
        {
            fieldname: "category",
            label: "Category",
            fieldtype: "Link",
            options: "Equipment Category"
        }
    ],
    formatter(value, row, column, data) {
        if (column.fieldname === "utilization_percent") {
            if (value < 30) {
                return `<span style="color:red">${value}%</span>`;
            }
            if (value >= 70) {
                return `<span style="color:green">${value}%</span>`;
            }
        }
        return value;
    }
};