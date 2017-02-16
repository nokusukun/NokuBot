from util import Events
from util.Ranks import Ranks
from tinydb import TinyDB, where, Query
import arrow
import random
from operator import itemgetter
import discord

class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.petcooldown = 3600
        self.feedcooldown = 1200
        self.database = 'pluginsconfig/data_I.json'
        self.userDBPath = 'pluginsconfig/data_usr_D.json'
        self.configPath = 'pluginsconfig/data_config_a.json'
        self.configDB = TinyDB(self.configPath) 
        self.db = TinyDB(self.database)
        self.userDB = TinyDB(self.userDBPath)
        self.food = [':chocolate_bar:', ':apple:', ':pear:', ':peach:', ':banana:']
        #self.status = ['dead', 'starving', 'hungry', 'content', 'amused', ]
        self.status = {0 : 'happy', 1 : 'happy', 2 : 'happy', 
        3 : 'amused', 4 : 'amused', 5 : 'amused', 
        6 : 'content', 7 : 'content', 8 : 'content', 
        9 : 'hungry', 10 : 'hungry', 11 : 'hungry', 
        12 : 'starving', 13 : 'starving', 14 : 'starving', 
        15 : 'dead'}
        self.emojistatus = {0 : ':smile:', 1 : ':smile:', 2 : ':smile:', 
        3 : ':slight_smile:', 4 : ':slight_smile:', 5 : ':slight_smile:', 
        6 : ':neutral_face:', 7 : ':neutral_face:', 8 : ':neutral_face:', 
        9 : ':unamused:', 10 : ':unamused:', 11 : ':unamused:', 
        12 : ':ok_hand: :joy: :gun:', 13 : ':ok_hand: :joy: :gun:', 14 : ':ok_hand: :joy: :gun:',
        15 : ':skull_crossbones:'}
        self.petavatar = ["http://i.imgur.com/2onQOX3.png",
        "http://i.imgur.com/3cSuvnh.png",
        "http://i.imgur.com/EmqYVoA.png",
        "http://i.imgur.com/Pht7mMp.png",
        "http://i.imgur.com/5a2r2rx.png",
        "http://i.imgur.com/jV9aAU5.png",
        "http://i.imgur.com/YWw7wCi.png",
        "http://i.imgur.com/YoVyAu5.png",
        "http://i.imgur.com/YxPtNvv.png"]

        print('[NokuBot] Loaded Pet Database {0}\n[NokuBot] Loaded User Database {1}'.format(self.database, self.userDBPath))

    @staticmethod
    def register_events():
        """
        Define events that this plugin will listen to
        :return: A list of util.Events
        """
        return [Events.Command("pet"), 
        Events.Command("mate"), 
        Events.Command("stat"), 
        Events.Command("feed"), 
        Events.Command("kill"),
        Events.Command("slut"),
        Events.Command("talive"),
        Events.Command("tpets"),
        Events.Command("allpets"),
        Events.Command("pets.allow", Ranks.Admin),
        Events.Command("pets.block", Ranks.Admin)] 

    async def handle_command(self, message_object, command, args):
        """
        Handle Events.Command events
        :param message_object: discord.Message object containing the message
        :param command: The name of the command (first word in the message, without prefix)
        :param args: List of words in the message
        """
        try:
            print("--{2}--\n[Noku] {0} command from {1} by {3}".format(command, message_object.channel.name, arrow.now().format('MM-DD HH:mm:ss'), message_object.author.name))
        except:
            print("[Noku]Cannot display data, probably emojis.")
                #print(args)
        config = Query()

        if self.configDB.contains(config.chanallow == message_object.channel.id):
            if command == "mate":
                await self.fuck(message_object, command, args[1])
            if command == "stat":
                await self.stat(message_object, args[1])
            if command == "feed":
                await self.feed(message_object, args[1])
            if command == "kill":
                await self.kill(message_object, args[1])
            if command == "slut":
                await self.slut(message_object, args[1])
            if command == "pet":
                await self.pet(message_object, args[1])
            if command == "talive":
                await self.aliveBoard(message_object)
            if command == "tpets":
                await self.petBoard(message_object)
            if command == "allpets":
                await self.allPets(message_object)

        if command == "pets.allow":
            await self.allowChan(message_object)
        if command == "pets.block":
            await self.blockChan(message_object)


    async def fuck(self, message_object, command, args):
        """
        Fuck command, neat name huh
        Changed to mate to reflect wholesomeness~
        """
        #print('[fuck] command executed by {0}'.format(message_object.author.name))
        db = self.db
        pet = Query()
        user = Query()
        if args == "" or message_object.author.id == message_object.mentions[0].id:
            await self.pm.client.send_message(message_object.channel, ':exclamation:`Specify another user to mate with!`')
        else:
            if len(message_object.mentions) != 0:
                if len(db.search(pet.owner == message_object.author.mention)) == 0:
                    lenx = int(len(message_object.author.name)/2)
                    leny = int(len(message_object.mentions[0].name)/2)
                    name = message_object.author.name[0:lenx] + message_object.mentions[0].name[leny:]

                    db.insert({'owner': message_object.author.mention, 
                        'ownerName' : message_object.author.name,
                        'assfucked': message_object.mentions[0].mention, 
                        'assfuckedName' : message_object.mentions[0].name,
                        'level': 1, 
                        'status': 5,
                        'pets' : 0,
                        'avatarImg' : random.choice(range(0,len(self.petavatar) - 1)),
                        'born': arrow.utcnow().timestamp,
                        'feed' : arrow.utcnow().timestamp,
                        'name': '{0}'.format(name),
                        'qname' : name.lower()})

                    userdata = self.userDB.search(user.username == message_object.author.mention)
                    if len(userdata) == 0:
                        self.userDB.insert({'username' : message_object.author.mention,
                            'lastpet' : arrow.utcnow().replace(hours=-1).timestamp,
                            'lastfeed': arrow.utcnow().replace(hours=-1).timestamp,
                            'previous': 0,
                            'food' : 0})
                    else:
                        self.userDB.update({'previous' : int(userdata[0]['previous']) + 1 }, user.username == message_object.author.mention)

                    await self.pm.client.send_message(message_object.channel, '{0.author.mention}'.format(message_object) + ' mated with ' + args + ' and {0} was born!'.format(name))
                else:
                    await self.pm.client.send_message(message_object.channel, ':exclamation:`Welp, you already have a pet!`')
            else:
                await self.pm.client.send_message(message_object.channel, ':exclamation:`Welp, that\'s not a valid user!`')


    async def stat(self, message_object, args):
        #print('[stat] command executed by {0}'.format(message_object.author.name))
        db = self.db
        pet = Query()
        if args == "":
            petdata = db.search(pet.owner == message_object.author.mention)
        else:
            petdata = db.search(pet.qname == args.lower())

        if len(petdata) == 0:
            #im suffering from split personality where the error check sometimes switches around.
            await self.pm.client.send_message(message_object.channel, ':exclamation:`You currenly have no pets or no pet with the name specified found!`')
        else:
            status = arrow.get((arrow.get(petdata[0]['feed']).timestamp - arrow.utcnow().timestamp) * -1).hour
            if status >= 15:
                statText = 'is deader than your great grandma'
                status = 15
            else:
                statText ='is alive and {0}'.format(self.status[status])

            print("Debug:{0}".format(petdata[0]['avatarImg']))

            em = discord.Embed(title='', description="Mood: "+self.emojistatus[status], colour=0x007AFF)
            em.set_author(name='{0}\'s Information'.format(petdata[0]['name']))
            em.set_footer(text="Noku Bot version 3.1.2", icon_url=self.pm.client.user.avatar_url)
            #em.set_image(url=self.pm.client.user.avatar_url)
            em.add_field(name="Status", value='{0} {1}'.format(petdata[0]['name'], statText), inline=True)
            em.add_field(name="Level", value=petdata[0]['level'])
            em.add_field(name="Owner", value=petdata[0]['ownerName'])
            em.add_field(name="Partner", value=petdata[0]['assfuckedName'])
            em.add_field(name="Birthdate", value=arrow.get(petdata[0]['born']).format("MMMM Do, YYYY"))
            em.add_field(name="Born", value=arrow.get(petdata[0]['born']).humanize())
            em.add_field(name="Last Feed", value=arrow.get(petdata[0]['feed']).humanize())
            em.add_field(name="Pets from users", value=petdata[0]['pets'])
            em.set_thumbnail(url=self.petavatar[petdata[0]['avatarImg']])
            await self.pm.client.send_message(message_object.channel, embed=em)    
            #await self.pm.client.send_message(message_object.channel, 'Stat page for: {0} {5}\n```{0} {1}!\nFed {2}\nBorn {3}\n{0} has been petted {4} time(s).```'.format(test[0]['name'], statText, arrow.get(test[0]['feed']).humanize(), arrow.get(test[0]['born']).humanize(), test[0]['pets'], self.emojistatus[status]))

    '''
    async def feed(self, message_object):
        print('[feed] command executed by {0}'.format(message_object.author.name))
        pet = Query()
        q = self.db.search(pet.owner == message_object.author.mention)
        if len(q) == 0:
            await self.pm.client.send_message(message_object.channel, 'Can\'t feed no pet if ya don\'t have any!')
        else:
            self.db.update({'feed':  arrow.utcnow().timestamp}, pet.owner == message_object.author.mention)
            await self.pm.client.send_message(message_object.channel, 'Neato! {0} muched on some {1}'.format(q[0]['name'], random.choice(self.food)))
    #old feed system
    '''
    async def feed(self, message_object, args):
        #print('[feed] command executed by {0}'.format(message_object.author.name))
        db = self.db
        pet = Query()
        user = Query()
        
        userdata = self.userDB.search(user.username == message_object.author.mention)
        if len(userdata) == 0:
            self.userDB.insert({'username' : message_object.author.mention,
                'lastpet' : arrow.utcnow().replace(hours=-1).timestamp,
                'lastfeed': arrow.utcnow().replace(hours=-1).timestamp,
                'previous': 0,
                'food' : 0})

        resultuser = self.userDB.search(user.username == message_object.author.mention)
        if args == "":
            resultpet = db.search(pet.owner == message_object.author.mention)
        else:
            resultpet = self.db.search(pet.qname == args.lower())

        #print(resultpet)
        if len(resultpet) == 0:
            #im suffering from split personality where the error check sometimes switches around.
            await self.pm.client.send_message(message_object.channel, ':exclamation:`You currenly have no pets or no pet with the name specified found!`')
        else:
            if len(resultuser) != 0:
                print('\t[NokuDebug]LastFeedElapsed: {0}'.format(arrow.utcnow().timestamp - arrow.get(resultuser[0]['lastfeed']).timestamp))
                if ((arrow.utcnow().timestamp - arrow.get(resultuser[0]['lastfeed']).timestamp) >= self.feedcooldown):
                    status = arrow.get((arrow.get(resultpet[0]['feed']).timestamp - arrow.utcnow().timestamp) * -1).hour
                    print("\t[NokuDebug] Feed Status: {0}".format(status))
                    if status < 15:
                        #allow petting
                        self.userDB.update({'lastfeed' : arrow.utcnow().timestamp}, user.username == message_object.author.mention)
                        self.db.update({'feed':  arrow.utcnow().timestamp}, pet.name == resultpet[0]['name'])
                        await self.pm.client.send_message(message_object.channel, 'You just fed {0} some {1}. {0} liked it a lot!'.format(resultpet[0]['name'], random.choice(self.food)))
                    else:
                        await self.pm.client.send_message(message_object.channel, ':exclamation:`Oh Heck, your pet died due to starvation!`')
                else:
                    await self.pm.client.send_message(message_object.channel, ':exclamation:`Welp, you already fed a pet! You can try again {0}.`'.format(arrow.get( ( self.feedcooldown - (arrow.utcnow().timestamp - arrow.get(resultuser[0]['lastfeed']).timestamp))+ arrow.utcnow().timestamp).humanize()))
            else:
                await self.pm.client.send_message(message_object.channel, ':exclamation:`Welp, you need or used to have a pet first!`')



    async def kill(self, message_object, arg):
        #print('[kill] command executed by {0}'.format(message_object.author.name))
        pet = Query()
        q = self.db.search(pet.owner == message_object.author.mention)
        matee = False
        if len(q) == 0:
            q = self.db.search(pet.assfucked == message_object.author.mention)
            matee = True

        print("[DPE]Debug:")
        try:
            print(q)
        except:
            print("[Noku]Cannot display data, probably emojis.")

        if len(q) == 0:
            await self.pm.client.send_message(message_object.channel, 'You don\'t have a pet!')
        else:
            if arg == q[0]['name']:
                if matee:
                    self.db.remove(pet.assfucked == message_object.author.mention)
                else:
                    self.db.remove(pet.owner == message_object.author.mention)
                await self.pm.client.send_message(message_object.channel, ':fire: Wao, you threw {0} in the incinerator. Bye {0}! :fire:'.format(q[0]['name']))
            else:
                await self.pm.client.send_message(message_object.channel, ':information_source:```For safety, you need to specify your pet\'s name (case sensitive)```')

    async def slut(self, message_object, args):
        #print('[slut] command executed by {0}'.format(message_object.author.name))
        pet = Query()
        if args == "":
            await self.pm.client.send_message(message_object.channel, 'Specify a valid username.')
        else:
            if len(message_object.mentions) != 0:
                q = self.db.search(pet.assfucked ==  message_object.mentions[0].mention)
                await self.pm.client.send_message(message_object.channel, '{0} is a mother of {1} pet(s)'.format(message_object.mentions[0].name, len(q)))


    async def pet(self, message_object, args):
        #print('[pet] command executed by {0}'.format(message_object.author.name))
        pet = Query()
        user = Query()
        userdata = self.userDB.search(user.username == message_object.author.mention)
        if len(userdata) == 0:
            self.userDB.insert({'username' : message_object.author.mention,
                'lastpet' : arrow.utcnow().replace(hours=-1).timestamp,
                'lastfeed': arrow.utcnow().replace(hours=-1).timestamp,
                'previous': 0,
                'food' : 0})

        resultpet = self.db.search(pet.qname == args.lower())
        resultuser = self.userDB.search(user.username == message_object.author.mention)
        print(resultpet)
        if len(resultpet) != 0:
            if len(resultuser) != 0:
                print('[NokuDebug]LastPetElapsed: {0}'.format(arrow.utcnow().timestamp - arrow.get(resultuser[0]['lastpet']).timestamp))
                if ((arrow.utcnow().timestamp - arrow.get(resultuser[0]['lastpet']).timestamp) >= self.petcooldown):
                    #allow petting
                    self.userDB.update({'lastpet' : arrow.utcnow().timestamp}, user.username == message_object.author.mention)
                    self.db.update({'pets' : int(resultpet[0]['pets']) + 1}, pet.qname == args.lower())
                    await self.pm.client.send_message(message_object.channel, ':wave: You just petted {0}. {0} was happy with it.'.format(args))
                else:
                    await self.pm.client.send_message(message_object.channel, ':exclamation:`Welp, you already petted a pet! You can try again {0}.`'.format(arrow.get( ( self.petcooldown - (arrow.utcnow().timestamp - arrow.get(resultuser[0]['lastpet']).timestamp))+ arrow.utcnow().timestamp).humanize()))
            else:
                await self.pm.client.send_message(message_object.channel, ':exclamation:`Welp, you need or used to have a pet first!`')
        else:
            await self.pm.client.send_message(message_object.channel, ':exclamation:`Uh-oh! No pet with that name. Maybe his owner killed him. Or he ded.`')

    async def aliveBoard(self, message_object):
        result = []
        #filter the dead pets
        for x in self.db.all():
            if arrow.get((arrow.get(x['feed']).timestamp - arrow.utcnow().timestamp) * -1).hour < 15:
                result.append(x)

        sortedLeaderBoard = sorted(result, key=itemgetter('born'))
        display = "Pet Age Leaderboard\n```No - Name  \t\t\t- Owner  \t\t\t- Born\n---\n"
        rank = 1
        for x in sortedLeaderBoard:
            display = display + "{0:02d} - {1:14.14}\t- {2:14.14}\t- {3}\n".format(rank, x['name'], x['ownerName'], arrow.get(x['born']).humanize());
            if rank >= 10:
                break
            rank = rank + 1
        display = display + "```"
        await self.pm.client.send_message(message_object.channel, display)
        pass

    async def allPets(self, message_object):
        result = []
        #filter the dead pets
        for x in self.db.all():
            if arrow.get((arrow.get(x['feed']).timestamp - arrow.utcnow().timestamp) * -1).hour < 15:
                result.append(x)

        sortedLeaderBoard = sorted(self.db.all(), key=itemgetter('born'), reverse=True)
        display = "Pet List\n```Stat - Name  \t\t\t- Owner  \t\t\t- Born\n---\n"
        #rank = 1
        for x in sortedLeaderBoard:
            if arrow.get((arrow.get(x['feed']).timestamp - arrow.utcnow().timestamp) * -1).hour < 15:
                stat = "live"
            else:
                stat = "dead"
            display = display + "{0:6.6} - {1:14.14}\t- {2:14.14}\t- {3}\n".format(stat, x['name'], x['ownerName'], arrow.get(x['born']).humanize());
            #if rank >= 10:
            #    break
            #rank = rank + 1
        display = display + "```"
        await self.pm.client.send_message(message_object.channel, display)
        pass

    async def petBoard(self, message_object):
        result = []
        #filter the dead pets
        for x in self.db.all():
            if arrow.get((arrow.get(x['feed']).timestamp - arrow.utcnow().timestamp) * -1).hour < 5:
                result.append(x)

        sortedLeaderBoard = sorted(result, key=itemgetter('pets'), reverse=True)
        display = "Most Petted Leaderboard\n```No - Name  \t\t\t- Owner  \t\t\t- No of Pets\n---\n"
        rank = 1
        for x in sortedLeaderBoard:
            display = display + "{0:02d} - {1:14.14}\t- {2:14.14}\t- {3}\n".format(rank, x['name'], x['ownerName'], x['pets']);
            if rank >= 10:
                break
            rank = rank + 1
        display = display + "```"
        await self.pm.client.send_message(message_object.channel, display)
        pass


    async def allowChan(self, message_object):
        self.configDB.insert({'chanallow' : message_object.channel.id});
        await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-pets has been allowed access to {0}`'.format(message_object.channel.name))

    async def blockChan(self, message_object):
        self.configDB.remove(Query().chanallow == message_object.channel.id);
        await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-pets has been blocked access to {0}`'.format(message_object.channel.name))
