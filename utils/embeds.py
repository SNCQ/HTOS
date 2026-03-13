import discord
from enum import Enum
from utils.constants import VERSION, OTHER_TIMEOUT, BLACKLIST_MESSAGE

class Color(Enum):
    DEFAULT = 0x854BF7
    GREEN = 0x22EA0D
    RED = 0xF42B00
    YELLOW = 0xD2D624

class Embed_t(Enum):
    DEFAULT_FOOTER = f"Hosted By SNCQ"
    QR_FOOTER1 = "Respond with the number of your desired game, or type 'EXIT' to quit.\nاكتب رقم اللعبه الي بغيتها, او اكتب 'EXIT' للخروج."
    QR_FOOTER2 = "Respond with the number of your desired save, or type 'BACK' to go to the game menu.\nاكتب رقم التخزينة الي بغيتها, او اكتب 'BACK' للرجوع الى قائمة الألعاب."

embUtimeout = discord.Embed(
    title="Upload alert: Error <a:tickred:1142861498260148224>\nإشعار لإرسال الملف: حدث خطأ <a:tickred:1142861498260148224>",
    description="- Time's up! You didn't attach any files.\n- انتهى الوقت! و لم تقم بإرسال الملفات.",
    colour=Color.DEFAULT.value
)
embUtimeout.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embgdt = discord.Embed(
    title="Google drive upload: Error <a:tickred:1142861498260148224>\nرابط جوجل درايف: حدث خطأ <a:tickred:1142861498260148224>",
    description="You did not respond with the link in time!\nلم تقم بإرسال الرابط في الوقت المناسب!",
    colour=Color.DEFAULT.value
)
embgdt.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embhttp = discord.Embed(
    title="HttpError",
    description="Are you sure that you uploaded binary content?",
    colour=Color.DEFAULT.value
)
embhttp.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embEncrypted1 = discord.Embed(
    title="Resigning process: Encrypted\nعميلة التحويل: تخزينة مشفرة",
    description="- Please attach at least two encrypted savefiles that you want to upload (.bin and non bin). Or type 'EXIT' to cancel command.\n"
    f"- الرجاء ارسال على الأقل ملفين للتخزينة من نوع (.bin و بدون bin). او اكتب 'EXIT' للخروج",
    colour=Color.DEFAULT.value
)
embEncrypted1.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embDecrypt1 = discord.Embed(
    title="Decrypt Process\nعملية فك التشفير",
    description="- Please attach at least two encrypted savefiles that you want to upload (.bin and non bin). Or type 'EXIT' to cancel command.\n"
    f"- الرجاء ارسال على الأقل ملفين للتخزينة من نوع (.bin و بدون bin). او اكتب 'EXIT' للخروج",
    colour=Color.DEFAULT.value
)
embDecrypt1.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

emb14 = discord.Embed(
    title="Resigning process: Decrypted\nعملية التحويل: فك التشفير",
    description="- Please attach at least two encrypted savefiles that you want to upload (.bin and non bin). Or type 'EXIT' to cancel command.\n"
    f"- الرجاء ارسال على الأقل ملفين للتخزينة من نوع (.bin و بدون bin). او اكتب 'EXIT' للخروج",
    colour=Color.DEFAULT.value
)
emb14.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

emb20 = discord.Embed(
    title="Re-region process: Upload encrypted files from the FOREIGN region\nعملية تغيير الريجون: ارسل ملفات التخزينة للريجون المختلف",
    description="- Please attach at least two encrypted savefiles that you want to upload (.bin and non bin). Or type 'EXIT' to cancel command.\n"
    f"- الرجاء ارسال على الأقل ملفين للتخزينة من نوع (.bin و بدون bin). او اكتب 'EXIT' للخروج",
    colour=Color.DEFAULT.value
)
emb20.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

emb21 = discord.Embed(
    title="Re-region process: Upload encrypted files from YOUR region\nعملية تغيير الريجون: ارسل ملفات التخزينة للريجون حقك",
    description="- Please attach two encrypted savefiles that you want to upload (.bin and non bin). Or type 'EXIT' to cancel command.\n"
    f"- الرجاء ارسال ملفين للتخزينة من نوع (.bin و بدون bin). او اكتب 'EXIT' للخروج",
    colour=Color.DEFAULT.value
)
emb21.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embpng = discord.Embed(
    title="PNG Process",
    description="Please attach at least two encrypted savefiles that you want to upload (.bin and non bin). Or type 'EXIT' to cancel command.",
    colour=Color.DEFAULT.value
)
embpng.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

