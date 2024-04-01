import discord
import os, shutil
import aiohttp
import re
import json
import asyncio
from discord.ext import commands
from discord import Option
from discord.ui.item import Item
from dotenv import load_dotenv
from network import FTPps, FTPError, SocketPS, SocketError
from google_drive import GDapi, GDapiError
from aiogoogle import HTTPError
from utils.constants import (
    logger, bot, change_group, quick_group, IP, PORT, PORTSOCKET, MOUNT_LOCATION, PS_UPLOADDIR, RANDOMSTRING_LENGTH, 
    FILE_LIMIT_DISCORD, SCE_SYS_CONTENTS, GTAV_TITLEID, BL3_TITLEID, RDR2_TITLEID, XENO2_TITLEID, WONDERLANDS_TITLEID, NDOG_TITLEID, NDOG_COL_TITLEID, NDOG_TLOU2_TITLEID, MGSV_TPP_TITLEID, MGSV_GZ_TITLEID, REV2_TITLEID, DL1_TITLEID, DL2_TITLEID, RGG_TITLEID, DI1_TITLEID, DI2_TITLEID,
    NPSSO, MAX_FILES, UPLOAD_TIMEOUT, PS_ID_DESC, BASE_ERROR_MSG, BOT_DISCORD_UPLOAD_LIMIT, OTHER_TIMEOUT, emb12, emb14, emb17, emb20, emb21, emb22, embgdt, embEncrypted1, embDecrypt1,
    emb6, embhttp, embpng, embpng1, embpng2, emb8, embvalidpsn, embnv1, embnt, embUtimeout, embinit, embTitleChange, embTitleErr, embTimedOut, emb_upl_savegame)
from utils.workspace import startup, initWorkspace, makeWorkspace, cleanup, cleanupSimple, enumerateFiles, listStoredSaves, WorkspaceError, write_threadid_db, fetch_accountid_db, write_accountid_db
from utils.orbis import obtainCUSA, checkid, checkSaves, handle_accid, OrbisError, handleTitles
from utils.extras import generate_random_string, zipfiles, pngprocess, obtain_savenames
from utils.exceptions import FileError, PSNIDError
from data.cheats import Cheats_GTAV, Cheats_RDR2, QuickCheatsError, TimeoutHelper, QuickCodes, QuickCodesError
from data.converter import Converter_Rstar, Converter_BL3, ConverterError
from data.crypto import Crypt_BL3, Crypt_Rstar, Crypt_Xeno2, Crypt_Ndog, Crypt_MGSV, Crypt_Rev2, Crypt_DL, Crypt_RGG, Crypt_DI2, CryptoError
from types import SimpleNamespace

Cheats = SimpleNamespace(GTAV=Cheats_GTAV, RDR2=Cheats_RDR2)
Converter = SimpleNamespace(Rstar=Converter_Rstar, BL3=Converter_BL3)
Crypto = SimpleNamespace(BL3=Crypt_BL3, Rstar=Crypt_Rstar, Xeno2=Crypt_Xeno2, 
                         Ndog=Crypt_Ndog, MGSV=Crypt_MGSV, Rev=Crypt_Rev2,
                         DL=Crypt_DL, RGG=Crypt_RGG, DI2=Crypt_DI2)

if NPSSO is not None:
    from psnawp_api import PSNAWP
    from psnawp_api.core.psnawp_exceptions import PSNAWPNotFound
    NPPSO = str(os.getenv("NPSSO"))
    psnawp = PSNAWP(NPPSO)
    print("psnawp initialized")

load_dotenv()

C1socket = SocketPS(IP, PORTSOCKET)

async def errorHandling(ctx: discord.ApplicationContext, error: str, workspaceFolders: list[str], uploaded_file_paths: list[str], mountPaths: list[str], C1ftp: FTPps) -> None:
    embe = discord.Embed(title="Error",
                            description=error,
                    colour=0x854bf7)
    embe.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
    embe.set_footer(text="Made with expertise by HTOP")
    await ctx.edit(embed=embe)
    if C1ftp is not None:
        await cleanup(C1ftp, workspaceFolders, uploaded_file_paths, mountPaths)
    else:
        cleanupSimple(workspaceFolders)

async def upload2(ctx: discord.ApplicationContext, saveLocation: str, max_files: int, sys_files: bool, ps_save_pair_upload: bool) -> list | None:

    def check(message: discord.Message, ctx: discord.ApplicationContext) -> discord.Attachment | str:
        if message.author == ctx.author and message.channel == ctx.channel:
            return len(message.attachments) >= 1 or (message.content and GDapi.is_google_drive_link(message.content))

    try:
        message = await bot.wait_for("message", check=lambda message: check(message, ctx), timeout=UPLOAD_TIMEOUT)  # Wait for 300 seconds for a response with one attachments
    except asyncio.TimeoutError:
        await ctx.edit(embed=embUtimeout)
        raise TimeoutError("TIMED OUT!")

    if len(message.attachments) >= 1 and len(message.attachments) <= max_files:
        attachments = message.attachments
        uploaded_file_paths = []
        await message.delete()
        valid_attachments = await checkSaves(ctx, attachments, ps_save_pair_upload, sys_files)

        for attachment in valid_attachments:
            file_path = os.path.join(saveLocation, attachment.filename)
            await attachment.save(file_path)
            
            emb1 = discord.Embed(title="Upload alert: Successful", description=f"File '{attachment.filename}' has been successfully uploaded and saved.",colour=0x854bf7)
            emb1.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
            emb1.set_footer(text="Made with expertise by HTOP")

            logger.info(f"Saved {attachment.filename} to {file_path}")
            
            await ctx.edit(embed=emb1)
            uploaded_file_paths.append(file_path)
    
    elif message.content != None:
        try:
            google_drive_link = message.content
            await message.delete()
            folder_id = await GDapi.grabfolderid(google_drive_link, ctx)
            if not folder_id: raise GDapiError("Could not find the folder id!")
            uploaded_file_paths, *_ = await GDapi.downloadsaves_gd(ctx, folder_id, saveLocation, max_files, [SCE_SYS_CONTENTS] if sys_files else None, ps_save_pair_upload)
           
        except asyncio.TimeoutError:
            await ctx.edit(embed=embgdt)
            raise TimeoutError("TIMED OUT!")
    
    else:
        await ctx.send("Reply to the message with files that does not reach the limit, or a public google drive link (no subfolders and dont reach the file limit)!", ephemeral=True)
        
    return uploaded_file_paths

async def upload1(ctx: discord.ApplicationContext, saveLocation: str) -> str | None:

    def check(message: discord.Message, ctx: discord.ApplicationContext) -> discord.Attachment | str:
        if message.author == ctx.author and message.channel == ctx.channel:
            return len(message.attachments) == 1 or (message.content and GDapi.is_google_drive_link(message.content))
        
    try:
        message = await bot.wait_for("message", check=lambda message: check(message, ctx), timeout=UPLOAD_TIMEOUT)  # Wait for 120 seconds for a response with an attachment
    except asyncio.TimeoutError:
        await ctx.edit(embed=embUtimeout)
        raise TimeoutError("TIMED OUT!")

    if len(message.attachments) == 1:
        attachment = message.attachments[0]

        if attachment.size > FILE_LIMIT_DISCORD:
            emb15 = discord.Embed(title="Upload alert: Error",
                      description=f"Sorry, the file size of '{attachment.filename}' exceeds the limit of {int(FILE_LIMIT_DISCORD / 1024 / 1024)} MB.",
                      colour=0x854bf7)
    
            emb15.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")

            emb15.set_footer(text="Made with expertise by HTOP")
            await ctx.edit(embed=emb15)
            await message.delete()
            raise FileError("DISCORD UPLOAD ERROR: File size too large!")
        
        else:
            save_path = saveLocation
            file_path = os.path.join(save_path, attachment.filename)
            await attachment.save(file_path)
            logger.info(f"Saved {attachment.filename} to {file_path}")
            emb16 = discord.Embed(title="Upload alert: Successful", description=f"File '{attachment.filename}' has been successfully uploaded and saved.", colour=0x854bf7)
            emb16.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
            emb16.set_footer(text="Made with expertise by HTOP")
            await message.delete()
            await ctx.edit(embed=emb16)

            name_of_file = attachment.filename

    elif message.content != None:
        try:
            google_drive_link = message.content
            await message.delete()
            folder_id = await GDapi.grabfolderid(google_drive_link, ctx)
            if not folder_id: raise GDapiError("Could not find the folder id!")
            *_ , name_of_file = await GDapi.downloadsaves_gd(ctx, folder_id, saveLocation, max_files=1, sys_files=False, ps_save_pair_upload=False)

        except asyncio.TimeoutError:
            await ctx.edit(embed=embgdt)
            raise TimeoutError("TIMED OUT!")
    
    else:
        await ctx.send("Reply to the message with either 1 file, or a public google drive folder link (no subfolders and dont reach the file limit)!", ephemeral=True)

    return name_of_file

