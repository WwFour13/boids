import colorsys
from functools import lru_cache


def normalize_hsv_to_rgb(hsv: tuple[float, float, float]):
    # normalize 0-1
    percent_h = hsv[0] / 360.0
    percent_s = hsv[1] / 100.0
    percent_v = hsv[2] / 100.0

    percent_rgb = colorsys.hsv_to_rgb(percent_h, percent_s, percent_v)

    return percent_rgb[0] * 256.0, percent_rgb[1] * 256.0, percent_rgb[2] * 256.0


def get_cyclical_rgb(seconds: float):
    color_strength = 30.0  # S-value ranging 0-100 lower values fades to white
    color_brightness = 80.0  # V-value ranging 0-100 lower values fades to black
    loop_time_seconds = 25.0

    h = seconds % loop_time_seconds / loop_time_seconds * 360.0
    s = color_strength
    v = color_brightness
    return normalize_hsv_to_rgb((h, s, v))


@lru_cache(maxsize=None)
def interpolate_color(color1, color2, t):
    """
  Interpolates between two colors based on a factor t (0-1).

  Args:
    color1: Starting color as a tuple (R, G, B).
    color2: Ending color as a tuple (R, G, B).
    t: Interpolation factor (0-1).

  Returns:
    The interpolated color as a tuple (R, G, B).
  """

    return tuple(int(c1 * (1 - t) + c2 * t) for c1, c2 in zip(color1, color2))


@lru_cache(maxsize=None)
def replace_color(image, old_color, new_color):
    image = image.copy()  # Create a copy to avoid modifying the original image
    for x in range(image.get_width()):
        for y in range(image.get_height()):
            color = image.get_at((x, y))
            if color == old_color:
                image.set_at((x, y), new_color)
    return image
