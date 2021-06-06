#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

"""
Copyright (c):
2021 zephyrj
zephyrj@protonmail.com

This file is part of sim-racing-tools.

sim-racing-tools is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

sim-racing-tools is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with sim-racing-tools. If not, see <https://www.gnu.org/licenses/>.
"""

import argcomplete
import argparse

parser = argparse.ArgumentParser(description='Tool to validate that an engine meets a set of criteria')
engine_source_group = parser.add_mutually_exclusive_group(required=True)
engine_source_group.add_argument("-n", "--name", type=str, nargs=2,
                                 help="The name of the engine as '<family-name>' '<variant-name>'. Note that each name "
                                      "must be quoted and there should be a space between the two names")
engine_source_group.add_argument('-u', "--variant-uid", type=str, help="The uid of the variant to check")
engine_source_group.add_argument('-c', "--exported-car-path", type=str,
                                 help="A path to an exported car - the engine of the car will be checked. "
                                      "Can be a full path to an exported zip file or unpacked folder,"
                                      " or the name of a zip file or unpacked folder in the BeamNG mod directory")
parser.add_argument('spec_file', help="A file containing the criteria which the engine must meet")


def main():
    import sys
    import sim_racing_tools.automation.scripts.scrutineering_impl as scrutineering_impl
    parser.set_defaults(func=scrutineering_impl.validate_engine)
    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == '__main__':
    main()
