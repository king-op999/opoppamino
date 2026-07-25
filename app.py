from flask import Flask, request, jsonify
import requests
import time
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)

CREDIT = "@BRONX_ULTRA"
DEVELOPER = "@BRONX_ULTRA"

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

def deep_clean(data):
    if isinstance(data, dict):
        blacklist = ['by', 'owner', 'developer_name', 'created_by', 'author', 'credit_to', 'thanks', 'ftgamer', '@ftgamer2', 'ft_osint', '_proxy', 'proxy', 'proxy_used', 'session_id', 'pool_size', 'total_fetched', 'tested', 'note', 'powered', 'powered_by', 'maintained_by', 'source_ip']
        for field in blacklist:
            data.pop(field, None)
        data['credit'] = CREDIT
        for key in list(data.keys()):
            if isinstance(data[key], dict): data[key] = deep_clean(data[key])
            elif isinstance(data[key], list): data[key] = [deep_clean(i) if isinstance(i, dict) else i for i in data[key]]
    return data

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

@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# ============ HOME ============
@app.route('/')
def home():
    return jsonify({
        "status": "BRONX ULTRA API ONLINE",
        "version": "6.0",
        "endpoints": {
            "bomber": "/api/bomber?key=KEY&number=NUMBER&counter=100",
            "pan": "/api/pan?key=KEY&pan=PAN",
            "upi": "/api/upi?key=KEY&upi=example@ybl"
        },
        "demo_key": "demo1",
        "credit": CREDIT
    })

# ============ SMS BOMBER ============
@app.route('/api/bomber')
def api_bomber():
    key = request.args.get('key', '').strip()
    kc = verify_key(key)
    if not kc['valid']: return jsonify({"success": False, "error": kc['error'], "credit": CREDIT}), 401
    
    number = request.args.get('number', '').strip()
    counter = request.args.get('counter', '100').strip()
    
    if not number or not number.isdigit() or len(number) != 10:
        return jsonify({"success": False, "error": "Valid 10 digit number required!", "credit": CREDIT}), 400
    
    try: counter = max(1, min(int(counter), 500))
    except: counter = 100
    
    start_time = time.time()
    
    try:
        resp = requests.get(f"{BOMBER_API}?key=bronx-ultra-king-ft-bro-op&number={number}&counter={counter}", timeout=90)
        data = resp.json()
        if isinstance(data, dict):
            data = deep_clean(data)
            data['response_time_ms'] = round((time.time() - start_time) * 1000)
            data['plan'] = kc['type']
            return jsonify(data)
    except:
        pass
    
    return jsonify({"success": True, "number": number, "counter": counter, "status": "Bombing initiated", "response_time_ms": round((time.time() - start_time) * 1000), "credit": CREDIT})

# ============ PAN INFO ============
@app.route('/api/pan')
def api_pan():
    key = request.args.get('key', '').strip()
    kc = verify_key(key)
    if not kc['valid']: return jsonify({"success": False, "error": kc['error'], "credit": CREDIT}), 401
    
    pan = request.args.get('pan', '').strip().upper()
    if not pan or len(pan) != 10:
        return jsonify({"success": False, "error": "Valid 10 char PAN required!", "credit": CREDIT}), 400
    
    start_time = time.time()
    
    try:
        resp = requests.get(f"{PAN_API}?key=bronx-ultra-king-ft-bro-op&pan={pan}", timeout=60)
        data = resp.json()
        if isinstance(data, dict):
            data = deep_clean(data)
            data['response_time_ms'] = round((time.time() - start_time) * 1000)
            data['plan'] = kc['type']
            return jsonify(data)
    except:
        pass
    
    return jsonify({"success": False, "error": "API call failed!", "pan": pan, "credit": CREDIT}), 500

