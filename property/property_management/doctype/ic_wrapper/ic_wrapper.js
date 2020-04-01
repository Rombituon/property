// Copyright (c) 2020, BJJ and contributors
// For license information, please see license.txt

frappe.ui.form.on('IC Wrapper', {
	refresh: function(frm) {
		frm.toggle_enable("seller_company", frm.doc.__islocal);
		frm.toggle_enable("buyer_company", frm.doc.__islocal);
	},
	setup:function(frm){
		frm.set_query("from_warehouse", function() {
			return {
				filters: {
					company: frm.doc.seller_company
				}
			}
		})
		frm.set_query("to_warehouse", function() {
			return {
				filters: {
					company: frm.doc.buyer_company
				}
			}
		})
	},
	buyer_company:function(frm){
		get_supplier_customer(frm)
	},
	seller_company:function(frm){
		get_supplier_customer(frm)
	}

});
function get_supplier_customer(frm){
	if(frm.doc.buyer_company && frm.doc.seller_company){
		frappe.call({
			method:"property.property_management.doctype.ic_wrapper.ic_wrapper.get_supplier_and_customer",
			args:{'buyer_company':frm.doc.buyer_company,'seller_company':frm.doc.seller_company},
			callback:function(r){
				if(r.message){
					frappe.model.set_value(frm.doc.doctype,frm.doc.name,"ic_supplier",r.message.supplier)
					frappe.model.set_value(frm.doc.doctype,frm.doc.name,"ic_customer",r.message.customer)
				}
			}
		})
	}
	else{
		frappe.model.set_value(frm.doc.doctype,frm.doc.name,"ic_supplier","")
		frappe.model.set_value(frm.doc.doctype,frm.doc.name,"ic_customer","")
	}
}
