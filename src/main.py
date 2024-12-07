import hikari
import miru
import os
import arc

from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TOKEN")
guilds = os.getenv("GUILDS").split(",")

bot = hikari.GatewayBot(token)
arc_client = arc.GatewayClient(bot)

arc_client.load_extensions_from("src/bot/plugins")

if __name__ == "__main__":
    bot.run()
