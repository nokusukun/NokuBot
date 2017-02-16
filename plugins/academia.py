from util import Events
from util.Ranks import Ranks
from tinydb import TinyDB, where, Query
import discord
import arrow
import random
#import tungsten
import pyowm
import json

class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.modulename = 'academia'
        self.configPath = 'pluginsconfig/data_config-{0}_a.json'.format(self.modulename)
        #self.waclient = tungsten.Tungsten("V48XKW-W2RE7VWR99") #V48XKW-W2RE7VWR99
        self.configDB = TinyDB(self.configPath) 
        self.chatinstances = {} 
        self.owm = pyowm.OWM("d458741c71140c009b31f4cfd05560ba")

    @staticmethod
    def register_events():
        return [Events.Command("ask", Ranks.Default,
            "[query] Ask him a question or anything analytical"),
        Events.Command("w", Ranks.Default,
            "[query] Posts weather data."),
        Events.Command("academia.allow", Ranks.Admin),
        Events.Command("academia.block", Ranks.Admin)]

    async def handle_command(self, message_object, command, args):
        try:
            print("--{2}--\n[Noku-chat] {0} command from {1} by {3}".format(command, message_object.channel.name, arrow.now().format('MM-DD HH:mm:ss'), message_object.author.name))
        except:
            print("[Noku]Cannot display data, probably emojis.")   

        if self.configDB.contains(Query().chanallow == message_object.channel.id):
            '''
            Add modules checks here
            '''
            if command == "ask":
                await self.ask(message_object, args[1])
            if command == "w":
                await self.weather(message_object, args[1])


        #Do not modify or add anything below it's for permissions
        if command == "{0}.allow".format(self.modulename):
            await self.allowChan(message_object)
        if command == "{0}.block".format(self.modulename):
            await self.blockChan(message_object)


    '''
    Add modules here
    '''

    async def weather(self, message_object, args):
        if args != "":
            await self.pm.client.send_typing(message_object.channel)
            obs = self.owm.weather_at_place(args)
            wjson = json.loads(obs.to_JSON())
            wobj = obs.get_weather()
            title = ":flag_{0}: **{1}, {2}**".format(wjson["Location"]["country"].lower(), wjson["Location"]["name"], wjson["Location"]["country"])
            #em = discord.Embed(title=title, description=wjson["Weather"]["status"], colour=0x007AFF)
            em = discord.Embed(title=title, description="{6} | :thermometer: **{0}°C** (_{1}°F_) from **{2}** to **{3}°C**, wind at **{4}m/s**, humidity at **{5}%**".format(wobj.get_temperature("celsius")["temp"], 
                                                                                                                                                    wobj.get_temperature("fahrenheit")["temp"],
                                                                                                                                                    wobj.get_temperature("celsius")["temp_min"],
                                                                                                                                                    wobj.get_temperature("celsius")["temp_max"],
                                                                                                                                                    wjson["Weather"]["wind"]["speed"],
                                                                                                                                                    wjson["Weather"]["humidity"],
                                                                                                                                                    wobj.get_status()), colour=0x007AFF)
            
            #em.add_field(name=":thermometer: Temperature", value=":black_small_square: Min: {0}°C[{3}°F]\n:black_small_square: Avg: {1}°C[{4}°F]\n:black_small_square: Max: {2}°C[{5}°F]\n".format(wobj.get_temperature("celsius")["temp_min"],wobj.get_temperature("celsius")["temp"],wobj.get_temperature("celsius")["temp_max"],wobj.get_temperature("fahrenheit")["temp_min"],wobj.get_temperature("fahrenheit")["temp"],wobj.get_temperature("fahrenheit")["temp_max"]))
            #em.add_field(name=":droplet: Humidity", value=":black_small_square: {0}%".format(wjson["Weather"]["wind"]["deg"], wjson["Weather"]["wind"]["speed"]))
            #em.add_field(name=":wind_chime: Wind", value=":arrow_upper_right: {0}\n:dash: :{1}m/s".format())
            #em.set_footer(text="Noku-academia module version 2.0.1, weather version 0.4.0", icon_url=self.pm.client.user.avatar_url)
            await self.pm.client.send_message(message_object.channel, embed=em)
        else:
            await self.pm.client.send_message(message_object.channel, ':information_source:`Usage: [location] gets weather data for location.`'.format())


    #Do not modify or add anything below it's for permissions
    async def allowChan(self, message_object):
        self.configDB.insert({'chanallow' : message_object.channel.id});
        await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-{1} has been allowed access to {0}`'.format(message_object.channel.name, self.modulename))

    async def blockChan(self, message_object):
        self.configDB.remove(Query().chanallow == message_object.channel.id);
        await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-{1} has been blocked access to {0}`'.format(message_object.channel.name, self.modulename))
