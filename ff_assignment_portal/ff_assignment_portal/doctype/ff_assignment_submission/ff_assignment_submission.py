# Copyright (c) 2023, Hussain Nagaria and contributors
# For license information, please see license.txt

import json
import frappe
import zipfile

from frappe.model.document import Document

doctype_check_parameters_map = {
	"Flight Passenger": {
		"field_type_counts": {"Data": 2, "Date": 1},
		"naming_rule_type": "Autoincrement",
	},
	"Airline": {
		"num_fields": 3,
		"num_mandatory": 2,
		"field_type_counts": {"Int": 1, "Data": 2},
		"validate_connections": True,
		"expected_num_connections": 1,
		"expected_connection_doctypes": ["Airplane"],
	},
	"Airplane": {
		"num_fields": 3,
		"num_mandatory": 3,
		"field_type_counts": {"Int": 1, "Link": 1, "Data": 1},
	},
	"Airplane Ticket": {
		"field_type_counts": {"Date": 1, "Time": 1, "Duration": 1, "Link": 5},
		"checked_doctype_flags": (
			("is_submittable", "Submittable"),
			("track_changes", "Tracking Changes"),
		),
		"num_document_states": 3,
		"fetched_fields": {"Airplane": 2},
	},
}


class FFAssignmentSubmission(Document):
	def validate(self):
		if not self.submission.endswith(".zip"):
			frappe.throw("Please upload a zip file.")

	def run_checks(self):
		if not self.day == "1":
			# TODO: Implement checks for day 2 and 3
			return

		all_problems = []  # to store all the problems
		filename_with_contents = self.get_filename_with_contents()

		# number of files must be 4
		num_files = len(list(filename_with_contents))
		if num_files != 4:
			all_problems.append(
				f"There must be exactly 4 files in the zip file, found {num_files}."
			)

		for filename, file_json in filename_with_contents:
			submission_doctype_json = SubmissionDocTypeJSON(
				filename, file_json, **doctype_check_parameters_map.get(filename, {})
			)
			problems = submission_doctype_json.run_checks()
			if problems:
				all_problems.extend(problems)

		if all_problems:
			self.status = "Failed"
			self.feedback = "\n".join(all_problems)
		else:
			self.status = "Passed"
			self.feedback = "All checks passed 🎉"

		self.save()

	def get_filename_with_contents(self):
		file_doc = frappe.get_doc("File", {"file_url": self.submission})

		with zipfile.ZipFile(file_doc.get_full_path()) as zip_file:
			for file_name in zip_file.namelist():
				print(file_name)

				# ignore files that contain __MACOSX and .DS_Store
				if "__MACOSX" in file_name or ".DS_Store" in file_name:
					continue

				if file_name.endswith(".json"):
					file_json = json.loads(zip_file.read(file_name).decode("utf-8"))
					file_name = file_name.split("/")[-1]
					yield file_name, file_json


