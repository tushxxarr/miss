import os
from telegram.ext import CommandHandler, MessageHandler, Filters, run_async
from telegram import ParseMode
from tg_bot import dispatcher, OWNER_ID
import tg_bot.modules.sql.tracker_sql as sql

# Fetches the separate Track Log Channel ID from Render Environment Variables!
try:
    TRACK_LOG_CHANNEL = int(os.environ.get("TRACK_LOG_CHANNEL"))
except (ValueError, TypeError):
    TRACK_LOG_CHANNEL = None

@run_async
def track_chat(bot, update, args):
    # Only Owner can set up tracking
    if update.effective_user.id != OWNER_ID:
        return
        
    if not TRACK_LOG_CHANNEL:
        update.effective_message.reply_text("⚠️ `TRACK_LOG_CHANNEL` environment variable is not set! Please add it in Render Settings.", parse_mode=ParseMode.MARKDOWN)
        return

    if len(args) < 1:
        update.effective_message.reply_text("⚠️ Please provide the Chat ID to track.\n**Example:** `/track -10012345678`", parse_mode=ParseMode.MARKDOWN)
        return
        
    target_chat = args[0]
    
    # Save the target chat and automatically route it to the environment Track Log Channel
    sql.add_track(target_chat, str(TRACK_LOG_CHANNEL))
    update.effective_message.reply_text(f"✅ **Tracking Activated!**\nAll messages from `{target_chat}` will now be automatically forwarded to your dedicated Track Log Channel.", parse_mode=ParseMode.MARKDOWN)
    
    # Extra Feature: Alert the Tracking Channel that a new target was added
    try:
        bot.send_message(TRACK_LOG_CHANNEL, f"📡 **New Tracking Initiated**\nTarget Chat: `{target_chat}`\nAuthorized by: `{update.effective_user.id}`", parse_mode=ParseMode.MARKDOWN)
    except Exception:
        pass

@run_async
def untrack_chat(bot, update, args):
    if update.effective_user.id != OWNER_ID:
        return
        
    if len(args) < 1:
        update.effective_message.reply_text("⚠️ Please provide the Chat ID to stop tracking.\n**Example:** `/untrack -10012345678`", parse_mode=ParseMode.MARKDOWN)
        return
        
    target_chat = args[0]
    if sql.remove_track(target_chat):
        update.effective_message.reply_text(f"🛑 Stopped tracking messages from `{target_chat}`.", parse_mode=ParseMode.MARKDOWN)
        
        # Extra Feature: Alert the Tracking Channel that a target was removed
        try:
            bot.send_message(TRACK_LOG_CHANNEL, f"🛑 **Tracking Terminated**\nTarget Chat: `{target_chat}`", parse_mode=ParseMode.MARKDOWN)
        except Exception:
            pass
    else:
        update.effective_message.reply_text("❌ That chat is not currently being tracked.")

@run_async
def track_messages(bot, update):
    # Only proceed if there is an actual message
    if not update.effective_message or not update.effective_chat:
        return
        
    chat_id = str(update.effective_chat.id)
    log_group_id = sql.get_log_group(chat_id)
    
    # If this chat ID matches a tracked chat in the database
    if log_group_id:
        user = update.effective_user
        
        # Build the User Details string
        user_text = f"👤 **User:** {user.first_name}"
        if user.username:
            user_text += f" (@{user.username})"
        user_text += f"\n🆔 **User ID:** `{user.id}`"
        user_text += f"\n💬 **From Chat:** {update.effective_chat.title} (`{chat_id}`)"
        
        # Extra Feature: Generate a direct clickable link to the original message
        msg_id = update.effective_message.message_id
        if chat_id.startswith("-100"):
            clean_chat_id = chat_id[4:]
            msg_link = f"https://t.me/c/{clean_chat_id}/{msg_id}"
            user_text += f"\n🔗 **Message Link:** [Click Here to View]({msg_link})"
            
        user_text += f"\n📝 **Message:**"
        
        try:
            # 1. Send the User Details box
            bot.send_message(log_group_id, user_text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            # 2. Forward the actual message (preserves photos, stickers, media, etc.)
            update.effective_message.forward(chat_id=log_group_id)
        except Exception as e:
            print(f"Error forwarding tracked message: {e}")

# Register commands
dispatcher.add_handler(CommandHandler("track", track_chat, pass_args=True))
dispatcher.add_handler(CommandHandler("untrack", untrack_chat, pass_args=True))

# Group 99 ensures this runs in the background for ALL messages without interrupting standard bot commands
dispatcher.add_handler(MessageHandler(Filters.all, track_messages), group=99)
