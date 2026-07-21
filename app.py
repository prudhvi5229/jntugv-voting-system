import hashlib
import json
import time
from datetime import datetime, timedelta
import pytz
from io import BytesIO
import sqlite3
import re
import random
import numpy as np
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, jsonify, make_response, url_for, session, redirect

# PostgreSQL Driver Import
try:
    import psycopg2
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

# PDF Libraries
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = "BCET_BLOCKCHAIN_2026_SECURE_ULTRA_PRO_MAX_Z_PLUS_DEEPCORE_IMMUTABLE_HARSH"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# --- CONFIGURATION ---
IST = pytz.timezone('Asia/Kolkata')
ADMIN_SECRET = "BCET_ADMIN_PRO" 

SIGNUP_OTP_CACHE = {}  
FORGOT_OTP_CACHE = {}  

FAILED_ATTEMPTS = {} 
MAX_FAILED_ATTEMPTS = 5
RATE_LIMIT_TRACKER = {} 
RATE_LIMIT_WINDOW = 10 
MAX_REQUESTS_PER_WINDOW = 20 
SYSTEM_FORENSIC_LOCKOUT = False 

DATABASE_URL = os.environ.get("DATABASE_URL", "")

def get_db_connection():
    if DATABASE_URL and HAS_POSTGRES:
        url = DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        conn = psycopg2.connect(url)
        conn.autocommit = True  # 🔥 INSTANT SAVE TO NEON DB
        return conn, "postgres"
    else:
        conn = sqlite3.connect('bcet_production.db')
        return conn, "sqlite"

def format_datetime_for_input(dt_str):
    if not dt_str:
        return datetime.now(IST).strftime("%Y-%m-%dT%H:%M")
    try:
        clean_str = str(dt_str).strip().replace(" ", "T")
        if len(clean_str) > 16:
            clean_str = clean_str[:16]
        return clean_str
    except Exception:
        return datetime.now(IST).strftime("%Y-%m-%dT%H:%M")

def init_db():
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        if db_type == "postgres":
            cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                              (student_id VARCHAR(100) PRIMARY KEY, email VARCHAR(255), password_hash TEXT)''')
                              
            cursor.execute('''CREATE TABLE IF NOT EXISTS android_biometrics 
                              (student_id VARCHAR(100) PRIMARY KEY, fingerprint_data TEXT, face_vector TEXT)''')
                              
            cursor.execute('''CREATE TABLE IF NOT EXISTS whitelist_registry 
                              (student_id VARCHAR(100) PRIMARY KEY, email VARCHAR(255))''')
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS system_settings 
                              (key VARCHAR(100) PRIMARY KEY, value TEXT)''')
            
            now_str = datetime.now(IST).strftime("%Y-%m-%dT%H:%M")
            future_str = (datetime.now(IST) + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M")
            
            cursor.execute("INSERT INTO system_settings VALUES ('start_time', %s) ON CONFLICT (key) DO NOTHING", (now_str,))
            cursor.execute("INSERT INTO system_settings VALUES ('end_time', %s) ON CONFLICT (key) DO NOTHING", (future_str,))
            cursor.execute("INSERT INTO system_settings VALUES ('is_active', '1') ON CONFLICT (key) DO NOTHING")
        else:
            cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                              (student_id TEXT PRIMARY KEY, email TEXT, password_hash TEXT)''')
                              
            cursor.execute('''CREATE TABLE IF NOT EXISTS android_biometrics 
                              (student_id TEXT PRIMARY KEY, fingerprint_data TEXT, face_vector TEXT)''')
                              
            cursor.execute('''CREATE TABLE IF NOT EXISTS whitelist_registry 
                              (student_id TEXT PRIMARY KEY, email TEXT)''')
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS system_settings 
                              (key TEXT PRIMARY KEY, value TEXT)''')
            
            now_str = datetime.now(IST).strftime("%Y-%m-%dT%H:%M")
            future_str = (datetime.now(IST) + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M")
            
            cursor.execute("INSERT OR IGNORE INTO system_settings VALUES ('start_time', ?)", (now_str,))
            cursor.execute("INSERT OR IGNORE INTO system_settings VALUES ('end_time', ?)", (future_str,))
            cursor.execute("INSERT OR IGNORE INTO system_settings VALUES ('is_active', '1')")
            conn.commit()
            
        conn.close()
    except Exception as e:
        print(f"Database Init Exception: {e}")

init_db()

ELECTION_SETTINGS = {
    "candidates": [
        {"name": "Ramu", "symbol": "", "manifesto": ""}, 
        {"name": "Laxman", "symbol": "", "manifesto": ""}
    ]
}

def mask_email(email_str):
    try:
        parts = email_str.split('@')
        name = parts[0]
        domain = parts[1]
        masked_name = name + "**" if len(name) <= 2 else name[:2] + "**" + name[-1]
        return f"{masked_name}@{domain}"
    except Exception:
        return "your registered email"

# --- TRI-NODE CRYPTOGRAPHIC BLOCKCHAIN ENGINE ---
class CryptographicNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.chain = []
        self.create_block(proof=100, previous_hash='1')

    def create_block(self, proof, previous_hash, votes=[]):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S"),
            'votes': list(votes),
            'proof': proof,
            'previous_hash': previous_hash,
        }
        self.chain.append(block)
        return block

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_node_valid(self):
        for i in range(1, len(self.chain)):
            if self.chain[i]['previous_hash'] != self.hash(self.chain[i-1]):
                return False
        return True

