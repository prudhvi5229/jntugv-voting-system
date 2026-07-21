import hashlib
import json
import time
from datetime import datetime, timedelta
import pytz
from io import BytesIO
import sqlite3
import re
import random
import requests
import numpy as np
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, jsonify, make_response, url_for, session, redirect

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
SENDER_EMAIL = "beharacollegeofengineering@gmail.com"

# --- VOLATILE OTP & PASSCODE MEMORY MATRIX ---
SIGNUP_OTP_CACHE = {}  
FORGOT_OTP_CACHE = {}  
DIRECT_OTP_CACHE = {}

# --- ADVANCED SECURITY MEMORY MATRIX ---
FAILED_ATTEMPTS = {} 
MAX_FAILED_ATTEMPTS = 5
RATE_LIMIT_TRACKER = {} 
RATE_LIMIT_WINDOW = 10 
MAX_REQUESTS_PER_WINDOW = 20 
SYSTEM_FORENSIC_LOCKOUT = False 

def init_db():
    conn = sqlite3.connect('bcet_production.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (student_id TEXT PRIMARY KEY, email TEXT, password_hash TEXT)''')
                      
    cursor.execute('''CREATE TABLE IF NOT EXISTS android_biometrics 
                      (student_id TEXT PRIMARY KEY, fingerprint_data TEXT, face_vector TEXT)''')
                      
    cursor.execute('''CREATE TABLE IF NOT EXISTS whitelist_registry 
                      (student_id TEXT PRIMARY KEY, email TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS system_settings 
                      (key TEXT PRIMARY KEY, value TEXT)''')
    
    cursor.execute("INSERT OR IGNORE INTO system_settings VALUES ('start_time', '2026-06-26T12:01')")
    cursor.execute("INSERT OR IGNORE INTO system_settings VALUES ('end_time', '2026-06-28T02:01')")
    cursor.execute("INSERT OR IGNORE INTO system_settings VALUES ('is_active', '1')")
    
    conn.commit()
    conn.close()

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
        if len(name) <= 2:
            masked_name = name + "**"
        else:
            masked_name = name[:2] + "**" + name[-1]
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
    
    conn = sqlite3.connect('bcet_production.db')
    cursor = conn.cursor()
    cursor.execute("SELECT student_id FROM whitelist_registry WHERE student_id=?", (student_id,))
    whitelisted = cursor.fetchone()
    
    if not whitelisted:
        conn.close()
        return jsonify({"status": "error", "message": "ID not in whitelist database!"}), 400
        
    face_vector_str = json.dumps(face_vector_raw) if face_vector_raw else None
    try:
        cursor.execute("INSERT OR REPLACE INTO android_biometrics VALUES (?, ?, ?)", (student_id, fingerprint_raw, face_vector_str))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Biometrics mapped successfully!"})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/biometric_login', methods=['POST'], strict_slashes=False)
def api_biometric_login():
    data = request.json
    student_id = sanitize_input(data.get('student_id', '')).upper()
    live_fingerprint = data.get('live_fingerprint', None)
    live_face_vector = data.get('live_face_vector', None)
    client_ip = get_client_ip()

    conn = sqlite3.connect('bcet_production.db')
    cursor = conn.cursor()
    cursor.execute("SELECT student_id FROM whitelist_registry WHERE student_id=?", (student_id,))
    whitelisted = cursor.fetchone()

    if not whitelisted:
        conn.close()
        consensus_blockchain.log_intrusion(student_id, "Non-Whitelist ID Attempt", client_ip)
        return jsonify({"status": "error", "message": "FAILED: Student ID is not authorized!"}), 401

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

@app.route('/signup_page', strict_slashes=False)
def signup_page():
    return render_template('signup.html')

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

