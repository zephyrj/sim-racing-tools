import re

from configobj import ConfigObj


class IniObj(ConfigObj):
    def __init__(self, *args, **kwargs):
        ConfigObj.__init__(self, *args, **kwargs)

    def _write_line(self, indent_string, entry, this_entry, comment):
        """Write an individual line, for the write method"""
        if not self.unrepr:
            val = self._decode_element(self._quote(this_entry))
        else:
            val = repr(this_entry)

        return '%s%s%s%s%s' % (indent_string,
                               self._decode_element(self._quote(entry, multiline=False)),
                               self._a_to_u('='),
                               val,
                               self._decode_element(comment))


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