async def extra_decrypt(ctx: discord.ApplicationContext, title_id: str, destination_directory: str, savePairName: str) -> None:
    embedTimeout = discord.Embed(title="Timeout Error:", description="You took too long, sending the file with the format: Encrypted", color=0x854bf7)
    embedTimeout.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
        
    embedFormat = discord.Embed(title=f"Format: {savePairName}", description="Choose what format you want the file to be sent in", color=0x854bf7)
    embedFormat.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
    embedFormat.set_footer(text="If you want to use the file in a save editor, choose decrypted")

    helper = TimeoutHelper(embedTimeout)

    class CryptChoiceButton(discord.ui.View):
        def __init__(self, game: str, start_offset: int, title_id: str) -> None:
            self.game = game
            self.offset = start_offset
            self.title_id = title_id
            super().__init__(timeout=OTHER_TIMEOUT)
                
        async def on_timeout(self) -> None:
            self.disable_all_items()
            await helper.handle_timeout(ctx)

        async def on_error(self, error: Exception, _: Item, __: discord.Interaction) -> None:
            self.disable_all_items()
            embedErrb = discord.Embed(title=f"ERROR!", description=f"Could not decrypt: {error}.", color=0x854bf7)
            embedErrb.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
            embedErrb.set_footer(text="Made with expertise by HTOP")
            helper.embTimeout = embedErrb
            await helper.handle_timeout(ctx)
            logger.error(f"{error} - {ctx.user.name}")
            
        @discord.ui.button(label="Decrypted", style=discord.ButtonStyle.blurple, custom_id="decrypt")
        async def decryption_callback(self, _, interaction: discord.Interaction) -> None:
            await interaction.response.edit_message(view=None)
            try:
                match self.game:
                    case "GTAV" | "RDR2":
                        await Crypto.Rstar.decryptFile(destination_directory, self.offset)
                    case "XENO2":
                        await Crypto.Xeno2.decryptFile(destination_directory)
                    case "BL3":
                        await Crypto.BL3.decryptFile(destination_directory, "ps4", False)
                    case "TTWL":
                        await Crypto.BL3.decryptFile(destination_directory, "ps4", True)
                    case "NDOG":
                        await Crypto.Ndog.decryptFile(destination_directory, self.offset)
                    case "MGSV":
                        await Crypto.MGSV.decryptFile(destination_directory, self.title_id)
                    case "REV2":
                        await Crypto.Rev2.decryptFile(destination_directory)
                    case "DL1" | "DL2" | "DI1":
                        await Crypto.DL.decryptFile(destination_directory)
                    case "RGG":
                       await Crypto.RGG.decryptFile(destination_directory)
                    case "DI2":
                        await Crypto.DI2.decryptFile(destination_directory)
            except CryptoError as e:
                raise CryptoError(e)
            except (ValueError, IOError, IndexError):
                raise CryptoError("Invalid save!")
            
            helper.done = True
            
        @discord.ui.button(label="Encrypted", style=discord.ButtonStyle.blurple, custom_id="encrypt")
        async def encryption_callback(self, _, interaction: discord.Interaction) -> None:
            await interaction.response.edit_message(view=None)
            helper.done = True

    if title_id in GTAV_TITLEID:
        await ctx.edit(embed=embedFormat, view=CryptChoiceButton("GTAV", start_offset=Crypto.Rstar.GTAV_PS_HEADER_OFFSET, title_id=None))
        await helper.await_done()
        
    elif title_id in RDR2_TITLEID:
        await ctx.edit(embed=embedFormat, view=CryptChoiceButton("RDR2", start_offset=Crypto.Rstar.RDR2_PS_HEADER_OFFSET, title_id=None))
        await helper.await_done()

    elif title_id in XENO2_TITLEID:
        await ctx.edit(embed=embedFormat, view=CryptChoiceButton("XENO2", start_offset=None, title_id=None))
        await helper.await_done()

    elif title_id in BL3_TITLEID:
        await ctx.edit(embed=embedFormat, view=CryptChoiceButton("BL3", start_offset=None, title_id=None))
        await helper.await_done()

    elif title_id in WONDERLANDS_TITLEID:
        await ctx.edit(embed=embedFormat, view=CryptChoiceButton("TTWL", start_offset=None, title_id=None))
        await helper.await_done()

    elif title_id in NDOG_TITLEID:
        await ctx.edit(embed=embedFormat, view=CryptChoiceButton("NDOG", start_offset=Crypto.Ndog.START_OFFSET, title_id=None))
        await helper.await_done()

    elif title_id in NDOG_COL_TITLEID:
        await ctx.edit(embed=embedFormat, view=CryptChoiceButton("NDOG", start_offset=Crypto.Ndog.START_OFFSET_COL, title_id=None))
        await helper.await_done()

    elif title_id in NDOG_TLOU2_TITLEID:
        await ctx.edit(embed=embedFormat, view=CryptChoiceButton("NDOG", start_offset=Crypto.Ndog.START_OFFSET_TLOU2, title_id=None))
        await helper.await_done()

    elif title_id in MGSV_TPP_TITLEID or title_id in MGSV_GZ_TITLEID:
        await ctx.edit(embed=embedFormat, view=CryptChoiceButton("MGSV", start_offset=None, title_id=title_id))
        await helper.await_done()

    elif title_id in REV2_TITLEID:
        await ctx.edit(embed=embedFormat, view=CryptChoiceButton("REV2", start_offset=None, title_id=None))
        await helper.await_done()

    elif title_id in DL1_TITLEID or title_id in DL2_TITLEID or title_id in DL1_TITLEID:
        await ctx.edit(embed=embedFormat, view=CryptChoiceButton("DL2", start_offset=None, title_id=None))
        await helper.await_done()
    
    elif title_id in RGG_TITLEID:
        await ctx.edit(embed=embedFormat, view=CryptChoiceButton("RGG", start_offset=None, title_id=None))
        await helper.await_done()

    elif title_id in DI2_TITLEID:
        await ctx.edit(embed=embedFormat, view=CryptChoiceButton("DI2", start_offset=None, title_id=None))
        await helper.await_done()

async def extra_import(title_id: str, file_name: str) -> None:
    try:
        if title_id in GTAV_TITLEID:
            await Crypto.Rstar.checkEnc_ps(file_name, GTAV_TITLEID)
           
        elif title_id in RDR2_TITLEID:
            await Crypto.Rstar.checkEnc_ps(file_name, RDR2_TITLEID)
            
        elif title_id in XENO2_TITLEID:
            await Crypto.Xeno2.checkEnc_ps(file_name)

        elif title_id in BL3_TITLEID:
            await Crypto.BL3.checkEnc_ps(file_name, "ps4", False)
        
        elif title_id in WONDERLANDS_TITLEID:
            await Crypto.BL3.checkEnc_ps(file_name, "ps4", True)

        elif title_id in NDOG_TITLEID:
            await Crypto.Ndog.checkEnc_ps(file_name, Crypto.Ndog.START_OFFSET)

        elif title_id in NDOG_COL_TITLEID:
            await Crypto.Ndog.checkEnc_ps(file_name, Crypto.Ndog.START_OFFSET_COL)

        elif title_id in NDOG_TLOU2_TITLEID:
            await Crypto.Ndog.checkEnc_ps(file_name, Crypto.Ndog.START_OFFSET_TLOU2)

        elif title_id in MGSV_TPP_TITLEID or title_id in MGSV_GZ_TITLEID:
            await Crypto.MGSV.checkEnc_ps(file_name, title_id)

        elif title_id in REV2_TITLEID:
            await Crypto.Rev2.checkEnc_ps(file_name)

        elif title_id in DL1_TITLEID:
            await Crypto.DL.checkEnc_ps(file_name, "DL1")

        elif title_id in DL2_TITLEID:
            await Crypto.DL.checkEnc_ps(file_name, "DL2")

        elif title_id in RGG_TITLEID:
            await Crypto.RGG.checkEnc_ps(file_name)

        elif title_id in DI1_TITLEID:
            await Crypto.DL.checkEnc_ps(file_name, "DI1")
        
        elif title_id in DI2_TITLEID:
            await Crypto.DI2.checkEnc_ps(file_name)

    except CryptoError as e:
        raise CryptoError(e)
    except (ValueError, IOError, IndexError):
        raise CryptoError("Invalid save!")
    
async def psusername(ctx: discord.ApplicationContext, username: str) -> str | None:
    await ctx.defer()

    if username == "":
        user_id = await fetch_accountid_db(ctx.author.id)
        if user_id is not None:
            user_id = hex(user_id)[2:]
            return user_id
        else:
            raise PSNIDError("Could not find previously stored account ID.")

    def check(message: discord.Message, ctx: discord.ApplicationContext) -> str:
        if message.author == ctx.author and message.channel == ctx.channel:
            return message.content and checkid(message.content)

    limit = 0
    usernamePattern = r"^[a-zA-Z0-9_-]+$"

    if len(username) < 3 or len(username) > 16:
        await ctx.edit(embed=embnv1)
        raise PSNIDError("Invalid PS username!")
    elif not bool(re.match(usernamePattern, username)):
        await ctx.edit(embed=embnv1)
        raise PSNIDError("Invalid PS username!")

    if NPPSO is not None:
        try:
            userSearch = psnawp.user(online_id=username)
            user_id = userSearch.account_id
            user_id = handle_accid(user_id)
            delmsg = False
        
        except PSNAWPNotFound:
            await ctx.respond(embed=emb8)
            delmsg = True

            try:
                response = await bot.wait_for("message", check=lambda message: check(message, ctx), timeout=OTHER_TIMEOUT)
                user_id = response.content
                await response.delete()
            except asyncio.TimeoutError:
                await ctx.edit(embed=embnt)
                raise TimeoutError("TIMED OUT!")
    else:
        while True:

            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://psn.flipscreen.games/search.php?username={username}") as response:
                    response.text = await response.text()

            if response.status == 200 and limit != 20:
                data = json.loads(response.text)
                obtainedUsername = data["online_id"]

                if obtainedUsername.lower() == username.lower():
                    user_id = data["user_id"]
                    user_id = handle_accid(user_id)
                    delmsg = False
                    break
                else:
                    limit += 1
            else:
                await ctx.respond(embed=emb8)
                delmsg = True

                try:
                    response = await bot.wait_for("message", check=lambda message: check(message, ctx), timeout=OTHER_TIMEOUT)
                    user_id = response.content
                    await response.delete()
                    break
                except asyncio.TimeoutError:
                    await ctx.edit(embed=embnt)
                    raise TimeoutError("TIMED OUT!")
            
    if delmsg:
        await asyncio.sleep(0.5)
        await ctx.edit(embed=embvalidpsn)
    else:
        await ctx.respond(embed=embvalidpsn)

    await asyncio.sleep(0.5)
    await write_accountid_db(ctx.author.id, user_id.lower())
    return user_id.lower()

async def replaceDecrypted(ctx: discord.ApplicationContext, fInstance: FTPps, files: list[str], titleid: str, mountLocation: str , upload_individually: bool, upload_decrypted: str, savePairName: str) -> list[str] | None:
    completed = []
    if upload_individually or len(files) == 1:
        for file in files:
            fullPath = mountLocation + "/" + file
            cwdHere = fullPath.split("/")
            lastN = cwdHere.pop(len(cwdHere) - 1)
            cwdHere = "/".join(cwdHere)

            emb18 = discord.Embed(title=f"Resigning Process (Decrypted): Upload\n{savePairName}",
                            description=f"Please attach a decrypted savefile that you want to upload, MUST be equivalent to {file} (can be any name).",
                            colour=0x854bf7)
            emb18.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
            emb18.set_footer(text="Made with expertise by HTOP")

            await ctx.edit(embed=emb18)

            attachmentName = await upload1(ctx, upload_decrypted)
            attachmentPath = os.path.join(upload_decrypted, attachmentName)
            newPath = os.path.join(upload_decrypted, lastN)
            os.rename(attachmentPath, newPath)
            await extra_import(titleid, newPath)

            await fInstance.replacer(cwdHere, lastN)
            completed.append(file)
    
    else:
        SPLITVALUE = "SLASH"
        patterned = "\n".join(files)
        emb18 = discord.Embed(title=f"Resigning Process (Decrypted): Upload\n{savePairName}",
                            description=f"Please attach at least one of these files and make sure its the same name, including path in the name if that is the case. Instead of '/' use '{SPLITVALUE}', here are the contents:\n\n**{patterned}**",
                            colour=0x854bf7)
        emb18.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
        emb18.set_footer(text="Made with expertise by HTOP")

        await ctx.edit(embed=emb18)
        uploaded_file_paths = await upload2(ctx, upload_decrypted, max_files=MAX_FILES, sys_files=False, ps_save_pair_upload=False)

        if len(uploaded_file_paths) >= 1:
            for file in os.listdir(upload_decrypted):
                file1 = file.split(SPLITVALUE)
                if file1[0] == "": file1 = file1[1:]
                file1 = "/".join(file1)

                if file1 not in patterned:
                    os.remove(os.path.join(upload_decrypted, file))
                    
                else:
                    for saveFile in files:
                        if file1 == saveFile:
                            lastN = os.path.basename(saveFile)
                            cwdHere = saveFile.split("/")
                            cwdHere = cwdHere[:-1]
                            cwdHere = "/".join(cwdHere)
                            cwdHere = mountLocation + "/" + cwdHere

                            filePath = os.path.join(upload_decrypted, file)
                            newRename = os.path.join(upload_decrypted, lastN)
                            os.rename(filePath, newRename)
                            await extra_import(titleid, newRename)

                            await fInstance.replacer(cwdHere, lastN) 
                            completed.append(lastN)     
                    
        else:
            raise FileError("Too many files!")

    if len(completed) == 0:
        raise FileError("Could not replace any files")

    return completed

