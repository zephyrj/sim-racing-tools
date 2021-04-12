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

class BilletSteelCrank(object):
    def __init__(self, quality):
        self.quality = quality

    def max_rpm(self):
        # + 15 = 13100
        # - 15 = 11500
        return 12300

    def max_torque(self):
        pass


class ForgedSteelCrank(object):
    def __init__(self, quality):
        self.quality = quality

    def max_rpm(self):
        pass

    def max_torque(self):
        pass

