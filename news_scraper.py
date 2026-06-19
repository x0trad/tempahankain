#!/usr/bin/env python3
"""
JARVIS News Scraper — RSS feed fetcher for Malaysian news hubs.
Fetches news from multiple sources every 4 hours, caches to JSON,
and pushes to dashboard via bridge server HTTP endpoint.
"""

import json
import os
import time
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

NEWS_SOURCES = [
    {
        "name": "Malaysiakini",
        "rss": "https://www.malaysiakini.com/news/feed",
        "lang": "ms",
        "icon": "📰"
    },
    {
        "name": "Malay Mail",
        "rss": "https://www.malaymail.com/feed/rss",
        "lang": "en",
        "icon": "📬"
    },
    {
        "name": "Free Malaysia Today",
        "rss": "https://www.freemalaysiatoday.com/feed/",
        "lang": "en",
        "icon": "📢"
    },
    {
        "name": "Astro Awani",
        "rss": "https://www.astroawani.com/rss/news.xml",
        "lang": "ms",
        "icon": "📡"
    },
    {
        "name": "Berita Harian",
        "rss": "https://www.bharian.com.my/rss/news.xml",
        "lang": "ms",
        "icon": "📰"
    },
    {
        "name": "Sinar Harian",
        "rss": "https://www.sinarharian.com.my/rss/berita-semasa",
        "lang": "ms",
        "icon": "☀️"
    },
    {
        "name": "The Star",
        "rss": "https://www.thestar.com.my/rss/top-news",
        "lang": "en",
        "icon": "⭐"
    },
    {
        "name": "Malaysia Now",
        "rss": "https://www.malaysianow.com/feed",
        "lang": "en",
        "icon": "📰"
    },
    {
        "name": "The Vibes",
        "rss": "https://www.thevibes.com/feed",
        "lang": "en",
        "icon": "🎵"
    },
    {
        "name": "Roketkini",
        "rss": "https://roketkini.com/feed/",
        "lang": "ms",
        "icon": "🚀"
    },
    {
        "name": "Malaysia Dateline",
        "rss": "https://malaysiadateline.com/feed/",
        "lang": "ms",
        "icon": "📰"
    },
    {
        "name": "The Malaysian Reserve",
        "rss": "https://themalaysianreserve.com/feed/",
        "lang": "en",
        "icon": "📊"
    },
    {
        "name": "Twentytwo13",
        "rss": "https://www.twentytwo13.my/feed/",
        "lang": "en",
        "icon": "🔢"
    },
    {
        "name": "Selangorkini",
        "rss": "https://selangorkini.my/feed/",
        "lang": "ms",
        "icon": "🌊"
    }
]

CACHE_FILE = Path(__file__).parent / "news_cache.json"
BRIDGE_URL = "http://localhost:8081/api/news"
MAX_ARTICLES = 50  # max articles to keep total
MAX_PER_SOURCE = 8  # max per source per fetch

USER_AGENT = "JARVIS-JIA/1.0 (AI Command Center; +https://jarvis-jia.local)"


