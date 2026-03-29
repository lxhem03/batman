from io import BytesIO
from pyrogram import filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from bot import bot, LOGGER
from ..helper.ext_utils.bot_utils import cmd_exec, new_task
from ..helper.telegram_helper.message_utils import send_message, send_file
from ..helper.telegram_helper.filters import CustomFilters
from ..helper.telegram_helper.bot_commands import BotCommands

@new_task
async def leave_group(client, message: Message):
    if len(message.command) < 2:
        return await send_message(message, "<b>Usage:</b> <code>/left -100xxxxxxxxxx</code>")
    
    chat_id = message.command[1]
    
    try:
        target_id = int(chat_id)
        await client.leave_chat(target_id)
        await send_message(message, f"<b>Success:</b> Left the group <code>{target_id}</code>")
    except ValueError:
        await send_message(message, "<b>Error:</b> Please provide a valid numerical Chat ID.")
    except Exception as e:
        await send_message(message, f"<b>Error:</b> {str(e)}")

@new_task
async def run_shell(_, message):
    cmd = message.text.split(maxsplit=1)
    if len(cmd) == 1:
        await send_message(message, "No command to execute was given.")
        return
    cmd = cmd[1]
    stdout, stderr, _ = await cmd_exec(cmd, shell=True)
    reply = ""
    if len(stdout) != 0:
        reply += f"<b>Stdout</b>\n<code>{stdout}</code>\n"
        LOGGER.info(f"Shell - {cmd} - {stdout}")
    if len(stderr) != 0:
        reply += f"<b>Stderr</b>\n<code>{stderr}</code>"
        LOGGER.error(f"Shell - {cmd} - {stderr}")
    
    if len(reply) > 3000:
        with BytesIO(str.encode(reply)) as out_file:
            out_file.name = "shell_output.txt"
            await send_file(message, out_file)
    elif len(reply) != 0:
        await send_message(message, reply)
    else:
        await send_message(message, "No Reply")

# THIS PART REGISTERS BOTH COMMANDS
bot.add_handler(MessageHandler(run_shell, filters.command(BotCommands.ShellCommand) & CustomFilters.owner))
bot.add_handler(MessageHandler(leave_group, filters.command("left") & CustomFilters.owner))
