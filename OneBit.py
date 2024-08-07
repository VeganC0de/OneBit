import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import requests
from io import BytesIO
from discord import File
import yt_dlp as youtube_dl
import streamlit as st
import qrcode

load_dotenv()

token = os.getenv('token')
randomVerso = "https://bible-api.com/?random=verse"
FnShop = "https://fortnite-api.com/v2/shop/br/combined"
dolarShop = "https://dolarapi.com/v1/dolares/tarjeta"

intents = discord.Intents.all()
intents.messages = True
intents.members = True

bot = commands.Bot(command_prefix= '!',intents = intents)

#Contestar con info

@bot.command()
async def info(ctx):
    await ctx.send("Que pasa Pa, soy un bot desarrollado por TESLA")

#Contestar a un hola

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if 'hola' in message.content.lower():
        await message.channel.send(f"Hola {message.author.name}! :P")

    await bot.process_commands(message)

#Traer el mapa de fortnite

@bot.command()
async def mapa(ctx):
     response = requests.get("https://fortnite-api.com/v1/map")
     data = response.json()
     map = data['data']['images']['blank']
     await ctx.send(map)

#Obtener la tienda de fortnite

@bot.command()
async def fshop(ctx):
    response = requests.get(FnShop)

    # Verificar que la solicitud fue exitosa
    if response.status_code == 200:
        data = response.json()

        if 'data' in data and 'featured' in data['data']:
            new_skins = data['data']['featured']['entries']
            
            # Iterar sobre cada skin y enviar un embed separado para cada imagen
            for skin in new_skins:
                try:
                    skin_name = skin['items'][0]['name']
                    image_url = skin['items'][0]['images']['icon']

                    embed = discord.Embed(title=skin_name, color=discord.Color.blue())
                    embed.set_image(url=image_url)
                    await ctx.send(embed=embed)
                except KeyError as e:
                    print(f"Error al procesar skin: {e}")
        else:
            await ctx.send("No se encontraron skins nuevas.")
    else:
        await ctx.send(f"Error al obtener los datos: {response.status_code}")

@bot.command()
async def play(ctx, url: str):
    # Asegúrate de que el usuario esté en un canal de voz
    if ctx.author.voice is None:
        await ctx.send("¡Necesitas estar en un canal de voz para usar este comando!")
        return

    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)

    # Configurar opciones para youtube_dl
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']

    # Crear un stream y reproducir el audio
    voice_client = ctx.voice_client
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    voice_client.stop()
    voice_client.play(discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS))

    await ctx.send(f"Reproduciendo: {info['title']}")

# Comando para parar la música
@bot.command()
async def stop(ctx):
    if ctx.voice_client is not None:
        ctx.voice_client.stop()
        await ctx.send("Música detenida.")
    else:
        await ctx.send("No estoy reproduciendo música.")


@bot.command()
async def versiculo(ctx):
        response = requests.get(randomVerso)
        data = response.json()
        verso = data['text']
        await ctx.send(verso)

@bot.command()
async def dolar(ctx):
    response = requests.get(dolarShop)
    # Verificar que la solicitud fue exitosa
    if response.status_code == 200:
        data = response.json()
        dl = data['venta']
        await ctx.send(f"El dolar tarjeta está {dl}")
    else:
        await ctx.send("No pude encontrar el precio bro")

@bot.command()
async def preciod(ctx,dolar):
    response = requests.get(dolarShop)
    # Verificar que la solicitud fue exitosa
    if response.status_code == 200:
        data = response.json()
        
        # Asegúrate de que 'venta' sea un número y conviértelo si es necesario
        dl = float(data.get('venta', 0))
        
        # Verifica que dl sea un número válido antes de usarlo
        if isinstance(dl, (int, float)):
            resultado = dl * float(dolar)
            await ctx.send(f"Comprar esa cantidad de Dólares te va a costar: {resultado} ARS")
        else:
            await ctx.send("No pude obtener el precio de venta correctamente")
    else:
        await ctx.send("No pude calcular el precio bro")

@bot.command()
async def qr(ctx,url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Generar la imagen del código QR
    img = qr.make_image(fill_color="black", back_color="white")

    # Convertir la imagen a bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    # Enviar la imagen como archivo adjunto en Discord
    await ctx.send(file=File(img_bytes, filename='codigo_qr.png'))



bot.run(token)