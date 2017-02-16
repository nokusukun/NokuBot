from util import Events
from util.Ranks import Ranks
from tinydb import TinyDB, where, Query
import discord
import arrow
import random
import re
import asyncio
from fuzzywuzzy import fuzz

class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.modulename = 'antispam'
        self.configPath = 'pluginsconfig/data_config-{0}_a.json'.format(self.modulename)
        self.configDB = TinyDB(self.configPath) 
        self.users = {}
        self.userimg = {}
        self.userlm = {}
        self.cooldown = {}
        self.channelconfig = {}
        self.exempted = []
        self.text = False
        self.attachments = False
        self.timeout = {}
        self.timeoutspan = {}
        self.timeoutmember = {}
        self.running = False
        try:
            for x in self.configDB.table('cooldown').all():
                self.cooldown[x['channel']] = x['value']
                print("Sucessfully updated {1} antispam cooldown to {0} seconds".format(x['value'], x['channel']))

            for x in self.configDB.table('exempt').all():
                self.exempted.append(x['user'])
                print("Sucessfully exempted {0}".format(x['user']))

            for x in self.configDB.table('scan').all():
                self.channelconfig[x['channel']] = [x['text'], x['attachments']]
                print("Sucessfully updated {0} antispam configuration to {1}/{2}".format(x['channel'], x['text'], x['attachments']))

            #x = self.configDB.table('scan').search(Query().name == 'text')
            #if len(x) > 0:
            #    self.text = bool(x[0]['value'])
            #x = self.configDB.table('scan').search(Query().name == 'attachments')
            #if len(x) > 0:
            #    self.attachments = bool(x[0]['value'])

        except:
            pass
        

    @staticmethod
    def register_events():
        return [
        Events.Command("as.setcooldown", Ranks.Admin,
            "[seconds] sets message cooldown before a user can post again."),
        Events.Command("as.exempt", Ranks.Admin,
            "[@username] exempts user from the antispam."),
        Events.Command("as.filter", Ranks.Admin,
            "[text true/false] [attachment true/false] Sets antispam configuration"),
        Events.Command("_as-event.checkmessage", Ranks.Default,
            "(!)Reserved function, for bot use only."),
        Events.Command("antispam.allow", Ranks.Admin),
        Events.Command("timeout", Ranks.Admin),
        Events.Command("antispam.block", Ranks.Admin)]

    async def handle_command(self, message_object, command, args):

        if self.configDB.contains(Query().chanallow == message_object.channel.id):
            '''
            Add modules checks here
            '''
            if command == "as.setcooldown":
                await self.setcooldown(message_object, args[1])
            if command == "as.exempt":
                await self.exempt(message_object)
            if command == "as.filter":
                await self.config(message_object, args[1])
            if command == "_as-event.checkmessage":
                await self.checkmessage(message_object)

        if command == "timeout".format():
            await self._timeout(message_object, args[1])
        #Do not modify or add anything below it's for permissions
        if command == "{0}.allow".format(self.modulename):
            await self.allowChan(message_object)
        if command == "{0}.block".format(self.modulename):
            await self.blockChan(message_object)

        await self.checktm()

    '''
    Add modules here
    '''

    async def _timeout(self, message_object, args):
        try:
            span = int(args.split(" ")[0]) * 60
            target = message_object.mentions[0]
            if not target in self.timeout:
                self.timeout[target.id] = arrow.utcnow().timestamp
                self.timeoutspan[target.id] = span
                self.timeoutmember[target.id] = target
                toadd = discord.utils.get(message_object.server.roles, name="Timeout")
                await self.pm.client.add_roles(target, toadd)
                em = discord.Embed(title="Timeout", description="**{0}** has been muted for {1} seconds".format(target.name, span), colour=0x007AFF)
        except:
            em = discord.Embed(title="Timeout", description="*Wrong syntax*\nUsage: **timeout <span> <@user>**", colour=0x007AFF)
        await self.pm.client.send_message(message_object.channel, embed=em)

    async def checktm(self):
        if not self.running:
            self.running = True
            while True:
                try:
                    if len(self.timeoutmember) > 0:
                        for id, user in self.timeoutmember.items():
                            if (arrow.utcnow().timestamp - arrow.get(self.timeout[user.id]).timestamp) > int(self.timeoutspan[user.id]):
                                torole = discord.utils.get(user.server.roles, name="Timeout")
                                arr = False
                                while not arr:
                                    arr = True
                                    if torole in user.roles:
                                        print("[ROLES]Removing {0}".format(torole.name))
                                        await self.pm.client.remove_roles(user, torole)
                                        arr = False
                                del self.timeoutmember[user.id]
                except:
                    print("An error has occured!")
                print("Timeout Cycle")
                await asyncio.sleep(10)

    async def exempt(self, message_object):
        if len(message_object.mentions) != 0:
            for x in message_object.mentions:
                self.configDB.table('exempt').insert({
                    'user' : x.id
                    })
                self.exempted.append(x.id)
                await self.pm.client.send_message(message_object.channel, 
                    ":information_source: > `Successfuly exempted {0}`".format(x.name))
        else:
            await self.pm.client.send_message(message_object.channel, 
                ":information_source: > `Invalid parameter must be mentioned @username`".format())

    async def config(self, message_object, args):
        try:
            if args.split(" ")[0] in "true false":
                if args.split(" ")[1] in "true false":
                    self.configDB.table('scan').remove(Query().channel == message_object.channel.id)
                    self.configDB.table('scan').insert({
                        'text' : args.split(" ")[0],
                        'attachments' : args.split(" ")[1],
                        'channel' : message_object.channel.id
                        })
                    self.channelconfig[message_object.channel.id] = [args.split(" ")[0], args.split(" ")[1]]
                    await self.pm.client.send_message(message_object.channel,
                        ":information_source: > `Set configuration for text: {0}, attachments: {1} on {2}`".format(args.split(" ")[0] ,args.split(" ")[1], message_object.channel.name))
                else:
                    await self.pm.client.send_message(message_object.channel,
                        ":information_source: > `[{0}] invalid paramter`".format(args.split(" ")[1]))
            else:
                await self.pm.client.send_message(message_object.channel,
                    ":information_source: > `[{0}] invalid paramter`".format(args.split(" ")[0]))
        except:
            pass

    async def setcooldown(self, message_object, args):
        if self.isInt(args):
            self.configDB.table('cooldown').insert({
                'channel' : message_object.channel.id,
                'value' : args
                })
            self.cooldown = args
            await self.pm.client.send_message(message_object.channel, 
                ":information_source: > `Successfuly updated antispam cooldown to {0} seconds`".format(args))
        else:
            await self.pm.client.send_message(message_object.channel, 
                ":information_source: > `Invalid parameter (must be int)`".format())

    async def checkmessage(self, message_object):
        if message_object.author.id in self.exempted:
            print("Exempted user {0}".format(message_object.author.id))
            pass
        else:
            #print("TESTA {0} {1}".format(self.channelconfig[message_object.channel.id][0], self.channelconfig[message_object.channel.id][1]))
            if self.channelconfig[message_object.channel.id][0] == 'true':
                print("TESTB")
                if message_object.author.id in self.users:
                    print("TESTC: {0}".format(arrow.utcnow().timestamp - arrow.get(self.users[message_object.author.id]).timestamp))
                    #print("TEST*: {0}".format(int(self.cooldown[message_object.channel.id])))
                    treshold = 100
                    if len(message_object.content) > 50:
                        treshold = 90
                    if len(message_object.content) > 200:
                        treshold = 84

                    if (arrow.utcnow().timestamp - arrow.get(self.users[message_object.author.id]).timestamp) < int(self.cooldown[message_object.channel.id]) and fuzz.ratio(self.userlm[message_object.author.id], message_object.content) >= treshold:
                        print("`Noku Bot[Antispam]: Treshold: {1}, Length: {2} Message Deleted: {0}`".format(message_object.author, treshold, len(message_object.content)))
                        await self.pm.client.delete_message(message_object)
                        self.users[message_object.author.id] = arrow.utcnow().timestamp
                        self.userlm[message_object.author.id] = message_object.content
                    else:
                        self.users[message_object.author.id] = arrow.utcnow().timestamp
                        self.userlm[message_object.author.id] = message_object.content
                else:
                    print("TESTE")
                    self.users[message_object.author.id] = arrow.utcnow().timestamp
                    self.userlm[message_object.author.id] = message_object.content

            if self.channelconfig[message_object.channel.id][1] == 'true' and (self.hasURL(message_object.content) or self.hasAttach(message_object)):
                print("TESTB2")
                if message_object.author.id in self.userimg:
                    print("TESTC2: {0}".format(arrow.utcnow().timestamp - arrow.get(self.userimg[message_object.author.id]).timestamp))
                    if (arrow.utcnow().timestamp - arrow.get(self.userimg[message_object.author.id]).timestamp) < int(self.cooldown[message_object.channel.id]):
                        print("{0}'s' Message Deleted".format(message_object.author.name))
                        await self.pm.client.delete_message(message_object)
                        self.userimg[message_object.author.id] = arrow.utcnow().timestamp
                    else:
                        self.userimg[message_object.author.id] = arrow.utcnow().timestamp
                else:
                    #print("TESTE2")
                    self.userimg[message_object.author.id] = arrow.utcnow().timestamp




    def isInt(self, integer):
        try:
            int(integer)
            return True
        except:
            return False
        pass

    def hasURL(self, string):
        if len(re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)) == 0:
            return False
        else:
            return True

    def hasAttach(self, message_object):
        #print("AttachScan: {0} - {1}".format(len(message_object.attachments), len(message_object.embeds)))
        if len(message_object.attachments) == 0 and len(message_object.embeds) == 0:
            return False
        else:
            return True
        
    #Do not modify or add anything below it's for permissions
    async def allowChan(self, message_object):
        self.configDB.insert({'chanallow' : message_object.channel.id});
        await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-{1} has been allowed access to {0}`'.format(message_object.channel.name, self.modulename))

    async def blockChan(self, message_object):
        self.configDB.remove(Query().chanallow == message_object.channel.id);
        await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-{1} has been blocked access to {0}`'.format(message_object.channel.name, self.modulename))
