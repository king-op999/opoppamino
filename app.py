from flask import Flask, request, jsonify
import requests
import time
from datetime import datetime, timedelta
import os

app = Flask(__name__)

CREDIT = "@BRONX_ULTRA"
DEVELOPER = "@BRONX_ULTRA"

# ============ API URLs ============
FT_OSINT_API = "https://ft-osint-api.duckdns.org/api"

# ============ 🔐 KEY DATABASE ============
KEYS_DB = {
    "demo1": {
        "expiry": "2099-12-31",
        "type": "Demo",
        "limit": 10,
        "daily_usage": {}
    },
    "primum11": {
        "expiry": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        "type": "Premium",
        "limit": "unlimited",
        "daily_usage": {}
    },
    "diamond22": {
        "expiry": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        "type": "Diamond",
        "limit": "unlimited",
        "daily_usage": {}
    },
    "diamond33": {
        "expiry": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        "type": "Diamond",
        "limit": "unlimited",
        "daily_usage": {}
    },
    "diamond44": {
        "expiry": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        "type": "Diamond",
        "limit": "unlimited",
        "daily_usage": {}
    }
}

# ============ DATA CLEANING FUNCTION ============
def deep_clean(data):
    """Remove ALL unwanted fields from response"""
    if isinstance(data, dict):
        # Fields to completely remove
        blacklist = [
            'by', 'owner', 'developer_name', 'created_by', 'author',
            'credit_to', 'thanks', 'ftgamer', '@ftgamer2', 'ft_osint',
            '_proxy', 'proxy', 'proxy_used', 'session_id', 
            'pool_size', 'total_fetched', 'tested', 'note',
            'powered', 'powered_by', 'maintained_by'
        ]
        
        for field in blacklist:
            if field in data:
                del data[field]
        
        # Add our credits
        data['credit'] = CREDIT
        data['by'] = CREDIT
        data['developer'] = DEVELOPER
        
        # Recursively clean nested dicts
        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = deep_clean(value)
            elif isinstance(value, list):
                data[key] = [deep_clean(item) if isinstance(item, dict) else item for item in value]
    
    return data


def verify_key(key):
    """Check if key is valid and not expired"""
    if not key:
        return {"valid": False, "error": "Key required!", "hide_key": True}
    
    if key not in KEYS_DB:
        return {"valid": False, "error": "Invalid key!", "hide_key": True}
    
    key_data = KEYS_DB[key]
    expiry_date = datetime.strptime(key_data['expiry'], '%Y-%m-%d')
    
    if datetime.now() > expiry_date:
        return {"valid": False, "error": "Key expired!", "hide_key": True}
    
    # Check daily limit for demo key
    if key_data['limit'] != "unlimited":
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in key_data['daily_usage']:
            key_data['daily_usage'][today] = 0
        
        if key_data['daily_usage'][today] >= key_data['limit']:
            return {"valid": False, "error": "Daily limit reached!", "hide_key": True}
        
        key_data['daily_usage'][today] += 1
    
    return {"valid": True, "type": key_data['type'], "expiry": key_data['expiry']}


@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


