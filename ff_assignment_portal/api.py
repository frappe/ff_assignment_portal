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
		
		if content_type not in ("application/zip", "video/mp4"):
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
