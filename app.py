from flask import Flask, request, jsonify
import requests
import time
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)

CREDIT = "@BRONX_ULTRA"

# ============ REAL API URLs ============
BOMBER_API = "https://ft-osint-api.duckdns.org/api/bomber"
PAN_API = "https://ft-osint-api.duckdns.org/api/paninfo"
UPI_API_1 = "https://bronx-web-api.onrender.com/api/key-bronx/upi"
UPI_API_2 = "https://god-level-upi-info.onrender.com/api/upi"

# ============ KEY DATABASE ============
KEYS_DB = {
    "demo1": {"expiry": "2099-12-31", "type": "Demo", "limit": 10, "daily_usage": {}},
    "primum11": {"expiry": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'), "type": "Premium", "limit": "unlimited", "daily_usage": {}},
    "diamond22": {"expiry": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'), "type": "Diamond", "limit": "unlimited", "daily_usage": {}},
    "diamond33": {"expiry": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'), "type": "Diamond", "limit": "unlimited", "daily_usage": {}},
    "diamond44": {"expiry": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'), "type": "Diamond", "limit": "unlimited", "daily_usage": {}},
    "456": {"expiry": "2099-12-31", "type": "Premium", "limit": "unlimited", "daily_usage": {}},
}

def verify_key(key):
    if not key: return {"valid": False, "error": "API Key required!"}
    if key not in KEYS_DB: return {"valid": False, "error": "Invalid API Key!"}
    key_data = KEYS_DB[key]
    expiry_date = datetime.strptime(key_data['expiry'], '%Y-%m-%d')
    if datetime.now() > expiry_date: return {"valid": False, "error": "Key expired!"}
    if key_data['limit'] != "unlimited":
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in key_data['daily_usage']: key_data['daily_usage'][today] = 0
        if key_data['daily_usage'][today] >= key_data['limit']: return {"valid": False, "error": f"Daily limit ({key_data['limit']}) reached!"}
        key_data['daily_usage'][today] += 1
    return {"valid": True, "type": key_data['type']}

def clean_source_info(data):
    """Remove only source/url/response_time_ms/success - keep everything else"""
    if isinstance(data, dict):
        # Remove only these 4 fields
        data.pop('source', None)
        data.pop('url', None)
        data.pop('response_time_ms', None)
        data.pop('success', None)
        # Also remove proxy junk
        data.pop('_proxy', None)
        data.pop('proxy', None)
        
        # Recursively clean nested dicts
        for key in list(data.keys()):
            if isinstance(data[key], dict):
                data[key] = clean_source_info(data[key])
            elif isinstance(data[key], list):
                data[key] = [clean_source_info(i) if isinstance(i, dict) else i for i in data[key]]
    return data

@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# ============ HOME ============
@app.route('/')
def home():
    return jsonify({"status": "online"})

# ============ SMS BOMBER ============
@app.route('/api/bomber')
def api_bomber():
    key = request.args.get('key', '').strip()
    kc = verify_key(key)
    if not kc['valid']: return jsonify({"error": kc['error']}), 401
    
    number = request.args.get('number', '').strip()
    counter = request.args.get('counter', '100').strip()
    
    if not number or not number.isdigit() or len(number) != 10:
        return jsonify({"error": "Valid 10 digit number required!"}), 400
    
    try: counter = max(1, min(int(counter), 500))
    except: counter = 100
    
    try:
        resp = requests.get(f"{BOMBER_API}?key=bronx-ultra-king-ft-bro-op&number={number}&counter={counter}", timeout=90)
        data = resp.json()
        data = clean_source_info(data)
        return jsonify(data)
    except:
        return jsonify({"status": "completed", "number": number, "counter": counter})

# ============ PAN INFO ============
@app.route('/api/pan')
def api_pan():
    key = request.args.get('key', '').strip()
    kc = verify_key(key)
    if not kc['valid']: return jsonify({"error": kc['error']}), 401
    
    pan = request.args.get('pan', '').strip().upper()
    if not pan or len(pan) != 10:
        return jsonify({"error": "Valid 10 char PAN required!"}), 400
    
    try:
        resp = requests.get(f"{PAN_API}?key=bronx-ultra-king-ft-bro-op&pan={pan}", timeout=60)
        data = resp.json()
        data = clean_source_info(data)
        return jsonify(data)
    except:
        return jsonify({"error": "API call failed", "pan": pan}), 500

# ============ UPI DUAL LOOKUP ============
@app.route('/api/upi')
def api_upi():
    key = request.args.get('key', '').strip()
    kc = verify_key(key)
    if not kc['valid']: return jsonify({"error": kc['error']}), 401
    
    upi_id = request.args.get('upi', '').strip()
    
    if not upi_id or '@' not in upi_id:
        return jsonify({"error": "Valid UPI ID required (e.g., name@oksbi)!"}), 400
    
    # ===== FETCH API 1 =====
    api1_data = None
    try:
        resp1 = requests.get(f"{UPI_API_1}?key=op&upi={upi_id}", timeout=30, verify=False)
        if resp1.status_code == 200:
            api1_data = resp1.json()
            api1_data = clean_source_info(api1_data)
    except:
        api1_data = {"error": "Failed to fetch"}
    
    # ===== FETCH API 2 =====
    api2_data = None
    try:
        resp2 = requests.get(f"{UPI_API_2}?upi_id={upi_id}&key=456", timeout=30, verify=False)
        if resp2.status_code == 200:
            api2_data = resp2.json()
            api2_data = clean_source_info(api2_data)
    except:
        api2_data = {"error": "Failed to fetch"}
    
    # ===== MERGE - Keep all real data, just hide source info =====
    result = {}
    
    # Add API 1 data (without source info)
    if api1_data and isinstance(api1_data, dict):
        for k, v in api1_data.items():
            if k not in ['source', 'url', 'response_time_ms', 'success', '_proxy', 'proxy']:
                result[k] = v
    
    # Add API 2 data (without source info)
    if api2_data and isinstance(api2_data, dict):
        for k, v in api2_data.items():
            if k not in ['source', 'url', 'response_time_ms', 'success', '_proxy', 'proxy']:
                # If key already exists from API1, don't overwrite
                if k not in result:
                    result[k] = v
    
    # If both returned error
    if not result:
        result = {"error": "Both APIs failed"}
    
    result['query'] = upi_id
    
    return jsonify(result)

# ============ HEALTH ============
@app.route('/health')
def health():
    return jsonify({"status": "online"})

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
