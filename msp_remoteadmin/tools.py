# Copyright (c) 2024, Luiz Costa and contributors
# For license information, please see license.txt

import frappe
import requests
import urllib.parse

PROTOCOL_PORT = {
    "SSH": 22,
    "RDP": 3389
}

@frappe.whitelist()
def create_session(name, protocol):
    guaca_config = frappe.get_single('Remote Connections Settings')
    guacamole_api = f'{guaca_config.guacamole_server}/api/tokens'
    auth = {
        'username': guaca_config.guacamole_user,
        'password': guaca_config.get_password('guacamole_pass')
    }
    response = requests.post(guacamole_api, data=auth)
    
    print(f"Response CODE: {response.status_code}\nResponde Content: {response.text}")
    
    if response.status_code == 200:
        try:
            token = response.json()['authToken']
        except:
            print("Error: Could not get token")
            token = None
        if token:
            # Get values from IT Object
            doc = frappe.get_doc('IT Object', name)
            # Get credentials from IT User Account
            acc_doc = frappe.get_doc('IT User Account', doc.get('link'))
            username = acc_doc.username
            password = acc_doc.get_password('password')
            domain = acc_doc.get('domain') if acc_doc.get('domain') else None
            # Get IP
            ip_doc = frappe.get_doc('IP Address', doc.get('main_ip'))
            ip_address = ip_doc.ip_address
            
            uri = f"{protocol.lower()}://{ip_address}{':' + str(PROTOCOL_PORT[protocol])}"
            if protocol == 'RDP':
                params = []
                if username:
                    params.append(f"username={username}")
                if password:
                    params.append(f"password={password}")
                if domain:
                    params.append(f"domain={domain}")
                if guaca_config.get('keyboard_layout'):
                    params.append(f"server-layout={guaca_config.keyboard_layout}")
                if params:
                    uri = f"{uri}/?ignore-cert=true&disable-audio=true&{'&'.join(params)}"
            elif protocol == 'SSH':
                params = []
                if username:
                    params.append(f"username={username}")
                if password:
                    params.append(f"password={password}")
                if params:
                    uri = f"{uri}/?{'&'.join(params)}"
            url = f'{guaca_config.guacamole_server}/?#/?token={token}&quickconnect={urllib.parse.quote(uri)}'
            return { 'url': url, 'resolution': guaca_config.resolution if guaca_config.get('resolution') else '800x600'}
