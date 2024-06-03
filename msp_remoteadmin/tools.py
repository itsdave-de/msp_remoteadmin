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
def create_session(doc, protocol):
    guaca_config = frappe.get_single('Remote Connections Settings')
    guacamole_url = f'{guaca_config.guacamole_server}/api/tokens'
    auth = {
        'username': guaca_config.guacamole_user,
        'password': guaca_config.get_password('guacamole_pass')
    }
    response = requests.post(guacamole_url, data=auth)
    
    print(f"Response CODE: {response.status_code}\nResponde Content: {response.text}")
    
    if response.status_code == 200:
        try:
            token = response.json()['authToken']
        except:
            print("Error: Could not get token")
            token = None
        if token:
            print(f"Token: {token}")
            # Get credentials from IT User Account
            print(f"Values from form: {doc}")
            print(f"Type: {type(doc.link)}")
            acc_doc = frappe.get_doc('IT User Account', doc.link)
            print(f"Print doc values: {acc_doc}")
            username = acc_doc.username
            password = acc_doc.get_password('password')
            
            uri = urllib.parse.quote_plus(f"{protocol}://{username if username else ''}{':' + password if password else ''}@{doc.main_ip}{':' + PROTOCOL_PORT[protocol]}").lower()
            if protocol == 'RDP':
                uri = f"{uri}/?ignore-cert=true&disable-audio=true"
            url = f'{guacamole_url}/?#/?token={token}&quickconnect={uri}'
            return url