# 🔥 INSTANT SCREEN POPUP CODE GENERATION
@app.route('/send_signup_otp', methods=['POST'], strict_slashes=False)
def send_signup_otp():
    email = sanitize_input(request.form.get('student_id', '')).lower()
    
    conn = sqlite3.connect('bcet_production.db')
    cursor = conn.cursor()
    cursor.execute("SELECT student_id FROM whitelist_registry WHERE LOWER(email)=? OR UPPER(student_id)=?", (email, email.upper()))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        consensus_blockchain.log_intrusion(email, "Non-Whitelisted Access Attempt", get_client_ip())
        return jsonify({"status": "error", "message": "Email ID or Roll Number is NOT Authorized in College Whitelist!"})
    
    student_id = row[0]
    
    nullifier = hashlib.sha256(f"{student_id}BCET_SALT_2026".encode()).hexdigest()
    if nullifier in consensus_blockchain.nullifiers:
        conn.close()
        return jsonify({"status": "error", "message": "You have ALREADY CAST your vote in this election!"})
        
    conn.close()

    generated_passcode = str(random.randint(100021, 999989))
    DIRECT_OTP_CACHE[student_id] = {
        "passcode": generated_passcode,
        "expires": time.time() + 300
    }

    return jsonify({
        "status": "success", 
        "message": f"🔑 YOUR VERIFICATION PASSCODE IS: {generated_passcode}",
        "passcode": generated_passcode
    })

@app.route('/verify_signup_otp', methods=['POST'], strict_slashes=False)
def verify_signup_otp():
    email = sanitize_input(request.form.get('student_id', '')).lower()
    user_passcode = sanitize_input(request.form.get('otp', '')).strip()

    conn = sqlite3.connect('bcet_production.db')
    cursor = conn.cursor()
    cursor.execute("SELECT student_id FROM whitelist_registry WHERE LOWER(email)=? OR UPPER(student_id)=?", (email, email.upper()))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"status": "error", "message": "Unauthorized Voter ID!"})

    student_id = row[0]
    cache = DIRECT_OTP_CACHE.get(student_id)

    if not cache or time.time() > cache["expires"]:
        return jsonify({"status": "error", "message": "Passcode Expired! Click Get Code again."})

    if cache["passcode"] == user_passcode:
        session.clear()
        session['user_id'] = student_id
        session['user_ip'] = get_client_ip()
        session['token_verified'] = True
        DIRECT_OTP_CACHE.pop(student_id, None)
        return jsonify({"status": "success", "message": "Identity Verified! Redirecting to Ballot Paper..."})
    else:
        consensus_blockchain.log_intrusion(student_id, "Incorrect Passcode Entered", get_client_ip())
        return jsonify({"status": "error", "message": "Incorrect Verification Passcode!"})

