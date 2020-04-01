# -*- coding: utf-8 -*-
# Copyright (c) 2020, BJJ and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint,format_datetime,add_days,today,formatdate,date_diff,getdate,get_last_day,flt
from erpnext.accounts.utils import get_fiscal_year
from erpnext.accounts.party import get_party_details


class ICWrapper(Document):
	def before_insert(self):
		#frappe.msgprint("call")
		if self.update_stock == 1:
			if not self.from_warehouse:
				frappe.throw("From Warehouse Mandatory")
			if not self.to_warehouse:
				frappe.throw("To Warehouse Mandatory")
		create_sales_invoice(self)
		create_purchase_invoice(self)

	def validate(self):
		if self.update_stock == 1:
			if not self.from_warehouse:
				frappe.throw("From Warehouse Mandatory")
			if not self.to_warehouse:
				frappe.throw("To Warehouse Mandatory")
		update_sales_invoice(self)
		update_purchase_invoice(self)
	
	def before_submit(self):
		#frappe.msgprint("submit")
		submit_invoice(self)

@frappe.whitelist()
def get_supplier_and_customer(buyer_company,seller_company):
	data =dict(
		customer = '',
		supplier = ''
	)
	inter_company_details = frappe.get_all("Inter Company Setting",filters={"from_company":seller_company,"to_company":buyer_company},fields=["*"])
	if len(inter_company_details) >= 1:
		data['customer'] = inter_company_details[0].get('customer')
		data['supplier'] = inter_company_details[0].get('supplier')
	return data

@frappe.whitelist()
def create_sales_invoice(doc):
	if not frappe.has_permission('Sales Invoice',"create"):
		frappe.throw("Unsufficient Permission To Create Sales Invoice")
	try:
		customer_details = get_party_details(party=doc.ic_customer, party_type="Customer")
		frappe.errprint(customer_details)
		sinv_doc = frappe.get_doc(dict(
			doctype = "Sales Invoice",
			company = doc.seller_company,
			posting_date = doc.date,
			set_posting_time = 1,
			due_date = add_days(doc.date,2),
			selling_price_list = customer_details.get('selling_price_list'),
			fiscal_year=get_fiscal_year(doc.date,company=doc.seller_company)[0],
			naming_series="SINV .######",
			customer = doc.ic_customer,
			update_stock = doc.update_stock,
			letter_head=frappe.db.get_value("Company",str(doc.seller_company),"default_letter_head"),
			items = get_item_object(doc.items,doc.from_warehouse),
			ic_invoice = 1
		)).insert()
		doc.ic_sales_invoice_no = sinv_doc.name
		doc.ic_sales_inv_status = sinv_doc.status
		# frappe.db.set_value(doc.doctype,doc.name,"ic_sales_invoice_no",sinv_doc.name)
		# frappe.db.set_value(doc.doctype,doc.name,"ic_sales_invoice_status",sinv_doc.status)
	except Exception:
		frappe.log_error(frappe.get_traceback())
		frappe.throw(frappe.get_traceback())

@frappe.whitelist()
def update_sales_invoice(self):
	#frappe.errprint(self)
	if self.ic_sales_invoice_no:
		customer_details = get_party_details(party=self.ic_customer, party_type="Customer")
		doc = frappe.get_doc("Sales Invoice",self.ic_sales_invoice_no)
		doc.posting_date = self.date
		doc.due_date = add_days(self.date,2)
		doc.update_stock = self.update_stock
		doc.selling_price_list = customer_details.get("selling_price_list")
		doc.set("items", [])
		for item in self.items:
			new_item = doc.append("items")
			new_item.item_code = item.item
			new_item.qty = item.qty
			new_item.warehouse = self.from_warehouse
		doc.save()

@frappe.whitelist()
def update_purchase_invoice(self):
	#frappe.errprint(self)
	if self.ic_pur_invoice_no:
		supplier_details = get_party_details(party=self.ic_supplier, party_type="Supplier")
		doc = frappe.get_doc("Purchase Invoice",self.ic_pur_invoice_no)
		doc.posting_date = self.date
		doc.due_date = add_days(self.date,2)
		doc.update_stock = self.update_stock
		doc.buying_price_list = supplier_details.get("buying_price_list")
		doc.set("items", [])
		for item in self.items:
			new_item = doc.append("items")
			new_item.item_code = item.item
			new_item.qty = item.qty
			new_item.warehouse = self.to_warehouse
		doc.save()


