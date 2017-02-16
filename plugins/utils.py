import datetime
from util import Events
from util.Ranks import Ranks
from tinydb import TinyDB, where, Query
import arrow
import random
from imgurpython import ImgurClient
import discord
import urbandict
import langdetect
import iso639
import requests


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.hugs = ['(づ￣ ³￣)づ', '(つ≧▽≦)つ', '(つ✧ω✧)つ', '(づ ◕‿◕ )づ', '(⊃｡•́‿•̀｡)⊃', '(つ . •́ _ʖ •̀ .)つ', '(っಠ‿ಠ)っ', '(づ◡﹏◡)づ']
        self.configPath = 'pluginsconfig/data_config-utils_a.json'
        self.configDB = TinyDB(self.configPath) 
        self.macroPath = 'pluginsconfig/data_macro_a.json'
        self.macroDB = TinyDB(self.macroPath)
        self.chaninfoPath = 'pluginsconfig/data_channel-info_a.json'
        self.chaninfDB = TinyDB(self.chaninfoPath)
        #self.converter = CurrencyConverter()
        print("[Noku-utils]Initalizing Imgur Stuff...")
        self.client = ImgurClient("43bdb8ab21d18b9", "fcba34a83a4650474ac57f6e3f8b0750dd26ecf5")
        print("[Noku-utils]Retrieving Images...")
        self.wmimages = self.client.subreddit_gallery("wholesomememes")
        self.catimages = self.client.subreddit_gallery("catsstandingup")
        self.dogimages = self.client.subreddit_gallery("rarepuppers")
        self.kanye = ["I miss the old Kanye, straight from the Go Kanye\nChop up the soul Kanye, set on his goals Kanye"
            ,"I hate the new Kanye, the bad mood Kanye\nThe always rude Kanye, spaz in the news Kanye"
            ,"I miss the sweet Kanye, chop up the beats Kanye"
            ,"I gotta say, at that time I'd like to meet Kanye"
            ,"See, I invented Kanye, it wasn't any Kanyes\nAnd now I look and look around and there's so many Kanyes"
            ,"I used to love Kanye, I used to love Kanye\nI even had the pink polo, I thought I was Kanye"
            ,"What if Kanye made a song about Kanye\nCalled 'I Miss The Old Kanye'? Man, that'd be so Kanye"
            ,"That's all it was Kanye, we still love Kanye\nAnd I love you like Kanye loves Kanye"]
        self.kanyeOrder = 0
        self.pats = [
        '{1}(ノ_<。)ヾ(´▽｀){0}',
        '{1}｡･ﾟ･(ﾉД`)ヽ(￣ω￣ ){0}', 
        '{1}ρ(-ω-、)ヾ(￣ω￣; ){0}',
        '{0}ヽ(￣ω￣(。。 )ゝ{1}',
        '{0}(*´I｀)ﾉﾟ(ﾉД｀ﾟ)ﾟ｡{1}',
        '{0}ヽ(~_~(・_・ )ゝ{1}',
        '{1}(ﾉ＿；)ヾ(´∀｀){0}',
        '{1}(；ω； )ヾ(´∀｀* ){0}',
        '{0}(*´ー)ﾉ(ノд`){1}',
        '{0}(´-ω-`( _ _ ){1}',
        '{0}(っ´ω｀)ﾉ(╥ω╥){1}',
        '{0}(ｏ・_・)ノ”(ノ_<、){1}']
        self.userqueue = []

    @staticmethod
    def register_events():
        return [
        Events.Command("ping", Ranks.Default,
            "Pings the bot, nothing special"),
        Events.Command("hug", Ranks.Default,
            "[@username] Sends a hug to a user."),
        Events.Command("system.purgeAllDM", Ranks.Admin,
            "(!Admin use only)~~Cause people are paranoid"),
        Events.Command("pat", Ranks.Default,
            "[@username] Sends a pat to a user."),
        Events.Command("info.set", Ranks.Admin),
        Events.Command("info.delete", Ranks.Admin),
        Events.Command("info", Ranks.Default,
            "Shows channel info"),
        Events.Command("meme", Ranks.Default,
            "posts a wholesome meme"),
        Events.Command("exch", Ranks.Default,
            "[ammount] [from] [to] converts currency"),
        Events.Command("ud", Ranks.Default,
            "[query] Urban Dictionary"),
        Events.Command("lang", Ranks.Default,
            "[query] Tries to determine the language"),
        Events.Command("cats", Ranks.Default,
            "Posts a cat"),
        Events.Command("emotext", Ranks.Default,
            "Emojifies a text"),
        Events.Command("poll", Ranks.Default,
            "[question]/[item1]/[item2]/[item3]/[item..] posts a poll and its corresponding reactions."),
        Events.Command("dogs", Ranks.Default,
            "Posts a dog"),
        Events.Command("old", Ranks.Default,
            "Kanye Kanye Kanye"),
        Events.Command("qjoin", Ranks.Default,
            "Join Queue"),
        Events.Command("qdone", Ranks.Default,
            "Finish Queue"),
        Events.Command("qview", Ranks.Default,
            "View Queue"),
        Events.Command("qkick", Ranks.Admin,
            "[Admin] Kick user from Queue"),
        Events.Command("qreset", Ranks.Default,
            "[Admin] Reset Queue"),
        Events.Command("qhelp", Ranks.Default,
            "View Queue"),
        Events.Command("pins", Ranks.Default,
            "[#channel] shows pins from a specified channel."),
        Events.Command("print_avatars_to_console", Ranks.Admin,
            "[secret stuff]"),
        Events.Command("utils.allow", Ranks.Admin),
        Events.Command("restart", Ranks.Admin),
        Events.Command("utils.block", Ranks.Admin)]

    async def handle_command(self, message_object, command, args):

        try:
            print("--{2}--\n[Noku-utils] {0} command from {1} by {3}".format(command, message_object.channel.name, arrow.now().format('MM-DD HH:mm:ss'), message_object.author.name))
        except:
            print("[Noku]Cannot display data, probably emojis.")        
        #print(args)
        config = Query()

        if self.configDB.contains(config.chanallow == message_object.channel.id) or message_object.channel.is_private:
            if command == "ping":
                await self.ping(message_object, "Pong")
            if command == "system.purgeAllDM":
                await self.purge(message_object)
            elif command == "pins":
                await self.showpins(message_object)
            elif command == "poll":
                await self.makepoll(message_object, args[1])
            elif command == "hug":
                await self.hug(message_object)
            elif command == "pat":
                await self.pat(message_object)
            elif command == "emotext":
                await self.emotext(message_object, args[1])
            elif command == "exch":
                await self.currency(message_object, args[1])
            elif command == "meme":
                await self.postmeme(message_object, self.wmimages)
            elif command == "ud":
                await self.urban(message_object, args[1])
            elif command == "lang":
                await self.lang(message_object, args[1])
            elif command == "cats":
                await self.postmeme(message_object, self.catimages)
            elif command == "dogs":
                await self.postmeme(message_object, self.dogimages)
            elif command == "old":
                await self.old(message_object, args[1])
            elif command == "info.set":
                await self.chaninfo(message_object, args[1], "set")
            elif command == "info.delete":
                await self.chaninfo(message_object, args[1], "delete")
            elif command == "info":
                await self.chaninfo(message_object, args[1], "info")
            elif command == "restart":
                await self.shutdown(message_object)
            elif command == "print_avatars_to_console":
                await self.getuser(message_object)

        if command == "qjoin":
            await self.qjoin(message_object)
        if command == "qdone":
            await self.qdone(message_object)
        if command == "qview":
            await self.qview(message_object)
        if command == "qkick":
            await self.qkick(message_object)
        if command == "qreset":
            await self.qreset(message_object)
        if command == "qhelp":
            await self.qhelp(message_object)

        if command == "utils.allow":
            await self.allowChan(message_object)
        if command == "utils.block":
            await self.blockChan(message_object)

    async def qhelp(self, message_object):
        em = discord.Embed(title="Queue Help", description="**~qjoin** : _Join Queue_\n**~qdone** : _Finish your turn_\n**~qview** : _Display the users in Queue_\n**~qkick** <@user> : _Kicks user from Queue (Admin only)_\n**~qreset** : _Resets Queue (Admin only)_", colour=0x007AFF)
        await self.pm.client.send_message(message_object.channel, embed=em)
        
    async def qkick(self, message_object):
        try:
            self.userqueue.remove(message_object.mentions[0])
            em = discord.Embed(title="Queue", description="{0} has been kicked from the Queue!".format(message_object.mentions[0].name), colour=0x007AFF)
        except:
            em = discord.Embed(title="Queue", description="No user specified or the user is not in the queue!", colour=0x007AFF)

        await self.pm.client.send_message(message_object.channel, embed=em)

    async def qreset(self, message_object):
        self.userqueue = []
        em = discord.Embed(title="Queue", description="The queue has been emptied!", colour=0x007AFF)
        await self.pm.client.send_message(message_object.channel, embed=em)

    async def qview(self, message_object):
        if len(self.userqueue) > 0:
            display = "There's currently {0} users in the queue.\n---\n".format(len(self.userqueue))
            count = 1
            for user in self.userqueue:
                display += "{0}. **{1}**\n".format(count, user.name)
                count += 1

            em = discord.Embed(title="Queue", description=display, colour=0x007AFF)
        else:
            em = discord.Embed(title="Queue", description="The queue is empty!", colour=0x007AFF)

        await self.pm.client.send_message(message_object.channel, embed=em)

    async def qdone(self, message_object):
        try:
            self.userqueue.remove(message_object.author)
            em = discord.Embed(title="Queue", description="You Successfuly left the Queue!", colour=0x007AFF)
        except:
            em = discord.Embed(title="Queue", description="You're not in the Queue!", colour=0x007AFF)

        await self.pm.client.send_message(message_object.channel, embed=em)
        await self.qview(message_object)

    async def qjoin(self, message_object):
        if not message_object.author in self.userqueue:
            self.userqueue.append(message_object.author)
            em = discord.Embed(title="Queue", description="{0} has been added to the queue!".format(message_object.author.name), colour=0x007AFF)
        else:
            em = discord.Embed(title="Queue", description="{0} is already in the queue!".format(message_object.author.name), colour=0x007AFF)

        await self.pm.client.send_message(message_object.channel, embed=em)
        await self.qview(message_object)

    async def currency(self, message_object, args):
        try:
            ammount = int(args.split(" ")[0])
            fr = args.split(" ")[1]
            to = args.split(" ")[2]
            re = requests.get("https://currency-api.appspot.com/api/{0}/{1}.json".format(fr.lower(),to.lower()))
            if re.json()["success"] or re.json()["success"] == "true":
                converted = ammount * float(re.json()["rate"])
                description = ":currency_exchange: **{0:,.2f} {1}** Equals **{2:,.2f} {3}**".format(ammount, fr.upper(), converted, to.upper())
                #em = discord.Embed(title=title, description=wjson["Weather"]["status"],)
                em = discord.Embed(title="Currency Exchange", description=description, colour=0x007AFF)
                em.set_footer(text="Current Rate: 1 {0} = {1} {2}".format( fr.upper(), re.json()["rate"], to.upper()))
            else:
                description = ":exclamation: _Invalid currency specified!_"
                #em = discord.Embed(title=title, description=wjson["Weather"]["status"], colour=0x007AFF)
                em = discord.Embed(title="Currency Exchange", description=description, colour=0x007AFF)

            await self.pm.client.send_message(message_object.channel, embed=em)
        except:
            description = ":information_source: Usage: [ammount] [from] [to]\nEx. `~exch 100 jpy usd`"
            em = discord.Embed(title="Currency Exchange", description=description, colour=0x007AFF)
            await self.pm.client.send_message(message_object.channel, embed=em)

    async def emotext(self, message_object, args):
        string = ""
        number = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
        for x in args.lower():
            try:
                if x in "qwertyuiopasdfghjklzxcvbnm":
                    string += ":regional_indicator_{0}: ".format(x)
                if x == " ":
                    string += "\n "
                if x in "1234567890":
                    string += ":{0}: ".format(number[int(x)])
            except:
                pass
        await self.pm.client.send_message(message_object.channel, string)

        pass

    async def lang(self, message_object, args):
        iso = langdetect.detect(args)
        x = "```{0}```Language result: {1}[{2}]".format(args, iso639.to_name(iso), iso639.to_native(iso))
        await self.pm.client.send_message(message_object.channel, x)

    async def urban(self, message_object, args):
        catalog = urbandict.define(args)
        em = discord.Embed(title='Urban Dictionary', description="Query: "+args, colour=0x007AFF)
        em.set_author(name='{0}\'s Result'.format(message_object.author.name))
        em.set_footer(text="Noku-utils version 0.3", icon_url=self.pm.client.user.avatar_url)
        em.add_field(name="Definiton", value=catalog[0]['def'])
        em.add_field(name="Example", value=catalog[0]['example'])
        await self.pm.client.send_message(message_object.channel, embed=em)

    async def purge(self, message_object):
        print("Purge: A") 
        for channels in self.pm.client.private_channels:
            if channels.is_private:
                print("Purge: B") 
                #try:
                print("Purge: B.5") 
                async for message in self.pm.client.logs_from(channels):
                    print("Purge: C") 
                    if message.author == self.pm.client.user:
                        try:
                            print("Purge: D") 
                            print("Delete:{0}".format(message.content))
                            await self.pm.client.delete_message(message)
                        except:
                            print("Purge: D.5") 
                            pass
                #except:
                #    pass
        pass

    async def makepoll(self, message_object, args):
        reactions = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯"]
        letter = "ABCDEFGHIJ"
        items = args.split("/")
        content = ":pencil:|**{0}**\n".format(items[0])
        count = 0
        for x in items[1:]:
            content += ":black_small_square: **{0}.** `{1}`\n".format(letter[count], x)
            count += 1
        message = await self.pm.client.send_message(message_object.channel, content)
        for x in range(0, count):
            await self.pm.client.add_reaction(message, reactions[x]) 
        await self.pm.client.delete_message(message_object)
        pass


    async def ping(self, message_object, reply):
        speed = datetime.datetime.now() - message_object.timestamp
        await self.pm.client.send_message(message_object.channel,
                                          reply + " " + str(round(speed.microseconds / 1000)) + "ms")

    async def old(self, message_object, args):
        if ".order" in args:
            args = args.replace(".order", args)
            await self.pm.client.send_message(message_object.channel, self.kanye[self.kanyeOrder].replace("Kanye", args))
            self.kanyeOrder = self.kanyeOrder + 1
            if self.kanyeOrder > len(self.kanye) - 1:
                self.kanyeOrder = 0
        else:
            await self.pm.client.send_message(message_object.channel, random.choice(self.kanye).replace("Kanye", args))

    async def getuser(self, message_object):
        for x in self.pm.client.get_all_members():
            print(x.avatar_url)

    async def hug(self, message_object):
        if len(message_object.mentions) != 0:
            await self.pm.client.send_message(message_object.channel, "{0} {1} {2}".format(message_object.author.mention, random.choice(self.hugs), message_object.mentions[0].mention))
        else:
            await self.pm.client.send_message(message_object.channel, ":exclamation:`Welp, that\'s not a valid user!`")

    async def pat(self, message_object):
        if len(message_object.mentions) != 0:
            await self.pm.client.send_message(message_object.channel, random.choice(self.pats).format(message_object.author.mention, message_object.mentions[0].mention))
        else:
            await self.pm.client.send_message(message_object.channel, ":exclamation:`Welp, that\'s not a valid user!`")

    async def macroadd(self, message_object, args):
        trigger = args.split(" ")[0]
        self.macroDB.insert({'trigger' : trigger, 'data' : args[len(trigger):]})
        await self.pm.client.send_message(message_object.channel, ":information_source:`{0} has been added as a macro!`".format(trigger))

    async def macrodel(self, message_object, args):
        self.macroDB.remove(Query().trigger == args)
        await self.pm.client.send_message(message_object.channel, ":information_source:`{0} has been deleted! Probably..`".format(args))

    async def helpUtil(self, message_object):
         await self.pm.client.send_message(message_object.channel, ":information_source: Help detail for Utilities")
         await self.pm.client.send_message(message_object.channel, "```~hug @user\n~ping\n~macro.add [trigger] [data]\n~macro.delete [trigger]\n~macro [trigger](alt. ~m)\n~macro.assigned```")

    async def macroShow(self, message_object, args):
        try:
            await self.pm.client.send_message(message_object.channel, self.macroDB.search(Query().trigger == args)[0]["data"])
        except:
            await self.pm.client.send_message(message_object.channel, ":exclamation:`Welp, that\'s not a valid macro!`")

    async def macroShowAssigned(self, message_object):
        macros = self.macroDB.search(Query().trigger != "")
        x = "```"
        for m in macros:
            x = x + m['trigger'] + " "
        x = x + "```"
        await self.pm.client.send_message(message_object.channel, x)


    async def chaninfo(self, message_object, args, trigger):
        #trigger = args.split(" ")[0]
        if trigger == "set":
            self.chaninfDB.remove(Query().channel == message_object.channel.id)
            self.chaninfDB.insert({'channel' : message_object.channel.id, 'data' : args})
            await self.pm.client.send_message(message_object.channel, ":information_source:`{0} info has been updated!`".format(trigger))
        elif trigger == "delete":
            self.chaninfDB.remove(Query().channel == message_object.channel.id)
            await self.pm.client.send_message(message_object.channel, ":information_source:`{0} info has been removed!`".format(trigger))
        else:
            try:
                await self.pm.client.send_message(message_object.channel, self.chaninfDB.search(Query().channel == message_object.channel.id)[0]["data"])
            except:
                await self.pm.client.send_message(message_object.channel, ":exclamation:No info! `~info set [message]` to set a channel info")

    async def postmeme(self, message_object, imagelist):
             await self.pm.client.send_message(message_object.channel, "{0}".format(random.choice(imagelist).link))

    async def showpins(self, message_object):
        try:
            if len(message_object.channel_mentions) > 0:
                for x in await self.pm.client.pins_from(message_object.channel_mentions[0]):
                    em = discord.Embed(title="\n", description=x.content, colour=0x007AFF)
                    em.set_author(name='{0} - {1}'.format(x.author.name, arrow.get(x.timestamp).format('MM-DD HH:mm')))
                    em.set_thumbnail(url=x.author.avatar_url)
                    await self.pm.client.send_message(message_object.channel, embed=em)
                pass
            else:
                await self.pm.client.send_message(message_object.channel, ":exclamation:No channel specified! Usage: `~pins [#channel]`")
        except:
            await self.pm.client.send_message(message_object.channel, ":exclamation:`Error retrieving pins!`")
            pass


    async def allowChan(self, message_object):
        self.configDB.insert({'chanallow' : message_object.channel.id});
        await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-utils has been allowed access to {0}`'.format(message_object.channel.name))

    async def blockChan(self, message_object):
        self.configDB.remove(Query().chanallow == message_object.channel.id);
        await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-utils has been blocked access to {0}`'.format(message_object.channel.name))

    async def shutdown(self, message_object):
        game = discord.Game()
        game.name = "Restarting...".format()
        await self.pm.client.change_presence(game=game, afk=False)
        await self.pm.client.send_message(message_object.channel, ':information_source:`さようなら {0}！ Noku bot is rebooting! <3`'.format(message_object.author.name))
        exit()