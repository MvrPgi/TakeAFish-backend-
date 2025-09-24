# config.py
GROWTH_PARAMETERS = {
  "ISLAND MACKEREL":{"L_inf":30.1, "K":2.00, "t0":0.91},
  "LAPU-LAPU":{"L_inf":30.9, "K":0.51, "t0":0.47},
  "TULINGAN":{"L_inf":78.5, "K":1.25, "t0":0.85},
  "BANGUS":{"L_inf":29.4, "K":0.090, "t0":0},
  "TILAPIA":{"L_inf":44.2, "K":0.43, "t0":0.333},
}


REFERENCE_COINS_DIAMETER_CM = {
    "1_PESO": 2.30,   # 23.0 CM
    "5_PESO": 2.50,   # 25.0 CM
    "10_PESO": 2.70   # 27.0 CM
}

CLASS_ID_TO_COIN = {
    0: "1_PESO",
    1: "10_PESO",
    2: "5_PESO"
}

PIXELS_PER_CM = 37.7952755906


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

MAX_FILE_SIZE = 3 * 1024 * 1024  # 3MB





CLASS_CONF_THRESHOLDS = {
    "ISLAND MACKEREL": 0.5,       
    "LAPU-LAPU": 0.5,      
    "TULINGAN": 0.5,   
    "BANGUS": 0.5,        
    "TILAPIA": 0.5,        
    "0": 0.1,
    "1": 0.1,
    "2": 0.1
}


