import requests
from telegram.ext import CommandHandler, run_async
from tg_bot import dispatcher, TOKEN, OWNER_ID

@run_async
def push_bot_menu(bot, update):
    if update.effective_user.id != OWNER_ID:
        return
        
    update.effective_message.reply_text("🔄 Pushing commands to Telegram Menu... Please wait.")
    
    # The complete list of commands to display in the user's menu
    commands = [
        {"command": "start", "description": "Start the bot"},
        {"command": "help", "description": "Open the help menu"},
        {"command": "settings", "description": "View group settings"},
        {"command": "rules", "description": "View group rules"},
        {"command": "ban", "description": "Ban a user"},
        {"command": "mute", "description": "Mute a user"},
        {"command": "kick", "description": "Kick a user"},
        {"command": "warn", "description": "Warn a user"},
        {"command": "notes", "description": "View saved notes"},
        {"command": "filters", "description": "View active filters"},
        {"command": "adminlist", "description": "List all group admins"},
        {"command": "id", "description": "Get User or Chat ID"},
        {"command": "info", "description": "Get User Info"},
        {"command": "pin", "description": "Pin a message"},
        {"command": "donate", "description": "Donate to the creator"}
    ]
    
    # Send directly to Telegram's backend API
    url = f"https://api.telegram.org/bot{TOKEN}/setMyCommands"
    try:
        res = requests.post(url, json={"commands": commands})
        if res.status_code == 200:
            update.effective_message.reply_text("✅ Menu updated successfully! Restart your Telegram app to see the `/` menu appear.")
        else:
            update.effective_message.reply_text(f"❌ Failed to push menu: {res.text}")
    except Exception as e:
        update.effective_message.reply_text(f"❌ Error: {e}")

dispatcher.add_handler(CommandHandler("updatemenu", push_bot_menu))