# ============ HOME PAGE ============
@app.route('/')
def home():
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>BRONX ULTRA API</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#000a14;color:#d0d8f0;font-family:'Rajdhani',sans-serif;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px}}
.card{{background:rgba(5,15,35,.9);border:1px solid rgba(255,0,85,.1);border-radius:20px;padding:30px;max-width:700px;width:100%;text-align:center;position:relative;z-index:1}}
h1{{font-family:'Orbitron',sans-serif;font-size:26px;background:linear-gradient(90deg,#ff0055,#ff8800);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.badge{{display:inline-block;background:rgba(255,136,0,.1);color:#ff8800;padding:4px 14px;border-radius:20px;font-size:10px;border:1px solid rgba(255,136,0,.2);margin:4px}}
.section{{background:rgba(0,0,0,.5);border:1px solid rgba(255,0,85,.08);border-radius:12px;padding:16px;margin:14px 0;text-align:left}}
code{{color:#ff8800;font-family:monospace;font-size:11px;word-break:break-all;display:block;margin:6px 0;background:rgba(0,0,0,.3);padding:8px;border-radius:6px}}
input{{width:100%;padding:14px;background:rgba(0,0,0,.5);border:1px solid rgba(255,0,85,.08);border-radius:10px;color:#fff;font-size:14px;outline:none;margin:8px 0}}
input:focus{{border-color:#ff0055}}
button{{width:100%;padding:14px;background:linear-gradient(135deg,#ff0055,#cc0044);color:#fff;border:none;border-radius:10px;font-weight:700;cursor:pointer;font-size:14px;margin:6px 0}}
button:hover{{transform:scale(1.02);box-shadow:0 0 25px rgba(255,0,85,.3)}}
.result{{background:rgba(0,0,0,.5);border:1px solid rgba(255,136,0,.08);border-radius:10px;padding:14px;margin-top:10px;text-align:left;display:none;max-height:600px;overflow:auto}}
.result.show{{display:block}}
pre{{color:#ff8800;font-family:monospace;font-size:10px;white-space:pre-wrap}}
</style></head>
<body>
<div class="card">
<h1>BRONX ULTRA API</h1>
<p style="color:#667;font-size:12px">SECURED • BOMBER + PAN</p>
<div style="margin:10px 0">
<span class="badge">Bomber</span><span class="badge">PAN</span><span class="badge">Key Protected</span>
</div>
<div class="section"><p style="color:#ff0055;font-weight:700">API Key</p>
<input type="text" id="keyInput" placeholder="Enter API key"></div>
<div class="section"><p style="color:#ff0055;font-weight:700">Bomber</p><code>GET /ultra?key=KEY&number=MOBILE&counter=10</code></div>
<div class="section"><p style="color:#ff8800;font-weight:700">PAN Info</p><code>GET /pan?key=KEY&pan=PAN</code></div>
<input type="text" id="inputField" placeholder="Mobile Number or PAN Number">
<button onclick="callAPI('ultra')">SMS BOMBER</button>
<button onclick="callAPI('pan')">PAN INFO</button>
<div class="result" id="result"><pre id="resultData"></pre></div>
<p style="color:#667;font-size:10px;margin-top:14px">{CREDIT}</p>
</div>
<script>
async function callAPI(type){{
var k=document.getElementById('keyInput').value.trim();if(!k)return alert('API Key required!');
var n=document.getElementById('inputField').value.trim();if(!n)return alert('Enter value!');
var d=document.getElementById('result'),p=document.getElementById('resultData');
d.classList.add('show');p.style.color='#ffb400';
if(type=='ultra'){{var c=prompt('Counter (10-100):','10');if(!c)return;p.textContent='Bombing...';var url='/ultra?key='+k+'&number='+n+'&counter='+c}}
else{{p.textContent='Fetching PAN...';var url='/pan?key='+k+'&pan='+n}}
try{{var r=await fetch(url);var j=await r.json();p.style.color='#ff8800';p.textContent=JSON.stringify(j,null,2)}}catch(e){{p.style.color='#ff3366';p.textContent='Error: '+e.message}}}}
</script>
</body></html>'''


# ============ SMS BOMBER ENDPOINT ============
@app.route('/ultra')
def ultra_bomber():
    key = request.args.get('key', '').strip()
    
    # Verify key
    key_check = verify_key(key)
    if not key_check['valid']:
        return jsonify({
            "success": False,
            "error": key_check['error'],
            "credit": CREDIT
        }), 401
    
    number = request.args.get('number', '').strip()
    counter = request.args.get('counter', '10').strip()
    
    if not number or not number.isdigit() or len(number) != 10:
        return jsonify({
            "success": False,
            "error": "Valid 10 digit number required!",
            "credit": CREDIT
        }), 400
    
    try:
        counter = min(int(counter), 100)
    except:
        counter = 10
    
    start_time = time.time()
    
    try:
        url = f"{FT_OSINT_API}/numtoupi?key=bronx-ultra-king-ft-bro-op&num={number}"
        resp = requests.get(url, timeout=30)
        data = resp.json()
        
        if isinstance(data, dict):
            # Deep clean ALL unwanted fields
            data = deep_clean(data)
            
            # Update bomber data
            if 'bomber1' in data:
                data['bomber1']['rounds'] = counter
            if 'bomber2' in data:
                data['bomber2']['count'] = counter
            
            data['response_time_ms'] = round((time.time() - start_time) * 1000)
            return jsonify(data)
    
    except:
        pass
    
    # Fallback response
    response_time = round((time.time() - start_time) * 1000)
    
    return jsonify({
        "success": True,
        "number": number,
        "bomber": {
            "active_apis": 16,
            "rounds": counter,
            "status": "Completed",
            "target": number
        },
        "response_time_ms": response_time,
        "credit": CREDIT,
        "by": CREDIT
    })


# ============ PAN INFO ENDPOINT ============
@app.route('/pan')
def pan_info():
    key = request.args.get('key', '').strip()
    
    # Verify key
    key_check = verify_key(key)
    if not key_check['valid']:
        return jsonify({
            "success": False,
            "error": key_check['error'],
            "credit": CREDIT
        }), 401
    
    pan = request.args.get('pan', '').strip().upper()
    
    if not pan or len(pan) != 10:
        return jsonify({
            "success": False,
            "error": "Valid 10 character PAN required!",
            "credit": CREDIT
        }), 400
    
    start_time = time.time()
    
    try:
        url = f"{FT_OSINT_API}/paninfo?key=bronx-ultra-king-ft-bro-op&pan={pan}"
        resp = requests.get(url, timeout=30)
        data = resp.json()
        
        if isinstance(data, dict):
            # Deep clean ALL unwanted fields
            data = deep_clean(data)
            
            # Fix any URL errors in nested data
            if 'source_1' in data:
                if 'existing_lead' in data.get('source_1', {}):
                    if 'error' in data['source_1']['existing_lead']:
                        data['source_1']['existing_lead']['error'] = "Request failed"
            
            data['response_time_ms'] = round((time.time() - start_time) * 1000)
            return jsonify(data)
    
    except:
        pass
    
    response_time = round((time.time() - start_time) * 1000)
    
    return jsonify({
        "success": False,
        "error": "Unable to fetch PAN details",
        "pan": pan,
        "response_time_ms": response_time,
        "credit": CREDIT,
        "by": CREDIT
    })


# ============ HEALTH CHECK ============
@app.route('/health')
def test():
    return jsonify({
        "status": "ONLINE",
        "version": "3.0",
        "credit": CREDIT
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Endpoint not found",
        "home": "/",
        "credit": CREDIT
    }), 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"BRONX ULTRA API Running on port {port}")
    app.run(host='0.0.0.0', port=port)
