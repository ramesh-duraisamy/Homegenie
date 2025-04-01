frappe.ui.form.on('Customer',{
   refresh:function(frm){
    const crm_activities = new erpnext.utils.CRMActivities({
        frm: frm,
        open_activities_wrapper: $(frm.fields_dict.custom_open_activities_html.wrapper),
        all_activities_wrapper: $(frm.fields_dict.custom_all_activities_html.wrapper),
        form_wrapper: $(frm.wrapper),
    });
    crm_activities.refresh();
    }
})

frappe.ui.form.on('Maintenance Visit',{
    refresh:function(frm){
     const crm_activities = new erpnext.utils.CRMActivities({
         frm: frm,
         open_activities_wrapper: $(frm.fields_dict.custom_open_activities_html.wrapper),
         all_activities_wrapper: $(frm.fields_dict.custom_all_activities_html.wrapper),
         form_wrapper: $(frm.wrapper),
     });
     crm_activities.refresh();
     }
 })

 frappe.ui.form.on('Installation Note',{
    refresh:function(frm){
     const crm_activities = new erpnext.utils.CRMActivities({
         frm: frm,
         open_activities_wrapper: $(frm.fields_dict.custom_open_activities_html.wrapper),
         all_activities_wrapper: $(frm.fields_dict.custom_all_activities_html.wrapper),
         form_wrapper: $(frm.wrapper),
     });
     crm_activities.refresh();
     }
 })

 frappe.ui.form.on('Issue',{
    refresh:function(frm){
     const crm_activities = new erpnext.utils.CRMActivities({
         frm: frm,
         open_activities_wrapper: $(frm.fields_dict.custom_open_activities_html.wrapper),
         all_activities_wrapper: $(frm.fields_dict.custom_all_activities_html.wrapper),
         form_wrapper: $(frm.wrapper),
     });
     crm_activities.refresh();
     }
 })