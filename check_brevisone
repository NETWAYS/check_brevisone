#!/usr/bin/env python3
# COPYRIGHT:
#
# This software is Copyright (c) 2018 NETWAYS GmbH, Matthias Jentsch
#                                <support@netways.de>
#
# (Except where explicitly superseded by other copyright notices)
#
# LICENSE:
#
# Copyright (C) 2020 NETWAYS GmbH <info@netways.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
# or see <http://www.gnu.org/licenses/>.
#
# CONTRIBUTION SUBMISSION POLICY:
#
# (The following paragraph is not intended to limit the rights granted
# to you to modify and distribute this software under the terms of
# the GNU General Public License and is only of importance to you if
# you choose to contribute your changes and enhancements to the
# community by submitting them to NETWAYS GmbH.)
#
# By intentionally submitting any modifications, corrections or
# derivatives to this work, or any other work intended for use with
# this Software, to NETWAYS GmbH, you confirm that
# you are the copyright holder for those contributions and you grant
# NETWAYS GmbH a nonexclusive, worldwide, irrevocable,
# royalty-free, perpetual, license to use, copy, create derivative
# works based on those contributions, and sublicense and distribute
# those contributions and any derivatives thereof.

from argparse import ArgumentParser
import urllib.request
from urllib.parse import urljoin
import ssl
import sys


# Return code level
# 0 - OK       - The plugin was able to check the service and it appeared to be functioning properly
# 1 - WARNING  - The plugin was able to check the service, but it appeared to be above some "warning"
#                threshold or did not appear to be working properly
# 2 - CRITICAL - The plugin detected that either the service was not running or it was above some "critical" threshold
# 3 - UNKNOWN  - Invalid command line arguments were supplied to the plugin or low-level failures
__version__ = '4.0.0-rc1'

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

STATES = {
    OK: "OK",
    WARNING: "WARNING",
    CRITICAL: "CRITICAL",
    UNKNOWN: "UNKNOWN",
}


def generate_output(status=3, outputs=None, perfdata=None):
    """
    Generate plugin data output with status and perfdata
    """

    pluginoutput = '[{}] - Brevis.One SMS Gateway Status\n'.format(STATES.get(status, 'UNKNOWN'))

    # All lines we received from the Endpoint
    if outputs:
        for line in outputs:
            pluginoutput += line + '\n'

    # Perfdata we explicitly extracted from the data
    # The perfdata var should be a dict, we normalize the keys and
    # transform everything into the expected output 'key 1': 3 > key_1=3
    if perfdata:
        pluginoutput += '|'
        for k, v in perfdata.items():
            if (k and v) and isinstance(v, int):
                pluginoutput += k.lower().replace(" ", "_").replace(",", "") + '=' + str(v) + ' '

    print(pluginoutput)


def commandline(args):
    """
    Parse commandline arguments.
    """
    parser = ArgumentParser(description="check_brevisone (Version: %s)" % (__version__))

    parser.add_argument('-V', '--version', action='version', version='check_brevisone' + __version__)

    parser.add_argument('-H', '--hostname', help='The host address of the SMS gateway', required=True)
    parser.add_argument('-T', '--timeout', help='Seconds before connection times out (default 10)',
                        default=10,
                        type=int)
    parser.add_argument('--ssl-insecure',
                        dest='insecure',
                        action='store_true',
                        default=False,
                        help='Allow insecure SSL connections (default False)')
    parser.add_argument('--protocol',
                        choices=["http", "https"],
                        default='https',
                        help='HTTP protocol, use one of http or https (default https)')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='debug mode')

    parser.add_argument('--queue-warning', help='The warning threshold for the amount of queued SMS (default 1)',
                        default=1,
                        type=int)
    parser.add_argument('--queue-critical', help='The critical threshold for the amount of queued SMS (default 5)',
                        default=5,
                        type=int)

    parser.add_argument('--failed-warning',
                        help='The warning threshold for failed SMS (default 1)',
                        default=1,
                        type=int)
    parser.add_argument('--failed-critical',
                        help='The critical threshold for failed SMS (default 5)',
                        default=5,
                        type=int)

    parser.add_argument('--signal-warning',
                        help='The warning threshold for the minimum signal strength (in db, default -91)',
                        default=-91,
                        type=int)
    parser.add_argument('--signal-critical',
                        help='The critical threshold for the minimum signal strength (in db, default -107)',
                        default=-107,
                        type=int)

    parser.add_argument('--disk-warning',
                        help='The warning threshold for the disk space (in bytes)',
                        required=False,
                        type=int)
    parser.add_argument('--disk-critical',
                        help='The critical threshold for the disk space (in bytes)',
                        required=False,
                        type=int)

    return parser.parse_args(args)


def get_data(base_url, timeout, insecure):
    """
    Requests the data via HTTP. Basically a wrapper around urllib.

    What we expect from the server:

    HTTP/1.0 200 OK
    que: foo
    failed: 0
    signal: 15 db
    total: 25
    """

    # Default context for connection
    ctx = ssl.create_default_context()
    if insecure is True:
        ctx.set_ciphers("ALL:@SECLEVEL=0")
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    # Example URL: https://mybrevisone/check.php
    url = urljoin(base_url, "check.php")
    response = urllib.request.urlopen(url=url, timeout=timeout, context=ctx)  # pylint: disable=consider-using-with

    if response.getcode() >= 400:
        raise RuntimeError("Could not get response")

    # We expect at least the que name otherwise we
    # assume none of the data got sent
    resp = response.read().decode()
    if "que:" not in resp:
        raise RuntimeError("Invalid response")

    return resp


