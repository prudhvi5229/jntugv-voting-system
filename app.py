import hashlib
import json
import time
from datetime import datetime
import pytz
from io import BytesIO
import sqlite3 # Persistent Storage
import re # Strict Input Sanitation
from werkzeug.security import generate_password_hash, check_password_hash # Secure Hashing
from flask import Flask, render_template, request, jsonify, make_response, url_for, session, redirect

# PDF Libraries
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# INITIALIZE FLASK WITH STATIC FOLDER SUPPORT
app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = "BCET_BLOCKCHAIN_2026_SECURE_ULTRA_PRO_MAX_Z_PLUS_DEEPCORE"

# --- CONFIGURATION ---
IST = pytz.timezone('Asia/Kolkata')
ADMIN_SECRET = "BCET_ADMIN_PRO" 

# --- ADVANCED SECURITY MEMORY MATRIX ---
FAILED_ATTEMPTS = {} 
MAX_FAILED_ATTEMPTS = 5
RATE_LIMIT_TRACKER = {} # DDoS Protection Matrix
RATE_LIMIT_WINDOW = 10 # Seconds
MAX_REQUESTS_PER_WINDOW = 20 

# --- AUTHORIZED STUDENT LIST ---
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

# --- PERSISTENCE: DATABASE SETUP ---
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

# --- LIGHTWEIGHT TRI-NODE MULTI-CONSENSUS BLOCKCHAIN CORE ---
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
        # 3 వేర్వేరు వర్చువల్ నోడ్స్ (Tri-Node Consensus Layout)
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

    # ఓటు వేసినప్పుడు 3 నోడ్స్ కి ఒకేసారి సమాంతరంగా (Parallel) బ్రాడ్‌కాస్ట్ అవుతుంది
    def broadcast_transaction(self, vote_data):
        self.global_voter_count += 1
        for node_name, node_obj in self.nodes.items():
            last_block = node_obj.chain[-1]
            prev_hash = node_obj.hash(last_block)
            node_obj.create_block(proof=123, previous_hash=prev_hash, votes=[vote_data])

    # Z+++++++ MULTI-NODE CONSENSUS CHECK ALGORITHM
    def verify_consensus_and_tally(self, candidate_name):
        tally_map = {"Node_A": 0, "Node_B": 0, "Node_C": 0}
        valid_nodes_count = 0

        # Step 1: ప్రతి నోడ్ యొక్క ఇంటర్నల్ హాష్ లింక్ చెక్ చేస్తుంది
        for name, node in self.nodes.items():
            if node.is_node_valid():
                valid_nodes_count += 1
                # ఆ నోడ్ లో సదరు కాండిడేట్ కి ఉన్న ఓట్లను లెక్కిస్తుంది
                for block in node.chain:
                    for v in block['votes']:
                        if v['candidate'] == candidate_name:
                            tally_map[name] += 1

        # Step 2: 51% Attack Detection (కనీసం 2 నోడ్స్ హాష్ అగ్రీ అవ్వాలి)
        votes_list = list(tally_map.values())
        # మెజారిటీ ఓటింగ్ కన్సెన్సస్ రూల్ (Consensus Check)
        majority_vote = max(set(votes_list), key=votes_list.count)
        
        # ఒకవేళ ఏదైనా నోడ్ లో డేటా మారితే ఇంట్రూజన్ రికార్డ్ అవుతుంది
        if votes_list.count(majority_vote) < 2 or len(self.nullifiers) != self.global_voter_count:
            return -999 # Security Breach Signal Trigger
            
        return majority_vote

consensus_blockchain = MultiNodeConsensusEngine()

# --- HELPER SECURITY FUNCTIONS ---
def get_client_ip():
    raw_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    return raw_ip.split(',')[0].strip() if raw_ip and ',' in raw_ip else request.remote_addr

def sanitize_input(text):
    if not text: return ""
    return re.sub(r"[<>\'\"\\;=\\-]", "", str(text)).strip()

# --- Anti-DDoS Interceptor ---
@app.before_request
def intercept_rate_limits():
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

# --- BLOCKCHAIN AUTH TOKEN ROUTES ---

@app.route('/auth_token_display')
def auth_token_display():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    sid = session['user_id']
    raw_data = f"{sid}{time.time()}{app.secret_key}"
    blockchain_token = hashlib.sha256(raw_data.encode()).hexdigest().upper()[:12]
    
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

# --- AUTHENTICATION ROUTES ---

@app.route('/signup_page')
def signup_page():
    return render_template('signup.html')

