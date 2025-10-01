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

# 画像付き漫画スレッド投稿
def post_manga_thread():
    files = [
        "page1.jpg", "page2.jpg", "page3.jpg", "page4.jpg",
        "page5.jpg", "page6.jpg", "page7.jpg", "page8.jpg"
    ]
    prev_tweet = None
    total = len(files)

    for i, f in enumerate(files, start=1):
        media = api.media_upload(f)
        status_text = f"({i}/{total})"
        if prev_tweet:
            new_tweet = api.update_status(
                status=status_text,
                media_ids=[media.media_id],
                in_reply_to_status_id=prev_tweet.id,
                auto_populate_reply_metadata=True
            )
        else:
            new_tweet = api.update_status(
                status=f"📖 新作漫画公開！({i}/{total})",
                media_ids=[media.media_id]
            )
        prev_tweet = new_tweet

    # 最後に通販リンク
    final_msg = "💖 続きはこちらで読めます！通販 👉 https://example.com"
    api.update_status(
        status=final_msg,
        in_reply_to_status_id=prev_tweet.id,
        auto_populate_reply_metadata=True
    )
    logging.info("漫画スレッド投稿 完了！")

# メインループ
last_post = {}
while True:
    now = datetime.now()
    for target_hour in [12, 20]:
        if now.hour == target_hour and last_post.get(target_hour) != now.date():
            post_ad()
            last_post[target_hour] = now.date()

    reply_mentions()
    keyword_reply()
    time.sleep(600)
