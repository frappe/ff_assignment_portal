import frappe


@frappe.whitelist()
def get_assignments_summary():
	"""Returns passed/failed for current user and each day"""
	summary = {}
	for day in range(1, 4):
		summary[f"day-{day}"] = has_passed_assignment(day)
	return summary


def has_passed_assignment(day):
	"""Returns passed/failed for current user and given day"""
	return bool(
		frappe.db.exists(
			"FF Assignment Submission",
			{
				"user": frappe.session.user,
				"day": day,
				"status": "Passed",
			},
		)
	)
