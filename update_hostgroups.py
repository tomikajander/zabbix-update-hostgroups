"""
This script is designed to update Zabbix host groups for specified hosts. It performs the following steps:

1. Fetches all hosts within a specified host group.
2. Removes all current members from this host group.
3. Updates the specified host group with a list of new server names provided via command-line arguments.

The script interacts with the Zabbix API, using JSON-RPC for communication. The user needs to provide a valid Zabbix API token and the host group ID to be updated. 
The hostgroupid and API token are set manually within the script.

Functions:
- get_hosts_in_group(host_group_id): Retrieves the list of hostids in a specified host group.
- remove_all_members_from_host_group(host_group_id, host_ids): Removes all hosts from a specified host group.
- update_host_group(server_names): Updates the host group with the new list of server names.

Usage:
    python3 update_hostgroups.py [Server1, Server2, Server3 ...]

Arguments:
    SERVER: List of hostnames to update in the host group.

Example:
    python update_hostgroups.py server1 server2 server3

Author:
    Tomi Kajander 
Date:    
    27.5.2024
"""

import argparse
import requests
import json

token = "ADD_TOKEN_HERE"
host_group_id = 9999 # Add hostgrouid here
api_url = 'https://your-zabbix-url.com/zabbix/api_jsonrpc.php'

def get_hosts_in_group(host_group_id):
    zabbix_url = api_url
    headers = {'Content-Type': 'application/json'}

    get_hosts_payload = {
        'jsonrpc': '2.0',
        'method': 'host.get',
        'params': {
            'output': ['hostid'],
            'groupids': host_group_id,
            'selectGroups': 'extend'
        },
        'auth': token,
        'id': 1
    }

    response = requests.post(zabbix_url, data=json.dumps(get_hosts_payload), headers=headers)
    result = response.json()

    if 'error' in result:
        print(f"Failed to get hosts in group '{host_group_id}':", result['error']['data'])
        return None
    else:
        return [host['hostid'] for host in result['result']]

def remove_all_members_from_host_group(host_group_id, host_ids):
    zabbix_url = api_url
    headers = {'Content-Type': 'application/json'}

    if not host_ids:
        print("No hosts found in the specified host group. Continuing.")
        return

    # Construct the payload for hostgroup.massremove method
    remove_payload = {
        'jsonrpc': '2.0',
        'method': 'hostgroup.massremove',
        'params': {
            'groupids': host_group_id,
            'hostids': host_ids
        },
        'auth': token,
        'id': 2
    }

    # Send the request to remove all members from the host group
    response = requests.post(zabbix_url, data=json.dumps(remove_payload), headers=headers)
    result = response.json()

    if 'error' in result:
        print(f"Failed to remove members from host group '{host_group_id}':", result['error']['data'])
    else:
        print(f"All members removed from host group '{host_group_id}'.")

def update_host_group(server_names):

    # Get all hosts in the specified host group
    host_ids = get_hosts_in_group(host_group_id)

    # Remove all members from the specified host group
    remove_all_members_from_host_group(host_group_id, host_ids)

    if not host_ids:
        print("No hosts found in the specified host group.")

    zabbix_url = api_url
    headers = {'Content-Type': 'application/json'}

    # Remove all members from the specified host group
    remove_all_members_from_host_group(host_group_id, server_names)

    for server_name in server_names:
        # Find the host ID for the server
        get_host_payload = {
            'jsonrpc': '2.0',
            'method': 'host.get',
            'params': {
                'output': ['hostid'],
                'selectGroups': 'extend',
                'search': {'host': [server_name]}
            },
            'auth': token,
            'id': 3
        }
        host_response = requests.post(zabbix_url, data=json.dumps(get_host_payload), headers=headers)

        host_result = host_response.json()

        if 'error' in host_result:
            print(f"Failed to get host ID for '{server_name}':", host_result['error']['data'])
            continue

        if not host_result['result']:
            print(f"Host '{server_name}' not found in Zabbix.")
            continue

        host_id = host_result['result'][0]['hostid']
        current_groups = host_result['result'][0]['groups']

        # Append the new host group to the existing ones
        current_groups_ids = [group['groupid'] for group in current_groups]
        current_groups_ids.append(host_group_id)

        # Update the host's group
        update_host_payload = {
            'jsonrpc': '2.0',
            'method': 'host.update',
            'params': {
                'hostid': host_id,
                'groups': [{'groupid': group_id} for group_id in current_groups_ids]
            },
            'auth': token,
            'id': 4
        }
        update_response = requests.post(zabbix_url, data=json.dumps(update_host_payload), headers=headers)
        update_result = update_response.json()

        if 'error' in update_result:
            print(f"Failed to update host '{server_name}' to group '{host_group_id}':", update_result['error']['data'])
        else:
            print(f"Updated host '{server_name}' to group '{host_group_id}' along with existing groups.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Update Zabbix host groups for hosts.')
    parser.add_argument('hosts', metavar='SERVER', type=str, nargs='+',
                        help='List of server names to update')
    args = parser.parse_args()

    update_host_group(args.hosts)