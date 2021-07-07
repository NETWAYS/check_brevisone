#!/usr/bin/env python
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

import requests
import argparse
import signal
import sys
import os

from functools import partial
from requests.packages.urllib3.exceptions import InsecureRequestWarning

__version__ = '2.0.0'


def readInt(string):
    try:
        return int(string.split(':')[1])
    except ValueError:
        return 0


def readStr(string):
    return ':'.join(string.split(':')[1:]).strip()


def readSig(string):
    sig = readStr(string).replace('db', '').replace('dBm', '').strip()
    try:
        return int(sig)
    except ValueError:
        return 0


def readPrf(string):
    return string.split(':')[1].strip().split(';')


def output(label, state=0, lines=None, perfdata=None, name='BREVISONE'):
    if lines is None:
        lines = []
    if perfdata is None:
        perfdata = {}

    pluginoutput = name + ': ' + str(label)

    if len(lines):
        pluginoutput += ' - '
        pluginoutput += ' '.join(lines)

    if perfdata:
        pluginoutput += '|'
        pluginoutput += ' '.join(["'" + key + "'" + '=' + str(value) for key, value in perfdata.items()])

    print(pluginoutput)
    sys.exit(state)


# Handle Timeout
def handle_sigalrm(signum, frame, timeout=None):
    output('CRITICAL - Plugin timed out after %d seconds' % timeout, 2)


if __name__ == '__main__':
    path = '%s://%s/check.php'
    prog = os.path.basename(sys.argv[0])
    output = partial(output, name=prog)
    readme = 'Plugin to check signal strength and availability of the Brevis.One SMS gateway.\n' \
             'This plugin was previously known as check_braintower, it was renamed due to a product name change. ' \
             'You should be able to check gateways running older versions as well.'
    
    # Parse Arguments
    parser = argparse.ArgumentParser(prog=prog, description=readme)
    parser.add_argument('-V', '--version', action='version', version='%(prog)s v' + sys.modules[__name__].__version__)
    
    parser.add_argument('-H', '--hostname', help='The host address of the SMS gateway', required=True)
    parser.add_argument('-T', '--timeout', help='Seconds before connection times out (default 10)',
                        default=10,
                        type=int)
    parser.add_argument('-Q', '--queue', help='The warning threshold for the amount of queued SMS (default 1)',
                        default=1,
                        type=int)
    parser.add_argument('-F', '--fail', help='The critical threshold for failed SMS (default 1)', default=1, type=int)
    parser.add_argument('--signal-warning',
                        help='The warning threshold for the minimum signal strength (in db, default 0)',
                        default=-91,
                        type=int)
    parser.add_argument('--signal-critical',
                        help='The critical threshold for the minimum signal strength (in db, default 0)',
                        default=-107,
                        type=int)
    parser.add_argument('--ssl-insecure',
                        dest='insecure',
                        action='store_true',
                        default=False,
                        help='Allow insecure SSL connections (default False)')
    parser.add_argument('--protocol',
                        default='https',
                        help='HTTP protocol, use one of http or https (default https)')
    
    args = parser.parse_args()
    
    signal.signal(signal.SIGALRM, partial(handle_sigalrm, timeout=args.timeout))
    signal.alarm(args.timeout)
    
    # Execute Check
    try:
        if args.insecure is True:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        response = requests.get(path % (args.protocol, args.hostname), verify=(not args.insecure))

        details = response.text.split("\n")

        lines = []
        for item in details:
            if not item:
                continue

            lines.append(str(item).strip())

        if response.status_code >= 400:
            raise IOError("HTTP Request Failed %d." % response.status_code)
        if not lines[0].strip().startswith('que:'):
            raise RuntimeError("Unexpected response, invalid check target '%s'?" % args.hostname)

        que = readInt(lines[0])
        failed = readInt(lines[1])
        total = readInt(lines[3])
        signal_strength = readSig(lines[2])

        perfdata = {
            'que': que,
            'failed': failed,
            'total': total,
            'signal': signal_strength
        }

        if failed >= args.fail or signal_strength <= args.signal_critical:
            output('CRITICAL', 2, lines=lines, perfdata=perfdata)

        # Return
        if que >= args.queue or signal_strength <= args.signal_warning:
            output('WARNING', 1, lines=lines, perfdata=perfdata)

        output('OK', 0, lines=lines, perfdata=perfdata)
    except Exception as e:
        output(e, 2)
