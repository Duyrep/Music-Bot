from discord.ext import commands
from discord import app_commands
import discord, os, setting


class Bot(commands.Cog):
  
  def __init__(self, bot: commands.Bot):
    super().__init__()
    self.bot = bot
  
  @commands.Cog.listener()
  async def on_ready(self):
    await self.bot.tree.sync()
    print(f"File {os.path.basename(__file__)} is runing")
  
  @app_commands.command(name="ping", description="Xem tốc độ kết nối của bot.")
  async def ping(self, interaction: discord.Interaction):
    await interaction.response.send_message(
      embed=discord.Embed(
        title=f"Tốc độ kết nói của bot là: {self.bot.latency * 1000:.1f}ms.",
        colour=discord.Colour.gold()
      ),
      delete_after=5
    )
  
  @app_commands.command(name="help", description="Xem hổ trợ của bot.")
  async def help(self, interaction: discord.Interaction):
    interaction.response.send_message(embed=discord.Embed(title=setting.HELP_MESSAGE_CONTENT, colour=setting.EMBED_MESSAGE_COLOUR))

async def setup(bot: commands.Bot):
  await bot.add_cog(Bot(bot))