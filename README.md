# check_braintower

Plugin to check signal strength of Braintower SMS gateways.

# Installation

Debian/Ubuntu:

    apt install python-requests
    
RHEL/CentOS 7:

    yum install python-requests

# Usage

    usage: check_braintower [-h] -H HOSTNAME [-T TIMEOUT] [-Q QUEUE] [-F FAIL]
                        [--signal-warning SIGNAL_WARNING]
                        [--signal-critical SIGNAL_CRITICAL] [--ssl-insecure]
                        [--protocol PROTOCOL]

# Example

    ./check_braintower -H 192.168.1.1 --signal-warning -85 --signal-critical -90
    
    BRAINTOWER OK - que: 0 failed: 0 signal: -83db total: 0 state: Idle load: 0;0.03;0.05 time: 1451320254 disk free: 647569408 uptime: 9 min, 0 users

# Advanced

To connect to the HTTP endpoint (unencrypted) you can use ```--protocol=http```. Since firmware version 4.0 HTTPS is the
default. I you using self-certified certificates on the appliance, use ```--ssl-insecure``` to disable verification. 

# Copyright

(c) 2018, [NETWAYS GmbH](http://www.netways.de), support@netways.de

# License

GPL Version 2, see head of the plugin file for more information.

# Version

1.4.2
