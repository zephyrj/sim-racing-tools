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
