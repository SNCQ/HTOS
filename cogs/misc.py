import asyncio
import discord
from discord.ext import commands
from network.socket_functions import C1socket
from network.ftp_functions import FTPps
from network.exceptions import SocketError
from utils.constants import (
    IP, PORT_FTP, CON_FAIL, CON_FAIL_MSG, COMMAND_COOLDOWN, MISC_TIMEOUT,
    logger, bot,
    BASE_ERROR_MSG
)
from utils.embeds import (
    embinit, loadkeyset_emb, Embed_t, Color,
    keyset_emb, embpingsuccess, embpingfail
)
from utils.helpers import ThreadButton, error_handling
from utils.workspace import fetchall_threadid_db, delall_threadid_db, make_workspace
from utils.orbis import keyset_to_fw
from utils.instance_lock import INSTANCE_LOCK_global
from utils.exceptions import WorkspaceError

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)  # Buttons expire after 60 seconds

    @discord.ui.button(label="English", style=discord.ButtonStyle.primary)
    async def english_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed_en = discord.Embed(
            title="Save Wizard Bot - Tutorial",
            description="Welcome to the Save Wizard Bot! This bot is designed to assist you in modifying and managing your PS4 save games.",
            color=Color.DEFAULT.value
        )

        embed_en.add_field(name="Core Commands:",
                           value="🔄 `/resign` - Resign your PS4 save file to a new PlayStation account.\n"
                                 "🌍 `/reregion` - Change the region of a save to match your game version.\n"
                                 "🔓 `/decrypt` - Decrypt your save file for editing.\n"
                                 "🔐 `/encrypt` - Re-encrypt your save file after making changes.\n",
                                 #"🖼 `/change picture` - Customize the icon/picture associated with your save.\n"
                                 #"✏️ `/change title` - Modify the title of your save file.",
                           inline=False)

        embed_en.add_field(name="Advanced Commands:",
                           value="📜 `/quick codes` - Apply quick save modifications.\n"
                                 "⚡ `/quick cheats` - Add pre-made cheat codes.\n"
                                 "🔍 `/quick resign` - Quickly resign pre-stored save files.\n"
                                 "🔑 `/sealed_key decrypt` - Decrypt sealed keys.\n"
                                 "🔄 `/convert` - Convert PS4 save files to other platforms.\n"
                                 "📂 `/sfo read` - Extract information from `param.sfo`.\n"
                                 "✏️ `/sfo write` - Edit `param.sfo` parameters.",
                           inline=False)

        embed_en.add_field(name="Important Notes:",
                           value="• Ensure your saves are properly backed up before modifications.\n"
                                 "• Resigning and re-encryption are required for saves to work on new accounts.",
                           inline=False)

        embed_en.add_field(name="Need Help?",
                           value="If you encounter any issues, open a ticket or type in the chat.\n",
                           inline=False)

        embed_en.set_footer(text=Embed_t.DEFAULT_FOOTER.value)
        await interaction.response.edit_message(embed=embed_en, view=None)  # Removes buttons

    @discord.ui.button(label="العربية", style=discord.ButtonStyle.primary)
    async def arabic_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed_ar = discord.Embed(
            title="بوت سيف وزرد - شرح",
            description="مرحبًا بك في بوت سيف وزرد على PS4! يساعدك هذا البوت في تعديل وإدارة التخزينات الخاصة بك.",
            color=Color.DEFAULT.value
        )

        embed_ar.add_field(name="الأوامر الأساسية:",
                           value="🔄 `/resign` - تحويل ملف التخزينة إلى حساب بلايستيشن جديد.\n"
                                 "🌍 `/reregion` - تغيير الريجون لملف التخزينة.\n"
                                 "🔓 `/decrypt` - فك تشفير ملف التخزينة للتعديل.\n"
                                 "🔐 `/encrypt` - إعادة تشفير ملف التخزينة بعد التعديلات.\n",
                                 #"🖼 `/change picture` - تخصيص صورة ملف الحفظ.\n"
                                 #"✏️ `/change title` - تعديل عنوان ملف الحفظ."
                           inline=False)

        embed_ar.add_field(name="الأوامر المتقدمة:",
                           value="⚡ `/quick cheats` - إضافة أكواد الغش الجاهزة.\n"
                                 "📜 `/quick codes` - تطبيق تعديلات الحفظ السريعة.\n"
                                 "🔍 `/quick resign` - تحويل التخزينات الجاهزه المخزنة مسبقًا.\n"
                                 "🔑 `/sealed_key decrypt` - فك تشفير المفاتيح المغلقة.\n"
                                 "🔄 `/convert` - تحويل تخزينة لعبة بلايستيشن 4 الى منصات اخرى.\n"
                                 "📂 `/sfo read` - استخراج معلومات من `param.sfo`.\n"
                                 "✏️ `/sfo write` - تعديل إعدادات `param.sfo`.",
                           inline=False)

        embed_ar.add_field(name="ملاحظات هامة:",
                           value="• تأكد من عمل نسخة احتياطية للتخزينة قبل التعديل.\n"
                                 "• لازم تحول التخزينة كل مره عشان تشتغل على الحسابات الجديدة.",
                           inline=False)

        embed_ar.add_field(name="تحتاج مساعدة؟",
                           value="إذا واجهت اي مشكلة، افتح تذكرة او اكتب في الشات.\n",
                           inline=False)

        embed_ar.set_footer(text=Embed_t.DEFAULT_FOOTER.value)
        await interaction.response.edit_message(embed=embed_ar, view=None)  # Removes buttons
    
