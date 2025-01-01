app_name = "ff_assignment_portal"
app_title = "FF Assignment Portal"
app_publisher = "Hussain Nagaria"
app_description = "Assignment Checker Portal"
app_email = "hussain@frappe.io"
app_license = "APGL 3.0"

website_route_rules = [{'from_route': '/assignments-portal/<path:app_path>', 'to_route': 'assignments-portal'},]

export_python_type_annotations = True