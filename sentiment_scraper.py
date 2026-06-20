#!/usr/bin/env python3
"""
Sentiment Scraper for Politician Monitoring
Scrapes news articles mentioning target politician, then uses GLM-5.2 for sentiment analysis.
"""

import json, os, re, time, urllib.request, urllib.error
from datetime import datetime, timedelta
import feedparser

# ============================================================
# Configuration
# ============================================================
POLITICIAN = "Fahmi Fadzil"
KEYWORDS = ["fahmi fadzil", "fahmi", "menteri komunikasi", "kkd"]
PARTY = "PKR"
COALITION = "PH"

# RSS sources to scan (same as news_scraper)
NEWS_SOURCES = [
    {"name": "Malay Mail", "url": "https://www.malaymail.com/feed/rss", "icon": "📰", "lang": "en"},
    {"name": "FMT", "url": "https://www.freemalaysiatoday.com/feed/", "icon": "📰", "lang": "en"},
    {"name": "Malaysia Now", "url": "https://malaysianow.com/feed/", "icon": "📰", "lang": "en"},
    {"name": "Malaysia Dateline", "url": "https://malaysiadateline.com/feed/", "icon": "📰", "lang": "ms"},
    {"name": "Twentytwo13", "url": "https://www.twentytwo13.my/feed/", "icon": "📰", "lang": "ms"},
    {"name": "Roketkini", "url": "https://roketkini.com/feed/", "icon": "📰", "lang": "ms"},
    {"name": "The Edge", "url": "https://www.theedgemalaysia.com/rss.xml", "icon": "📰", "lang": "en"},
    {"name": "Bernama", "url": "https://www.bernama.com/en/rss.php", "icon": "📰", "lang": "en"},
    {"name": "Utusan", "url": "https://www.utusan.com.my/feed/", "icon": "📰", "lang": "ms"},
    {"name": "Harakah Daily", "url": "https://harakahdaily.net/feed/", "icon": "📰", "lang": "ms"},
]

# GLM API config
GLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
GLM_API_KEY=os.environ.get("GLM_API_KEY", "")
if not GLM_API_KEY:
    # Try loading from .env file
    import subprocess
    result = subprocess.run(["bash", "-c", "grep GLM_API_KEY /root/.hermes/.env 2>/dev/null | cut -d= -f2"], capture_output=True, text=True)
    GLM_API_KEY=result.stdout.strip()
    print(f"  GLM key loaded from .env: {len(GLM_API_KEY)} chars")

CACHE_FILE = "/root/jarvis-jia-dashboard/sentiment_cache.json"

# ============================================================
# RSS Scanning
# ============================================================
def scan_news_for_politician():
    """Scan all RSS feeds for articles mentioning the politician."""
    found = []
    for source in NEWS_SOURCES:
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries[:20]:
                title = entry.get("title", "")
                summary = entry.get("summary", entry.get("description", ""))
                text = (title + " " + summary).lower()
                
                # Check if any keyword matches
                if any(kw in text for kw in KEYWORDS):
                    found.append({
                        "title": title,
                        "summary": re.sub(r'<[^>]+>', '', summary)[:300],
                        "link": entry.get("link", ""),
                        "source": source["name"],
                        "icon": source["icon"],
                        "published": entry.get("published", ""),
                        "scanned_at": datetime.now().isoformat(),
                    })
        except Exception as e:
            print(f"  [FAIL] {source['name']}: {e}")
    
    return found

