#!/bin/env python3
import shelve
import json

db = shelve.open("db", flag="c", writeback=True)

f = open("migration_v1.json", "r")
replacements = json.loads(f.read())

def replace(old):
    return replacements[old]

users = db['users']
for user in users:
    settings = users[user]
    for place in ["first", "second", "third"]:
        settings[place] = replace(settings[place])