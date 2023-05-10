# check_brevisone

Plugin to check signal strength and availability of the [Brevis.One SMS gateway](https://brevis.one).

This plugin was previously known as check_braintower, it was renamed due to a product name change.
You should be able to check gateways running older versions as well.

## Installation

The plugin requires at least Python 3.

## Usage

```
check_brevisone [-h] -H HOSTNAME [-T TIMEOUT] [-Q QUEUE] [-F FAIL]
       [--signal-warning SIGNAL_WARNING]
       [--signal-critical SIGNAL_CRITICAL] [--ssl-insecure]
       [--protocol PROTOCOL]
```

## Example

```
check_brevisone -H 192.168.1.1 --signal-warning -85 --signal-critical -90

OK - que: 0 failed: 0 signal: -83db total: 0 state: Idle load: 0;0.03;0.05 time: 1451320254 disk free: 647569408 uptime: 9 min, 0 users
```

## Advanced

Since firmware version 4.0 HTTPS is the default. To connect to a unencrypted HTTP endpoint you can use ```--protocol=http```.

I you are using a self-certified certificate, use ```--ssl-insecure``` to disable verification.

# License

Copyright (C) 2020 [NETWAYS GmbH](mailto:info@netways.de)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
