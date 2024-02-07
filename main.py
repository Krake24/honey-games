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


def get_user_reward(user, placement):
   if user in users and placement in users[user]:
      reward = users[user][placement]
      if "Choose each time" != reward:
        return reward
   return "Please choose a prize and tag your game host"

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

:first_place: {get_user_reward(user, "first")}
:second_place: {get_user_reward(user, "second")}
:third_place: {get_user_reward(user, "third")}

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
f''':first_place: <@{first.id}> ({get_user_reward(first.id, "first")} {get_account_info(first.id)})
:second_place: <@{second.id}> ({get_user_reward(second.id, "second")} {get_account_info(second.id)})
:third_place: <@{third.id}> ({get_user_reward(third.id, "third")} {get_account_info(third.id)})
'''
    )
    await inter.response.send_message(embed=embed)


bot.run(os.environ['botToken'])