class SubmissionDocTypeJSON:
	def __init__(
		self,
		filename,
		doctype_meta,
		num_fields=None,
		num_mandatory=None,
		field_type_counts=None,
		naming_rule_type=None,
		validate_connections=False,
		expected_num_connections=None,
		expected_connection_doctypes=None,
		checked_doctype_flags=None,
		num_document_states=None,
		fetched_fields=None,
	):
		self.filename = filename
		self.doctype_meta = doctype_meta
		self.problems = []

		# check parameters
		self.num_fields = num_fields
		self.num_mandatory = num_mandatory
		self.field_type_counts = field_type_counts
		self.naming_rule_type = naming_rule_type
		self.validate_connections = validate_connections
		self.expected_num_connections = expected_num_connections
		self.expected_connection_doctypes = expected_connection_doctypes
		self.checked_doctype_flags = checked_doctype_flags
		self.num_document_states = num_document_states
		self.fetched_fields = fetched_fields

	def validate_num_fields(self, expected_num_fields):
		fields = self.doctype_meta["fields"]

		# ignore meta fields
		meta_field_types = ("Column Break", "Section Break", "Tab Break")

		filtered_fields = []
		for field in fields:
			if field["fieldtype"] not in meta_field_types:
				filtered_fields.append(field)

		num = len(filtered_fields)

		if num != expected_num_fields:
			self.problems.append(
				f"{self.doctype_meta['name']} DocType must contain {expected_num_fields} fields, but found {num}"
			)

	def validate_num_mandatory(self, expected_num_mandatory):
		num = 0
		fields = self.doctype_meta["fields"]
		for field in fields:
			if field.get("reqd", 0) == 1:
				num = num + 1
		if num != expected_num_mandatory:
			self.problems.append(
				f"There must be exactly {expected_num_mandatory} mandatory fields in {self.doctype_meta['name']}, but found {num}"
			)

	def validate_field_type_counts(self, expected_count_map):
		fields = self.doctype_meta["fields"]
		actual_count_map = {}
		for field in fields:
			fieldtype = field["fieldtype"]
			if fieldtype in actual_count_map:
				actual_count_map[fieldtype] = actual_count_map[fieldtype] + 1
			else:
				actual_count_map[fieldtype] = 1

		for t in expected_count_map:
			expected_count = expected_count_map[t]
			if t not in actual_count_map:
				self.problems.append(
					f"{self.doctype_meta['name']} must have exactly {expected_count} `{t}` fields, but found 0"
				)
			elif actual_count_map[t] != expected_count_map[t]:
				actual_count = actual_count_map[t]
				self.problems.append(
					f"{self.doctype_meta['name']} must have exactly {expected_count} `{t}` fields, but found {actual_count}"
				)

	def validate_naming_rule_type(self, naming_rule_type):
		if not self.doctype_meta.get("naming_rule") == naming_rule_type:
			self.problems.append(f"{self.doctype} naming rule should be {naming_rule_type}")

	def validate_connections(self, expected_num_connections, expected_connection_doctypes):
		links = self.doctype_meta.get("links", [])

		if len(links) != expected_num_connections:
			self.problems.append(
				f"Expected {expected_num_connections} connections in {self.doctype}, but found {len(links)}"
			)

		doctypes = [link["link_doctype"] for link in links]
		for dt in expected_connection_doctypes:
			if dt not in doctypes:
				self.problems.append(
					f"Connection/Link in `{self.doctype}` DocType does not exist for `{dt}`"
				)

	def validate_doctype_flags(self):
		for flag, summary in self.checked_doctype_flags:
			if not self.doctype_meta.get(flag, 0) == 1:
				self.problems.append(f"{self.doctype} DocType must be {summary}.")

	def validate_document_states(self):
		states = self.doctype_meta.get("states", [])
		if len(states) < self.num_document_states:
			self.problems.append(
				f"At least {self.num_document_states} Document States not defined in {self.doctype} doctype."
			)

	def validate_fetched_fields(self):
		fields = self.doctype_meta["fields"]

		for doctype, num_fields in self.fetched_fields.items():
			fetched_fields_count = 0
			for field in fields:
				if field.get("fetch_from", "") == doctype:
					fetched_fields_count = fetched_fields_count + 1

			if fetched_fields_count != num_fields:
				self.problems.append(
					f"Exactly {num_fields} fields must be fetched from {doctype} into {self.doctype} DocType."
				)

	@property
	def doctype(self):
		if "passenger" in self.filename:
			return "Flight Passenger"

		if "airline" in self.filename:
			return "Airline"

		if "airplane_ticket" in self.filename:
			return "Airplane Ticket"

		if "airplane" in self.filename:
			return "Airplane"

		return None

	def run_checks(self):
		if self.num_fields:
			self.validate_num_fields(self.num_fields)

		if self.num_mandatory:
			self.validate_num_mandatory(self.num_mandatory)

		if self.field_type_counts:
			self.validate_field_type_counts(self.field_type_counts)

		if self.naming_rule_type:
			self.validate_naming_rule_type(self.naming_rule_type)

		if self.validate_connections:
			self.validate_connections(
				self.expected_num_connections, self.expected_connection_doctypes
			)

		if self.checked_doctype_flags:
			self.validate_doctype_flags()

		if self.num_document_states:
			self.validate_document_states()

		if self.fetched_fields:
			self.validate_fetched_fields()

		return self.problems


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
