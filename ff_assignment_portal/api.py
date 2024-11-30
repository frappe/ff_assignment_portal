import frappe

from mimetypes import guess_type
from frappe.utils import cint


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


@frappe.whitelist()
def get_solution_status(problem):
	current_user = frappe.session.user
	already_attempted = frappe.db.exists(
		"SQL Problem Solution", {"problem": problem, "student": current_user}
	)

	summary = frappe._dict({"status": "Not Attempted"})

	if already_attempted:
		attempt_name = already_attempted
		status, last_submitted_query, feedback = frappe.db.get_value(
			"SQL Problem Solution",
			attempt_name,
			["status", "last_submitted_query", "feedback"],
		)
		summary.status = status
		summary.last_submitted_query = last_submitted_query
		summary.feedback = feedback

	return summary


@frappe.whitelist()
def submit_sql_solution(problem, solution):
	current_user = frappe.session.user
	already_attempted = frappe.db.exists(
		"SQL Problem Solution", {"problem": problem, "student": current_user}
	)

	if already_attempted:
		attempt_name = already_attempted
		solution_doc = frappe.get_doc("SQL Problem Solution", attempt_name)
	else:
		solution_doc = frappe.new_doc("SQL Problem Solution")
		solution_doc.student = current_user
		solution_doc.problem = problem

	solution_doc.last_submitted_query = solution
	solution_doc.save(ignore_permissions=True)

	return solution_doc
