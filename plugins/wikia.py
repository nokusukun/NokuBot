from util import Events
from util.Ranks import Ranks
from tinydb import TinyDB, where, Query
import discord
import arrow
import wikia
import re

class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.modulename = 'wikia'
        self.configPath = 'pluginsconfig/data_config-{0}_a.json'.format(self.modulename)
        self.configDB = TinyDB(self.configPath) 

    @staticmethod
    def register_events():
        return [
        Events.Command("wikia", Ranks.Default,
            "[wiki]/[page]/[subsec?] Displays a wikia page. Provide a subcategory for more information."),
        Events.Command("findwiki", Ranks.Default,
            "[wiki]/[searchterm] search for a wikia page"),
        Events.Command("wikia.allow", Ranks.Admin),
        Events.Command("wikia.block", Ranks.Admin)]

    async def handle_command(self, message_object, command, args):
        try:
            print("--{2}--\n[Noku-macro] {0} command from {1} by {3}".format(command, message_object.channel.name, arrow.now().format('MM-DD HH:mm:ss'), message_object.author.name))
        except:
            print("[Noku]Cannot display data, probably emojis.")   

        if self.configDB.contains(Query().chanallow == message_object.channel.id):
            '''
            Add modules checks here
            '''
            if command == "wikia":
                await self.displaypage(message_object, args[1])

        #Do not modify or add anything below it's for permissions
        if command == "{0}.allow".format(self.modulename):
            await self.allowChan(message_object)
        if command == "{0}.block".format(self.modulename):
            await self.blockChan(message_object)


    '''
    Add modules here
    '''
    async def displaypage(self, message_object, args):
        elements = args.split("/")
        if len(elements) > 1:
            try:
                print ("[a]")
                status = await self.pm.client.send_message(message_object.channel, ':information_source:`Looking up wikia page~`'.format())
                print ("[b]")
                await self.pm.client.send_typing(message_object.channel)
                print ("[c]")
                page = wikia.page(elements[0], elements[1])
                url = page.url
                print ("[d]")
                if len(elements) == 2:
                    print ("[e]")
                    header = '{0} > {1}'.format(elements[0], elements[1])
                    content = page.summary
                    print ("[e.5]")
                else:
                    print ("[f]")
                    header = '{0} > {1} > {2}'.format(elements[0], elements[1], elements[2])
                    content =  page.section(elements[2])
                    print ("[f.5]")
            except:
                try:
                    print ("[search]")
                    search = wikia.search(elements[0], elements[1])
                    print ("[search.1]")
                    results = ""
                    i = 1
                    print ("[search.2]")
                    for x in search:
                        results = results + "{0}: {1}\n".format(i, x)
                        i += 1
                    print ("[search.3]")
                    await self.pm.client.edit_message(status, ":information_source:**No page found, here's the search results instead**\n```{0}```\n*Select the page you want to view by responding with a number*".format(results))
                    print ("[search.4]")
                    response = await self.pm.client.wait_for_message(author=message_object.author)
                    print ("[search.7]")
                    try:
                        page = wikia.page(elements[0], search[int(response.content) - 1])
                        print ("[search.8]")
                        header = '{0} > {1}'.format(elements[0], search[int(response.content) - 1])
                        print ("[search.9]")
                        content = page.summary
                        print ("[search.10]")
                        url = page.url
                        print ("[search.11]")
                    except:
                        await self.pm.client.edit_message(status, ":exclamation:`Invalid Selection!`".format())
                        return
                except:
                    await self.pm.client.edit_message(status, ":exclamation:`Invalid Wikia or no results found!`".format())
                    return

            
            print ("[display.1]")
            tags = ""
            for x in page.sections:
                tags = tags + x + ', '
            print ("[display.1.5]")
            if len(content) > 1000:
                content = content[:1000]+"..."
            print ("[display.2]")
            em = discord.Embed(title='', description="**Summary**\n{0}\n\n**Sub Sections**\n{1}\n\n**Link**\n{2}".format(content, tags, url), colour=0x007AFF, url=url)
            em.set_author(name=header)
            em.set_footer(text="Noku-wikia version 1.0.5", icon_url=self.pm.client.user.avatar_url)
            print ("[display.3]")
            if len(page.images) > 0:
                em.set_thumbnail(url=page.images[0])

            #print(content)
            print ("[display.4]")
            try:
                await self.pm.client.send_message(message_object.channel, embed=em)
            except:
                await self.pm.client.send_message(message_object.channel, "***{3}***\n\n**Summary**\n{0}\n\n**Sub Sections**\n{1}\n\n**Link**\n{2}".format(content, tags, url, header))
            try:
                await self.pm.client.delete_message(status)
                await self.pm.client.delete_message(response)
            except:
                pass
            #except:
                #await self.pm.client.send_message(message_object.channel,":exclamation:`Something went terribly wrong.`")
            #    print ("Sum error happened.")
            #    pass


    #Do not modify or add anything below it's for permissions
    async def allowChan(self, message_object):
        self.configDB.insert({'chanallow' : message_object.channel.id});
        await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-{1} has been allowed access to {0}`'.format(message_object.channel.name, self.modulename))

    async def blockChan(self, message_object):
        self.configDB.remove(Query().chanallow == message_object.channel.id);
        await self.pm.client.send_message(message_object.channel, ':information_source:`Noku Bot-{1} has been blocked access to {0}`'.format(message_object.channel.name, self.modulename))
