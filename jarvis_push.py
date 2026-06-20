#!/usr/bin/env python3
"""
JARVIS JIA — Agent Data Push Utility
Call this from the agent to update dashboard data in real-time.

Usage:
    python3 jarvis_push.py update sentiment_index value=55.2 change=-3.1 direction=down
    python3 jarvis_push.py alert critical "🚨" "Isu baru dikesan" "Ambil tindakan"
    python3 jarvis_push.py feed "10:05:00" "Isu baru trending" "Bot Detection" critical
    python3 jarvis_push.py full '{"sentiment_index": {"value": 55.2}}'
"""
import json
import sys
import asyncio

WS_URL = "ws://localhost:8765"

async def send_to_bridge(data):
    try:
        import websockets
        async with websockets.connect(WS_URL) as ws:
            await ws.send(json.dumps(data))
            # Wait for response
            response = await asyncio.wait_for(ws.recv(), timeout=3)
            print(response)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  jarvis_push.py full <json_data>")
        print("  jarvis_push.py update <section> <key=value> ...")
        print("  jarvis_push.py alert <type> <icon> <message> [action]")
        print("  jarvis_push.py feed <time> <text> <tag> [critical|warning]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "full":
        data = json.loads(sys.argv[2])
        asyncio.run(send_to_bridge({"type": "update_full", "data": data}))

    elif cmd == "alert":
        alert_type = sys.argv[2]
        icon = sys.argv[3]
        message = sys.argv[4]
        action = sys.argv[5] if len(sys.argv) > 5 else ""
        asyncio.run(send_to_bridge({
            "type": "push_alert",
            "data": {"type": alert_type, "icon": icon, "message": message, "action": action}
        }))

    elif cmd == "feed":
        time_str = sys.argv[2]
        text = sys.argv[3]
        tag = sys.argv[4]
        flags = sys.argv[5] if len(sys.argv) > 5 else ""
        entry = {"time": time_str, "text": text, "tag": tag}
        if "critical" in flags:
            entry["critical"] = True
        if "warning" in flags:
            entry["warning"] = True
        asyncio.run(send_to_bridge({
            "type": "push_feed",
            "data": entry
        }))

    elif cmd == "update":
        section = sys.argv[2]
        data = {}
        for arg in sys.argv[3:]:
            if "=" in arg:
                k, v = arg.split("=", 1)
                # Try to parse as number
                try:
                    if "." in v:
                        v = float(v)
                    else:
                        v = int(v)
                except ValueError:
                    pass
                data[k] = v
        asyncio.run(send_to_bridge({
            "type": "update_section",
            "section": section,
            "data": data
        }))
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
