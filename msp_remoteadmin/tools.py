# Copyright (c) 2024, Luiz Costa and contributors
# For license information, please see license.txt

import time
from datetime import datetime
import frappe
from frappe.utils import now
import requests
import urllib.parse

PROTOCOL_PORT = {
    "SSH": 22,
    "RDP": 3389
}

@frappe.whitelist(allow_guest=True)
def log_start_session(session_id, start_time):
    try:
        doc = frappe.get_doc({
            "doctype": "Remote Connection Sessions",
            "id": session_id,
            "start_datetime": datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%f")
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.logger().info(f"Session {session_id} started and saved in Frappe")
        return True
    except Exception as e:
        frappe.logger().error(f"Error saving session {session_id}: {str(e)}")
        return False
    
@frappe.whitelist(allow_guest=True)
def log_end_session(session_id, end_time):
    active_session = frappe.get_all(
        "Remote Connection Sessions",
        filters={
            "id": session_id, 
            "end_datetime": ["is", "not set"]
        },
        fields=["name"]
    )
    if active_session:
        doc = frappe.get_doc("Remote Connection Sessions", active_session[0]["name"])
        doc.end_datetime = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%f")
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.logger().info(f"Session {session_id} ended and updated in Frappe")
        return True
    else:
        frappe.logger().error(f"Session {session_id} not found in Frappe")
        return False

def log_guacamole_session(session_data):
    # Wait for guacamole to create the session
    time.sleep(1.8)
    active_sessions = frappe.get_all(
        "Remote Connection Sessions", 
        filters={
            "protocol": ["is", "not set"],
            "host": ["is", "not set"],
            "user": ["is", "not set"],
            "end_datetime": ["is", "not set"]
        }, 
        fields=["name", "id"]
    )
    for session in active_sessions:
        try:
            doc = frappe.get_doc("Remote Connection Sessions", session["name"])
            doc.it_object = session_data['it_object']
            doc.protocol = session_data['protocol']
            doc.host = session_data['host']
            doc.user = session_data['user']
            doc.ip_user = session_data['ip_user']
            doc.save()
            frappe.db.commit()
            frappe.logger().info(f"Session {session['id']} updated in Frappe")
        except Exception as e:
            frappe.logger().error(f"Error updating session {session['id']}: {str(e)}")

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
            frappe.enqueue(
                log_guacamole_session, 
                queue='short', 
                session_data={
                    'it_object': doc.name,
                    'protocol': protocol,
                    'host': ip_address,
                    'user': frappe.session.user,
                    'ip_user': frappe.local.request_ip
                }
            )
            return { 'url': url, 'resolution': guaca_config.resolution if guaca_config.get('resolution') else '800x600'}