# ============ UPI DUAL LOOKUP ============
@app.route('/api/upi')
def api_upi():
    print("=" * 50)
    print("🔥 UPI DUAL API CALLED")
    print("=" * 50)
    
    key = request.args.get('key', '').strip()
    kc = verify_key(key)
    if not kc['valid']:
        return jsonify({"success": False, "error": kc['error'], "credit": CREDIT}), 401
    
    upi_id = request.args.get('upi', '').strip()
    
    if not upi_id or '@' not in upi_id:
        return jsonify({"success": False, "error": "Valid UPI ID required (e.g., name@oksbi)!", "credit": CREDIT}), 400
    
    print(f"📱 UPI ID: {upi_id}")
    
    start_time = time.time()
    
    # ===== API 1 =====
    api1_url = f"{UPI_API_1}?key=op&upi={upi_id}"
    api1_data = None
    api1_success = False
    api1_time = 0
    
    print(f"📡 [API 1] Calling: {api1_url}")
    
    try:
        t1 = time.time()
        resp1 = requests.get(api1_url, timeout=30, verify=False)
        api1_time = round((time.time() - t1) * 1000)
        print(f"📡 [API 1] Status: {resp1.status_code} | Time: {api1_time}ms")
        
        if resp1.status_code == 200:
            try:
                api1_data = resp1.json()
                api1_data = deep_clean(api1_data)
                api1_success = True
                print(f"📡 [API 1] SUCCESS")
            except Exception as e:
                api1_data = {"raw_response": resp1.text[:500]}
                print(f"📡 [API 1] JSON Parse Error: {e}")
        else:
            api1_data = {"error": f"Status: {resp1.status_code}"}
    except requests.exceptions.Timeout:
        api1_data = {"error": "API 1 Timeout"}
        api1_time = 30000
        print(f"📡 [API 1] TIMEOUT")
    except Exception as e:
        api1_data = {"error": str(e)}
        print(f"📡 [API 1] Error: {e}")
    
    # ===== API 2 =====
    api2_url = f"{UPI_API_2}?upi_id={upi_id}&key=456"
    api2_data = None
    api2_success = False
    api2_time = 0
    
    print(f"📡 [API 2] Calling: {api2_url}")
    
    try:
        t2 = time.time()
        resp2 = requests.get(api2_url, timeout=30, verify=False)
        api2_time = round((time.time() - t2) * 1000)
        print(f"📡 [API 2] Status: {resp2.status_code} | Time: {api2_time}ms")
        
        if resp2.status_code == 200:
            try:
                api2_data = resp2.json()
                api2_data = deep_clean(api2_data)
                api2_success = True
                print(f"📡 [API 2] SUCCESS")
            except Exception as e:
                api2_data = {"raw_response": resp2.text[:500]}
                print(f"📡 [API 2] JSON Parse Error: {e}")
        else:
            api2_data = {"error": f"Status: {resp2.status_code}"}
    except requests.exceptions.Timeout:
        api2_data = {"error": "API 2 Timeout"}
        api2_time = 30000
        print(f"📡 [API 2] TIMEOUT")
    except Exception as e:
        api2_data = {"error": str(e)}
        print(f"📡 [API 2] Error: {e}")
    
    # ===== MERGE =====
    total_time = round((time.time() - start_time) * 1000)
    
    # Extract merged name
    merged_name = None
    merged_bank = None
    
    if api1_data and isinstance(api1_data, dict):
        merged_name = api1_data.get('name') or api1_data.get('account_holder')
        merged_bank = api1_data.get('bank') or api1_data.get('bank_name')
        # Check nested
        for k in ['data', 'result', 'vpa_details']:
            nested = api1_data.get(k, {})
            if isinstance(nested, dict):
                merged_name = merged_name or nested.get('name') or nested.get('owner')
                merged_bank = merged_bank or nested.get('bank') or nested.get('bank_name')
    
    if api2_data and isinstance(api2_data, dict):
        result = api2_data.get('result', {}) or {}
        bank_info = result.get('bank_info', {}) or result.get('bank_details', {}) or {}
        merged_name = merged_name or result.get('name') or api2_data.get('name')
        merged_bank = merged_bank or bank_info.get('bank_name') or result.get('bank')
    
    print(f"👤 Merged Name: {merged_name}")
    print(f"🏦 Merged Bank: {merged_bank}")
    print(f"✅ Total Time: {total_time}ms")
    print("=" * 50)
    
    final = {
        "success": api1_success or api2_success,
        "query": upi_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_response_time_ms": total_time,
        
        "merged_result": {
            "name": merged_name,
            "bank": merged_bank,
            "sources_working": sum([api1_success, api2_success]),
            "total_sources": 2
        },
        
        "api_1_bronx": {
            "source": "BRONX UPI API",
            "url": UPI_API_1,
            "success": api1_success,
            "response_time_ms": api1_time,
            "data": api1_data
        },
        
        "api_2_godlevel": {
            "source": "GOD LEVEL UPI API",
            "url": UPI_API_2,
            "success": api2_success,
            "response_time_ms": api2_time,
            "data": api2_data
        },
        
        "plan": kc['type'],
        "credit": CREDIT
    }
    
    return jsonify(final)

# ============ HEALTH ============
@app.route('/health')
def health():
    return jsonify({"status": "ONLINE", "version": "6.0", "credit": CREDIT})

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found", "home": "/", "credit": CREDIT}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"""
╔══════════════════════════════════════╗
║   🔥 BRONX ULTRA API v6.0          ║
║   Port: {port}                       ║
║   Endpoints:                        ║
║   /api/bomber  - SMS Bomber        ║
║   /api/pan     - PAN Info          ║
║   /api/upi     - UPI Dual Lookup   ║
║   Credit: {CREDIT}      ║
╚══════════════════════════════════════╝
""")
    app.run(host='0.0.0.0', port=port)
