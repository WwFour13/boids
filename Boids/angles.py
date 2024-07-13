import math


def get_quadrant(rad):
    rad %= math.radians(360)

    if 0 < rad < math.radians(90):
        return 1
    elif rad < math.radians(180):
        return 2
    elif rad < math.radians(270):
        return 3
    elif rad < math.radians(360):
        return 4
    else:
        raise ValueError("Invalid angle")


def get_radian_difference(from_, to):
    diff = to - from_
    if diff < -math.radians(180):
        diff += math.pi * 2
    elif diff > math.radians(180):
        diff -= math.pi * 2
    return diff


def circular_mean(angles, is_degrees=True):
    if not angles:
        raise ValueError("Input list of angles cannot be empty")

    # Convert angles to radians
    radians = [math.radians(angle) for angle in angles]

    # Calculate sum of cos and sin of angles
    sum_cos = sum(math.cos(angle) for angle in radians)
    sum_sin = sum(math.sin(angle) for angle in radians)

    # Calculate the mean angle in radians using arctangent of means
    mean_angle_rad = math.atan2(sum_sin, sum_cos)

    # Convert back to degrees and ensure between 0 and 360
    mean_angle_deg = math.degrees(mean_angle_rad) % 360

    return mean_angle_deg

