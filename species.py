from dotenv import load_dotenv
import os
from pprint import pprint
from inference_sdk import InferenceHTTPClient
import json
from utils import convert_bbox_to_cm as convert
import math

load_dotenv()  # Load environment variables


GROWTH_PARAMETERS = {
  "ISLAND MACKEREL":{"L_inf":30.1, "K":2.00, "t0":0.91},
  "LAPU-LAPU":{"L_inf":30.9, "K":0.51, "t0":0.47},
  "TULINGAN":{"L_inf":78.5, "K":1.25, "t0":0.85},
  "BANGUS":{"L_inf":29.4, "K":0.090, "t0":0},
  "TILAPIA":{"L_inf":44.2, "K":0.43, "t0":0.333},
}



def estimate_age(length_cm, species, maturity_threshold=0.8):
    param = GROWTH_PARAMETERS.get(species.upper())
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



def predict_fish_specie(image_file):
  try:
    api_key = os.getenv('API_KEY')
    model_id = os.getenv('MODEL_ID')

    if not api_key:
      return {"error": "Walang Key. Check Sa Environment File"}

    if not os.path.exists(image_file):
      return {"error": f"Check Test_Images: {image_file}"}

    if not model_id:
      return {"error": "Walang Model ID. Check Sa Environment File"}

    client = InferenceHTTPClient(
      api_url="https://detect.roboflow.com",
      api_key=api_key
    )

    result = client.infer(image_file, model_id)

    return result

  except Exception as e:  
    return {"error": f"May Error: {str(e)}"}




def process_prediction(result):
  """Process The Image And Return Formatted Results"""
  if not result or "predictions" not in result or len(result["predictions"]) == 0:
    return {"message": "Walang Isda Na Nadetect","fish_detected": []}
  

  pixels_per_cm = 37.7952755906 #standard pixel to cm conversion pero aayusin pa to
  detected_fish = []


  for prediction in result["predictions"]:

    fish_data = {
      "id":prediction.get("detection_id", "Unknown"),
      "species":prediction.get("class", "Unknown"),
      "confidence":prediction.get("confidence", 0),
      "width_px":prediction.get("width", 0),
      "height_px": prediction.get("height", 0)
    }

    width_cm, height_cm = convert(fish_data["width_px"],fish_data["height_px"] , pixels_per_cm)


    estimate_age_result = estimate_age(width_cm, fish_data["species"])
    
    fish_data.update({
        "width_cm": width_cm,
        "height_cm": height_cm,
        "area_cm2": width_cm * height_cm,
        "days_before_maturity": estimate_age_result.get("days_before_maturity", "Unknown")
    })
    detected_fish.append(fish_data)


  return {
    "message": "Fish species detected successfully","fish_detected": detected_fish
  }















# def test_predict_fish_specie():
#   image = "test_images/test3.jpg"
#   print(f"Testing image: {image}")
#   pixels_per_cm = 37.7952755906  # Example value, adjust as needed

#   result = predict_fish_specie(image) # Call the function to predict fish species


#   # print("Full Result Dictionary:")
#   # print(json.dumps(result, indent=4))

  

#   if not result or "predictions" not in result or len(result["predictions"])== 0:
#     print("Walang Isda Na Nadetect")
#     return
  
#   pixels_per_cm = 37.7952755906  # Example value, adjust as needed

#   print("Detected Fish Species:")
#   for prediction in result["predictions"]:
#     id = prediction.get("detection_id", "Unknown")
#     species = prediction.get("class", "Unknown")
#     confidence = prediction.get("confidence", 0)
#     width_px = prediction.get("width", 0)
#     height_px = prediction.get("height", 0)

  

#     width_cm, height_cm = convert(width_px, height_px, pixels_per_cm)
#     area_cm2 = width_cm * height_cm

#     print(f"ID: {id}, Species: {species}, Confidence: {confidence:.2f}, "
#           f"Width: {width_cm:.2f} cm, Height: {height_cm:.2f} cm, Area: {area_cm2:.2f} cm²")



# if __name__ == "__main__":
#   test_predict_fish_specie()
  


