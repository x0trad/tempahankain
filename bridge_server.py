#!/usr/bin/env python3
"""
JARVIS JIA Bridge Server
- WebSocket server on port 8765 (for live dashboard pushes)
- HTTP server on port 8081 (for agent/scraper to push data updates)
- Serves news cache via POST /api/news and GET /api/news
- Broadcasts state updates to all connected dashboard WebSocket clients
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import hashlib

# Try importing websockets
try:
    import websockets
except ImportError:
    print("[BRIDGE] Installing websockets...")
    os.system(f"{sys.executable} -m pip install websockets 2>/dev/null")
    import websockets

# --- State ---
dashboard_state = {
    "sentiment_index": {"value": 43.2, "change": 5.8, "direction": "down"},
    "mentions_24h": {"value": 247800, "change": 12.3, "spike": True},
    "hot_zones": {"value": 14, "change": 3, "critical": 2},
    "public_trust": {"value": 61.7, "change": 2.1, "direction": "down"},
    "crisis": {"title": "Isu Subsidi B45", "details": "50k+ reach detected · War Plan auto-generated"},
    "alerts": [
        {"type": "critical", "icon": "🚨", "message": "Isu B45 Trending #1 — 87K sebutan dalam 4 jam"},
        {"type": "warning", "icon": "⚠️", "message": "VIP Alert: @nurulizzah Live Sekarang — 4.2K viewers"},
    ],
    "feed": [
        {"time": "10:02:47", "text": "Isu B45 — Naratif 'rakyat terbeban' menang 68%", "tag": "Narrative Tracking", "critical": True},
        {"time": "10:01:12", "text": "Bot Attack Pattern Detected — 1,247 akaun baru aktif", "tag": "Bot Detection", "warning": True},
    ],
    "hot_issues": [
        {"issue": "Isu B45 / Subsidi", "mentions": "87.2K", "sentiment": "-8%", "trend": "critical"},
        {"issue": "Pendidikan 2026", "mentions": "34.1K", "sentiment": "-2%", "trend": "elevated"},
    ],
    "influencers": [
        {"name": "@ishamjalil", "reach": "142K", "lean": "attack"},
        {"name": "@nurulizzah", "reach": "87K", "lean": "defend"},
    ],
    "narratives": [
        {"name": "Rakyat Terbeban B45", "share": 68, "momentum": "rising", "action": "counter"},
        {"name": "Subsidi Tepat Sasaran", "share": 22, "momentum": "steady", "action": "defend"},
    ],
    "news": []  # News articles from scraper
}

connected_clients = set()
MAX_NEWS = 50


# --- WebSocket Handler ---
async def ws_handler(websocket):
    connected_clients.add(websocket)
    print(f"[BRIDGE] WebSocket client connected ({len(connected_clients)} total)")
    
    # Send current full state on connect
    try:
        await websocket.send(json.dumps({"type": "full_state", "full_state": dashboard_state}))
    except:
        pass
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                
                # Handle agent state updates
                if data.get("type") in ("state_update", "full_state"):
                    if "data" in data:
                        for key, val in data["data"].items():
                            if val is not None and key in dashboard_state:
                                dashboard_state[key] = val
                    elif "full_state" in data:
                        for key, val in data["full_state"].items():
                            if val is not None:
                                dashboard_state[key] = val
                    
                    # Broadcast to all clients
                    msg = json.dumps({"type": "state_update", "data": dashboard_state})
                    await broadcast(msg)
                
                # Handle Jarvis queries
                elif data.get("type") == "ask_jarvis":
                    query = data.get("query", "")
                    print(f"[BRIDGE] Jarvis query: {query}")
                    await websocket.send(json.dumps({
                        "type": "jarvis_thinking",
                        "message": f"Menganalisis soalan anda tentang '{query}'..."
                    }))
                    await asyncio.sleep(1)
                    await websocket.send(json.dumps({
                        "type": "jarvis_reply",
                        "message": f"🧠 **Analisis untuk:** \"{query}\"\n\nMaaf, modul DeepSeek AI belum disambung lagi. Saya akan aktifkan bila boss ready. Buat masa ni saya boleh bantu update data dashboard atau fetch news terkini."
                    }))
                
                # Handle news broadcast request
                elif data.get("type") == "news_update":
                    articles = data.get("articles", [])
                    for a in articles:
                        a["id"] = hashlib.md5((a.get("title","") + a.get("link","")).encode()).hexdigest()[:12]
                    
                    # Merge into state
                    existing_ids = {n.get("id") for n in dashboard_state["news"]}
                    for a in articles:
                        if a.get("id") not in existing_ids:
                            dashboard_state["news"].append(a)
                            existing_ids.add(a.get("id"))
                    
                    # Sort by date, keep MAX_NEWS
                    dashboard_state["news"].sort(key=lambda x: x.get("date", ""), reverse=True)
                    dashboard_state["news"] = dashboard_state["news"][:MAX_NEWS]
                    
                    await broadcast(json.dumps({
                        "type": "state_update",
                        "data": {"news": dashboard_state["news"]}
                    }))
                    
            except json.JSONDecodeError:
                pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.discard(websocket)
        print(f"[BRIDGE] WebSocket client disconnected ({len(connected_clients)} remaining)")


async def broadcast(message):
    """Send message to all connected WebSocket clients."""
    if not connected_clients:
        return
    await asyncio.gather(
        *[client.send(message) for client in connected_clients.copy()],
        return_exceptions=True
    )


# --- HTTP Handler (for agent/scraper push) ---
class BridgeHTTPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        
        try:
            data = json.loads(body)
        except:
            self.send_error(400, "Invalid JSON")
            return
        
        if parsed.path == "/api/news":
            # Accept news push
            articles = data.get("articles", [])
            source = data.get("source", "unknown")
            
            for a in articles:
                a["id"] = hashlib.md5((a.get("title","") + a.get("link","")).encode()).hexdigest()[:12]
            
            existing_ids = {n.get("id") for n in dashboard_state["news"]}
            for a in articles:
                if a.get("id") not in existing_ids:
                    dashboard_state["news"].append(a)
                    existing_ids.add(a.get("id"))
            
            dashboard_state["news"].sort(key=lambda x: x.get("date", ""), reverse=True)
            dashboard_state["news"] = dashboard_state["news"][:MAX_NEWS]
            
            # Broadcast to WS clients
            asyncio.run_coroutine_threadsafe(
                broadcast(json.dumps({
                    "type": "state_update",
                    "data": {"news": dashboard_state["news"]}
                })),
                loop
            )
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "count": len(articles)}).encode())
            
        elif parsed.path == "/api/state":
            # Full state update
            update = data.get("data", data)
            for key, val in update.items():
                if val is not None and key in dashboard_state:
                    dashboard_state[key] = val
            
            asyncio.run_coroutine_threadsafe(
                broadcast(json.dumps({"type": "state_update", "data": dashboard_state})),
                loop
            )
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_error(404)
    
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == "/api/news":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "articles": dashboard_state["news"],
                "count": len(dashboard_state["news"]),
                "last_fetch": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            }).encode())
        
        elif parsed.path == "/api/state":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(dashboard_state).encode())
        
        elif parsed.path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "online",
                "ws_clients": len(connected_clients),
                "news_count": len(dashboard_state["news"]),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }).encode())
        
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        print(f"[BRIDGE-HTTP] {args[0]} {args[1]} {args[2]}")


async def run_ws_server():
    """Run WebSocket server."""
    async with websockets.serve(ws_handler, "0.0.0.0", 8765):
        print("[BRIDGE] WebSocket server ready on ws://0.0.0.0:8765")
        await asyncio.Future()  # run forever


def run_http_server(loop_ref):
    """Run HTTP server in a separate thread."""
    global loop
    loop = loop_ref
    server = HTTPServer(("0.0.0.0", 8081), BridgeHTTPHandler)
    print("[BRIDGE] HTTP server running on http://0.0.0.0:8081")
    server.serve_forever()


# --- Main ---
if __name__ == "__main__":
    import threading

    print("=" * 50)
    print("  JARVIS JIA BRIDGE SERVER v2.0")
    print("  WebSocket : ws://0.0.0.0:8765")
    print("  HTTP API  : http://0.0.0.0:8081")
    print("=" * 50)

    # Get or create event loop
    global loop
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Start HTTP server in separate thread
    http_thread = threading.Thread(target=run_http_server, args=(loop,), daemon=True)
    http_thread.start()

    # Run WebSocket server
    try:
        loop.run_until_complete(run_ws_server())
    except KeyboardInterrupt:
        print("\n[BRIDGE] Shutting down...")
    finally:
        loop.close()
