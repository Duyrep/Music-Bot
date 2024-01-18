import discord

#-----Cài đặt bot-----

#Tiền tố lệnh bot.
COMMAND_PREFIX = "!"
#Quyền của bot.
INTENTS = discord.Intents.all()
#Màu của tin nhắn
EMBED_MESSAGE_COLOUR = discord.Colour.gold()
#Trợ giúp
HELP_MESSAGE_CONTENT = """/help để trợ giúp.
/join để tham gia kênh thoại.
/play để chơi nhạc.
/stop để dừng nhạc.
/pause để tạm dừng nhạc.
/resume để tiếp tục nhạc"""