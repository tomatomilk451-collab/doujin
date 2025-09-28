import tweepy, random, time
from datetime import datetime

# 認証情報（Renderに環境変数で入れるのでここはダミー）
API_KEY = "API_KEY"
API_SECRET = "API_SECRET"
ACCESS_TOKEN = "ACCESS_TOKEN"
ACCESS_SECRET = "ACCESS_SECRET"

# tweepy認証
auth = tweepy.OAuth1UserHandler(
    API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET
)
api = tweepy.API(auth)

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
    api.update_status(msg)
    print("宣伝投稿:", msg)

# リプライ確認（お礼）
def reply_mentions():
    mentions = api.mentions_timeline(count=5, tweet_mode="extended")
    for m in mentions:
        if not m.favorited:
            api.create_favorite(m.id)
            reply = f"@{m.user.screen_name} ありがとうございます💕"
            api.update_status(reply, in_reply_to_status_id=m.id)
            print("お礼リプ:", reply)

# キーワード反応（TLから検索）
def keyword_reply():
    for key, msg in keywords.items():
        tweets = api.search_tweets(q=key, count=3, result_type="recent")
        for t in tweets:
            if not t.favorited:  # 未対応チェック
                api.create_favorite(t.id)
                reply = f"@{t.user.screen_name} {msg}"
                api.update_status(reply, in_reply_to_status_id=t.id)
                print("キーワード反応:", reply)

# メインループ
while True:
    now = datetime.now()
    if now.hour in [12, 20]:  # 毎日12時と20時に宣伝
        post_ad()
    reply_mentions()
    keyword_reply()
    time.sleep(600)  # 10分ごとにチェック
