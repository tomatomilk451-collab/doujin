import os, random, time, logging
from datetime import datetime
import tweepy

# ログ設定
logging.basicConfig(level=logging.INFO)

# 環境変数からキー取得
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
    logging.error("環境変数が足りません！Renderのダッシュボードで設定してください。")
    exit(1)

# tweepy認証
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

# 宣伝文リスト（テスト用）
ads = [
    "📕テスト投稿: 新刊は準備中です → https://example.com",
    "✨テスト投稿: Bot稼働確認中 → https://example.com"
]

# 自動返信キーワード（テスト用）
keywords = {
    "テスト": "ありがとうございます！テスト返信です → https://example.com"
}

# 宣伝投稿
def post_ad():
    msg = random.choice(ads)
    try:
        api.update_status(msg)
        logging.info("宣伝投稿: %s", msg)
    except Exception as e:
        logging.error("投稿エラー: %s", e)

# リプライ確認（お礼）
def reply_mentions():
    try:
        mentions = api.mentions_timeline(count=5, tweet_mode="extended")
        for m in mentions:
            if not m.favorited:
                api.create_favorite(m.id)
                reply = f"@{m.user.screen_name} ありがとうございます💕"
                api.update_status(reply, in_reply_to_status_id=m.id)
                logging.info("お礼リプ: %s", reply)
    except Exception as e:
        logging.error("リプライ処理エラー: %s", e)

# キーワード反応（TL検索）
def keyword_reply():
    try:
        for key, msg in keywords.items():
            tweets = api.search_tweets(q=f"{key} -filter:retweets", count=3, result_type="recent")
            for t in tweets:
                if not t.favorited:
                    api.create_favorite(t.id)
                    reply = f"@{t.user.screen_name} {msg}"
                    api.update_status(reply, in_reply_to_status_id=t.id)
                    logging.info("キーワード反応: %s", reply)
    except Exception as e:
        logging.error("キーワード処理エラー: %s", e)

# メインループ（テスト用）
last_post = {}
while True:
    now = datetime.now()
    # テスト用に毎時0分に1回投稿してみる
    if now.minute == 0 and last_post.get(now.hour) != now.date():
        post_ad()
        last_post[now.hour] = now.date()

    reply_mentions()
    keyword_reply()
    time.sleep(60)  # 1分ごとにチェック
