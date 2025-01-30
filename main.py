import json
import discord
from datetime import datetime, timedelta
import random
import os

TOKEN = os.getenv("DISCORD_TOKEN")

client = discord.Client(intents=discord.Intents.all())

data = {
    "status": False,
    "users": {},
    "weeks": {}
}

def get_current_week_str():
    now = datetime.now()
    then = now - timedelta(days=now.weekday())
    return then.strftime('%B.%d.%Y').lower()

def save():
    if not os.path.isdir("data"):
        os.mkdir("data")
    with open("data/data.json", "w") as datafile:
        json.dump(data, datafile)

def convo():
   return random.choice([
                "quAck!",
                "QUACK QUACK QUACK",
                "quack",
                "quack",
                "quack",
                "quack",
                "quack",
                "I AM THE OMNISCIENT DANA DUCK"
            ])

try:
    with open("data/data.json", "r") as datafile:
        data = json.load(datafile)
except FileNotFoundError:
    pass


async def update_status():
    if len(data["weeks"].keys()) == 0:
        return
    if data["status"]:
        game = discord.CustomActivity("Dana 3 is OPEN [" + str(round(data["weeks"][get_current_week_str()]["total_hours"],1)) + " hours this week]")
        await client.change_presence(status=discord.Status.online, activity=game)
    else:
        game = discord.CustomActivity("Dana 3 is EMPTY [" + str(round(data["weeks"][get_current_week_str()]["total_hours"],1)) + " hours this week]")
        await client.change_presence(status=discord.Status.dnd, activity=game)

@client.event
async def on_ready():
    await update_status()

@client.event
async def on_message(message):
    global data

    if message.author == client.user:
        return

    # print(888, repr(message.channel))

    if isinstance(message.channel, discord.DMChannel):
        if message.reference is not None:
            data["users"][message.author.id] = message.content
            await message.channel.send(f"thanks! I set your name/id to `{message.content}` (**quacks**)")
            await message.channel.send("if you want to change your name/id just REPLY to this message again")
            save()
        else:
            await message.channel.send(convo())
        return

    if client.user.mentioned_in(message):
        if "report" in message.content.lower():
            await message.reply("Currently, Dana 3 has been used for " + str(round(data["weeks"][get_current_week_str()]["total_hours"],2)) + " hours this week!")
            await message.channel.send("... and according to my records, " + ("someone" if data["status"] else "no one") + " is in the shop right now.")

        else:
            await message.reply(convo())

    if message.channel.name != "room-log":
        return

    # print(999)

    op = -1
    for i in 'gone.left.close.closed.empty.leave.leaving.done.bye.out.gn'.split("."):
        if i in message.content.lower():
            op = 0
            break
    for i in 'here.arriving.arrive.open.showed up.in.hello.hi'.split("."):
        if i in message.content.lower():
            op = 1
            break


    if op == 1:
        data["status"] = True
        await message.add_reaction("🦆")
        save()
        await update_status()


    elif op == 0:
        data["status"] = False
        await message.add_reaction("🦆")
        save()
        await update_status()


    if op >= 0:
        if str(message.author.id) not in data["users"].keys():
            dm = await message.author.create_dm()
            await dm.send("Hey there, I'm the Omniscient Attendance Duck that logs hours spent in Dana 3!")
            await dm.send("I don't know you yet, so please reply to this message with your name and WSU ID number so I know who you are.")


        if get_current_week_str() not in data["weeks"]:
            data["weeks"][get_current_week_str()] = {
                "total_hours": 0,
                "log": []
            }
        if op == 1:
            data["weeks"][get_current_week_str()]["log"].append({
                "user": message.author.id,
                "time": datetime.now().isoformat(),
                "state": "open"
            })
        elif op == 0:
            ts = datetime.now()

            try:
                last = data["weeks"][get_current_week_str()]["log"][-1]
            except IndexError:
                last = 0
            if last["state"] == "open":
                delta = ts - datetime.fromisoformat(last["time"])
                # await message.channel.send("last " + str(delta.total_seconds()) + " seconds")
                data["weeks"][get_current_week_str()]["total_hours"] += delta.total_seconds() / 3600
                # await message.channel.send(str(data["weeks"][get_current_week_str()]["total_hours"]) + "total hours")

            data["weeks"][get_current_week_str()]["log"].append({
                "user": message.author.id,
                "time": ts.isoformat(),
                "state": "close"
            })

    save()


    # print()

try:
    client.run(TOKEN)
except:
    save()
