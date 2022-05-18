# wilderzone-discord-bot

## Setup & Run

Create a discord bot with permissions for Send Message, Manage Messages, and Read Message History. (75776 permissions integer)

```
# setup
echo "MAIN_TOKEN=$DISCORD_BOT_TOKEN" > .env
pip install -r requirements.txt

# run
python3 main.py
```