import logging
import os
from datetime import datetime
from random import Random
from typing import Tuple

from telegram import ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler, Updater

from exusiai_bot.dice_commands import dice_handler, dot_rd_handler
from exusiai_bot.dot_command import DotCommandDispatcher
from exusiai_bot.telegram_bot_utils import send_timed_message

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
PROXY_URL = "http://127.0.0.1:1081"

request_kwargs = {"proxy_url": PROXY_URL}

updater = Updater(token=TELEGRAM_BOT_TOKEN,
                  use_context=True,
                  request_kwargs=request_kwargs)
dispatcher = updater.dispatcher


def test(update: Update, context: CallbackContext):
    print('command: test')
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="I'm a bot, please talk to me!")
    send_timed_message(bot=context.bot,
                       chat_id=update.effective_chat.id,
                       text="test",
                       timeout=5000)


def error_handler(update: Update, context: CallbackContext):
    print(f'{context.error=}')
    raise context.error


def dot_jrrp_handler(
    update: Update,
    context: CallbackContext,
    argv: Tuple[str],
) -> None:
    username = update.effective_user.username
    rp = Random(hash(
        (username, *datetime.now().isocalendar()))).randint(0, 100)
    chat_id = update.effective_chat.id
    msg = f"@{username} 今天的人品值是：**{rp}**。"
    context.bot.send_message(chat_id, text=msg, parse_mode=ParseMode.MARKDOWN)


dispatcher.add_handler(CommandHandler('test', test))
dispatcher.add_error_handler(error_handler)
dot_dispatcher = DotCommandDispatcher(dispatcher=dispatcher)
dot_dispatcher.add_command("jrrp", dot_jrrp_handler)
dot_dispatcher.add_command("r", dice_handler)
dot_dispatcher.add_command("rd", dot_rd_handler)

updater.start_polling()
updater.idle()
