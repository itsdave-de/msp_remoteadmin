frappe.ui.form.on('IT Object', {
    refresh: function (frm) {
        if (frm.doc.link) {
            frm.add_custom_button(__('Connect'), function () {
                open_modal(frm);
            });
        }
    }
});

function open_modal(frm) {
    // Protocol options
    const protocol_options = [
        { label: __('RDP'), value: 'RDP' },
        { label: __('SSH'), value: 'SSH' }
    ];
    // Resolutions options
    const resolution_options = [
        { label: __('800x600'), value: '800x600' },
        { label: __('1024x768'), value: '1024x768' },
        { label: __('1280x1024'), value: '1280x1024' },
        { label: __('1440x900'), value: '1440x900' },
        { label: __('1920x1080'), value: '1920x1080' }
    ];
    // Keyboard options
    const keyboard_options = [
        { label: __('Brazilian (Portuguese)'), value: 'pt-br-qwerty' },
        { label: __('English (UK)'), value: 'en-gb-qwerty' },
        { label: __('English (US)'), value: 'en-us-qwerty' },
        { label: __('French'), value: 'fr-fr-azerty' },
        { label: __('French (Belgian)'), value: 'fr-be-azerty' },
        { label: __('French (Swiss)'), value: 'fr-ch-qwertz' },
        { label: __('German'), value: 'de-de-qwertz' },
        { label: __('German (Swiss)'), value: 'de-ch-qwertz' },
        { label: __('Hungarian'), value: 'hu-hu-qwertz' },
        { label: __('Italian'), value: 'it-it-qwerty' },
        { label: __('Japanese'), value: 'ja-jp-qwerty' },
        { label: __('Norwegian'), value: 'no-no-qwerty' },
        { label: __('Spanish'), value: 'es-es-qwerty' },
        { label: __('Spanish (Latin American)'), value: 'es-latam-qwerty' },
        { label: __('Swedish'), value: 'sv-se-qwerty' },
        { label: __('Turkish-Q'), value: 'tr-tr-qwerty' }
    ];

    const dialog = new frappe.ui.Dialog({
        title: __('Connect to Remote'),
        fields: [
            {
                label: __('Protocol'),
                fieldtype: 'Select',
                fieldname: 'protocol',
                options: protocol_options.map(option => option.label)
            },
            {
                label: __('Port'),
                fieldtype: 'Int',
                fieldname: 'port'
            },
            {
                label: __('Resolution'),
                fieldtype: 'Select',
                fieldname: 'resolution',
                options: resolution_options.map(option => option.label)
            },
            {
                label: __('Keyboard Layout'),
                fieldtype: 'Select',
                fieldname: 'keyboard',
                options: keyboard_options.map(option => option.label)
            }
        ],
        primary_action_label: __('Connect'),
        primary_action: () => {
            const values = dialog.get_values();
            if (!values) return;
            frappe.call({
                method: 'msp_remoteadmin.tools.create_session',
                args: {
                    name: frm.doc.name,
                    protocol: values.protocol,
                    port: values.port,
                    resolution: values.resolution,
                    keyboard: values.keyboard
                },
                callback: r => {
                    if (r.message) {
                        const url = r.message;
                        var resolution = values.resolution.split('x');
                        window.open(url, 'GuacamoleConsole', 'width=' + resolution[0] + ',height=' + resolution[1]);
                    }
                }
            });
            dialog.hide();
        }
    });
    dialog.show();
}
