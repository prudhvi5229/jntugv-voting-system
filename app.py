import hashlib
import json
import time
from datetime import datetime, timedelta
import pytz
from io import BytesIO
import sqlite3 # Persistent Storage
import re # Strict Input Sanitation
import random # For OTP Generation
import smtplib # For Sending Email OTP
import ssl # For Secure SMTP SSL Handshake
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash # Secure Hashing
from flask import Flask, render_template, request, jsonify, make_response, url_for, session, redirect

# PDF Libraries
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# INITIALIZE FLASK WITH STATIC FOLDER SUPPORT
app = Flask(__name__, static_url_path='/static', static_folder='static')
# FIXED: Session permanence configuration for the continuous 7-day window
app.secret_key = "BCET_BLOCKCHAIN_2026_SECURE_ULTRA_PRO_MAX_Z_PLUS_DEEPCORE_IMMUTABLE_HARSH"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# --- CONFIGURATION ---
IST = pytz.timezone('Asia/Kolkata')
ADMIN_SECRET = "BCET_ADMIN_PRO" 

# --- PRODUCTION MAIL ENGINE INITIALIZATION ---
SMTP_SERVER = "smtp.gmail.com"
SENDER_EMAIL = "beharacollegeofengineering@gmail.com"
SENDER_PASSWORD = "eiqi zqts lweq ruf"

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
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (student_id TEXT PRIMARY KEY, email TEXT, password_hash TEXT)''')
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

# --- FIXED: Secure Email Engine utilizing SSL Port 465 to bypass Render outbound blocks ---
def send_secure_otp_email(target_email, otp_code, purpose="Registration"):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = target_email
        msg['Subject'] = f"Secure Gatekeeper - OTP for {purpose}"
        body = f"Hello Student,\n\nYour 6-Digit One-Time Password (OTP) for BCET Voting System {purpose} is: {otp_code}\n\nThis code is valid for 5 minutes only.\n\nRegards,\nBCET Blockchain Core Engine"
        msg.attach(MIMEText(body, 'plain'))
        
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL(SMTP_SERVER, 465, context=context)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, target_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Secure SSL Port 465 Error Alert: {e}")
        return False

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

@app.before_request
def intercept_rate_limits():
    global SYSTEM_FORENSIC_LOCKOUT
    if SYSTEM_FORENSIC_LOCKOUT and not request.path.startswith('/admin-results') and not request.path.startswith('/admin/'):
        return "<h1>503 Service Unavailable: Cryptographic Forensic Lockout Active.</h1>", 503

    client_ip = get_client_ip()
    current_time = time.time()
    if client_ip not in RATE_LIMIT_TRACKER:
        RATE_LIMIT_TRACKER[client_ip] = []
    RATE_LIMIT_TRACKER[client_ip] = [t for t in RATE_LIMIT_TRACKER[client_ip] if current_time - t < RATE_LIMIT_WINDOW]
    if len(RATE_LIMIT_TRACKER[client_ip]) >= MAX_REQUESTS_PER_WINDOW:
        consensus_blockchain.log_intrusion("ANTI_DDOS_GATE", "Rate Limit Violation / Network Attack Blocked", client_ip)
        return "<h1>429 Too Many Requests. Anti-DDoS Lock Activated.</h1>", 429
    RATE_LIMIT_TRACKER[client_ip].append(current_time)

# --- ROUTES ---

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
    start = datetime.strptime(ELECTION_SETTINGS["start_time"], "%Y-%m-%dT%H:%M").replace(tzinfo=IST)
    end = datetime.strptime(ELECTION_SETTINGS["end_time"], "%Y-%m-%dT%H:%M").replace(tzinfo=IST)
    
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
        consensus_blockchain.log_intrusion(student_id, "Brute Force Threshold Breached (Node Locked)", client_ip)
        return "<h1>IP blocked temporarily due to excessive failures.</h1>", 423

    conn = sqlite3.connect('bcet_production.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE student_id=?", (student_id,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[0], password):
        FAILED_ATTEMPTS[client_ip] = 0 
        # FIXED: Forces browser session state persistence across the 7-day window
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
        consensus_blockchain.log_intrusion(student_id, "Fraudulent Recovery Sequence Execution Breach", get_client_ip())
        return jsonify({"status": "error", "message": "Credentials mismatch mapping!"})

    otp = str(random.randint(100021, 999989))
    FORGOT_OTP_CACHE[student_id] = {"otp": otp, "expires": time.time() + 300, "verified": False}

    if send_secure_otp_email(email, otp, "Password Reset Protocol"):
        return jsonify({"status": "success", "message": "Security recovery token pushed to email address!"})
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
        return jsonify({"status": "success", "message": "Security shield cleared! You can now update password configurations."})
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

    expected_sig = hashlib.sha256(f"{student_id}{user_ip}{session.get('generated_token')}".encode()).hexdigest()
    if session.get('binding_signature') != expected_sig:
        consensus_blockchain.log_intrusion(student_id, "Cryptographic Packet Signature Mismatch! Tampering Blocked.", user_ip)
        session.clear()
        return "<h1>Security Intrusion Terminated.</h1>", 403

    nullifier = hashlib.sha256(f"{student_id}BCET_SALT_2026".encode()).hexdigest()
    if nullifier in consensus_blockchain.nullifiers:
        consensus_blockchain.log_intrusion(student_id, "Double Broadcast Transaction Packet Intercepted", user_ip)
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

                    result = {
                        "candidate": matched_candidate, 
                        "timestamp": block['timestamp'], 
                        "block_index": block['index']
                    }
                    break
            if result: break
    return render_template('audit.html', searched_id=searched_id, result=result)

@app.route(f'/admin-results/{ADMIN_SECRET}')
def admin_results():
    global SYSTEM_FORENSIC_LOCKOUT
    vote_counts = {}

    for c in ELECTION_SETTINGS["candidates"]:
        tally = consensus_blockchain.verify_consensus_and_tally(c['name'])
        if tally == -999:
            vote_counts[c['name']] = "🔴 LOCKOUT ACTIVE"
        else:
            vote_counts[c['name']] = tally

    if SYSTEM_FORENSIC_LOCKOUT:
        consensus_blockchain.log_intrusion("TRI_NODE_CORE", "CRITICAL ATTEMPT: System Halted Due to Multi-Node Tampering!", get_client_ip())

    return render_template('results.html', 
                            settings=ELECTION_SETTINGS, 
                            vote_counts=vote_counts, 
                            logs=consensus_blockchain.security_logs)

@app.route('/admin/voter-registry/<secret>')
def dynamic_voter_registry_view(secret):
    if secret != ADMIN_SECRET:
        return "Unauthorized Core Request", 403
    return render_template('voter_registry.html', students=AUTHORIZED_STUDENTS, secret=ADMIN_SECRET)

@app.route('/admin/add_student_live', methods=['POST'])
def add_student_live():
    new_id = sanitize_input(request.form.get('student_id', '')).upper()
    if new_id and new_id not in AUTHORIZED_STUDENTS:
        AUTHORIZED_STUDENTS.append(new_id)
        return jsonify({"status": "success", "message": f"Student Node [{new_id}] injected into Whitelist!"})
    return jsonify({"status": "error", "message": "ID already exists or parameter invalid!"})

@app.route('/admin/delete_student_live', methods=['POST'])
def delete_student_live():
    target_id = sanitize_input(request.form.get('student_id', '')).upper()
    if target_id in AUTHORIZED_STUDENTS:
        AUTHORIZED_STUDENTS.remove(target_id)
        return jsonify({"status": "success", "message": f"Voter Node [{target_id}] removed from Whitelist."})
    return jsonify({"status": "error", "message": "Target parsing mapping resolution error."})

@app.route('/admin/factory-reset/<secret>')
def dynamic_factory_reset_view(secret):
    if secret != ADMIN_SECRET:
        return "Unauthorized Core Request", 403
    return render_template('factory_reset.html', secret=ADMIN_SECRET)

@app.route('/admin/execute_node_flush', methods=['POST'])
def execute_node_flush():
    target_id = sanitize_input(request.form.get('student_id', '')).upper()
    if not target_id:
        return jsonify({"status": "error", "message": "Empty framework reference tracker."})
    conn = sqlite3.connect('bcet_production.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE student_id=?", (target_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": f"Database scrubbed for Student [{target_id}]. Safe for new signup."})

@app.route('/admin/security-audit/<secret>')
def dynamic_security_audit_view(secret):
    if secret != ADMIN_SECRET:
        return "Unauthorized Core Request", 403
    return render_template('security_audit.html', secret=ADMIN_SECRET, logs=consensus_blockchain.security_logs)

@app.route('/sync_candidates', methods=['POST'])
def sync_candidates():
    incoming_data = request.json
    updated_candidates = []
    for c in incoming_data.get('candidates', []):
        updated_candidates.append({
            "name": sanitize_input(c.get('name')),
            "symbol": c.get('symbol', ''), 
            "manifesto": c.get('manifesto', '') 
        })
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
        return "Unauthorized Request Execution Aborted.", 403
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