class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    @discord.slash_command(description="Display bot commands and information.")
    async def help(self, ctx: discord.ApplicationContext) -> None:
        embed = discord.Embed(
            title="Choose a Language | اختر لغة",
            description="Please select your language to display the instructure using the buttons below.\nيرجى اختيار اللغة لظهور التعليمات باستخدام الأزرار أدناه.",
            color=Color.DEFAULT.value
        )

        view = HelpView()
        await ctx.respond(embed=embed, view=view, ephemeral=False)
    info_group = discord.SlashCommandGroup("info")

    @info_group.command(description="Display the maximum firmware/keyset the hoster's console can mount/unmount a save from.")
    @commands.cooldown(1, COMMAND_COOLDOWN, commands.BucketType.user)
    async def keyset(self, ctx: discord.ApplicationContext) -> None:
        workspace_folders = []
        try: await make_workspace(ctx, workspace_folders, ctx.channel_id, skip_gd_check=True)
        except (WorkspaceError, discord.HTTPException): return

        try:
            await ctx.respond(embed=loadkeyset_emb)
        except discord.HTTPException as e:
            logger.info(f"Error while responding to msg: {e}", exc_info=True)
            await INSTANCE_LOCK_global.release(ctx.author.id)
            return

        try:
            async with asyncio.timeout(MISC_TIMEOUT):
                keyset = await C1socket.socket_keyset()
            fw = keyset_to_fw(keyset)

            emb = keyset_emb.copy()
            emb.description = emb.description.format(keyset=keyset, fw=fw)
            await ctx.edit(embed=emb)
        except TimeoutError:
            await error_handling(ctx, "Timed out!", workspace_folders, None, None, None)
            logger.info(f"Timed out!")
        except (SocketError, OSError) as e:
            status = "expected"
            if isinstance(e, OSError) and e.errno in CON_FAIL:
                e = CON_FAIL_MSG
            elif isinstance(e, OSError):
                e = BASE_ERROR_MSG
                status = "unexpected"
            await error_handling(ctx, e, workspace_folders, None, None, None)
            if status == "expected":
                logger.info(f"{e} - {ctx.user.name} - ({status})", exc_info=True)
            else:
                logger.exception(f"{e} - {ctx.user.name} - ({status})")
        except Exception as e:
            await error_handling(ctx, BASE_ERROR_MSG, workspace_folders, None, None, None)
            logger.exception(f"{e} - {ctx.user.name} - (unexpected)")
        finally:
            await INSTANCE_LOCK_global.release(ctx.author.id)

    @discord.slash_command(description="Checks if the bot is functional.")
    @commands.cooldown(1, COMMAND_COOLDOWN, commands.BucketType.user)
    async def ping(self, ctx: discord.ApplicationContext) -> None:
        try:
            await ctx.defer()
        except discord.HTTPException as e:
            logger.info(f"Error while deferring: {e}", exc_info=True)
            return

        latency = self.bot.latency * 1000
        result = 0

        C1ftp = FTPps(IP, PORT_FTP, "", "", "", "", "", "", "", "")

        ftp_result = socket_result = "Unavailable"

        try:
            await C1ftp.test_connection()
            result += 1
            ftp_result = "Available"
        except OSError as e:
            logger.exception(f"PING: FTP could not connect: {e}")

        try:
            await C1socket.test_connection()
            result += 1
            socket_result = "Available"
        except OSError as e:
            logger.exception(f"PING: SOCKET (Cecie) could not connect: {e}")

        if result == 2:
            emb = embpingsuccess.copy()
        else:
            emb = embpingfail.copy()
        emb.title = emb.title.format(
            ftp_result=ftp_result,
            socket_result=socket_result,
            instances_len=INSTANCE_LOCK_global.instances_len,
            maximum_instances=INSTANCE_LOCK_global.maximum_instances,
            latency=latency
        )

        try:
            await ctx.respond(embed=emb)
        except discord.HTTPException as e:
            logger.info(f"Error while responding to msg: {e}", exc_info=True)
            return

    @discord.slash_command(description="Send the panel to create threads.")
    @commands.is_owner()
    async def init(self, ctx: discord.ApplicationContext) -> None:
        await ctx.respond("Sending panel...", ephemeral=True)
        await ctx.send(embed=embinit, view=ThreadButton())

    @discord.slash_command(description="Remove all threads created by the bot.")
    @commands.is_owner()
    async def clear_threads(self, ctx: discord.ApplicationContext) -> None:
        await ctx.respond("Clearing threads...", ephemeral=True)
        try:
            db_dict = await fetchall_threadid_db()
            await delall_threadid_db(db_dict)

            for _, thread_id in db_dict.items():
                thread = bot.get_channel(thread_id)
                if thread is not None:
                    await thread.delete()
        except (discord.Forbidden, WorkspaceError) as e:
            logger.error(f"Error clearing all threads: {e}")

        await ctx.respond(f"Cleared {len(db_dict)} thread(s)!", ephemeral=True)

def setup(bot: commands.Bot) -> None:
    bot.add_cog(Misc(bot))
