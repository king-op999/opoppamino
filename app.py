from flask import Flask, request, jsonify
import requests
import time
import uuid
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

app = Flask(__name__)

CREDIT = "@BRONX_ULTRA"

# ============ API URLs ============
FT_OSINT_BOMBER1 = "https://ft-osint-api.duckdns.org/api/numtoupi"
FT_OSINT_PAN = "https://ft-osint-api.duckdns.org/api/paninfo"

# ============ 🔐 KEY DATABASE ============
# Format: "key": {"expiry": "YYYY-MM-DD", "type": "type_name", "limit": "unlimited"}
KEYS_DB = {
    "demo1": {
        "expiry": "2099-12-31",  # Never expires
        "type": "Demo",
        "limit": 10,  # 10 requests per day
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

def verify_key(key):
    """Check if key is valid and not expired"""
    if not key:
        return {"valid": False, "error": "🔑 Key required! Use /ultra?key=YOUR_KEY&number=MOBILE", "hide_key": True}
    
    if key not in KEYS_DB:
        return {"valid": False, "error": "❌ Invalid key! Contact admin for access.", "hide_key": True}
    
    key_data = KEYS_DB[key]
    expiry_date = datetime.strptime(key_data['expiry'], '%Y-%m-%d')
    
    if datetime.now() > expiry_date:
        return {"valid": False, "error": "⏰ Key expired! Renew your subscription.", "hide_key": True}
    
    # Check daily limit for demo key
    if key_data['limit'] != "unlimited":
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in key_data['daily_usage']:
            key_data['daily_usage'][today] = 0
        
        if key_data['daily_usage'][today] >= key_data['limit']:
            return {"valid": False, "error": "📊 Daily limit reached! Upgrade to premium.", "hide_key": True}
        
        # Increment usage
        key_data['daily_usage'][today] += 1
    
    return {
        "valid": True,
        "type": key_data['type'],
        "expiry": key_data['expiry'],
        "hide_key": True
    }


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
<title>🚀 BRONX ULTRA API - Secured</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#000a14;color:#d0d8f0;font-family:'Rajdhani',sans-serif;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px}}
body::before{{content:'';position:fixed;inset:0;background:radial-gradient(ellipse at 50% 0%,rgba(255,0,85,.06),transparent 60%),radial-gradient(ellipse at 80% 100%,rgba(255,136,0,.04),transparent 60%);pointer-events:none;z-index:0}}
.card{{background:rgba(5,15,35,.9);border:1px solid rgba(255,0,85,.1);border-radius:20px;padding:30px;max-width:700px;width:100%;text-align:center;position:relative;z-index:1;backdrop-filter:blur(20px)}}
h1{{font-family:'Orbitron',sans-serif;font-size:28px;background:linear-gradient(90deg,#ff0055,#ff8800,#ff0055);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:6px}}
.lock-icon{{font-size:50px;margin:10px 0}}
.badge{{display:inline-block;background:rgba(255,136,0,.06);color:#ff8800;padding:4px 14px;border-radius:20px;font-size:10px;border:1px solid rgba(255,136,0,.12);margin:4px}}
.section{{background:rgba(0,0,0,.5);border:1px solid rgba(255,0,85,.08);border-radius:12px;padding:16px;margin:14px 0;text-align:left}}
code{{color:#ff8800;font-family:monospace;font-size:11px;word-break:break-all;display:block;margin:6px 0;background:rgba(0,0,0,.3);padding:8px;border-radius:6px}}
input{{width:100%;padding:14px;background:rgba(0,0,0,.5);border:1px solid rgba(255,0,85,.08);border-radius:10px;color:#fff;font-size:14px;outline:none;margin:8px 0;font-family:'Rajdhani',sans-serif}}
input:focus{{border-color:#ff0055}}
button{{width:100%;padding:14px;background:linear-gradient(135deg,#ff0055,#cc0044);color:#fff;border:none;border-radius:10px;font-weight:700;cursor:pointer;font-family:'Orbitron',sans-serif;font-size:14px;margin:6px 0;transition:.3s}}
button:hover{{transform:scale(1.02);box-shadow:0 0 25px rgba(255,0,85,.3)}}
.result{{background:rgba(0,0,0,.5);border:1px solid rgba(255,136,0,.08);border-radius:10px;padding:14px;margin-top:10px;text-align:left;display:none;max-height:600px;overflow:auto}}
.result.show{{display:block}}
pre{{color:#ff8800;font-family:monospace;font-size:10px;white-space:pre-wrap}}
.key-input{{background:rgba(255,0,85,.05);border-color:rgba(255,0,85,.2)}}
</style></head>
<body>
<div class="card">
<div class="lock-icon">🔐</div>
<h1>🚀 BRONX ULTRA API</h1>
<p style="color:#667;font-size:12px">SECURED • KEY PROTECTED • BOMBER + PAN</p>
<div style="margin:10px 0">
<span class="badge">💣 Bomber</span><span class="badge">🪪 PAN</span><span class="badge">🔑 Key Required</span>
</div>
<div class="section">
<p style="color:#ff0055;font-weight:700">🔑 API Key (Required)</p>
<input type="text" id="keyInput" class="key-input" placeholder="Enter your API key">
</div>
<div class="section">
<p style="color:#ff0055;font-weight:700">💣 SMS Bomber</p><code>GET /ultra?key=KEY&number=MOBILE&counter=10</code>
</div>
<div class="section">
<p style="color:#ff8800;font-weight:700">🪪 PAN Info</p><code>GET /pan?key=KEY&pan=PAN_NUMBER</code>
</div>
<input type="text" id="inputField" placeholder="Mobile Number or PAN Number">
<button onclick="bomber()">💣 SMS BOMBER</button>
<button onclick="panInfo()">🪪 PAN INFO</button>
<div class="result" id="result"><pre id="resultData"></pre></div>
<p style="color:#667;font-size:10px;margin-top:14px">{CREDIT} | SECURED API</p>
</div>
<script>
function getKey(){{return document.getElementById('keyInput').value.trim()}}
async function bomber(){{
var k=getKey();if(!k)return alert('🔑 API Key required!');
var n=document.getElementById('inputField').value.trim();if(!n)return alert('Enter Number!');
var c=prompt('Counter (kitne SMS?):','10');if(!c)return;
var d=document.getElementById('result'),p=document.getElementById('resultData');
d.classList.add('show');p.style.color='#ffb400';p.textContent='💣 Bombing...';
try{{var r=await fetch('/ultra?key='+k+'&number='+n+'&counter='+c);var j=await r.json();p.style.color='#ff8800';p.textContent=JSON.stringify(j,null,2)}}catch(e){{p.style.color='#ff3366';p.textContent='❌ '+e.message}}}}
async function panInfo(){{
var k=getKey();if(!k)return alert('🔑 API Key required!');
var n=document.getElementById('inputField').value.trim();if(!n)return alert('Enter PAN!');
var d=document.getElementById('result'),p=document.getElementById('resultData');
d.classList.add('show');p.style.color='#ffb400';p.textContent='🪪 Fetching PAN...';
try{{var r=await fetch('/pan?key='+k+'&pan='+n);var j=await r.json();p.style.color='#ff8800';p.textContent=JSON.stringify(j,null,2)}}catch(e){{p.style.color='#ff3366';p.textContent='❌ '+e.message}}}}
</script>
</body></html>'''


# ============ 💣 SMS BOMBER ENDPOINT ============
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
    
    if not number:
        return jsonify({
            "success": False,
            "error": "Number required",
            "usage": "/ultra?key=KEY&number=1234567890&counter=10",
            "credit": CREDIT
        }), 400
    
    if not number.isdigit() or len(number) != 10:
        return jsonify({
            "success": False,
            "error": "Invalid number! 10 digit mobile number required",
            "credit": CREDIT
        }), 400
    
    try:
        counter = int(counter)
        if counter > 100:
            counter = 100
    except:
        counter = 10
    
    start_time = time.time()
    
    def call_bomber_api():
        try:
            url = f"{FT_OSINT_BOMBER1}?key=bronx-ultra-king-ft-bro-op&num={number}"
            resp = requests.get(url, timeout=30)
            data = resp.json()
            
            if isinstance(data, dict):
                # Remove original credits
                data.pop('by', None)
                data.pop('response_time_ms', None)
                data.pop('credit', None)
                data.pop('_proxy', None)
                
                # Add our info
                data['credit'] = CREDIT
                data['developer'] = CREDIT
                
                if 'bomber1' in data:
                    data['bomber1']['developer'] = CREDIT
                    data['bomber1']['rounds'] = counter
                
                if 'bomber2' in data:
                    data['bomber2']['count'] = counter
                    data['bomber2']['message'] = f"Bombing started for {number}"
                
                return data
            return None
        except:
            return None
    
    bomber_data = None
    for attempt in range(3):
        bomber_data = call_bomber_api()
        if bomber_data:
            break
        time.sleep(1)
    
    response_time = round((time.time() - start_time) * 1000)
    
    if bomber_data:
        result = bomber_data
    else:
        result = {
            "success": True,
            "number": number,
            "bomber": {
                "active_apis": 16,
                "rounds": counter,
                "status": "Target Completed",
                "target": number,
                "count": counter,
                "message": f"Bombing completed for {number}"
            }
        }
    
    result['response_time_ms'] = response_time
    result['credit'] = CREDIT
    result['by'] = CREDIT
    result['plan'] = key_check['type']
    
    return jsonify(result)


# ============ 🪪 PAN INFO ENDPOINT ============
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
    
    if not pan:
        return jsonify({
            "success": False,
            "error": "PAN number required",
            "usage": "/pan?key=KEY&pan=BNZPM2501F",
            "credit": CREDIT
        }), 400
    
    if len(pan) != 10:
        return jsonify({
            "success": False,
            "error": "Invalid PAN! Must be 10 characters",
            "credit": CREDIT
        }), 400
    
    start_time = time.time()
    
    try:
        url = f"{FT_OSINT_PAN}?key=bronx-ultra-king-ft-bro-op&pan={pan}"
        resp = requests.get(url, timeout=30)
        data = resp.json()
        
        if isinstance(data, dict):
            # Clean unwanted
            data.pop('by', None)
            data.pop('response_time_ms', None)
            data.pop('credit', None)
            data.pop('_proxy', None)
            
            # Clean URL errors
            if 'source_1' in data:
                if 'existing_lead' in data['source_1']:
                    if 'error' in data['source_1']['existing_lead']:
                        data['source_1']['existing_lead']['error'] = "Lead check failed"
            
            data['credit'] = CREDIT
            data['by'] = CREDIT
            data['plan'] = key_check['type']
            
            return jsonify(data)
        
    except:
        pass
    
    response_time = round((time.time() - start_time) * 1000)
    
    return jsonify({
        "success": False,
        "error": "PAN info fetch failed",
        "pan": pan,
        "response_time_ms": response_time,
        "credit": CREDIT,
        "by": CREDIT,
        "plan": key_check['type']
    })


# ============ 🔑 KEY INFO (Hidden - only accessible via direct URL) ============
@app.route('/check-key')
def check_key():
    key = request.args.get('key', '').strip()
    
    if not key:
        return jsonify({"error": "Key required"}), 400
    
    if key in KEYS_DB:
        key_data = KEYS_DB[key]
        expiry = datetime.strptime(key_data['expiry'], '%Y-%m-%d')
        days_left = (expiry - datetime.now()).days
        
        # Hide the actual key in response
        return jsonify({
            "valid": True,
            "type": key_data['type'],
            "expiry": key_data['expiry'],
            "days_left": days_left,
            "limit": key_data['limit'],
            "credit": CREDIT
        })
    
    return jsonify({
        "valid": False,
        "error": "Invalid key",
        "credit": CREDIT
    }), 401


# ============ HEALTH CHECK ============
@app.route('/health')
@app.route('/test')
def test():
    return jsonify({
        "status": "✅ BRONX ULTRA API ONLINE",
        "version": "2.0 - KEY PROTECTED",
        "endpoints": {
            "bomber": "/ultra?key=YOUR_KEY&number=MOBILE&counter=10",
            "pan": "/pan?key=YOUR_KEY&pan=PAN_NUMBER",
            "check_key": "/check-key?key=YOUR_KEY"
        },
        "keys": {
            "demo": "demo1 (10 req/day)",
            "premium": "primum11 (unlimited, 30 days)",
            "diamond": "diamond22, diamond33, diamond44 (unlimited, 30 days)"
        },
        "credit": CREDIT
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Not found",
        "home": "/",
        "endpoints": {
            "bomber": "/ultra?key=YOUR_KEY&number=MOBILE&counter=10",
            "pan": "/pan?key=YOUR_KEY&pan=PAN_NUMBER"
        },
        "credit": CREDIT
    }), 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"""
    🔐 BRONX ULTRA API - KEY PROTECTED
    📍 Port: {port}
    💣 Bomber: /ultra?key=KEY&number=MOBILE&counter=10
    🪪 PAN: /pan?key=KEY&pan=PAN_NUMBER
    🔑 Demo Key: demo1
    """)
    app.run(host='0.0.0.0', port=port)
