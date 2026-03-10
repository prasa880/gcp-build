import asyncio, pytz, base64, os, threading, time, socket
from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
from telethon import TelegramClient
from telethon.tl.types import UserStatusOnline, UserStatusOffline
from telethon.tl.functions.users import GetFullUserRequest

# --- CONFIG ---
API_ID = 36600266
API_HASH = "767d9ba0588da914d44002a7f182a733"
SESSION_NAME = "prasanth_session"
COURIER_ID = 1321263736
WEB_PIN = "2858"
TIMEZONE = pytz.timezone('Asia/Kolkata')
HOSTNAME = socket.gethostname()

app = Flask(__name__)
app.secret_key = os.urandom(24)

cache = {"online": False, "history": [], "error": None, "unread": 0, "last_seen": "Unknown"}

def telegram_worker():
    global cache
    last_msg_id = 0
    while True:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        client = TelegramClient(SESSION_NAME, API_ID, API_HASH, loop=loop)
        try:
            loop.run_until_complete(client.connect())
            if loop.run_until_complete(client.is_user_authorized()):
                full = loop.run_until_complete(client(GetFullUserRequest(COURIER_ID)))
                user = full.users[0]
                status_obj = user.status
                is_online = isinstance(status_obj, UserStatusOnline)
                
                last_seen_str = "Online"
                if not is_online and isinstance(status_obj, UserStatusOffline):
                    last_seen_str = status_obj.was_online.astimezone(TIMEZONE).strftime("%H:%M")
                elif is_online:
                    last_seen_str = "Now"

                msgs = loop.run_until_complete(client.get_messages(COURIER_ID, limit=15))
                if msgs:
                    current_top_id = msgs[0].id
                    if last_msg_id != 0 and current_top_id > last_msg_id:
                        new_count = sum(1 for m in msgs if m.id > last_msg_id and not m.out)
                        if new_count > 0: cache["unread"] += new_count
                    last_msg_id = current_top_id

                new_h = []
                for m in msgs:
                    txt = m.text if m.text else "🖼️ [Media/Cartoon]"
                    new_h.append({
                        "sender": "You" if m.out else "Target",
                        "text": base64.b64encode(txt.encode()).decode(),
                        "time": m.date.astimezone(TIMEZONE).strftime("%H:%M")
                    })
                cache["online"] = is_online
                cache["last_seen"] = last_seen_str
                cache["history"] = new_h
                cache["error"] = None
        except Exception as e:
            cache["error"] = str(e)
        finally:
            if client.is_connected():
                # FIX: Remove run_until_complete for disconnect
                client.disconnect()
            loop.close()
        time.sleep(10)

threading.Thread(target=telegram_worker, daemon=True).start()

