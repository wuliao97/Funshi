from util import *
from config import *
from funshi import *

import discord
from discord.ui import *
from discord.commands import Option
from discord.ext import commands

import os, json, datetime



class MyBot(commands.Cog):
    def __init__(self, bot:discord.Bot):
        self.bot = bot

    f = discord.SlashCommandGroup(name="funshi")
    l = f.create_subgroup(name="list")
    s = f.create_subgroup(name="search")
    b = f.create_subgroup(name="backup")



    @f.command(name="source")
    async def source(self, inter:discord.Interaction):
        await inter.respond("https://github.com/wuliao97/Funshi")
    


    @b.command(name="send-a-json")
    async def backup_send_a_json(self, inter:discord.Interaction):
        file = discord.File(BACKUP_JSON, filename=f"backup_{datetime.datetime.now().strftime(TimeFormat.DEFAULT)}.json")
        await inter.response.send_message(file=file)



    @f.command(name="format")
    #@commands.check_any()
    async def funshi_format(
        self, inter:discord.Interaction, 
    ):
        if Funshi.backup():
            material = {}

            with open(FUNSHI_JSON, "w", encoding="utf-8") as f:
                json.dump(material, fp=f, indent=4, ensure_ascii=False)
        
        tit = "憤死者名簿"
        desc = "```" + Funshi.show() + "```"
        e = Funshi._embed(title=tit, description=desc, color=True)
        await inter.response.send_message(embeds=[e], ephemeral=True)


    @l.command(name="show")
    async def funshi_show(self, 
        inter:discord.Interaction, 
        format:Option(
            str, description="display format", choices=["json", "assi"], default="assi", 
        )
    ):
        tit = "憤死者名簿"
        desc = "```" + Funshi.show(format) + "```"
        e = Funshi._embed(title=tit, description=desc, color=True)
        
        await inter.response.send_message(embeds=[e])


    @commands.user_command(name="funshi list add")
    async def funshi_add_withUserCMD(self, inter:discord.Interaction, user:discord.Member):
        result, err = Funshi.check_in_data(user=user, exist_OK=True)

        if result:
            data = Funshi.loading()
            data[user.id] = Funshi.base_generate(user=user, about="(This guy were added with User command)")
            
            with open(FUNSHI_JSON, "r+", encoding="utf-8") as f:
                f.seek(0)
                f.write(json.dumps(data, ensure_ascii=False, indent=2))
                f.truncate()
            
            e = Funshi.details_base(data=data[user.id])
            e.title="Successfully Registered!"
            await inter.response.send_message(embeds=[e])
        else:
            e = discord.Embed(description=err)
            await inter.response.send_message(embeds=[e], ephemeral=True)


    @l.command(name="add")
    async def funshi_add(
        self, 
        inter:discord.Interaction, 
        user:Option(discord.Member, "登録したいユーザーの選択"), 
        about:Option(
            str, "憤死内容", max_length=1_000
        )
    ):
        result, err = Funshi.check_in_data(user=user, exist_OK=True)

        if result:
            data = Funshi.loading()
            data[user.id] = Funshi.base_generate(user=user, about=about)
            
            with open(FUNSHI_JSON, "r+", encoding="utf-8") as f:
                f.seek(0)
                f.write(json.dumps(data, ensure_ascii=False, indent=2))
                f.truncate()
            
            e = Funshi.details_base(data=data[user.id])
            e.title="Successfully Registered!"
            await inter.response.send_message(embeds=[e])
        
        else:
            e = discord.Embed(description=err)
            await inter.response.send_message(embeds=[e], ephemeral=True)



    @l.command(name="remove")
    async def funshi_remove(self, inter:discord.Interaction):
        data = Funshi.select_data()
        e = discord.Embed(description="Total: " + str(len(data)))
        view = FunshiView(data, mode="remove") if len(data) > 0 else discord.ui.View()

        await inter.response.send_message(
            embeds = [e], 
            view   = view
        )
    
    
    @l.command(name="edit")
    async def funshi_remove(self, inter:discord.Interaction):
        data = Funshi.select_data()
        e = discord.Embed(description="Total: " + str(len(data)))
        view = FunshiView(data, mode="edit") if len(data) > 0 else discord.ui.View()

        await inter.response.send_message(
            embeds = [e], 
            view   = view
        )




    @s.command(name="person")
    async def funshi_search_cmd(
        self, 
        inter:discord.Interaction,
        me_only:Option(
            bool, "Display to just me?", choices=[True, False], default=False
        )
    ):
        data = Funshi.select_data()
        e = discord.Embed(description="Total: " + str(len(data)))
        view = FunshiView(options=data, ephemeral=me_only) if len(data) > 0 else discord.ui.View()

        await inter.response.send_message(
            embeds    = [e], 
            view      = view, 
            ephemeral = me_only
        )





def setup(bot:discord.Bot):
    return bot.add_cog(MyBot(bot))