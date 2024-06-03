frappe.ui.form.on('IT Object', {
    refresh: function (frm) {
        // Verifica se todos os campos necessários estão preenchidos
        if (frm.doc.link) {
            // Adiciona o botão "Connect"
            frm.add_custom_button(__('Connect'), null, 'btn-default', null, 'btn-connect');
            frm.page.add_menu_item(__('RDP'), function () {
                connect_remote(frm, 'RDP');
            }, 'btn-connect');

            frm.page.add_menu_item(__('SSH'), function () {
                connect_remote(frm, 'SSH');
            }, 'btn-connect');
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
