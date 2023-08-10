# Copyright (c) 2023, Hussain Nagaria and contributors
# For license information, please see license.txt

import json
import frappe
import zipfile
from frappe.model.document import Document


class FFAssignmentSubmission(Document):
	def validate(self):
		if not self.submission.endswith(".zip"):
			frappe.throw("Please upload a zip file.")

	def run_checks(self):
		self.status = "Passed"
		self.feedback = "You have <strong>failed</strong> the assignment."
		self.save()

	def get_filename_with_contents(self):
		file_doc = frappe.get_doc("File", {"file_url": self.submission})

		with zipfile.ZipFile(file_doc.get_full_path()) as zip_file:
			for file_name in zip_file.namelist():
				if file_name.endswith(".json"):
					file_json = json.loads(zip_file.read(file_name).decode("utf-8"))
					file_name =  file_name.split("/")[-1]
					yield file_name, file_json


@frappe.whitelist()
def submit_assignment(day, file):
	submission_doc = frappe.new_doc("FF Assignment Submission")
	submission_doc.user = frappe.session.user
	submission_doc.submission = file.get("file_url")
	submission_doc.day = day
	submission_doc.insert()

	# If day 1, run the checks now
	if day == "1":
		submission_doc.run_checks()
