# Copyright (c) 2024, Hussain Nagaria and contributors
# For license information, please see license.txt

import frappe

import sqlite3

from frappe.model.document import Document


class SQLProblemSolution(Document):
	def before_save(self):
		self.check_solution()
		if not self.feedback:
			self.status = "Correct"
	
	def check_solution(self):
		self.feedback = None

		problem_name = self.problem
		submitted_query = self.last_submitted_query
		pset_name, correct_query, consider_order = frappe.db.get_value("SQL Problem", problem_name, ["problem_set", "correct_query", "consider_order"])

		data_set_file = frappe.db.get_value("SQL Problem Set", pset_name, "data_set")
		data_set_file = frappe.get_doc("File", {"file_url": data_set_file}).get_full_path()

		con = sqlite3.connect(data_set_file)
		cur = con.cursor()

		cur.execute(correct_query)
		correct_output = list(cur)

		try:
			cur.execute(submitted_query)
			student_output = list(cur)
		except sqlite3.OperationalError as e:
			self.feedback = f"Problem with your query: <br>{frappe.bold(e)}"
			self.status = "Incorrect"
			return


		print(correct_output)
		print(student_output)

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
