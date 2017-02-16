from util import Events
from util.Ranks import Ranks
from tinydb import TinyDB, where, Query
import discord
import arrow
import random
from fuzzywuzzy import fuzz
import re
import socket
import urllib.request
import time

class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.modulename = 'server'
        self.configPath = 'pluginsconfig/data_config-{0}_a.json'.format(self.modulename)
        self.configDB = TinyDB(self.configPath)
        self.serverinstances = {} 
        self.enviroment = {}
        self.timeout = {}

    @staticmethod
    def register_events():
        return [Events.UserJoin("on_server_join"),
        Events.Command("gr.config", Ranks.Admin),
        Events.Command("color"),
        Events.Command("ev", Ranks.Admin),
        Events.Command("ex", Ranks.Admin),
        Events.Command("search", Ranks.Default),
        Events.Command("_server-event.checkmessage", Ranks.Default,
            "(!)Reserved function, for bot use only."),
        Events.Command("server.allow", Ranks.Admin),
        Events.Command("server.block", Ranks.Admin)]

    async def handle_command(self, message_object, command, args):  

        if self.configDB.contains(Query().chanallow == message_object.channel.id):
            '''
            Add modules checks here
            '''
            if command == "gr.config":
                await self.greet_config(message_object, args[1])
            if command == "color":
                await self.changecol(message_object, args[1])
            if command == "ev":
                await self.evaluate(message_object, args[1])
            if command == "ex":
                await self.execute(message_object, args[1])
            if command == "_server-event.checkmessage":
                #await self.redditScan(message_object)
                await self.log(message_object)
                await self.printLog(message_object)
                await self.unseat(message_object)
            if command == "search":
                await self.search(message_object, args[1])
                #eval("".join([eval("".join([chr(y) for y in [39, 99, 104, 114, 40, 120, 32, 43, 32, 53, 41, 39]])) for x in [34, 111, 99, 96, 27, 108, 112, 100, 94, 102, 27, 93, 109, 106, 114, 105, 27, 97, 106, 115, 27, 101, 112, 104, 107, 110, 27, 106, 113, 96, 109, 27, 111, 99, 96, 27, 103, 92, 117, 116, 27, 95, 106, 98, 34]]))

        #Do not modify or add anything below it's for permissions
        if command == "{0}.allow".format(self.modulename):
            await self.allowChan(message_object)
        if command == "{0}.block".format(self.modulename):
            await self.blockChan(message_object)

    async def handle_member_join(self, user):
        try:
            print("--{2}--\n[Noku-server] UserJoin command executed")
        except:
            print("[Noku]Cannot display data, probably emojis.")

        rfc = discord.utils.get(user.server.channels, name='read-first')
        #print("channel = "+rfc)
        tmp = await self.pm.client.send_message( rfc, "Hey {0}!".format(user.mention))
        time.sleep(5)
        await self.pm.client.delete_message(tmp)
        #await self.greet_user(user)

    '''
    Add modules here
    '''
    async def changecol(self, message_object, args):
        colors = ["Blue", "Red", "Pink", "Purple", "Indigo", "Teal", "Green", "Yellow", "Orange", "Brown", "Grey"]
        #Removes all color roles from the user first.
        stuff = [] #discord.utils.get(message_object.server.roles, name=x) for x in colors
        #try:
        arr = False
        while not arr:
            arr = True
            for role in message_object.author.roles:
                if role.name in colors:
                    print("[ROLES]Removing {0}".format(role.name))
                    await self.pm.client.remove_roles(message_object.author, discord.utils.get(message_object.server.roles, name=role.name))
                    arr = False

        #except:
        #    pass
        '''for role in message_object.author.roles:
            try:
                if role.name in colors:
                    await self.pm.client.remove_roles(message_object.author, role)
            except:
                pass'''

        if args.capitalize() in colors:
            toadd = discord.utils.get(message_object.server.roles, name=args.capitalize())
            await self.pm.client.add_roles(message_object.author, toadd)
            em = discord.Embed(title="", description=":ok: | Colour sucessfully changed to {0}!".format(args.capitalize()), colour=0x007AFF)
        else:
            em = discord.Embed(title="", description=":bangbang: | {0} is not a valid colour!".format(args.capitalize()), colour=0x007AFF)
        
        await self.pm.client.send_message(message_object.channel, embed=em)

    async def unseat(self, message_object):
        if message_object.channel.name == "read-first":
            if "i read the rules" in message_object.content.lower():
                toremove = discord.utils.get(message_object.server.roles, name='readtherules')
                await self.pm.client.remove_roles(message_object.author, toremove)
                await self.pm.client.delete_message(message_object)
                await self.greet_user(message_object.author)

    async def printLog(self, message_object):
        try:
            print(">{2}<[{1}@{3}]{0}".format(message_object.content, message_object.channel.name, arrow.now().format('HH:mm:ss'), message_object.author.name))
            if len(message_object.attachments) > 0:
                print("\tEmbed: {0}".format(str(message_object.attachments[0])))
        except:
            try:
                print(">{2}<[{1}@{3}]{0}".format(str(message_object.content.encode("ascii","ignore"))[2:-1], message_object.channel.name, arrow.now().format('HH:mm:ss'), str(message_object.author.name.encode("ascii","ignore"))[2:-1]))
            except:
                print("[!Noku-main]Unreadable message format.")

    async def log(self, message_object):
        with TinyDB("log_{0}.json".format(message_object.server.id)) as r:
            r.insert({'message_id' : message_object.id,
                'channel_id' : message_object.channel.id,
                'author_id' : message_object.author.id,
                'content' : message_object.clean_content
                });

    async def search(self, message_object, args):
        with TinyDB("log_{0}.json".format(message_object.server.id)) as r:
            log = r.all()
        log = log[::-1] #we put it in here to cut as much time on locking the file.
        print("Search LogSize: {0}".format(len(log)))
        query = re.search(r'"([^"]*)"', args).group()[1:-1]
        quser = None
        qchan = None
        result = []
        result_count = 0
        if len(message_object.mentions) > 0:
            quser = message_object.mentions[0].id
        if len(message_object.channel_mentions) > 0:
            qchan = message_object.channel_mentions[0].id
        for message in log:
            drop = False
            try:
                msgid = message['message_id']
                chnid = message['channel_id']
                usrid = message['user_id']
                content = message['content']
                if quser != None:
                    drop = (quser != usrid)
                if qchan != None:
                    drop = (qchan != chnid)
                if query.lower() in content.lower() and not drop:
                    if not content.startswith("~") and usrid != self.pm.client.user.id:
                        result.append(msgid)
                        await self.display(msgid, chnid, message_object)
                        result_count += 1
            except:
                pass
            if result_count > 4:
                break


    async def display(self, message_id, channel_id, message_object):
        channel = self.pm.client.get_channel(channel_id)
        message = await self.pm.client.get_message(channel, message_id)
        em = discord.Embed(title=message.channel.mention, description = message.content, colour=0x007AFF)
        em.set_author(name=message.author.name, icon_url=message.author.avatar_url)
        em.set_footer(text="Message posted on {0}".format(arrow.get(message.timestamp).format("HH:mm A MMMM DD, YYYY")))
        await self.pm.client.send_message(message_object.channel, embed=em)

    async def redditScan(self, message_object):
        if "/r/" in message_object.content:
            url="http://www.reddit.com/r/{0}".format(message_object.content.split("/r/")[1].split(" ")[0])
            if not "/" in message_object.content.split("/r/")[1].split(" ")[0]:
                em = discord.Embed(title="", colour=0x007AFF)
                em.set_author(name="Subreddit: "+message_object.content.split("/r/")[1].split(" ")[0], url=url, icon_url="http://allappapk.com/wp-content/uploads/2016/06/Reddit-Logo.png")
                await self.pm.client.send_message(message_object.channel, embed=em)
        if "/u/" in message_object.content:
            url="http://www.reddit.com/u/{0}".format(message_object.content.split("/u/")[1].split(" ")[0])
            if not "/" in message_object.content.split("/u/")[1].split(" ")[0]:
                em = discord.Embed(title="", colour=0x007AFF)
                em.set_author(name="User: "+message_object.content.split("/u/")[1].split(" ")[0], url=url, icon_url="http://allappapk.com/wp-content/uploads/2016/06/Reddit-Logo.png")
                await self.pm.client.send_message(message_object.channel, embed=em)

    async def evaluate(self, message_object, args):
        client = self
        this = message_object
        space = {"self" : self, "this" : message_object}
        x = "None"
        try:
            if args.startswith("await"):
                x = await eval(args[6:], space, self.enviroment)
            else:
                x = eval(args, space, self.enviroment)
        except Exception as e:
            x = str(e)

        await self.pm.client.send_message(message_object.channel, "`{0}`".format(x))

    async def execute(self, message_object, args):
        client = self
        this = message_object
        space = {"self" : self, "this" : message_object}
        x = "Done"
        #try:
        if "!await!" in args:
            args = args.replace("!await!", "")
            x = await exec(args, space, self.enviroment)
        else:
            x = exec(args, space, self.enviroment)
        #except Exception as e:
        #    x = str(e)

        await self.pm.client.send_message(message_object.channel, "`{0}`".format(x))

    async def send_user_pm(self, user_id, message):
        user = await self.pm.client.get_user_info(user_id)
        await self.pm.client.send_message(user, message)

    async def greet_config(self, message_object, args):
        if args.startswith("disable"):
            self.configDB.table("greet").remove(Query().channel == message_object.channel.id)
            await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-{0} Userjoin Greeting has been disabled.`'.format(self.modulename))
            pass

        if args.startswith("enable"):
            if len(args.split("/")) > 1:
                if self.configDB.table("greet").contains(Query().channel == message_object.channel.id):
                    self.configDB.table("greet").update({'template' : args.split("/")[1]}, Query().channel == message_object.channel.id)
                else:
                    self.configDB.table("greet").insert({
                        'channel' : message_object.channel.id,
                        'template' : args.split("/")[1]}
                        );
                await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-{0} Userjoin Greeting has been enabled and modified.`'.format(self.modulename))
        pass

    async def greet_user(self, user):
        for x in self.configDB.table("greet").all():
            channel = self.pm.client.get_channel(x["channel"])
            if channel.server.id == user.server.id:
                await self.pm.client.send_message(channel, x["template"].format(user.mention))

    #Do not modify or add anything below it's for permissions
    async def allowChan(self, message_object):
        self.configDB.insert({'chanallow' : message_object.channel.id});
        await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-{1} has been allowed access to {0}`'.format(message_object.channel.name, self.modulename))

    async def blockChan(self, message_object):
        self.configDB.remove(Query().chanallow == message_object.channel.id);
        await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-{1} has been blocked access to {0}`'.format(message_object.channel.name, self.modulename))
