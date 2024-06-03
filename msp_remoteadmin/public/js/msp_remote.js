frappe.ui.form.on('IT Object', {
    refresh: function (frm) {
        if (frm.doc.link) {
            frm.add_custom_button(__('RDP'), function () {
                connect_remote(frm, 'RDP');
            }, __("Connect"));

            frm.add_custom_button(__('SSH'), function () {
                connect_remote(frm, 'SSH');
            }, __("Connect"));

        }
    }
});

function connect_remote(frm, type) {
    frappe.call({
        method: "msp_removeadmin.tools.create_session",
        args: {
            doc: frm.doc,
            protocol: type
        },
        callback: function (r) {
            if (r.message) {
                var url = r.message;
                window.open(url, 'GuacamoleConsole', 'width=1024,height=768');
            }
        }
    })
}
