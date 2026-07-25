from flask import Flask, request, jsonify
import requests
import time
from datetime import datetime, timedelta
import os

app = Flask(__name__)

CREDIT = "@BRONX_ULTRA"
DEVELOPER = "@BRONX_ULTRA"

# ============ REAL API URLs ============
BOMBER_API = "https://ft-osint-api.duckdns.org/api/bomber"  # 👈 REAL BOMBER API
PAN_API = "https://ft-osint-api.duckdns.org/api/paninfo"

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

# ============ 🧹 DEEP CLEAN ============
def deep_clean(data):
    """Remove ALL unwanted fields"""
    if isinstance(data, dict):
        blacklist = [
            'by', 'owner', 'developer_name', 'created_by', 'author',
            'credit_to', 'thanks', 'ftgamer', '@ftgamer2', 'ft_osint',
            '_proxy', 'proxy', 'proxy_used', 'session_id',
            'pool_size', 'total_fetched', 'tested', 'note',
            'powered', 'powered_by', 'maintained_by', 'source_ip'
        ]
        
        for field in blacklist:
            data.pop(field, None)
        
        data['credit'] = CREDIT
        data['by'] = CREDIT
        data['developer'] = DEVELOPER
        
        for key in list(data.keys()):
            if isinstance(data[key], dict):
                data[key] = deep_clean(data[key])
            elif isinstance(data[key], list):
                data[key] = [deep_clean(item) if isinstance(item, dict) else item for item in data[key]]
    
    return data


def verify_key(key):
    """Key validation"""
    if not key:
        return {"valid": False, "error": "🔑 API Key required!"}
    
    if key not in KEYS_DB:
        return {"valid": False, "error": "❌ Invalid API Key!"}
    
    key_data = KEYS_DB[key]
    expiry_date = datetime.strptime(key_data['expiry'], '%Y-%m-%d')
    
    if datetime.now() > expiry_date:
        return {"valid": False, "error": "⏰ Key expired!"}
    
    if key_data['limit'] != "unlimited":
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in key_data['daily_usage']:
            key_data['daily_usage'][today] = 0
        
        if key_data['daily_usage'][today] >= key_data['limit']:
            return {"valid": False, "error": f"📊 Daily limit ({key_data['limit']}) reached!"}
        
        key_data['daily_usage'][today] += 1
    
    return {"valid": True, "type": key_data['type']}


@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


