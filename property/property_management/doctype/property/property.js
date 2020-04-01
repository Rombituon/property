// Copyright (c) 2020, BJJ and contributors
// For license information, please see license.txt

frappe.ui.form.on('Property', {
	setup: function(frm) {
		frm.set_query('gas_safety_certificate', 'gas_safety_certificate_details', function(doc, cdt, cdn) {
			var filters = {
				'certificate_type': 'Gas'
			};
			return {
				filters: filters
			}
		});
		frm.set_query('electric_safety_certificate', 'electric_safety_certificate_details', function(doc, cdt, cdn) {
			var filters = {
				'certificate_type': 'Electric'
			};
			return {
				filters: filters
			}
		});

		frm.set_query('building_insurance', 'building_insurance_details', function(doc, cdt, cdn) {
			var filters = {
				'insurance_type': 'Building'
			};
			return {
				filters: filters
			}
		});

		frm.set_query('boiler_and_ch_insurance', 'boiler_and_ch_insurance_details', function(doc, cdt, cdn) {
			var filters = {
				'insurance_type': 'Boiler'
			};
			return {
				filters: filters
			}
		});

	}
});
