import hashlib
import json
import time
from datetime import datetime, timedelta
import pytz
from io import BytesIO
import sqlite3 # Persistent Storage
import re # Strict Input Sanitation
import random # For OTP Generation
import requests # Used for Resend HTTP API calls to bypass Render SMTP blocks
import numpy as np # For numerical processing of Face Vectors from Android Engine
from werkzeug.security import generate_password_hash, check_password_hash # Secure Hashing
from flask import Flask, render_template, request, jsonify, make_response, url_for, session, redirect

# PDF Libraries
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# INITIALIZE FLASK WITH STATIC FOLDER SUPPORT
app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = "BCET_BLOCKCHAIN_2026_SECURE_ULTRA_PRO_MAX_Z_PLUS_DEEPCORE_IMMUTABLE_HARSH"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# --- CONFIGURATION ---
IST = pytz.timezone('Asia/Kolkata')
ADMIN_SECRET = "BCET_ADMIN_PRO" 

# --- PRODUCTION RESEND API CONFIGURATION ---
RESEND_API_KEY = "re_LP3esKc4_QL2iupoPzxxnwznc2cADtYNZ"
SENDER_EMAIL = "onboarding@resend.dev" 

# --- VOLATILE OTP MEMORY MATRIX ---
SIGNUP_OTP_CACHE = {}  
FORGOT_OTP_CACHE = {}  

# --- ADVANCED SECURITY MEMORY MATRIX ---
FAILED_ATTEMPTS = {} 
MAX_FAILED_ATTEMPTS = 5
RATE_LIMIT_TRACKER = {} 
RATE_LIMIT_WINDOW = 10 
MAX_REQUESTS_PER_WINDOW = 20 
SYSTEM_FORENSIC_LOCKOUT = False # Critical Anti-Hacking Killswitch

# --- AUTHORIZED STUDENT LIST Matrix ---
AUTHORIZED_STUDENTS = [
    "24V11A0501", "24V11A0502", "24V11A0503", "24V11A0504", "24V11A0505",
    "24V11A0506", "24V11A0507", "24V11A0510", "24V11A0511", "24V11A0512",
    "24V11A0513", "24V11A0514", "24V11A0515", "24V11A0516", "24V11A0517",
    "24V11A0518", "24V11A0519", "24V11A0520", "24V11A0521", "24V11A0522",
    "24V11A0523", "24V11A0525", "24V11A0526", "24V11A0527", "24V11A0528",
    "24V11A0529", "24V11A0530", "24V11A0531", "24V11A0532", "24V11A0534",
    "24V11A0535", "24V11A0536", "24V11A0537", "24V11A0538", "24V11A0539",
    "24V11A0541", "24V11A0542", "24V11A0543", "24V11A0544", "24V11A0545",
    "24V11A0546", "24V11A0547", "24V11A0548", "24V11A0549", "24V11A0550",
    "24V11A0551", "24V11A0552", "24V11A0553", "24V11A0554", "24V11A0555",
    "24V11A0556", "24V11A0557", "24V11A0558", "24V11A0559", "24V11A0560",
    "24V11A0561", "24V11A0563", "24V11A0564", "24V11A0565", "24V11A0566",
    "24V11A0567", "24V11A0568", "24V11A0569", "24V11A0570", "24V11A0571",
    "24V11A0572", "24V11A0573", "24V11A0574", "24V11A0575", "24V11A0576",
    "24V11A0577", "24V11A0578", "24V11A0579", "25V15A0501", "25V15A0502",
    "25V15A0503", "25V15A0504"
]

