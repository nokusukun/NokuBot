from util import Events
from util.Ranks import Ranks
from tinydb import TinyDB, where, Query
import discord
import arrow
import quotegen
import re

class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.modulename = 'quotegen'
        self.configPath = 'data_config-{0}_a.json'.format(self.modulename)
        self.configDB = TinyDB(self.configPath) 

    @staticmethod
    def register_events():
        return [
        Events.Command("quotegen", Ranks.Default,
            "Generates a quote from "),
        Events.Command("quotegen.allow", Ranks.Admin),
        Events.Command("quotegen.block", Ranks.Admin)]

    async def handle_command(self, message_object, command, args):
        try:
            print("--{2}--\n[Noku-macro] {0} command from {1} by {3}".format(command, message_object.channel.name, arrow.now().format('MM-DD HH:mm:ss'), message_object.author.name))
        except:
            print("[Noku]Cannot display data, probably emojis.")   

        if self.configDB.contains(Query().chanallow == message_object.channel.id):
            '''
            Add modules checks here
            '''
            if command == "quotegen":
                await self.generate_quote(message_object, args[1])

        #Do not modify or add anything below it's for permissions
        if command == "{0}.allow".format(self.modulename):
            await self.allowChan(message_object)
        if command == "{0}.block".format(self.modulename):
            await self.blockChan(message_object)


    '''
    Add modules here
    '''
    async def generate_quote(self, message_object, args):
        corpus = ""
        for log in TinyDB("{0}@{1}.json".format(message_object.server.name, message_object.server.id)).search(Query().channel == message_object.channel.id):
            if re.match("\w*", log["content"]):
                corpus = corpus + log['content'] + "\n"

        textmodel = markovify.NewlineText(corpus)
        textmodel.make_short_sentence(120)
        await self.pm.client.send_message(message_object.channel, '*{0} says...*\n```{1}```'.format(message_object.channel.name, textmodel.make_short_sentence(120)))
    #Do not modify or add anything below it's for permissions
    async def allowChan(self, message_object):
        self.configDB.insert({'chanallow' : message_object.channel.id});
        await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-{1} has been allowed access to {0}`'.format(message_object.channel.name, self.modulename))

    async def blockChan(self, message_object):
        self.configDB.remove(Query().chanallow == message_object.channel.id);
        await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-{1} has been blocked access to {0}`'.format(message_object.channel.name, self.modulename))
