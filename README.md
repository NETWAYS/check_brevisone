# check_brevisone

Plugin to check signal strength and availability of the [Brevis.One SMS gateway](https://brevis.one).

This plugin was previously known as check_braintower, it was renamed due to a product name change.
You should be able to check gateways running older versions as well.

## Installation

The plugin requires at least Python 3.

## Usage

```
usage: check_brevisone.py [-h] [-V] -H HOSTNAME [-T TIMEOUT] [--ssl-insecure] [--protocol {http,https}] [-d] [--queue-warning QUEUE_WARNING]
                          [--queue-critical QUEUE_CRITICAL] [--failed-warning FAILED_WARNING] [--failed-critical FAILED_CRITICAL]
                          [--signal-warning SIGNAL_WARNING] [--signal-critical SIGNAL_CRITICAL] [--disk-warning DISK_WARNING] [--disk-critical DISK_CRITICAL]

```

## Example

```
check_brevisone -H 192.168.1.1
[CRITICAL] - Brevis.One SMS Gateway Status
 \_[CRITICAL] Failed sending: 12
 \_[OK] Signal strength: 95
 \_[CRITICAL] Que length: 23
|que=23 failed=12 signal=95 total=885 time=1713865490 disk=1400246272

check_brevisone -H 192.168.1.1 --protocol http --failed-critical 18 --failed-warning 15 --signal-warning 100 --signal-critical 120
[CRITICAL] - Brevis.One SMS Gateway Status
 \_[OK] Failed sending: 12
 \_[OK] Signal strength: 95
 \_[CRITICAL] Que length: 23
|que=23 failed=12 signal=95 total=885 time=1713865490 disk=1400246272
```

Since firmware version 4.0 HTTPS is the default. To connect to a unencrypted HTTP endpoint you can use `--protocol=http`.
If you are using a self-certified certificate, use `--ssl-insecure` to disable verification.

`--disk-warning` and `--disk-critical` don't have defaults, since we don't know the limit of the specific device. Each user will have to check their devices disk capacity and set an appropriate value.

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
