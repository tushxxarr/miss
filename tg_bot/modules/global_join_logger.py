from telegram.ext import MessageHandler, Filters
from tg_bot import dispatcher, OWNER_ID

# Replace OWNER_ID with your specific global log channel ID if you have one
# Example: GLOBAL_LOG_CHANNEL = -1001234567890
GLOBAL_LOG_CHANNEL = OWNER_ID 

def log_bot_joined(bot, update):
    message = update.effective_message
    chat = update.effective_chat
    
    # Check if new members were added
    if not message.new_chat_members:
        return

    # Check if the bot itself is one of the members added
    is_bot_added = any(member.id == bot.id for member in message.new_chat_members)
    
    if is_bot_added:
        chat_name = chat.title
        chat_id = chat.id
        chat_username = f"@{chat.username}" if chat.username else "Private Group"
        added_by = message.from_user.first_name
        added_by_id = message.from_user.id
        
        # Try to get the invite link 
        # (This succeeds if the person adding the bot promoted it to Admin at the same time)
        try:
            link = bot.export_chat_invite_link(chat.id)
        except Exception:
            link = "No admin rights yet to generate link."
            
        log_text = (
            f"🎉 **Bot added to a new group!**\n"
            f"**Group Name:** {chat_name}\n"
            f"**Group ID:** `{chat_id}`\n"
            f"**Username:** {chat_username}\n"
            f"**Link:** {link}\n"
            f"**Added By:** {added_by} (`{added_by_id}`)"
        )
        
        # Send the log to the global log channel or Owner ID
        try:
            bot.send_message(
                chat_id=GLOBAL_LOG_CHANNEL, 
                text=log_text, 
                parse_mode="Markdown"
            )
        except Exception as e:
            pass # Silently fail if the log channel ID is invalid or bot can't reach it

# Create the handler and add it to the dispatcher
join_handler = MessageHandler(Filters.status_update.new_chat_members, log_bot_joined)
dispatcher.add_handler(join_handler)
