frappe.ui.form.on('Company',{
    refresh:function(frm){
        setTimeout(() => {
            $('[data-label="Delete%20Transactions"]').hide()
        }, 1000);
        frm.add_custom_button(__("Delete Company Transactions"), function() {
            frm.trigger("hg_delete_company_transactions");
        })
    },
    hg_delete_company_transactions: function (frm) {
        frappe.call({
            method: "homegenie_custom_app.homegenie.doctype.homegenie_transaction_deletion_record.homegenie_transaction_deletion_record.is_deletion_doc_running",
            args: {
                company: frm.doc.name,
            },
            freeze: true,
            callback: function (r) {
                if (!r.exc) {
                    frappe.verify_password(function () {
                        var d = frappe.prompt(
                            {
                                fieldtype: "Data",
                                fieldname: "company_name",
                                label: __("Please enter the company name to confirm"),
                                reqd: 1,
                                description: __(
                                    "Please make sure you really want to delete all the transactions for this company. Your master data will remain as it is. This action cannot be undone."
                                ),
                            },
                            function (data) {
                                if (data.company_name !== frm.doc.name) {
                                    frappe.msgprint(__("Company name not same"));
                                    return;
                                }
                                frappe.call({
                                    method: "homegenie_custom_app.homegenie.api.create_transaction_deletion_request",
                                    args: {
                                        company: data.company_name,
                                    },
                                    freeze: true,
                                    callback: function (r, rt) {},
                                    onerror: function () {
                                        frappe.msgprint(__("Wrong Password"));
                                    },
                                });
                            },
                            __("Delete all the Transactions for this Company"),
                            __("Delete")
                        );
                        d.get_primary_btn().addClass("btn-danger");
                    });
                }
            },
        });
    }
})