def parse_data(data):
    """
    Safely extract data from the APIs reponse
    """
    lines = [str(i).strip() for i in data.split("\n") if i]

    parsed_data = {}

    for line in lines:
        d = line.split(":")
        if len(d) == 2:
            key = d[0].strip()
            value = d[1].strip()

            # Remove the db string from the signal value
            if key == "signal":
                value = value.replace('db', '').replace('dBm', '').strip()

            # Parse integer value to be actual integers
            if value.lstrip('-').isdigit():
                value = int(value)

            parsed_data[key] = value

    return parsed_data


def worst_state(*states):
    overall = -1

    for state in states:
        if state == CRITICAL:
            overall = CRITICAL
        elif state == UNKNOWN:
            if overall != CRITICAL:
                overall = UNKNOWN
        elif state > overall:
            overall = state

    if overall < 0 or overall > 3:
        overall = UNKNOWN

    return overall


def debug_print(debug_flag, message):
    """
    Print debug messages if -d is set.
    """
    if not debug_flag:
        return

    print(message)


def determine_status(args, perfdata):
    states = []
    outputs = []

    if perfdata['failed'] >= args.failed_critical:
        outputs.append(" \\_[CRITICAL] Failed sending: {}".format(perfdata['failed']))
        states.append(CRITICAL)
    elif perfdata['failed'] >= args.failed_warning:
        outputs.append(" \\_[WARNING] Failed sending: {}".format(perfdata['failed']))
        states.append(WARNING)
    else:
        outputs.append(" \\_[OK] Failed sending: {}".format(perfdata['failed']))
        states.append(OK)

    if perfdata['signal'] <= args.signal_critical:
        outputs.append(" \\_[CRITICAL] Signal strength: {}".format(perfdata['signal']))
        states.append(CRITICAL)
    elif perfdata['signal'] <= args.signal_warning:
        outputs.append(" \\_[WARNING] Signal strength: {}".format(perfdata['signal']))
        states.append(WARNING)
    else:
        outputs.append(" \\_[OK] Signal strength: {}".format(perfdata['signal']))
        states.append(OK)

    if perfdata['que'] >= args.queue_critical:
        outputs.append(" \\_[CRITICAL] Queue length: {}".format(perfdata['que']))
        states.append(CRITICAL)
    elif perfdata['que'] >= args.queue_warning:
        outputs.append(" \\_[WARNING] Queue length: {}".format(perfdata['que']))
        states.append(WARNING)
    else:
        outputs.append(" \\_[OK] Queue length: {}".format(perfdata['que']))
        states.append(OK)

    if args.disk_critical and perfdata['disk'] >= args.disk_critical:
        outputs.append(" \\_[CRITICAL] Disk usage: {}".format(perfdata['disk']))
        states.append(CRITICAL)
    elif args.disk_warning and perfdata['disk'] >= args.disk_warning:
        outputs.append(" \\_[WARNING] Disk usage: {}".format(perfdata['disk']))
        states.append(WARNING)
    elif args.disk_warning or args.disk_critical:
        outputs.append(" \\_[OK] Disk usage: {}".format(perfdata['disk']))
        states.append(OK)

    return states, outputs


def main(args):
    try:
        base_url = args.protocol + '://' + args.hostname
        data = get_data(base_url=base_url,
                        timeout=args.timeout,
                        insecure=args.insecure)
    except Exception as data_exc:  # pylint: disable=broad-except
        print('UNKNOWN - Could not connect to SMS Gateway', data_exc)
        return UNKNOWN

    # Safely extract perfdata, which we'll also use to determine the final status
    perfdata = parse_data(data)

    if not perfdata:
        print('UNKNOWN - Could not determine status', perfdata)
        return UNKNOWN

    if 'failed' not in perfdata:
        print('UNKNOWN - Could not determine failed status', perfdata)
        return UNKNOWN

    if 'que' not in perfdata:
        print('UNKNOWN - Could not determine que status', perfdata)
        return UNKNOWN

    # Determine the final status
    states, outputs = determine_status(args, perfdata)

    debug_print(args.debug, "API Response:\n{}".format(data))

    generate_output(worst_state(*states), outputs=outputs, perfdata=perfdata)
    return worst_state(*states)


if __name__ == '__main__':  # pragma: no cover
    try:
        ARGS = commandline(sys.argv[1:])
        sys.exit(main(ARGS))
    except SystemExit:
        # Re-throw the exception
        exception = sys.exc_info()[1]

        if exception is not None:
            raise exception.with_traceback(sys.exc_info()[2])  # pylint: disable=raise-missing-from
    except Exception as excpt:  # pylint: disable=broad-except
        print("UNKNOWN - Error: %s" % (excpt))
        sys.exit(3)
