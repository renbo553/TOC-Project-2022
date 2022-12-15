import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fsm import TocMachine
from utils import send_text_message

from flask_sqlalchemy import SQLAlchemy # for mysql database

load_dotenv()


app = Flask(__name__, static_url_path="")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://sql6584163:LhfpILmD32@sql6.freemysqlhosting.net:3306/sql6584163"
db = SQLAlchemy()
db.init_app(app)

machine = TocMachine(
    db=db,
    states=[
        "initial",
        "menu",
        "insert_0", "insert_1", "insert_2", "insert_3", "insert_fin",
        "delete_0", "delete_1", "delete_fin",
        "modify_0", "modify_1", "modify_2", "modify_3", "modify_4", "modify_5", "modify_fin",
        "search_0", "search_fin",
    ],
    transitions=[
        {
            "trigger": "advance",
            "source": "initial",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "insert_0",
            "conditions": "is_going_to_insert_0",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "delete_0",
            "conditions": "is_going_to_delete_0",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "modify_0",
            "conditions": "is_going_to_modify_0",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "search_0",
            "conditions": "is_going_to_search_0",
        },
        {
            "trigger": "advance",
            "source": "insert_0",
            "dest": "insert_1",
            "conditions": "is_going_to_insert_1",
        },
        {
            "trigger": "advance",
            "source": "insert_1",
            "dest": "insert_2",
            "conditions": "is_going_to_insert_2",
        },
        {
            "trigger": "advance",
            "source": "insert_2",
            "dest": "insert_3",
            "conditions": "is_going_to_insert_3",
        },
        {
            "trigger": "advance",
            "source": "insert_3",
            "dest": "insert_fin",
            "conditions": "is_going_to_insert_fin",
        },
        {
            "trigger": "advance",
            "source": "insert_fin",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        {
            "trigger": "advance",
            "source": "delete_0",
            "dest": "delete_1",
            "conditions": "is_going_to_delete_1",
        },
        {
            "trigger": "advance",
            "source": "delete_1",
            "dest": "delete_fin",
            "conditions": "is_going_to_delete_fin",
        },
        {
            "trigger": "advance",
            "source": "delete_fin",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        {
            "trigger": "advance",
            "source": "modify_0",
            "dest": "modify_1",
            "conditions": "is_going_to_modify_1",
        },
        {
            "trigger": "advance",
            "source": "modify_1",
            "dest": "modify_2",
            "conditions": "is_going_to_modify_2",
        },
        {
            "trigger": "advance",
            "source": "modify_2",
            "dest": "modify_3",
            "conditions": "is_going_to_modify_3",
        },
        {
            "trigger": "advance",
            "source": "modify_3",
            "dest": "modify_4",
            "conditions": "is_going_to_modify_4",
        },
        {
            "trigger": "advance",
            "source": "modify_4",
            "dest": "modify_5",
            "conditions": "is_going_to_modify_5",
        },
        {
            "trigger": "advance",
            "source": "modify_5",
            "dest": "modify_fin",
            "conditions": "is_going_to_modify_fin",
        },
        {
            "trigger": "advance",
            "source": "modify_fin",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        {
            "trigger": "advance",
            "source": "search_0",
            "dest": "search_fin",
            "conditions": "is_going_to_search_fin",
        },
        {
            "trigger": "advance",
            "source": "search_fin",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        {
            "trigger": "go_back",
            "source": ["delete_1", "modify_1"],
            "dest": "menu",
        },
    ],
    initial="initial",
    auto_transitions=False,
    show_conditions=True,
)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response == False:
            send_text_message(event.reply_token, "此內容無效，請輸入正確的資訊")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
