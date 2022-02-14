import discord, json, re
from discord.ext import commands

TOKEN = ""

intents = discord.Intents.all()

client = commands.Bot(command_prefix = "+")

# Load the banned links
# A link is represented by a dictionary with the following keys:
#   - "link": the url
#   - "reason": the reason for the ban
#   - "banned_by": the user who banned the link
try :
    BANNED_LINKS: list = json.load(open("bannedLink.json",'r',encoding='utf-8'))
except Exception as e:
    print(e)
    BANNED_LINKS: list = []


# Load the banned websites
# A website is represented by a dictionary with the following keys:
#   - "url": the url "https://www.google.com" (then all the links on this website will be banned)
#   - "reason": the reason for the ban
#   - "banned_by": the user who banned the website
try :
    BANNED_WEBSITES: list = json.load(open("bannedWebsite.json",'r',encoding='utf-8'))
except Exception as e:
    print(e)
    BANNED_WEBSITES: list = []


def have_a_link(messge: str) -> bool :
    """
     Return True if the message contains a url
    """
    return re.search(r'(https?://\S+)', messge) is not None


def is_url_same_website(website: str, url_to_compare: str) -> bool:
    """
    Return True if the url_to_compare come from the same website
    """
    return re.search(website, url_to_compare) is not None


def add_link_embed(message: str, reason: str, author: str) -> discord.Embed :
    embed = discord.Embed(title="New link/website banned", description=f"{message}", color=0xeb4034)
    embed.add_field(name="Reason", value=f"{reason}", inline=False)
    embed.add_field(name="Banned by", value=f"{author}", inline=False)
    return embed

def add_link_embed_unban(message,reason,author) -> discord.Embed:
    embed = discord.Embed(title="Link/website unbanned", description=f"{message}", color=0x099e27)
    embed.add_field(name="Reason", value=f"{reason}", inline=False)
    embed.add_field(name="Unbanned by", value=f"{author}", inline=False)
    return embed

@client.event
async def on_ready():
    print("Connected as : ")
    print(f"{client.user.name}#{client.user.discriminator}")
    print(client.user.id)
    print("-----------------")


@client.event
async def on_command_error(ctx: discord.Context, error : Exception):
    if isinstance(error, commands.CommandInvokeError): await ctx.send(":x: 403 Forbidden ! Missing Permissions")
    if isinstance(error, commands.CommandNotFound): await ctx.send(":x: Command not found")
    else: raise error

@client.command(aliases=["banL"])
async def add_banned_link(ctx: discord.Context, link :str, *reason: tuple):

    # Check if the user of the command have admin permissions
    if ctx.message.author.guild_permissions.administrator:

        # Check if the link is already banned
        for link_ in BANNED_LINKS:
            if link_['link'] == link:
                return await ctx.send(":x: Link already banned")

        reason_, author_ = " ".join(reason), ctx.author.name

        # Add the link to the list
        BANNED_LINKS.append({'link':link,'reason':reason_,'author':author_})

        # Write the list to the json file
        with open('bannedLink.json','w',encoding='utf-8') as j:
            json.dump(BANNED_LINKS,j,indent=4)

        # Send the embed to the channel
        await ctx.send(embed=add_link_embed(link,reason_,author_))

    else :
        await ctx.send(":x: 403 Forbidden ! Missing Permissions")


@client.command(aliases=["unbanL"])
async def remove_banned_link(ctx: discord.Context, link: str):
    
    # Check if the user of the command have admin permissions
    if ctx.message.author.guild_permissions.administrator:

        # Check if the link is already banned
        for link_ in BANNED_LINKS:
            if link_['link'] == link:
                BANNED_LINKS.remove(link_)
                with open('bannedLink.json','w',encoding='utf-8') as j:
                    json.dump(BANNED_LINKS,j,indent=4)
                await ctx.send(embed=add_link_embed_unban(link,link_['reason'],link_['author']))
                return

        await ctx.send(":x: Link not found")

    else :
        await ctx.send(":x: 403 Forbidden ! Missing Permissions")

@client.command(aliases=["banW"])
async def add_banned_website(ctx: discord.Context, url: str, *reason: tuple):
    
    # Check if the user of the command have admin permissions
    if ctx.message.author.guild_permissions.administrator:

        # Check if the link is already banned
        for website_ in BANNED_WEBSITES:
            if website_['url'] == url:
                return await ctx.send(":x: Website already banned")

        reason_, author_ = " ".join(reason), ctx.author.name

        # Add the link to the list
        BANNED_WEBSITES.append({'url':url,'reason':reason_,'author':author_})

        # Write the list to the json file
        with open('bannedWebsite.json','w',encoding='utf-8') as j:
            json.dump(BANNED_WEBSITES,j,indent=4)

        # Send the embed to the channel
        await ctx.send(embed=add_link_embed(url,reason_,author_))

    else :
        await ctx.send(":x: 403 Forbidden ! Missing Permissions")

@client.command(aliases=["unbanW"])
async def remove_banned_website(ctx: discord.Context, url: str):
        
    # Check if the user of the command have admin permissions
    if ctx.message.author.guild_permissions.administrator:

        # Check if the link is already banned
        for website_ in BANNED_WEBSITES:
            if website_['url'] == url:
                BANNED_WEBSITES.remove(website_)
                with open('bannedWebsite.json','w',encoding='utf-8') as j:
                    json.dump(BANNED_WEBSITES,j,indent=4)
                await ctx.send(embed=add_link_embed_unban(url,website_['reason'],website_['author']))
                return

        await ctx.send(":x: Website not found")

    else :
        await ctx.send(":x: 403 Forbidden ! Missing Permissions")



@client.command(aliases=["helps"])
async def help_command(ctx):
    embed=discord.Embed(title="How Cops Miku works !",color=0x0c5ddf)
    embed.set_thumbnail(url="https://i.redd.it/rdbcv3orpjy71.jpg")
    embed.add_field(name="+banL",value="<link> <reason>",inline=False)
    embed.add_field(name="+unbandL",value="<link>",inline=False)
    embed.add_field(name="+banW",value="<url_website> <reason>",inline=False)
    embed.add_field(name="+unbandW",value="<url_website>",inline=False)
    embed.set_footer(text="Made by Yù, my GitHub : https://github.com/Wongt8")
    await ctx.send(embed=embed)

@client.event
async def on_message(message: discord.Message):

    # This make the command work
    await client.process_commands(message)

    # Get the context of the message
    ctx = await client.get_context(message)

    # Check if the message is a command 
    if ctx.valid:
        return

    # Check if the message contains a url that is in the bannded list
    for link in BANNED_LINKS:
        if link['link'] in message.content:
            await message.delete()
            await message.channel.send(f":x: This link is not allowed for the reason **{link['reason']}**")
            break

    # Check if the message contains a url of a banned website
    for website in BANNED_WEBSITES:
        if is_url_same_website(website['url'],message.content):
            await message.delete()
            await message.channel.send(f":x: This website is not allowed for the reason **{website['reason']}**")
            break
    
    # Check if the message is @everyone and the author don't have admin permission
    if message.mention_everyone and not message.author.guild_permissions.administrator:

        # Check if the message contains a url
        if have_a_link(message.content):
            await message.delete() 
            await message.channel.send(f":x: Do not send a link and `@everyone` at the same time")

client.run(TOKEN)