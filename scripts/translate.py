"""無料のMyMemory Translation APIを使った簡易翻訳。

失敗時(通信エラー・レート制限など)は例外を投げず、原文をそのまま返す。
"""

import requests

API_URL = "https://api.mymemory.translated.net/get"
TIMEOUT = 10


def translate_to_ja(text: str) -> str:
    """英語テキストを日本語に翻訳する。失敗時は原文をそのまま返す。"""
    text = text.strip()
    if not text:
        return text

    try:
        resp = requests.get(
            API_URL,
            params={"q": text, "langpair": "en|ja"},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        translated = data.get("responseData", {}).get("translatedText", "")
        # MyMemoryはレート制限時にエラーメッセージ文字列を translatedText に埋めて返すことがある
        if not translated or "MYMEMORY WARNING" in translated.upper():
            return text
        return translated
    except (requests.RequestException, ValueError):
        return text
