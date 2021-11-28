import configuration
import logging
import os
from telegram import (
    Update,
    ParseMode,
    Bot,
    InlineQueryResultCachedSticker,
    InputTextMessageContent,
    InlineQueryResultArticle,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    InlineQueryHandler,
)
from telegram.utils.helpers import escape_markdown
from datetime import datetime, timezone
import re
from unicodedata import normalize
import pandas as pd
import traceback
import html
import json
import random
from uuid import uuid4
import typing
import time
from collections import OrderedDict
import praw
import pandas as pd

START_BOT_DATETIME = datetime.now(timezone.utc)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text("Hi!")


def get_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    args = update.message.text.split(" ")
    subreddit_name = "AskRedditespanol"
    if len(args) == 2:
        subreddit_name = args[1]
    topic = get_topic_from_subreddit(subreddit_name)
    message = topic.title
    if topic.selftext != "" and len(topic.selftext) < 1000:
        message += "\n" + topic.selftext
    url = topic.url
    file_name = url.split("/")
    if len(file_name) == 0:
        file_name = re.findall("/(.*?)", url)
    configuration.update_already_sended_submissions_csv_file(
        {"ID": topic.id, "Postname": topic.title, "Subreddit": topic.subreddit.title},
        configuration.get_file_location("already_sended_submissions.csv"),
    )
    if url != "" and file_name[2] == "i.redd.it":
        update.message.reply_photo(url, caption=message)
    else:
        update.message.reply_text(message)


def get_topic_from_subreddit(subreddit_name, counter=0):
    reddit = configuration.get_reddit(configuration.get_file_location("config.yaml"))
    topic = reddit.subreddit(subreddit_name).random()
    if (
        configuration.check_if_submission_was_sent(
            topic.id, configuration.get_file_location("already_sended_submissions.csv")
        )
        and counter < 3
    ):
        get_topic_from_subreddit(subreddit_name, counter + 1)
    return topic


def inlinequery(update: Update, context: CallbackContext) -> None:
    """Handle the inline query."""
    query = update.inline_query.query

    results = []

    # This constant is defined by the Bot API.
    MAX_RESULTS = 50

    inline_query = update.inline_query
    query = update.inline_query.query
    offset = update.inline_query.offset

    if not inline_query:
        return

    # If query is empty - return random stickers.
    return_random = not inline_query.query

    if return_random:
        stickers = random_stickers(MAX_RESULTS)
    elif query == "":
        stickers = random_stickers(MAX_RESULTS)
    else:
        stickers = search_stickers(inline_query.query)

    stickers = list(dict.fromkeys(stickers))

    if len(stickers) > MAX_RESULTS:
        stickers = stickers[:MAX_RESULTS]

    for sticker_file_id in stickers:
        results.append(
            InlineQueryResultCachedSticker(
                id=uuid4(),
                sticker_file_id=sticker_file_id,
            ),
        )
    if len(results) > 0:
        update.inline_query.answer(results)


def error_handler(update: Update, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    context.bot.send_message(chat_id=232424901, text=message, parse_mode=ParseMode.HTML)
    args = update.message.text.split(" ")
    if len(args) == 2:
        update.message.reply_text(
            get_topic_from_subreddit("Subreddit r/" + args[1]) + "no existe"
        )
    update.message.reply_text(get_topic_from_subreddit("AskRedditespanol"))


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(
        token=configuration.get_bot_token(
            configuration.get_file_location("config.yaml")
        ),
    )

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("get", get_command))

    # add inlinequery
    dispatcher.add_handler(InlineQueryHandler(inlinequery))
    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_error_handler(error_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
