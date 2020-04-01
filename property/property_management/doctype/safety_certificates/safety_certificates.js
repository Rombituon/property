frappe.ui.form.on("Safety Certificates", "refresh", function(frm) {
	frm.toggle_enable("certificate_type", frm.doc.__islocal);
});