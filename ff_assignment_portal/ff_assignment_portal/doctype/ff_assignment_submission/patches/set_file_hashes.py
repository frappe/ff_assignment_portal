import frappe


def execute():
    submissions = frappe.db.get_all(
        "FF Assignment Submission",
        filters={"status": "Passed", "day": ("!=", "4")},
        pluck="name",
    )

    for submission in submissions:
        doc = frappe.get_doc("FF Assignment Submission", submission)
        doc.set_file_hashes()
        doc.save()