emb8 = discord.Embed(
    title="Error: PSN username <a:tickred:1142861498260148224>\nخطأ: اسم حساب بلايستيشن <a:tickred:1142861498260148224>",
    description=f"- {{msg}}. You have {OTHER_TIMEOUT} seconds to reply with your account ID instead.\nOr type 'EXIT' to cancel command.\n"
    f"- اسم حساب البلايستشن الذي ادخلته غير صحيح, لديك  {OTHER_TIMEOUT} ثانية للرد برقم حسابك بدال الأسم.\n  - او اكتب 'EXIT' لإلغاء العمليه.",
    colour=Color.YELLOW.value
)
emb8.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embnt = discord.Embed(
    title="Error: Time limit reached <a:tickred:1142861498260148224>\nخطأ: انتهى الوقت <a:tickred:1142861498260148224>",
    description="- You did not send your account ID in time.\n"
    f"- لم تقم بإرسال رقم حسابك في الوقت المناسب.",
    colour=Color.DEFAULT.value
)
embnt.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embvalidpsn = discord.Embed(
    title="Obtained: PSN username <a:tick_mark:1142861488206381056>\nتم الحصول على: اسم مستخدم بلايستيتشن <a:tick_mark:1142861488206381056>",
    description="- Your input was a valid PSN username.\n"
    f"- اسم حسابك صحيح.",
    colour=Color.DEFAULT.value
)
embvalidpsn.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embinit = discord.Embed(
    title="Save Wizard Bot | بوت سيف وزرد",
    description="- Click **`Create thread`** button to get started!\n  - You can also use old threads that you have created with the bot.\n"
    f"- إضغط على زر **`Create thread`** للبدء!\n  - تستطيع ايضا استخدام الرسائل القديمة مع البوت.",
    colour=discord.Color.from_rgb(0, 255, 255)
)
embinit.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embTitleChange = discord.Embed(
    title="Change title: Upload",
    description="Please attach at least two encrypted savefiles that you want to upload (.bin and non bin). Or type 'EXIT' to cancel command.",
    colour=Color.DEFAULT.value
)
embTitleChange.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embTitleErr = discord.Embed(
    title="Change title: Error",
    description="Please select a maintitle or subtitle.",
    colour=Color.DEFAULT.value
)
embTitleErr.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embTimedOut = discord.Embed(
    title="Timed out!",
    description="Sending file.",
    colour=Color.DEFAULT.value
)
embTimedOut.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embDone_G = discord.Embed(
    title="Success",
    description=f"Please report any errors.",
    colour=Color.DEFAULT.value
)
embDone_G.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

emb_upl_savegame = discord.Embed(
    title="Upload files",
    description=f"Please attach at least 1 savefile, it must be fully decrypted. Or type 'EXIT' to cancel command.",
    colour=Color.DEFAULT.value
)
emb_upl_savegame.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

loadSFO_emb = discord.Embed(
    title="Initializing",
    description="Loading param.sfo...",
    color=Color.DEFAULT.value
)
loadSFO_emb.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

finished_emb = discord.Embed(title="Finished", color=Color.DEFAULT.value)
finished_emb.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

loadkeyset_emb = discord.Embed(
    title="Initializing",
    description="Obtaining keyset...",
    color=Color.DEFAULT.value
)
loadkeyset_emb.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

working_emb = discord.Embed(
    title="Working...",
    color=Color.DEFAULT.value
)
working_emb.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

retry_emb = discord.Embed(
    title="Please try again.\nيرجى المحاولة مرة أخرى.",
    color=Color.DEFAULT.value
)
retry_emb.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

