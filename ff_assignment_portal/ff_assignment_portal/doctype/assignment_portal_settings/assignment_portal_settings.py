# Copyright (c) 2024, Hussain Nagaria and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AssignmentPortalSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		code_server_host: DF.Data | None
		code_server_password: DF.Password | None
		private_key_type: DF.Literal["ed25519", "RSA"]
	# end: auto-generated types

	pass
