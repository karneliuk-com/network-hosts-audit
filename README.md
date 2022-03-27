# Network Host Lookup
Real world tool to dump all the IPv4 hosts in your network and find where they are connected (to which access switch) assuming that interface description is correct (the latter can easily be replaced with LLDP or CDP data, if available).

## Used Frameworks
- Nornir
- Scrapli (Nornir tasks)

## Why not NAPALM?
This tool was created for a particular real-world environment, where upgrade of the software version was not possible. We tried to use NAPALM, but it failed to pull ARP table from network switches running Arista EOS.

## Usage
1. Populate inventory following Nornir's SimpleInventory:
```
$ cat inventory/hosts.yaml
---
core1-row1:
  hostname: 192.168.255.11
  groups:
    - core
access1-row13
  hostname: 192.168.255.101
  groups:
    - access
...


$ cat inventory/groups.yaml
---
core:
  platform: eos
  data:
    role: core
access:
  platform: ios
  data:
    role: access
...

$ cat inventory/defaults.yaml
---
username: test
password: test
## Add scrapli details
connection_options:
  scrapli:
    port: 22
    extras:
      ssh_config_file: True
      auth_strict_key: False
...
```

2. To see all IPs/MACs in the network, run it with `-a` argument:
```
$ python main.py -c environment -a
178 results found:
{
    "192.168.1.11": {
        "interface": "GigabitEthernet1/17",
        "mac": "ac1f.6b21.ed22",
        "server": "HYPERVISOR-1",
        "switch": "access1-row13",
        "vlan": 100
    }
    ,
    ...
}
```

3. To find a specific IP in the network, run it with `-q ip=x.x.x.x` argument:
```
$ python main.py -c environment -q ip=192.168.1.11
3 results found:
{
    "192.168.1.11": {
        "interface": "GigabitEthernet1/17",
        "mac": "ac1f.6b21.ed22",
        "server": "HYPERVISOR-1",
        "switch": "access1-row13",
        "vlan": 100
    }
}
```

4. To find a specific MAC in the network, run it with `-q mac=aaaa.bbbb.cccc` argument:
```
$ python main.py -c environment -q mac=ac1f.6b21.ed22
3 results found:
{
    "192.168.1.11": {
        "interface": "GigabitEthernet1/17",
        "mac": "ac1f.6b21.ed22",
        "server": "HYPERVISOR-1",
        "switch": "access1-row13",
        "vlan": 100
    },
    "192.168.1.12": {
        "interface": "GigabitEthernet1/17",
        "mac": "ac1f.6b21.ed22",
        "server": "HYPERVISOR-1",
        "switch": "access1-row13",
        "vlan": 100
    },
    "192.168.1.13": {
        "interface": "GigabitEthernet1/17",
        "mac": "ac1f.6b21.ed22",
        "server": "HYPERVISOR-1",
        "switch": "access1-row13",
        "vlan": 100
    }
}
```

## 