blacklist_emb = discord.Embed(
    title=BLACKLIST_MESSAGE,
    color=Color.RED.value
)
blacklist_emb.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embChannelError = discord.Embed(
    title="Error | خطأ",
    description=
    "- Invalid channel!\n  - Please go to this channel https://discord.com/channels/901212631103328316/1324776984999624807.\n"
    "- قناة خاطئة!\n  - يرجى الذهاب إلى هذه القناة https://discord.com/channels/901212631103328316/1324776984999624807.",
    colour=Color.DEFAULT.value
)
embChannelError.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

cancel_notify_emb = discord.Embed(
    title="Notice",
    description="You can 'EXIT' if you want to cancel while the files are uploading.",
    color=Color.DEFAULT.value
)
cancel_notify_emb.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

gd_upl_progress_emb = discord.Embed(
    title="Google Drive Upload",
    color=Color.DEFAULT.value
)
gd_upl_progress_emb.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

gd_maintenance_emb = discord.Embed(
    title="Google Drive maintenance",
    description="Please try again later.",
    colour=Color.YELLOW.value
)
gd_maintenance_emb.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embpng1 = discord.Embed(
    title="PNG process: Initializng",
    description="Your save (**{savename}**) is being mounted, (save {j}/{savecount}, batch {i}/{batches}), please wait...\nSend 'EXIT' to cancel.",
    colour=Color.DEFAULT.value
)
embpng1.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embpng2 = discord.Embed(
    title="PNG process: Initializng",
    description="Your save (**{savename}**) has mounted, (save {j}/{savecount}, batch {i}/{batches}), please wait...\nSend 'EXIT' to cancel.",
    colour=Color.DEFAULT.value
)
embpng2.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embpngs = discord.Embed(
    title="PNG process: Successful",
    description="Altered the save png and resigned **{savename}** (save {j}/{savecount}, batch {i}/{batches}).",
    colour=Color.DEFAULT.value
)
embpngs.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embPdone = discord.Embed(
    title="PNG process: Successful",
    description=(
        "Altered the save png of **{printed}** and resigned to **{id}** (batch {i}/{batches}).\n"
        "Uploading file...\n"
        "If file is being uploaded to Google Drive, you can send 'EXIT' to cancel."
    ),
    colour=Color.DEFAULT.value
)
embPdone.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embTitleChange1 = discord.Embed(
    title="Title altering process: Initializng",
    description="Processing {savename} (save {j}/{savecount}, batch {i}/{batches}), please wait...\nSend 'EXIT' to attempt cancelling.",
    colour=Color.DEFAULT.value
)
embTitleChange1.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embTitleSuccess = discord.Embed(
    title="Title altering process: Successful",
    description="Altered the save titles of **{savename}** (save {j}/{savecount}, batch {i}/{batches}).",
    colour=Color.DEFAULT.value
)
embTitleSuccess.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embTdone = discord.Embed(
    title="Title altering process: Successful",
    description=(
        "Altered the save titles of **{printed}**, and resigned to **{id}** (batch {i}/{batches}).\n"
        "Uploading file...\n"
        "If file is being uploaded to Google Drive, you can send 'EXIT' to cancel."
    ),
    colour=Color.DEFAULT.value
)
embTdone.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

emb_conv_upl = discord.Embed(
    title="Conversion process: {game}",
    description="Please attach atleast 1 savefile. Or type 'EXIT' to cancel command.",
    colour=Color.DEFAULT.value
    )
emb_conv_upl.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

