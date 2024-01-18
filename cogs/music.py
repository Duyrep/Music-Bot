from discord.ext import commands
from discord import app_commands
from yt_dlp import YoutubeDL
import discord, os, asyncio, datetime, setting


class Music(commands.Cog):
  
  def __init__(self, bot: commands.Bot):
    super().__init__()
    self.bot = bot
    self.FFMPEG_OPTIONS = {
      'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
      'options': '-vn'
    }
    self.YDL_OPTIONS = {
      'quiet': True,
      'format': 'bestaudio/best',
      'outtmpl': 'downloads/%(title)s.%(ext)s',
      'postprocessors': [
        {
          'key': 'FFmpegExtractAudio',
          'preferredcodec': 'mp3',
          'preferredquality': '192',
        }
      ],
      'extract_info': True
    }
    self.ytdl = YoutubeDL(self.YDL_OPTIONS)
    self.voice = None

  #Lấy kênh thoại bot đang vào
  def get_voice_client(self, interaction: discord.Interaction) -> discord.VoiceClient:
    voice: discord.VoiceClient = None
    for vc in interaction.client.voice_clients:
      if vc.guild == interaction.guild:
        voice = vc
        break
    return voice
  
  #Kiểm tra url
  def is_url(self, url: str):
    if url.startswith("https://youtu.be/"):
      return True
    return False

  #Kiểu url
  def url_type(self, url: str):
    if url.startswith("https://youtu.be/"):
      return "Youtube"
    return ""
  
  #Tạo embed
  def create_embed(self, data: dict, url: str) -> discord.Embed:
    embed = discord.Embed(
      title=data.get('title', None),
      url=url,
      colour=discord.Colour.gold(), 
      description=self.url_type(url)
    )
    embed.add_field(name="Lược xem", value=data.get('view_count', None))
    embed.add_field(name="Thời gian video", value=f"{str(datetime.timedelta(seconds=data.get('duration', None)))}", inline=True)
    embed.set_author(
      name=data.get('uploader', None),
      url=data.get('uploader_url', None),
      icon_url=data.get('channel_thumbnail', None)
    )
    embed.set_image(url=data.get('thumbnail', None))
    return embed
  
  async def send_embed_message(self, interaction: discord.Interaction, content: str):
    await interaction.response.send_message(embed=discord.Embed(colour=setting.EMBED_MESSAGE_COLOUR, title=content))

  #Chơi nhạc
  async def play_music(self, channel: discord.TextChannel, vc: discord.VoiceClient, url: str):
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(url, download=False))
    await channel.send(embed=self.create_embed(data, url))
    song = data.get('url', None)
    vc.stop()
    vc.play(discord.FFmpegPCMAudio(song, executable="ffmpeg.exe", **self.FFMPEG_OPTIONS))
    
  @commands.Cog.listener()
  async def on_ready(self):
    await self.bot.tree.sync()
    print(f"File {os.path.basename(__file__)} is runing")
  
  #Tham gia kênh thoại
  @app_commands.command(name="join", description="Tham gia kênh thoại hiện tại bạn đã tham gia.")
  async def join(self, interaction: discord.Interaction):
    user_voice = interaction.user.voice
    if user_voice:
      bot_voice: discord.VoiceClient = interaction.guild.voice_client
      if bot_voice:
        if bot_voice.channel.id == user_voice.channel.id:
          await self.send_embed_message(interaction, f"Bot hiện tại đang ở trong kênh thoại của bạn.")
        else:
          await bot_voice.move_to(user_voice.channel)
          await self.send_embed_message(interaction, f"Bot đã tham gia kênh thoại {user_voice.channel.name}.")
      else:
        self.voice = await user_voice.channel.connect()
        await self.send_embed_message(interaction, f"Bot đã tham gia kênh thoại {user_voice.channel.name}.")
    else:
      await self.send_embed_message(interaction, "Bạn phải tham gia 1 kênh thoại thì bot mới có thể vào.")
  
  #Thoát kênh thoại
  @app_commands.command(name="leave", description="Rời khỏi kênh thoại hiện tại của bot.")
  async def leave(self, interaction: discord.Interaction):
    voice = self.get_voice_client(interaction)
    if voice is None:
      await self.send_embed_message(interaction, "Bot không ở trong kênh thoại nào cả.")
    else:
      self.get_voice_client(interaction).stop()
      await interaction.guild.voice_client.disconnect()
      await self.send_embed_message(interaction, f"Bot đã rời kênh thoại {voice.channel.name}.")
  
  #Chơi nhạc
  @app_commands.command(name="play", description="Chơi nhạc.")
  async def play(self, interaction: discord.Interaction, url: str):
    voice = self.get_voice_client(interaction)
    user_voice = interaction.user.voice
    if voice is None:
      self.voice = await user_voice.channel.connect()
      await self.send_embed_message(interaction, f"Bot đã tham gia kênh thoại {interaction.user.voice.channel.name}.")
      await self.play_music(interaction.channel, self.get_voice_client(interaction), url)
    elif not self.is_url(url):
      await self.send_embed_message(interaction, "Url không hợp lệ.")
    else:
      voice.stop()
      bot_voice: discord.VoiceClient = interaction.guild.voice_client
      if bot_voice and bot_voice.channel.id != user_voice.channel.id:
        await bot_voice.move_to(user_voice.channel)
        await self.send_embed_message(interaction, f"Bot đã tham gia kênh thoại {interaction.user.voice.channel.name}.")
      await self.play_music(interaction.channel, voice, url)
  
  #Dừng nhạc
  @app_commands.command(name="stop", description="Dừng phát nhạc.")
  async def stop(self, interaction: discord.Interaction):
    voice = self.get_voice_client(interaction)
    if voice == None:
      await self.send_embed_message(interaction, "Không thể dừng nhạc vì bot không ở trong kênh thoại nào.")
    else:
      voice.stop()
      await self.send_embed_message(interaction, "Nhạc đã dừng phát.")
  
  #Tạm dừng nhạc
  @app_commands.command(name="pause", description="Tạm dừng phát nhạc.")
  async def pause(self, interaction: discord.Interaction):
    voice = self.get_voice_client(interaction)
    if voice == None:
      await self.send_embed_message(interaction, "Không thể tạm dừng nhạc vì bot không ở trong kênh thoại nào.")
    else:
      voice.pause()
      await self.send_embed_message(interaction, "Nhạc đã tạm dừng phát.")
  
  #Tiếp tục phát nhạc
  @app_commands.command(name="resume", description="Tiếp tục phát nhạc.")
  async def resume(self, interaction: discord.Interaction):
    voice = self.get_voice_client(interaction)
    if voice == None:
      await self.send_embed_message(interaction, "Không thể tiếp tục nhạc vì bot không ở trong kênh thoại nào.")
    else:
      voice.resume()
      await self.send_embed_message(interaction, "Nhạc đã tiếp tục phát.")
  
  #Thay đổ âm lượng
  @app_commands.command(name="volume", description="Thay đổi âm lượng.")
  async def volume(self, interaction: discord.Interaction, volume: int):
    voice = self.get_voice_client(interaction)
    if voice == None:
      await self.send_embed_message(interaction, "Không thể thay đổi âm lượng nhạc vì bot không ở trong kênh thoại nào.")
    elif volume > 100:
      await self.send_embed_message(interaction, "Không thể đặt âm lượng quá 100%.")
    else:
      try:
        self.voice.source = discord.PCMVolumeTransformer(self.voice.source, volume=volume / 100)
      except Exception as e:
        error = str(e)
        if "'Music' object has no attribute 'voice'" in error:
          await self.send_embed_message(interaction, f"Không có âm lượng âm thanh để điều chỉnh.")
          return
      await self.send_embed_message(interaction, f"Đã thay đổi âm lương thành {volume}% ({volume}/100%)")

async def setup(bot: commands.Bot):
  await bot.add_cog(Music(bot))