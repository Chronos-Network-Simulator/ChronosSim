from typing import List


def convert_hex_to_decimal(hex_color: str) -> List[float]:
    """
    Helper function to convert a color string into a list of decimals

    :param hex_color: Hex color string
    :type hex_color: str
    """
    return [int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4)]
