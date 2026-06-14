import os
import tg_bot.modules.sql.users_sql as sql
from telegram.ext import MessageHandler, Filters, CommandHandler, run_async
from telegram import ParseMode
from tg_bot import dispatcher, OWNER_ID, LOGGER

# 👇 Fetches the Log Channel ID from Render Environment Variables! 👇
# If it's not set or is invalid, it defaults to sending logs to the Owner ID.
try:
    GLOBAL_LOG_CHANNEL = int(os.environ.get("GLOBAL_LOG_CHANNEL", OWNER_ID))
except (ValueError, TypeError):
    GLOBAL_LOG_CHANNEL = OWNER_ID 

def send_group_log(bot, chat, added_by=None):
    try:
        invite_link = bot.export_chat_invite_link(chat.id)
    except Exception:
        invite_link = "❌ No Admin Rights (Cannot generate link yet)"
        
    member_count = bot.get_chat_members_count(chat.id)
    username = f"@{chat.username}" if chat.username else "Private Group"
    
    text = f"🚨 **Group Update** 🚨\n\n"
    text += f"**Group Name:** {chat.title}\n"
    text += f"**ID:** `{chat.id}`\n"
    text += f"**Username:** {username}\n"
    text += f"**Members:** {member_count}\n"
    text += f"**Invite Link:** {invite_link}\n"
    
    if added_by:
        text += f"\n**Added By:** {added_by.first_name} (`{added_by.id}`)"

    try:
        bot.send_message(GLOBAL_LOG_CHANNEL, text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        LOGGER.error(f"Failed to send join log: {e}")

@run_async
def join_logger(bot, update):
    message = update.effective_message
    if not message.new_chat_members: 
        return
    
    for member in message.new_chat_members:
        if member.id == bot.id:
            # Sends log automatically when bot is added to a new group
            send_group_log(bot, update.effective_chat, message.from_user)

@run_async
def fetch_all_details(bot, update):
    # Only the Owner can use this command
    if update.effective_user.id != OWNER_ID:
        return
        
    update.effective_message.reply_text("🔄 Fetching details from **ALL** known groups... Please wait.")
    
    all_chats = sql.get_all_chats()
    success_count = 0
    
    for chat_db in all_chats:
        try:
            chat = bot.get_chat(chat_db.chat_id)
            send_group_log(bot, chat)
            success_count += 1
        except Exception:
            pass # Bot might have been kicked, or chat deleted
            
    update.effective_message.reply_text(f"✅ Finished! Fetched and sent details for {success_count} groups to your log channel.")

dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, join_logger), group=1)
dispatcher.add_handler(CommandHandler("fetchdetails", fetch_all_details))
