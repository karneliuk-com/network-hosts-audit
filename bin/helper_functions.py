# Modules
import re
from argparse import ArgumentParser
from getpass import getpass
import os


# Functions
def get_args():
    """
    This helper function helps to control the execution of the tool via the CLI arguments.
    """
    parser = ArgumentParser()

    parser.add_argument(
        "-a", "--all",
        action="store_true",
        default=False,
        help="Dump all the IP addresses."
    )

    parser.add_argument(
        "-q", "--query",
        type=str,
        required=False,
        default="",
        help="Specify the IP (ip=192.168.1.1) or MAC (mac=aaaa.bbbb.cccc) address you are willing to look for."
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=False,
        help="Specify if you need to see Nornir detaild output."
    )

    parser.add_argument(
        "-c", "--credentials",
        type=str,
        required=False,
        default="inventory",
        choices = ["environment", "inventory", "cli"],
        help="Specify the IP address you are willing to find."
    )


    return parser.parse_args()


def get_credentials(creds_type: str) -> tuple:
    """
    This helper function allows the specify the credentials in a ways 
    different to putting them in a clear text in the configuration file.
    """
    result = ()

    if creds_type == "environment":
        result = (os.getenv("AUTOMATION_USERNAME"), os.getenv("AUTOMATION_PASSWORD"))

    elif creds_type == "cli":
        result = (input("Provide username > "), getpass("Provide password > "))

    return result


def get_unique_hosts(arp_table) -> dict:
    """
    This helper function performs conversion of the ARP table into a dictionary.
    """
    return _normalise_data(raw_input=arp_table, 
                           unique_field=0, 
                           mapping={"mac": 2}, 
                           filter=["Address"])


def match_ip_mac_port_description(arp_table: dict, mac_table, interfaces_table) -> dict:
    """
    This helper function performs conversion of the MAC address tables, 
    interfaces description table, and collected ARP in a singe dictionary.
    """
    result = arp_table

    normailed_mac_table = _normalise_data(raw_input=mac_table, 
                                          unique_field=1, 
                                          mapping={"vlan": 0, "interface": -1}, 
                                          filter=["Entries", "mac", "EOF", "ffff.ffff.ffff"])

    normalized_interface_table = _normalise_data(raw_input=interfaces_table, 
                                                 unique_field=0, 
                                                 mapping={"description": -1}, 
                                                 filter=["Interface"],
                                                 add_host=True)

    for ip_entry, ip_var in arp_table.items():
        to = {}

        if ip_var["mac"] in normailed_mac_table:
            pre_normalized_interface = normailed_mac_table[ip_var["mac"]]["interface"].split(",")
            normalized_interface_name = pre_normalized_interface[0] + "," + pre_normalized_interface[1][0:2] + re.sub(r'^\D+(\d?/?\d+)$', r'\1',   pre_normalized_interface[1])
            
            if normalized_interface_name in normalized_interface_table and not re.match(r'.*Po.*', pre_normalized_interface[1]):
                to= {
                        "switch": pre_normalized_interface[0], 
                        "interface": pre_normalized_interface[1], 
                        "vlan": int(normailed_mac_table[ip_var["mac"]]["vlan"]),
                        "server": normalized_interface_table[normalized_interface_name]["description"]
                    }

        if not to:
            to= {
                    "switch": None, 
                    "interface": None, 
                    "vlan": None,
                    "server": None
                }

        result[ip_entry].update(to)

    return result


def _normalise_data(raw_input, unique_field: int, mapping: dict, filter: list, add_host: bool = False) -> dict:
    """
    This helper functions allows to convery semi-formatted text into a structure 
    dictionary by choosing a key field and other important fields for nested data.
    """
    result = {}

    for hostname, entry_1_level in raw_input.items():
        for entry_2_level in str(entry_1_level[0]).splitlines():
            list_3_level = entry_2_level.split()

            try:
                if list_3_level[unique_field] not in result and list_3_level[unique_field] not in filter:
                    if "interface" not in mapping or not re.match(r'.*Po.*',list_3_level[mapping["interface"]]):
                        key_field = list_3_level[unique_field] if not add_host else f"{hostname},{list_3_level[unique_field]}"

                        result.update({key_field: {}})

                        for key_name, key_index in mapping.items():
                            value = f"{hostname},{list_3_level[key_index]}" if key_name == "interface" else list_3_level[key_index]
                                
                            result[key_field].update({key_name: value})

            except:
                pass

    return result


def data_lookup(dict_for_lookup: dict, query: str) -> dict:
    """
    This helper functions performs a data lookup in a provided dictionary based on a provided argument.
    """
    result = {}

    query = query.split("=")

    if query[0] == "ip":
        if query[1] in dict_for_lookup:
            result.update({query[1]: dict_for_lookup[query[1]]})

    elif query[0] == "mac":
        for ip_address, ip_vars in dict_for_lookup.items():
            if ip_vars["mac"] == query[1]:
                result.update({ip_address: ip_vars})

    else:
        print("Unsupported query type")

    return result