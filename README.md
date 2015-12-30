# check_braintower

Plugin to check signal strength of Braintower SMS gateways.

# Usage

    usage: check_braintower [-h] -H HOSTNAME [-T TIMEOUT] [-Q QUEUE] [-F FAIL]
                        [--signal-warning SIGNAL_WARNING]
                        [--signal-critical SIGNAL_CRITICAL]

# Example

    ./check_braintower -H 192.168.1.1 --signal-warning -85 --signal-critical -90
    
    BRAINTOWER OK - que: 0 failed: 0 signal: -83db total: 0 state: Idle load: 0;0.03;0.05 time: 1451320254 disk free: 647569408 uptime: 9 min, 0 users

# Copyright

(c) 2015, [NETWAYS GmbH](http://www.netways.de), info@netways.de

# License

GPL Version 2, see head of the plugin file for more information.

# Version

1.0

