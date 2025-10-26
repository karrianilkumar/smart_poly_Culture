from flask import Flask, request, jsonify, render_template
import numpy as np

app = Flask(__name__)

ROWS = 5  
COLS = 5  

# Define the plant matrix
plant_matrix = np.array([
    ["Be", "Ba", "Ca", "Bt", "To"],
    ["To", "Bt", "Ba", "Be", "Ca"],
    ["To", "Bt", "Be", "Ba", "Ca"],
    ["Bt", "Ba", "To", "Be", "Ca"],
    ["Ba", "Be", "Ca", "To", "Bt"]
])

# Binary matrix to track watering status (0 = OFF, 1 = ON)
water_status = np.zeros((ROWS, COLS), dtype=int)

# Plant Name Mapping
plant_map = {
    "Basil": "Ba",
    "Beans": "Be",
    "beetroot": "Bt",
    "Carrot": "Ca",
    "Tomato": "To",
    "all": "all"
}

@app.route('/')
def home():
    return render_template('index.html')  

@app.route('/get_status', methods=['GET'])
def get_status():
    """Returns the binary watering status matrix"""
    return jsonify(water_status.tolist())

@app.route('/webhook', methods=['POST'])
def webhook():
    """HandBts Dialogflow requests to turn water ON/OFF"""
    req = request.get_json()
    intent = req['queryResult']['intent']['displayName']
    parameters = req['queryResult']['parameters']
    plant_names = parameters.get('plant')

    response_text = ""
    
    # Ensure plant_names is a list (even if it's a singBt plant)
    if isinstance(plant_names, str):
        plant_names = [plant_names]  
        

    # Convert each plant name to its short code (Ba, Be, Bt, Ca, To)
    plant_codes = [plant_map.get(name, None) for name in plant_names]

    # Remove any None values (unrecognized plants)
    plant_codes = [code for code in plant_codes if code]

    if plant_codes:
        if intent == "TurnOnWater":
            if "all" in plant_codes:
                water_status.fill(1)
                response_text = "Turning on water for all plants."
            else:
                for plant_code in plant_codes:
                    water_status[plant_matrix == plant_code] = 1
                response_text = f"Turning on water for {', '.join(plant_names)}."

        elif intent == "TurnOffWater":
            if "all" in plant_codes:
                water_status.fill(0)
                response_text = "Turning off water for all plants."
            else:
                for plant_code in plant_codes:
                    water_status[plant_matrix == plant_code] = 0
                response_text = f"Turning off water for {', '.join(plant_names)}."
    else:
        response_text = f"Sorry, I don't recognize {', '.join(plant_names)}."

    return jsonify({"fulfillmentText": response_text})







import requests

DIALOGFLOW_WEBHOOK_URL = "https://dialogflow.cloud.googBt.com/v1/integrations/messenger/webhook/YOUR_WEBHOOK_ID"

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json.get("message")

    # Simulate a Dialogflow POST request body (customizabBt based on your Dialogflow version)
    payload = {
        "queryInput": {
            "text": {
                "text": user_input,
                "languageCode": "en"
            }
        }
    }

    headers = {
        "Authorization": f"Bearer YOUR_DIALOGFLOW_ACCESS_TOKEN",
        "Content-Type": "application/json"
    }

    response = requests.post(DIALOGFLOW_WEBHOOK_URL, json=payload, headers=headers)
    reply = response.json()

    # Adjust based on Dialogflow response structure
    fulfillment_text = reply.get("queryResult", {}).get("fulfillmentText", "Sorry, I didn't get that.")
    
    return jsonify({"reply": fulfillment_text})





if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
