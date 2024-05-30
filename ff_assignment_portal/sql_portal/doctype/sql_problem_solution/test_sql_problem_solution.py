# Copyright (c) 2024, Hussain Nagaria and Contributors
# See license.txt


import frappe

from pathlib import Path


from frappe.tests.utils import FrappeTestCase


class TestSQLProblemSolution(FrappeTestCase):
	def setUp(self):
		test_pset = frappe.new_doc("SQL Problem Set")
		test_pset.name = "test-pset"

		test_db_path = Path(frappe.get_app_path("ff_assignment_portal")) / "test.db"
		file_doc = frappe.get_doc(
			{
				"doctype": "File",
				"file_name": "test_db",
				"content": open(test_db_path, "rb").read(),
			}
		).insert()
		data_set_path = file_doc.file_url

		test_pset.data_set = data_set_path
		test_pset.insert(ignore_if_duplicate=True)

		self.test_pset = test_pset

	def test_column_mismatch(self):
		CORRECT_QUERY = "SELECT ID From testTable"
		INCORRECT_QUERY = "SELECT * FROM testTable"
		test_problem = self.create_problem_with_correct_query(CORRECT_QUERY)

		test_solution = self.create_solution(test_problem.name, INCORRECT_QUERY)
		self.assertEqual(test_solution.status, "Incorrect")

		test_solution = self.create_solution(test_problem.name, CORRECT_QUERY)
		self.assertEqual(test_solution.status, "Correct")

	def test_row_mismatch(self):
		CORRECT_QUERY = "SELECT * FROM testTable LIMIT 1"
		INCORRECT_QUERY = "SELECT * FROM testTable"

		test_problem = self.create_problem_with_correct_query(CORRECT_QUERY)

		test_solution = self.create_solution(test_problem.name, INCORRECT_QUERY)
		self.assertEqual(test_solution.status, "Incorrect")

		test_solution = self.create_solution(test_problem.name, CORRECT_QUERY)
		self.assertEqual(test_solution.status, "Correct")

	def create_problem_with_correct_query(self, query: str):
		return frappe.get_doc(
			{
				"doctype": "SQL Problem",
				"problem_set": self.test_pset.name,
				"correct_query": query,
			}
		).insert()

	def create_solution(self, problem_name: str, query: str):
		return frappe.get_doc(
			{
				"doctype": "SQL Problem Solution",
				"student": "Administrator",
				"problem": problem_name,
				"last_submitted_query": query,
			}
		).insert()

	def test_data_mismatch(self):
		pass

	def test_sql_query_error(self):
		test_problem = self.create_problem_with_correct_query("SELECT * FROM testTable")
		test_solution = self.create_solution(
			test_problem.name, "SELECT COLUMN_THAT_DOES_NOT_EXIST FROM testTable"
		)
		self.assertEqual(test_solution.status, "Incorrect")

	def test_prevents_write_queries(self):
		DANGER_WRITE_QUERY = "DROP TABLE testTable"

		test_problem = self.create_problem_with_correct_query("SELECT * FROM testTable")
		test_solution = self.create_solution(test_problem.name, DANGER_WRITE_QUERY)
		self.assertEqual(test_solution.status, "Incorrect")
		self.assertIn("attempt to write a readonly database", test_solution.feedback)
