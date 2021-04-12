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

import sys
import struct
import toml
import logging

from collections import OrderedDict

from typing import List

# Appears to denote the start of a blob
BLOB_MARK = 1
# Bytes denoting true or false
FALSE = 48
TRUE = 49
# A number seems to represent a REAL or a NUMBER but is always stored as 8 byte Double
NUMBER = 78
# TEXT can be a string or a blob of data
TEXT = 83
# This tag denote other attributes live inside this one
ATTRIBUTE_SECTION = 84


def type_byte_to_string(byte):
    if byte == NUMBER:
        return "Number"
    elif byte == TEXT:
        return "Text"
    elif byte == ATTRIBUTE_SECTION:
        return "AttributeSection"
    return str(byte)


class ByteChunk(object):
    def __init__(self, byte_stream):
        self.byte_stream = byte_stream

    def hex(self):
        return " ".join(f'{b:02X}' for b in self.byte_stream)

    @property
    def bytes(self):
        return self.byte_stream

    @property
    def length(self):
        return len(self.byte_stream)


class AttributeSection(ByteChunk):
    def __init__(self, name, byte_stream):
        super(AttributeSection, self).__init__(byte_stream)
        self.name = name
        if struct.unpack("<I", bytearray(byte_stream[0:4]))[0] > 0:
            self.num_children = struct.unpack("<LL", bytearray(byte_stream[0:8]))[0]
        else:
            self.num_children = struct.unpack("<I", bytearray(byte_stream[4:8]))[0]
        self.attribute_list = list()
        self.section_list = list()
        self.section_stack = list()

    def __str__(self):
        return "\n".join(self.summary())

    def as_dict(self):
        data_dict = OrderedDict()
        for attribute in self.attribute_list:
            data_dict[attribute.name] = attribute.value
        for section in self.section_list:
            data_dict[section.name] = section.as_dict()
        return data_dict

    def summary(self):
        lines = list()
        lines.append(f'{self.name}')
        lines.extend([f'  {str(a)}' for a in self.attribute_list])
        for section in self.section_list:
            lines.extend([f'  {line}' for line in section.summary()])
            lines.append("")
        return lines

    def add_attribute(self, attribute):
        if len(self.section_stack):
            self.section_stack[-1].add_attribute(attribute)
        else:
            self.attribute_list.append(attribute)
        self._check_for_complete_sections()

    def add_section(self, section):
        if len(self.section_stack):
            self.section_stack[-1].add_section(section)
        else:
            self.section_stack.append(section)
            self.section_list.append(self.section_stack[-1])
        self._check_for_complete_sections()

    def complete(self):
        if len(self.section_stack):
            return False
        return self.num_children == (len(self.attribute_list) + len(self.section_list))

    def _check_for_complete_sections(self):
        while len(self.section_stack) and self.section_stack[-1].complete():
            self.section_stack.pop()


class Blob(ByteChunk):
    def __init__(self, name, byte_stream):
        super(Blob, self).__init__(byte_stream)
        self.name = name
        self.attributes = list()
        self.sections = list()
        self.section_stack = list()


class Text(ByteChunk):
    def __init__(self, byte_stream):
        super(Text, self).__init__(byte_stream)

    def __str__(self):
        try:
            return self.byte_stream.decode("utf-8")
        except (AttributeError, ValueError):
            return self.hex()

    @property
    def value(self):
        return self.__str__()


class Number(ByteChunk):
    def __init__(self, byte_stream):
        super(Number, self).__init__(byte_stream)
        self._value = struct.unpack("d", bytearray(self.byte_stream))[0]

    def __str__(self):
        return str(self._value)

    @property
    def value(self):
        return self._value


class FalseType(ByteChunk):
    def __init__(self, byte_stream):
        super(FalseType, self).__init__(byte_stream)

    def __str__(self):
        return str(False)

    @property
    def value(self):
        return False


class TrueType(ByteChunk):
    def __init__(self, byte_stream):
        super(TrueType, self).__init__(byte_stream)

    def __str__(self):
        return str(True)

    @property
    def value(self):
        return True


class CarAttribute(object):
    def __init__(self):
        self.name = None
        self.value_object = None

    def __str__(self):
        return f'{self.name} = {str(self.value_object)}'

    @property
    def value(self):
        return self.value_object.value