emb_conv_choice = discord.Embed(
    title="Converter: Choice ({basename})",
    description="Could not recognize the platform of the save, please choose what platform to convert the save to (file {j}/{count_entry}, batch {i}/{batches}).",
    colour=Color.DEFAULT.value
)
emb_conv_choice.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embCDone1 = discord.Embed(
    title="Timed Out!\nانتهى الوقت!",
    colour=Color.DEFAULT.value
)
embCDone1.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embCDone2 = discord.Embed(
    title="ERROR!",
    description="Invalid save!",
    colour=Color.RED.value
)
embCDone2.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embCDone3 = discord.Embed(
    title="Success",
    description="{result}\n**{basename}** (file {j}/{count_entry}, batch {i}/{batches}).",
    colour=Color.DEFAULT.value
)
embCDone3.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embconvCompleted = discord.Embed(
    title="Success!",
    description=(
        "Converted **{finished_files}** (batch {i}/{batches}).\n"
        "Uploading file...\n"
        "If file is being uploaded to Google Drive, you can send 'EXIT' to cancel."
    ),
    colour=Color.DEFAULT.value
)
embconvCompleted.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embSceSys = discord.Embed(
    title="Upload: sce_sys contents\n{savename}",
    description="Please attach the sce_sys files you want to upload. Or type 'EXIT' to cancel command.",
    colour=Color.DEFAULT.value
)
embSceSys.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embgs = discord.Embed(
    title="Upload: Gamesaves\n{savename}",
    description=(
        "Please attach the gamesave files you want to upload.\n"
        "**FOLLOW THESE INSTRUCTIONS CAREFULLY**\n\n"
        "For **discord uploads** rename the files according to the path they are going to have inside the savefile using the value '{splitvalue}'. For example the file 'savedata' inside the data directory would be called 'data{splitvalue}savedata'.\n\n"
        "For **google drive uploads** just create the directories on the drive and send the folder link from root, it will be recursively downloaded.\n\n"
        "*Or type 'EXIT' to cancel command.*"
    ),
    colour=Color.DEFAULT.value
)
embgs.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embsl = discord.Embed(
    title="Gamesaves: Second layer\n{displaysave}",
    description="Checking for supported second layer encryption/compression...",
    colour=Color.DEFAULT.value
)
embsl.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embc = discord.Embed(
    title="Processing",
    description="Creating {savename}...",
    colour=Color.DEFAULT.value
)
embc.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embCRdone = discord.Embed(
    title="Creation process: Successful",
    description=(
        "**{savename}** created & resigned to **{id}**.\n"
        "Uploading file...\n"
        "If file is being uploaded to Google Drive, you can send 'EXIT' to cancel."
    ),
    colour=Color.DEFAULT.value
)
embCRdone.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

emb11 = discord.Embed(
    title="Decryption process: Initializing",
    description="Mounting {savename} (save {j}/{savecount}, batch {i}/{batches}), please wait...\nSend 'EXIT' to cancel.",
    colour=Color.DEFAULT.value
)
emb11.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

emb_dl = discord.Embed(
    title="Decryption process: Downloading",
    description="{savename} mounted (save {j}/{savecount}, batch {i}/{batches}), downloading decrypted savefile...\nSend 'EXIT' to cancel.",
    colour=Color.DEFAULT.value
)
emb_dl.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

emb13 = discord.Embed(
    title="Decryption process: Successful",
    description="Downloaded the decrypted save of **{savename}** (save {j}/{savecount}, batch {i}/{batches}).",
    colour=Color.DEFAULT.value
)
emb13.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embDdone = discord.Embed(
    title="Decryption process: Successful",
    description=(
        "**{printed}** has been decrypted (batch {i}/{batches}).\n"
        "Uploading file...\n"
        "Send 'EXIT' to cancel."
    ),
    colour=Color.DEFAULT.value
)
embDdone.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embmo = discord.Embed(
    title="Encryption process: Initializing",
    description="Mounting **{savename}**, (save {j}/{savecount}, batch {i}/{batches}), please wait...\nSend 'EXIT' to cancel.",
    colour=Color.DEFAULT.value
)
embmo.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embmidComplete = discord.Embed(
    title="Encryption Processs: Successful",
    description="Encrypted **{dec_print}** into **{savename}** for **{id}** (save {j}/{savecount}, batch {i}/{batches}).",
    colour=Color.DEFAULT.value
)
embmidComplete.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embencComplete = discord.Embed(
    title="Encryption process: Successful",
    description=(
        "Encrypted files into **{printed}** for **{id}** (batch {i}/{batches}).\n"
        "Uploading file...\n"
        "If file is being uploaded to Google Drive, you can send 'EXIT' to cancel."
    ),
    colour=Color.DEFAULT.value
)
embencComplete.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embmenCompletef = discord.Embed(
    title="Encryption Processs: Successful",
    description="Encrypted **{dec_print}** into **{savename}** for **{id}**.",
    colour=Color.DEFAULT.value
)
embmenCompletef.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

