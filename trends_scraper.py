#!/usr/bin/env python3
"""
JARVIS Multi-Source Scraper — Google Trends + YouTube + Twitter/X
Scrapes trending data without official APIs.
"""
import json, hashlib, re, time
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.parse import quote

CACHE_FILE = Path(__file__).parent / "trends_cache.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0"

def fetch_url(url, timeout=15):
    req = Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/json,application/xml,*/*"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")

# ============================================================
# 1. GOOGLE TRENDS — Malaysia (RSS feed, no API needed)
# ============================================================
def scrape_google_trends():
    """Scrape Google Trends RSS for Malaysia."""
    try:
        raw = fetch_url("https://trends.google.com/trending/rss?geo=MY", timeout=15)
        import feedparser
        feed = feedparser.parse(raw)
        trends = []
        for entry in feed.entries[:20]:
            # Extract traffic/traffic volume if available
            traffic = ""
            if hasattr(entry, 'ht_approx_traffic'):
                traffic = entry.ht_approx_traffic
            trends.append({
                "rank": len(trends) + 1,
                "title": entry.title.strip() if hasattr(entry, 'title') else "Unknown",
                "traffic": traffic,
                "url": entry.link if hasattr(entry, 'link') else "",
                "published": time.strftime("%Y-%m-%d %H:%M", entry.published_parsed) if hasattr(entry, 'published_parsed') and entry.published_parsed else "",
                "source": "Google Trends MY"
            })
        return trends, None
    except Exception as e:
        return [], str(e)

# ============================================================
# 2. YOUTUBE — Trending Malaysia + Politician Channels (RSS)
# ============================================================
# Key Malaysian political YouTube channels
YOUTUBE_CHANNELS = [
    {"name": "MalaysiaKini", "channel_id": "UCvU1OHq6k4j5z3z5z5z5z5z"},
    {"name": "Astro Awani", "channel_id": "UCk1nQ7m2e2e2e2e2e2e2e2"},
    {"name": "Bernama TV", "channel_id": "UCj1j1j1j1j1j1j1j1j1j1j"},
]

def scrape_youtube_trending():
    """Scrape YouTube trending for Malaysia via Invidious API."""
    videos = []
    # Try multiple Invidious instances
    invidious_instances = [
        "https://invidious.fdn.fr/api/v1/trending?region=MY&limit=15",
        "https://yewtu.be/api/v1/trending?region=MY&limit=15",
        "https://invidious.nerdvpn.de/api/v1/trending?region=MY&limit=15",
    ]
    for api_url in invidious_instances:
        try:
            raw = fetch_url(api_url, timeout=15)
            data = json.loads(raw)
            if isinstance(data, list) and data:
                for v in data:
                    views = v.get("viewCount", 0) or 0
                    videos.append({
                        "title": v.get("title", ""),
                        "channel": v.get("author", ""),
                        "views": views,
                        "published": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
                        "url": f"https://www.youtube.com/watch?v={v.get('videoId','')}",
                        "duration": v.get("lengthSeconds", 0),
                        "source": "YouTube MY"
                    })
                return videos, None
        except:
            continue
    # Fallback: scrape YouTube RSS for known political channels
    try:
        political_channels = [
            {"name": "MalaysiaKini", "id": "UCvU1OHq6k4j5z3z5z5z5z5z"},
            {"name": "Astro Awani", "id": "UCk1nQ7m2e2e2e2e2e2e2e2"},
        ]
        for ch in political_channels:
            raw = fetch_url(f"https://www.youtube.com/feeds/videos.xml?channel_id={ch['id']}", timeout=10)
            import feedparser
            feed = feedparser.parse(raw)
            for entry in feed.entries[:3]:
                videos.append({
                    "title": entry.title if hasattr(entry, 'title') else "",
                    "channel": ch["name"],
                    "views": 0,
                    "published": time.strftime("%Y-%m-%d %H:%M", entry.published_parsed) if hasattr(entry, 'published_parsed') and entry.published_parsed else "",
                    "url": entry.link if hasattr(entry, 'link') else "",
                    "source": "YouTube Channel"
                })
        if videos:
            return videos, None
    except Exception as e:
        return [], str(e)
    return [], "All YouTube sources failed"

# ============================================================
# 3. TWITTER/X — via Nitter instances (no API needed)
# ============================================================
NITTER_INSTANCES = [
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.woodland.cafe",
]

# Malaysian political accounts to monitor
TWITTER_ACCOUNTS = [
    "@anwaribrahim", "@nurulizzah", "@rafiziramli", "@ishaamjalil",
    "@limkianeng", "@hannahyeoh", "@msabu_official", "@syedsaddiq",
    "@muhyiddinyassin", "@drwanazizah", "@fahmifadzil",
    "@TonyPua", "@hannahyeoh", "@SaifuddinNas", "@AzminAli",
]

def scrape_twitter_nitter():
    """Scrape latest tweets from Malaysian politicians via Nitter."""
    tweets = []
    errors = []
    
    for account in TWITTER_ACCOUNTS[:8]:  # Limit to 8 accounts per run
        username = account.replace("@", "")
        fetched = False
        for instance in NITTER_INSTANCES:
            try:
                url = f"{instance}/{username}"
                raw = fetch_url(url, timeout=10)
                # Parse Nitter HTML for tweet content
                # Look for tweet elements
                tweet_matches = re.findall(r'class="tweet-content[^"]*"[^>]*>(.*?)</div>', raw, re.DOTALL)
                if not tweet_matches:
                    # Try alternative pattern
                    tweet_matches = re.findall(r'class="tweet-text[^"]*"[^>]*>(.*?)</div>', raw, re.DOTALL)
                
                for match in tweet_matches[:2]:  # Get latest 2 tweets per account
                    # Clean HTML
                    text = re.sub(r'<[^>]+>', '', match).strip()
                    text = re.sub(r'\s+', ' ', text)
                    if text:
                        tweets.append({
                            "account": account,
                            "text": text[:200],
                            "url": f"https://x.com/{username}",
                            "published": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
                            "source": "Twitter/X",
                            "id": hashlib.md5((account + text[:50]).encode()).hexdigest()[:12]
                        })
                if tweet_matches:
                    fetched = True
                    break
            except:
                continue
        
        if not fetched:
            errors.append(f"{account}: all Nitter instances failed")
    
    return tweets, errors if errors else None

# ============================================================
# MAIN
# ============================================================
def run():
    cache = {"trends": [], "youtube": [], "twitter": [], "last_fetch": None}
    
    print("=" * 60)
    print("  JARVIS Multi-Source Scraper")
    print("=" * 60)
    
    # 1. Google Trends
    print("\n📊 Scraping Google Trends Malaysia...")
    trends, err = scrape_google_trends()
    if trends:
        cache["trends"] = trends
        print(f"  ✓ {len(trends)} trending topics")
        for t in trends[:5]:
            print(f"    #{t['rank']}: {t['title']} ({t.get('traffic','')})")
    else:
        print(f"  ✗ Failed: {err}")
    
    # 2. YouTube Trending
    print("\n▶️ Scraping YouTube Malaysia Trending...")
    videos, err = scrape_youtube_trending()
    if videos:
        cache["youtube"] = videos
        print(f"  ✓ {len(videos)} trending videos")
        for v in videos[:5]:
            views = v.get('views', 0)
            views_str = f"{views//1000}K" if views >= 1000 else str(views)
            print(f"    [{views_str} views] {v['channel']}: {v['title'][:50]}")
    else:
        print(f"  ✗ Failed: {err}")
    
    # 3. Twitter/X
    print("\n🐦 Scraping Twitter/X (Nitter)...")
    tweets, err = scrape_twitter_nitter()
    if tweets:
        cache["twitter"] = tweets
        print(f"  ✓ {len(tweets)} tweets from politicians")
        for t in tweets[:5]:
            print(f"    {t['account']}: {t['text'][:60]}")
    else:
        print(f"  ✗ Failed: {err}")
    
    cache["last_fetch"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    
    # Save cache
    CACHE_FILE.write_text(json.dumps(cache, indent=2))
    print(f"\n✅ Cache saved: {CACHE_FILE}")
    print(f"   Trends: {len(cache['trends'])} | YouTube: {len(cache['youtube'])} | Twitter: {len(cache['twitter'])}")

if __name__ == "__main__":
    run()
