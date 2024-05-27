# zabbix-update-hostgroups
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
