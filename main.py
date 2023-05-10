import os, discord, asyncio
from discord.ext import commands, tasks
#import secret

class AutoPublisher(commands.Bot):

    publishLogs = {}

    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

async def get_prefix(client, message):
    return commands.when_mentioned_or(*("ap!",))(client, message)

# Creating the Client using AutoPublisher class
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = AutoPublisher(command_prefix = get_prefix, intents = intents)

#Tell them you're ready to rock!
@client.event
async def on_ready():
    await client.change_presence(status = discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.listening, name="the prefix `ap!`"))
    print('The Auto Publisher is online.')

#Okay here we publish the messages
@client.event
async def on_message(message):
    channel = message.channel
    if channel.is_news():
        publish_count = client.publishLogs.get(channel.id, 0)
        if publish_count <= 10:
            #Not gonna publish more than 10 message per channel in an hour. [Rate Limit Measure]
            client.publishLogs[channel.id] = publish_count + 1
            await message.publish()

    #here we will process the message to check if it has any commands
    await client.process_commands(message)


#Reset the publishLogs every hour
@tasks.loop(hours=1)
async def resetpublishLogs():
    client.publishLogs = {}
    print("Publish Logs are reset now!")

@resetpublishLogs.before_loop
async def before_resetpublishLogs():
    await client.wait_until_ready()

#A couple of commands below
@client.command()
async def ping(ctx):
    """Displays the bot latency."""
    await ctx.send(f"`Pong! {round(client.latency * 1000, 2)}ms.`")

@client.command(hidden=True)
async def invite(ctx):
    """Invite link to add the bot to your server!"""
    await ctx.send(f"{os.environ.get('INVITE')}")

@client.command()
async def info(ctx):
    """Displays the information about the bot."""
    e = discord.Embed()
    e.description = """> This bot will automatically publish every new message in an Announcement/News channel.\n> Bot requires the following permissions:
    ```
    View Channel\nSend Messages\nManage Messages\nRead Message History
    ```
    """
    e.set_author(name=client.user.name, icon_url=client.user.avatar)
    e.set_thumbnail(url=client.user.avatar)
    e.set_footer(text=f"Made by EliteBOY#1337 | Total Servers: {len(client.guilds)}")
    await ctx.send(embed=e)

#This is the place for errors and exceptions
@client.event
async def on_command_error(ctx, error):
    print(f"Ignoring the exception: {str(error)}")

#Start the Bot like a Boss!
async def main():
    async with client:
        resetpublishLogs.start()
        print("Background Publish Logs task started.")
        await client.start(os.environ.get('TOKEN'))
        
asyncio.run(main())
