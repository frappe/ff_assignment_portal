# Copyright (c) 2024, Hussain Nagaria and contributors
# For license information, please see license.txt

import frappe
import sqlite3

from frappe.model.document import Document


class SQLProblemSolution(Document):
	def before_save(self):
		self.run_check()

	def run_check(self) -> None:
		self.feedback = None
		self.set_problem_data()
		self.set_correct_output()

		try:
			cur = self.get_db_cursor()
			submitted_query = self.last_submitted_query
			cur.execute(submitted_query)
			self.student_output = cur.fetchall()
		except sqlite3.OperationalError as e:
			self.feedback = f"Problem with your query: <br>{frappe.bold(e)}"
			self.status = "Incorrect"
			return

		if (
			self.column_count_match()
			and self.row_count_match()
			and self.row_data_match()
		):
			self.status = "Correct"
		else:
			self.status = "Incorrect"

	def set_problem_data(self):
		problem_name = self.problem
		self.problem_data = frappe.db.get_value(
			"SQL Problem",
			problem_name,
			["correct_query", "consider_order", "problem_set"],
			as_dict=True,
		)

	def set_correct_output(self):
		cur = self.get_db_cursor()
		cur.execute(self.problem_data.correct_query)
		self.correct_output = cur.fetchall()

	def get_db_cursor(self):
		if hasattr(self, "db_cursor"):
			return self.db_cursor

		db_path = self.get_data_set_path()
		db_uri = (
			f"file:{db_path}?mode=ro"
		)  # https://docs.python.org/3/library/sqlite3.html#how-to-work-with-sqlite-uris
		con = sqlite3.connect(db_uri, uri=True)
		self.db_cursor = con.cursor()
		return self.db_cursor

	def get_data_set_path(self) -> str:
		pset_name = self.problem_data.problem_set

		data_set_url = frappe.db.get_value("SQL Problem Set", pset_name, "data_set")
		data_set_path = frappe.get_doc(
			"File", {"file_url": data_set_url}
		).get_full_path()

		return data_set_path

	def column_count_match(self) -> bool:
		num_columns_student = get_num_columns(self.student_output)
		num_columns_correct = get_num_columns(self.correct_output)

		if num_columns_student != num_columns_correct:
			self.feedback = f"The number of columns returned are incorrect. Your query returns {frappe.bold(num_columns_student)} columns, while expected number of columns is {frappe.bold(num_columns_correct)}."
			return False

		return True

	def row_count_match(self) -> bool:
		num_rows_student = len(self.student_output)
		num_rows_correct = len(self.correct_output)

		if num_rows_student != num_rows_correct:
			self.feedback = f"The number of rows returned are incorrect. Your query returns {frappe.bold(num_rows_student)} rows, while expected number of rows is {frappe.bold(num_rows_correct)}."
			return False

		return True

	def row_data_match(self) -> bool:
		num_rows_correct = len(self.correct_output)
		num_columns_correct = get_num_columns(self.correct_output)

		if self.problem_data.consider_order:
			for i in range(num_rows_correct):
				for j in range(num_columns_correct):
					student_cell_data = self.student_output[i][j]
					correct_cell_data = self.correct_output[i][j]
					if student_cell_data != correct_cell_data:
						self.feedback = f"Incorrect Output on row {i+1}, column {j+1}. <br> Expected: {frappe.bold(correct_cell_data)}, Got: {frappe.bold(student_cell_data)}"
						return False

		else:
			if set(self.student_output) != set(self.correct_output):
				self.feedback = "Incorrect output"
				return False

		return True


def get_num_columns(output: list) -> int:
	num_columns = 0
	num_rows = len(output)

	if num_rows > 0:
		num_columns = len(output[0])

	return num_columns
