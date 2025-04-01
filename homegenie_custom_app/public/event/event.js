// frappe.ui.form.on('Event',{
//     before_save:function(frm){
//         if(frm.doc.custom_visit == 0){
      
//         frm.set_value("custom_visit",1)
//         frappe.call({
//             method:'homegenie_custom_app.public.event.event.create_visit',
//             args:{
//                 Date:frm.doc.starts_on,
//                 source:frm.doc.custom_location,
//                 event_id:frm.doc.name
//             },
//             callback:(r)=>{
//               console.log(r)
//             }

//     })

// }
//     }
// })
