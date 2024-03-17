import discord
import asyncio
import aiofiles
import struct
import os
from data.crypto.rstar_crypt import Crypt_Rstar as crypt
from utils.constants import OTHER_TIMEOUT, embDone_G
from .common import QuickCheatsError, QuickCheats, TimeoutHelper

class Cheats_RDR2:
    MONEY_LIMIT = 0x7FFFFFFF
    MONEY_OFFSET_IDENTIFIER_BEFORE = b"\xCE\x54\x8C\xF5"
    BYTES_BETWEEN_IDENTIFIER = 16

    class MoneyModal(discord.ui.Modal):
        def __init__(self, ctx: discord.ApplicationContext, helper: TimeoutHelper, filePath: str, platform: str) -> None:
            super().__init__(title="Alter money", timeout=None)
            self.ctx = ctx
            self.helper = helper
            self.filePath = filePath
            self.platform = platform
            self.add_item(discord.ui.InputText(
                label="Choose value",
                custom_id="ValueChooseMoney_RDR2",
                placeholder="99999",
                max_length=10,
                style=discord.InputTextStyle.short,
            ))

        async def on_error(self, err: Exception, _: discord.Interaction) -> None:
            if isinstance(err, QuickCheatsError):
                await self.ctx.respond(err, ephemeral=True)
            else:
                print(f"Error with modal: {err}")

        async def callback(self, interaction: discord.Interaction) -> None:
            await interaction.response.defer()
            await asyncio.sleep(2)
            if not self.helper.done:
                money = self.children[0].value
                if not money.isdigit():
                    self.stop()
                    raise QuickCheatsError("Invalid input!")
                else:
                    money = int(money)
                    await Cheats_RDR2.changeMoney(self.filePath, money, self.platform)
                    stats = await Cheats_RDR2.fetchStats(self.filePath, self.platform)
                    embLoaded = Cheats_RDR2.loaded_embed(stats)
                    await self.ctx.edit(embed=embLoaded)

    class CheatsButton(discord.ui.View):
        def __init__(self, ctx: discord.ApplicationContext, helper: TimeoutHelper, filePath: str, platform: str) -> None:
            super().__init__(timeout=OTHER_TIMEOUT)
            self.ctx = ctx
            self.helper = helper
            self.filePath = filePath
            self.platform = platform
            self.closed = False

        async def on_timeout(self) -> None:
            await asyncio.sleep(3)
            if not self.closed:
                self.disable_all_items()
                if self.platform == "pc":
                    await crypt.encryptFile(self.filePath, crypt.RDR2_PC_HEADER_OFFSET)
                await self.helper.handle_timeout(self.ctx)

        @discord.ui.button(label="Change money", style=discord.ButtonStyle.primary, custom_id="ChangeMoney_RDR2")
        async def changeMoney_callback(self, _, interaction: discord.Interaction) -> None:
            await interaction.response.send_modal(Cheats_RDR2.MoneyModal(self.ctx, self.helper, self.filePath, self.platform))

        @discord.ui.button(label="Save file", style=discord.ButtonStyle.green, custom_id="SaveFile_RDR2")
        async def saveFile_callback(self, _, interaction: discord.Interaction) -> None:
            await interaction.response.edit_message(embed=embDone_G, view=None)
            if self.platform == "pc":
                await crypt.encryptFile(self.filePath, crypt.RDR2_PC_HEADER_OFFSET)
            self.helper.done = True
            self.closed = True

    @staticmethod
    async def initSavefile(filePath: str) -> str | None:
        try:
            async with aiofiles.open(filePath, "rb") as file:
                await file.seek(crypt.RDR2_PC_HEADER_OFFSET)
                check_bytes = await file.read(len(crypt.RDR2_HEADER))
            
                if check_bytes == b"\x00\x00\x00\x00": # ps4 if true
                    platform = "ps4"
                    await file.seek(crypt.RDR2_PS_HEADER_OFFSET)
                    header = await file.read(len(crypt.RDR2_HEADER))
                
                else: # pc if true or invalid 
                    platform = "pc"
                    header = await file.read(len(crypt.RDR2_HEADER))
        except (ValueError, IOError):
            raise QuickCheatsError("File not supported!")
        
        if header == crypt.RDR2_HEADER:
            encrypted = False
                
        elif header != crypt.RDR2_HEADER:
            encrypted = True
        
        if encrypted:
            start_offset = crypt.RDR2_PS_HEADER_OFFSET if platform == "ps4" else crypt.RDR2_PC_HEADER_OFFSET  
            try: await crypt.decryptFile(os.path.dirname(filePath), start_offset)
            except (ValueError, IOError): raise QuickCheatsError("File not supported!")
        return platform 

    @staticmethod
    async def changeMoney(filePath: str, money: int, platform: str) -> None:
        if money > Cheats_RDR2.MONEY_LIMIT or money < 0:
            raise QuickCheatsError(f"Invalid money limit, maximum is {Cheats_RDR2.MONEY_LIMIT: ,} and it must be positive.")
        
        try:
            async with aiofiles.open(filePath, "r+b") as savegame:
                money_offset = await QuickCheats.findOffset_with_identifier32(savegame, None, Cheats_RDR2.MONEY_OFFSET_IDENTIFIER_BEFORE, None, Cheats_RDR2.BYTES_BETWEEN_IDENTIFIER)
                if money_offset == -1:
                    raise QuickCheatsError("File not supported!")

                await savegame.seek(money_offset)
                await savegame.write(struct.pack(">I", money))

            start_offset = crypt.RDR2_PS_HEADER_OFFSET if platform == "ps4" else crypt.RDR2_PC_HEADER_OFFSET
            await crypt.encryptFile(filePath, start_offset)
            await crypt.decryptFile(os.path.dirname(filePath), start_offset) # for better compatability 
        except (ValueError, IOError):
            raise QuickCheatsError("File not supported!")
    
    @staticmethod
    async def fetchStats(filePath: str, platform: str) -> dict | None:
        stats = {}
        try:
            async with aiofiles.open(filePath, "rb") as savegame:
                money_offset = await QuickCheats.findOffset_with_identifier32(savegame, None, Cheats_RDR2.MONEY_OFFSET_IDENTIFIER_BEFORE, None, Cheats_RDR2.BYTES_BETWEEN_IDENTIFIER)
                if money_offset == -1:
                    raise QuickCheatsError("File not supported!")
                
                await savegame.seek(money_offset)
                money = struct.unpack(">I", await savegame.read(4))[0]
        except (ValueError, IOError):
            raise QuickCheatsError("File not supported!")
        
        # display money like for example 555500 as 5,555.00
        moneyformatted = str(money)
        moneyWhole = f"{int(moneyformatted[:-2]): ,}"
        moneyCent = f".{moneyformatted[-2:]}"
        moneyformatted = moneyWhole + moneyCent

        stats["Money"] = moneyformatted
        stats["Platform"] = platform
        return stats
    
    @staticmethod
    def loaded_embed(stats: dict) -> discord.Embed:
        embLoaded = discord.Embed(title=f"Save loaded: RDR 2",
                    description=(
                        f"Platform: **{stats['Platform']}**\n"
                        f"Money: **{stats['Money']}**"
                    ),
                    colour=0x854bf7)
        embLoaded.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
        embLoaded.set_footer(text="Made with expertise by HTOP")
        return embLoaded
