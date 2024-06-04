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
        method: "msp_remoteadmin.tools.create_session",
        args: {
            name: frm.doc.name,
            protocol: type
        },
        callback: function (r) {
            if (r.message) {
                var url = r.message.url;
                resolution = r.message.resolution.split('x');
                window.open(url, 'GuacamoleConsole', 'width=' + resolution[0] + ',height=' + resolution[1]);
            }
        }
    })
}
