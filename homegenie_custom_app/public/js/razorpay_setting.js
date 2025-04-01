frappe.ui.form.on("Razorpay Settings", {
    refresh: function (frm) {
         
    }
});
cur_frm.fields_dict.custom_company_configuration.grid.get_field("commission_account_head").get_query  = function (doc, cdt, cdn) {
    const row = locals[cdt][cdn];
    return {
       filters:{
            company:row.r_company
             
        }
    };
}
cur_frm.fields_dict.custom_company_configuration.grid.get_field("cost_center").get_query  = function (doc, cdt, cdn) {
    const row = locals[cdt][cdn];
    return {
       filters:{
            company:row.r_company
             
        }
    };
}
cur_frm.fields_dict.custom_company_configuration.grid.get_field("paid_to_account").get_query  = function (doc, cdt, cdn) {
    const row = locals[cdt][cdn];
    return {
       filters:{
            company:row.r_company,
            account_type:["in",["Bank","Cash"]]
             
        }
    };
}