DASH_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: -apple-system, sans-serif; margin: 0; padding: 15px; display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #050505; color: white; }
        .bg-container { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; background: radial-gradient(circle at center, #111 0%, #000 100%); }
        .card { width: 100%; max-width: 400px; background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 28px; backdrop-filter: blur(25px); border: 1px solid rgba(255,255,255,0.08); position: relative; }
        
        /* Cartoon Styling */
        .greetings { text-align: center; margin-bottom: 20px; }
        .avatar { font-size: 3rem; margin-bottom: 5px; display: block; }
        .host-info { font-size: 0.6rem; color: #555; font-family: monospace; }

        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; cursor: pointer; padding: 15px; background: rgba(255,255,255,0.02); border-radius: 18px; }
        .dot { font-size: 1.6rem; margin-right: 12px; color: #333; }
        .online-active { color: #00ff88 !important; text-shadow: 0 0 15px #00ff88; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }
        #chat { display: none; height: 300px; overflow-y: auto; flex-direction: column; }
        .msg { padding: 10px 15px; border-radius: 15px; margin-bottom: 10px; font-size: 0.9rem; }
        .You { align-self: flex-end; background: #007bff; }
        .Target { align-self: flex-start; background: rgba(255,255,255,0.1); }
        textarea { width: 100%; background: rgba(255,255,255,0.05); color: white; border: none; padding: 15px; border-radius: 12px; resize: none; box-sizing: border-box; }
        .send-btn { width: 100%; background: #007bff; color: white; border: none; padding: 15px; border-radius: 12px; margin-top: 10px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="bg-container"></div>
    <div class="card">
        <div class="greetings">
            <span class="avatar">🐱‍👤</span>
            <div style="font-size: 1.2rem; font-weight: bold;">Hi Rishan!</div>
            <div class="host-info">POD: {{ host }}</div>
        </div>

        <div class="header" onclick="handleAction()">
            <div style="display: flex; align-items: center;">
                <span id="status-dot" class="dot">●</span> 
                <div>
                    <div id="status-txt" style="font-size: 0.8rem; font-weight: 800;">IDLE</div>
                    <div id="last-seen" style="font-size: 0.6rem; opacity: 0.5;"></div>
                </div>
            </div>
            <div>🔒</div>
        </div>
        <div id="chat"></div>
        <form action="/send" method="post">
            <textarea name="msg" placeholder="Write to Rishan..." required rows="2"></textarea>
            <button type="submit" class="send-btn">SEND MESSAGE</button>
        </form>
    </div>
    <script>
        let isRevealed = false, taps = 0, timer;
        async function updateData() {
            try {
                const res = await fetch('/api/data');
                const d = await res.json();
                document.getElementById('status-txt').innerText = d.online ? 'ONLINE' : 'IDLE';
                document.getElementById('last-seen').innerText = 'Last: ' + d.last_seen;
                document.getElementById('status-dot').className = d.online ? 'dot online-active' : 'dot';
                
                const win = document.getElementById('chat');
                let h = '';
                d.history.slice().reverse().forEach(m => {
                    const t = isRevealed ? atob(m.text) : '••••••••';
                    h += `<div class="msg ${m.sender}">${t}</div>`;
                });
                win.innerHTML = h;
            } catch(e){}
        }
        function handleAction() {
            taps++; clearTimeout(timer);
            timer = setTimeout(() => {
                if (taps === 2) { isRevealed = true; document.getElementById('chat').style.display = 'flex'; updateData(); }
                else if (taps === 1 && isRevealed) { isRevealed = false; document.getElementById('chat').style.display = 'none'; }
                taps = 0;
            }, 300);
        }
        setInterval(updateData, 5000);
        updateData();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    if not session.get('auth'): return render_template_string(LOGIN_HTML)
    return render_template_string(DASH_HTML, host=HOSTNAME)

@app.route('/api/data')
def api_data():
    if not session.get('auth'): return jsonify({"error": "unauthorized"}), 401
    return jsonify(cache)

@app.route('/login', methods=['POST'])
def login():
    if request.form.get('p') == WEB_PIN: session['auth'] = True
    return redirect(url_for('home'))

@app.route('/send', methods=['POST'])
def send():
    if session.get('auth') and request.form.get('msg'):
        msg = request.form.get('msg')
        def run():
            l = asyncio.new_event_loop()
            asyncio.set_event_loop(l)
            c = TelegramClient(SESSION_NAME, API_ID, API_HASH, loop=l)
            l.run_until_complete(c.connect())
            l.run_until_complete(c.send_message(COURIER_ID, msg))
            c.disconnect()
            l.close()
        threading.Thread(target=run, daemon=True).start()
    return redirect(url_for('home'))

LOGIN_HTML = """
<body style="background:#000; color:white; display:flex; justify-content:center; align-items:center; height:100vh; font-family:sans-serif;">
    <form action="/login" method="post" style="text-align:center;">
        <input type="password" name="p" placeholder="PIN" style="padding:10px; border-radius:5px; border:none;">
        <button type="submit" style="padding:10px; background:#007bff; color:white; border:none; border-radius:5px;">ENTER</button>
    </form>
</body>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
