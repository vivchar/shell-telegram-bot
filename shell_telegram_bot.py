#!/usr/bin/env python
# pylint: disable=unused-argument
import asyncio
import enviroment

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


def is_command_safe(command: str) -> bool:
    command = command.strip()
    for safe_command in enviroment.WHITE_LIST_COMMANDS:
        if command.startswith(safe_command):
            return True

    return False


async def can_execute(update: Update, command: str) -> bool:
    if not update.effective_user.id == enviroment.MY_USER_ID:
        await update.message.reply_text("You don't have a access to this bot!")
        return False

    if not is_command_safe(command):
        await update.message.reply_text("It is not safe command, sorry ;(")
        return False

    return True


async def execute_shell_command(command: str) -> str:
    process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, text=False)
    stdout, stderr = await process.communicate()
    return (stderr.decode('utf-8') + stdout.decode('utf-8'))[:4000]  # message limit


async def process_command(command: str, update: Update):
    if not await can_execute(update, command):
        return

    output = await execute_shell_command(command)
    await update.message.reply_text("```shell\n" + output + "```", parse_mode='MarkdownV2')


async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(rf"Your USER_ID is <b>{update.effective_user.id}</b>")


async def docker_ps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await process_command("docker ps", update)


async def docker_rm_blum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await process_command("docker rm blum", update)


async def docker_stop_blum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await process_command("docker stop blum", update)


async def docker_run_blum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = "docker run --name blum -d -v $(pwd)/clients.json:/BlumBot/clients.json --pull=always ghcr.io/anisovaleksey/blumbot:latest"
    await process_command(command, update)


async def handle_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await process_command(update.message.text, update)


def main() -> None:
    application = Application.builder().token(enviroment.BOT_TOKEN).build()

    application.add_handler(CommandHandler("me", me))
    application.add_handler(CommandHandler("dockerps", docker_ps))
    application.add_handler(CommandHandler("dockerrmblum", docker_rm_blum))
    application.add_handler(CommandHandler("dockerstopblum", docker_stop_blum))
    application.add_handler(CommandHandler("dockerrunblum", docker_run_blum))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_commands))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

# me - Get my info
# dockerps - List containers
# dockerstopblum - Stop Blum container
# dockerrmblum - Remove Blum container
# dockerrunblum - Pull and run Blum container
