# check_brevisone

Plugin to check signal strength of Braintower SMS gateways.

Important Note:
>Since BASIS Europe acquired the Braintower SMS Gateways business, the distribution
>and development will be continued under the new brandname brevis.one. The Plugin functionality
>and code of check_braintower stays the same, except for the new name: check_brevisone
>
>For more information see: [brevis.one](https://brevis.one/en/), [BASIS europe](https://www.basis-europe.eu/)

# Installation

Debian/Ubuntu:

    apt install python-requests
    
RHEL/CentOS 7:

    yum install python-requests

# Usage

    usage: check_brevisone [-h] -H HOSTNAME [-T TIMEOUT] [-Q QUEUE] [-F FAIL]
                        [--signal-warning SIGNAL_WARNING]
                        [--signal-critical SIGNAL_CRITICAL] [--ssl-insecure]
                        [--protocol PROTOCOL]

# Example

    ./check_brevisone -H 192.168.1.1 --signal-warning -85 --signal-critical -90
    
    BREVISONE OK - que: 0 failed: 0 signal: -83db total: 0 state: Idle load: 0;0.03;0.05 time: 1451320254 disk free: 647569408 uptime: 9 min, 0 users

# Advanced

To connect to the HTTP endpoint (unencrypted) you can use ```--protocol=http```. Since firmware version 4.0 HTTPS is the
default. I you using self-certified certificates on the appliance, use ```--ssl-insecure``` to disable verification. 

# Copyright

(c) 2020, [NETWAYS GmbH](http://www.netways.de), info@netways.de

# License

GPL Version 2, see head of the plugin file for more information.

# Version

1.4.2
