from PluginManager import PluginManager
import discord
import traceback
import arrow
from os import system
from tinydb import TinyDB, where, Query
import arrow
from os import environ
from flask import Flask, render_template, send_from_directory
import _thread
import time
import socket
import urllib.request
import heroku3



logger = TinyDB("userlog.json")

print("[Noku]Initalizing Noku Bot!")
system("title NokuBot[DI]")
# Creates a discord client, which we will use to connect and interact with the server.
# All methods with @client.event annotations are event handlers for this client.
client = discord.Client()
print("[Noku]Loading plugins")
# Loads and initializes the plugin manager for the bot
pm = PluginManager("plugins", client)
pm.load_plugins()
pm.register_events()
selected_channel = ""
print("[Noku]Plugins loaded and registered")
#settings for crowd moderation
crowd_delete = "❌"
reacted = {}
counter_react = {}
react_info = {}
threshold = 5
nokusu = heroku3.from_key(environ.get('api')).apps()[0]

#user info for last online
online_users = {}
online_users_name = {}
online_users_obj = {}

#Web centric stuff/heroku

app = Flask(__name__, static_url_path='')
@app.route("/")
def main():
    return render_template('index.html', active_users=str(len(get_online_users(60))), users_table=generate_table(), commits=generate_commit())
    #return "Nokusu is online! :3\n There are {0} active users for the past hour.".format()

@app.route('/pluginsconfig/<path:path>')
def send_config(path):
    return send_from_directory('pluginsconfig', path)

def dummy():
    port = int(environ.get('PORT'))
    app.run(host='0.0.0.0', port=port)


def ping():
    while True:
        socket.setdefaulttimeout( 23 )  # timeout in seconds
        url = 'https://nokusu.herokuapp.com/'
        f = urllib.request.urlopen(url)
        x = f.read()
        time.sleep(120)



#bot stuff goes here.

@client.event
async def on_ready():
    """
    Event handler, fires when the bot has connected and is logged in
    """
    print('[Noku]Bot is ready under ' + client.user.name + " (" + client.user.id + ")")
    print('[Noku]Bot avatar updated!')
    # Change nickname to nickname in configuration
    for instance in client.servers:
        await client.change_nickname(instance.me, pm.botPreferences.nickName)
    game = discord.Game()
    rel = nokusu.releases()[len(list(nokusu.releases())) - 1]
    game.name = "NokuBot[v{0}@{1}]: ~help".format(rel.version, rel.description)
    await client.change_presence(game=game, afk=False)


@client.event
async def on_message(message):
    """
    Event handler, fires when a message is received in the server.
    :param message: discord.Message object containing the received message
    """
    try:
        #Adds/updates user to recently online
        if not message.author.bot:
            online_users[message.author.id] = arrow.now().timestamp
            online_users_name[message.author.id] = message.author.name
            online_users_obj[message.author.id] = message.author

        #Shows Users online in the past 2 minutes
        if message.content.startswith("~active") and message.author.id != client.user.id:
            span = 5
            try:
                span = int(message.content.split(" ")[1])
            except:
                pass
            x = "There are currently **{0}** Users active in the last {1} minutes".format(len(get_online_users(span)), span)
            if "verbose" in message.content:
                x += "\n```"
                for user in get_online_users(span):
                    x += online_users_name[user] + "\n"
                x += "```"
            
            await client.send_message(message.channel, x)

        #Custom hook for antispam/international
        await pm.handle_command(message, "_as-event.checkmessage", "")

        try:
            await pm.handle_command(message, "_server-event.checkmessage", "")
        except:
            pass

        #Hook for in message nokuchat
        if message.content.startswith("$>>") and message.author.id != client.user.id:
            if len(message.content[3:]) == 0:
                for server in client.servers:
                    x = ""
                    x += "Server: " + server.name + "```"
                    for channel in server.channels:
                        x += channel.name + " - " + channel.id + "\n"
                    x += "```"
                    await client.send_message(message.channel, x)
            else:
                selected_channel = message.content[3:]
                pm.active_channel = client.get_channel(selected_channel)
                await client.send_message(message.channel, "Changed channel to {0}".format(pm.active_channel))
        #Hook for in message nokuchat
        if message.content.startswith(">>>") and message.author.id != client.user.id:
            if len(message.content[3:]) != 0 and pm.active_channel != None:
                await client.send_message(pm.active_channel, message.content[3:])
            else:
                await client.send_message(message.channel, "No Channel selected!")

        #Mention Hook for nokubot's chatterbot 
        if client.user.mention in message.content.replace("<@!", "<@") and message.author.id != client.user.id:
            trigger = ["send", "nudes", "please"]
            words = message.content.partition(' ')

            print("[nokuEaster] Nood detector: {0}".format(len([y for y in trigger if y in message.content])))

            if len([y for y in trigger if y in message.clean_content]) >= 2:
                #await client.send_message(message.author, "Shhhh don't tell anyone okay?:P\nhttp://i.imgur.com/oatlOTr.png")
                await client.send_message(message.channel, "This easter egg has been removed because of user complaints. :(")
            else:
                await pm.handle_command(message, "chat", words[1:])

        #Hook for macro
        if message.content.startswith("~~") and message.author.id != client.user.id:
            if not "~~" in message.content[2:]:
                words = message.content[2:]
                await pm.handle_command(message, "m", ["m", words])

        #Plugin manager hook
        if message.content.startswith(pm.botPreferences.commandPrefix) and message.author.id != client.user.id:
            # Send the received message off to the Plugin Manager to handle the command
            words = message.content.partition(' ')
            await pm.handle_command(message, words[0][len(pm.botPreferences.commandPrefix):], words[1:])
        #else:
        #    await pm.handle_message(message)
    except Exception as e:
        #await client.send_message(message.channel, "`There was an error! Check console for more info.`")
        if pm.botPreferences.get_config_value("client", "debug") == "1":
            traceback.print_exc()


