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

import logging

LIST = 0
DICT = 1


#  Start by looking for key starting with "
#  Once found there will then be a ":" then it could be could be one of 4 things:
#    string - "
#    dict - {
#    list - [
#    number - any other char
class ParseState(object):
    ATTRIBUTE_NAME_SEARCH = 0
    ATTRIBUTE_VALUE_SEARCH = 1


class NewLineFound(IndexError):
    def __init__(self):
        super(NewLineFound, self).__init__("Found new line")


class Parser(object):
    def __init__(self):
        self.data_dict = dict()
        self.container_stack = [self.data_dict]
        self.current_container = self.container_stack[-1]
        self.line = None
        self.idx = 0
        self.current_attribute_name = None

        self.state = ParseState.ATTRIBUTE_NAME_SEARCH

    def naive_parse(self, filename):
        with open(filename, "r") as f:
            return self._naive_parse(f.readlines(), logging.getLogger("jbeam_load"))

    def _naive_parse(self, jbeam_lines, logger):
        line_idx = 0
        try:
            for line_idx, line in enumerate(jbeam_lines, start=1):
                self.idx = 0
                if line[0] == "{":
                    continue
                self.line = line.strip()
                comment_start = self.line.find("//")
                if comment_start >= 0:
                    comment = line[comment_start:-1]
                    logger.info(f"Removing {comment} from line {line_idx}")
                    self.line = self.line[:comment_start] + "\n"
                self._parse_line()
        except Exception as e:
            err_msg = f"Error on line {line_idx}: {str(e)}\n {self.line}"
            logger.error(err_msg)
            raise ValueError(err_msg)
        return self.data_dict

    def _parse_string(self):
        if self.line[self.idx] != '"':
            raise ValueError("String doesn't start with a \"")
        self.idx += 1
        ending_quote_idx = self.line[self.idx:].index('"')
        string = self.line[self.idx:self.idx+ending_quote_idx]
        self.idx += ending_quote_idx + 1
        return string

    def _parse_number(self):
        is_float = False
        found_non_digit = False
        first_char = True
        for number_end, char in enumerate(self.line[self.idx:]):
            if first_char:
                first_char = False
                if char == "-":
                    continue
            if char.isdigit():
                continue
            if char == ".":
                if is_float:
                    raise ValueError("Unknown number type containing multiple decimal places")
                is_float = True
            else:
                found_non_digit = True
                break
        if not found_non_digit:
            number_end += 1
        if is_float:
            val = float(self.line[self.idx:self.idx+number_end])
        else:
            val = int(self.line[self.idx:self.idx+number_end])
        self.idx += number_end
        return val

    def _parse_bool(self):
        if self.line[self.idx] in ["T", "t"]:
            val = bool(self.line[self.idx:self.idx+4])
            self.idx += 4
            return val
        else:
            val = bool(self.line[self.idx:self.idx+5])
            self.idx += 5
            return val

    def _found_container_close(self):
        return self.line[self.idx] in ["}", "]"]

    def _parse_container_close(self):
        self._pop_container()
        self.idx += 1

    def _parse_line(self):
        while self.idx < len(self.line):
            if self.state == ParseState.ATTRIBUTE_NAME_SEARCH:
                try:
                    self.idx = self._find_next_char()
                except (NewLineFound, ValueError):
                    return

                if self._found_container_close():
                    self._parse_container_close()
                    continue

                if self.line[self.idx] != '"':
                    raise ValueError(f"Was expecting an attribute name but found {self.line[self.idx]} at position "
                                     f"{self.idx}")
                attribute_name = self._parse_string()
                self.idx = self.idx + self.line[self.idx:].index(":") + 1
                self._attribute_name_found(attribute_name)
                continue

            try:
                self.idx = self._find_next_char()
            except (NewLineFound, ValueError):
                return

            if self.line[self.idx] == '"':
                self._add_value(self._parse_string())
                continue
            elif self.line[self.idx].isdigit() or self.line[self.idx] == "-":
                self._add_value(self._parse_number())
                continue
            elif self.line[self.idx] in ["T", "t", "F", "f"]:
                self._add_value(self._parse_bool())
                continue
            elif self._found_container_close():
                self._parse_container_close()
                continue

            if self.line[self.idx] == '{':
                self._add_container(dict())
            elif self.line[self.idx] == '[':
                self._add_container(list())
            else:
                raise ValueError(f"Unexpected char {self.line[self.idx]} at position {self.idx}")
            self.idx += 1

    def _attribute_name_found(self, name):
        self.state = ParseState.ATTRIBUTE_VALUE_SEARCH
        self.current_attribute_name = name

    def _attribute_stored(self):
        self.state = ParseState.ATTRIBUTE_NAME_SEARCH
        self.current_attribute_name = None

    def _current_container_type(self):
        return type(self.current_container)

    def _find_next_char(self):
        for idx, char in enumerate(self.line[self.idx:]):
            if char == "\n":
                raise NewLineFound()
            if char.isspace() or char == ",":
                continue
            return self.idx + idx
        raise ValueError("Couldn't find a non-space char on current line")

    def _push_container(self, container):
        self.container_stack.append(container)
        self.current_container = self.container_stack[-1]
        self._set_state_for_current_container()

    def _pop_container(self):
        self.container_stack.pop()
        if len(self.container_stack):
            self.current_container = self.container_stack[-1]
        self._set_state_for_current_container()

    def _add_container(self, container):
        if self._current_container_type() == list:
            self.current_container.append(container)
            self._push_container(self.current_container[-1])
        else:
            if self.current_attribute_name is None:
                raise ValueError(f"Cannot add {type(container)} to dict without a key")
            self.current_container[self.current_attribute_name] = container
            self._push_container(self.current_container[self.current_attribute_name])
            self.current_attribute_name = None

    def _add_value(self, value):
        if self._current_container_type() == list:
            self.current_container.append(value)
        else:
            if self.current_attribute_name is None:
                raise ValueError(f"Cannot add {type(value)} to dict without a key")
            self.current_container[self.current_attribute_name] = value
            self.state = ParseState.ATTRIBUTE_NAME_SEARCH
            self.current_attribute_name = None

    def _set_state_for_current_container(self):
        if self._current_container_type() == dict:
            self.state = ParseState.ATTRIBUTE_NAME_SEARCH
        else:
            self.state = ParseState.ATTRIBUTE_VALUE_SEARCH
