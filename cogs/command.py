from util import *
from config import *
from funshi import *

import discord
from discord.ui import *
from discord.commands import Option
from discord.ext import commands

import io
import json 
import math
import textwrap
import datetime
import requests

from pilmoji import Pilmoji
from PIL import Image, ImageDraw, ImageFont



def is_dev():
    def check_developer(inter:discord.Interaction | discord.ApplicationContext):
        result = int(inter.author.id) in admins
        if result:
            pass
        return result
    return commands.check(check_developer)



class MyBot(commands.Cog):
    def __init__(self, bot:discord.Bot):
        self.bot = bot

    f = discord.SlashCommandGroup(name="funshi")
    l = f.create_subgroup(name="list")
    s = f.create_subgroup(name="search")
    b = f.create_subgroup(name="backup")




    @commands.message_command(name="Make it a Quote(Fake)")
    async def make_it_a_quote(self, inter:discord.Interaction, message:discord.Message):
        W, H = 1200, 630
        
        def make_it_a_quote_base(url:str, msg, mode="L"):
            icon_img = Image.open(io.BytesIO(requests.get(url).content)).convert(mode=mode)
            background_img = Image.open(f"resouse{os.sep}image{os.sep}background.png")
            mask_img = Image.open(f"resouse{os.sep}image{os.sep}base-gd-3.png")
            black = Image.open(f"resouse{os.sep}image{os.sep}background.png")
            icon = icon_img.resize((H, H))
            background_img.paste(icon)
            result = Image.composite(black, background_img, mask=mask_img)
            draw = ImageDraw.Draw(result)

            tsize_t = draw_text(result, (850, 270), msg.content, size=45, color=(255,255,255,255), split_len=14, auto_expand=True) 
            user_name:str =  f"{msg.author.display_name} ({msg.author.name})#{msg.author.discriminator}" if not msg.author.display_name==msg.author.name else f"{msg.author.name}#{msg.author.discriminator}"

            draw_text(result, (850, tsize_t[2] + 40), str(f"- {user_name}"), size=25, color=(255,255,255,255), split_len=25, disable_dot_wrap=True)
            
            frame = f"resouse{os.sep}image{os.sep}done{os.sep}result.png"
            print(os.path.exists(frame))
            result.save(frame)
            
            return  frame, (result.size)
        
        def draw_text(im, ofs, string, font=f'resouse{os.sep}fonts{os.sep}MPLUSRounded1c-Regular.ttf', size=16, color=(0,0,0,255), split_len=None, padding=4, auto_expand=False, emojis: list = [], disable_dot_wrap=False):
            draw = ImageDraw.Draw(im)
            fontObj = ImageFont.truetype(font, size=size)

            pure_lines, pos, l = [], 0, ""

            if not disable_dot_wrap:
                for char in str(string):
                    if char == '\n':
                        pure_lines.append(l)
                        l = ''
                        pos += 1
                    elif char == '、' or char == ',':
                        pure_lines.append(l + ('、' if char == '、' else ','))
                        l = ''
                        pos += 1
                    elif char == '。' or char == '.':
                        pure_lines.append(l + ('。' if char == '。' else '.'))
                        l = ''
                        pos += 1
                    else:
                        l += char
                        pos += 1
                if l:
                    pure_lines.append(l)
            else:
                pure_lines = string.split('\n')

            lines = []

            for line in pure_lines:
                lines.extend(textwrap.wrap(line, width=split_len))
            
            dy = 0
            draw_lines = []

            for line in lines:
                tsize = fontObj.getsize(line)
                ofs_y = ofs[1] + dy
                t_height = tsize[1]

                x = int(ofs[0] - (tsize[0]/2))
                draw_lines.append((x, ofs_y, line))
                ofs_y += t_height + padding
                dy += t_height + padding
            
            adj_y = -30 * (len(draw_lines)-1)
            for dl in draw_lines:
                with Pilmoji(im) as p:
                    p.text((dl[0], (adj_y + dl[1])), dl[2], font=fontObj, fill=color, emojis=emojis, emoji_position_offset=(-4, 4))

            real_y = ofs[1] + adj_y + dy
            return (0, dy, real_y)


        msg = await inter.channel.fetch_message(message.id)
        url = message.author.display_avatar.url
        
        file_name, b = make_it_a_quote_base(url=url, msg=msg, mode="L")
        b = iter(b)

        e = discord.Embed(color=0x2f3136)
        e.set_image(url=f"attachment://{file_name}")
        e.set_footer(text=f"{next(b)}x{next(b)}, {convert_size(os.stat(file_name).st_size)}")
        file = file=discord.File(file_name)
        
        await inter.response.send_message(embed=e, file=file)



    @f.command(name="source")
    async def source(self, inter:discord.Interaction):
        await inter.response.send_message("https://github.com/wuliao97/Funshi", ephemeral=True)
    


    @b.command(name="send-a-json")
    @commands.check_any(commands.has_any_role(verified_roles), is_dev())
    async def backup_send_a_json(self, inter:discord.Interaction):
        file = discord.File(BACKUP_JSON, filename=f"backup_{datetime.datetime.now().strftime(TimeFormat.DEFAULT)}.json")
        await inter.response.send_message(file=file)



    @f.command(name="format")
    @commands.check_any(is_dev())
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
    @commands.check_any(commands.has_any_role(verified_roles), is_dev())
    async def funshi_add_withUserCMD(self, inter:discord.Interaction, user:discord.Member):
        result, err = Funshi.check_in_data(user=user)

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
    @commands.check_any(commands.has_any_role(verified_roles), is_dev())
    async def funshi_add(
        self, 
        inter:discord.Interaction, 
        user:Option(discord.Member, "登録したいユーザーの選択"), 
        about:Option(
            str, "憤死内容", max_length=1_000
        )
    ):
        result, err = Funshi.check_in_data(user=user)

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
    @commands.check_any(commands.has_any_role(verified_roles), is_dev())
    async def funshi_remove(self, inter:discord.Interaction):
        data = Funshi.select_data()
        e = discord.Embed(description="Total: " + str(len(data)))
        view = FunshiView(data, mode="remove") if len(data) > 0 else discord.ui.View()

        await inter.response.send_message(
            embeds = [e], 
            view   = view
        )
    
    
    @l.command(name="edit")
    @commands.check_any(commands.has_any_role(verified_roles), is_dev())
    async def funshi_remove(self, inter:discord.Interaction):
        data = Funshi.select_data()
        e = discord.Embed(description="Total: " + str(len(data)))
        view = FunshiView(data, mode="edit") if len(data) > 0 else discord.ui.View()

        await inter.response.send_message(
            embeds = [e], 
            view   = view
        )


    @s.command(name="select")
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


    @s.command(name="by-id")
    async def funshi_search_cmd(
        self, 
        inter:discord.Interaction,
        user:Option(str, "ONLY user `ID`. Like: 1039780426564239431"),
        me_only:Option(
            bool, "Display to just me?", choices=[True, False], default=False
        )
    ):
        result, err = Funshi.check_in_data(user=user, exist_OK=True)

        if result:
            data = Funshi.loading()[user]
            e = Funshi.details_base(data=data, user=inter.user)

            await inter.response.send_message(
                embeds    = [e], 
                ephemeral = me_only
            )            
            
        else:
            e = discord.Embed(description=err)
            await inter.response.send_message(embeds=[e], ephemeral=True)



    @s.command(name="simple")
    async def funshi_search_cmd(
        self, 
        inter:discord.Interaction,
        user:Option(discord.Member, ""),
        me_only:Option(
            bool, "Display to just me?", choices=[True, False], default=False
        )
    ):
        result, err = Funshi.check_in_data(user=user, exist_OK=True)

        if result:
            data = Funshi.loading()[str(user.id)]
            e = Funshi.details_base(data=data, user=inter.user)

            await inter.response.send_message(
                embeds    = [e], 
                ephemeral = me_only
            )            
            
        else:
            e = discord.Embed(description=err)
            await inter.response.send_message(embeds=[e], ephemeral=True)




def setup(bot:discord.Bot):
    return bot.add_cog(MyBot(bot))