@client.event
async def on_typing(channel, user, when):
    """
    Event handler, fires when a user is typing in a channel
    :param channel: discord.Channel object containing channel information
    :param user: discord.Member object containing the user information
    :param when: datetime timestamp
    """
    try:
        await pm.handle_typing(channel, user, when)
    except Exception as e:
        await client.send_message(channel, "Error: " + str(e))
        if pm.botPreferences.get_config_value("client", "debug") == "1":
            traceback.print_exc()


@client.event
async def on_message_delete(message):
    """
    Event handler, fires when a message is deleted
    :param message: discord.Message object containing the deleted message
    """
    try:
        if message.author.name != "PluginBot":
            await pm.handle_message_delete(message)
    except Exception as e:
        await client.send_message(message.channel, "Error: " + str(e))
        if pm.botPreferences.get_config_value("client", "debug") == "1":
            traceback.print_exc()


@client.event
async def on_member_join(member):
    await pm.handle_member_join(member)


@client.event
async def on_member_remove(member):
    await pm.handle_member_leave(member)

@client.event
async def on_reaction_add(reaction, user):
    if reaction.emoji == crowd_delete and reaction.message.author.id != client.user.id:
        print("[Noku Crowd Moderation]Content Tagged for Moderation")
        if reaction.message.id in reacted:
            if not user.id in reacted[reaction.message.id]:
                threshold = int(len(get_online_users(5)) / 1.75)
                reacted[reaction.message.id].append(user.id)
                try:
                    print("[Noku Crowd Moderation]({1}/{2}){0} approved for deletion".format(user.name, len(reacted[reaction.message.id]), threshold))
                except:
                    pass
                if len(reacted[reaction.message.id]) - len(counter_react[reaction.message.id]) >= threshold:
                    await client.delete_message(react_info[reaction.message.id])
                    await client.delete_message(reaction.message)
            pass
        else:
            reacted[reaction.message.id] = [user.id]
            print("[Noku Crowd Moderation]({1}/{2}){0} approved for deletion".format(user.name, len(reacted[reaction.message.id]), threshold))
            await client.add_reaction(reaction.message, "⭕") 
            await client.add_reaction(reaction.message, "❌") 
            react_info[reaction.message.id] = await client.send_message(reaction.message.channel, "`{0}'s message has been tagged for crowd moderation. React with '❌' to vote for deletion, '⭕' to protect it.`".format(reaction.message.author))
            

    if reaction.emoji == "⭕":
        counter_react[reaction.message.id] = [user.id]

def get_online_users(span):

    users = []
    for x in online_users:
        #print("{0}@{2}:{1}".format(x, (arrow.utcnow().timestamp - int(online_users[x])), online_users[x]))
        if (arrow.utcnow().timestamp - int(online_users[x])) < (span * 60):
            users.append(x)
    return users

def generate_table():
    template = """<tr>
                  <td style="max-width: 50px"><img src="{0}" style="background-size: 40px 40px;
                  border-radius: 50%;
                  height: 40px;
                  width: 40px"></div></td>
                  <td>{1}</td>
                  <td>{2}</td>
                  </tr>"""
    ret = ""
    for x in online_users:
        #print("{0}@{2}:{1}".format(x, (arrow.utcnow().timestamp - int(online_users[x])), online_users[x]))
        if (arrow.utcnow().timestamp - int(online_users[x])) < (60 * 60):
            ret += template.format(online_users_obj[x].avatar_url, online_users_obj[x].name, arrow.get(int(online_users[x])).humanize())
    return ret
def generate_commit():
    rel = list(reversed(list(nokusu.releases())))

    template = """<tr>
                  <td>{0}</td>
                  </tr>"""
    ret = ""
    for x in range(0, 10):
        #print("{0}@{2}:{1}".format(x, (arrow.utcnow().timestamp - int(online_users[x])), online_users[x]))
            ret += template.format(str(rel[x]).replace("<", "").replace(">", ""))
    return ret

# Run the client and login with the bot token (yes, this needs to be down here)
print("Running Dummy Server")
_thread.start_new_thread( dummy , ())
print("Dummy Server is Running")
print("Running Heartbeat Service")
_thread.start_new_thread( ping , ())
print("Heartbeat Service is Running")
client.run(pm.botPreferences.token)

