// Copyright (c) 2023, Hussain Nagaria and contributors
// For license information, please see license.txt

frappe.ui.form.on("FF Assignment Submission", {
	refresh(frm) {
        frm.add_custom_button("Generate Similarity Score", () => {
            frm.call("_generate_similarity_score").then(() => {
                frappe.show_alert("Similarity score set!")
                frm.refresh();
            })
        })

        if (frm.doc.day === "4") {
            frm.add_custom_button("Clone to Code Server", () => {
                frm.call("clone_to_code_server")
            })
        }
	},
});
