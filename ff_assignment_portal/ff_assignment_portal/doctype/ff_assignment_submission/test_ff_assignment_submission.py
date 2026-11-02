# Copyright (c) 2023, Hussain Nagaria and Contributors
# See license.txt

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from ff_assignment_portal.ff_assignment_portal.doctype.ff_assignment_submission.ff_assignment_submission import (
	FFAssignmentSubmission,
)


class TestFFAssignmentSubmission(FrappeTestCase):
	def test_similarity_score_generation(self):
		# have a sample zip file
		# create 2 submissions with different users
		# call generate method
		# check the score
		pass


class TestNotifyStudent(FrappeTestCase):
	"""The student is emailed only when there is feedback to send."""

	def notify(self, feedback):
		submission = frappe._dict(day="3", user="student@example.com", feedback=feedback, doctype="FF Assignment Submission", name="TEST")
		with patch.dict(frappe.conf, {"developer_mode": 0}), patch("frappe.sendmail") as sendmail:
			FFAssignmentSubmission.notify_student(submission)
		return sendmail

	def test_no_email_while_feedback_is_empty(self):
		for feedback in (None, "", "<p></p>", "<p> </p>"):
			self.notify(feedback).assert_not_called()

	def test_email_carries_the_feedback(self):
		sendmail = self.notify("Fix the naming rule of Airline")
		sendmail.assert_called_once()
		self.assertEqual(sendmail.call_args.kwargs["message"], "Fix the naming rule of Airline")
