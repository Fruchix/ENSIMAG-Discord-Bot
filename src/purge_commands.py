from src.main import arc_client, bot

arc_client.purge_all_commands()
arc_client.resync_commands()

if __name__ == "__main__":
    bot.run()
