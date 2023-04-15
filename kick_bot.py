import logging
import json
import random
import asyncio
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, ContextTypes
from pprint import pprint
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
import sys


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def random_ban_unban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    chat_id = update.effective_chat.id

    with open(f'user_ids_{group_name}.json', 'r') as f:
        user_ids = json.load(f)

    chat_members = user_ids

    print(chat_members)

    chat = await context.bot.get_chat(f"@{group_name}")

    print(chat.to_dict())

    while True:
        print('executing loop')

        for user_id, username in chat_members.items():
            if username not in ["jaimin_building", "tg_kicker_bot"] and random.random() < 0.5:
                await context.bot.ban_chat_member(chat_id, user_id)
                asyncio.sleep(1)
                await context.bot.unban_chat_member(chat_id, user_id)
                await context.bot.send_message(chat_id, f"Banned and unbanned user: {username}")
                print(f"Banned and unbanned user: {username}")
            

        await asyncio.sleep(5)  # Wait for 30 seconds


async def on_chat_join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    context.bot_data[chat_id] = True
    logger.info(f"Bot joined chat: {chat_id}")


async def get_users(api_id, api_hash, phone_number, group_name):

    async with TelegramClient('anon', api_id, api_hash) as client:
        # Ensure you're authorized
        if not await client.is_user_authorized():
            await client.start(phone=phone_number)
            # Getting information about yourself
            me = await client.get_me()
            print("Connected as", me.stringify())

        # Get the group entity
        entity = await client.get_entity(group_name)

        # Get the group members
        participants = await client.get_participants(entity)
        print(participants)
        """
        participants = await client(GetParticipantsRequest(
            entity, ChannelParticipantsSearch(group_name), 0, 1000
        ))
        """

    user_ids = {p.id: p.username for p in participants}

    with open(f'user_ids_{group_name}.json', 'w') as f:
        json.dump(user_ids, f)

    return participants

with open('tg_keys.json', 'r') as f:
    api_dict = json.load(f)

group_name = 'testingasdfgasd'


tg_api = api_dict['bot_api']
api_id = api_dict['telethon_api_id']
api_hash = api_dict['telethon_api_hash']
phone_number = api_dict['phone_number']

async def main():

    participants = await get_users(api_id, api_hash, phone_number, group_name)
    return participants


def bot_start():

    application = Application.builder().token(tg_api).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("on_chat_join", on_chat_join))
    application.add_handler(CommandHandler("unlink", random_ban_unban))

    application.run_polling()

    random_ban_unban(application.context)


if __name__ == "__main__":
    if '-1' in sys.argv:
        asyncio.run(main())
    else:
        bot_start()

