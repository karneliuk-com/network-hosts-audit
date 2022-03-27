#! /usr/bin/env python

# Modules
from nornir import InitNornir
from nornir_scrapli.tasks import send_command
from nornir_utils.plugins.functions import print_result
import json
import datetime


# Local artefacts
import bin.helper_functions as hf


# Variables
config_file = "./config.yaml"


# Body
if __name__ == "__main__":
    ## Initail timestamp
    t1 = datetime.datetime.now()

    ## Get args
    args = hf.get_args()

    ## Initiate Nornir
    nr = InitNornir(config_file=config_file)
    
    ## Update creds
    user_creds = hf.get_credentials(creds_type=args.credentials)
    if user_creds:
        nr.inventory.defaults.username, nr.inventory.defaults.password = user_creds

    ## Collect ARP from core
    nr_core = nr.filter(role="core")
    r1 = nr_core.run(task=send_command, command="show ip arp")

    ## Validate collected ARP
    if args.verbose:
        print_result(r1)

    ## Normalise ARP
    arp_table = hf.get_unique_hosts(arp_table=r1)

    ## Collect MAC from access
    nr_access = nr.filter(role="access")
    r2 = nr_access.run(task=send_command, command="show mac address-table")
    
    ## Validated collected MAC
    if args.verbose:
        print_result(r2)

    ## Collect Interface description
    r3 = nr_access.run(task=send_command, command="show interface description")

    ## Validated collected MAC
    if args.verbose:
        print_result(r3)

    ## Map all the data
    final_mapping = hf.match_ip_mac_port_description(arp_table=arp_table,
                                                     mac_table=r2, interfaces_table=r3)
    
    ## Final timestamp
    t2 = datetime.datetime.now()

    ## Print results
    if args.all:
        print(json.dumps(final_mapping, indent=4, sort_keys=True))

    if args.query:
        search_result = hf.data_lookup(dict_for_lookup=final_mapping, query=args.query)

        print(f"{len(search_result)} results found:")
        print(json.dumps(search_result, indent=4, sort_keys=True))

    print(f"\n\n\nCompleted in {t2 - t1}\n\n\n")