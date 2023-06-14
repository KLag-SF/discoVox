import logging
import os
from queue import Queue
import sys
from threading import Thread
import time

import discord
from discord import app_commands, Interaction, Message

from src.db.Models.Server import Server
from src.db.Database import Engine, Session
from src.Voicevox import Vvox_req

try:
    from src import discordSettings
except ModuleNotFoundError:
    print("File discordSetings.py missing.\nTerminated.", file=sys.stderr)
    sys.exit()


try:
    TOKEN = discordSettings.TOKEN
except ModuleNotFoundError:
    print("File discordSetings.py missing.\nTerminated.", file=sys.stderr)
    sys.exit()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# logging.basicConfig(filename="/var/log/discovox.log", level=logging.DEBUG)
# log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)
# log.debug("DiscoVox has successfully initialized.")

query_que = Queue()
synthe_que = Queue()
play_que = Queue()

v_clients = {}

@client.event
async def on_ready():
    await tree.sync()

@client.event
async def on_message(msg: Message):
    if msg.author.bot:
        return
    
    # log.debug(msg)
    svr = Session().query(Server)\
                   .filter(Server.server_ID == msg.guild.id)\
                   .first()
    if svr is None:
        return
    text_ch = svr.channel

    # print(f"{type(msg.channel.id)}, {type(text_ch)}")
    # print(f"{msg.channel.id}\n{text_ch} -> {msg.channel==text_ch}")

    if str(msg.channel.id) == text_ch:
        v = Vvox_req(msg.author.id, msg.guild.id, msg.created_at, msg.content)
        query_que.put(v)
        # print(f"{msg.content} pushed.")

@tree.command(name="voice", description="ボイスチャンネルに参加します。")
async def join_voice_channel(interaction: Interaction):
    if interaction.user.voice is None:
        await interaction.response.send_message("先にボイスチャンネルへ接続してください！")
        return
    
    svr = Session.query(Server)\
        .filter(Server.server_ID == interaction.guild_id)\
        .first()

    if svr is None:
        new_svr = Server()
        new_svr.server_ID = interaction.guild_id
        new_svr.channel = interaction.channel_id
        Session.add(new_svr)
        Session.commit()

    elif client.get_channel(svr.channel) is None:
        new_svr = Session.query(Server)\
                         .filter(Server.server_ID==interaction.guild_id)\
                         .first()
        new_svr.channel = interaction.channel_id
        Session.add(new_svr)
        Session.commit()
    
    await interaction.user.voice.channel.connect()
    ch_name = interaction.user.voice.channel.name
    await interaction.response.send_message(f"チャンネル「{ch_name}」に接続しました！")

def audio_query():
    while True:
        v: Vvox_req = query_que.get()
        v.audio_query()
        synthe_que.put(v)
        query_que.task_done()
        # print("query consumed")

t_query = Thread(target=audio_query, name="query")
t_query.daemon = True
t_query.start()

def synthesis():
    while True:
        v: Vvox_req = synthe_que.get()
        v.synthesis()
        play_que.put(v)
        synthe_que.task_done()
        # print("synthesis consumed")

t_synthe = Thread(target=synthesis, name="sysnthesis")
t_synthe.daemon = True
t_synthe.start()

def play():
    v = play_que.get()
    vc: discord.VoiceClient = client.get_guild(v.server_id).voice_client
    audio = discord.FFmpegPCMAudio(v.tmp_file_name, executable="./ffmpeg")
    vc.play(audio, after=lambda e: [os.remove(v.tmp_file_name),
                                    play()])

t_play = Thread(target=play, name="play")
t_play.daemon = True
t_play.start()

client.run(TOKEN)