import discord
from discord.ext import commands
import random
import json
import time

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================== IMAGE LINKS ==================
IMG_AWAKEN = "https://cdn.discordapp.com/attachments/1442886780608053308/1487031818526916608/latest.png"
IMG_PVP_WIN = "https://cdn.discordapp.com/attachments/1442886780608053308/1487031975259930746/content.png"
IMG_DEATH = "https://cdn.discordapp.com/attachments/1442886780608053308/1487032088900272188/content.png"
IMG_REINCARNATE = "https://media.discordapp.net/attachments/1442886780608053308/1487032248443076678/content.png"
IMG_LORE = "https://cdn.discordapp.com/attachments/1442886780608053308/1487032349270212689/content.png"
IMG_ROAST = "https://cdn.discordapp.com/attachments/1442886780608053308/1487032479004098670/content.png"

# ================== DATA ==================
try:
    with open("users.json", "r") as f:
        users = json.load(f)
except:
    users = {}

def save():
    with open("users.json", "w") as f:
        json.dump(users, f)

def get_user(uid):
    if uid not in users:
        users[uid] = {
            "power": 10,
            "deaths": 0,
            "level": 1,
            "xp": 0,
            "alive": True,
            "last_daily": 0,
            "reputation": 0
        }
    return users[uid]

# ================== TITLE ==================
def get_title(user):
    if user["deaths"] > 10:
        return "Frequent Corpse ☠️"
    elif user["power"] > 100:
        return "Harbinger of Violence ⚔️"
    elif user["level"] > 5:
        return "Evolving Threat 🧬"
    elif not user["alive"]:
        return "Currently Irrelevant 💀"
    else:
        return "Insignificant Being"

# ================== SMART ROAST ==================
def smart_roast(user, name):
    if user["deaths"] > 8:
        return f"{name} has respawned more than they’ve succeeded."
    elif user["power"] < 15:
        return f"{name}'s power level feels like a suggestion, not a stat."
    elif user["level"] > 5:
        return f"{name} climbed levels but forgot skill."
    elif not user["alive"]:
        return f"{name} is currently dead. Improvement noted."
    else:
        return f"{name} exists… aggressively average."

# ================== LORE ==================
lore = [
    "The world does not reward kindness. Only strength.",
    "You were not chosen. You survived.",
    "Every death refines you.",
    "Trust is a luxury of the weak."
]

# ================== EVENTS ==================
@bot.event
async def on_ready():
    print(f"{bot.user} has awakened...")

# ================== COMMANDS ==================

@bot.command()
async def awaken(ctx):
    get_user(str(ctx.author.id))
    save()

    embed = discord.Embed(title="Awakening",
                          description="You awaken in chaos. The world does not care.")
    embed.set_image(url=IMG_AWAKEN)

    await ctx.send(embed=embed)

@bot.command()
async def status(ctx):
    user = get_user(str(ctx.author.id))
    title = get_title(user)

    await ctx.send(
        f"Title: {title}\nLevel: {user['level']} | Power: {user['power']} | XP: {user['xp']} | Deaths: {user['deaths']}"
    )

@bot.command()
async def fight(ctx):
    user = get_user(str(ctx.author.id))

    if not user["alive"]:
        await ctx.send("You are dead. Stay that way.")
        return

    if random.randint(1, 100) > 50:
        gain = random.randint(5, 15)
        user["power"] += gain
        user["xp"] += 10
        msg = "Violence remains undefeated."
    else:
        user["power"] -= 5
        user["deaths"] += 1
        user["alive"] = False
        user["reputation"] -= 3

        embed = discord.Embed(title="Death",
                              description="You died. The system barely noticed.")
        embed.set_image(url=IMG_DEATH)

        save()
        await ctx.send(embed=embed)
        return

    if user["xp"] >= 50:
        user["level"] += 1
        user["xp"] = 0
        user["power"] += 10
        msg += "\nYou evolved."

    save()
    await ctx.send(msg)

@bot.command()
async def pvp(ctx, opponent: discord.Member):
    attacker = get_user(str(ctx.author.id))
    defender = get_user(str(opponent.id))

    if not attacker["alive"] or not defender["alive"]:
        await ctx.send("One of you is already dead.")
        return

    total = attacker["power"] + defender["power"]
    roll = random.randint(1, total)

    if roll <= attacker["power"]:
        winner, loser = attacker, defender
        wname, lname = ctx.author.name, opponent.name
        img = IMG_PVP_WIN
    else:
        winner, loser = defender, attacker
        wname, lname = opponent.name, ctx.author.name
        img = IMG_DEATH

    winner["power"] += random.randint(10, 20)
    winner["xp"] += 15
    winner["reputation"] += 5

    loser["power"] -= 10
    loser["deaths"] += 1
    loser["alive"] = False
    loser["reputation"] -= 5

    msg = f"{wname} erased {lname}. {lname} will be remembered… briefly."

    embed = discord.Embed(title="PvP Result", description=msg)
    embed.set_image(url=img)

    save()
    await ctx.send(embed=embed)

@bot.command()
async def reincarnate(ctx):
    user = get_user(str(ctx.author.id))

    if user["alive"]:
        await ctx.send("You are still alive.")
        return

    user["alive"] = True
    user["power"] += 5

    embed = discord.Embed(title="Reincarnation",
                          description="You return. Not stronger… just less weak.")
    embed.set_image(url=IMG_REINCARNATE)

    save()
    await ctx.send(embed=embed)

@bot.command()
async def lore(ctx):
    embed = discord.Embed(title="Lore Fragment",
                          description=random.choice(lore))
    embed.set_image(url=IMG_LORE)

    await ctx.send(embed=embed)

@bot.command()
async def roast(ctx, target: discord.Member = None):
    if target is None:
        target = ctx.author

    user = get_user(str(target.id))
    roast = smart_roast(user, target.name)

    embed = discord.Embed(title="Judgment", description=roast)
    embed.set_image(url=IMG_ROAST)

    await ctx.send(embed=embed)

@bot.command()
async def reputation(ctx):
    user = get_user(str(ctx.author.id))
    rep = user["reputation"]

    if rep > 20:
        status = "Feared 🩸"
    elif rep < -20:
        status = "Mocked 🤡"
    else:
        status = "Unknown"

    await ctx.send(f"Reputation: {rep} ({status})")

import os
bot.run(os.getenv("TOKEN"))