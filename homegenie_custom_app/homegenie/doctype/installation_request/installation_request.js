// Copyright (c) 2024, Homegenie and contributors
// For license information, please see license.txt

frappe.ui.form.on('Installation Request', {
	refresh: function(frm) {
		
		if(frm.doc.docstatus==1){
			frm.add_custom_button(__("Quotation"),function(){
				frappe.call({
					method: 'homegenie_custom_app.homegenie.doctype.installation_request.installation_request.get_child_item_value',
					args: {'name':cur_frm.doc},
					callback:function(r){
						if(r.message.function=='Success'){
							change_route(frm,r.message.doctype,r.message.value)
						}
						else{
							frappe.msgprint({ message: `Quotation is not created.`, indicator: "red" }, 5)
						}
					}
				})
			},__("Create"));
			frm.add_custom_button(__("Installation Note"),function(){
				frappe.call({
					method: 'homegenie_custom_app.homegenie.doctype.installation_request.installation_request.get_installation_note_child_table',
					args: {'name':cur_frm.doc},
					callback:function(r){
						if(r.message.function=='Success'){
							change_route(frm,r.message.doctype,r.message.value)
						}
						else{
							frappe.msgprint({ message: `Installation Note is not created.`, indicator: "red" }, 5)
						}
					}
				})
			},__("Create"));
		}

		if(frm.doc.__islocal){
			frm.fields_dict.customer_contact.$wrapper.html('');
			frm.fields_dict.address.$wrapper.html('');
		}
		
		if(frm.doc.customer && !frm.doc.__unsaved)
		{
			get_customer_contact(frm)
			get_customer_address(frm)

			frm.set_query("customer_address",()=>{
				return{
					filters:{
						link_doctype:'Customer',
						link_name:frm.doc.customer
					}
				}
			})
			frm.set_query('contact_person',()=>{
				return {
					filters:{
						link_doctype:'Customer',
						link_name:frm.doc.customer
					}
				}
			})
		}
	},
	"customer":function(frm)
    {
        if(frm.doc.customer)
		{
			frm.set_query("customer_address",()=>{
				return{
					filters:{
						link_doctype:'Customer',
						link_name:frm.doc.customer
					}
				}
			})
			frm.set_query('contact_person',()=>{
				return {
					filters:{
						link_doctype:'Customer',
						link_name:frm.doc.customer
					}
				}
			})
			get_html(frm)
			// if (frm.doc.contact_person)
			// {
			// 	frm.set_value("contact_person","")
			// 	frm.fields_dict.customer_contact.$wrapper.html('');
			// }	
		}
		else{	
			frm.set_value("customer_address","")
			frm.set_value("contact_person","")
			frm.fields_dict.address.$wrapper.html('');
			frm.fields_dict.customer_contact.$wrapper.html('');
		}
		
	},


	"customer_address":function(frm)
	{
		if (frm.doc.customer_address)
		{
			get_customer_address(frm)
			// get_customer_contact(frm)
		}
		else{
			
			frm.fields_dict.address.$wrapper.html('');
			// frm.fields_dict.customer_contact.$wrapper.html('')
			
		}
	},
	"contact_person":function(frm)
	{
		if(frm.doc.contact_person){
			get_customer_contact(frm)
		}
		else{
			frm.fields_dict.customer_contact.$wrapper.html('');
		}
	}
	
});

function get_customer_address(frm)
{
	frappe.call({
		method: 'homegenie_custom_app.homegenie.doctype.installation_request.installation_request.get_address',
	args: {
		"customer_name":frm.doc.customer_address
	},
	callback:function(r)
	{
		if(r.message)
		{
			if(r.message.function=='Success')
			{
				frm.fields_dict.address.$wrapper.html('<div style="border-radius: 6px;background-color: #f4f5f6;padding: 1px 8px;">'+r.message.value+'</div>')
				frm.refresh_field('address')
			}
		}
	}
	})
}

function get_customer_contact(frm)
{
	frappe.call({
		method: 'homegenie_custom_app.homegenie.doctype.installation_request.installation_request.get_contact',
		args: {
			"contact":frm.doc.contact_person
		},
	async:false,
	callback:function(r)
	{
		if(r.message)
		{
			if(r.message.function=='Success')
			{
				if(r.message.mobile){
					frm.fields_dict.customer_contact.$wrapper.html('<div style="border-radius: 6px;background-color: #f4f5f6;padding: 10px 8px;">'+r.message.value.contact_display+ '<br>'+r.message.mobile+'</div>')
				}else{
					frm.fields_dict.customer_contact.$wrapper.html('<div style="border-radius: 6px;background-color: #f4f5f6;padding: 10px 8px;">'+r.message.value.contact_display+'</div>')
				}
				frm.refresh_field('customer_contact')
				frm.refresh_field('contact_person')
			}
		}
	}
	})
}
	



function get_html(frm){

	frappe.call({
		method: 'homegenie_custom_app.homegenie.doctype.installation_request.installation_request.fetch_party_details',
		args: {
			"party":frm.doc.customer
		},
		callback:function(r)
		{
			if(r.message)
			{
				// frm.fields_dict.address.$wrapper.html(r.message.value)
				// frm.fields_dict.customer_contact.$wrapper.html(r.message.value)
				if(r.message.customer_address){
					frm.set_value("customer_address",r.message.customer_address)
				}
				if(r.message.contact_person){
					frm.set_value("contact_person",r.message.contact_person)
				}
			}
		}
	})
}


var change_route = function(frm,doctype, name)
{
	frappe.set_route('Form',doctype, name)
}