frappe.ui.form.on('Sales Invoice',{
    refresh:function(frm)
    {
        if(frm.doc.docstatus==1)
        {
            frm.add_custom_button(__("Installation Note"),function(){
                console.log("working")
                frappe.call({
					method: 'homegenie_custom_app.homegenie.api.create_installation_note',
					args: {'name':cur_frm.doc.name},
                    async: false,
					callback:function(r){
						if(r.message.function=='Success'){
							// console.log("Ok")
                            change_route(frm,r.message.doctype,r.message.value)
						}
						else{
							// console.log("not ok")
                            frappe.msgprint({ message: `Installation Note is not created.`, indicator: "red" }, 5)
						}
					}
				})
			},__("Create"));
        }
        if(cur_frm.doc.outstanding_amount>0 && frm.doc.docstatus==1){
	    	frm.add_custom_button(__("Send Payment Link"), function() {
	            frappe.call({
					method: 'homegenie_custom_app.homegenie.razorpay.create_payment_link',
					args: {'dt':cur_frm.doc.doctype,"docname":cur_frm.doc.name},
                    async: false,
					callback:function(r){
						if(r.message.status=='Success'){
                            frappe.msgprint({ message:r.message.message})
						}
						else{
							// console.log("not ok")
                            frappe.msgprint({ message: "Something went wrong."})
						}
					}
				})
	    	})
	    }
    }
    
    
})

var change_route = function(frm,doctype, name)
{
	frappe.set_route('Form',doctype, name)
}
