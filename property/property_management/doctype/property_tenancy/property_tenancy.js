// Copyright (c) 2020, BJJ and contributors
// For license information, please see license.txt

frappe.ui.form.on('Property Tenancy', {
	refresh: function(frm,cdt,cdn) {
		if(!frm.doc.deafult_rent_item){
			frappe.call({
				method:"frappe.client.get",
				args:{'doctype':'Novo Single Parameters','name':'SPRM 022'},
				callback:function(data){
					frappe.model.set_value(cdt,cdn,"deafult_rent_item",data.message.parameter_value)
				}
			})
		}
	}
});
