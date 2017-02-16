from util import Events
from util.Ranks import Ranks
from tinydb import TinyDB, where, Query
import discord
import arrow
import random
import re

class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.modulename = 'macros'
        self.configPath = 'pluginsconfig/data_config-{0}_a.json'.format(self.modulename)
        self.configDB = TinyDB(self.configPath) 
        self.macroPath = 'pluginsconfig/data_macro_a.json'
        self.macroDB = TinyDB(self.macroPath)

    @staticmethod
    def register_events():
        return [
        Events.Command("m", Ranks.Default,
            "[tag] [content] use ~m to show all tags, ~m [tagname] to show a macro, ~m [tagname] [content] to make a new tag"),
        #Events.Command("~", Ranks.Default,
        #    "(alias, see m)"),
        Events.Command("md", Ranks.Default,
            "[tag] deletes a self created macro"),
        Events.Command("admd", Ranks.Default,
            "[tag] deletes a macro as an admin"),
        Events.Command("macros.allow", Ranks.Admin),
        Events.Command("macros.block", Ranks.Admin)]

    async def handle_command(self, message_object, command, args):
        try:
            print("--{2}--\n[Noku-macro] {0} command from {1} by {3}".format(command, message_object.channel.name, arrow.now().format('MM-DD HH:mm:ss'), message_object.author.name))
        except:
            print("[Noku]Cannot display data, probably emojis.")   

        if self.configDB.contains(Query().chanallow == message_object.channel.id):
            '''
            Add modules checks here
            '''
            if command == "admd":
                await self.macrodel(message_object, args[1])
            if command == "md":
                await self.mdelete(message_object, args[1])
            elif command == "m" or command == "~":
                if args[1] == "":
                    await self.macroShowAssigned(message_object)
                elif  len(args[1].split(" ")) > 1:
                    await self.macroadd(message_object, args[1])
                else:
                    await self.macroShow(message_object, args[1])


        #Do not modify or add anything below it's for permissions
        if command == "{0}.allow".format(self.modulename):
            await self.allowChan(message_object)
        if command == "{0}.block".format(self.modulename):
            await self.blockChan(message_object)


    '''
    Add modules here
    '''
    async def macroadd(self, message_object, args):
        trigger = args.split(" ")[0]
        if re.match("^[a-zA-Z0-9_]*$", trigger):
            if len(self.macroDB.search(Query().trigger == trigger)) == 0:
                self.macroDB.insert({
                    'trigger' : trigger, 
                    'data' : args[len(trigger):],
                    'owner' : message_object.author.id})
                await self.pm.client.send_message(message_object.channel, ":information_source:`{0} has been added as a macro!`".format(trigger))
                await self.pm.client.delete_message(message_object)

            else:
                await self.pm.client.send_message(message_object.channel, ":exclamation:`{0} is already an assigned tag!`".format(trigger))
                await self.pm.client.delete_message(message_object)
        
        else:
            await self.pm.client.send_message(message_object.channel, ":exclamation:`{0} contains symbols!`".format(trigger))
            await self.pm.client.delete_message(message_object)

    async def macrodel(self, message_object, args):
        triggers = args.split(" ")
        for trigger in triggers:
            if len(self.macroDB.search(Query().trigger == trigger)) > 0:
                self.macroDB.remove(Query().trigger == trigger)
                await self.pm.client.send_message(message_object.channel, ":information_source:`{0} has been deleted!`".format(trigger))
            else:
                await self.pm.client.send_message(message_object.channel, ":exclamation:`{0} does not exist!`".format(trigger))
        
        await self.pm.client.delete_message(message_object)


    async def mdelete(self, message_object, args):
        trigger = args.split(" ")[0]
        macroData = self.macroDB.search(Query().trigger == trigger)
        if len(macroData) > 0:
            if macroData[0]['owner'] == message_object.author.id:
                self.macroDB.remove(Query().trigger == trigger)
                await self.pm.client.send_message(message_object.channel, ":information_source:`{0} has been deleted!`".format(args))
            else:
                await self.pm.client.send_message(message_object.channel, ":exclamation:`You do not own the {0} tag!`".format(trigger))
                await self.pm.client.delete_message(message_object)
        else:
            await self.pm.client.send_message(message_object.channel, ":exclamation:`{0} does not exist!`".format(trigger))
            await self.pm.client.delete_message(message_object)

    async def macroShow(self, message_object, args):
        try:
            await self.pm.client.send_message(message_object.channel, self.macroDB.search(Query().trigger == args)[0]["data"])
        except:
            await self.pm.client.send_message(message_object.channel, ":exclamation:`Welp, that\'s not a valid macro!`")
        await self.pm.client.delete_message(message_object)

    async def macroShowAssigned(self, message_object):
        macros = self.macroDB.search(Query().trigger != "")
        x = "Currently available macros:```"
        count = 1
        for m in macros:
            x = x + "{0:14.14}".format(m['trigger'])
            if count == 4:
                x = x + "\n"
                count = 0
            count = count + 1
        x = x + "```"
        await self.pm.client.send_message(message_object.channel, x)

    #Do not modify or add anything below it's for permissions
    async def allowChan(self, message_object):
        self.configDB.insert({'chanallow' : message_object.channel.id});
        await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-{1} has been allowed access to {0}`'.format(message_object.channel.name, self.modulename))

    async def blockChan(self, message_object):
        self.configDB.remove(Query().chanallow == message_object.channel.id);
        await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-{1} has been blocked access to {0}`'.format(message_object.channel.name, self.modulename))