class MultiNodeConsensusEngine:
    def __init__(self):
        self.reset_engine()

    def reset_engine(self):
        self.nodes = {
            "Node_A": CryptographicNode("Node_A"),
            "Node_B": CryptographicNode("Node_B"),
            "Node_C": CryptographicNode("Node_C")
        }
        self.nullifiers = set()
        self.security_logs = []
        self.global_voter_count = 0 

    def log_intrusion(self, user_id, reason, ip):
        self.security_logs.append({
            "id": user_id,
            "time": datetime.now(IST).strftime("%H:%M:%S"),
            "reason": reason,
            "ip": ip
        })

    def broadcast_transaction(self, vote_data):
        self.global_voter_count += 1
        for node_name, node_obj in self.nodes.items():
            last_block = node_obj.chain[-1]
            prev_hash = node_obj.hash(last_block)
            node_obj.create_block(proof=123, previous_hash=prev_hash, votes=[vote_data])

    def verify_consensus_and_tally(self, candidate_name):
        global SYSTEM_FORENSIC_LOCKOUT
        if SYSTEM_FORENSIC_LOCKOUT:
            return -999

        tally_map = {"Node_A": 0, "Node_B": 0, "Node_C": 0}
        target_ballot_hash = hashlib.sha256(f"{candidate_name}_BCET_BALLOT_SALT".encode()).hexdigest()

        for name, node in self.nodes.items():
            if node.is_node_valid():
                for block in node.chain:
                    for v in block['votes']:
                        if v['ballot_hash'] == target_ballot_hash:
                            tally_map[name] += 1
            else:
                SYSTEM_FORENSIC_LOCKOUT = True
                return -999

        votes_list = list(tally_map.values())
        majority_vote = max(set(votes_list), key=votes_list.count)
        
        if votes_list.count(majority_vote) < 2 or len(self.nullifiers) != self.global_voter_count:
            SYSTEM_FORENSIC_LOCKOUT = True
            return -999
            
        return majority_vote

consensus_blockchain = MultiNodeConsensusEngine()

def get_client_ip():
    raw_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    return raw_ip.split(',')[0].strip() if raw_ip and ',' in raw_ip else request.remote_addr

def sanitize_input(text):
    if not text: return ""
    return re.sub(r"[<>\'\"\\;=\\-]", "", str(text)).strip()

def verify_fingerprint_match(saved_fingerprint, live_fingerprint):
    if not saved_fingerprint or not live_fingerprint:
        return False
    return saved_fingerprint.strip() == live_fingerprint.strip()

def verify_face_match(saved_face_str, live_face_vector):
    try:
        if not saved_face_str or not live_face_vector:
            return False
        saved_vector = np.array(json.loads(saved_face_str))
        current_vector = np.array(live_face_vector)
        distance = np.linalg.norm(saved_vector - current_vector)
        return float(distance) < 0.6
    except Exception:
        return False

@app.before_request
def intercept_rate_limits():
    global SYSTEM_FORENSIC_LOCKOUT
    if SYSTEM_FORENSIC_LOCKOUT and not request.path.startswith('/admin-results') and not request.path.startswith('/admin/') and not request.path.startswith('/api/'):
        return "<h1>503 Service Unavailable: Cryptographic Forensic Lockout Active.</h1>", 503

    client_ip = get_client_ip()
    current_time = time.time()
    if client_ip not in RATE_LIMIT_TRACKER:
        RATE_LIMIT_TRACKER[client_ip] = []
    RATE_LIMIT_TRACKER[client_ip] = [t for t in RATE_LIMIT_TRACKER[client_ip] if current_time - t < RATE_LIMIT_WINDOW]
    if len(RATE_LIMIT_TRACKER[client_ip]) >= MAX_REQUESTS_PER_WINDOW:
        consensus_blockchain.log_intrusion("ANTI_DDOS_GATE", "Rate Limit Violation Blocked", client_ip)
        return "<h1>429 Too Many Requests.</h1>", 429
    RATE_LIMIT_TRACKER[client_ip].append(current_time)

