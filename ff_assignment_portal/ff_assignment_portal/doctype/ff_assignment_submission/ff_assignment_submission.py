# Copyright (c) 2023, Hussain Nagaria and contributors
# For license information, please see license.txt

import json
import frappe
import zipfile

from frappe.model.document import Document

ASSIGNMENT_DOCTYPE_NAME = "FF Assignment Submission"

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
        "num_fetched_fields": 2,
    },
}


class FFAssignmentSubmission(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        cloned_to_code_server: DF.Check
        day: DF.Literal["1", "2", "3", "4"]
        demo_video: DF.Attach | None
        feedback: DF.HTMLEditor | None
        full_name: DF.Data | None
        hashes: DF.Code | None
        similar_assignment: DF.Link | None
        similarity_score: DF.Percent
        status: DF.Literal[
            "Unchecked", "Check In Progress", "Stale", "Passed", "Failed"
        ]
        submission: DF.Attach
        submission_summary: DF.SmallText | None
        user: DF.Link
    # end: auto-generated types

    def validate(self):
        if not self.submission.endswith(".zip"):
            frappe.throw("Please upload a zip file.")

    def on_update(self):
        if not self.is_new() and self.has_value_changed("status"):
            self.notify_student()

    def before_insert(self):
        self.validate_previous_in_progress()
        self.set_submission_summary()
        self.run_checks()
        self.set_file_hashes()

    def after_insert(self):
        self.enqueue_generate_similarity_score()

    def enqueue_generate_similarity_score(self):
        if self.day == "4":
            return

        frappe.enqueue_doc(
            ASSIGNMENT_DOCTYPE_NAME,
            self.name,
            "_generate_similarity_score",
            queue="long",
        )

    @frappe.whitelist()
    def _generate_similarity_score(self):
        submissions = frappe.db.get_all(
            self.doctype,
            fields=["name", "hashes"],
            filters={"day": self.day, "status": "Passed", "user": ("!=", self.user)},
        )

        max_similarity_score = 0
        similar_assignment = None

        for submission in submissions:
            if not submission.hashes:
                continue
            file_hashes = frappe.parse_json(submission.hashes)
            current_submission_hashes = frappe.parse_json(self.hashes)

            similarity_score = compare_hashes(file_hashes, current_submission_hashes)

            if similarity_score > max_similarity_score:
                max_similarity_score = similarity_score
                similar_assignment = submission.name

        self.similarity_score = max_similarity_score
        self.similar_assignment = similar_assignment
        self.save()

    def validate_previous_in_progress(self):
        previous_in_progress = frappe.db.get_all(
            ASSIGNMENT_DOCTYPE_NAME,
            filters={"status": "Check In Progress", "day": self.day, "user": self.user},
            pluck="name",
        )

        if previous_in_progress:
            for name in previous_in_progress:
                frappe.db.set_value(ASSIGNMENT_DOCTYPE_NAME, name, "status", "Stale")

    def set_submission_summary(self):
        summary = ""

        if self.day == "4":
            summary = ""
            summary += f"Assignment: {self.submission}, Demo Video: {self.demo_video}"
        else:
            files = list(self.get_filename_with_contents())
            summary += f"{len(files)} Files"
            summary += " (" + ", ".join([f[0] for f in files]) + ")"

        self.submission_summary = summary

    def notify_student(self):
        if frappe.conf.developer_mode or self.day == "4":
            return

        frappe.sendmail(
            recipients=self.user,
            subject=f"[Frappe School] There is an update on your submission for Day {self.day}",
            message=self.feedback,
        )

    def run_checks(self):
        if self.day == "1":
            self.run_checks_for_day_1()
        elif self.day == "2":
            self.run_checks_for_day_2()
        elif self.day == "3":
            self.run_checks_for_day_3()
        elif self.day == "4":
            self.mark_as_check_in_progress()
        else:
            frappe.throw("Unsupported day.")

    def run_checks_for_day_1(self):
        all_problems = []  # to store all the problems
        filename_with_contents = list(self.get_filename_with_contents())

        # number of files must be 4
        num_files = len(filename_with_contents)
        if num_files != 4:
            frappe.throw(
                f"There must be exactly 4 files in the zip file, found {num_files}."
            )

        # name of the files must be correct
        expected_filenames = [
            "airline.json",
            "airplane.json",
            "airplane_ticket.json",
            "flight_passenger.json",
        ]
        for filename, _ in filename_with_contents:
            if filename not in expected_filenames:
                all_problems.append(
                    f"Expected file name to be one of {expected_filenames}, but found {filename}."
                )

        for filename, file_json in filename_with_contents:
            doctype_name = guess_doctype_from_filename(filename)
            submission_doctype_json = SubmissionDocTypeJSON(
                filename,
                file_json,
                **doctype_check_parameters_map.get(doctype_name, {}),
            )
            problems = submission_doctype_json.run_checks()
            if problems:
                all_problems.extend(problems)

        if all_problems:
            self.status = "Failed"
            self.feedback = "<br/>".join(all_problems)
        else:
            self.status = "Passed"
            self.feedback = "All checks passed 🎉"

    def run_checks_for_day_2(self):
        problems = self.run_schema_checks_for_day_2()

        if problems:
            self.status = "Failed"
            self.feedback = "<br/>".join(problems)
            return

        self.mark_as_check_in_progress()
        self.send_to_gh_actions_for_checking_day_2()

    def send_to_gh_actions_for_checking_day_2(self):
        # NOTE: Happens in a webhook in frappe.school
        pass

    def run_schema_checks_for_day_2(self):
        problems = []
        required_files_in_zip = [
            "airplane_flight.json",
            "airplane_ticket.json",
            "show-me.html",
            "airplane_flight.html",
            "airplane_flight_row.html",
            "airplane_ticket.py",
            "flight_passenger.py",
            "airplane_flight.py",
            "*web_form.json",
            "*notification.json",
            "populate_seats.py",
        ]

        self.check_required_files(required_files_in_zip, problems)

        # check the web form json
        web_form_json = None
        for filename, file_json in self.get_filename_with_contents():
            if filename.endswith("web_form.json"):
                web_form_json = file_json
                break

        # For the web form, we have to check these: "doc_type": "Airplane Ticket"
        if web_form_json:
            if web_form_json.get("doc_type") != "Airplane Ticket":
                problems.append("Web Form must be for Airplane Ticket DocType.")

        # Check the notification json
        notification_json = None
        for filename, file_json in self.get_filename_with_contents():
            if filename.endswith("notification.json"):
                notification_json = file_json
                break

        # For the Notification, we have to check "event": "Days Before", "days_in_advance": 1,
        # "document_type": "Airplane Flight" and "condition": "doc.status==\"Scheduled\""
        if notification_json:
            if notification_json.get("event") != "Days Before":
                problems.append("Notification must be for Days Before event.")
            if notification_json.get("days_in_advance") != 1:
                problems.append("Notification must be sent 1 day in advance.")
            if notification_json.get("document_type") != "Airplane Flight":
                problems.append("Notification must be for Airplane Flight DocType.")

            condition = (
                notification_json.get("condition", "")
                .replace(" ", "")
                .replace(r"\"", "'")
            )

            # replace double quotes with single quotes in condition
            condition = condition.replace('"', "'")

            if "doc.status=='Scheduled'" not in condition:
                problems.append(
                    f"Notification must be for {frappe.bold('Scheduled')} Airplane Flights only."
                )

        # Web View must be enabled for Airplane Flight DocType (i.e. has_web_view must be 1)
        airplane_flight_doctype = None
        for filename, file_json in self.get_filename_with_contents():
            if filename.endswith("airplane_flight.json"):
                airplane_flight_doctype = file_json
                break

        if airplane_flight_doctype:
            if not airplane_flight_doctype.get("has_web_view"):
                problems.append(
                    f"Web View must be enabled for {frappe.bold('Airplane Flight')} DocType."
                )

        return problems

    def check_required_files(self, required_files_in_zip, problems):
        filename_with_contents = list(self.get_filename_with_contents())

        # all the required file names must be present
        for required_file in required_files_in_zip:
            found = False
            for filename, _ in filename_with_contents:
                if required_file.startswith("*"):
                    if filename.endswith(required_file[1:]):
                        found = True
                        break
                elif filename == required_file:
                    found = True
                    break

            if not found:
                problems.append(
                    f"Required file `{frappe.bold(required_file)}` not found."
                )

    def run_checks_for_day_3(self):
        problems = self.run_schema_checks_for_day_3()

        if problems:
            self.status = "Failed"
            self.feedback = "<br/>".join(problems)
            return

        self.mark_as_check_in_progress()

    def run_schema_checks_for_day_3(self):
        problems = []

        required_files_in_zip = [
            "airline.js",
            "airplane_ticket.js",
            "airplane_ticket.py",
            "airplane_ticket.json",
            "airplane.json",
            "airport.json",
            "airplanes_by_airline.json",
            "revenue_by_airline.py",
            "add_on_popularity.json",
        ]

        self.check_required_files(required_files_in_zip, problems)

        if problems:
            return problems

        file_name_with_contents = list(self.get_filename_with_contents())
        js_files = {
            file_name: content
            for file_name, content in file_name_with_contents
            if file_name.endswith(".js")
        }

        json_files = {
            file_name: content
            for file_name, content in file_name_with_contents
            if file_name.endswith(".json")
        }

        check_client_scripts(js_files, problems)

        # check if proper permissions are applied
        check_permissions_for_day_3(json_files, problems)

        return problems

    def mark_as_check_in_progress(self):
        self.status = "Check In Progress"

    def get_filename_with_contents(self):
        file_doc = frappe.get_doc("File", {"file_url": self.submission})

        with zipfile.ZipFile(file_doc.get_full_path()) as zip_file:
            for file_name in zip_file.namelist():
                # ignore files that contain __MACOSX and .DS_Store
                if "__MACOSX" in file_name or ".DS_Store" in file_name:
                    continue

                if file_name.endswith((".json", ".py", ".html", ".js")):
                    file_json = zip_file.read(file_name).decode("utf-8")
                    if file_name.endswith(".json"):
                        try:
                            file_json = json.loads(file_json)
                        except json.decoder.JSONDecodeError:
                            frappe.throw(
                                f"Unable to parse JSON file. There is a problem with your JSON file: {frappe.bold(file_name)}."
                            )
                    parts = file_name.split("/")
                    file_name = parts[-1]

                    if len(parts) > 2:
                        frappe.throw(
                            f"You have files inside a sub-directory ({parts[0]}/{parts[1]}), please place all the required files directly inside the zipped folder."
                        )

                    yield file_name, file_json

    def set_file_hashes(self):
        if self.day == "4":
            return

        from hashlib import md5

        files_with_content = self.get_filename_with_contents()
        hashes = {}

        for file_name, content in files_with_content:
            if file_name.endswith(".json"):
                content = frappe.as_json(content)

            hash_obj = md5(content.encode())
            hashes[file_name] = hash_obj.hexdigest()

        self.hashes = frappe.as_json(hashes, indent=2)

    @frappe.whitelist()
    def clone_to_code_server(self):
        if self.cloned_to_code_server:
            frappe.throw("Already cloned to code server.")

        self._clone_to_code_server()

    def _clone_to_code_server(self):
        ssh_private_key = frappe.conf.ssh_private_key

        if not ssh_private_key:
            frappe.throw("SSH Private Key is not configured.")

        from ff_assignment_portal.utils import get_ssh_client

        ssh = get_ssh_client(ssh_private_key)

        # scp the zip file to code server
        assignment_file = self.submission
        assignment_file_doc = frappe.get_doc("File", {"file_url": assignment_file})
        assignment_file_path = assignment_file_doc.get_full_path()

        base_dir = "/home/school/ff-assignments"

        sftp = ssh.open_sftp()
        sftp.put(assignment_file_path, f"{base_dir}/{self.name}.zip")

        # run the script to extract the zip file
        stdin, stdout, stderr = ssh.exec_command(
            f"cd {base_dir} && unzip {self.name}.zip -d {self.name}"
        )

        # check if the command was successful
        error = stderr.read()
        if error:
            frappe.throw(f"stderr: {error}")

        # delete the zip file
        sftp.remove(f"/home/school/ff-assignments/{self.name}.zip")

        self.cloned_to_code_server = 1
        self.save()
        ssh.close()


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
        num_fetched_fields=None,
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
        self.num_fetched_fields = num_fetched_fields

        self.validate_meta()

    def validate_meta(self):
        if not isinstance(self.doctype_meta, dict):
            frappe.throw(f"Invalid DocType JSON: {frappe.bold(self.filename)}!")

        if not self.doctype_meta.get("name"):
            frappe.throw(
                f"Invalid DocType JSON: {frappe.bold(self.filename)}! Cannot find `name` key."
            )

    def validate_num_fields(self, expected_num_fields):
        try:
            fields = self.doctype_meta["fields"]
        except Exception:
            frappe.throw(
                f"Cannot read `fields` list from DocType JSON: {frappe.bold(self.filename)}"
            )

        # ignore meta fields
        meta_field_types = ("Column Break", "Section Break", "Tab Break")

        filtered_fields = []
        for field in fields:
            if field["fieldtype"] not in meta_field_types:
                filtered_fields.append(field)

        num = len(filtered_fields)

        if num != expected_num_fields:
            self.problems.append(
                f"{self.doctype_meta['name']} DocType must contain {frappe.bold(expected_num_fields)} fields, but found {num}"
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
            self.problems.append(
                f"{self.doctype} naming rule should be {naming_rule_type}"
            )

    def validate_doctype_connections(
        self, expected_num_connections, expected_connection_doctypes
    ):
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
                self.problems.append(
                    f"{self.doctype} DocType must be {frappe.bold(summary)}."
                )

    def validate_document_states(self):
        states = self.doctype_meta.get("states", [])

        if len(states) < self.num_document_states:
            self.problems.append(
                f"At least {self.num_document_states} <strong>Document States</strong> must be defined for {self.doctype} doctype."
            )

    def validate_fetched_fields(self):
        fields = self.doctype_meta["fields"]

        fetched_fields_count = 0
        for field in fields:
            if field.get("fetch_from"):
                fetched_fields_count = fetched_fields_count + 1

        if fetched_fields_count != self.num_fetched_fields:
            self.problems.append(
                f"Exactly {self.num_fetched_fields} fields must be fetched from some link into {self.doctype} DocType."
            )

    @property
    def doctype(self):
        return guess_doctype_from_filename(self.filename)

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
            self.validate_doctype_connections(
                self.expected_num_connections, self.expected_connection_doctypes
            )

        if self.checked_doctype_flags:
            self.validate_doctype_flags()

        if self.num_document_states:
            self.validate_document_states()

        if self.num_fetched_fields:
            self.validate_fetched_fields()

        return self.problems


@frappe.whitelist()
def submit_assignment(day, file, demo_video=None):
    if day == "4" and not demo_video:
        frappe.throw("Demo video is required to be submitted with final assignment!")

    submission_doc: FFAssignmentSubmission = frappe.new_doc("FF Assignment Submission")
    submission_doc.user = frappe.session.user
    submission_doc.submission = file.get("file_url")
    submission_doc.day = day
    if demo_video:
        submission_doc.demo_video = demo_video.get("file_url")
    submission_doc.insert()


def guess_doctype_from_filename(filename):
    if "passenger" in filename:
        return "Flight Passenger"

    if "airline" in filename:
        return "Airline"

    if "airplane_ticket" in filename:
        return "Airplane Ticket"

    if "airplane" in filename:
        return "Airplane"

    return None


def check_client_scripts(script_files_with_name, problems):
    airplane_ticket_js = script_files_with_name.get("airplane_ticket.js", "")
    airline_js = script_files_with_name.get("airline.js", "")

    airplane_ticket_js = get_cleaned_up_content(airplane_ticket_js)
    airline_js = get_cleaned_up_content(airline_js)

    # airplane_ticket.js must contain frm.add_custom_button()
    if "frm.add_custom_button" not in airplane_ticket_js:
        problems.append(
            f"`airplane_ticket.js` must add a custom button using {frappe.bold('frm.add_custom_button()')} function"
        )

    # airplane_ticket.js must contain new frappe.ui.Dialog()
    if ("newfrappe.ui.Dialog" not in airplane_ticket_js) and (
        "frappe.prompt(" not in airplane_ticket_js
    ):
        problems.append(
            f"`airplane_ticket.js` must create a new dialog using {frappe.bold('new frappe.ui.Dialog()')} or {frappe.bold('frappe.prompt')}"
        )

    # airplane_ticket.js must contain frm.set_value()
    if "frm.set_value" not in airplane_ticket_js:
        problems.append(
            f"`airplane_ticket.js` must set value of 'seat' using {frappe.bold('frm.set_value()')} function"
        )

    # airline.js must contain frm.add_web_link()
    if "frm.add_web_link" not in airline_js:
        problems.append(
            f"`airline.js` must add a web link using {frappe.bold('frm.add_web_link()')} function"
        )


def get_cleaned_up_content(content_string):
    # remove whitespace
    content_string = content_string.replace(" ", "")
    # remove newlines
    content_string = content_string.replace("\n", "")
    # remove trailing and leading spaces
    content_string = content_string.strip()

    return content_string


def check_permissions_for_day_3(json_files, problems):
    required_permissions_for_airplane_ticket = [
        ("Flight Crew Member", {"create", "read", "write"}),
        ("Travel Agent", {"create", "read", "write", "delete"}),
        ("Airport Authority Personnel", {"create", "read", "write", "delete"}),
    ]

    # get airplane_ticket.json
    airplane_ticket_json = json_files.get("airplane_ticket.json", {})
    airplane_ticket_permissions = airplane_ticket_json.get("permissions", [])

    # check if all the required permissions are present

    permissions_by_role = frappe._dict()
    for permission in airplane_ticket_permissions:
        role = permission.get("role")
        processed_permissions = set()
        for key, value in permission.items():
            if key in ("create", "read", "write", "delete") and value == 1:
                processed_permissions.add(key)

        permissions_by_role.setdefault(role, set()).update(processed_permissions)

    for role, required_permissions in required_permissions_for_airplane_ticket:
        if role not in permissions_by_role:
            problems.append(
                f"Role {frappe.bold(role)} must be added in permission rules of Airplane Ticket DocType."
            )
            continue

        permissions = permissions_by_role[role]
        if not required_permissions == permissions:
            missing_permissions = required_permissions.difference(permissions)
            problems.append(
                f"Role {frappe.bold(role)} must have {frappe.bold(', '.join(missing_permissions))} permissions for Airplane Ticket DocType."
            )


def compare_hashes(other: dict, original: dict) -> float:
    "Compares file hashes and returns similarity score percent"
    score = 0

    for filename, hash in original.items():
        if other.get(filename, "") == hash:
            # MATCH!!
            score += 1 / len(original)

    return score * 100
