# utils.py

# Convert bounding box dimensions from pixels to centimeters.
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


# Calculate pixels per cm for detected coin
from services.config import REFERENCE_COINS_DIAMETER_CM

def calculate_pixels_per_cm(coin_prediction, coin_label):
    """
    Calculate pixels per cm based on detected coin prediction and known diameter.
    """
    if not coin_label:
        return {
            "message": "Coin detected but mapping failed",
            "coin_label": None,
            "width_px": coin_prediction.get("width", 0),
            "pixels_per_cm": 0
        }

    coin_diameter_cm = REFERENCE_COINS_DIAMETER_CM.get(coin_label)
    coin_width_px = coin_prediction.get("width", 0)

    if coin_diameter_cm and coin_width_px > 0:
        pixels_per_cm = coin_width_px / coin_diameter_cm
        return {
            "message": f"{coin_label} detected",
            "coin_label": coin_label,
            "width_px": coin_width_px,
            "coin_diameter_cm": coin_diameter_cm,
            "pixels_per_cm": pixels_per_cm
        }

    return {
        "message": "Coin detected but invalid measurement",
        "coin_label": coin_label,
        "width_px": coin_width_px,
        "pixels_per_cm": 0
    }



from inference_sdk import InferenceHTTPClient
import os

def run_inference(image_file, api_key_env, model_id_env):
    """Generic inference runner for Roboflow models."""
    try:
        api_key = os.getenv(api_key_env)
        model_id = os.getenv(model_id_env)

        if not api_key:
            return {"error": f"Walang Key. Check Sa Environment File: {api_key_env}"}
        if not os.path.exists(image_file):
            return {"error": f"Check Test_Images: {image_file}"}
        if not model_id:
            return {"error": f"Walang Model ID. Check Sa Environment File: {model_id_env}"}

        client = InferenceHTTPClient(
            api_url="https://detect.roboflow.com",
            api_key=api_key
        )
        result = client.infer(image_file, model_id)

        return result if result else {"error": "No predictions returned"}

    except Exception as e:
        return {"error": f"May Error: {str(e)}"}