def fetch_rss(url, timeout=15):
    """Fetch and parse RSS feed using raw XML/feedparser."""
    try:
        import feedparser
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
        feed = feedparser.parse(raw)
        
        articles = []
        for entry in feed.entries[:MAX_PER_SOURCE]:
            pub_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = time.strftime("%Y-%m-%d %H:%M:%S", entry.published_parsed)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                pub_date = time.strftime("%Y-%m-%d %H:%M:%S", entry.updated_parsed)
            
            # Get summary/description
            summary = ""
            if hasattr(entry, 'summary'):
                summary = entry.summary
            elif hasattr(entry, 'description'):
                summary = entry.description
            # Strip HTML tags
            summary = summary.replace('<p>', '').replace('</p>', '\n').replace('<br>', '\n').replace('<br/>', '\n')
            summary = summary.split('<')[0] if '<' in summary else summary
            summary = summary[:200].strip()
            
            link = entry.link if hasattr(entry, 'link') else ""
            
            articles.append({
                "title": entry.title.strip() if hasattr(entry, 'title') else "Untitled",
                "link": link,
                "summary": summary,
                "date": pub_date or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                "id": hashlib.md5((entry.title + link).encode()).hexdigest()[:12],
            })
        
        return articles, None
    except ImportError:
        # Fallback: manual XML parsing
        try:
            import xml.etree.ElementTree as ET
            req = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
            root = ET.fromstring(raw)
            
            # Find namespace
            ns = {}
            for m in ["http://www.w3.org/2005/Atom", ""]:
                items = root.findall(f".//{{{m}}}item") or root.findall(f".//{{{m}}}entry")
                if items:
                    break
            
            articles = []
            # Try common RSS structures
            for item in (root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")):
                def _find(tag):
                    for t in [tag, f"{{http://www.w3.org/2005/Atom}}{tag}"]:
                        el = item.find(t)
                        if el is not None and el.text:
                            return el.text
                    return ""
                
                title = _find("title")
                link = _find("link")
                if link.startswith("http"):
                    pass
                else:
                    link_el = item.find("link")
                    if link_el is not None:
                        link = link_el.get("href", "")
                
                desc = _find("description") or _find("summary")
                date = _find("pubDate") or _find("published") or _find("updated")
                
                if not title:
                    continue
                    
                articles.append({
                    "title": title.strip()[:150],
                    "link": link,
                    "summary": desc[:200].strip() if desc else "",
                    "date": date or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                    "id": hashlib.md5((title + link).encode()).hexdigest()[:12],
                })
                if len(articles) >= MAX_PER_SOURCE:
                    break
            
            return articles, None
        except Exception as e2:
            return [], str(e2)
    except Exception as e:
        return [], str(e)


# ============================================================
# Political Party Detection
# ============================================================
PARTY_KEYWORDS = {
    "PKR":     {"keywords": ["pkr", "anwar", "anwar ibrahim", "parti keadilan rakyat", "keadilan", " Rafizi", "saifuddin", "fahmi fadzil", "nurul izzah", "nurulizzah"], "color": "#e63946", "coalition": "PH"},
    "DAP":     {"keywords": ["dap", "lim guan eng", "lim kit siang", "anthony loke", "hannah yeoh", "gobind singh", "teo nie ching", "chong zhemin", "parti tindakan demokratik"], "color": "#e63946", "coalition": "PH"},
    "AMANAH":  {"keywords": ["amanah", "mohamad sabu", "mat sabu", "khalid samad", "parti amanah"], "color": "#f4a261", "coalition": "PH"},
    "UMNO":    {"keywords": ["umno", " Zahid", "ahmad zahid", "ismail sabri", "khairy jamaluddin", "tok mat", "mohamad hasan", "parti kemakmuran"], "color": "#3a86ff", "coalition": "BN"},
    "MIC":     {"keywords": ["mic", "s.a. vigneswaran", "saravanan", "parti india malaysia"], "color": "#3a86ff", "coalition": "BN"},
    "MCA":     {"keywords": ["mca", "wee ka siong", "liow tiong lai", "parti cina malaysia"], "color": "#3a86ff", "coalition": "BN"},
    "PAS":     {"keywords": ["pas", "hadi awang", "abdul hadi", "tuan ibrahim", "mariah", "parti islam", "ulama"], "color": "#2dc653", "coalition": "PN"},
    "BERSATU": {"keywords": ["bersatu", "muhyiddin", "hamzah zainudin", "hamzah", "azmin ali", "faekah", "parti pribumi", "ppbm"], "color": "#7b2cbf", "coalition": "PN"},
    "GERAKAN": {"keywords": ["gerakan", "dominic lau"], "color": "#2dc653", "coalition": "PN"},
    "WARISAN": {"keywords": ["warisan", "shafie apdal", "parti warisan"], "color": "#9d4edd", "coalition": "-"},
    "MUDA":    {"keywords": ["muda", "syed saddiq", "parti muda"], "color": "#ffd60a", "coalition": "-"},
    "GPS":     {"keywords": ["gps", "abang johari", "fadillah yusof", "gabungan parti sarawak"], "color": "#06ffa5", "coalition": "GPS"},
    "GRS":     {"keywords": ["grs", "hajiji noor", "gabungan rakyat sabah"], "color": "#00b4d8", "coalition": "GRS"},
    "PH":      {"keywords": ["pakatan harapan", "ph ", "ph,", "ph.", "ph)", "kerajaan ph", "kerajaan perpaduan"], "color": "#e63946", "coalition": "PH"},
    "PN":      {"keywords": ["perikatan nasional", "pn ", "pn,", "pn.", "pn)", "pembangkang"], "color": "#2dc653", "coalition": "PN"},
    "BN":      {"keywords": ["barisan nasional", "bn ", "bn,", "bn.", "bn)"], "color": "#3a86ff", "coalition": "BN"},
}

# Politician names → party mapping (quick lookup)
POLITICIAN_MAP = {
    "anwar": "PKR", "anwar ibrahim": "PKR", "nurul izzah": "PKR", "nurulizzah": "PKR",
    "rafizi": "PKR", "saifuddin": "PKR", "fahmi fadzil": "PKR",
    "lim guan eng": "DAP", "lim kit siang": "DAP", "anthony loke": "DAP",
    "hannah yeoh": "DAP", "gobind singh": "DAP", "teo nie ching": "DAP",
    "mohamad sabu": "AMANAH", "mat sabu": "AMANAH", "khalid samad": "AMANAH",
    "zahid": "UMNO", "ahmad zahid": "UMNO", "ismail sabri": "UMNO",
    "khairy": "UMNO", "tok mat": "UMNO", "mohamad hasan": "UMNO",
    "hadi awang": "PAS", "abdul hadi": "PAS", "tuan ibrahim": "PAS",
    "muhyiddin": "BERSATU", "hamzah zainudin": "BERSATU", "hamzah": "BERSATU",
    "azmin ali": "BERSATU", "azmin": "BERSATU",
    "shafie apdal": "WARISAN", "shafie": "WARISAN",
    "syed saddiq": "MUDA",
    "abang johari": "GPS", "fadillah yusof": "GPS",
    "hajiji": "GRS", "hajiji noor": "GRS",
    "isham jalil": "BERSATU", "ishamjalil": "BERSATU",
}


import re

def detect_parties(title, summary=""):
    """Scan title + summary for political party mentions. Returns list of {party, color, coalition}."""
    text = (title + " " + summary).lower()
    found = {}
    
    # Check party keywords (use word boundary for short keywords to avoid false positives)
    for party, info in PARTY_KEYWORDS.items():
        for kw in info["keywords"]:
            kw_lower = kw.lower().strip()
            # Use word boundary for short keywords (<=4 chars), substring for longer ones
            if len(kw_lower) <= 4:
                pattern = r'\b' + re.escape(kw_lower) + r'\b'
                if re.search(pattern, text):
                    found[party] = {"party": party, "color": info["color"], "coalition": info["coalition"]}
                    break
            else:
                if kw_lower in text:
                    found[party] = {"party": party, "color": info["color"], "coalition": info["coalition"]}
                    break
    
    # Check politician names (always substring match — names are long enough)
    for name, party in POLITICIAN_MAP.items():
        if name.lower() in text and party not in found:
            found[party] = {"party": party, "color": PARTY_KEYWORDS[party]["color"], "coalition": PARTY_KEYWORDS[party]["coalition"]}
    
    if not found:
        return [{"party": "NEUTRAL", "color": "#6c757d", "coalition": "-"}]
    
    return list(found.values())


def push_to_bridge(articles, source_name):
    """Push fetched articles to bridge server."""
    try:
        data = json.dumps({
            "type": "news_update",
            "source": source_name,
            "articles": articles,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        }).encode()
        req = Request(
            BRIDGE_URL,
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
            method="POST"
        )
        with urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def load_cache():
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text())
        except:
            pass
    return {"articles": [], "last_fetch": None}


