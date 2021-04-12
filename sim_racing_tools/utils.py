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

import re
import decimal


def create_filename_safe_name(in_name):
    """
    Take a string and make it safe to use in a file path by removing any non-letter and number characters and
    replacing any spaces with single underscores

    Args:
        in_name: the name to adapt

    Returns:
        a string that is suitable for using in file paths
    """
    normalized = re.sub(r"[^\w\s]", '', in_name)
    return re.sub(r"\s+", '_', normalized)


def round_up(x, place=0):
    context = decimal.getcontext()
    # get the original setting so we can put it back when we're done
    original_rounding = context.rounding
    # change context to act like ceil()
    context.rounding = decimal.ROUND_CEILING

    rounded = round(decimal.Decimal(str(x)), place)
    context.rounding = original_rounding
    return float(rounded)