# ============ 🏠 HOME PAGE ============
@app.route('/')
def home():
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>BRONX ULTRA API</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#000a14;color:#d0d8f0;font-family:'Courier New',monospace;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px}}
.card{{background:rgba(5,15,35,.95);border:2px solid rgba(255,0,85,.2);border-radius:20px;padding:30px;max-width:650px;width:100%;text-align:center}}
h1{{font-size:24px;background:linear-gradient(90deg,#ff0055,#ff8800);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:15px}}
.box{{background:rgba(0,0,0,.6);border:1px solid rgba(255,0,85,.1);border-radius:12px;padding:15px;margin:12px 0;text-align:left}}
code{{color:#ff8800;font-size:11px;display:block;margin:8px 0;background:rgba(0,0,0,.5);padding:10px;border-radius:8px;word-break:break-all}}
input{{width:100%;padding:12px;background:rgba(0,0,0,.7);border:1px solid rgba(255,0,85,.2);border-radius:8px;color:#fff;font-size:14px;outline:none;margin:6px 0}}
input:focus{{border-color:#ff0055;box-shadow:0 0 10px rgba(255,0,85,.2)}}
button{{width:100%;padding:14px;background:linear-gradient(135deg,#ff0055,#cc0044);color:#fff;border:none;border-radius:10px;font-weight:700;cursor:pointer;font-size:14px;margin:8px 0;transition:.3s}}
button:hover{{transform:scale(1.02);box-shadow:0 0 30px rgba(255,0,85,.4)}}
.btn-pan{{background:linear-gradient(135deg,#ff8800,#cc6600)}}
.result{{background:rgba(0,0,0,.7);border:1px solid rgba(255,136,0,.2);border-radius:10px;padding:15px;margin-top:15px;text-align:left;display:none;max-height:500px;overflow:auto}}
.result.show{{display:block}}
pre{{color:#ff8800;font-size:10px;white-space:pre-wrap}}
.loading{{color:#ffb400;animation:blink 1s infinite}}
@keyframes blink{{50%{{opacity:0.5}}}}
</style></head>
<body>
<div class="card">
<h1>🚀 BRONX ULTRA API</h1>
<p style="color:#888;font-size:11px;margin-bottom:15px">REAL BOMBER + PAN API</p>

<div class="box">
<p style="color:#ff0055;font-weight:700;margin-bottom:8px">🔑 API Key</p>
<input type="text" id="apiKey" placeholder="Enter your API key...">
</div>

<div class="box">
<p style="color:#ff8800;font-weight:700;margin-bottom:8px">📱 Mobile Number / PAN</p>
<input type="text" id="inputValue" placeholder="9876543210 or BNZPM2501F">
</div>

<div class="box" id="counterBox" style="display:none">
<p style="color:#ff0055;font-weight:700;margin-bottom:8px">🔢 Counter (SMS Count)</p>
<input type="number" id="counter" value="100" min="1" max="500">
</div>

<button onclick="callBomber()">💣 START BOMBER</button>
<button class="btn-pan" onclick="callPan()">🪪 CHECK PAN</button>

<div class="result" id="result">
<pre id="resultData"></pre>
</div>
<p style="color:#555;font-size:9px;margin-top:15px">{CREDIT} | REAL API BACKEND</p>
</div>

<script>
async function callBomber(){{
var k=document.getElementById('apiKey').value.trim();if(!k)return alert('API Key required!');
var n=document.getElementById('inputValue').value.trim();if(!n||n.length!=10||!n.match(/^\\d{{10}}$/))return alert('Valid 10 digit mobile number required!');
var c=document.getElementById('counter').value||'100';
var d=document.getElementById('result'),p=document.getElementById('resultData');
d.classList.add('show');p.className='loading';p.textContent='💣 Calling REAL bomber API... Bombing '+n+' with '+c+' SMS... Please wait...';
try{{
var r=await fetch('/ultra?key='+encodeURIComponent(k)+'&number='+n+'&counter='+c);
var j=await r.json();p.className='';p.style.color='#ff8800';p.textContent=JSON.stringify(j,null,2)
}}catch(e){{p.className='';p.style.color='#ff3366';p.textContent='Error: '+e.message}}
}}

async function callPan(){{
var k=document.getElementById('apiKey').value.trim();if(!k)return alert('API Key required!');
var n=document.getElementById('inputValue').value.trim();if(!n||n.length!=10)return alert('Valid 10 character PAN required!');
var d=document.getElementById('result'),p=document.getElementById('resultData');
d.classList.add('show');p.className='loading';p.textContent='🪪 Calling REAL PAN API... Please wait...';
try{{
var r=await fetch('/pan?key='+encodeURIComponent(k)+'&pan='+n.toUpperCase());
var j=await r.json();p.className='';p.style.color='#ff8800';p.textContent=JSON.stringify(j,null,2)
}}catch(e){{p.className='';p.style.color='#ff3366';p.textContent='Error: '+e.message}}
}}

document.getElementById('inputValue').addEventListener('input',function(){{
if(this.value.match(/^\\d+$/)) document.getElementById('counterBox').style.display='block';
else document.getElementById('counterBox').style.display='none';
}});
</script>
</body></html>'''


# ============ 💣 SMS BOMBER - REAL API ============
@app.route('/ultra')
def ultra_bomber():
    key = request.args.get('key', '').strip()
    
    key_check = verify_key(key)
    if not key_check['valid']:
        return jsonify({"success": False, "error": key_check['error'], "credit": CREDIT}), 401
    
    number = request.args.get('number', '').strip()
    counter = request.args.get('counter', '100').strip()
    
    if not number or not number.isdigit() or len(number) != 10:
        return jsonify({"success": False, "error": "Valid 10 digit number required!", "credit": CREDIT}), 400
    
    try:
        counter = max(1, min(int(counter), 500))
    except:
        counter = 100
    
    start_time = time.time()
    
    # 👇 REAL BOMBER API CALL
    real_url = f"{BOMBER_API}?key=bronx-ultra-king-ft-bro-op&number={number}&counter={counter}"
    
    try:
        response = requests.get(real_url, timeout=90)  # 90 sec for bomber
        data = response.json()
        
        if isinstance(data, dict):
            data = deep_clean(data)
            elapsed = round((time.time() - start_time) * 1000)
            data['response_time_ms'] = elapsed
            data['plan'] = key_check['type']
            return jsonify(data)
    
    except requests.exceptions.Timeout:
        return jsonify({
            "success": True,
            "number": number,
            "counter": counter,
            "status": "Bombing initiated (timeout but likely sent)",
            "response_time_ms": round((time.time() - start_time) * 1000),
            "credit": CREDIT
        })
    
    except:
        return jsonify({
            "success": True,
            "number": number,
            "counter": counter,
            "status": "Bombing initiated",
            "response_time_ms": round((time.time() - start_time) * 1000),
            "credit": CREDIT
        })


# ============ 🪪 PAN INFO - REAL API ============
@app.route('/pan')
def pan_info():
    key = request.args.get('key', '').strip()
    
    key_check = verify_key(key)
    if not key_check['valid']:
        return jsonify({"success": False, "error": key_check['error'], "credit": CREDIT}), 401
    
    pan = request.args.get('pan', '').strip().upper()
    
    if not pan or len(pan) != 10:
        return jsonify({"success": False, "error": "Valid 10 character PAN required!", "credit": CREDIT}), 400
    
    start_time = time.time()
    
    # 👇 REAL PAN API CALL
    real_url = f"{PAN_API}?key=bronx-ultra-king-ft-bro-op&pan={pan}"
    
    try:
        response = requests.get(real_url, timeout=60)
        data = response.json()
        
        if isinstance(data, dict):
            data = deep_clean(data)
            
            if 'source_1' in data:
                lead = data['source_1'].get('existing_lead', {})
                if 'error' in lead:
                    lead['error'] = "Request failed"
            
            elapsed = round((time.time() - start_time) * 1000)
            data['response_time_ms'] = elapsed
            data['plan'] = key_check['type']
            return jsonify(data)
    
    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "error": "API timeout! Try again.",
            "pan": pan,
            "credit": CREDIT
        }), 504
    
    except:
        return jsonify({
            "success": False,
            "error": "API call failed!",
            "pan": pan,
            "credit": CREDIT
        }), 500


# ============ 💚 HEALTH CHECK ============
@app.route('/health')
def health():
    return jsonify({
        "status": "✅ ONLINE",
        "version": "5.0",
        "bomber_api": "/api/bomber",
        "pan_api": "/api/paninfo",
        "credit": CREDIT
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found", "home": "/", "credit": CREDIT}), 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🔥 BRONX ULTRA API :{port}")
    app.run(host='0.0.0.0', port=port)
