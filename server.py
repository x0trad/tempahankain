#!/usr/bin/env python3
"""
JARVIS JIA — Dashboard + Bridge Server
Serves the dashboard + WebSocket bridge on a single port.
"""
import json, os, re, sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
import asyncio
import websockets
import threading
from datetime import datetime

HOST = "0.0.0.0"
HTTP_PORT = 8080
WS_PORT = 8765

# ================================================================
# Dashboard State
# ================================================================
CURRENT_STATE = {
    "sentiment_index": {"value": 43.2, "change": -5.8, "direction": "down"},
    "mentions_24h": {"value": 247800, "change": 12.3, "spike": True},
    "hot_zones": {"value": 14, "change": 3, "critical": 2},
    "public_trust": {"value": 61.7, "change": -2.1, "direction": "down"},
    "crisis": {"title": "Isu Subsidi B45", "details": "50k+ reach detected · War Plan auto-generated"},
    "alerts": [
        {"type":"critical","icon":"🚨","message":"Isu B45 Trending #1 — 87K sebutan dalam 4 jam","action":"Counter Narrative Generator aktif"},
        {"type":"warning","icon":"⚠️","message":"VIP Alert: @nurulizzah Live — Bincang isu pendidikan","action":"Auto-suggest: Hantar talking point Pendidikan 2026"}
    ],
    "feed": [
        {"time":"10:02:47","text":"Isu B45 — Naratif 'rakyat terbeban' menang 68%","tag":"Narrative Tracking","critical":True},
        {"time":"10:01:12","text":"Bot Attack Pattern Detected — 1,247 akaun baru aktif","tag":"Bot Detection","warning":True},
        {"time":"09:58:30","text":"@chegubard — Post video mengenai isu subsidi. Reach 12K","tag":"VIP Watchlist"},
        {"time":"09:55:00","text":"Taman Sri Muda — Aduan sampah tidak dikutip 5 hari","tag":"Isu Kawasan"},
        {"time":"09:50:22","text":"Daily Briefing 10AM — Auto push ke semua YB","tag":"System"}
    ],
    "hot_issues": [
        {"issue":"Isu B45 / Subsidi","mentions":"87.2K","sentiment":"-8%","trend":"critical"},
        {"issue":"Pendidikan 2026","mentions":"34.1K","sentiment":"-2%","trend":"elevated"},
        {"issue":"Banjir Pantai Timur","mentions":"28.5K","sentiment":"-12%","trend":"critical"},
        {"issue":"Kos Sara & Gaji","mentions":"22.3K","sentiment":"-5%","trend":"elevated"},
        {"issue":"PRK Dun Gana","mentions":"15.7K","sentiment":"+3%","trend":"stable"}
    ],
    "influencers": [
        {"name":"@ishamjalil","reach":"142K","lean":"attack"},
        {"name":"@nurulizzah (Live)","reach":"87K","lean":"defend"},
        {"name":"@chegubard","reach":"65K","lean":"attack"},
        {"name":"Portal Kini","reach":"52K","lean":"neutral"},
        {"name":"Edisi Siasat","reach":"41K","lean":"attack"},
        {"name":"Malaysia Gazette","reach":"38K","lean":"neutral"}
    ],
    "narratives": [
        {"name":"Rakyat Terbeban B45","share":68,"momentum":"rising","action":"counter"},
        {"name":"Subsidi Tepat Sasaran","share":22,"momentum":"steady","action":"defend"},
        {"name":"Reformasi Pendidikan","share":10,"momentum":"rising","action":"monitor"}
    ],
    "scenario": {"peak":"18-24 hours","reach":"250K-400K","influencer_wave":"Expected 6 hours","timeline_progress":15},
    "network_stats": {"attack":{"count":14,"reach":"340K"},"defend":{"count":8,"reach":"195K"},"bot":{"clusters":3}},
    "war_plan": {
        "day0":"Issue official statement · Activate defend network · Brief YB",
        "day1":"Launch counter-narrative campaign · Media briefing",
        "day2":"Fact-check articles · Parlimen Q&A prep · Community engagement",
        "day3_5":"Monitor shift · Adjust narrative · Deploy second wave",
        "day6_7":"Post-mortem · Report generation · Strategy review"
    },
    "last_updated": datetime.now().isoformat()
}

# ================================================================
# WebSocket Clients
# ================================================================
dashboard_clients = set()

async def safe_send(ws, msg):
    try:
        await ws.send(msg)
    except:
        dashboard_clients.discard(ws)

async def broadcast_full_state():
    if not dashboard_clients:
        return
    msg = json.dumps({"type": "full_state", "data": CURRENT_STATE})
    for client in dashboard_clients.copy():
        await safe_send(client, msg)

