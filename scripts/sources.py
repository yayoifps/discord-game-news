"""収集するRSSフィードの一覧。

category:
  - "japan"    国内ゲームニュース
  - "overseas" 海外ゲームニュース
  - "security" セキュリティ/データ流出系(Google Newsのキーワード検索)

lang:
  - "ja" 日本語(翻訳不要)
  - "en" 英語(日本語に翻訳する)
"""

FEEDS = [
    # --- 日本語ゲームメディア ---
    {"name": "4Gamer", "url": "https://www.4gamer.net/rss/index.xml", "category": "japan", "lang": "ja"},
    {"name": "AUTOMATON", "url": "https://automaton-media.com/feed/", "category": "japan", "lang": "ja"},
    {"name": "Game*Spark", "url": "https://www.gamespark.jp/rss/index.rdf", "category": "japan", "lang": "ja"},
    {"name": "INSIDE", "url": "https://www.inside-games.jp/rss/index.rdf", "category": "japan", "lang": "ja"},

    # --- 海外ゲームメディア(翻訳対象) ---
    {"name": "IGN", "url": "https://www.ign.com/rss/articles/feed", "category": "overseas", "lang": "en"},
    {"name": "GameSpot", "url": "https://www.gamespot.com/feeds/mashup/", "category": "overseas", "lang": "en"},
    {"name": "PC Gamer", "url": "https://www.pcgamer.com/rss/", "category": "overseas", "lang": "en"},
    {"name": "Eurogamer", "url": "https://www.eurogamer.net/feed", "category": "overseas", "lang": "en"},
    {"name": "Polygon", "url": "https://www.polygon.com/rss/index.xml", "category": "overseas", "lang": "en"},

    # --- セキュリティ/データ流出系(キーワード検索) ---
    {
        "name": "セキュリティニュース(日本語)",
        "url": "https://news.google.com/rss/search?q=%E3%82%B2%E3%83%BC%E3%83%A0%20(%E6%83%85%E5%A0%B1%E6%BC%8F%E3%81%88%E3%81%84%20OR%20%E4%B8%8D%E6%AD%A3%E3%82%A2%E3%82%AF%E3%82%BB%E3%82%B9%20OR%20%E3%83%87%E3%83%BC%E3%82%BF%E6%B5%81%E5%87%BA)&hl=ja&gl=JP&ceid=JP:ja",
        "category": "security",
        "lang": "ja",
    },
    {
        "name": "Security News (English)",
        "url": "https://news.google.com/rss/search?q=game+(data+breach+OR+leak+OR+hack)&hl=en-US&gl=US&ceid=US:en",
        "category": "security",
        "lang": "en",
    },
]

# カテゴリごとのDiscord embed色
CATEGORY_COLOR = {
    "japan": 0x3BA55D,     # 緑
    "overseas": 0x5865F2,  # Discordブルー
    "security": 0xED4245,  # 赤
}

CATEGORY_LABEL = {
    "japan": "国内",
    "overseas": "海外",
    "security": "セキュリティ",
}
