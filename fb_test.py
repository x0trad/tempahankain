import json, urllib.request

with open('/root/jarvis-jia-dashboard/.fb_token') as f:
    TOKEN = f.read().strip()

# Test 1: verify token
print("=== Token Check ===")
url = f"https://graph.facebook.com/v18.0/me?access_token={TOKEN}"
try:
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read())
        print(f"User: {data.get('name','?')} | ID: {data.get('id','?')}")
except urllib.error.HTTPError as e:
    err = e.read().decode()
    print(f"HTTP {e.code}: {err}")

# Test 2: try known politician pages by ID
known_pages = {
    "Anwar Ibrahim": "122467757813274",
    "DAP Malaysia": "132215626820089",
    "PAS Malaysia": "143664575702950",
    "Hannah Yeoh": "121854814620705",
    "Syed Saddiq": "100047907953540",
}

print("\n=== Page Lookup ===")
for name, page_id in known_pages.items():
    url = f"https://graph.facebook.com/v18.0/{page_id}?fields=name,fan_count,followers_count&access_token={TOKEN}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
        print(f"[OK] {data.get('name','?')} | Followers: {data.get('followers_count','?')} | Fans: {data.get('fan_count','?')}")
    except Exception as e:
        err_msg = str(e)
        if hasattr(e, 'read'):
            try:
                err_data = json.loads(e.read())
                err_msg = err_data.get('error',{}).get('message','?')
            except:
                pass
        print(f"[FAIL] {name}: {err_msg}")

# Test 3: get latest posts from a page
print("\n=== Latest Posts (Anwar Ibrahim) ===")
url = f"https://graph.facebook.com/v18.0/122467757813274/posts?fields=message,created_time,permalink_url,reactions.summary(total_count),comments.summary(total_count)&limit=3&access_token={TOKEN}"
try:
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read())
    for post in data.get('data', []):
        msg = post.get('message','')[:80]
        reactions = post.get('reactions',{}).get('summary',{}).get('total_count',0)
        comments = post.get('comments',{}).get('summary',{}).get('total_count',0)
        print(f"  [{post.get('created_time','')[:16]}] {msg}...")
        print(f"    Reactions: {reactions} | Comments: {comments}")
        print(f"    URL: {post.get('permalink_url','')}")
except Exception as e:
    err_msg = str(e)
    if hasattr(e, 'read'):
        try:
            err_data = json.loads(e.read())
            err_msg = err_data.get('error',{}).get('message','?')
        except:
            pass
    print(f"FAIL: {err_msg}")
