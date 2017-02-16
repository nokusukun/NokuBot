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
        self.modulename = 'role'
        self.configPath = 'pluginsconfig/data_config-{0}_a.json'.format(self.modulename)
        self.configDB = TinyDB(self.configPath) 
        self.rolePath = 'pluginsconfig/data_user-roles_h.json'
        self.roleDB = TinyDB(self.rolePath)
        self.roleposition = 15

    @staticmethod
    def register_events():
        return [Events.Command("myrole"),
        Events.Command("mytext"),
        Events.Command("role.allow", Ranks.Admin),
        Events.Command("role.block", Ranks.Admin)]

    async def handle_command(self, message_object, command, args):
        try:
            print("--{2}--\n[Noku-{4}] {0} command from {1} by {3}".format(command, message_object.channel.name, arrow.now().format('MM-DD HH:mm:ss'), message_object.author.name, self.modulename))
        except:
            print("[Noku]Cannot display data, probably emojis.")   

        if self.configDB.contains(Query().chanallow == message_object.channel.id):
            '''
            Add modules checks here
            '''
            if command == "myrole":
                await self.myRole(message_object, args[1])
            if command == "mytext":
                await self.myRoleText(message_object, args[1])

        #Do not modify or add anything below it's for permissions
        if command == "{0}.allow".format(self.modulename):
            await self.allowChan(message_object)
        if command == "{0}.block".format(self.modulename):
            await self.blockChan(message_object)


    '''
    Add modules here
    '''
    async def myRole(self, message_object, args):
        if args != "":
            color = args.split(" ")[0]
            try:
                roleText = args[len(color):]
            except:
                roleText = message_object.author.name + "'s Color"

            if re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color):
                print("\t[Debug-]{0}".format(args))
                if self.roleDB.contains((Query().user == message_object.author.id) & (Query().server == message_object.server.id)):
                    role = discord.Role(
                        server=message_object.server.id, 
                        id=self.roleDB.search((Query().user == message_object.author.id) & (Query().server == message_object.server.id))[0]['role'] )
                    
                    print("\t[Debug-]{0}".format("Modifying Role"))
                    await self.pm.client.edit_role(message_object.server, role, 
                        name=roleText, 
                        color=discord.Colour(int(color[1:], 16)))
                else:
                    print("\t[Debug-]{0}".format("Creating Role"))
                    newrole = await self.pm.client.create_role(message_object.server)
                    newrole.name = message_object.author.name + "'s Color"
                    newrole.colour = discord.Colour((int(color[1:], 16)))
                    self.roleDB.insert({'user' : message_object.author.id,
                    'role' : newrole.id,
                    'server' : message_object.server.id})
                    print("\t[Debug-]{0}".format("Setting Role to User"))
                    await self.pm.client.add_roles(message_object.author, newrole)
                    print("\t[Debug-]{0}".format("Editing Role Properties"))
                    await self.pm.client.edit_role(message_object.server, newrole, 
                        name=message_object.author.name + "'s Color", 
                        color=discord.Colour(int(color[1:], 16)))
                    print("\t[Debug-]{0}".format("Setting Role Position"))
                    await self.pm.client.move_role(message_object.server, newrole, self.roleposition) 
                    print("\t[Debug-]{0}".format("Done!"))
                await self.pm.client.send_message(message_object.channel, ':information_source:`Your custom role has been changed to {0}!`'.format(args))
            else:
                await self.pm.client.send_message(message_object.channel, ':information_source:`{0} is an invalid Hex colour!`'.format(args))

        else:
            await self.pm.client.send_message(message_object.channel, ':information_source:`Usage: ~myrole [#color] [text?]`'.format(message_object.author.mention))

    async def myRoleText(self, message_object, args):
        if args != "":
            print("\t[Debug-]{0}".format(args))
            if self.roleDB.contains((Query().user == message_object.author.id) & (Query().server == message_object.server.id)):
                role = discord.Role(
                    server=message_object.server.id, 
                    id=self.roleDB.search((Query().user == message_object.author.id) & (Query().server == message_object.server.id))[0]['role'] )
                print("\t[Debug-]{0}".format("Modifying Role"))
                await self.pm.client.edit_role(message_object.server, role, 
                    name=args)
        else:
            await self.pm.client.send_message(message_object.channel, ':information_source:`Usage: ~mytext [text]`'.format(message_object.author.mention))


    #Do not modify or add anything below it's for permissions
    async def allowChan(self, message_object):
        self.configDB.insert({'chanallow' : message_object.channel.id});
        await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-{1} has been allowed access to {0}`'.format(message_object.channel.name, self.modulename))

    async def blockChan(self, message_object):
        self.configDB.remove(Query().chanallow == message_object.channel.id);
        await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-{1} has been blocked access to {0}`'.format(message_object.channel.name, self.modulename))
