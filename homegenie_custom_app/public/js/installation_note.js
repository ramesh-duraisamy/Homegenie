frappe.ui.form.on('Installation Note',{
	refresh: function(frm){
		if (frm.doc.customer_address){
			get_customer_address(frm)
			frm.refresh_field('custom_address')
		} else {
			frm.set_value("customer_address","")
			frm.fields_dict.custom_address.$wrapper.html('');
			frm.refresh_field('custom_address')
		}
		if (frm.doc.contact_person){
			get_customer_contact(frm)
			frm.refresh_field('custom_contacts')
		} else {
			frm.set_value("contact_person","")
			frm.fields_dict.custom_contacts.$wrapper.html('');
			frm.refresh_field('custom_contacts')
		}

		// Display the activities tab
		const crm_activities = new erpnext.utils.CRMActivities({
			frm: frm,
			open_activities_wrapper: $(frm.fields_dict.custom_open_activities_html.wrapper),
			all_activities_wrapper: $(frm.fields_dict.custom_all_activities_html.wrapper),
			form_wrapper: $(frm.wrapper),
		});
		crm_activities.refresh();
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
			// if (frm.doc.customer_address){
			// 	get_customer_address(frm)
			// }
			// if(frm.doc.contact_person){
			// 	get_customer_contact(frm)
			// }

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
    customer_address(frm){
		if (frm.doc.customer_address){
			get_customer_address(frm)
			frm.refresh_field('custom_address')
		} else {
			frm.set_value("customer_address","")
			frm.fields_dict.custom_address.$wrapper.html('');
			frm.refresh_field('custom_address')
		}
        // console.log(frm.doc.customer_address)
    },
    contact_person(frm){
		if (frm.doc.contact_person){
			get_customer_contact(frm)
			frm.refresh_field('custom_contacts')
		} else {
			frm.set_value("contact_person","")
			frm.fields_dict.custom_contacts.$wrapper.html('');
			frm.refresh_field('custom_contacts')
		}
    }
})

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
					frm.fields_dict.custom_contacts.$wrapper.html('<div style="border-radius: 6px;background-color: #f4f5f6;padding: 10px 8px;">' + r.message.value.contact_display + '<br>' + r.message.mobile + '</div>')
				}else{
					frm.fields_dict.custom_contacts.$wrapper.html('<div style="border-radius: 6px;background-color: #f4f5f6;padding: 10px 8px;">' + r.message.value.contact_display + '</div>')
				}
				// console.log("Test", r.message.value.contact_display)
				// frm.refresh_field('contact_person')
			}
		}
	}
	})
}

function get_customer_address(frm)
{
	frappe.call({
		method: 'homegenie_custom_app.homegenie.doctype.installation_request.installation_request.get_address',
	args: {
		"customer_name":frm.doc.customer_address
	},
	async:false,
	callback:function(r)
	{
		if(r.message)
		{
			if(r.message.function=='Success')
			{
				frm.fields_dict.custom_address.$wrapper.html('<div style="border-radius: 6px;background-color: #f4f5f6;padding: 1px 8px;">'+r.message.value+'</div>')
				console.log("Address is added")
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
		async:false,
		callback:function(r)
		{
			if(r.message)
			{
				console.log(r.message)
				// frm.fields_dict.address.$wrapper.html(r.message.value)
				// frm.fields_dict.customer_contact.$wrapper.html(r.message.value)
				if(r.message.customer_address){
					frm.set_value("customer_address",r.message.customer_address)
					// get_customer_address(frm)
				}
				if(r.message.contact_person){
					frm.set_value("contact_person",r.message.contact_person)
					// get_customer_contact(frm)
				}
			}
		}
	})
}
