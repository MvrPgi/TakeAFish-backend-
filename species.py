from dotenv import load_dotenv
import os
from pprint import pprint
import requests
from inference_sdk import InferenceHTTPClient  # Roboflow Inference import

load_dotenv()

def get_species_from_image(image_path, model_id="fish-pytorch-phb1f/3"):
    try:
        # Get API key
        api_key = os.getenv('API_KEY')
        model_id = os.getenv('MODEL_ID', model_id)  # Use environment variable if set
        
        if not api_key:
            return {
                "error": "API key not found. Please set the API_KEY environment variable."
            }
        
        # Check if image file exists
        if not os.path.exists(image_path):
            return {
                "error": f"Image file not found: {image_path}"
            }
        
        # Initialize Roboflow Inference client
        client = InferenceHTTPClient(
            api_url="https://detect.roboflow.com",
            api_key=api_key
        )
        
        # Make prediction
        result = client.infer(image_path, model_id=model_id)
        
        return result
        
    except Exception as e:
        return {
            "error": f"An error occurred: {str(e)}"
        }

def test_roboflow():
    image_path = "test_images/test1.jpg"
    
    print(f"Testing image: {image_path}")
    
    try:
        result = get_species_from_image(image_path)
        
        # Check if result is None
        if result is None:
            print("Error: get_species_from_image() returned None")
            return
            
        # Check if result is the expected type (dict)
        if not isinstance(result, dict):
            print(f"Error: Expected dict, got {type(result)}: {result}")
            return
            
        # Now safely check for error key
        if "error" in result:
            print(f"API Error: {result['error']}")
        else:
            print("Success! Species identification result:")
            
            # Process the results
            detected_objects = result.get('predictions', [])
            print(f"Number of objects detected: {len(detected_objects)}")
            
            for idx, obj in enumerate(detected_objects, start=1):
                class_name = obj.get('class', 'Unknown')
                confidence = obj.get('confidence', 0)
                print(f"Object {idx}: Class = {class_name}, Confidence = {confidence:.2f}")
                
                # Additional details if available
                if 'x' in obj and 'y' in obj:
                    x, y = obj.get('x'), obj.get('y')
                    width, height = obj.get('width', 0), obj.get('height', 0)
                    print(f"    Position: ({x:.1f}, {y:.1f}), Size: {width:.1f} x {height:.1f}")
            
            print("\nFull result:")
            pprint(result)
            
    except Exception as e:
        print(f"Exception occurred: {e}")
        print(f"Exception type: {type(e)}")

if __name__ == "__main__":
    test_roboflow()