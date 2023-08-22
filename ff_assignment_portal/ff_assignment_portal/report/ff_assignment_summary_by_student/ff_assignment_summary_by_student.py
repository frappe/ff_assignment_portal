# Copyright (c) 2023, Hussain Nagaria and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	return get_columns(), get_data(filters)


def get_data(filters=None):
	data = []
	students = frappe.get_all(
		"FF Assignment Submission",
		fields=["user", "user.full_name"],
		group_by="user",
		order_by="full_name",
	)

	for student in students:
		data.append(
			{
				"full_name": student.full_name,
				"user": student.user,
				"day_1": status_for_day(student.user, "1"),
				"day_2": status_for_day(student.user, "2"),
				"day_3": status_for_day(student.user, "3"),
			}
		)

	for row in data:
		total_submitted = 0
		total_passed = 0

		for day in ("1", "2", "3"):
			status = row[f"day_{day}"]
			if has_passed(status):
				total_passed = total_passed + 1
				total_submitted = total_submitted + 1
				continue

			if has_submitted(status):
				total_submitted = total_submitted + 1

		row["submitted_summary"] = f"{total_submitted} / 3"
		row["passed_summary"] = f"{total_passed} / 3"

	return data


def get_columns():
	return [
		{
			"fieldname": "full_name",
			"label": "Student Name",
			"fieldtype": "Data",
			"width": 250,
		},
		{
			"fieldname": "user",
			"label": "User",
			"fieldtype": "Link",
			"options": "User",
			"width": 250,
		},
		{
			"fieldname": "day_1",
			"label": "Day 1",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"fieldname": "day_2",
			"label": "Day 2",
			"fieldtype": "Data",
		},
		{
			"fieldname": "day_3",
			"label": "Day 3",
			"fieldtype": "Data",
		},
		{
			"fieldname": "submitted_summary",
			"label": "Submitted Summary",
			"fieldtype": "Data",
		},
		{
			"fieldname": "passed_summary",
			"label": "Passed Summary",
			"fieldtype": "Data",
		},
	]


def status_for_day(user, day):
	latest_submission_for_day = frappe.get_all(
		"FF Assignment Submission",
		filters={"user": user, "day": day},
		pluck="status",
		order_by="creation desc",
		limit=1,
	)

	if latest_submission_for_day:
		latest_submission_for_day = latest_submission_for_day[0]
		return latest_submission_for_day

	return "Not Submitted"


def has_submitted(status):
	return status != "Not Submitted"


def has_passed(status):
	return status == "Passed"
