



def convert_bbox_to_cm(width_px, height_px, pixels_per_cm):
    """
    Convert bounding box dimensions from pixels to centimeters.
    
    :param width_px: Width in pixels
    :param height_px: Height in pixels
    :param pixels_per_cm: Number of pixels per centimeter
    :return: Tuple of (width_cm, height_cm)
    """

    
    width_cm = width_px / pixels_per_cm
    height_cm = height_px / pixels_per_cm
    return width_cm, height_cm