def init_db():
    conn = sqlite3.connect('bcet_production.db')
    cursor = conn.cursor()
    # Web Auth Table (Your original web logic database remains fully intact)
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (student_id TEXT PRIMARY KEY, email TEXT, password_hash TEXT)''')
    # Android Biometric Matrix Table (For roll number mapping without passwords/emails)
    cursor.execute('''CREATE TABLE IF NOT EXISTS android_biometrics 
                      (student_id TEXT PRIMARY KEY, fingerprint_data TEXT, face_vector TEXT)''')
    conn.commit()
    conn.close()

init_db()

ELECTION_SETTINGS = {
    "candidates": [
        {"name": "Ramu", "symbol": "", "manifesto": ""}, 
        {"name": "Laxman", "symbol": "", "manifesto": ""}
    ],
    "start_time": "2026-06-26T12:01",
    "end_time": "2026-06-28T02:01",
    "is_active": True,
    "authorized_prefix": "24V11A",
    "range_start": 501,
    "range_end": 580,
    "admin_secret": ADMIN_SECRET
}

def send_secure_otp_email(target_email, otp_code, purpose="Registration"):
    try:
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "from": f"BCET Gatekeeper <{SENDER_EMAIL}>",
            "to": [target_email],
            "subject": f"Secure Gatekeeper - OTP for {purpose}",
            "text": f"Hello Student,\n\nYour 6-Digit One-Time Password (OTP) for BCET Voting System {purpose} is: {otp_code}\n\nThis code is valid for 5 minutes only.\n\nRegards,\nBCET Blockchain Core Engine"
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            return True
        return False
    except Exception:
        return False

# --- TRI-NODE CRYPTOGRAPHIC BLOCKCHAIN ENGINE (Untouched) ---
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

# --- APP BIOMETRIC VERIFICATION LOGIC ---
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

# --- NEW ANDROID APP INTEGRATION ENDPOINTS ---

@app.route('/api/admin/upload_biometrics', methods=['POST'])
def api_admin_upload_biometrics():
    secret = request.headers.get('Admin-Secret', '')
    if secret != ADMIN_SECRET:
        return jsonify({"status": "error", "message": "Unauthorized Admin Request."}), 403
    data = request.json
    student_id = sanitize_input(data.get('student_id', '')).upper()
    fingerprint_raw = data.get('fingerprint_data', None)
    face_vector_raw = data.get('face_vector', None)
    if student_id not in AUTHORIZED_STUDENTS:
        return jsonify({"status": "error", "message": "ID not in whitelist!"}), 400
    conn = sqlite3.connect('bcet_production.db')
    cursor = conn.cursor()
    face_vector_str = json.dumps(face_vector_raw) if face_vector_raw else None
    try:
        cursor.execute("INSERT OR REPLACE INTO android_biometrics VALUES (?, ?, ?)", (student_id, fingerprint_raw, face_vector_str))
        conn.commit()
        return jsonify({"status": "success", "message": "Biometrics mapped successfully!"})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/biometric_login', methods=['POST'])
def api_biometric_login():
    """APP BIOMETRIC 'OR' LOGIC GATEWAY"""
    data = request.json
    student_id = sanitize_input(data.get('student_id', '')).upper()
    live_fingerprint = data.get('live_fingerprint', None)
    live_face_vector = data.get('live_face_vector', None)
    client_ip = get_client_ip()

    if student_id not in AUTHORIZED_STUDENTS:
        consensus_blockchain.log_intrusion(student_id, "Non-Whitelist ID Attempt", client_ip)
        return jsonify({"status": "error", "message": "FAILED: Student ID is not authorized!"}), 401

    conn = sqlite3.connect('bcet_production.db')
    cursor = conn.cursor()
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

@app.route('/api/verify_app_token', methods=['POST'])
def api_verify_app_token():
    """Validates token copy-paste on App verification page and bridges to Web Session"""
    data = request.json
    student_id = sanitize_input(data.get('student_id', '')).upper()
    user_input_token = sanitize_input(data.get('input_token', '')).upper()

    actual_token = session.get('vote_token')
    active_voter = session.get('active_voter')

    if active_voter == student_id and user_input_token == actual_token:
        session['app_verified'] = True
        session['user_id'] = student_id
        session['user_ip'] = get_client_ip()
        session['token_verified'] = True # Bypasses web login OTP check entirely
        
        return jsonify({
            "status": "success",
            "message": "Token matched successfully! Session authorized.",
            "redirect_url": url_for('index', _external=True)
        })
    else:
        consensus_blockchain.log_intrusion(student_id, "App Token Mismatch", get_client_ip())
        return jsonify({"status": "error", "message": "FAILED: Token mismatch configuration!"}), 403

# --- ORIGINAL WEB PORTAL ROUTES ---

@app.route('/welcome')
def welcome():
    if 'user_id' in session and session.get('token_verified'):
        return redirect(url_for('index'))
    return render_template('welcome.html')

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('welcome'))
    
    if session.get('user_ip') != get_client_ip():
        consensus_blockchain.log_intrusion(session.get('user_id'), "Session Hijack Blocked (IP Alteration)", get_client_ip())
        session.clear()
        return redirect(url_for('welcome'))

    if not session.get('token_verified'):
        return redirect(url_for('auth_token_display'))

    now = datetime.now(IST)
    
    # --- Advanced Time Format Fallback Detection ---
    def parse_election_time(time_str):
        if "-" not in time_str:
            return datetime.strptime(time_str, "%Y%m%dT%H:%M").replace(tzinfo=IST)
        return datetime.strptime(time_str, "%Y-%m-%dT%H:%M").replace(tzinfo=IST)

    try:
        start = parse_election_time(ELECTION_SETTINGS["start_time"])
        end = parse_election_time(ELECTION_SETTINGS["end_time"])
    except Exception:
        start = now - timedelta(days=1)
        end = now + timedelta(days=1)
    
    status = "OPEN"
    if not ELECTION_SETTINGS["is_active"] or now > end:
        status = "CLOSED"
    elif now < start:
        status = "NOT_STARTED"
    
    return render_template('index.html', 
                           candidate_list=ELECTION_SETTINGS["candidates"], 
                           settings=ELECTION_SETTINGS,
                           election_status=status)

@app.route('/auth_token_display')
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

@app.route('/verify_token_page')
def verify_token_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('token_verification_input.html')

@app.route('/verify_token', methods=['POST'])
def verify_token():
    user_input = sanitize_input(request.form.get('input_token', '')).upper()
    actual_token = session.get('generated_token')

    if user_input and user_input == actual_token:
        session['token_verified'] = True
        return redirect(url_for('index'))
    else:
        consensus_blockchain.log_intrusion(session.get('user_id'), "Token Guard Exception Triggered", get_client_ip())
        return render_template('token_verification_input.html', error="Invalid Token!")

@app.route('/signup_page')
def signup_page():
    return render_template('signup.html')

@app.route('/send_signup_otp', methods=['POST'])
def send_signup_otp():
    student_id = sanitize_input(request.form.get('student_id', '')).upper()
    email = sanitize_input(request.form.get('email', '')).lower()
    password = request.form.get('password', '').strip()

    if student_id not in AUTHORIZED_STUDENTS:
        consensus_blockchain.log_intrusion(student_id, "Non-Authorized Whitelist Sign-up Intrusion Attempt", get_client_ip())
        return jsonify({"status": "error", "message": "ID not authorized by BCET Whitelist!"})

    conn = sqlite3.connect('bcet_production.db')
    cursor = conn.cursor()
    cursor.execute("SELECT student_id FROM users WHERE student_id=?", (student_id,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"status": "error", "message": "Already registered! Log in directly."})
    conn.close()

    otp = str(random.randint(100021, 999989))
    SIGNUP_OTP_CACHE[student_id] = {
        "otp": otp, "email": email, "password_hash": generate_password_hash(password),
        "expires": time.time() + 300
    }

    if send_secure_otp_email(email, otp, "Account Registration Gate"):
        return jsonify({"status": "success", "message": "Verification OTP sent to your email!"})
    return jsonify({"status": "error", "message": "Email Relay Failed. Check App Configurations."})

@app.route('/verify_signup_otp', methods=['POST'])
def verify_signup_otp():
    student_id = sanitize_input(request.form.get('student_id', '')).upper()
    user_otp = sanitize_input(request.form.get('otp', '')).strip()

    cache = SIGNUP_OTP_CACHE.get(student_id)
    if not cache or time.time() > cache["expires"]:
        return jsonify({"status": "error", "message": "OTP Expired or Invalid Session Key!"})

    if cache["otp"] == user_otp:
        try:
            conn = sqlite3.connect('bcet_production.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (student_id, cache["email"], cache["password_hash"]))
            conn.commit()
            conn.close()
            SIGNUP_OTP_CACHE.pop(student_id, None)
            return jsonify({"status": "success", "message": "Account created successfully!"})
        except sqlite3.Error:
            return jsonify({"status": "error", "message": "Database Lockout Error."})
    else:
        consensus_blockchain.log_intrusion(student_id, "Fraudulent Account Verification OTP Code Defect", get_client_ip())
        return jsonify({"status": "error", "message": "Incorrect OTP Verification Code!"})

@app.route('/login', methods=['POST'])
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

@app.route('/forgot_password_page')
def forgot_password_page():
    return render_template('forgot_password.html')

@app.route('/send_forgot_otp', methods=['POST'])
def send_forgot_otp():
    student_id = sanitize_input(request.form.get('student_id', '')).upper()
    email = sanitize_input(request.form.get('email', '')).lower()
    conn = sqlite3.connect('bcet_production.db')
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users WHERE student_id=?", (student_id,))
    user = cursor.fetchone()
    conn.close()
    if not user or user[0] != email:
        return jsonify({"status": "error", "message": "Credentials mismatch mapping!"})
    otp = str(random.randint(100021, 999989))
    FORGOT_OTP_CACHE[student_id] = {"otp": otp, "expires": time.time() + 300, "verified": False}
    if send_secure_otp_email(email, otp, "Password Reset Protocol"):
        return jsonify({"status": "success", "message": "Security recovery token pushed!"})
    return jsonify({"status": "error", "message": "Email Dispatched Relay Mechanism Failed."})

@app.route('/verify_forgot_code', methods=['POST'])
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

@app.route('/commit_new_password', methods=['POST'])
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

@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('welcome'))

@app.route('/cast_vote', methods=['POST'])
def cast_vote():
    if 'user_id' not in session or not session.get('token_verified'):
        return redirect(url_for('welcome'))
    if not ELECTION_SETTINGS["is_active"]:
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

@app.route('/audit', methods=['GET', 'POST'])
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

@app.route(f'/admin-results/{ADMIN_SECRET}')
def admin_results():
    global SYSTEM_FORENSIC_LOCKOUT
    vote_counts = {}
    for c in ELECTION_SETTINGS["candidates"]:
        tally = consensus_blockchain.verify_consensus_and_tally(c['name'])
        vote_counts[c['name']] = "🔴 LOCKOUT ACTIVE" if tally == -999 else tally
    return render_template('results.html', settings=ELECTION_SETTINGS, vote_counts=vote_counts, logs=consensus_blockchain.security_logs)

@app.route('/admin/voter-registry/<secret>')
def dynamic_voter_registry_view(secret):
    if secret != ADMIN_SECRET:
        return "Unauthorized Request", 403
    return render_template('voter_registry.html', students=AUTHORIZED_STUDENTS, secret=ADMIN_SECRET)

@app.route('/admin/add_student_live', methods=['POST'])
def add_student_live():
    new_id = sanitize_input(request.form.get('student_id', '')).upper()
    if new_id and new_id not in AUTHORIZED_STUDENTS:
        AUTHORIZED_STUDENTS.append(new_id)
        return jsonify({"status": "success", "message": f"Student Node [{new_id}] injected!"})
    return jsonify({"status": "error", "message": "ID invalid or exists!"})

@app.route('/admin/delete_student_live', methods=['POST'])
def delete_student_live():
    target_id = sanitize_input(request.form.get('student_id', '')).upper()
    if target_id in AUTHORIZED_STUDENTS:
        AUTHORIZED_STUDENTS.remove(target_id)
        return jsonify({"status": "success", "message": f"Node [{target_id}] removed."})
    return jsonify({"status": "error", "message": "Target parsing mapping resolution error."})

@app.route('/admin/factory-reset/<secret>')
def dynamic_factory_reset_view(secret):
    if secret != ADMIN_SECRET:
        return "Unauthorized Request", 403
    return render_template('factory_reset.html', secret=ADMIN_SECRET)

@app.route('/admin/execute_node_flush', methods=['POST'])
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

@app.route('/admin/security-audit/<secret>')
def dynamic_security_audit_view(secret):
    if secret != ADMIN_SECRET:
        return "Unauthorized Request", 403
    return render_template('security_audit.html', secret=ADMIN_SECRET, logs=consensus_blockchain.security_logs)

@app.route('/sync_candidates', methods=['POST'])
def sync_candidates():
    incoming_data = request.json
    updated_candidates = []
    for c in incoming_data.get('candidates', []):
        updated_candidates.append({"name": sanitize_input(c.get('name')), "symbol": c.get('symbol', ''), "manifesto": c.get('manifesto', '')})
    ELECTION_SETTINGS["candidates"] = updated_candidates
    return jsonify({"status": "success", "message": "Synced Successfully!"})

@app.route('/update_timing', methods=['POST'])
def update_timing():
    data = request.json
    ELECTION_SETTINGS["start_time"] = sanitize_input(data['start'])
    ELECTION_SETTINGS["end_time"] = sanitize_input(data['end'])
    ELECTION_SETTINGS["is_active"] = True
    return jsonify({"status": "success"})

@app.route('/stop_election', methods=['POST'])
def stop_election():
    ELECTION_SETTINGS["is_active"] = False
    return jsonify({"status": "success"})

@app.route('/reset_election', methods=['POST'])
def reset_election():
    global SYSTEM_FORENSIC_LOCKOUT
    SYSTEM_FORENSIC_LOCKOUT = False
    consensus_blockchain.reset_engine()
    return jsonify({"status": "success"})

@app.route('/download-results/<secret>')
def download_results(secret):
    if secret != ADMIN_SECRET:
        return "Unauthorized Aborted.", 403
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