from dotenv import load_dotenv
import logging
import math
from services.config import  GROWTH_PARAMETERS
load_dotenv()  # Load environment variables
from datetime import datetime, timedelta


def calculate_age_from_length(length_cm, L_inf, K, t0):
    """Calculate age from length (reverse Von Bertalanffy)"""
    if length_cm >= L_inf:
        return 10.0  # Cap age at 10 years if length exceeds L_inf
    try:
        return t0 - (1/K) * math.log(1 - (length_cm / L_inf))
    except (ValueError, ZeroDivisionError):
        return t0 + 0.1  # Default to slightly above t0

def age_to_length(age_years, L_inf, K, t0):
    """Convert age to length using Von Bertalanffy"""
    if age_years <= t0:
        return 0.1  # Very small fish, just above zero
    return L_inf * (1 - math.exp(-K * (age_years - t0)))

def calculate_species_forecast(species, days_before_maturity, current_date):
    """Calculate monthly growth forecast for a species using UTILS.py parameters"""

    if days_before_maturity < 0:
        logging.warning(f"Negative days before maturity for {species}: {days_before_maturity}")
        return {"error": f"Invalid days before maturity for {species}: {days_before_maturity}"}


    # Get growth parameters from your config
    species_key = species.upper().strip()
    params = GROWTH_PARAMETERS.get(species_key)
    if not params:
        available_species = list(GROWTH_PARAMETERS.keys())
        logging.warning(f"Species not found: {species}. Available species: {available_species}")
        return {"error": f"No growth parameters for {species}. Available: {available_species}"}
    
    L_inf = params["L_inf"]
    K = params["K"]
    t0 = params["t0"]
    
    # Calculate maturity age first (using your actual parameters)
    maturity_length = L_inf * 0.8  # 80% of L_inf is typically maturity
    maturity_age_years = calculate_age_from_length(maturity_length, L_inf, K, t0)
    
    # Calculate current age and length
    current_age_years = maturity_age_years - (days_before_maturity / 365.0)
    
    # Ensure current age is not negative
    if current_age_years < t0:
        current_age_years = t0 + 0.1  # Start slightly above t0
    
    current_length = age_to_length(current_age_years, L_inf, K, t0)
    
    # Generate 12-month forecast
    monthly_forecast = []
    previous_length = current_length
    
    for month in range(1, 13):
        future_age = current_age_years + (month / 12.0)
        future_length = age_to_length(future_age, L_inf, K, t0)
        
        # Calculate growth from previous month
        growth = future_length - previous_length
        
        forecast_date = current_date + timedelta(days=30 * month)
        
        monthly_forecast.append({
            "month": month,
            "date": forecast_date.strftime("%Y-%m-%d"),
            "age_years": round(future_age, 2),
            "length_cm": round(future_length, 2),
            "growth_cm": round(growth, 2),
            "total_growth_cm": round(future_length - current_length, 2)
        })
        
        previous_length = future_length
        logging.info(f"Forecast for {species} Month {month}: Age {future_age}, Length {future_length}")
    
    logging.info(f"Completed forecast for {species}")
    return {
        "current_status": {
            "days_before_maturity": days_before_maturity,
            "current_age_years": round(current_age_years, 2),
            "current_length_cm": round(current_length, 2),
            "maturity_length_cm": round(maturity_length, 2),
            "maturity_age_years": round(maturity_age_years, 2)
        },
        "monthly_forecast": monthly_forecast
    }


def generate_monthly_forecast(species_days_map):
    """Generate monthly forecast for multiple species"""
    try:
        logging.info(f"Monthly forecast requested: {species_days_map}")
        
        if not species_days_map:
            return {"error": "No species data provided"}
        
        # Process each fish species
        forecasts = {}
        current_date = datetime.now()
        
        for species, days_before_maturity in species_days_map.items():
            try:
                species_forecast = calculate_species_forecast(
                    species, 
                    days_before_maturity, 
                    current_date
                )
                forecasts[species] = species_forecast
            except Exception as e:
                logging.error(f"Error processing {species}: {str(e)}")
                forecasts[species] = {"error": f"Could not process {species}"}
        
        logging.info(f"Forecast completed: {len(forecasts)} species processed")
        return {
            "message": "Monthly forecast generated successfully",
            "generated_date": current_date.isoformat(),
            "forecasts": forecasts
        }
        
    except Exception as e:
        logging.exception("Error in monthly forecast generation")
        return {"error": f"Server error: {str(e)}"}