# --- ANDROID APP INTEGRATION ENDPOINTS ---

@app.route('/api/admin/upload_biometrics', methods=['POST'], strict_slashes=False)
def api_admin_upload_biometrics():
    secret = request.headers.get('Admin-Secret', '')
    if secret != ADMIN_SECRET:
        return jsonify({"status": "error", "message": "Unauthorized Admin Request."}), 403
    data = request.json
    student_id = sanitize_input(data.get('student_id', '')).upper()
    fingerprint_raw = data.get('fingerprint_data', None)
    face_vector_raw = data.get('face_vector', None)
    
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    if db_type == "postgres":
        cursor.execute("SELECT student_id FROM whitelist_registry WHERE student_id=%s", (student_id,))
    else:
        cursor.execute("SELECT student_id FROM whitelist_registry WHERE student_id=?", (student_id,))
    whitelisted = cursor.fetchone()
    
    if not whitelisted:
        conn.close()
        return jsonify({"status": "error", "message": "ID not in whitelist database!"}), 400
        
    face_vector_str = json.dumps(face_vector_raw) if face_vector_raw else None
    try:
        if db_type == "postgres":
            cursor.execute("INSERT INTO android_biometrics VALUES (%s, %s, %s) ON CONFLICT (student_id) DO UPDATE SET fingerprint_data=EXCLUDED.fingerprint_data, face_vector=EXCLUDED.face_vector", (student_id, fingerprint_raw, face_vector_str))
        else:
            cursor.execute("INSERT OR REPLACE INTO android_biometrics VALUES (?, ?, ?)", (student_id, fingerprint_raw, face_vector_str))
            conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Biometrics mapped successfully!"})
    except Exception as e:
        conn.close()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/biometric_login', methods=['POST'], strict_slashes=False)
def api_biometric_login():
    data = request.json
    student_id = sanitize_input(data.get('student_id', '')).upper()
    live_fingerprint = data.get('live_fingerprint', None)
    live_face_vector = data.get('live_face_vector', None)
    client_ip = get_client_ip()

    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    if db_type == "postgres":
        cursor.execute("SELECT student_id FROM whitelist_registry WHERE student_id=%s", (student_id,))
    else:
        cursor.execute("SELECT student_id FROM whitelist_registry WHERE student_id=?", (student_id,))
    whitelisted = cursor.fetchone()

    if not whitelisted:
        conn.close()
        consensus_blockchain.log_intrusion(student_id, "Non-Whitelist ID Attempt", client_ip)
        return jsonify({"status": "error", "message": "FAILED: Student ID is not authorized!"}), 401

    if db_type == "postgres":
        cursor.execute("SELECT fingerprint_data, face_vector FROM android_biometrics WHERE student_id=%s", (student_id,))
    else:
        cursor.execute("SELECT fingerprint_data, face_vector FROM android_biometrics WHERE student_id=?", (student_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"status": "error", "message": "FAILED: Biometrics not registered yet!"}), 404

    saved_fingerprint, saved_face_str = row[0], row[1]
    fingerprint_match = verify_fingerprint_match(saved_fingerprint, live_fingerprint)
    face_match = verify_face_match(saved_face_str, live_face_vector)

    if fingerprint_match or face_match:
        raw_token = f"{student_id}{time.time()}{app.secret_key}"
        blockchain_token = hashlib.sha256(raw_token.encode()).hexdigest().upper()[:12]
        
        session['active_voter'] = student_id
        session['vote_token'] = blockchain_token
        session['app_verified'] = False
        
        return jsonify({
            "status": "success",
            "message": "Biometric verification successful!",
            "blockchain_token": blockchain_token
        })
    else:
        consensus_blockchain.log_intrusion(student_id, "Biometric Failed (Both Failed)", client_ip)
        return jsonify({"status": "error", "message": "FAILED: Biometric mismatch!"}), 403

@app.route('/api/verify_app_token', methods=['POST'], strict_slashes=False)
def api_verify_app_token():
    data = request.json
    student_id = sanitize_input(data.get('student_id', '')).upper()
    user_input_token = sanitize_input(data.get('input_token', '')).upper()

    actual_token = session.get('vote_token')
    active_voter = session.get('active_voter')

    if active_voter == student_id and user_input_token == actual_token:
        session['app_verified'] = True
        session['user_id'] = student_id
        session['user_ip'] = get_client_ip()
        session['token_verified'] = True 
        
        return jsonify({
            "status": "success",
            "message": "Token matched successfully! Session authorized.",
            "redirect_url": url_for('index', _external=True)
        })
    else:
        consensus_blockchain.log_intrusion(student_id, "App Token Mismatch", get_client_ip())
        return jsonify({"status": "error", "message": "FAILED: Token mismatch configuration!"}), 403

