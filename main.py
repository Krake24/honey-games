#!/bin/env python3
import os
import json
import shelve
import atexit
import disnake
from disnake.ext import commands

db = shelve.open("db", flag="c", writeback=True)

def exit_handler():
    db.close()

atexit.register(exit_handler)

if not "users" in db:
   db["users"] = {}

users = db["users"]

intents = disnake.Intents.default()
intents.members = True

bot = commands.InteractionBot(intents=intents, activity=disnake.Game(name="Honeyland"))

f = open("rewards.json", "r")
rewards = json.loads(f.read())

def or_else(result, default):
   if result: 
      return result
   return default

def get_user_reward(user, placement):
   if user in users and placement in users[user]:
      reward = users[user][placement]
      if "Choose each time" != reward:
        return reward
   return None

def get_account_info(user):
  info = ""
  if user in users and "account_name" in users[user]:
    info = f":arrow_right: {users[user]['account_name']}"
  return info 

@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))

@bot.slash_command(name="game_default_prizes_reset")
async def game_prizes_config_reset(inter):
    del users[inter.user.id]["first"]
    del users[inter.user.id]["second"]
    del users[inter.user.id]["third"]
    embed=disnake.Embed(
      title="Game Prizes",
      color=disnake.Colour.yellow(),
      description=
f'''Your default prizes have been reset.
If you win a prize you will be asked which one you'll get each time.
'''
    )
    await inter.response.send_message(embed=embed, ephemeral=True)

@bot.slash_command(name="game_account_reset", description="add info to your Honeyland account to facilitate paying out prizes")
async def game_account_reset(inter):
    del users[inter.user.id]["account_name"]
    embed=disnake.Embed(
      title="Game Prizes",
      color=disnake.Colour.yellow(),
      description=
f'''Your account details have been reset. The game hosts will ask you to provide these, should you win a prize.
'''
    )
    await inter.response.send_message(embed=embed, ephemeral=True)

@bot.slash_command(name="game_show_defaults", description="shows your current settings")
async def game_account(inter):
    user = inter.user.id

    if not user in users:
       users[user]={}

    if "account_name" in users[user]:
      ingame_name = users[user]["account_name"]
    else:
      ingame_name = "---"
    
    hint=""
    if not "first" in users[user]:
       hint = "You haven't selected default prizes yet. You can do so by using the command /game_default_prizes"

    embed=disnake.Embed(
      title="Game Account Setting",
      color=disnake.Colour.yellow(),
      description=
f'''These are your current settings:

**Prizes:**
:first_place: {or_else(get_user_reward(user, "first"), "Please choose a prize")}
:second_place: {or_else(get_user_reward(user, "second"), "Please choose a prize")}
:third_place: {or_else(get_user_reward(user, "third"), "Please choose a prize")}

**Account**
Honeyland Account Name: {ingame_name}
''')
    await inter.response.send_message(embed=embed, ephemeral=True)

@bot.slash_command(name="game_account", description="add info to your Honeyland account to facilitate paying out prizes")
async def game_account(
   inter,
   ingame_name: str
   ):
    user = inter.user.id

    if not user in users:
       users[user]={}

    users[user]["account_name"] = ingame_name
    
    hint=""
    if not "first" in users[user]:
       hint = "You haven't selected default prizes yet. You can do so by using the command /game_default_prizes"

    embed=disnake.Embed(
      title="Game Account Setting",
      color=disnake.Colour.yellow(),
      description=
f'''Your account settings have been saved
Honeyland Account Name: {ingame_name}

{hint}
'''
    )
    await inter.response.send_message(embed=embed, ephemeral=True)

@bot.slash_command(name="game_default_prizes", description="Tell us which prizes you want in case you finish in certain positions")
async def game_default_prizes(
   inter,
   first: str = commands.Param(choices=rewards["first"]), 
   second: str = commands.Param(choices=rewards["second"]), 
   third: str = commands.Param(choices=rewards["third"])
   ):
    user = inter.user.id

    if not user in users:
       users[user]={}

    users[user]["first"] = first
    users[user]["second"] = second
    users[user]["third"] = third
    
    hint=""
    if not "account" in users[user]:
       hint = "You haven't added account details yet to deliver your prizes. Please do so by using /game_account"

    embed=disnake.Embed(
      title="Game Prizes",
      color=disnake.Colour.yellow(),
      description=
f'''Your default prizes have been set to the following:

:first_place: {or_else(get_user_reward(user, "first"), "Please choose a prize")}
:second_place: {or_else(get_user_reward(user, "second"), "Please choose a prize")}
:third_place: {or_else(get_user_reward(user, "third"), "Please choose a prize")}

If you want to change these rewards run this command again. 
{hint}
'''
    )
    await inter.response.send_message(embed=embed, ephemeral=True)

@bot.slash_command(name="game_winners", default_member_permissions=disnake.Permissions(moderate_members=True), description="Print out the winners and their account and prize info")
async def game_winners(inter, first: disnake.User, second: disnake.User, third: disnake.User):
    embed=disnake.Embed(
      title="Game Winners",
      color=disnake.Colour.yellow(),
      description=
f''':first_place: <@{first.id}> ({or_else(get_user_reward(first.id, "first"), "Please setup your gaming account (see below)")} {get_account_info(first.id)})
:second_place: <@{second.id}> ({or_else(get_user_reward(second.id, "second"), "Please setup your gaming account (see below)")} {get_account_info(second.id)})
:third_place: <@{third.id}> ({or_else(get_user_reward(third.id, "third"), "Please setup your gaming account (see below)")} {get_account_info(third.id)})

**IMPORTANT!**
Everyone who plays discord games, in order to be eligible for prizes, please set up your game profile by entering username and the prize of your choice as follows: 

Make sure you are in ⁠<#933556625652989973>
Step 1: use the /game_account command and enter your in game username
Step 2: Use the /game_default_prizes command and choose your prizes for first, second, and third place from the lists
'''
    )
    await inter.response.send_message(embed=embed)


bot.run(os.environ['botToken'])
