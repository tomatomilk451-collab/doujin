import os, random, time, logging
from datetime import datetime
import tweepy

# ログ設定
logging.basicConfig(level=logging.INFO)

# 環境変数からキーを取得
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

# 宣伝文リスト
ads = [
    "📕新刊できました！通販はこちら → https://example.com",
    "✨サンプル公開中！ぜひ読んでください → https://example.com",
    "🔥在庫わずか！今すぐチェック → https://example.com"
]

# 自動返信キーワード
keywords = {
    "同人誌": "ありがとうございます！新刊はこちらです💕 → https://example.com",
    "サークル名": "見つけてくれて感謝です！✨ → https://example.com",
    "タイトル名": "話題にしてくださり感謝です🙏 新刊通販はこちら！ → https://example.com"
}

# 投稿済みチェック
last_post = {}

def post_ad():
    msg = random.choice(ads)
    try:
        api.update_status(msg)
        logging.info("宣伝投稿: %s", msg)
    except Exception as e:
        logging.error("投稿エラー: %s", e)

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

# メインループ
while True:
    now = datetime.now()
    for target_hour in [12, 20]:
        if now.hour == target_hour and last_post.get(target_hour) != now.date():
            post_ad()
            last_post[target_hour] = now.date()

    reply_mentions()
    keyword_reply()
    time.sleep(600)  # 10分ごとにチェック