keyset_emb = discord.Embed(
    title="Success",
    description="Keyset: {keyset}\nFW: {fw}",
    color=Color.DEFAULT.value
)
keyset_emb.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embpingsuccess = discord.Embed(
    title=(
        "📂 FTP: **{ftp_result}**\n"
        "🌐 CECIE: **{socket_result}**\n"
        "🟢 Active instances: **{instances_len}**/**{maximum_instances}**\n"
        "⏱️ Latency: **{latency: .2f}** ms"
    ),
    colour=Color.GREEN.value)
embpingsuccess.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embpingfail = discord.Embed(
    title=(
        "📂 FTP: **{ftp_result}**\n"
        "🌐 CECIE: **{socket_result}**\n"
        "🟢 Active instances: **{instances_len}**/**{maximum_instances}**\n"
        "⏱️ Latency: **{latency: .2f}** ms"
    ),
    colour=Color.RED.value)
embpingfail.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embExit = discord.Embed(title="Exited.", colour=Color.DEFAULT.value)
embExit.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embresb = discord.Embed(
    title="Resigning process: Encrypted\nعميلة التحويل: تخزينة مشفرة",
    description=(
        "- Your save (**{savename}**) is being resigned ({i}/{savecount}), please wait... ⏰\n  - Send 'EXIT' to cancel.\n"
        "- تخزينتك (**{savename}**) يتم تحويلها (**{i}/{savecount}**), الرجاء الإنتظار... ⏰\n  - اكتب 'EXIT' لإلغاء العمليه."
    ),
    colour=Color.DEFAULT.value
)
embresb.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embresbs = discord.Embed(
    title="Resigning process (Encrypted): Successful <a:tick_mark:1142861488206381056>\nعملية تحويل التخزينة : ناجحة <a:tick_mark:1142861488206381056>",
    description=(
        "- **{savename}** resigned to **{id}**.\n"
        "- **{id}** تم تحويلها الى **{savename}**."
    ),
    colour=Color.DEFAULT.value
)
embresbs.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embRdone = discord.Embed(
    title="Resigning process (Encrypted): Successful <a:tick_mark:1142861488206381056>\nعملية تحويل التخزينة : ناجحة <a:tick_mark:1142861488206381056>",
    description=(
        "- **{printed}** resigned to **{id}**.\n"
        "  - Uploading file...\n"
        "  - If file is being uploaded to Google Drive, you can send 'EXIT' to cancel.\n"
        "- **{id}** تم تحويلها الى **{printed}**.\n"
        "  - يتم رفع الملفات...\n"
        "  - اذا الملف يتم رفعه على جوجل درايف, تقدر تكتب 'EXIT' لإلغاء العمليه."
    ),
    colour=Color.DEFAULT.value
)
embRdone.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embresbsf = discord.Embed(
    title="Resigning process (Encrypted): Successful <a:tick_mark:1142861488206381056>\nعملية تحويل التخزينة : ناجحة <a:tick_mark:1142861488206381056>",
    description=(
        "- **`{printed}`** resigned to **`{id}`**.\n"
        "- **`{id}`** تم تحويلها الى **`{printed}`**."
    ),
    colour=Color.DEFAULT.value
)
embresbsf.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embLoading = discord.Embed(
    title="Loading",
    description="Loading **{basename}**... (file {j}/{count_entry}, batch {i}/{batches}).",
    colour=Color.DEFAULT.value
)
embLoading.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embApplied = discord.Embed(
    title="Success!",
    description="Quick codes applied to **{basename}** (file {j}/{count_entry}, batch {i}/{batches}).",
    colour=Color.DEFAULT.value
)
embApplied.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embqcCompleted = discord.Embed(
    title="Success!",
    description=(
        "Quick codes applied to **{finished_files}** ({i}/{batches}).\n"
        "Uploading file...\n"
        "If file is being uploaded to Google Drive, you can send 'EXIT' to cancel."
    ),
    colour=Color.DEFAULT.value
)
embqcCompleted.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embchLoading = discord.Embed(
    title="Loading",
    description="Loading cheats process for **{game}**...",
    colour=Color.DEFAULT.value
)
embchLoading.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embkstone1 = discord.Embed(
    title="Obtain process: Keystone",
    description="Obtaining keystone from file: **{savename}**, please wait...\nSend 'EXIT' to cancel.",
    colour=Color.DEFAULT.value
)
embkstone1.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embkstone2 = discord.Embed(
    title="Obtain process: Keystone",
    description="Keystone from **{target_titleid}** obtained.",
    colour=Color.DEFAULT.value
)
embkstone2.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embrrp = discord.Embed(
    title="Re-regioning process: Encrypted\nعملية تغيير الريجون: تخزينة مشفرة",
    description=(
        "- Your save (**{savename}**) is being re-regioned & resigned, (save {j}/{savecount}, batch {i}/{batches}), please wait...\n  - Send 'EXIT' to cancel.\n"
        "- تخزينتك (**{savename}**) يتم الاّن تحويلها و تغيير الريجون, (تخزينة {j}/{savecount}, من {i}/{batches}), يرجى الإنتظار...\n  - أكتب 'EXIT' لإلغاء العمليه."
    ),
)
embrrp.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embrrps = discord.Embed(
    title="Re-regioning (Encrypted): Successful <a:tick_mark:1142861488206381056>\nعملية تغيير الريجون: ناجحة <a:tick_mark:1142861488206381056>",
    description=(
        "- **{savename}** re-regioned & resigned to **{id}** (**{target_titleid}**), (save {j}/{savecount}, batch {i}/{batches}).\n"
        "- **{id}** تم تحويلها و تغيير الرجون الى **{savename}** (**{target_titleid}**), (تخزينة {j}/{savecount}, من {i}/{batches})."
    ),
    colour=Color.DEFAULT.value
)
embrrps.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embrrdone = discord.Embed(
    title="Re-region: Successful <a:tick_mark:1142861488206381056>\n عملية تغيير الريجون: ناجحة <a:tick_mark:1142861488206381056>",
    description=(
        "- **{printed}** re-regioned & resigned to **{id}** (**{target_titleid}**), (batch {i}/{batches}).\n"
        "  - Uploading file...\n"
        "  - If file is being uploaded to Google Drive, you can send 'EXIT' to cancel.\n"
        "- **{id}** تم تحويلها و تغيير الريجون الى **{printed}** (**{target_titleid}**), ({i}/{batches}).\n"
        "  - يتم رفع الملفات...\n"
        "  - اذا الملف يتم رفعه على جوجل درايف, تقدر تكتب 'EXIT' لإلغاء العملية." 
    ),
    colour=Color.DEFAULT.value
)
embrrdone.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embrrpsf = discord.Embed(
    title="Re-regioning (Encrypted): Successful <a:tick_mark:1142861488206381056>\nعملية تغيير الريجون: ناجحة <a:tick_mark:1142861488206381056>",
    description=(
        "- **`{printed}`** re-regioned & resigned to **`{id}`** - (**`{target_titleid}`**).\n"
        "- (**`{target_titleid}`**) - **`{id}`** تم تحويلها و تغيير الرجون الى **`{printed}`**"
    ),
    colour=Color.DEFAULT.value
)
embrrpsf.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embres = discord.Embed(
    title="Resigning process: Encrypted Save\nعميلة التحويل:  تخزينة مشفرة",
    description=(
        "- Your save (**{savename}**) is being resigned, (save {j}/{savecount}, batch {i}/{batches}), please wait... ⏰\n  - Send 'EXIT' to cancel.\n"
        "- تخزينتك (**{savename}**) يتم تحويلها (**{j}/{savecount}**, من **{i}/{batches}**), الرجاء الإنتظار... ⏰\n  - أكتب 'EXIT' لإلغاء العمليه."
    ),
    colour=Color.DEFAULT.value
)
embres.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embress = discord.Embed(
    title="Resigning process (Encrypted): Successful <a:tick_mark:1142861488206381056>\nعملية تحويل التخزينة : ناجحة <a:tick_mark:1142861488206381056>",
    description=(
        "- **{savename}** resigned to **{id}**.\n"
        "- **{id}** تم تحويلها الى **{savename}**."
    ),
    colour=Color.DEFAULT.value
)
embress.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embRbdone = discord.Embed(
    title="Resigning process (Encrypted): Successful <a:tick_mark:1142861488206381056>\nعملية تحويل التخزينة : ناجحة <a:tick_mark:1142861488206381056>",
    description=(
        "- **{printed}** resigned to **{id}** (batch {i}/{batches}).\n"
        "  - Uploading file...\n"
        "  - If file is being uploaded to Google Drive, you can send 'EXIT' to cancel.\n"
        "- .({i}/{batches}) **{id}** تم تحويلها الى **{printed}**\n"
        "  - يتم رفع الملفات...\n"
        "  - اذا الملف يتم رفعه على جوجل درايف, تقدر تكتب 'EXIT' لإلغاء العملية."
    ),
    colour=Color.DEFAULT.value)
