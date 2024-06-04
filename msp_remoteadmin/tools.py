# Copyright (c) 2024, Luiz Costa and contributors
# For license information, please see license.txt

import time
import frappe
from frappe.utils import now
import requests
import urllib.parse

PROTOCOL_PORT = {
    "SSH": 22,
    "RDP": 3389
}

def log_guacamole_session(url, protocol, host, user):
    # Wait for guacamole to create the session
    time.sleep(1.2)
    # Debug
    print(f"DEBUG: New session -> Protocol: {protocol} :: Host: {host} :: User: {user}")
    # Set guacamole url
    guacamole_url = url.replace('https:', 'http:').replace('/guacamole', '')
    # Get last id created on guacamole
    last_id = requests.get(f'{guacamole_url}:8085/last_id')
    if last_id.status_code == 200:
        last_id = last_id.json()['last_id']
        # add log session
        doc = frappe.new_doc('Remote Connection Sessions')
        doc.id = last_id
        doc.protocol = protocol
        doc.host = host
        doc.user = user
        doc.start_datetime = time.strftime('%Y-%m-%d %H:%M:%S')
        doc.insert()
        doc.save()
        frappe.db.commit()
        frappe.logger().info(f"Session {last_id} created and updated in Frappe")
    else:
        last_id = 0

@frappe.whitelist(allow_guest=True)
def check_session_status():
    # URL from guacamole server
    guaca_config = frappe.get_single('Remote Connections Settings')
    guacamole_url = guaca_config.guacamole_server.replace('https:', 'http:').replace('/guacamole', '')
    
    # Get all active sessions in "Remote Connection Sessions" Doctype
    active_sessions = frappe.get_all("Remote Connection Sessions", filters={"end_datetime": ["is", ""]}, fields=["name", "id"])
    
    for session in active_sessions:
        session_id = session["id"]
        try:
            response = requests.get(f"{guacamole_url}:8085/session/{session_id}")
            response_data = response.json()
            
            # Verify if the session was ended
            if "end" in response_data.keys():
                # Update the "end_datetime" field of the corresponding document
                doc = frappe.get_doc("Remote Connection Sessions", session["name"])
                doc.end_datetime = now()
                doc.save()
                frappe.db.commit()
                frappe.logger().info(f"Session {session_id} ended and updated in Frappe")
        except Exception as e:
            frappe.logger().error(f"Error checking session {session_id}: {str(e)}")


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
            frappe.enqueue(log_guacamole_session, queue='short', url=guaca_config.guacamole_server, protocol=protocol, ip_address=ip_address, user=frappe.session.user)
            return { 'url': url, 'resolution': guaca_config.resolution if guaca_config.get('resolution') else '800x600'}