# ================================================================
# WebSocket Handler
# ================================================================
async def ws_handler(websocket):
    dashboard_clients.add(websocket)
    print(f"[WS] Dashboard client connected. Total: {len(dashboard_clients)}")
    try:
        await websocket.send(json.dumps({"type": "full_state", "data": CURRENT_STATE}))
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get("type", "")
                if msg_type == "ping":
                    await websocket.send(json.dumps({"type": "pong"}))
                elif msg_type == "update_full":
                    CURRENT_STATE.update(data.get("data", {}))
                    CURRENT_STATE["last_updated"] = datetime.now().isoformat()
                    await broadcast_full_state()
                elif msg_type == "update_section":
                    section = data.get("section", "")
                    sd = data.get("data", {})
                    if section in CURRENT_STATE and isinstance(CURRENT_STATE[section], dict):
                        CURRENT_STATE[section].update(sd)
                    else:
                        CURRENT_STATE[section] = sd
                    CURRENT_STATE["last_updated"] = datetime.now().isoformat()
                    await broadcast_full_state()
                elif msg_type == "push_alert":
                    a = data.get("data", {})
                    CURRENT_STATE["alerts"].insert(0, a)
                    if len(CURRENT_STATE["alerts"]) > 10:
                        CURRENT_STATE["alerts"].pop()
                    CURRENT_STATE["last_updated"] = datetime.now().isoformat()
                    await broadcast_full_state()
                elif msg_type == "push_feed":
                    e = data.get("data", {})
                    CURRENT_STATE["feed"].insert(0, e)
                    if len(CURRENT_STATE["feed"]) > 20:
                        CURRENT_STATE["feed"].pop()
                    CURRENT_STATE["last_updated"] = datetime.now().isoformat()
                    await broadcast_full_state()
                elif msg_type == "ask_jarvis":
                    query = data.get("query", "")
                    print(f"\n[JARVIS QUERY] {query}")
                    print("[JARVIS REPLY] ", end="", flush=True)
                    await websocket.send(json.dumps({
                        "type": "jarvis_thinking",
                        "message": "🧠 Kirra sedang menganalisis..."
                    }))
                elif msg_type == "request_refresh":
                    await websocket.send(json.dumps({"type": "full_state", "data": CURRENT_STATE}))
            except json.JSONDecodeError:
                pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        dashboard_clients.discard(websocket)
        print(f"[WS] Dashboard client disconnected. Total: {len(dashboard_clients)}")

# ================================================================
# Agent Push API (called from this same process or externally)
# ================================================================
def update_dashboard(section, data):
    if section == "full":
        CURRENT_STATE.update(data)
    elif section in CURRENT_STATE:
        CURRENT_STATE[section].update(data)
    else:
        CURRENT_STATE[section] = data
    CURRENT_STATE["last_updated"] = datetime.now().isoformat()
    if dashboard_clients:
        msg = json.dumps({
            "type": "state_update",
            "section": section if section != "full" else None,
            "data": CURRENT_STATE if section == "full" else CURRENT_STATE[section],
            "full_state": CURRENT_STATE
        })
        for client in dashboard_clients.copy():
            asyncio.ensure_future(safe_send(client, msg))
    print(f"[AGENT] Dashboard updated: {section}")

def push_alert(alert_type, icon, message, action=""):
    alert = {"type": alert_type, "icon": icon, "message": message, "action": action}
    CURRENT_STATE["alerts"].insert(0, alert)
    if len(CURRENT_STATE["alerts"]) > 10:
        CURRENT_STATE["alerts"].pop()
    CURRENT_STATE["last_updated"] = datetime.now().isoformat()
    if dashboard_clients:
        msg = json.dumps({"type": "new_alert", "data": alert, "full_state": CURRENT_STATE})
        for client in dashboard_clients.copy():
            asyncio.ensure_future(safe_send(client, msg))

def push_feed_entry(time_str, text, tag="", critical=False, warning=False):
    entry = {"time": time_str, "text": text, "tag": tag, "critical": critical, "warning": warning}
    CURRENT_STATE["feed"].insert(0, entry)
    if len(CURRENT_STATE["feed"]) > 20:
        CURRENT_STATE["feed"].pop()
    CURRENT_STATE["last_updated"] = datetime.now().isoformat()
    if dashboard_clients:
        msg = json.dumps({"type": "new_feed_entry", "data": entry, "full_state": CURRENT_STATE})
        for client in dashboard_clients.copy():
            asyncio.ensure_future(safe_send(client, msg))

# ================================================================
# HTTP Server (serves static files + WS injector)
# ================================================================
class JarvisHTTPHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)
    def log_message(self, format, *args):
        pass

def start_http():
    server = HTTPServer((HOST, HTTP_PORT), JarvisHTTPHandler)
    print(f"[HTTP] Server started on http://{HOST}:{HTTP_PORT}")
    server.serve_forever()

# ================================================================
# MAIN
# ================================================================
async def main():
    # Start HTTP in a thread
    t = threading.Thread(target=start_http, daemon=True)
    t.start()
    await asyncio.sleep(0.5)
    
    # Start WebSocket
    ws_server = await websockets.serve(ws_handler, HOST, WS_PORT)
    print(f"[WS] Server started on ws://{HOST}:{WS_PORT}")
    print(f"\n{'='*60}")
    print(f"  JARVIS JIA — Agent Bridge Server")
    print(f"{'='*60}")
    print(f"\n  Dashboard:   http://{HOST}:{HTTP_PORT}")
    print(f"  WebSocket:   ws://{HOST}:{WS_PORT}")
    print(f"\n  To update data from agent:")
    print(f"    update_dashboard('section', {{'key': 'value'}})")
    print(f"    push_alert('critical', '🚨', 'message', 'action')")
    print(f"    push_feed_entry('time', 'text', 'tag')")
    print(f"{'='*60}\n")
    print("[JARVIS] Waiting for dashboard connections...")
    print("[JARVIS] Ready for agent data pushes.")
    
    await ws_server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