def save_cache(data):
    CACHE_FILE.write_text(json.dumps(data, indent=2))


def merge_articles(existing, new_articles):
    """Merge new articles into existing list, dedup by id, keep latest 50."""
    seen = {a["id"] for a in existing}
    for a in new_articles:
        if a["id"] not in seen:
            existing.append(a)
            seen.add(a["id"])
    # Sort by date (most recent first), keep MAX_ARTICLES
    existing.sort(key=lambda x: x.get("date", ""), reverse=True)
    return existing[:MAX_ARTICLES]


def run():
    cache = load_cache()
    total_new = 0
    errors = []
    
    for source in NEWS_SOURCES:
        articles, error = fetch_rss(source["rss"])
        if error:
            errors.append(f"{source['name']}: {error}")
            continue
        if not articles:
            errors.append(f"{source['name']}: 0 articles")
            continue
        
        # Add source metadata to each article
        for a in articles:
            a["source"] = source["name"]
            a["icon"] = source["icon"]
            a["lang"] = source["lang"]
            # Auto-tag political parties
            a["parties"] = detect_parties(a["title"], a.get("summary", ""))
        
        # Push to bridge
        pushed = push_to_bridge(articles, source["name"])
        
        # Merge into cache
        cache["articles"] = merge_articles(cache["articles"], articles)
        total_new += len(articles)
        
        status = f"  ✓ {source['name']}: {len(articles)} articles {'(pushed to bridge)' if pushed else '(bridge unavailable)'}"
        print(status)
    
    cache["last_fetch"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    save_cache(cache)
    
    print(f"\n📰 Total: {total_new} new articles | Cache: {len(cache['articles'])} stored")
    if errors:
        print(f"⚠️  Errors ({len(errors)}):")
        for e in errors[:5]:
            print(f"  - {e}")


if __name__ == "__main__":
    run()