@app.route('/login', methods=['POST'], strict_slashes=False)
def login():
    student_id = sanitize_input(request.form.get('student_id', '')).upper()
    password = request.form.get('password', '').strip()
    client_ip = get_client_ip()

    if FAILED_ATTEMPTS.get(client_ip, 0) >= MAX_FAILED_ATTEMPTS:
        consensus_blockchain.log_intrusion(student_id, "Brute Force Threshold Breached", client_ip)
        return "<h1>IP blocked temporarily due to excessive failures.</h1>", 423

    conn = sqlite3.connect('bcet_production.db')
    cursor = conn.cursor()
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
    
    conn = sqlite3.connect('bcet_production.db')
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM whitelist_registry WHERE student_id=?", (student_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or user[0].lower() != email:
        return jsonify({"status": "error", "message": "Credentials mismatch mapping!"})
        
    otp = str(random.randint(100021, 999989))
    FORGOT_OTP_CACHE[student_id] = {"otp": otp, "expires": time.time() + 300, "verified": False}
    return jsonify({"status": "success", "message": f"🔑 RECOVERY PASSCODE: {otp}", "passcode": otp})

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
    conn = sqlite3.connect('bcet_production.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash=? WHERE student_id=?", (hashed, student_id))
    conn.commit()
    conn.close()
    FORGOT_OTP_CACHE.pop(student_id, None)
    return jsonify({"status": "success", "message": "Secret password allocation overridden successfully!"})

@app.route('/', strict_slashes=False)
def index():
    if 'user_id' not in session or not session.get('token_verified'):
        return redirect(url_for('signup_page'))

    conn = sqlite3.connect('bcet_production.db')
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM system_settings WHERE key='start_time'")
    db_start = cursor.fetchone()[0]
    cursor.execute("SELECT value FROM system_settings WHERE key='end_time'")
    db_end = cursor.fetchone()[0]
    cursor.execute("SELECT value FROM system_settings WHERE key='is_active'")
    db_active = cursor.fetchone()[0] == '1'
    conn.close()

    current_settings = {
        "candidates": ELECTION_SETTINGS["candidates"],
        "start_time": db_start,
        "end_time": db_end,
        "is_active": db_active
    }

    now = datetime.now(IST)
    
    def parse_election_time(time_str):
        if "-" not in time_str:
            return datetime.strptime(time_str, "%Y%m%dT%H:%M").replace(tzinfo=IST)
        return datetime.strptime(time_str, "%Y-%m-%dT%H:%M").replace(tzinfo=IST)

    try:
        start = parse_election_time(db_start)
        end = parse_election_time(db_end)
    except Exception:
        start = now - timedelta(days=1)
        end = now + timedelta(days=1)
    
    status = "OPEN"
    if not db_active or now > end:
        status = "CLOSED"
    elif now < start:
        status = "NOT_STARTED"
    
    return render_template('index.html', 
                           candidate_list=ELECTION_SETTINGS["candidates"], 
                           settings=current_settings,
                           election_status=status)

@app.route('/logout', strict_slashes=False)
def logout():
    session.clear() 
    return redirect(url_for('signup_page'))

@app.route('/cast_vote', methods=['POST'], strict_slashes=False)
def cast_vote():
    if 'user_id' not in session or not session.get('token_verified'):
        return redirect(url_for('signup_page'))
    
    conn = sqlite3.connect('bcet_production.db')
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

    time.sleep(1.0)
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

# 🔥 UNIVERSAL ADMIN PANEL ROUTING MATRIX

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
    return render_template('results.html', settings=ELECTION_SETTINGS, vote_counts=vote_counts, logs=consensus_blockchain.security_logs, secret=ADMIN_SECRET, secret_key=ADMIN_SECRET)

@app.route('/admin/voter-registry', methods=['GET'], strict_slashes=False)
@app.route('/admin/voter-registry/<path:secret>', methods=['GET'], strict_slashes=False)
def dynamic_voter_registry_view(secret=None):
    conn = sqlite3.connect('bcet_production.db')
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
            conn = sqlite3.connect('bcet_production.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO whitelist_registry VALUES (?, ?)", (new_id, new_email))
            conn.commit()
            conn.close()
            return jsonify({"status": "success", "message": f"Student Node [{new_id}] mapped successfully!"})
        except sqlite3.Error:
            return jsonify({"status": "error", "message": "ID already exists in Database Whitelist!"})
    return jsonify({"status": "error", "message": "Invalid mapping parameters provided!"})

@app.route('/admin/delete_student_live', methods=['POST'], strict_slashes=False)
@app.route('/admin/delete_student_live/<path:secret>', methods=['POST'], strict_slashes=False)
def delete_student_live(secret=None):
    target_id = sanitize_input(request.form.get('student_id', '')).upper()
    conn = sqlite3.connect('bcet_production.db')
    cursor = conn.cursor()
    cursor.execute("SELECT student_id FROM whitelist_registry WHERE student_id=?", (target_id,))
    exists = cursor.fetchone()
    if exists:
        cursor.execute("DELETE FROM whitelist_registry WHERE student_id=?", (target_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": f"Node [{target_id}] scrubbed from Whitelist Registry."})
    conn.close()
    return jsonify({"status": "error", "message": "Target parsing mapping resolution error."})

@app.route('/admin/factory-reset', methods=['GET'], strict_slashes=False)
@app.route('/admin/factory-reset/<path:secret>', methods=['GET'], strict_slashes=False)
def dynamic_factory_reset_view(secret=None):
    return render_template('factory_reset.html', secret=ADMIN_SECRET, secret_key=ADMIN_SECRET)

@app.route('/admin/execute_node_flush', methods=['POST'], strict_slashes=False)
def execute_node_flush():
    target_id = sanitize_input(request.form.get('student_id', '')).upper()
    if not target_id:
        return jsonify({"status": "error", "message": "Empty tracker reference."})
    conn = sqlite3.connect('bcet_production.db')
    cursor = conn.cursor()
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
    start_val = sanitize_input(data['start'])
    end_val = sanitize_input(data['end'])
    
    conn = sqlite3.connect('bcet_production.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE system_settings SET value=? WHERE key='start_time'", (start_val,))
    cursor.execute("UPDATE system_settings SET value=? WHERE key='end_time'", (end_val,))
    cursor.execute("UPDATE system_settings SET value='1' WHERE key='is_active'")
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/stop_election', methods=['POST'], strict_slashes=False)
def stop_election():
    conn = sqlite3.connect('bcet_production.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE system_settings SET value='0' WHERE key='is_active'")
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