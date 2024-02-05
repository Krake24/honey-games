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
print(users)

intents = disnake.Intents.default()
intents.members = True

bot = commands.InteractionBot(intents=intents)

f = open("rewards.json", "r")
rewards = json.loads(f.read())

@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))

def get_user_reward(user, placement):
   if user in users and placement in users[user]:
      reward = users[user][placement]
      if "Choose each time" != reward:
        return reward
   return "Please choose a prize and tag your game host"

@bot.slash_command(name="game_prizes_config_reset")
async def game_prizes_config_reset(inter):
    users[inter.user.id] = {}
    embed=disnake.Embed(
      title="Game Prizes",
      color=disnake.Colour.yellow(),
      ephemeral=True,
      description=f'''You default prizes have been reset.
      If you win a prize you will be asked which one you'll get each time.
      '''
    )
    await inter.response.send_message(embed=embed, ephemeral=True)

@bot.slash_command(name="game_prizes_config")
async def game_prizes_config(inter, first: str = commands.Param(choices=rewards["first"]), second: str = commands.Param(choices=rewards["second"]), third: str = commands.Param(choices=rewards["third"])):
    user = inter.user.id
    print(user)
    users[user] = {
       "first" : first,
       "second" : second,
       "third" : third
    }
    embed=disnake.Embed(
      title="Game Prizes",
      color=disnake.Colour.yellow(),
      description=f'''Your default prizes have been set to the following
      First place: {get_user_reward(user, "first")}
      Second place: {get_user_reward(user, "second")}
      Third place: {get_user_reward(user, "third")}

      If you want to change these rewards run this command again. 
      '''
    )
    await inter.response.send_message(embed=embed, ephemeral=True)

@bot.slash_command(name="game_winners", default_member_permissions=disnake.Permissions(moderate_members=True))
async def game_winners(inter, first: disnake.User, second: disnake.User, third: disnake.User):
    embed=disnake.Embed(
      title="Game Winners",
      color=disnake.Colour.yellow(),
      description=f'''First place: <@{first.id}> ({get_user_reward(first.id, "first")})
      Second place: <@{second.id}> ({get_user_reward(second.id, "second")})
      Third place: <@{third.id}> ({get_user_reward(third.id, "third")})
      '''
    )
    await inter.response.send_message(embed=embed)


bot.run(os.environ['botToken'])
