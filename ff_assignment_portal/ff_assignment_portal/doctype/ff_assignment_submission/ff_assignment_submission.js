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

        if (!frm.doc.cloned_to_code_server) {
            const button = frm.add_custom_button("Clone to Code Server", () => {
                frm.call({ method: "clone_to_code_server", button, freeze: true, doc: frm.doc }).then(() => {
                    frappe.show_alert({message: "Successfully cloned!", indicator: "green"})
                    frm.refresh();
                })
            })
        }

        if (frm.doc.cloned_to_code_server) {
            frm.add_web_link(`https://code.frappe.school/?folder=/home/school/ff-assignments/${frm.doc.name}`, "View in Code Server")
        }
	},
});
