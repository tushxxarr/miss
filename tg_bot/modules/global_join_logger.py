import requests
from telegram.ext import MessageHandler, Filters, CommandHandler, run_async
from tg_bot import dispatcher, OWNER_ID

# Sends logs to the Owner PMs. Replace OWNER_ID with a channel ID (e.g., -100123456) if you prefer a channel.
LOG_CHANNEL = OWNER_ID

def send_group_log(bot, chat, added_by=None):
    try:
        invite_link = bot.export_chat_invite_link(chat.id)
    except Exception:
        invite_link = "❌ No Admin Rights (Cannot generate link yet)"
        
    member_count = bot.get_chat_members_count(chat.id)
    username = f"@{chat.username}" if chat.username else "Private Group"
    
    text = f"🚨 **New Group Update** 🚨\n\n"
    text += f"**Group Name:** {chat.title}\n"
    text += f"**ID:** `{chat.id}`\n"
    text += f"**Username:** {username}\n"
    text += f"**Members:** {member_count}\n"
    text += f"**Invite Link:** {invite_link}\n"
    
    if added_by:
        text += f"\n**Added By:** {added_by.first_name} (`{added_by.id}`)"

    try:
        bot.send_message(LOG_CHANNEL, text, parse_mode="Markdown")
    except Exception:
        pass # Fail silently if bot can't reach log channel

@run_async
def join_logger(bot, update):
    message = update.effective_message
    if not message.new_chat_members: 
        return
    
    for member in message.new_chat_members:
        if member.id == bot.id:
            send_group_log(bot, update.effective_chat, message.from_user)

@run_async
def fetch_group_details(bot, update):
    # Only the Owner can use this command to fetch details
    if update.effective_user.id != OWNER_ID:
        return
        
    send_group_log(bot, update.effective_chat)
    update.effective_message.reply_text("✅ Group details fetched and sent to the log channel.")

dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, join_logger))
dispatcher.add_handler(CommandHandler("fetchdetails", fetch_group_details))
