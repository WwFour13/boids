import colorsys

color_strength = 30.0  # S-value ranging 0-100 lower values fades to white
color_brightness = 80.0  # V-value ranging 0-100 lower values fades to black
loop_time_seconds = 25.0


def normalize_hsv_to_rgb(hsv: tuple[float, float, float]):
    # normalize 0-1
    percent_h = hsv[0] / 360.0
    percent_s = hsv[1] / 100.0
    percent_v = hsv[2] / 100.0

    percent_rgb = colorsys.hsv_to_rgb(percent_h, percent_s, percent_v)

    return percent_rgb[0] * 256.0, percent_rgb[1] * 256.0, percent_rgb[2] * 256.0


def get_cyclical_rgb(run_time_seconds: float):
    h = run_time_seconds % loop_time_seconds / loop_time_seconds * 360.0
    s = color_strength
    v = color_brightness
    return normalize_hsv_to_rgb((h, s, v))
