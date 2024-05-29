# Copyright (c) 2024, Hussain Nagaria and contributors
# For license information, please see license.txt

import frappe
import sqlite3

from frappe.model.document import Document


class SQLProblemSolution(Document):
	def before_save(self):
		self.check_solution()
	
	def check_solution(self):
		self.feedback = None

		problem_name = self.problem
		submitted_query = self.last_submitted_query
		correct_query, consider_order = frappe.db.get_value("SQL Problem", problem_name, ["correct_query", "consider_order"])
		
		db_path = self.get_data_set_path()
		db_uri = f"file:{db_path}?mode=ro" # https://docs.python.org/3/library/sqlite3.html#how-to-work-with-sqlite-uris
		con = sqlite3.connect(db_uri, uri=True)
		cur = con.cursor()

		cur.execute(correct_query)
		correct_output = cur.fetchall()

		try:
			cur.execute(submitted_query)
			student_output = cur.fetchall()
		except sqlite3.OperationalError as e:
			self.feedback = f"Problem with your query: <br>{frappe.bold(e)}"
			self.status = "Incorrect"
			return

		num_rows_student = len(student_output)
		num_rows_correct = len(correct_output)

		if num_rows_student != num_rows_correct:
			self.feedback = f"The number of rows returned are incorrect. Your query returns {frappe.bold(num_rows_student)} rows, while expected number of rows is {frappe.bold(num_rows_correct)}."
			self.status = "Incorrect"
			return
		
		num_columns_correct = 0
		num_columns_student = 0

		if num_rows_correct > 0:
			num_columns_correct = len(correct_output[0])
		
		if num_rows_student > 0:
			num_columns_student = len(student_output[0])

		if num_columns_student != num_columns_correct:
			self.feedback = f"The number of columns returned are incorrect. Your query returns {frappe.bold(num_columns_student)} columns, while expected number of columns is {frappe.bold(num_columns_correct)}."
			self.status = "Incorrect"
			return

		if consider_order:
			for i in range(num_rows_correct):
				for j in range(num_columns_correct):
					if student_output[i][j] != correct_output[i][j]:
						self.feedback = f"Incorrect Output on row {i+1}, column {j+1}."
						self.status = "Incorrect"
						return

		else:
			if set(student_output) != set(correct_output):
				self.feedback = "Incorrect output"
				self.status = "Incorrect"
				return

		self.status = "Correct"
	
	def get_data_set_path(self):
		problem_name = self.problem

		pset_name = frappe.db.get_value("SQL Problem", problem_name, "problem_set")

		data_set_url = frappe.db.get_value("SQL Problem Set", pset_name, "data_set")
		data_set_path = frappe.get_doc("File", {"file_url": data_set_url}).get_full_path()

		return data_set_path