import os, asyncio
from discord.ext import commands
import setting


bot = commands.Bot(command_prefix=setting.COMMAND_PREFIX, intents=setting.INTENTS)

#Tải cog.
async def load_cogs():
  for file in os.listdir("./cogs"):
    if file.endswith(".py"):
      await bot.load_extension(f"cogs.{file[:-3]}")

#Chạy bot.
async def run():
  await load_cogs()
  await bot.start(os.getenv("TOKEN"))
  #Nếu bạn biết cài biến môi trường thì giữ nguyên.
  #Còn nếu không thì xóa "os.getenv("TOKEN")" thay vào token của bot.

asyncio.run(run())