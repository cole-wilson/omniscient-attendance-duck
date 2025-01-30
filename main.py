import json
import discord
from datetime import datetime, timedelta
import random
import os
import math

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
        json.dump(data, datafile, indent=2)

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

def get_current_total():
    ts = datetime.now()
    if len(data["weeks"].keys()) == 0:
        return 0

    try:
        last = data["weeks"][get_current_week_str()]["log"][-1]
    except IndexError:
        return 0

    if last["state"] == "open":
        delta = ts - datetime.fromisoformat(last["time"])
        # await message.channel.send("last " + str(delta.total_seconds()) + " seconds")
        return data["weeks"][get_current_week_str()]["total_hours"] + delta.total_seconds() / 3600
    else:
        return data["weeks"][get_current_week_str()]["total_hours"]


async def update_status():
    if data["status"]:
        game = discord.CustomActivity("Dana 3 is OPEN [" + str(round(get_current_total(),2)) + " hours this week]")
        await client.change_presence(status=discord.Status.online, activity=game)
    else:
        game = discord.CustomActivity("Dana 3 is EMPTY [" + str(round(get_current_total(),2)) + " hours this week]")
        await client.change_presence(status=discord.Status.do_not_disturb, activity=game)

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
        elif str(message.author.id) in os.getenv("MOD_USERS").split("."):
            if "dump" in message.content:
                save()
                file = discord.File("data/data.json", filename="data.json")
                # embed = discord.Embed()
                await message.channel.send(file=file)
            else:
                await message.channel.send(convo())

        else:
            await message.channel.send(convo())
        return

    if client.user.mentioned_in(message) or "duck" in message.content.lower() or "quack" in message.content.lower():
        if "report" in message.content.lower() or "status" in message.content.lower():
            await message.add_reaction("🫡")
            t = get_current_total()
            h = int(t)
            m = math.floor((t*60) % 60)
            s = math.floor((t*3600) % 60)

            await message.reply(f"Currently, Dana 3 has been used for {h} hours, {m} minutes, and {s} seconds this week! According to my records, " + ("someone" if data["status"] else "no one") + " is in the shop right now.")

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
            data["weeks"][get_current_week_str()]["total_hours"] = get_current_total()
            data["weeks"][get_current_week_str()]["log"].append({
                "user": message.author.id,
                "time": datetime.now().isoformat(),
                "state": "close"
            })

    save()


    # print()

try:
    client.run(TOKEN)
except:
    save()
