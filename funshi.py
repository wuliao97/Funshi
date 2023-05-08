from util import *
from config import *

import discord
from discord.ui import *

import json
import datetime

class Funshi:
    """
    Base Class
    
    
    """
    def _embed(title=None, description=None, color=False):
        e = discord.Embed()

        if title:
            e.title=title

        if description:
            e.description=description
        
        if color:
            e.color = discord.Color.red()

        return e




    def base_generate(user:discord.Member, about:str=None):
        return {
            "name" : user.name,
            "discriminator": user.discriminator,
            "id"   : user.id,
            "about": about,
            "date" : datetime.datetime.now().strftime(TimeFormat.DEFAULT)
        }


    def details_base(data:dict, user:discord.Member=None) -> discord.Embed:
        e = discord.Embed(color=discord.Color.red())
        
        e.set_footer(text=f"Added Date: {data['date']}")
        e.add_field(
            name="Name", value=f"```{data['name']}#{data['discriminator']}```"
        )
        
        e.add_field(
            name="ID", value=f"```{data['id']}```", inline=False
        )
        
        e.add_field(
            name="About", value=f"```{data['about']}```", inline=False
        )
        
        if user:
            e.set_author(icon_url=user.display_avatar, name=user)
        
        return e



    def backup():
        try:
            with open(FUNSHI_JSON, encoding="utf-8") as material:
                m = json.dumps(json.load(material), indent=4, ensure_ascii=False)

            with open(BACKUP_JSON, "w", encoding="utf-8") as backup:
                backup.write(m)

            return True
        
        except Exception as e:
            print(e)
            return False



    def show(mode="json"):
        with open(FUNSHI_JSON) as f:
            e = "json\n"

            if mode == "json":
                e = json.dumps(json.load(f), indent=2, ensure_ascii=False)
            
            elif mode == "assi":
                e = "ansi\n"
                object:dict = Funshi.loading(default=True)

                for idx, obj in enumerate(object.values()):
                    e  += f"\u001b[1;0m[\u001b[1;31m{idx + 1}\u001b[0m] \u001b[31m{obj['name']}\u001b[0m\u001b[31m#\u001b[31m{obj['discriminator']} \u001b[0m-\u001b[31m {obj['id']}\u001b[0m\n"
                
                if e == "ansi\n" :
                    e = "There is no Member." 
            
            return e
    

    def loading(mode="r", default=True):
        with open(file=FUNSHI_JSON, mode=mode, encoding="utf-8") as f:    
            if default:
                m = json.load(f)
            else:
                m = json.dumps(json.load(f), indent=2, ensure_ascii=False)
        return m


    def check_in_data(user:discord.Member | int , exist_OK=False):
        result = True
        text   = ""
        material = Funshi.loading()
        user_ID = user.id if isinstance(user, discord.Member) else user
        
        if exist_OK is False:
            if str(user_ID) in material:
                result = False
                text   = "This user is ALready Registed! Please use `/funshi edit` command If you want to edit"

            elif user.bot:
                result = False
                text   = "This user is Bot! Don't allowed Add Bot"

            return result, text

        else:
            if str(user_ID) not in material:
                result = False
                text   = "No existing in member list" 

            return result, text
    

    def select_data() -> list[discord.SelectOption]:    
        data:list[discord.SelectOption] = []
        funshi_data:dict = Funshi.loading()

        for idx, user in enumerate(funshi_data.values()):
            label = f"{idx + 1}: {user['name']}#{user['discriminator']}"
            data.append(discord.SelectOption(
                label       = label,
                value       = f"{user['id']}",
                description = f"{user['id']}"
            ))
        return data



class FunshiView(discord.ui.View):
    def __init__(self, options, placeholder="Choose a User", ephemeral = False, mode="select"):
        super().__init__(timeout=120, disable_on_timeout=True)
        if mode == "select":
            self.add_item(FunshiSearchSelect(placeholder=placeholder, options=options, ephemeral=ephemeral))

        elif mode == "remove":
            self.add_item(FunshiRemoveSelect(placeholder=placeholder, options=options, ephemeral=ephemeral))
            
        elif mode == "edit":
            self.add_item(FunshiEditSelect(placeholder=placeholder, options=options, ephemeral=ephemeral))



class FunshiSearchSelect(discord.ui.Select):
    def __init__(self, placeholder:str, options: list[discord.SelectOption], ephemeral=False):
        super().__init__(placeholder=placeholder, options=options)
        self.ephemeral = ephemeral
        
    async def callback(self, inter:discord.Interaction):
        self
        data = Funshi.loading()
        e = Funshi.details_base(data[self.values[0]], inter.user)
        await inter.response.send_message(embeds=[e], ephemeral=self.ephemeral)



class FunshiRemoveSelect(discord.ui.Select):
    def __init__(self, placeholder:str, options: list[discord.SelectOption], ephemeral=False):
        super().__init__(placeholder=placeholder, options=options)
        self.ephemeral = ephemeral
        
    async def callback(self, inter: discord.Interaction):
        data = Funshi.loading()
        material = data[self.values[0]]
        del data[self.values[0]]
        with open(FUNSHI_JSON, "r+") as f:
            f.seek(0)
            f.write(json.dumps(data, ensure_ascii=False, indent=4))
            f.truncate()
        e = Funshi.details_base(material, inter.user)
        e.title="Successfully Removed!"
        await inter.response.send_message(embed=e)



class FunshiEditSelect(discord.ui.Select):
    def __init__(self, placeholder:str, options: list[discord.SelectOption], ephemeral=False):
        super().__init__(placeholder=placeholder, options=options)
        self.ephemeral = ephemeral
    
    async def callback(self, inter: discord.Interaction):
        
        data = Funshi.loading()
        e = Funshi.details_base(data[self.values[0]], inter.user)
        
        async def button_callback(inter:discord.Interaction):
            await inter.response.send_modal(FunshiEditModal(title="Edit a User About", about=data[self.values[0]]["about"], user_id=self.values[0]))
        
        b = discord.ui.Button(label="EDIT", style=discord.ButtonStyle.green)
        b.callback = button_callback
        view = discord.ui.View()
        view.add_item(b)
        
        await inter.response.send_message(embeds=[e], view=view)

class FunshiEditModal(discord.ui.Modal):
    def __init__(self, title: str, about, user_id, timeout: float = None):
        super().__init__(title=title, timeout=timeout)
        self.user_id = user_id

        self.add_item(discord.ui.InputText(
                style       = discord.InputTextStyle.long,
                max_length  = 1_000,
                label       = "About `User About`",
                value       = about
            )
        )
    
    async def callback(self, inter:discord.Interaction):
        material = self.children[0].value
        
        base = Funshi.loading()        
        base[self.user_id]["about"] = material

        with open(FUNSHI_JSON, "r+", encoding="utf-8") as f:
            f.seek(0)
            f.write(json.dumps(base, ensure_ascii=False, indent=2))
            f.truncate()
        
        e = discord.Embed(title="Sucessfully edited!")
        e.set_footer(text=f"Date: {datetime.datetime.now().strftime(TimeFormat.THREE)}")
        e.description = f"```{material}```"
        
        await inter.response.send_message(embeds=[e])