embRbdone.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embressf = discord.Embed(
    title="Resigning process: Successful <a:tick_mark:1142861488206381056>\nعملية تحويل التخزينة : ناجحة <a:tick_mark:1142861488206381056>",
    description=(
        "- **`{printed}`** resigned to **`{id}`**.\n"
        "- **`{id}`** تم تحويلها الى **`{printed}`**."
    ),
    colour=0x00ffcc
)
embressf.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embLoad = discord.Embed(
    title="Loading",
    description="Loading {filename}...",
    colour=Color.DEFAULT.value
)
embLoad.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embdec = discord.Embed(
    title="Finished",
    description="Successfully decrypted {filename}.",
    colour=Color.DEFAULT.value
)
embdec.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

paramEmb = discord.Embed(
    colour=Color.DEFAULT.value
)
paramEmb.set_footer(
    text=Embed_t.DEFAULT_FOOTER.value
)

embchErr = discord.Embed(
    title="ERROR!",
    description="Could not add cheat: {error}.",
    colour=Color.RED.value
)
embchErr.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embErrconv = discord.Embed(
    title="ERROR!",
    description="Could not convert: {error}.",
    colour=Color.RED.value
)
embErrconv.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embErrdec = discord.Embed(
    title="ERROR!",
    description="Could not convert: {error}.",
    colour=Color.RED.value
)
embErrdec.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embchgtav = discord.Embed(
    title="Save loaded: GTA V",
    description=(
        "Platform: **{platform}**\n"
        "Franklin money: **{franklin_cash: ,}**\n"
        "Michael money: **{michael_cash: ,}**\n"
        "Trevor money: **{trevor_cash: ,}**"
    ),
    colour=Color.DEFAULT.value
)
embchgtav.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embchrdr2 = discord.Embed(
    title="Save loaded: RDR 2",
    description=(
        "Platform: **{platform}**\n"
        "Money: **{money}**"
    ),
    colour=Color.DEFAULT.value
)
embchrdr2.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embfn = discord.Embed(
    title="Upload alert: Error",
    description="Sorry, the file name of '{filename}' ({len}) exceeds {max}.",
    colour=Color.DEFAULT.value
)
embfn.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embFileLarge = discord.Embed(
    title="Upload alert: Error",
    description="Sorry, the file size of '{filename}' exceeds the limit of {max} MB.",
    colour=Color.DEFAULT.value
)
embFileLarge.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embnvSys = discord.Embed(
    title="Upload alert: Error",
    description="{filename} is not a valid sce_sys file!",
    colour=Color.DEFAULT.value
)
embnvSys.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embpn = discord.Embed(
    title="Upload alert: Error",
    description="Sorry, the path '{filename}' ({len}) will create exceed ({max}).",
    colour=Color.DEFAULT.value
)
embpn.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embnvBin = discord.Embed(
    title="Upload alert: Error",
    description="Sorry, the file size of '{filename}' is not {size} bytes.",
    colour=Color.DEFAULT.value
)
embnvBin.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embffn = discord.Embed(
    title="Upload alert: Error",
    description="Sorry, the amount of files/folders in {path} exceeds {max}.",
    colour=Color.DEFAULT.value
)
embffn.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embgddone = discord.Embed(
    title="Google drive upload: Retrieved file",
    description="{filename} has been uploaded and saved ({i}/{filecount}).",
    colour=Color.DEFAULT.value
)
embgddone.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embuplSuccess = discord.Embed(
    title="Upload alert: Successful",
    description="File '{filename}' has been successfully uploaded and saved ({i}/{filecount}).",
    colour=Color.DEFAULT.value
)
embuplSuccess.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embe = discord.Embed(
    title="Error | خطأ",
    description="{error}",
    colour=Color.RED.value
)
embe.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embuplSuccess1 = discord.Embed(
    title="Upload alert: Successful",
    description="File '{filename}' has been successfully uploaded and saved.",
    colour=Color.DEFAULT.value
)
embuplSuccess1.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embencupl = discord.Embed(
    title="Current save: {savename}",
    description="Please attach a decrypted savefile that you want to upload, MUST be equivalent to {filename} (can be any name). Or type 'EXIT' to cancel command.",
    colour=Color.DEFAULT.value
)
embencupl.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embenc_out = discord.Embed(
    title="Current save: {savename}",
    colour=Color.DEFAULT.value
)
embenc_out.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embencinst = discord.Embed(
    title="Current save: {savename}",
    description=(
        "**FOLLOW THESE INSTRUCTIONS CAREFULLY**\n\n"
        "FOR **DISCORD ATTACHMENT UPLOAD**:\n"
        "Please attach at least one of these files and make sure its the same name, including path in the name if that is the case. Instead of '/' use '{splitvalue}'.\n"
        "\nFOR **GOOGLE DRIVE LINK UPLOAD**:\n"
        "UPLOAD WITH ANY FOLDER STRUCTURE!\n\n"
        "*Or type 'EXIT' to cancel command*."
        "\n\nHere are the contents:"),
    colour=Color.DEFAULT.value
)
embencinst.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embgdout = discord.Embed(
    title="Google Drive: Upload complete",
    description="[Download | تحميل]({url})\n{extra_msg}",
    colour=Color.DEFAULT.value
)
embgdout.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embgames = discord.Embed(
    title="All available games\nكل الألعاب المتوفرة",
    colour=Color.DEFAULT.value
)
embgames.set_footer(text=Embed_t.QR_FOOTER1.value)

