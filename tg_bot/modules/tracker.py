from telegram.ext import CommandHandler, MessageHandler, Filters, run_async
from telegram import ParseMode
from tg_bot import dispatcher, OWNER_ID
import tg_bot.modules.sql.tracker_sql as sql

@run_async
def track_chat(bot, update, args):
    # Only Owner can set up tracking
    if update.effective_user.id != OWNER_ID:
        return
        
    if len(args) < 1:
        update.effective_message.reply_text("⚠️ Please provide the Chat ID to track.\n**Example:** `/track -10012345678`", parse_mode=ParseMode.MARKDOWN)
        return
        
    target_chat = args[0]
    current_chat = str(update.effective_chat.id)
    
    sql.add_track(target_chat, current_chat)
    update.effective_message.reply_text(f"✅ **Tracking Activated!**\nAll messages from `{target_chat}` will now be forwarded to THIS group along with user details.", parse_mode=ParseMode.MARKDOWN)

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
        user_text += f"\n💬 **From Chat:** {update.effective_chat.title} (`{chat_id}`)\n"
        user_text += f"📝 **Message:**"
        
        try:
            # 1. Send the User Details box
            bot.send_message(log_group_id, user_text, parse_mode=ParseMode.MARKDOWN)
            # 2. Forward the actual message (preserves photos, stickers, media, etc.)
            update.effective_message.forward(chat_id=log_group_id)
        except Exception as e:
            print(f"Error forwarding tracked message: {e}")

# Register commands
dispatcher.add_handler(CommandHandler("track", track_chat, pass_args=True))
dispatcher.add_handler(CommandHandler("untrack", untrack_chat, pass_args=True))

# Group 99 ensures this runs in the background for ALL messages without interrupting standard bot commands
dispatcher.add_handler(MessageHandler(Filters.all, track_messages), group=99)