@app.route('/register', methods=['POST'])
def register():
    student_id = sanitize_input(request.form.get('student_id', '')).upper()
    email = sanitize_input(request.form.get('email', '')).lower()
    password = request.form.get('password', '').strip()

    if student_id not in AUTHORIZED_STUDENTS:
        consensus_blockchain.log_intrusion(student_id, "Blacklisted / Non-Authorized Student Signup Registry Attempt", get_client_ip())
        return jsonify({"status": "error", "message": "ID not authorized by BCET!"})
    
    hashed_password = generate_password_hash(password)

    try:
        conn = sqlite3.connect('bcet_production.db')
        cursor = conn.cursor()
        cursor.execute("SELECT student_id FROM users WHERE student_id=?", (student_id,))
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "Already registered!"})

        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (student_id, email, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Account created!"})
    except sqlite3.Error:
        return jsonify({"status": "error", "message": "Database Lockout."})

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

@app.route('/reset_password', methods=['POST'])
def reset_password():
    student_id = sanitize_input(request.form.get('student_id', '')).upper()
    email = sanitize_input(request.form.get('email', '')).lower()
    new_password = request.form.get('password', '').strip()
    
    conn = sqlite3.connect('bcet_production.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE student_id=? AND email=?", (student_id, email))
    user = cursor.fetchone()

    if not user:
        conn.close()
        consensus_blockchain.log_intrusion(student_id, "Fraudulent Password Override Attempt", get_client_ip())
        return jsonify({"status": "error", "message": "Hall Ticket and Email mismatch!"})

    hashed_password = generate_password_hash(new_password)
    cursor.execute("UPDATE users SET password_hash=? WHERE student_id=?", (hashed_password, student_id))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Password Reset Successful!"})

@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('welcome'))

# --- VOTING & AUDIT ---

@app.route('/cast_vote', methods=['POST'])
def cast_vote():
    if 'user_id' not in session or not session.get('token_verified'):
        return redirect(url_for('welcome'))

    if not ELECTION_SETTINGS["is_active"]:
        return "<h1>Election Closed</h1>"
    
    student_id = session['user_id']
    candidate = sanitize_input(request.form.get('candidate'))
    user_ip = get_client_ip()

    # Zero-Knowledge సాల్టెడ్ నల్లిఫైయర్ ప్రొటెక్షన్ లేయర్
    nullifier = hashlib.sha256(f"{student_id}BCET_SALT_2026".encode()).hexdigest()
    if nullifier in consensus_blockchain.nullifiers:
        consensus_blockchain.log_intrusion(student_id, "Double Broadcast Transaction Packet Intercepted", user_ip)
        session.clear() 
        return render_template('already_cast.html')

    time.sleep(1.5)

    consensus_blockchain.nullifiers.add(nullifier)
    receipt_id = hashlib.sha256(str(time.time()).encode()).hexdigest().upper()[:12]
    
    # మొత్తం 3 వర్చువల్ నోడ్స్ కి ఒకేసారి ఓటు బ్రాడ్‌కాస్ట్ అవుతుంది
    vote_packet = {'candidate': candidate, 'receipt': receipt_id}
    consensus_blockchain.broadcast_transaction(vote_packet)
    
    session.clear() 
    return render_template('success.html', candidate=candidate, receipt=receipt_id, timestamp=datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/audit', methods=['GET', 'POST'])
def audit_portal():
    searched_id = sanitize_input(request.form.get('receipt', '')).upper()
    result = None
    if request.method == 'POST':
        # మెజారిటీ నోడ్ (Node A) నుండి ట్రాన్సాక్షన్ ఆడిట్ వెరిఫై చేస్తుంది
        for block in consensus_blockchain.nodes["Node_A"].chain:
            for vote in block['votes']:
                if vote.get('receipt') == searched_id:
                    result = {
                        "candidate": vote['candidate'], 
                        "timestamp": block['timestamp'], 
                        "block_index": block['index']
                    }
                    break
            if result: break
    return render_template('audit.html', searched_id=searched_id, result=result)

# --- ADMIN ROUTES ---

@app.route(f'/admin-results/{ADMIN_SECRET}')
def admin_results():
    vote_counts = {}
    security_breach_detected = False

    for c in ELECTION_SETTINGS["candidates"]:
        # ప్రతి అడ్మిన్ పేజీ రీఫ్రెష్ కి 3 నోడ్స్ మధ్య Consensus ని కాలిక్యులేట్ చేస్తుంది
        tally = consensus_blockchain.verify_consensus_and_tally(c['name'])
        if tally == -999:
            security_breach_detected = True
            vote_counts[c['name']] = 0
        else:
            vote_counts[c['name']] = tally

    if security_breach_detected:
        consensus_blockchain.log_intrusion("TRI_NODE_CORE", "CRITICAL ALERT: 51% Node Attack Vector Detected!", get_client_ip())

    return render_template('results.html', 
                            settings=ELECTION_SETTINGS, 
                            vote_counts=vote_counts, 
                            logs=consensus_blockchain.security_logs)

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
    consensus_blockchain.reset_engine()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)