import os
from flask import Flask, abort, request
import random
from linebot.v3.webhook import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    ImageMessage,
    PushMessageRequest
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
import datetime
from dotenv import load_dotenv
import schedule
import time
import threading
from csvDB import *

load_dotenv()
app = Flask(__name__)

# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
YOUR_CHANNEL_SECRET = os.environ['YOUR_CHANNEL_SECRET']
csvFile = "dataBase/0001.csv"
EmergencyFlag = False
LimitHour = 12
FamilyGroupID = "C12a441783aca758e02cd06a9771da067"

handler = WebhookHandler(YOUR_CHANNEL_SECRET)
configuration = Configuration(access_token=YOUR_CHANNEL_ACCESS_TOKEN)


@app.route('/toiletLinebot/')
def index():
    return "Hello from toiletlinebotURL"


@app.route("/toiletLinebot/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info(
            "Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        profile = line_bot_api.get_profile(event.source.user_id)
        msg = None  # msgの初期化
        # 相手の送信した内容で条件分岐して回答を変数に代入

        if event.message.text == '最終':
            # 時間の差を計算
            time_difference = timeDiff_lasttime_and_nowtime()

            # 差を時分で出力
            hours, remainder = divmod(time_difference.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)

            msg = f"{int(hours)}時間{int(minutes)}分前にベットの前を通過しました。"
        elif event.message.text == '確認':
            global EmergencyFlag
            if EmergencyFlag == True:
                msg = "確認しました。"
                EmergencyFlag = False
                with open(csvFile, 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [datetime.now(), "check of Family"])

        else:
            pass

        messages = [TextMessage(text=msg)]

        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=messages
            )
        )


def timeDiff_lasttime_and_nowtime():
    lasttime = lastTime(csvFile)
    date_object = datetime.strptime(
        str(lasttime), "%Y-%m-%d %H:%M:%S.%f")
    # 現在の時間を取得
    now = datetime.now()

    # 時間の差を計算
    return now - date_object


def send_periodic_message():
    # 時間の差を計算
    time_difference = timeDiff_lasttime_and_nowtime()

    # 差を時分で出力
    hours, remainder = divmod(time_difference.total_seconds(), 3600)

    if hours > LimitHour:
        global EmergencyFlag
        EmergencyFlag = True
        print("緊急メッセージ")
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            user_id = FamilyGroupID  # 送信先のユーザーIDを指定
            msg = f"{LimitHour}時間以上ベットの前を通過した形跡がありません。\n至急確認してください。\n確認後、'確認'と入力してください。"
            messages = [TextMessage(text=msg)]

            push_message_request = PushMessageRequest(
                to=user_id,
                messages=messages
            )

            line_bot_api.push_message(push_message_request)


# 1分おきにsend_periodic_messageを実行するスケジュールを設定
schedule.every(1).minutes.do(send_periodic_message)


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    # port = int(os.getenv("PORT", 6060))

    # # スケジュールを別スレッドで実行
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.start()

    app.run(host="0.0.0.0", port=6060, debug=False)