class CarFile(object):
    def __init__(self, filename, byte_stream):
        attributes: List[CarAttribute]
        sections: List[AttributeSection]

        self.car_file_path = filename
        self.byte_stream = byte_stream
        self.current_pos = 0
        self.section_stack = list()
        self.sections = list()
        self.attributes = list()
        self.attribute_offset_map = dict()
        self._parse_opening_blob_mark("Car")
        self.current_attribute = None

    def __str__(self):
        out = "\n\n".join([str(a) for a in self.attributes])
        for section in self.sections:
            out += str(section)
        return out

    def get_data(self):
        data_dict = OrderedDict()
        data_dict["car-file-path"] = self.car_file_path

        for attribute in self.attributes:
            data_dict[attribute.name] = attribute.value

        for section in self.sections:
            data_dict[section.name] = section.as_dict()
        return data_dict

    def write_toml(self, path):
        with open(path, "w+") as out_file:
            toml.dump(self.get_data(), out_file)

    def parse(self):
        parsing_attribute = False
        parsing_int_pair = False
        while True:
            if self.current_pos >= len(self.byte_stream):
                break
            if parsing_attribute or parsing_int_pair:
                if not parsing_int_pair:
                    length = self._parse_length()
                    if self._is_blob():
                        logging.debug("Skipped non-string:")
                        logging.debug(" ".join(f'{b:02X}' for b in self.byte_stream[self.current_pos: self.current_pos + length]))
                        self.current_pos += length
                        continue
                    attribute_name = self._parse_text(length)
                else:
                    attribute_name = str(self._parse_number())

                object_type = self._parse_type()
                if object_type == ATTRIBUTE_SECTION:
                    self._add_section(self._parse_attribute_section(str(attribute_name)))
                elif object_type == FALSE:
                    self._add_attribute(str(attribute_name), FalseType(object_type))
                elif object_type == TRUE:
                    self._add_attribute(str(attribute_name), TrueType(object_type))
                else:
                    if object_type == NUMBER:
                        self._add_attribute(str(attribute_name), self._parse_number())
                    else:
                        length = self._parse_length()
                        if self._is_blob():
                            self.current_pos += 2
                            self._add_section(self._parse_attribute_section(str(attribute_name)))
                        else:
                            self._add_attribute(str(attribute_name), self._parse_text(length))

                self._check_for_section_complete()
                parsing_attribute = False
                parsing_int_pair = False
            else:
                type_byte = self._parse_type()
                if type_byte == TEXT:
                    parsing_attribute = True
                elif type_byte == NUMBER:
                    parsing_int_pair = True

    def _check_for_section_complete(self):
        while len(self.section_stack) and self.section_stack[-1].complete():
            self.section_stack.pop()

    def _add_section(self, section):
        if len(self.section_stack):
            self.section_stack[-1].add_section(section)
        else:
            self.section_stack.append(section)
            self.sections.append(self.section_stack[-1])

    def _add_attribute(self, name, value):
        attribute = CarAttribute()
        attribute.name = name
        attribute.value_object = value

        if len(self.section_stack):
            self.section_stack[-1].add_attribute(attribute)
        else:
            self.attributes.append(attribute)
        self.attribute_offset_map[attribute.name] = self.current_pos

    def _is_blob(self):
        if self.byte_stream[self.current_pos] == 1:
            return True
        return False

    def _parse_string_length(self):
        try:
            return struct.unpack("<I", bytearray(self.byte_stream[self.current_pos:self.current_pos + 4]))[0]
        finally:
            self.current_pos += 4

    def _parse_text(self, length):
        try:
            return Text(self.byte_stream[self.current_pos:self.current_pos + length])
        finally:
            self.current_pos += length

    def _parse_number(self):
        try:
            return Number(self.byte_stream[self.current_pos:self.current_pos + 8])
        finally:
            self.current_pos += 8

    def _parse_attribute_section(self, name):
        try:
            return AttributeSection(name, self.byte_stream[self.current_pos:self.current_pos + 8])
        finally:
            self.current_pos += 8

    def _parse_type(self):
        try:
            return self.byte_stream[self.current_pos]
        finally:
            self.current_pos += 1

    def _parse_opening_blob_mark(self, opening_section_name):
        if self.byte_stream[self.current_pos] != BLOB_MARK:
            raise ValueError("File doesn't open with a blob mark - is it a valid .car file?")
        self.current_pos += 2  # Jump over
        self.section_stack.append(self._parse_attribute_section(opening_section_name))
        self.sections.append(self.section_stack[-1])

    def _parse_length(self):
        try:
            return struct.unpack("<I", bytearray(self.byte_stream[self.current_pos:self.current_pos + 4]))[0]
        finally:
            self.current_pos += 4


def hp_lut_calculator(torque_lut):
    # hp = T x RPM/5,252
    out_lut = OrderedDict()
    for rpm, T in torque_lut:
        out_lut[rpm] = T * rpm/5252


if __name__ == '__main__':
    with open(sys.argv[1], "rb") as f:
        car_bytes = f.read()
        c = CarFile(f.name, car_bytes)
        c.parse()
        c.write_toml("out.toml")