@frappe.whitelist()
def create_purchase_invoice(doc):
	if not frappe.has_permission('Purchase Invoice',"create"):
		frappe.throw("Unsufficient Permission To Create Purchase Invoice")
	try:
		supplier_details = get_party_details(party=doc.ic_supplier, party_type="Supplier")
		pinv_doc = frappe.get_doc(dict(
			doctype = "Purchase Invoice",
			company = doc.buyer_company,
			posting_date = doc.date,
			buying_price_list = supplier_details.get("buying_price_list"),
			set_posting_time = 1,
			due_date = add_days(doc.date,2),
			supplier = doc.ic_supplier,
			update_stock = doc.update_stock,
			items = get_item_object(doc.items,doc.to_warehouse),
			ic_invoice = 1,
			sales_invoice_no = doc.ic_sales_invoice_no
		)).insert()
		doc.ic_pur_invoice_no = pinv_doc.name
		doc.ic_pur_inv_status = pinv_doc.status
		if pinv_doc.sales_invoice_no:
			frappe.db.set_value("Sales Invoice",pinv_doc.sales_invoice_no,"purchase_invoice_no",pinv_doc.name)
		# frappe.db.set_value(doc.doctype,doc.name,"ic_purchase_invoice_no",pinv_doc.name)
		# frappe.db.set_value(doc.doctype,doc.name,"ic_purchase_inv_status",pinv_doc.status)
	except Exception:
		frappe.log_error(frappe.get_traceback())
		sales_invoice_no = frappe.db.get_value(doc.doctype,doc.name,"ic_sales_invoice_no")
		delete_or_cancel_sales_invocie("Sales Invoice",sales_invoice_no,doc)
		frappe.throw(frappe.get_traceback())

def get_item_object(items,warehouse=None):
	new_items_obj = []
	for row in items:
		item = dict(
			item_code = row.item,
			qty = row.qty,
			warehouse = warehouse
		)
		new_items_obj.append(item)
	return new_items_obj

@frappe.whitelist()
def submit_invoice(self):
	try:
		if not frappe.has_permission('Sales Invoice',"submit"):
			frappe.throw("Unsufficient Permission To Submit Sales Invoice")
		if not frappe.has_permission('Purchase Invoice',"submit"):
			frappe.throw("Unsufficient Permission To Submit Purchase Invoice")
		if not self.ic_sales_invoice_no:
			frappe.throw("Sales Invoice Required")
		if not self.ic_pur_invoice_no:
			frappe.throw("Purchase Invoice Required")
		si_doc = frappe.get_doc("Sales Invoice",self.ic_sales_invoice_no)
		si_doc.submit()
		pi_doc = frappe.get_doc("Purchase Invoice",self.ic_pur_invoice_no)
		pi_doc.submit()
		self.ic_sales_inv_status = frappe.db.get_value("Sales Invoice",si_doc.name,"status")
		self.ic_pur_inv_status = frappe.db.get_value("Purchase Invoice",pi_doc.name,"status")
	except Exception:
		frappe.log_error(frappe.get_traceback())
		frappe.throw(frappe.get_traceback())

def delete_or_cancel_sales_invocie(doctype,name,doc):
	doc_details = frappe.get_doc(doctype,name)
	if cint(doc_details.docstatus) == 0:
		if not frappe.has_permission('Sales Invoice',"delete"):
			frappe.throw("Unsufficient Permission To Delete Sales Invoice")
		else:
			frappe.delete_doc(doctype,name,force=1)
			frappe.db.set_value(doc.doctype,doc.name,"ic_sales_invoice_no","")
			frappe.db.set_value(doc.doctype,doc.name,"ic_sales_inv_status","")

	if cint(doc_details.docstatus) == 1:
		if not frappe.has_permission('Sales Invoice',"cancel"):
			frappe.throw("Unsufficient Permission To Cancel Sales Invoice")
		doc_details.cancel()
		up_doc_details = frappe.get_doc(doctype,name)
		frappe.db.set_value(doc.doctype,doc.name,"ic_sales_invoice_no",up_doc_details.name)
		frappe.db.set_value(doc.doctype,doc.name,"ic_sales_inv_status",up_doc_details.status)

	

