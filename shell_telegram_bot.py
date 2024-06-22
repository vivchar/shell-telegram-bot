#!/usr/bin/env python
# pylint: disable=unused-argument
import asyncio
import enviroment
import subprocess

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
    # loop = asyncio.get_running_loop()
    # result = await loop.run_in_executor(None, exec2, command)
    # print("result " + result)
    # return result
    p = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, text=False)
    stdout, stderr = await p.communicate()
    return (stderr.decode('utf-8') + stdout.decode('utf-8'))[:4000]  # message limit


def exec_test(command: str) -> str:
    try:
        # p = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        # out, err = p.communicate(command)
        # return out
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd="..")
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stdout


async def process(command: str, update: Update):
    if not await can_execute(update, command):
        return

    output = await execute_shell_command(command)
    await update.message.reply_text("```shell\n~ >>> " + command + "\n\n" + output + "```", parse_mode='MarkdownV2')


async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(rf"Your USER_ID is <b>{update.effective_user.id}</b>")


async def hamster_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await process(
        "docker stop hamster",
        update
    )
    await process(
        "docker rm hamster",
        update
    )
    await process(
        "docker rmi hamster",
        update
    )
    await process(
        "git -C HamsterKombatBot/ pull",
        update
    )
    await process(
        "docker build -t hamster HamsterKombatBot/",
        update
    )
    await process(
        "docker run --name hamster -d hamster",
        update
    )


async def blum_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await process(
        "docker stop blum",
        update
    )
    await process(
        "docker rm blum",
        update
    )
    await process(
        "docker run --name blum -d -v $(pwd)/clients.json:/BlumBot/clients.json --pull=always ghcr.io/anisovaleksey/blumbot:latest",
        update
    )


async def handle_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await process(update.message.text, update)


def main() -> None:
    application = Application.builder().token(enviroment.BOT_TOKEN).build()

    application.add_handler(CommandHandler("me", me))
    application.add_handler(CommandHandler("blumrestart", blum_restart))
    application.add_handler(CommandHandler("hamsterrestart", hamster_restart))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_commands))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.run_until_complete(main())
    # loop.close()

# me - Get my info
# dockerps - List containers
# dockerstopblum - Stop Blum container
# dockerrmblum - Remove Blum container
# dockerrunblum - Pull and run Blum container
