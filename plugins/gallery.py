from util import Events
from util.Ranks import Ranks
from tinydb import TinyDB, where, Query
from imgurpython import ImgurClient
import arrow
import random

class Plugin(object):
    '''
    Noku Image Module
    '''
    def __init__(self, pm):
        self.pm = pm
        self.modulename = 'gallery'
        self.configPath = 'pluginsconfig/data_config-{0}_a.json'.format(self.modulename)
        self.configDB = TinyDB(self.configPath) 
        self.client = ImgurClient("43bdb8ab21d18b9", "fcba34a83a4650474ac57f6e3f8b0750dd26ecf5")
        self.imagecache = {}
        self.schcache = {}
        self.buildImagePre()



    @staticmethod
    def register_events():
        return [
        Events.Command("gallery.build", Ranks.Default, 
            "Builds the gallery cache, must be run after booting the bot."),
        Events.Command("gallery.add", Ranks.Default, 
            "[tag] [subreddit] - scans the subreddit for images and posts a random image."),
        Events.Command("gallery.delete", Ranks.Default,
            "[tag] Deletes an image tag."),
        Events.Command("subimg", Ranks.Default,
            "[tag] - Posts a random image from a subreddit."),
        Events.Command("imgs", Ranks.Default,
            "[query] - Searches imgur for images."),
        Events.Command("gallery.allow", Ranks.Admin),
        Events.Command("gallery.block", Ranks.Admin)]

    async def handle_command(self, message_object, command, args):
        try:
            print("--{2}--\n[Noku-{4}] {0} command from {1} by {3}".format(command, message_object.channel.name, arrow.now().format('MM-DD HH:mm:ss'), message_object.author.name, self.modulename))
        except:
            print("[Noku]Cannot display data, probably emojis.")   

        if self.configDB.contains(Query().chanallow == message_object.channel.id) or message_object.channel.is_private:
            '''
            Add modules checks here
            '''
            if command == "gallery.build":
                await self.buildImage(message_object)
            if command == "gallery.add":
                await self.addImage(message_object, args[1])
            if command == "gallery.delete":
                await self.delImage(message_object, args[1])      
            if command == "imgs":
                await self.imgs(message_object, args[1])           
            if command == "subimg":
                if args[1] != "":
                    await self.showImage(message_object, args[1])
                else:
                    await self.showGallery(message_object)


        #Do not modify or add anything below it's for permissions
        if command == "{0}.allow".format(self.modulename):
            await self.allowChan(message_object)
        if command == "{0}.block".format(self.modulename):
            await self.blockChan(message_object)


    '''
    Add modules here
    '''
    async def imgs(self, message_object, args):
        await self.pm.client.send_typing(message_object.channel)
        new = True
        while new:
            if args.lower() in self.schcache:
                if len(self.schcache[args]) > 0:
                    image = random.choice(self.schcache[args])
                    if "imgur.com/a/" in image.link:
                        image = random.choice(self.client.get_album_images(image.id)).link
                    else:
                        image = image.link
                else:
                    image = ":information_source:`No results for your query!`"
                print("[Gallery]Sending: {0}".format(image))
                new = False
                await self.pm.client.send_message(message_object.channel, image)
            else:
                self.schcache[args.lower()] = self.client.gallery_search(args)



    async def buildImage(self, message_object=None):
        status = await self.pm.client.send_message(message_object.channel, ':information_source:`Building Cache for Noku-Image`'.format())
        await self.pm.client.send_typing(message_object.channel)
        dbCache = self.configDB.search(Query().tag != "")
        print("[Noku]Building cache")
        if dbCache != 0:
            for item in dbCache:
                print("[Noku]Retrieving Image Cache for {0}".format(item['tag']))
                #self.imagecache[item['tag']] = self.client.subreddit_gallery(item['link'])
                #await self.pm.client.edit_message(status, ':information_source:`Noku-Image: Building {0} cache.`'.format(item['tag']))
                await self.addCache(item['tag'], item['link'])
        #await self.pm.client.send_message(message_object.channel, ':information_source:`Cache Build complete!`'.format())
    
    def buildImagePre(self, message_object=None):
        #status = await self.pm.client.send_message(message_object.channel, ':information_source:`Building Cache for Noku-Image`'.format())
        #await self.pm.client.send_typing(message_object.channel)
        dbCache = self.configDB.search(Query().tag != "")
        print("[Noku]Building cache")
        if dbCache != 0:
            for item in dbCache:
                print("[Noku]Retrieving Image Cache for {0}".format(item['tag']))
                #self.imagecache[item['tag']] = self.client.subreddit_gallery(item['link'])
                #await self.pm.client.edit_message(status, ':information_source:`Noku-Image: Building {0} cache.`'.format(item['tag']))
                self.imagecache[item['tag']] = self.client.subreddit_gallery(item['link'])
    
    async def addCache(self, tag, link):
        self.imagecache[tag] = self.client.subreddit_gallery(link)

    async def addImage(self, message_object, args):
        status = await self.pm.client.send_message(message_object.channel, ':information_source:`Retreiving gallery info for Noku-Image`'.format())
        if len(args.split(" ")) > 0:
            tag = args.split(" ")[0]
            subreddit = args.split(" ")[1]
            await self.pm.client.edit_message(status, ':information_source:`Noku-Image: Building {0} cache.`'.format(tag))
            await self.pm.client.send_typing(message_object.channel)
            self.imagecache[tag] = self.client.subreddit_gallery(subreddit)
            if len(self.imagecache[tag]) > 10:
                self.configDB.insert({'tag' : tag,
                    'link' : subreddit})
                await self.pm.client.send_message(message_object.channel, ':information_source:`Successfully generated and added tag!`'.format())
            else:
                await self.pm.client.send_message(message_object.channel, ':exclamation:`Gallery provided is less than 10 images!`'.format())
        else:
            await self.pm.client.send_message(message_object.channel, ':information_source: Usage:`~addgalery [tag] [subreddit]`'.format())

    async def delImage(self, message_object, args):
        self.configDB.remove(Query().tag == args)
        await self.pm.client.send_message(message_object.channel, ":information_source:`{0} has been deleted! Probably..`".format(args))

    async def showImage(self, message_object, args):
        try:
            image = random.choice(self.imagecache[args])
            if "imgur.com/a/" in image.link:
                image = random.choice(self.client.get_album_images(image.id)).link
            else:
                image = image.link

            await self.pm.client.send_message(message_object.channel, "{0}".format(image))
        except:
            await self.pm.client.send_message(message_object.channel, ":exclamation:`Welp, that\'s not a valid tag!`")

    async def showGallery(self, message_object):
        macros = self.configDB.search(Query().tag != "")
        x = "```"
        for m in macros:
            x = x + m['tag'] + " "
        x = x + "```"
        await self.pm.client.send_message(message_object.channel, x)

    #Do not modify or add anything below it's for permissions
    async def allowChan(self, message_object):
        self.configDB.insert({'chanallow' : message_object.channel.id});
        await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-{1} has been allowed access to {0}`'.format(message_object.channel.name, self.modulename))

    async def blockChan(self, message_object):
        self.configDB.remove(Query().chanallow == message_object.channel.id);
        await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-{1} has been blocked access to {0}`'.format(message_object.channel.name, self.modulename))