# --- WEB PORTAL ROUTES ---

@app.route('/welcome', strict_slashes=False)
def welcome():
    if 'user_id' in session and session.get('token_verified'):
        return redirect(url_for('index'))
    return render_template('welcome.html')

@app.route('/login_page', strict_slashes=False)
def login_page():
    return render_template('login.html')

@app.route('/', strict_slashes=False)
def index():
    if 'user_id' not in session:
        return redirect(url_for('welcome'))
    
    if session.get('user_ip') != get_client_ip():
        consensus_blockchain.log_intrusion(session.get('user_id'), "Session Hijack Blocked (IP Alteration)", get_client_ip())
        session.clear()
        return redirect(url_for('welcome'))

    if not session.get('token_verified'):
        return redirect(url_for('auth_token_display'))

    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM system_settings WHERE key='start_time'")
    db_start_row = cursor.fetchone()
    cursor.execute("SELECT value FROM system_settings WHERE key='end_time'")
    db_end_row = cursor.fetchone()
    cursor.execute("SELECT value FROM system_settings WHERE key='is_active'")
    db_active_row = cursor.fetchone()

    db_start = db_start_row[0] if db_start_row else datetime.now(IST).strftime("%Y-%m-%dT%H:%M")
    db_end = db_end_row[0] if db_end_row else (datetime.now(IST) + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M")
    db_active = (db_active_row[0] == '1') if db_active_row else True
    conn.close()

    current_settings = {
        "candidates": ELECTION_SETTINGS["candidates"],
        "start_time": db_start,
        "end_time": db_end,
        "is_active": db_active
    }

    now = datetime.now(IST)
    
    def parse_election_time(time_str):
        try:
            clean_str = str(time_str).replace("T", " ")
            return datetime.strptime(clean_str, "%Y-%m-%d %H:%M").replace(tzinfo=IST)
        except Exception:
            return None

    start = parse_election_time(db_start)
    end = parse_election_time(db_end)
    
    status = "OPEN"
    if not db_active:
        status = "CLOSED"
    elif start and now < start:
        status = "NOT_STARTED"
    elif end and now > end:
        status = "CLOSED"
    
    return render_template('index.html', 
                           candidate_list=ELECTION_SETTINGS["candidates"], 
                           settings=current_settings,
                           election_status=status)

@app.route('/auth_token_display', strict_slashes=False)
def auth_token_display():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    sid = session['user_id']
    raw_data = f"{sid}{time.time()}{app.secret_key}"
    blockchain_token = hashlib.sha256(raw_data.encode()).hexdigest().upper()[:12]
    
    session['binding_signature'] = hashlib.sha256(f"{sid}{get_client_ip()}{blockchain_token}".encode()).hexdigest()
    session['generated_token'] = blockchain_token
    session['token_verified'] = False 
    return render_template('auth_token_display.html', token=blockchain_token)

@app.route('/verify_token_page', strict_slashes=False)
def verify_token_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('token_verification_input.html')

@app.route('/verify_token', methods=['POST'], strict_slashes=False)
def verify_token():
    user_input = sanitize_input(request.form.get('input_token', '')).upper()
    actual_token = session.get('generated_token')

    if user_input and user_input == actual_token:
        session['token_verified'] = True
        return redirect(url_for('index'))
    else:
        consensus_blockchain.log_intrusion(session.get('user_id'), "Token Guard Exception Triggered", get_client_ip())
        return render_template('token_verification_input.html', error="Invalid Token!")

@app.route('/signup_page', strict_slashes=False)
def signup_page():
    return render_template('signup.html')

@app.route('/send_signup_otp', methods=['POST'], strict_slashes=False)
def send_signup_otp():
    student_id = sanitize_input(request.form.get('student_id', '')).upper()
    password = request.form.get('password', '').strip()

    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    if db_type == "postgres":
        cursor.execute("SELECT email FROM whitelist_registry WHERE student_id=%s", (student_id,))
    else:
        cursor.execute("SELECT email FROM whitelist_registry WHERE student_id=?", (student_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        consensus_blockchain.log_intrusion(student_id, "Non-Whitelisted Database Intrusion Attempt", get_client_ip())
        return jsonify({"status": "error", "message": "ID not authorized by BCET Database Registry!"})
    
    registered_email = row[0]

    if db_type == "postgres":
        cursor.execute("SELECT student_id FROM users WHERE student_id=%s", (student_id,))
    else:
        cursor.execute("SELECT student_id FROM users WHERE student_id=?", (student_id,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"status": "error", "message": "Already registered! Log in directly."})
    conn.close()

    random_dynamic_otp = str(random.randint(100000, 999999))

    SIGNUP_OTP_CACHE[student_id] = {
        "otp": random_dynamic_otp, 
        "email": registered_email, 
        "password_hash": generate_password_hash(password),
        "expires": time.time() + 300
    }
    
    return jsonify({
        "status": "success", 
        "message": f"🔑 YOUR OTP CODE IS: [{random_dynamic_otp}]"
    })

@app.route('/verify_signup_otp', methods=['POST'], strict_slashes=False)
def verify_signup_otp():
    student_id = sanitize_input(request.form.get('student_id', '')).upper()
    user_otp = sanitize_input(request.form.get('otp', '')).strip()

    cache = SIGNUP_OTP_CACHE.get(student_id)
    if not cache:
        return jsonify({"status": "error", "message": "Session expired or ID not found. Click Send OTP again!"})

    if cache["otp"] == user_otp:
        try:
            conn, db_type = get_db_connection()
            cursor = conn.cursor()
            
            if db_type == "postgres":
                cursor.execute("DELETE FROM users WHERE student_id=%s", (student_id,))
                cursor.execute("INSERT INTO users (student_id, email, password_hash) VALUES (%s, %s, %s)", 
                               (student_id, cache["email"], cache["password_hash"]))
            else:
                cursor.execute("DELETE FROM users WHERE student_id=?", (student_id,))
                cursor.execute("INSERT INTO users (student_id, email, password_hash) VALUES (?, ?, ?)", 
                               (student_id, cache["email"], cache["password_hash"]))
                conn.commit()
            conn.close()
            
            SIGNUP_OTP_CACHE.pop(student_id, None)
            return jsonify({"status": "success", "message": "Account created successfully! Log in now."})
        except Exception as e:
            return jsonify({"status": "error", "message": f"Database Error: {str(e)}"})
    else:
        consensus_blockchain.log_intrusion(student_id, "Incorrect OTP Entry", get_client_ip())
        return jsonify({"status": "error", "message": "Incorrect OTP Verification Code!"})

@app.route('/login', methods=['POST'], strict_slashes=False)
def login():
    student_id = sanitize_input(request.form.get('student_id', '')).upper()
    password = request.form.get('password', '').strip()
    client_ip = get_client_ip()

    if FAILED_ATTEMPTS.get(client_ip, 0) >= MAX_FAILED_ATTEMPTS:
        consensus_blockchain.log_intrusion(student_id, "Brute Force Threshold Breached", client_ip)
        return "<h1>IP blocked temporarily due to excessive failures.</h1>", 423

    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    if db_type == "postgres":
        cursor.execute("SELECT password_hash FROM users WHERE student_id=%s", (student_id,))
    else:
        cursor.execute("SELECT password_hash FROM users WHERE student_id=?", (student_id,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[0], password):
        FAILED_ATTEMPTS[client_ip] = 0 
        session.permanent = True
        session['user_id'] = student_id
        session['user_ip'] = client_ip 
        session['token_verified'] = False
        return redirect(url_for('auth_token_display'))
    
    FAILED_ATTEMPTS[client_ip] = FAILED_ATTEMPTS.get(client_ip, 0) + 1
    consensus_blockchain.log_intrusion(student_id, f"Failed Node Authentication ({FAILED_ATTEMPTS[client_ip]}/{MAX_FAILED_ATTEMPTS})", client_ip)
    return render_template('login_error.html')

@app.route('/forgot_password_page', strict_slashes=False)
def forgot_password_page():
    return render_template('forgot_password.html')

@app.route('/send_forgot_otp', methods=['POST'], strict_slashes=False)
def send_forgot_otp():
    student_id = sanitize_input(request.form.get('student_id', '')).upper()
    email = sanitize_input(request.form.get('email', '')).lower()
    
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    if db_type == "postgres":
        cursor.execute("SELECT email FROM users WHERE student_id=%s", (student_id,))
    else:
        cursor.execute("SELECT email FROM users WHERE student_id=?", (student_id,))
    user = cursor.fetchone()
    conn.close()

    if not user or user[0] != email:
        return jsonify({"status": "error", "message": "Credentials mismatch mapping!"})
    
    random_dynamic_otp = str(random.randint(100000, 999999))
    FORGOT_OTP_CACHE[student_id] = {"otp": random_dynamic_otp, "expires": time.time() + 300, "verified": False}
    return jsonify({"status": "success", "message": f"🔑 YOUR OTP CODE IS: [{random_dynamic_otp}]"})

@app.route('/verify_forgot_code', methods=['POST'], strict_slashes=False)
def verify_forgot_code():
    student_id = sanitize_input(request.form.get('student_id', '')).upper()
    user_otp = sanitize_input(request.form.get('otp', '')).strip()
    cache = FORGOT_OTP_CACHE.get(student_id)
    if not cache or time.time() > cache["expires"]:
        return jsonify({"status": "error", "message": "Token window session expired!"})
    if cache["otp"] == user_otp:
        FORGOT_OTP_CACHE[student_id]["verified"] = True
        return jsonify({"status": "success", "message": "Security shield cleared!"})
    return jsonify({"status": "error", "message": "Invalid security authentication code sequence."})

@app.route('/commit_new_password', methods=['POST'], strict_slashes=False)
def commit_new_password():
    student_id = sanitize_input(request.form.get('student_id', '')).upper()
    new_password = request.form.get('password', '').strip()
    cache = FORGOT_OTP_CACHE.get(student_id)
    if not cache or not cache.get("verified"):
        return jsonify({"status": "error", "message": "State access architecture violation blocked!"})
    
    hashed = generate_password_hash(new_password)
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    if db_type == "postgres":
        cursor.execute("UPDATE users SET password_hash=%s WHERE student_id=%s", (hashed, student_id))
    else:
        cursor.execute("UPDATE users SET password_hash=? WHERE student_id=?", (hashed, student_id))
        conn.commit()
    conn.close()
    FORGOT_OTP_CACHE.pop(student_id, None)
    return jsonify({"status": "success", "message": "Secret password allocation overridden successfully!"})

@app.route('/logout', strict_slashes=False)
def logout():
    session.clear() 
    return redirect(url_for('welcome'))

@app.route('/cast_vote', methods=['POST'], strict_slashes=False)
def cast_vote():
    if 'user_id' not in session or not session.get('token_verified'):
        return redirect(url_for('welcome'))
    
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM system_settings WHERE key='is_active'")
    db_active = cursor.fetchone()[0] == '1'
    conn.close()
    
    if not db_active:
        return "<h1>Election Closed</h1>"
    
    student_id = session['user_id']
    candidate = sanitize_input(request.form.get('candidate'))
    user_ip = get_client_ip()

    nullifier = hashlib.sha256(f"{student_id}BCET_SALT_2026".encode()).hexdigest()
    if nullifier in consensus_blockchain.nullifiers:
        consensus_blockchain.log_intrusion(student_id, "Double Broadcast Packet Intercepted", user_ip)
        session.clear() 
        return render_template('already_cast.html')

    time.sleep(1.5)
    consensus_blockchain.nullifiers.add(nullifier)
    receipt_id = hashlib.sha256(str(time.time()).encode()).hexdigest().upper()[:12]
    
    secured_ballot_hash = hashlib.sha256(f"{candidate}_BCET_BALLOT_SALT".encode()).hexdigest()
    vote_packet = {'ballot_hash': secured_ballot_hash, 'receipt': receipt_id}
    consensus_blockchain.broadcast_transaction(vote_packet)
    
    session.clear() 
    return render_template('success.html', candidate=candidate, receipt=receipt_id, timestamp=datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/audit', methods=['GET', 'POST'], strict_slashes=False)
def audit_portal():
    searched_id = sanitize_input(request.form.get('receipt', '')).upper()
    result = None
    if request.method == 'POST':
        for block in consensus_blockchain.nodes["Node_A"].chain:
            for vote in block['votes']:
                if vote.get('receipt') == searched_id:
                    matched_candidate = "Unknown / Encrypted"
                    for c in ELECTION_SETTINGS["candidates"]:
                        check_hash = hashlib.sha256(f"{c['name']}_BCET_BALLOT_SALT".encode()).hexdigest()
                        if vote['ballot_hash'] == check_hash:
                            matched_candidate = c['name']
                            break
                    result = {"candidate": matched_candidate, "timestamp": block['timestamp'], "block_index": block['index']}
                    break
            if result: break
    return render_template('audit.html', searched_id=searched_id, result=result)

# --- DYNAMIC ADMIN PANEL ROUTES ---

@app.route('/admin-results', methods=['GET'], strict_slashes=False)
@app.route('/admin-results/<path:secret>', methods=['GET'], strict_slashes=False)
@app.route('/admin/results', methods=['GET'], strict_slashes=False)
@app.route('/admin/results/<path:secret>', methods=['GET'], strict_slashes=False)
def admin_results(secret=None):
    global SYSTEM_FORENSIC_LOCKOUT
    vote_counts = {}
    for c in ELECTION_SETTINGS["candidates"]:
        tally = consensus_blockchain.verify_consensus_and_tally(c['name'])
        vote_counts[c['name']] = "🔴 LOCKOUT ACTIVE" if tally == -999 else tally

    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM system_settings WHERE key='start_time'")
    r_start = cursor.fetchone()
    cursor.execute("SELECT value FROM system_settings WHERE key='end_time'")
    r_end = cursor.fetchone()
    cursor.execute("SELECT value FROM system_settings WHERE key='is_active'")
    r_active = cursor.fetchone()
    conn.close()

    raw_start = r_start[0] if r_start else ""
    raw_end = r_end[0] if r_end else ""

    current_settings = {
        "candidates": ELECTION_SETTINGS["candidates"],
        "start_time": format_datetime_for_input(raw_start),
        "end_time": format_datetime_for_input(raw_end),
        "is_active": (r_active[0] == '1') if r_active else True
    }

    return render_template('results.html', settings=current_settings, vote_counts=vote_counts, logs=consensus_blockchain.security_logs, secret=ADMIN_SECRET, secret_key=ADMIN_SECRET)

@app.route('/admin/voter-registry', methods=['GET'], strict_slashes=False)
@app.route('/admin/voter-registry/<path:secret>', methods=['GET'], strict_slashes=False)
def dynamic_voter_registry_view(secret=None):
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, email FROM whitelist_registry")
    rows = cursor.fetchall()
    conn.close()
    student_list = [{"id": r[0], "email": r[1]} for r in rows]
    return render_template('voter_registry.html', students=student_list, secret=ADMIN_SECRET, secret_key=ADMIN_SECRET)

@app.route('/admin/add_student_live', methods=['POST'], strict_slashes=False)
@app.route('/admin/add_student_live/<path:secret>', methods=['POST'], strict_slashes=False)
def add_student_live(secret=None):
    new_id = sanitize_input(request.form.get('student_id', '')).upper()
    new_email = sanitize_input(request.form.get('email', '')).lower()
    if new_id and new_email:
        try:
            conn, db_type = get_db_connection()
            cursor = conn.cursor()
            if db_type == "postgres":
                cursor.execute("INSERT INTO whitelist_registry VALUES (%s, %s) ON CONFLICT (student_id) DO UPDATE SET email = EXCLUDED.email", (new_id, new_email))
            else:
                cursor.execute("INSERT OR REPLACE INTO whitelist_registry VALUES (?, ?)", (new_id, new_email))
                conn.commit()
            conn.close()
            return jsonify({"status": "success", "message": f"Student [{new_id}] mapped permanently!"})
        except Exception as e:
            return jsonify({"status": "error", "message": f"Database Error: {str(e)}"})
    return jsonify({"status": "error", "message": "Invalid Hall Ticket or Email format!"})

@app.route('/admin/delete_student_live', methods=['POST'], strict_slashes=False)
@app.route('/admin/delete_student_live/<path:secret>', methods=['POST'], strict_slashes=False)
def delete_student_live(secret=None):
    target_id = sanitize_input(request.form.get('student_id', '')).upper()
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    if db_type == "postgres":
        cursor.execute("SELECT student_id FROM whitelist_registry WHERE student_id=%s", (target_id,))
        exists = cursor.fetchone()
        if exists:
            cursor.execute("DELETE FROM whitelist_registry WHERE student_id=%s", (target_id,))
            cursor.execute("DELETE FROM users WHERE student_id=%s", (target_id,))
            conn.close()
            return jsonify({"status": "success", "message": f"Student [{target_id}] scrubbed permanently."})
    else:
        cursor.execute("SELECT student_id FROM whitelist_registry WHERE student_id=?", (target_id,))
        exists = cursor.fetchone()
        if exists:
            cursor.execute("DELETE FROM whitelist_registry WHERE student_id=?", (target_id,))
            cursor.execute("DELETE FROM users WHERE student_id=?", (target_id,))
            conn.commit()
            conn.close()
            return jsonify({"status": "success", "message": f"Student [{target_id}] scrubbed permanently."})
    conn.close()
    return jsonify({"status": "error", "message": "Student ID not found!"})

@app.route('/admin/factory-reset', methods=['GET'], strict_slashes=False)
@app.route('/admin/factory-reset/<path:secret>', methods=['GET'], strict_slashes=False)
def dynamic_factory_reset_view(secret=None):
    return render_template('factory_reset.html', secret=ADMIN_SECRET, secret_key=ADMIN_SECRET)

@app.route('/admin/execute_node_flush', methods=['POST'], strict_slashes=False)
def execute_node_flush():
    target_id = sanitize_input(request.form.get('student_id', '')).upper()
    if not target_id:
        return jsonify({"status": "error", "message": "Empty tracker reference."})
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    if db_type == "postgres":
        cursor.execute("DELETE FROM users WHERE student_id=%s", (target_id,))
        cursor.execute("DELETE FROM android_biometrics WHERE student_id=%s", (target_id,))
    else:
        cursor.execute("DELETE FROM users WHERE student_id=?", (target_id,))
        cursor.execute("DELETE FROM android_biometrics WHERE student_id=?", (target_id,))
        conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": f"Database scrubbed for Student [{target_id}]."})

@app.route('/admin/security-audit', methods=['GET'], strict_slashes=False)
@app.route('/admin/security-audit/<path:secret>', methods=['GET'], strict_slashes=False)
def dynamic_security_audit_view(secret=None):
    return render_template('security_audit.html', secret=ADMIN_SECRET, secret_key=ADMIN_SECRET, logs=consensus_blockchain.security_logs)

@app.route('/sync_candidates', methods=['POST'], strict_slashes=False)
def sync_candidates():
    incoming_data = request.json
    updated_candidates = []
    for c in incoming_data.get('candidates', []):
        updated_candidates.append({"name": sanitize_input(c.get('name')), "symbol": c.get('symbol', ''), "manifesto": c.get('manifesto', '')})
    ELECTION_SETTINGS["candidates"] = updated_candidates
    return jsonify({"status": "success", "message": "Synced Successfully!"})

@app.route('/update_timing', methods=['POST'], strict_slashes=False)
def update_timing():
    data = request.json
    start_val = sanitize_input(data.get('start', ''))
    end_val = sanitize_input(data.get('end', ''))
    
    formatted_start = format_datetime_for_input(start_val)
    formatted_end = format_datetime_for_input(end_val)
    
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    if db_type == "postgres":
        cursor.execute("INSERT INTO system_settings VALUES ('start_time', %s) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value", (formatted_start,))
        cursor.execute("INSERT INTO system_settings VALUES ('end_time', %s) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value", (formatted_end,))
        cursor.execute("INSERT INTO system_settings VALUES ('is_active', '1') ON CONFLICT (key) DO UPDATE SET value = '1'")
    else:
        cursor.execute("INSERT OR REPLACE INTO system_settings VALUES ('start_time', ?)", (formatted_start,))
        cursor.execute("INSERT OR REPLACE INTO system_settings VALUES ('end_time', ?)", (formatted_end,))
        cursor.execute("INSERT OR REPLACE INTO system_settings VALUES ('is_active', '1')")
        conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/stop_election', methods=['POST'], strict_slashes=False)
def stop_election():
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    if db_type == "postgres":
        cursor.execute("INSERT INTO system_settings VALUES ('is_active', '0') ON CONFLICT (key) DO UPDATE SET value = '0'")
    else:
        cursor.execute("INSERT OR REPLACE INTO system_settings VALUES ('is_active', '0')")
        conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/reset_election', methods=['POST'], strict_slashes=False)
def reset_election():
    global SYSTEM_FORENSIC_LOCKOUT
    SYSTEM_FORENSIC_LOCKOUT = False
    consensus_blockchain.reset_engine()
    return jsonify({"status": "success"})

@app.route('/download-results', methods=['GET'], strict_slashes=False)
@app.route('/download-results/<path:secret>', methods=['GET'], strict_slashes=False)
def download_results(secret=None):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFillColor(colors.HexColor("#0f172a"))
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, 750, "BCET ELECTION MANAGEMENT SYSTEMS NODE")
    p.setFont("Helvetica", 10)
    p.setFillColor(colors.HexColor("#64748b"))
    p.drawString(50, 735, f"Report Compilation Ledger Timestamp: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')} IST")
    p.setStrokeColor(colors.HexColor("#cbd5e1"))
    p.line(50, 720, 550, 720)
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(colors.HexColor("#1e293b"))
    p.drawString(50, 680, "Consensus Verification Tally Summary Matrix:")
    y = 650
    for c in ELECTION_SETTINGS["candidates"]:
        tally = consensus_blockchain.verify_consensus_and_tally(c['name'])
        display_tally = "CRYPTOGRAPHIC LOCKOUT" if tally == -999 else str(tally)
        p.setFont("Helvetica", 12)
        p.drawString(60, y, f"Candidate Handle: {c['name']}")
        p.drawString(350, y, f"Verified Ballot Units: {display_tally}")
        y -= 25
    p.line(50, y, 550, y)
    y -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Total System Ballot Mappings Log Count Check: {len(consensus_blockchain.nullifiers)}")
    p.showPage()
    p.save()
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=BCET_Node_Report_{datetime.now(IST).strftime("%Y%m%d")}.pdf'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)