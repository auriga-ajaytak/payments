# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import json

import frappe
from frappe import _
from frappe.utils import cint, flt

no_cache = 1

expected_keys = (
	"amount",
	"title",
	"description",
	"reference_doctype",
	"reference_docname",
	"payer_name",
	"payer_email",
	"order_id",
	"currency",
)


def get_context(context):
	print("context",frappe.form_dict["company"])
	context.no_cache = 1
	context.api_key = get_api_key(company=frappe.form_dict["company"])
	
	try:
		doc = frappe.get_doc("Integration Request", frappe.form_dict["token"])
		payment_details = json.loads(doc.data)

		for key in expected_keys:
			context[key] = payment_details[key]

		context["token"] = frappe.form_dict["token"]
		context["company"] = frappe.form_dict["company"]
		context["amount"] = flt(context["amount"])
		context["subscription_id"] = (
			payment_details["subscription_id"] if payment_details.get("subscription_id") else ""
		)

	except Exception:
		frappe.redirect_to_message(
			_("Invalid Token"),
			_("Seems token you are using is invalid!"),
			http_status_code=400,
			indicator_color="red",
		)

		frappe.local.flags.redirect_location = frappe.local.response.location
		raise frappe.Redirect


def get_api_key(company=None):
	# api_key = frappe.db.get_single_value("Razorpay Settings", "api_key")
	try:
		api_key = frappe.db.get_value("Company RazorPay", {"company":company}, "api_key")
		print("get_api_key",api_key)
		print(frappe.form_dict.get("use_sandbox"))
		if cint(frappe.form_dict.get("use_sandbox")):
			api_key = frappe.conf.sandbox_api_key

		return api_key
	except:
		frappe.throw("Payment gateway not found for School")


@frappe.whitelist(allow_guest=True)
def make_payment(razorpay_payment_id, options, reference_doctype, reference_docname, token,company):
	data = {}

	if isinstance(options, str):
		data = json.loads(options)

	data.update(
		{
			"razorpay_payment_id": razorpay_payment_id,
			"reference_docname": reference_docname,
			"reference_doctype": reference_doctype,
			"token": token,
			"company": company,
		}
	)
	doc_name = frappe.db.get_value("Company RazorPay", {"company":company}, )
	if doc_name:
		doc = frappe.get_doc("Company RazorPay", doc_name)
		print(doc)
	else:
		frappe.throw("Payment gateway not found for School")

	data = doc.create_request(data)
	frappe.db.commit()
	return data
