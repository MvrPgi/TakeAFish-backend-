from dotenv import load_dotenv
import os
from inference_sdk import InferenceHTTPClient
from utils import convert_bbox_to_cm as convert, run_inference
from utils import calculate_pixels_per_cm
import math
from config import CLASS_ID_TO_COIN, GROWTH_PARAMETERS,  PIXELS_PER_CM, REFERENCE_COINS_DIAMETER_CM
load_dotenv()  # Load environment variables



def predict_fish_specie(image_file):
    """Detect fish species."""
    return run_inference(image_file, "API_KEY", "MODEL_ID")
  
def detect_reference_coin(image_file):
    """Detect coin reference for calibration."""
    result = run_inference(image_file, "REFERENCE_API_KEY", "COIN_MODEL_ID")
    if "error" in result:
        return result
    if not result or "predictions" not in result or len(result["predictions"]) == 0:
        return {"message": "Walang Barya Na Nadetect", "pixels_per_cm": 0}

    # Pick most confident coin
    coin_prediction = result["predictions"][0]
    coin_class_id = coin_prediction.get("class_id", None)
    coin_label = CLASS_ID_TO_COIN.get(coin_class_id, None)
    return calculate_pixels_per_cm(coin_prediction, coin_label)


def estimate_age(length_cm, species, maturity_threshold=0.8):
    param = GROWTH_PARAMETERS.get(species, GROWTH_PARAMETERS.get(species.upper()))
    if param is None:
        return {"error": f"Unknown species: {species}"}

    try:
        L_inf = param["L_inf"]
        K = param["K"]
        t0 = param["t0"]

        maturity_length = L_inf * maturity_threshold
        maturity_age = (math.log((L_inf - maturity_length) / L_inf) / -K) + t0
        maturity_age_days = maturity_age * 365

        # current age
        current_age = (math.log((L_inf - length_cm) / L_inf) / -K) + t0
        current_age_days = current_age * 365

        days_before_maturity = maturity_age_days - current_age_days

        return {
            "days_before_maturity": max(0, round(days_before_maturity, 2))
        }
    except Exception as e:
        return {"error": f"Error estimating age: {str(e)}"}


def process_prediction(result, image_file):
    """Process fish detection and convert to cm using coin if available."""
    if not result or "predictions" not in result or len(result["predictions"]) == 0:
        return {"message": "Walang Isda Na Nadetect", "fish_detected": []}

    # Try to detect coin for dynamic calibration
    coin_result = detect_reference_coin(image_file)
    pixels_per_cm = coin_result.get("pixels_per_cm", 0) if isinstance(coin_result, dict) else 0

    # Fallback to default PIXELS_PER_CM if coin not detected
    if pixels_per_cm <= 0:
        pixels_per_cm = PIXELS_PER_CM
        coin_used = {
            "message": "Using default calibration",
            "coin_label": None,
            "width_px": None,
            "coin_diameter_cm": None,
            "pixels_per_cm": pixels_per_cm
        }
    else:
        coin_used = coin_result   # keep full details from calculate_pixels_per_cm

    detected_fish = []

    for prediction in result["predictions"]:
        fish_data = {
            "id": prediction.get("detection_id", "Unknown"),
            "species": prediction.get("class", "Unknown"),
            "confidence": prediction.get("confidence", 0),
            "width_px": prediction.get("width", 0),
            "height_px": prediction.get("height", 0)
        }

        width_cm, height_cm = convert(
            fish_data["width_px"], fish_data["height_px"], pixels_per_cm
        )
        estimate_age_result = estimate_age(width_cm, fish_data["species"])

        fish_data.update({
            "width_cm": width_cm,
            "height_cm": height_cm,
            "area_cm2": width_cm * height_cm,
            "days_before_maturity": estimate_age_result.get("days_before_maturity", "Mature")
        })
        detected_fish.append(fish_data)

    return {
        "message": "Fish species detected successfully",
        "coin_used": coin_used,
        "fish_detected": detected_fish
    }