class threadButton(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Create thread", style=discord.ButtonStyle.primary, custom_id="CreateThread")
    async def callback(self, _, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Creating thread...", ephemeral=True)

        ids_to_remove = []
        
        try:
            thread = await interaction.channel.create_thread(name=interaction.user.name, auto_archive_duration=10080)
            await thread.send(interaction.user.mention)
            ids_to_remove = await write_threadid_db(interaction.user.id, thread.id)
            
        except (WorkspaceError, discord.Forbidden) as e:
            logger.error(f"Can not create thread: {e}")
        
        try:
            for thread_id in ids_to_remove:
                old_thread = bot.get_channel(thread_id)
                if old_thread is not None:
                    await old_thread.delete() 
        except discord.Forbidden:
            pass

@bot.event
async def on_ready() -> None:
    startup()
    bot.add_view(threadButton())
    print(
        f"Bot is ready, invite link: https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot"
    )

@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return

    if message.content == "hello":
        await message.channel.send("hi")

    await bot.process_commands(message)

@bot.slash_command(description="Resign encrypted savefiles (the usable ones you put in the console).")
async def resign(ctx: discord.ApplicationContext, playstation_id: Option(str, description=PS_ID_DESC, default="")) -> None: # type: ignore
    newUPLOAD_ENCRYPTED, newUPLOAD_DECRYPTED, newDOWNLOAD_ENCRYPTED, newPNG_PATH, newPARAM_PATH, newDOWNLOAD_DECRYPTED, newKEYSTONE_PATH = initWorkspace()
    workspaceFolders = [newUPLOAD_ENCRYPTED, newUPLOAD_DECRYPTED, newDOWNLOAD_ENCRYPTED, 
                        newPNG_PATH, newPARAM_PATH, newDOWNLOAD_DECRYPTED, newKEYSTONE_PATH]
    try: await makeWorkspace(ctx, workspaceFolders, ctx.channel_id)
    except WorkspaceError: return
    C1ftp = FTPps(IP, PORT, PS_UPLOADDIR, newDOWNLOAD_DECRYPTED, newUPLOAD_DECRYPTED, newUPLOAD_ENCRYPTED,
                  newDOWNLOAD_ENCRYPTED, newPARAM_PATH, newKEYSTONE_PATH, newPNG_PATH)
    mountPaths = []
    
    try:
        user_id = await psusername(ctx, playstation_id)
        await asyncio.sleep(0.5)
        await ctx.edit(embed=embEncrypted1)
        uploaded_file_paths = await upload2(ctx, newUPLOAD_ENCRYPTED, max_files=MAX_FILES, sys_files=False, ps_save_pair_upload=True)
    except HTTPError as e:
        await ctx.edit(embed=embhttp)
        cleanupSimple(workspaceFolders)
        logger.exception(f"{e} - {ctx.user.name} - (expected)")
        return
    except (PSNIDError, TimeoutError, GDapiError) as e:
        await errorHandling(ctx, e, workspaceFolders, None, None, None)
        logger.exception(f"{e} - {ctx.user.name} - (expected)")
        return
    except Exception as e:
        await errorHandling(ctx, BASE_ERROR_MSG, workspaceFolders, None, None, None)
        logger.exception(f"{e} - {ctx.user.name} - (unexpected)")
        return

    savenames = obtain_savenames(newUPLOAD_ENCRYPTED)

    if len(uploaded_file_paths) >= 2:
        random_string = generate_random_string(RANDOMSTRING_LENGTH)
        uploaded_file_paths = enumerateFiles(uploaded_file_paths, random_string)
        for save in savenames:
            realSave = f"{save}_{random_string}"
            random_string_mount = generate_random_string(RANDOMSTRING_LENGTH)
            try:
                os.rename(os.path.join(newUPLOAD_ENCRYPTED, save), os.path.join(newUPLOAD_ENCRYPTED, realSave))
                os.rename(os.path.join(newUPLOAD_ENCRYPTED, save + ".bin"), os.path.join(newUPLOAD_ENCRYPTED, realSave + ".bin"))
                emb4 = discord.Embed(title="Resigning process: Encrypted",
                            description=f"Your save (**{save}**) is being resigned, please wait...",
                            colour=0x854bf7)
                emb4.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
                emb4.set_footer(text="Made with expertise by HTOP")

                await ctx.edit(embed=emb4)
                await C1ftp.uploadencrypted_bulk(realSave)
                mount_location_new = MOUNT_LOCATION + "/" + random_string_mount
                await C1ftp.make1(mount_location_new)
                mountPaths.append(mount_location_new)
                await C1socket.socket_dump(mount_location_new, realSave)
                location_to_scesys = mount_location_new + "/sce_sys"
                await C1ftp.dlparam(location_to_scesys, user_id)
                await C1socket.socket_update(mount_location_new, realSave)
                await C1ftp.dlencrypted_bulk(False, user_id, realSave)

                emb5 = discord.Embed(title="Resigning process (Encrypted): Successful",
                            description=f"**{save}** resigned to **{playstation_id or user_id}**",
                            colour=0x854bf7)
                emb5.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
                emb5.set_footer(text="Made with expertise by HTOP")

                await ctx.edit(embed=emb5)

            except (SocketError, FTPError, OrbisError, OSError) as e:
                if isinstance(e, OSError) and hasattr(e, "winerror") and e.winerror == 121: 
                    e = "PS4 not connected!"
                await errorHandling(ctx, e, workspaceFolders, uploaded_file_paths, mountPaths, C1ftp)
                logger.exception(f"{e} - {ctx.user.name} - (expected)")
                return
            except Exception as e:
                await errorHandling(ctx, BASE_ERROR_MSG, workspaceFolders, uploaded_file_paths, mountPaths, C1ftp)
                logger.exception(f"{e} - {ctx.user.name} - (unexpected)")
                return
            
        if len(savenames) == 1:
            finishedFiles = "".join(savenames)
        else: finishedFiles = ", ".join(savenames)
        
        embRdone = discord.Embed(title="Resigning process (Encrypted): Successful",
                            description=f"**{finishedFiles}** resigned to **{playstation_id or user_id}**.",
                            colour=0x854bf7)
        embRdone.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
        embRdone.set_footer(text="Made with expertise by HTOP")
        
        await ctx.edit(embed=embRdone)
        
        final_file_name = "PS4.zip"
        zipfiles(newDOWNLOAD_ENCRYPTED, final_file_name)
        final_file = os.path.join(newDOWNLOAD_ENCRYPTED, final_file_name)
        final_size = os.path.getsize(final_file)
        file_size_mb = final_size / (1024 * 1024)

        if file_size_mb < BOT_DISCORD_UPLOAD_LIMIT:
            await ctx.respond(file=discord.File(final_file))
        else:
            file_url = await GDapi.uploadzip(final_file, final_file_name)
            embg = discord.Embed(title="Google Drive: Upload complete",
                        description=f"Here is **{finishedFiles}** resigned:\n<{file_url}>.",
                        colour=0x854bf7)
            embg.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
            embg.set_footer(text="Made with expertise by HTOP")
            await ctx.respond(embed=embg)

        await asyncio.sleep(1)
        await cleanup(C1ftp, workspaceFolders, uploaded_file_paths, mountPaths)
            
    else: 
        await ctx.edit(embed=emb6)
        cleanupSimple(workspaceFolders)

@bot.slash_command(description="Decrypt a savefile and download the contents.")
async def decrypt(ctx: discord.ApplicationContext, include_sce_sys: Option(bool, description="Choose if you want to include the 'sce_sys' folder.")) -> None: # type: ignore
    newUPLOAD_ENCRYPTED, newUPLOAD_DECRYPTED, newDOWNLOAD_ENCRYPTED, newPNG_PATH, newPARAM_PATH, newDOWNLOAD_DECRYPTED, newKEYSTONE_PATH = initWorkspace()
    workspaceFolders = [newUPLOAD_ENCRYPTED, newUPLOAD_DECRYPTED, newDOWNLOAD_ENCRYPTED, 
                        newPNG_PATH, newPARAM_PATH, newDOWNLOAD_DECRYPTED, newKEYSTONE_PATH]
    try: await makeWorkspace(ctx, workspaceFolders, ctx.channel_id)
    except WorkspaceError: return
    C1ftp = FTPps(IP, PORT, PS_UPLOADDIR, newDOWNLOAD_DECRYPTED, newUPLOAD_DECRYPTED, newUPLOAD_ENCRYPTED,
                  newDOWNLOAD_ENCRYPTED, newPARAM_PATH, newKEYSTONE_PATH, newPNG_PATH)
    mountPaths = []

    await ctx.respond(embed=embDecrypt1)
    try:
        uploaded_file_paths = await upload2(ctx, newUPLOAD_ENCRYPTED, max_files=MAX_FILES, sys_files=False, ps_save_pair_upload=True)
    except HTTPError as e:
        await ctx.edit(embed=embhttp)
        cleanupSimple(workspaceFolders)
        logger.exception(f"{e} - {ctx.user.name} - (expected)")
        return
    except (TimeoutError, GDapiError) as e:
        await errorHandling(ctx, e, workspaceFolders, None, None, None)
        logger.exception(f"{e} - {ctx.user.name} - (expected)")
        return
    except Exception as e:
        await errorHandling(ctx, BASE_ERROR_MSG, workspaceFolders, None, None, None)
        logger.exception(f"{e} - {ctx.user.name} - (unexpected)")
        return
            
    savenames = obtain_savenames(newUPLOAD_ENCRYPTED)
 
    if len(uploaded_file_paths) >= 2:
        random_string = generate_random_string(RANDOMSTRING_LENGTH)
        uploaded_file_paths = enumerateFiles(uploaded_file_paths, random_string)
        for save in savenames:
            destination_directory = os.path.join(newDOWNLOAD_DECRYPTED, f"dec_{save}")
            realSave = f"{save}_{random_string}"
            random_string_mount = generate_random_string(RANDOMSTRING_LENGTH)

            emb11 = discord.Embed(title="Decrypt process: Initializing",
                      description=f"Mounting {save}.",
                      colour=0x854bf7)
            emb11.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
            emb11.set_footer(text="Made with expertise by HTOP")
            
            try:
                os.rename(os.path.join(newUPLOAD_ENCRYPTED, save), os.path.join(newUPLOAD_ENCRYPTED, realSave))
                os.rename(os.path.join(newUPLOAD_ENCRYPTED, save + ".bin"), os.path.join(newUPLOAD_ENCRYPTED, realSave + ".bin"))
                os.mkdir(destination_directory)
                await ctx.edit(embed=emb11)
                await C1ftp.uploadencrypted_bulk(realSave)
                mount_location_new = MOUNT_LOCATION + "/" + random_string_mount
                await C1ftp.make1(mount_location_new)
                mountPaths.append(mount_location_new)
                await C1socket.socket_dump(mount_location_new, realSave)
                await ctx.edit(embed=emb12)

                if include_sce_sys:
                    await C1ftp.ftp_download_folder(mount_location_new, destination_directory, False)
                else:
                    await C1ftp.ftp_download_folder(mount_location_new, destination_directory, True)
                
                location_to_scesys = mount_location_new + "/sce_sys"
                await C1ftp.dlparamonly_grab(location_to_scesys)
                title_id_grab = await obtainCUSA(newPARAM_PATH)
                os.rename(destination_directory, destination_directory + f"_{title_id_grab}")
                destination_directory = destination_directory + f"_{title_id_grab}"

                emb13 = discord.Embed(title="Decrypt process: Successful",
                            description=f"Downloaded the decrypted save of **{save}** from **{title_id_grab}**.",
                            colour=0x854bf7)
                emb13.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
                emb13.set_footer(text="Made with expertise by HTOP")
                
                await extra_decrypt(ctx, title_id_grab, destination_directory, save)

                await ctx.edit(embed=emb13)

            except (SocketError, FTPError, OrbisError, CryptoError, OSError) as e:
                if isinstance(e, OSError) and hasattr(e, "winerror") and e.winerror == 121: 
                    e = "PS4 not connected!"
                await errorHandling(ctx, e, workspaceFolders, uploaded_file_paths, mountPaths, C1ftp)
                logger.exception(f"{e} - {ctx.user.name} - (expected)")
                return
            except Exception as e:
                await errorHandling(ctx, BASE_ERROR_MSG, workspaceFolders, uploaded_file_paths, mountPaths, C1ftp)
                logger.exception(f"{e} - {ctx.user.name} - (unexpected)")
                return
        
        if len(os.listdir(newDOWNLOAD_DECRYPTED)) == 1:
            zip_name = os.listdir(newDOWNLOAD_DECRYPTED)
            zip_name = "".join(zip_name)
            zip_name += ".zip"
        else:
            zip_name = "Decrypted-Saves.zip"
        
        zipfiles(newDOWNLOAD_DECRYPTED, zip_name)
        zip_in_THIS_path = os.path.join(newDOWNLOAD_DECRYPTED, zip_name)
        size_check1 = os.path.getsize(zip_in_THIS_path)
        size_in_mb = size_check1 / (1024 * 1024)

        if len(savenames) == 1:
            finishedFiles = "".join(savenames)
        else: finishedFiles = ", ".join(savenames)

        embDdone = discord.Embed(title="Decryption process: Successful",
                            description=f"**{finishedFiles}** has been decrypted.",
                            colour=0x854bf7)
        embDdone.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
        embDdone.set_footer(text="Made with expertise by HTOP")

        await ctx.edit(embed=embDdone)

        if size_in_mb < BOT_DISCORD_UPLOAD_LIMIT:
            await ctx.respond(file=discord.File(zip_in_THIS_path))
        else:
            file_url = await GDapi.uploadzip(zip_in_THIS_path, zip_name)
            embg = discord.Embed(title="Google Drive: Upload complete", description=f"Here is **{finishedFiles}** decrypted:\n<{file_url}>", colour=0x854bf7)
            embg.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
            embg.set_footer(text="Made with expertise by HTOP")
            await ctx.respond(embed=embg)
        
        await asyncio.sleep(1)
        await cleanup(C1ftp, workspaceFolders, uploaded_file_paths, mountPaths)

    else:
        await ctx.edit(embed=emb6)
        cleanupSimple(workspaceFolders)

@bot.slash_command(description="Swap the decrypted savefile from the encrypted ones you upload.")
async def encrypt(ctx: discord.ApplicationContext, upload_individually: Option(bool, description="Choose if you want to upload the decrypted files one by one, or the ones you want at once."), include_sce_sys: Option(bool, description="Choose if you want to upload the contents of the 'sce_sys' folder."), playstation_id: Option(str, description=PS_ID_DESC, default="")) -> None: # type: ignore # type: ignore
    newUPLOAD_ENCRYPTED, newUPLOAD_DECRYPTED, newDOWNLOAD_ENCRYPTED, newPNG_PATH, newPARAM_PATH, newDOWNLOAD_DECRYPTED, newKEYSTONE_PATH = initWorkspace()
    workspaceFolders = [newUPLOAD_ENCRYPTED, newUPLOAD_DECRYPTED, newDOWNLOAD_ENCRYPTED, 
                        newPNG_PATH, newPARAM_PATH, newDOWNLOAD_DECRYPTED, newKEYSTONE_PATH]
    try: await makeWorkspace(ctx, workspaceFolders, ctx.channel_id)
    except WorkspaceError: return
    C1ftp = FTPps(IP, PORT, PS_UPLOADDIR, newDOWNLOAD_DECRYPTED, newUPLOAD_DECRYPTED, newUPLOAD_ENCRYPTED,
                  newDOWNLOAD_ENCRYPTED, newPARAM_PATH, newKEYSTONE_PATH, newPNG_PATH)
    mountPaths = []

    try:
        user_id = await psusername(ctx, playstation_id)
        await asyncio.sleep(0.5)
        await ctx.edit(embed=emb14)
        uploaded_file_paths = await upload2(ctx, newUPLOAD_ENCRYPTED, max_files=MAX_FILES, sys_files=False, ps_save_pair_upload=True)
    except HTTPError as e:
        await ctx.edit(embed=embhttp)
        cleanupSimple(workspaceFolders)
        logger.exception(f"{e} - {ctx.user.name} - (expected)")
        return
    except (PSNIDError, TimeoutError, GDapiError) as e:
        await errorHandling(ctx, e, workspaceFolders, None, None, None)
        logger.exception(f"{e} - {ctx.user.name} - (expected)")
        return
    except Exception as e:
        await errorHandling(ctx, BASE_ERROR_MSG, workspaceFolders, None, None, None)
        logger.exception(f"{e} - {ctx.user.name} - (unexpected)")
        return

    savenames = obtain_savenames(newUPLOAD_ENCRYPTED)
    full_completed = []

    if len(uploaded_file_paths) >= 2:
        random_string = generate_random_string(RANDOMSTRING_LENGTH)
        uploaded_file_paths = enumerateFiles(uploaded_file_paths, random_string)
        for save in savenames:
            realSave = f"{save}_{random_string}"
            random_string_mount = generate_random_string(RANDOMSTRING_LENGTH)
            try:
                os.rename(os.path.join(newUPLOAD_ENCRYPTED, save), os.path.join(newUPLOAD_ENCRYPTED, realSave))
                os.rename(os.path.join(newUPLOAD_ENCRYPTED, save + ".bin"), os.path.join(newUPLOAD_ENCRYPTED, realSave + ".bin"))
                await ctx.edit(embed=emb17)
                await C1ftp.uploadencrypted_bulk(realSave)
                mount_location_new = MOUNT_LOCATION + "/" + random_string_mount
                await C1ftp.make1(mount_location_new)
                mountPaths.append(mount_location_new)
                await C1socket.socket_dump(mount_location_new, realSave)
            
                files = await C1ftp.ftpListContents(mount_location_new)

                if len(files) == 0: raise FileError("Could not list any decrypted saves!")
                location_to_scesys = mount_location_new + "/sce_sys"
                await C1ftp.dlparamonly_grab(location_to_scesys)
                title_id = await obtainCUSA(newPARAM_PATH)

                if upload_individually: 
                    completed = await replaceDecrypted(ctx, C1ftp, files, title_id, mount_location_new, True, newUPLOAD_DECRYPTED, save)
                else: 
                    completed = await replaceDecrypted(ctx, C1ftp, files, title_id, mount_location_new, False, newUPLOAD_DECRYPTED, save)

                if include_sce_sys:
                    if len(os.listdir(newUPLOAD_DECRYPTED)) > 0:
                        shutil.rmtree(newUPLOAD_DECRYPTED)
                        os.mkdir(newUPLOAD_DECRYPTED)
                        
                    embSceSys = discord.Embed(title=f"Upload: sce_sys contents\n{save}",
                        description="Please attach the sce_sys files you want to upload.",
                        colour=0x854bf7)
                    embSceSys.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
                    embSceSys.set_footer(text="Made with expertise by HTOP")

                    await ctx.edit(embed=embSceSys)
                    uploaded_file_paths_sys = await upload2(ctx, newUPLOAD_DECRYPTED, max_files=len(SCE_SYS_CONTENTS), sys_files=True, ps_save_pair_upload=False)

                    if len(uploaded_file_paths_sys) <= len(SCE_SYS_CONTENTS) and len(uploaded_file_paths) >= 1:
                        filesToUpload = os.listdir(newUPLOAD_DECRYPTED)
                        await C1ftp.upload_scesysContents(ctx, filesToUpload, location_to_scesys)
                    
                location_to_scesys = mount_location_new + "/sce_sys"
                await C1ftp.dlparam(location_to_scesys, user_id)
                await C1socket.socket_update(mount_location_new, realSave)
                await C1ftp.dlencrypted_bulk(False, user_id, realSave)

                if len(completed) == 1: completed = "".join(completed)
                else: completed = ", ".join(completed)
                full_completed.append(completed)

                embmidComplete = discord.Embed(title="Resigning Process (Decrypted): Successful",
                            description=f"Resigned **{completed}** with title id **{title_id}** to **{playstation_id or user_id}**.",
                            colour=0x854bf7)
                embmidComplete.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
                embmidComplete.set_footer(text="Made with expertise by HTOP")

                await ctx.edit(embed=embmidComplete)
            except HTTPError as e:
                await ctx.edit(embed=embhttp)
                cleanup(C1ftp, workspaceFolders, uploaded_file_paths, mountPaths)
                logger.exception(f"{e} - {ctx.user.name} - (expected)")
                return
            except (SocketError, FTPError, OrbisError, FileError, CryptoError, OSError) as e:
                if isinstance(e, OSError) and hasattr(e, "winerror") and e.winerror == 121: 
                    e = "PS4 not connected!"
                await errorHandling(ctx, e, workspaceFolders, uploaded_file_paths, mountPaths, C1ftp)
                logger.exception(f"{e} - {ctx.user.name} - (expected)")
                return
            except Exception as e:
                await errorHandling(ctx, BASE_ERROR_MSG, workspaceFolders, uploaded_file_paths, mountPaths, C1ftp)
                logger.exception(f"{e} - {ctx.user.name} - (unexpected)")
                return
            
        if len(full_completed) == 1: full_completed = "".join(full_completed)
        else: full_completed = ", ".join(full_completed)

        embComplete = discord.Embed(title="Resigning Process (Decrypted): Successful",
                        description=f"Resigned **{full_completed}** to **{playstation_id or user_id}**.",
                        colour=0x854bf7)
        embComplete.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
        embComplete.set_footer(text="Made with expertise by HTOP")

        await ctx.edit(embed=embComplete)

        final_file_name = "PS4.zip"
        zipfiles(newDOWNLOAD_ENCRYPTED, final_file_name)
        final_file = os.path.join(newDOWNLOAD_ENCRYPTED, final_file_name)
        final_size = os.path.getsize(final_file)
        file_size_mb = final_size / (1024 * 1024)

        if file_size_mb < BOT_DISCORD_UPLOAD_LIMIT:
            await ctx.respond(file=discord.File(final_file))
        else:
            file_url = await GDapi.uploadzip(final_file, final_file_name)

            embg = discord.Embed(title="Google Drive: Upload complete",
                        description=f"Here is your save:\n<{file_url}>",
                        colour=0x854bf7)
            embg.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
            embg.set_footer(text="Made with expertise by HTOP")
            await ctx.edit(embed=embg)

        await cleanup(C1ftp, workspaceFolders, uploaded_file_paths, mountPaths)
    else:
        await ctx.edit(embed=emb6)
        cleanupSimple(workspaceFolders)

@bot.slash_command(description="Change the region of a save (Must be from the same game).")
async def reregion(ctx: discord.ApplicationContext, playstation_id: Option(str, description=PS_ID_DESC, default="")) -> None:  # type: ignore
    newUPLOAD_ENCRYPTED, newUPLOAD_DECRYPTED, newDOWNLOAD_ENCRYPTED, newPNG_PATH, newPARAM_PATH, newDOWNLOAD_DECRYPTED, newKEYSTONE_PATH = initWorkspace()
    workspaceFolders = [newUPLOAD_ENCRYPTED, newUPLOAD_DECRYPTED, newDOWNLOAD_ENCRYPTED, 
                        newPNG_PATH, newPARAM_PATH, newDOWNLOAD_DECRYPTED, newKEYSTONE_PATH]
    try: await makeWorkspace(ctx, workspaceFolders, ctx.channel_id)
    except WorkspaceError: return
    C1ftp = FTPps(IP, PORT, PS_UPLOADDIR, newDOWNLOAD_DECRYPTED, newUPLOAD_DECRYPTED, newUPLOAD_ENCRYPTED,
                  newDOWNLOAD_ENCRYPTED, newPARAM_PATH, newKEYSTONE_PATH, newPNG_PATH)
    mountPaths = []

    try:
        user_id = await psusername(ctx, playstation_id)
        await asyncio.sleep(0.5)
        await ctx.edit(embed=emb21)
        uploaded_file_paths = await upload2(ctx, newUPLOAD_ENCRYPTED, max_files=2, sys_files=False, ps_save_pair_upload=True)
    except HTTPError as e:
        await ctx.edit(embed=embhttp)
        cleanupSimple(workspaceFolders)
        logger.exception(f"{e} - {ctx.user.name} - (expected)")
        return
    except (PSNIDError, TimeoutError, GDapiError) as e:
        await errorHandling(ctx, e, workspaceFolders, None, None, None)
        logger.exception(f"{e} - {ctx.user.name} - (expected)")
        return
    except Exception as e:
        await errorHandling(ctx, BASE_ERROR_MSG, workspaceFolders, None, None, None)
        logger.exception(f"{e} - {ctx.user.name} - (unexpected)")
        return
        
    savenames = obtain_savenames(newUPLOAD_ENCRYPTED)
    savename = "".join(savenames)

    if len(uploaded_file_paths) == 2:
        random_string = generate_random_string(RANDOMSTRING_LENGTH)
        uploaded_file_paths = enumerateFiles(uploaded_file_paths, random_string)
        savename += f"_{random_string}"
        try:
            for file in os.listdir(newUPLOAD_ENCRYPTED):
                if file.endswith(".bin"):
                    os.rename(os.path.join(newUPLOAD_ENCRYPTED, file), os.path.join(newUPLOAD_ENCRYPTED, os.path.splitext(file)[0] + f"_{random_string}" + ".bin"))
                else:
                    os.rename(os.path.join(newUPLOAD_ENCRYPTED, file), os.path.join(newUPLOAD_ENCRYPTED, file + f"_{random_string}"))
        
            await ctx.edit(embed=emb22)
            await C1ftp.uploadencrypted()
            mount_location_new = MOUNT_LOCATION + "/" + random_string
            await C1ftp.make1(mount_location_new)
            mountPaths.append(mount_location_new)
            await C1socket.socket_dump(mount_location_new, savename)
            location_to_scesys = mount_location_new + "/sce_sys"
            await C1ftp.retrievekeystone(location_to_scesys)
            await C1ftp.dlparamonly_grab(location_to_scesys)

            target_titleid = await obtainCUSA(newPARAM_PATH)
            
            emb23 = discord.Embed(title="Obtain process: Keystone",
                          description=f"Keystone from **{target_titleid}** obtained.",
                          colour=0x854bf7)
            emb23.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
            emb23.set_footer(text="Made with expertise by HTOP")

            await ctx.edit(embed=emb23)

            shutil.rmtree(newUPLOAD_ENCRYPTED)
            os.makedirs(newUPLOAD_ENCRYPTED)

            await C1ftp.deleteuploads(savename)

        except (SocketError, FTPError, OrbisError, OSError) as e:
            if isinstance(e, OSError) and hasattr(e, "winerror") and e.winerror == 121: 
                e = "PS4 not connected!"
            await errorHandling(ctx, e, workspaceFolders, uploaded_file_paths, mountPaths, C1ftp)
            logger.exception(f"{e} - {ctx.user.name} - (expected)")
            return
        except Exception as e:
            await errorHandling(ctx, BASE_ERROR_MSG, workspaceFolders, uploaded_file_paths, mountPaths, C1ftp)
            logger.exception(f"{e} - {ctx.user.name} - (unexpected)")
            return
       
    else: 
        await ctx.edit(embed=emb6)
        cleanupSimple(workspaceFolders)
        return

    await ctx.edit(embed=emb20)

    try: uploaded_file_paths = await upload2(ctx, newUPLOAD_ENCRYPTED, max_files=MAX_FILES, sys_files=False, ps_save_pair_upload=True)
    except HTTPError as e:
        await ctx.edit(embed=embhttp)
        await cleanup(C1ftp, workspaceFolders, uploaded_file_paths, mountPaths)
        logger.exception(f"{e} - {ctx.user.name} - (expected)")
        return
    except (TimeoutError, GDapiError) as e:
        await errorHandling(ctx, e, workspaceFolders, uploaded_file_paths, mountPaths, C1ftp)
        logger.exception(f"{e} - {ctx.user.name} - (expected)")
        return
    except Exception as e:
        await errorHandling(ctx, BASE_ERROR_MSG, workspaceFolders, uploaded_file_paths, mountPaths, C1ftp)
        logger.exception(f"{e} - {ctx.user.name} - (unexpected)")
        return
        
    savenames = obtain_savenames(newUPLOAD_ENCRYPTED)

    if len(uploaded_file_paths) >= 2:
        random_string = generate_random_string(RANDOMSTRING_LENGTH)
        uploaded_file_paths = enumerateFiles(uploaded_file_paths, random_string)
        for save in savenames:
            realSave = f"{save}_{random_string}"
            random_string_mount = generate_random_string(RANDOMSTRING_LENGTH)
            try:
                os.rename(os.path.join(newUPLOAD_ENCRYPTED, save), os.path.join(newUPLOAD_ENCRYPTED, realSave))
                os.rename(os.path.join(newUPLOAD_ENCRYPTED, save + ".bin"), os.path.join(newUPLOAD_ENCRYPTED, realSave + ".bin")) 
                emb4 = discord.Embed(title="Resigning process: Encrypted",
                            description=f"Your save (**{save}**) is being resigned, please wait...",
                            colour=0x854bf7)
                emb4.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
                emb4.set_footer(text="Made with expertise by HTOP")
                await ctx.edit(embed=emb4)
                await C1ftp.uploadencrypted_bulk(realSave)
                mount_location_new = MOUNT_LOCATION + "/" + random_string_mount
                await C1ftp.make1(mount_location_new)
                mountPaths.append(mount_location_new)
                location_to_scesys = mount_location_new + "/sce_sys"
                await C1socket.socket_dump(mount_location_new, realSave)
                await C1ftp.reregioner(mount_location_new, target_titleid, user_id)
                await C1ftp.keystoneswap(location_to_scesys)
                await C1socket.socket_update(mount_location_new, realSave)
                await C1ftp.dlencrypted_bulk(True, user_id, realSave)

                emb5 = discord.Embed(title="Re-regioning & Resigning process (Encrypted): Successful",
                            description=f"**{save}** resigned to **{playstation_id or user_id}** (**{target_titleid}**).",
                            colour=0x854bf7)
                emb5.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
                emb5.set_footer(text="Made with expertise by HTOP")

                await ctx.edit(embed=emb5)

            except (SocketError, FTPError, OrbisError, OSError) as e:
                if isinstance(e, OSError) and hasattr(e, "winerror") and e.winerror == 121: 
                    e = "PS4 not connected!"
                await errorHandling(ctx, e, workspaceFolders, uploaded_file_paths, mountPaths, C1ftp)
                logger.exception(f"{e} - {ctx.user.name} - (expected)")
                return
            except Exception as e:
                await errorHandling(ctx, BASE_ERROR_MSG, workspaceFolders, uploaded_file_paths, mountPaths, C1ftp)
                logger.exception(f"{e} - {ctx.user.name} - (unexpected)")
                return
            
        if len(savenames) == 1:
            finishedFiles = "".join(savenames)
        else: finishedFiles = ", ".join(savenames)

        embRgdone = discord.Embed(title="Re-regioning & Resigning process (Encrypted): Successful",
                            description=f"**{finishedFiles}** resigned to **{playstation_id or user_id}** (**{target_titleid}**).",
                            colour=0x854bf7)
        embRgdone.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
        embRgdone.set_footer(text="Made with expertise by HTOP")
        
        await ctx.edit(embed=embRgdone)
        
        final_file_name = "PS4.zip"
        zipfiles(newDOWNLOAD_ENCRYPTED, final_file_name)
        final_file = os.path.join(newDOWNLOAD_ENCRYPTED, final_file_name)
        final_size = os.path.getsize(final_file)
        file_size_mb = final_size / (1024 * 1024)

        if file_size_mb < BOT_DISCORD_UPLOAD_LIMIT:
            await ctx.respond(file=discord.File(final_file))
        else:
            file_url = await GDapi.uploadzip(final_file, final_file_name)

            embg = discord.Embed(title="Google Drive: Upload complete",
                    description=f"Here is **{finishedFiles}** re-regioned and resigned to **{playstation_id or user_id}** with title id **{target_titleid}**:\n<{file_url}>",
                    colour=0x854bf7)
            embg.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
            embg.set_footer(text="Made with expertise by HTOP")
            await ctx.respond(embed=embg)

        if target_titleid in XENO2_TITLEID or target_titleid in MGSV_TPP_TITLEID or target_titleid in MGSV_GZ_TITLEID:
            await ctx.respond("Make sure to remove the random string after and including '_' when you are going to copy that file to the console. Only required if you re-regioned more than 1 save at once.", ephemeral=True)

        await asyncio.sleep(1)
        await cleanup(C1ftp, workspaceFolders, uploaded_file_paths, mountPaths)
        
    else: 
        await ctx.edit(embed=emb6)
        cleanupSimple(workspaceFolders)

@change_group.command(description="Changes the picture of your save, this is just cosmetic.")
async def picture(ctx: discord.ApplicationContext, picture: discord.Attachment, playstation_id: Option(str, description=PS_ID_DESC, defualt="")) -> None: # type: ignore
    newUPLOAD_ENCRYPTED, newUPLOAD_DECRYPTED, newDOWNLOAD_ENCRYPTED, newPNG_PATH, newPARAM_PATH, newDOWNLOAD_DECRYPTED, newKEYSTONE_PATH = initWorkspace()
    workspaceFolders = [newUPLOAD_ENCRYPTED, newUPLOAD_DECRYPTED, newDOWNLOAD_ENCRYPTED, 
                        newPNG_PATH, newPARAM_PATH, newDOWNLOAD_DECRYPTED, newKEYSTONE_PATH]
    try: await makeWorkspace(ctx, workspaceFolders, ctx.channel_id)
    except WorkspaceError: return
    C1ftp = FTPps(IP, PORT, PS_UPLOADDIR, newDOWNLOAD_DECRYPTED, newUPLOAD_DECRYPTED, newUPLOAD_ENCRYPTED,
                  newDOWNLOAD_ENCRYPTED, newPARAM_PATH, newKEYSTONE_PATH, newPNG_PATH)
    mountPaths = []
    pngfile = os.path.join(newPNG_PATH, "icon0.png")
    size = (228, 128)

    try:
        user_id = await psusername(ctx, playstation_id)
        await asyncio.sleep(0.5)
        await ctx.edit(embed=embpng)
        uploaded_file_paths = await upload2(ctx, newUPLOAD_ENCRYPTED, max_files=MAX_FILES, sys_files=False, ps_save_pair_upload=True)
    except HTTPError as e:
        await ctx.edit(embed=embhttp)
        cleanupSimple(workspaceFolders)
        logger.exception(f"{e} - {ctx.user.name} - (expected)")
        return
    except (TimeoutError, GDapiError) as e:
        await errorHandling(ctx, e, workspaceFolders, None, None, None)
        logger.exception(f"{e} - {ctx.user.name} - (expected)")
        return
    except Exception as e:
        await errorHandling(ctx, BASE_ERROR_MSG, workspaceFolders, None, None, None)
        logger.exception(f"{e} - {ctx.user.name} - (unexpected)")
        return
            
    savenames = obtain_savenames(newUPLOAD_ENCRYPTED)

    if len(uploaded_file_paths) >= 2:
        # png handling
        await picture.save(pngfile)
        pngprocess(pngfile, size)
        random_string = generate_random_string(RANDOMSTRING_LENGTH)
        uploaded_file_paths = enumerateFiles(uploaded_file_paths, random_string)
        for save in savenames:
            realSave = f"{save}_{random_string}"
            random_string_mount = generate_random_string(RANDOMSTRING_LENGTH)
            try:
                os.rename(os.path.join(newUPLOAD_ENCRYPTED, save), os.path.join(newUPLOAD_ENCRYPTED, realSave))
                os.rename(os.path.join(newUPLOAD_ENCRYPTED, save + ".bin"), os.path.join(newUPLOAD_ENCRYPTED, realSave + ".bin"))
                await ctx.edit(embed=embpng1)
                await C1ftp.uploadencrypted_bulk(realSave)
                mount_location_new = MOUNT_LOCATION + "/" + random_string_mount
                await C1ftp.make1(mount_location_new)
                mountPaths.append(mount_location_new)
                await C1socket.socket_dump(mount_location_new, realSave)
                await ctx.edit(embed=embpng2)
                location_to_scesys = mount_location_new + "/sce_sys"
                await C1ftp.swappng(location_to_scesys)
                await C1ftp.dlparam(location_to_scesys, user_id)
                await C1socket.socket_update(mount_location_new, realSave)
                await C1ftp.dlencrypted_bulk(False, user_id, realSave)

                embpngs = discord.Embed(title="PNG process: Successful",
                            description=f"Altered the save png of **{save}**.",
                            colour=0x854bf7)
                embpngs.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
                embpngs.set_footer(text="Made with expertise by HTOP")

                await ctx.edit(embed=embpngs)

            except (SocketError, FTPError, OrbisError, OSError) as e:
                if isinstance(e, OSError) and hasattr(e, "winerror") and e.winerror == 121: 
                    e = "PS4 not connected!"
                await errorHandling(ctx, e, workspaceFolders, uploaded_file_paths, mountPaths, C1ftp)
                logger.exception(f"{e} - {ctx.user.name} - (expected)")
                return
            except Exception as e:
                await errorHandling(ctx, BASE_ERROR_MSG, workspaceFolders, uploaded_file_paths, mountPaths, C1ftp)
                logger.exception(f"{e} - {ctx.user.name} - (unexpected)")
                return

        if len(savenames) == 1:
            finishedFiles = "".join(savenames)
        else: finishedFiles = ", ".join(savenames)

        embPdone = discord.Embed(title="PNG process: Successful",
                            description=f"Altered the save png of **{finishedFiles} and resigned to {playstation_id or user_id}**.",
                            colour=0x854bf7)
        embPdone.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
        embPdone.set_footer(text="Made with expertise by HTOP")

        await ctx.edit(embed=embPdone)
        
        final_file_name = "PS4.zip"
        zipfiles(newDOWNLOAD_ENCRYPTED, final_file_name)
        final_file = os.path.join(newDOWNLOAD_ENCRYPTED, final_file_name)
        final_size = os.path.getsize(final_file)
        file_size_mb = final_size / (1024 * 1024)

        if file_size_mb < BOT_DISCORD_UPLOAD_LIMIT:
            await ctx.respond(file=discord.File(final_file))
        else:
            file_url = await GDapi.uploadzip(final_file, final_file_name)

            embg = discord.Embed(title="Google Drive: Upload complete",
                    description=f"Here is **{finishedFiles}** with altered save png:\n<{file_url}>",
                    colour=0x854bf7)
            embg.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
            embg.set_footer(text="Made with expertise by HTOP")
            await ctx.respond(embed=embg)

        await asyncio.sleep(1)
        await cleanup(C1ftp, workspaceFolders, uploaded_file_paths, mountPaths)

    else:
        await ctx.edit(embed=emb6)
        cleanupSimple(workspaceFolders)

@quick_group.command(description="Resign pre stored saves.")
async def resign(ctx: discord.ApplicationContext, playstation_id: Option(str, description=PS_ID_DESC, default="")) -> None: # type: ignore
    newUPLOAD_ENCRYPTED, newUPLOAD_DECRYPTED, newDOWNLOAD_ENCRYPTED, newPNG_PATH, newPARAM_PATH, newDOWNLOAD_DECRYPTED, newKEYSTONE_PATH = initWorkspace()
    workspaceFolders = [newUPLOAD_ENCRYPTED, newUPLOAD_DECRYPTED, newDOWNLOAD_ENCRYPTED, 
                        newPNG_PATH, newPARAM_PATH, newDOWNLOAD_DECRYPTED, newKEYSTONE_PATH]
    try: await makeWorkspace(ctx, workspaceFolders, ctx.channel_id)
    except: return
    C1ftp = FTPps(IP, PORT, PS_UPLOADDIR, newDOWNLOAD_DECRYPTED, newUPLOAD_DECRYPTED, newUPLOAD_ENCRYPTED,
                  newDOWNLOAD_ENCRYPTED, newPARAM_PATH, newKEYSTONE_PATH, newPNG_PATH)
    mountPaths = []
    
    try:
        user_id = await psusername(ctx, playstation_id)
        await asyncio.sleep(0.5)
        response = await listStoredSaves(ctx)
    except (PSNIDError, TimeoutError) as e:
        await errorHandling(ctx, e, workspaceFolders, None, None, None)
        logger.exception(f"{e} - {ctx.user.name} - (expected)")
        return
    except Exception as e:
        await errorHandling(ctx, BASE_ERROR_MSG, workspaceFolders, None, None, None)
        logger.exception(f"{e} - {ctx.user.name} - (unexpected)")
        return
    
    if response == "EXIT":
        embExit = discord.Embed(title="Exited.", colour=0x854bf7)
        embExit.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
        embExit.set_footer(text="Made with expertise by HTOP")
        await ctx.edit(embed=embExit)
        cleanupSimple(workspaceFolders)
        return
    
    random_string = generate_random_string(RANDOMSTRING_LENGTH)
    saveName = os.path.basename(response)
    files = os.listdir(newUPLOAD_ENCRYPTED)
    realSave = f"{saveName}_{random_string}"

    try:
        shutil.copyfile(response, os.path.join(newUPLOAD_ENCRYPTED, f"{saveName}_{random_string}"))
        shutil.copyfile(response + ".bin", os.path.join(newUPLOAD_ENCRYPTED, f"{saveName}_{random_string}.bin"))

        emb4 = discord.Embed(title="Resigning process: Encrypted",
                    description=f"Your save (**{saveName}**) is being resigned, please wait...",
                    colour=0x854bf7)
        emb4.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
        emb4.set_footer(text="Made with expertise by HTOP")

        await ctx.edit(embed=emb4)
        await C1ftp.uploadencrypted_bulk(realSave)
        mount_location_new = MOUNT_LOCATION + "/" + random_string
        await C1ftp.make1(mount_location_new)
        mountPaths.append(mount_location_new)
        await C1socket.socket_dump(mount_location_new, realSave)
        location_to_scesys = mount_location_new + "/sce_sys"
        await C1ftp.dlparam(location_to_scesys, user_id)
        await C1socket.socket_update(mount_location_new, realSave)
        await C1ftp.dlencrypted_bulk(False, user_id, realSave)

        emb5 = discord.Embed(title="Resigning process (Encrypted): Successful",
                    description=f"**{saveName}** resigned to **{playstation_id or user_id}**",
                    colour=0x854bf7)
        emb5.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
        emb5.set_footer(text="Made with expertise by HTOP")

        await ctx.edit(embed=emb5)

    except (SocketError, FTPError, OrbisError, OSError) as e:
        if isinstance(e, OSError) and hasattr(e, "winerror") and e.winerror == 121: 
            e = "PS4 not connected!"
        elif isinstance(e, OrbisError): 
            logger.error(f"{response} is a invalid save") # If OrbisError is raised you have stored an invalid save
        await errorHandling(ctx, e, workspaceFolders, files, mountPaths, C1ftp)
        logger.exception(f"{e} - {ctx.user.name} - (expected)")
        return
    except Exception as e:
        await errorHandling(ctx, BASE_ERROR_MSG, workspaceFolders, files, mountPaths, C1ftp)
        logger.exception(f"{e} - {ctx.user.name} - (unexpected)")
        return
    
    embRdone = discord.Embed(title="Resigning process (Encrypted): Successful",
                            description=f"**{saveName}** resigned to **{playstation_id or user_id}**",
                            colour=0x854bf7)
    embRdone.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
    embRdone.set_footer(text="Made with expertise by HTOP")
    
    await ctx.edit(embed=embRdone)
    
    final_file_name = "PS4.zip"
    zipfiles(newDOWNLOAD_ENCRYPTED, final_file_name)
    final_file = os.path.join(newDOWNLOAD_ENCRYPTED, final_file_name)
    final_size = os.path.getsize(final_file)
    file_size_mb = final_size / (1024 * 1024)

    if file_size_mb < BOT_DISCORD_UPLOAD_LIMIT:
        await ctx.respond(file=discord.File(final_file))
    else:
        file_url = await GDapi.uploadzip(final_file, final_file_name)

        embg = discord.Embed(title="Google Drive: Upload complete",
                    description=f"Here is **{saveName}** resigned:\n<{file_url}>.",
                    colour=0x854bf7)
        embg.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
        embg.set_footer(text="Made with expertise by HTOP")
        await ctx.respond(embed=embg)

    # await asyncio.sleep(1)
    await cleanup(C1ftp, workspaceFolders, files, mountPaths)

@change_group.command(description="Change the titles of your save.")
async def title(ctx: discord.ApplicationContext, playstation_id: Option(str, description=PS_ID_DESC, default=""), maintitle: Option(str, description="For example Grand Theft Auto V.", default=""), subtitle: Option(str, description="For example Franklin and Lamar (1.6%).", default="")) -> None: # type: ignore
    if maintitle == "" and subtitle == "":
        await ctx.respond(embed=embTitleErr)
        return
    newUPLOAD_ENCRYPTED, newUPLOAD_DECRYPTED, newDOWNLOAD_ENCRYPTED, newPNG_PATH, newPARAM_PATH, newDOWNLOAD_DECRYPTED, newKEYSTONE_PATH = initWorkspace()
    workspaceFolders = [newUPLOAD_ENCRYPTED, newUPLOAD_DECRYPTED, newDOWNLOAD_ENCRYPTED, 
                        newPNG_PATH, newPARAM_PATH, newDOWNLOAD_DECRYPTED, newKEYSTONE_PATH]
    try: await makeWorkspace(ctx, workspaceFolders, ctx.channel_id)
    except WorkspaceError: return
    C1ftp = FTPps(IP, PORT, PS_UPLOADDIR, newDOWNLOAD_DECRYPTED, newUPLOAD_DECRYPTED, newUPLOAD_ENCRYPTED,
                  newDOWNLOAD_ENCRYPTED, newPARAM_PATH, newKEYSTONE_PATH, newPNG_PATH)
    mountPaths = []

    try: 
        user_id = await psusername(ctx, playstation_id)
        await asyncio.sleep(0.5)
        await ctx.edit(embed=embTitleChange)
        uploaded_file_paths = await upload2(ctx, newUPLOAD_ENCRYPTED, max_files=MAX_FILES, sys_files=False, ps_save_pair_upload=True)
    except HTTPError as e:
        await ctx.edit(embed=embhttp)
        cleanupSimple(workspaceFolders)
        logger.exception(f"{e} - {ctx.user.name} - (expected)")
        return
    except (TimeoutError, GDapiError) as e:
        await errorHandling(ctx, e, workspaceFolders, None, None, None)
        logger.exception(f"{e} - {ctx.user.name} - (expected)")
        return
    except Exception as e:
        await errorHandling(ctx, BASE_ERROR_MSG, workspaceFolders, None, None, None)
        logger.exception(f"{e} - {ctx.user.name} - (unexpected)")
        return
            
    savenames = obtain_savenames(newUPLOAD_ENCRYPTED)

    if len(uploaded_file_paths) >= 2:
        random_string = generate_random_string(RANDOMSTRING_LENGTH)
        uploaded_file_paths = enumerateFiles(uploaded_file_paths, random_string)
        for save in savenames:
            realSave = f"{save}_{random_string}"
            random_string_mount = generate_random_string(RANDOMSTRING_LENGTH)

            embTitleChange1 = discord.Embed(title="Change title: Processing",
                                description=f"Processing {save}.",
                                colour=0x854bf7)
            embTitleChange1.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
            embTitleChange1.set_footer(text="Made with expertise by HTOP")

            try:
                os.rename(os.path.join(newUPLOAD_ENCRYPTED, save), os.path.join(newUPLOAD_ENCRYPTED, realSave))
                os.rename(os.path.join(newUPLOAD_ENCRYPTED, save + ".bin"), os.path.join(newUPLOAD_ENCRYPTED, realSave + ".bin"))
                await ctx.edit(embed=embTitleChange1)
                await C1ftp.uploadencrypted_bulk(realSave)
                mount_location_new = MOUNT_LOCATION + "/" + random_string_mount
                await C1ftp.make1(mount_location_new)
                mountPaths.append(mount_location_new)
                await C1socket.socket_dump(mount_location_new, realSave)
                location_to_scesys = mount_location_new + "/sce_sys"
                await C1ftp.dlparamonly_grab(location_to_scesys)
                await handleTitles(newPARAM_PATH, user_id, maintitle, subtitle)
                await C1ftp.upload_sfo(newPARAM_PATH, location_to_scesys)
                await C1socket.socket_update(mount_location_new, realSave)
                await C1ftp.dlencrypted_bulk(False, user_id, realSave)

                embTitleSuccess = discord.Embed(title="Title altering process: Successful",
                            description=f"Altered the save titles of **{save}**.",
                            colour=0x854bf7)
                embTitleSuccess.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
                embTitleSuccess.set_footer(text="Made with expertise by HTOP")

                await ctx.edit(embed=embTitleSuccess)

            except (SocketError, FTPError, OrbisError, OSError) as e:
                if isinstance(e, OSError) and hasattr(e, "winerror") and e.winerror == 121: 
                    e = "PS4 not connected!"
                await errorHandling(ctx, e, workspaceFolders, uploaded_file_paths, mountPaths, C1ftp)
                logger.exception(f"{e} - {ctx.user.name} - (expected)")
                return
            except Exception as e:
                await errorHandling(ctx, BASE_ERROR_MSG, workspaceFolders, uploaded_file_paths, mountPaths, C1ftp)
                logger.exception(f"{e} - {ctx.user.name} - (unexpected)")
                return
        
        if len(savenames) == 1:
            finishedFiles = "".join(savenames)
        else: finishedFiles = ", ".join(savenames)

        embTdone = discord.Embed(title="Title altering process: Successful",
                            description=f"Altered the save titles of **{finishedFiles} and resigned to {playstation_id or user_id}**.",
                            colour=0x854bf7)
        embTdone.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
        embTdone.set_footer(text="Made with expertise by HTOP")

        await ctx.edit(embed=embTdone)
        
        final_file_name = "PS4.zip"
        zipfiles(newDOWNLOAD_ENCRYPTED, final_file_name)
        final_file = os.path.join(newDOWNLOAD_ENCRYPTED, final_file_name)
        final_size = os.path.getsize(final_file)
        file_size_mb = final_size / (1024 * 1024)

        if file_size_mb < BOT_DISCORD_UPLOAD_LIMIT:
            await ctx.respond(file=discord.File(final_file))
        else:
            file_url = await GDapi.uploadzip(final_file, final_file_name)

            embg = discord.Embed(title="Google Drive: Upload complete",
                    description=f"Here is **{finishedFiles}** with altered save titles:\n<{file_url}>",
                    colour=0x854bf7)
            embg.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
            embg.set_footer(text="Made with expertise by HTOP")
            await ctx.respond(embed=embg)

        await asyncio.sleep(1)
        await cleanup(C1ftp, workspaceFolders, uploaded_file_paths, mountPaths)

    else:
        await ctx.edit(embed=emb6)
        cleanupSimple(workspaceFolders)

@bot.slash_command(description="Convert a ps4 savefile to pc or vice versa on supported games that needs converting.")
async def convert(ctx: discord.ApplicationContext, game: Option(str, choices=["GTA V", "RDR 2", "BL 3", "TTWL"], description="Choose what game the savefile belongs to."), savefile: discord.Attachment) -> None: # type: ignore
    newUPLOAD_ENCRYPTED, newUPLOAD_DECRYPTED, newDOWNLOAD_ENCRYPTED, newPNG_PATH, newPARAM_PATH, newDOWNLOAD_DECRYPTED, newKEYSTONE_PATH = initWorkspace()
    workspaceFolders = [newUPLOAD_ENCRYPTED, newUPLOAD_DECRYPTED, newDOWNLOAD_ENCRYPTED, 
                        newPNG_PATH, newPARAM_PATH, newDOWNLOAD_DECRYPTED, newKEYSTONE_PATH]
    try: await makeWorkspace(ctx, workspaceFolders, ctx.channel_id)
    except WorkspaceError: return

    embConverting = discord.Embed(title="Converting",
                        description=f"Starting convertion process for {game}...",
                        colour=0x854bf7)
    embConverting.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
    embConverting.set_footer(text="Made with expertise by HTOP")

    await ctx.respond(embed=embConverting)

    if savefile.size / (1024 * 1024) > BOT_DISCORD_UPLOAD_LIMIT:
        e = "File size is too large!" # may change in the future when a game with larger savefile sizes are implemented
        await errorHandling(ctx, e, workspaceFolders, None, None, None)
        return

    savegame = os.path.join(newUPLOAD_DECRYPTED, savefile.filename)
    await savefile.save(savegame)

    try:
        match game:
            case "GTA V":
                result = await Converter.Rstar.convertFile_GTAV(savegame)
        
            case "RDR 2":
                result = await Converter.Rstar.convertFile_RDR2(savegame)

            case "BL 3":
                helper = TimeoutHelper(embTimedOut)
                result = await Converter.BL3.convertFile(ctx, helper, savegame, False)
            
            case "TTWL":
                helper = TimeoutHelper(embTimedOut)
                result = await Converter.BL3.convertFile(ctx, helper, savegame, True)
    
    except ConverterError as e:
        await errorHandling(ctx, e, workspaceFolders, None, None, None)
        logger.exception(f"{e} - {ctx.user.name} - (expected)")
        return
    except Exception as e:
        await errorHandling(ctx, BASE_ERROR_MSG, workspaceFolders, None, None, None)
        logger.exception(f"{e} - {ctx.user.name} - (unexpected)")
        return
    
    if result == "TIMED OUT":
        embCDone = discord.Embed(title="TIMED OUT!", colour=0x854bf7)
        embCDone.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
        embCDone.set_footer(text="Made with expertise by HTOP")
    elif result == "ERROR":
        embCDone = discord.Embed(title="ERROR!", description="Invalid save!", colour=0x854bf7)
        embCDone.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
        embCDone.set_footer(text="Made with expertise by HTOP")
    else:
        embCDone = discord.Embed(title="Success",
                            description=f"{result}\nPlease report any errors.",
                            colour=0x854bf7)
        embCDone.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
        embCDone.set_footer(text="Made with expertise by HTOP")

    await ctx.edit(embed=embCDone)
    await ctx.respond(file=discord.File(savegame))

    cleanupSimple(workspaceFolders)

@bot.slash_command(description="Add cheats to your save.")
async def cheats(ctx: discord.ApplicationContext, game: Option(str, choices=["GTA V", "RDR 2"]), savefile: discord.Attachment) -> None: # type: ignore
    newUPLOAD_ENCRYPTED, newUPLOAD_DECRYPTED, newDOWNLOAD_ENCRYPTED, newPNG_PATH, newPARAM_PATH, newDOWNLOAD_DECRYPTED, newKEYSTONE_PATH = initWorkspace()
    workspaceFolders = [newUPLOAD_ENCRYPTED, newUPLOAD_DECRYPTED, newDOWNLOAD_ENCRYPTED, 
                        newPNG_PATH, newPARAM_PATH, newDOWNLOAD_DECRYPTED, newKEYSTONE_PATH]
    try: await makeWorkspace(ctx, workspaceFolders, ctx.channel_id)
    except WorkspaceError: return

    embLoading = discord.Embed(title="Loading",
                        description=f"Loading cheats process for {game}...",
                        colour=0x854bf7)
    embLoading.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
    embLoading.set_footer(text="Made with expertise by HTOP")

    await ctx.respond(embed=embLoading)

    if savefile.size / (1024 * 1024) > BOT_DISCORD_UPLOAD_LIMIT:
        e = "File size is too large!" # may change in the future when a game with larger savefile sizes are implemented
        await errorHandling(ctx, e, workspaceFolders, None, None, None)
        return

    savegame = os.path.join(newUPLOAD_DECRYPTED, savefile.filename)
    await savefile.save(savegame)

    helper = TimeoutHelper(embTimedOut)

    try:
        match game:
            case "GTA V":
                platform = await Cheats.GTAV.initSavefile(savegame)
                stats = await Cheats.GTAV.fetchStats(savegame, platform)
                embLoaded = Cheats.GTAV.loaded_embed(stats)
                await ctx.edit(embed=embLoaded, view=Cheats.GTAV.CheatsButton(ctx, helper, savegame, platform))
            case "RDR 2":
                platform = await Cheats.RDR2.initSavefile(savegame)
                stats = await Cheats.RDR2.fetchStats(savegame, platform)
                embLoaded = Cheats.RDR2.loaded_embed(stats)
                await ctx.edit(embed=embLoaded, view=Cheats.RDR2.CheatsButton(ctx, helper, savegame, platform))
        await helper.await_done()
    
    except QuickCheatsError as e:
        await errorHandling(ctx, e, workspaceFolders, None, None, None)
        logger.exception(f"{e} - {ctx.user.name} - (expected)")
        return
    except Exception as e:
        await errorHandling(ctx, BASE_ERROR_MSG, workspaceFolders, None, None, None)
        logger.exception(f"{e} - {ctx.user.name} - (unexpected)")
        return
    
    await ctx.respond(file=discord.File(savegame))
    await asyncio.sleep(1)

    cleanupSimple(workspaceFolders)

@quick_group.command(description="Apply save wizard quick codes to your save.")
async def codes(ctx: discord.ApplicationContext, codes: str, endianness: Option(str, choices=["little", "big"], description="Little is default, if little does not work use this option and try big.", default="little")) -> None: # type: ignore
    newUPLOAD_ENCRYPTED, newUPLOAD_DECRYPTED, newDOWNLOAD_ENCRYPTED, newPNG_PATH, newPARAM_PATH, newDOWNLOAD_DECRYPTED, newKEYSTONE_PATH = initWorkspace()
    workspaceFolders = [newUPLOAD_ENCRYPTED, newUPLOAD_DECRYPTED, newDOWNLOAD_ENCRYPTED, 
                        newPNG_PATH, newPARAM_PATH, newDOWNLOAD_DECRYPTED, newKEYSTONE_PATH]
    try: await makeWorkspace(ctx, workspaceFolders, ctx.channel_id)
    except WorkspaceError: return

    await ctx.respond(embed=emb_upl_savegame)

    try:
        uploaded_file_paths = await upload2(ctx, newUPLOAD_DECRYPTED, max_files=MAX_FILES, sys_files=False, ps_save_pair_upload=False)
    except HTTPError as e:
        await ctx.edit(embed=embhttp)
        cleanupSimple(workspaceFolders)
        logger.exception(f"{e} - {ctx.user.name} - (expected)")
        return
    except (TimeoutError, GDapiError) as e:
        await errorHandling(ctx, e, workspaceFolders, None, None, None)
        logger.exception(f"{e} - {ctx.user.name} - (expected)")
        return
    except Exception as e:
        await errorHandling(ctx, BASE_ERROR_MSG, workspaceFolders, None, None, None)
        logger.exception(f"{e} - {ctx.user.name} - (unexpected)")
        return
    
    completed = []

    if len(uploaded_file_paths) >= 1:
        savefiles = os.listdir(newUPLOAD_DECRYPTED)

        for savefile in savefiles:
            savegame = os.path.join(newUPLOAD_DECRYPTED, savefile)
            
            embLoading = discord.Embed(title="Loading",
                                description=f"Loading {savefile}...",
                                colour=0x854bf7)
            embLoading.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
            embLoading.set_footer(text="Made with expertise by HTOP")

            embApplied = discord.Embed(title="Success!",
                                description=f"Quick codes applied to {savefile}.",
                                colour=0x854bf7)
            embApplied.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
            embApplied.set_footer(text="Made with expertise by HTOP")

            await ctx.edit(embed=embLoading)

            try:
                qc = QuickCodes(savegame, codes, endianness)
                await qc.apply_code()  
            except QuickCodesError as e:
                e += "\nThe code has to work on all the savefiles you uploaded!"
                await errorHandling(ctx, e, workspaceFolders, None, None, None)
                logger.exception(f"{e} - {ctx.user.name} - (expected)")
                return
            except Exception as e:
                await errorHandling(ctx, BASE_ERROR_MSG, workspaceFolders, None, None, None)
                logger.exception(f"{e} - {ctx.user.name} - (unexpected)")
                return
    
            await ctx.edit(embed=embApplied)
            completed.append(savefile)

    if len(completed) == 1:
        finishedFiles = "".join(completed)
    else: finishedFiles = ", ".join(completed)

    embCompleted = discord.Embed(title="Success!",
                                description=f"Quick codes applied to {finishedFiles}.",
                                colour=0x854bf7)
    embCompleted.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
    embCompleted.set_footer(text="Made with expertise by HTOP")
    await ctx.edit(embed=embCompleted)

    savezipName = "savegame_CodeApplied.zip"
    zipfiles(newUPLOAD_DECRYPTED, savezipName)
    final_file = os.path.join(newUPLOAD_DECRYPTED, savezipName)
    final_size = os.path.getsize(final_file)
    file_size_mb = final_size / (1024 * 1024)
    
    if file_size_mb < BOT_DISCORD_UPLOAD_LIMIT:
            await ctx.respond(file=discord.File(final_file))
    else:
        file_url = await GDapi.uploadzip(final_file, savezipName)
        embg = discord.Embed(title="Google Drive: Upload complete",
                    description=f"Here is **{finishedFiles}** with the applied quick code.:\n<{file_url}>.",
                    colour=0x854bf7)
        embg.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
        embg.set_footer(text="Made with expertise by HTOP")
        await ctx.respond(embed=embg)
    await asyncio.sleep(1)

    cleanupSimple(workspaceFolders)

@bot.slash_command(description="Checks if the bot is functional.")
async def ping(ctx: discord.ApplicationContext) -> None:
    await ctx.defer()
    result = 0
    latency = bot.latency * 1000
    C1ftp = FTPps(IP, PORT, None, None, None, None, None, None, None, None)
    try:
        await C1ftp.testConnection()
        result += 1
    except OSError as e:
        logger.exception(f"PING: FTP could not connect: {e}")

    try:
        await C1socket.testConnection()
        result += 1
    except (OSError) as e:
        logger.exception(f"PING: SOCKET could not connect: {e}")

    if result == 2:
        func = discord.Embed(title=f"Connections: 2/2\nLatency: {latency: .2f}ms", color=0x22EA0D)

        func.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
        await ctx.respond(embed=func)
    else: 
        notfunc = discord.Embed(title=f"Connections: {result}/2\nLatency: {latency: .2f}ms", colour=0xF42B00)

        notfunc.set_thumbnail(url="https://cdn.discordapp.com/avatars/248104046924267531/743790a3f380feaf0b41dd8544255085.png?size=1024")
        await ctx.respond(embed=notfunc)

@bot.command()
@commands.is_owner()
async def init(ctx: discord.ApplicationContext) -> None:
    try: 
        await ctx.channel.purge(limit=1)
    except discord.Forbidden as e:
        logger.error(f"Can not purge message sent: {e}")

    await ctx.send(embed=embinit, view=threadButton())

bot.add_application_command(change_group)
bot.add_application_command(quick_group)
bot.run(str(os.getenv("TOKEN")))