# ============================================================
# GLM-5.2 Sentiment Analysis
# ============================================================
def analyze_sentiment(article):
    """Use GLM-5.2 to analyze sentiment of an article about the politician."""
    
    prompt = f"""You are a political sentiment analyst. Analyze this news article about {POLITICIAN} (Malaysian politician, {PARTY}/{COALITION}).

Title: {article['title']}
Source: {article['source']}
Summary: {article['summary']}

Return ONLY a JSON object with this exact format:
{{
  "sentiment": "positive" | "negative" | "neutral",
  "score": <number from -100 to 100>,
  "confidence": <number 0-100>,
  "topics": ["topic1", "topic2"],
  "summary": "<one line summary in Malay>",
  "impact": "high" | "medium" | "low"
}}

Rules:
- positive score = good coverage (praise, achievement, policy support)
- negative score = bad coverage (criticism, scandal, failure, attack)
- 0 = neutral
- Consider Malaysian political context (PH vs PN vs BN dynamics)
- "topics" should be key themes (e.g. "media freedom", "5G", "internet", "licensing")
- "summary" in Bahasa Melayu"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GLM_API_KEY}"
    }
    
    body = json.dumps({
        "model": "glm-5.2",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
    }).encode()
    
    req = urllib.request.Request(GLM_API_URL, data=body, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Extract JSON from response
        json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return result
        else:
            return {"sentiment": "neutral", "score": 0, "confidence": 0, 
                    "topics": [], "summary": "Analysis failed", "impact": "low"}
    except Exception as e:
        print(f"  [GLM ERROR] {e}")
        return {"sentiment": "neutral", "score": 0, "confidence": 0,
                "topics": [], "summary": f"Error: {str(e)[:50]}", "impact": "low"}

# ============================================================
# Main
# ============================================================
def run():
    print(f"=== Sentiment Scraper: {POLITICIAN} ===\n")
    
    # Step 1: Scan RSS feeds
    print("1. Scanning RSS feeds...")
    articles = scan_news_for_politician()
    print(f"   Found {len(articles)} articles mentioning {POLITICIAN}\n")
    
    if not articles:
        print("   No articles found. Try expanding keywords or adding more sources.")
    
    # Step 2: Analyze each article with GLM-5.2
    print("2. Analyzing sentiment with GLM-5.2...")
    for i, article in enumerate(articles):
        print(f"   [{i+1}/{len(articles)}] {article['title'][:60]}...")
        sentiment = analyze_sentiment(article)
        article["sentiment"] = sentiment
        print(f"       → {sentiment['sentiment'].upper()} (score: {sentiment['score']}, impact: {sentiment['impact']})")
        print(f"       → {sentiment['summary']}")
        time.sleep(1)  # Rate limit
    
    # Step 3: Calculate overall sentiment
    if articles:
        scores = [a["sentiment"]["score"] for a in articles]
        avg_score = sum(scores) / len(scores)
        pos = len([s for s in scores if s > 10])
        neg = len([s for s in scores if s < -10])
        neu = len(scores) - pos - neg
        
        overall = {
            "politician": POLITICIAN,
            "party": PARTY,
            "coalition": COALITION,
            "last_updated": datetime.now().isoformat(),
            "total_articles": len(articles),
            "average_score": round(avg_score, 1),
            "positive": pos,
            "negative": neg,
            "neutral": neu,
            "positive_pct": round(pos / len(articles) * 100),
            "negative_pct": round(neg / len(articles) * 100),
            "neutral_pct": round(neu / len(articles) * 100),
            "overall_sentiment": "positive" if avg_score > 10 else "negative" if avg_score < -10 else "neutral",
        }
        print(f"\n3. Overall Sentiment:")
        print(f"   Score: {overall['average_score']}/100")
        print(f"   Positive: {pos} ({overall['positive_pct']}%) | Negative: {neg} ({overall['negative_pct']}%) | Neutral: {neu} ({overall['neutral_pct']}%)")
        print(f"   Verdict: {overall['overall_sentiment'].upper()}")
    else:
        overall = {
            "politician": POLITICIAN,
            "party": PARTY,
            "coalition": COALITION,
            "last_updated": datetime.now().isoformat(),
            "total_articles": 0,
            "average_score": 0,
            "positive": 0, "negative": 0, "neutral": 0,
            "positive_pct": 0, "negative_pct": 0, "neutral_pct": 0,
            "overall_sentiment": "neutral",
        }
    
    # Step 4: Save to cache
    cache = {
        "politician": POLITICIAN,
        "party": PARTY,
        "coalition": COALITION,
        "last_updated": datetime.now().isoformat(),
        "overall": overall,
        "articles": articles,
    }
    
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
    
    print(f"\n4. Saved to {CACHE_FILE}")
    print(f"\nDone! {len(articles)} articles analyzed.")

if __name__ == "__main__":
    run()
