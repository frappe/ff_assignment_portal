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
def upload_assignment_submission():
	"""Handles zip file upload for assignment submission"""
	files = frappe.request.files
	is_private = frappe.form_dict.is_private
	doctype = frappe.form_dict.doctype
	docname = frappe.form_dict.docname
	fieldname = frappe.form_dict.fieldname
	file_url = frappe.form_dict.file_url
	folder = frappe.form_dict.folder or "Home"
	filename = frappe.form_dict.file_name
	content = None

	if "file" in files:
		file = files["file"]
		content = file.stream.read()
		filename = file.filename

		content_type = guess_type(filename)[0]

		if content_type not in ("application/zip", "video/mp4", "video/quicktime"):
			if "video" in content_type:
				frappe.throw(f"Only {frappe.bold('mp4')} or {frappe.bold('mov')} files supported for videos.")
			else:	 
				frappe.throw("Only zip files are allowed")

	frappe.local.uploaded_file = content
	frappe.local.uploaded_filename = filename

	return frappe.get_doc(
		{
			"doctype": "File",
			"attached_to_doctype": doctype,
			"attached_to_name": docname,
			"attached_to_field": fieldname,
			"folder": folder,
			"file_name": filename,
			"file_url": file_url,
			"is_private": cint(is_private),
			"content": content,
		}
	).save(ignore_permissions=True)


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