embgame = discord.Embed(
    colour=Color.DEFAULT.value
)
embgame.set_footer(text=Embed_t.QR_FOOTER2.value)

emb_il = discord.Embed(
    title="Too many users at the moment!",
    description="{error}",
    colour=Color.YELLOW.value
)
emb_il.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embdecTimeout = discord.Embed(
        title="Timeout Error:",
        description="You took too long, sending the file with the format: 'Encrypted'",
        colour=Color.DEFAULT.value)
embdecTimeout.set_footer(text=Embed_t.DEFAULT_FOOTER.value)

embdecFormat = discord.Embed(
    title="Current save: {savename}",
    description="Choose if you want second layer removed ('Decrypted') or just Sony PFS layer ('Encrypted').",
    colour=Color.DEFAULT.value)
embdecFormat.set_footer(text="If you want to use the file in a save editor, choose 'Decrypted'!")

embwlcom = discord.Embed(
    title="Welcome **`{user}`** <a:pikachu:1475180008178979060>\nاهلاً و سهلاً يا **`{user}`** <a:pikachu:1475180008178979060>",
    description=(
                f"📌 **How to use the bot:**\n"
                f"- Type **`/`** and select a command to begin.\n\n"
                f"❓ **Need help?**\n"
                f"- Type **`/help`** or ask in <#1171086371029532745>.\n\n"
                f"📌 **طريقة استخدام البوت:**\n"
                f"- اكتب **`/`** واختر الأمر الذي تريده.\n\n"
                f"❓ **تحتاج مساعده ؟**\n"
                f"- اكتب **`/help`** او اسأل في <#1171086371029532745>.\n\n\n"
                f"### <a:warning1:1479422977685590189> **Important:**\n"
                f"- Please do not use more than one PlayStation account or your access will be permanently revoked.\n"
                f"- **Only** <@&1169543372717953024> **are allowed to use many PlayStation accounts.**\n\n"
                f"### <a:warning1:1479422977685590189> **مهم:**\n"
                f"- يرجى عدم استخدام أكثر من حساب بلايستيشن واحد وإلا سيتم سحب صلاحيتك بشكل دائم.\n"
                f"- **فقط** <@&1169543372717953024> **مسموح لهم استخدام اكثر من حساب بلايستيشن.**"
                ),
    colour=0x00ffcc
)
embwlcom.set_footer(text=Embed_t.DEFAULT_FOOTER.value)
