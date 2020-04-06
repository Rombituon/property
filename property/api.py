from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint,format_datetime,add_days,today,formatdate,date_diff,getdate,get_last_day,flt
from erpnext.accounts.utils import get_fiscal_year
from erpnext.accounts.party import get_party_details

@frappe.whitelist()
def validate_rental_invoice(doc,method):
	if doc.rental_invoice:
		if not doc.tenancy:
			frappe.throw("Tenancy Mandatory For Rental Invoice")
		for item in doc.items:
			if not item.from_date:
				frappe.throw("From Date Mandatory For Rental Invoice")
			if not item.to_date:
				frappe.throw("To Date Mandatory For Rental Invoice")
			
		if len(doc.items) > 1:
			frappe.throw("More than one item not allow for rental invoice")
		tenancy_close = frappe.db.get_value("Property Tenancy",doc.tenancy,"tenancy_closed")
		if cint(tenancy_close) == 1:
			frappe.throw("Rental Invoice Not Allow For Closed Tenancy")

@frappe.whitelist()
def submit_rental_invoice(doc,method):
	#frappe.msgprint("call")
	if doc.rental_invoice:
		tenancy_doc = frappe.get_doc("Property Tenancy",doc.tenancy)
		for row in doc.items:
			tenancy_doc.append("rental_invoice",{"invoice_no":doc.name,"from_date":row.from_date,"to_date":row.to_date})
		tenancy_doc.save()
		update_till_date_value(doc.tenancy)

@frappe.whitelist()
def cancel_rental_invoice(doc,method):
	if doc.rental_invoice:
		frappe.db.sql("""delete from `tabRental Invoice` where invoice_no=%s""",doc.name)
		update_till_date_value(doc.tenancy)

def update_till_date_value(tenancy):
	data = frappe.db.sql("""select max(to_date) from `tabRental Invoice` where parent=%s""",tenancy)
	if len(data) >= 1:
		frappe.db.set_value("Property Tenancy",tenancy,"invoice_till_date",data[0][0])

