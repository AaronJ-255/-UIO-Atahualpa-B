import discord
from discord.ext import commands
import os
import random

TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# --- Configuración del sistema de verificación ---
VERIFICATION_CHANNEL_ID = 1339503726825701387     # Reemplaza con el ID del canal de verificación
ADMIN_VERIFICATION_CHANNEL_ID = 1339513315923197983  # Reemplaza con el ID del canal de administración de verificaciones
APPROVED_ROLE_ID =   1339503507027529760    # Reemplaza con el ID del rol que se dará al aprobar
REMOVED_ROLE_ID = 1339503572424986645     # Reemplaza con el ID del rol que se removerá al aprobar
ADMIN_ROLE_IDS = [112233445566778899, 1339503496034254860]  # Reemplaza con los IDs de los roles de administrador

pending_verifications = {}

@bot.event
async def on_ready():
    print(f'¡Bot conectado como {bot.user.name}!')

# --- Comandos básicos ---
@bot.command()
async def hola(ctx):
    await ctx.send(f'¡Hola, {ctx.author.mention}!')

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! Latencia: {round(bot.latency * 1000)}ms')

@bot.command(name='dado', aliases=['tirar'])
async def roll_dice(ctx, caras: int = 6):
    if caras <= 1:
        await ctx.send("El número de caras debe ser mayor que 1.")
        return
    resultado = random.randint(1, caras)
    await ctx.send(f'{ctx.author.mention} tiró un dado de {caras} caras y obtuvo: **{resultado}**')

@bot.command(name='info', aliases=['usuario'])
async def user_info(ctx, miembro: discord.Member = None):
    if miembro is None:
        miembro = ctx.author
    await ctx.send(f"**Nombre de usuario:** {miembro.name}")
    await ctx.send(f"**ID:** {miembro.id}")
    await ctx.send(f"**Se unió al servidor el:** {miembro.joined_at.strftime('%Y-%m-%d %H:%M:%S')}")
    await ctx.send(f"**Se unió a Discord el:** {miembro.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    await ctx.send(f"**Avatar:** {miembro.display_avatar.url}")

@bot.command()
async def say(ctx, *, texto):
    """Hace que el bot diga lo que escribes."""
    await ctx.send(texto)

# --- Comandos del sistema de verificación ---
@bot.command()
async def verificar(ctx):
    if ctx.channel.id == VERIFICATION_CHANNEL_ID:
        author_id = ctx.author.id
        if author_id not in pending_verifications:
            pending_verifications[author_id] = {}
            embed = discord.Embed(
                title="Proceso de Verificación",
                description="Por favor, responde las siguientes preguntas:",
                color=discord.Color.blue()
            )
            embed.add_field(name="Pregunta 1", value="Usuario de Roblox (No apodo):", inline=False)
            embed.add_field(name="Pregunta 2", value="Nombre de rol:", inline=False)
            embed.add_field(name="Pregunta 3", value="Apellido de rol:", inline=False)
            embed.add_field(name="Pregunta 4", value="Edad (Rol):", inline=False)
            embed.add_field(name="Pregunta 5", value="Edad (Real):", inline=False)
            embed.add_field(name="Pregunta 6", value="Como conociste el servidor?:", inline=False)
            embed.add_field(name="Pregunta 7", value="Has estado en otro servidor de rol?:", inline=False)
            embed.add_field(name="Pregunta 8", value="Sabes que si eres aceptado tienes que ser respetuoso con los miembros del servidor y del Staff? (Sí/No)", inline=False)
            embed.add_field(name="Pregunta 9", value="Imagen del perfil (debe salir el nombre de roblox):", inline=False)
            embed.set_footer(text="Recuerda leer las normas. Para jugar en el servidor requieres de un cuerpo cuadrado en caso de tener un PJ masculino y hágase el DNI al ingresar.")
            await ctx.author.send(embed=embed)
            await ctx.send(f"{ctx.author.mention} Te he enviado un mensaje privado con el formulario de verificación.")
        else:
            await ctx.send(f"{ctx.author.mention} Ya tienes una verificación pendiente. Por favor, revisa tus mensajes privados.")
    else:
        await ctx.send(f"Este comando solo puede usarse en el canal <#1339503726825701387>.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    author_id = message.author.id
    if isinstance(message.channel, discord.DMChannel) and author_id in pending_verifications:
        user_responses = pending_verifications[author_id]
        num_responses = len(user_responses)

        if num_responses == 0:
            user_responses['roblox_usuario'] = message.content
            await message.channel.send("Gracias. Siguiente pregunta: Nombre de rol:")
        elif num_responses == 1:
            user_responses['rol_nombre'] = message.content
            await message.channel.send("Gracias. Siguiente pregunta: Apellido de rol:")
        elif num_responses == 2:
            user_responses['rol_apellido'] = message.content
            await message.channel.send("Gracias. Siguiente pregunta: Edad (Rol):")
        elif num_responses == 3:
            user_responses['edad_rol'] = message.content
            await message.channel.send("Gracias. Siguiente pregunta: Edad (Real):")
        elif num_responses == 4:
            user_responses['edad_real'] = message.content
            await message.channel.send("Gracias. Siguiente pregunta: Como conociste el servidor?:")
        elif num_responses == 5:
            user_responses['conocio_servidor'] = message.content
            await message.channel.send("Gracias. Siguiente pregunta: Has estado en otro servidor de rol?:")
        elif num_responses == 6:
            user_responses['otro_servidor_rol'] = message.content
            await message.channel.send("Gracias. Siguiente pregunta: Sabes que si eres aceptado tienes que ser respetuoso con los miembros del servidor y del Staff? (Sí/No)")
        elif num_responses == 7:
            response = message.content.lower()
            if response == 'sí' or response == 'si':
                user_responses['respetuoso'] = True
                await message.channel.send("Gracias. Última pregunta: Imagen del perfil (debe salir el nombre de roblox):")
            elif response == 'no':
                user_responses['respetuoso'] = False
                await message.channel.send("Lo siento, el respeto es fundamental para unirte al servidor. Si cambias de opinión, puedes usar el comando `!verificar` nuevamente en el servidor.")
                del pending_verifications[author_id]
                return
            else:
                await message.channel.send("Respuesta inválida. Por favor, responde 'Sí' o 'No' a la pregunta sobre el respeto.")
        elif num_responses == 8:
            user_responses['imagen_perfil'] = message.content
            await message.channel.send("¡Gracias por completar el formulario de verificación! Tu solicitud será revisada por un administrador.")
            admin_verification_channel = bot.get_channel(ADMIN_VERIFICATION_CHANNEL_ID)
            if admin_verification_channel:
                embed = discord.Embed(
                    title="Nueva Solicitud de Verificación",
                    color=discord.Color.green()
                )
                embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
                embed.add_field(name="Usuario de Discord", value=message.author.mention, inline=False)
                embed.add_field(name="ID de Discord", value=author_id, inline=False)
                embed.add_field(name="Usuario de Roblox", value=user_responses.get('roblox_usuario', 'No respondió'), inline=False)
                embed.add_field(name="Nombre de rol", value=user_responses.get('rol_nombre', 'No respondió'), inline=False)
                embed.add_field(name="Apellido de rol", value=user_responses.get('rol_apellido', 'No respondió'), inline=False)
                embed.add_field(name="Edad (Rol)", value=user_responses.get('edad_rol', 'No respondió'), inline=False)
                embed.add_field(name="Edad (Real)", value=user_responses.get('edad_real', 'No respondió'), inline=False)
                embed.add_field(name="Como conociste el servidor?", value=user_responses.get('conocio_servidor', 'No respondió'), inline=False)
                embed.add_field(name="Ha estado en otro servidor de rol?", value=user_responses.get('otro_servidor_rol', 'No respondió'), inline=False)
                embed.add_field(name="Respetuoso", value="Sí" if user_responses.get('respetuoso') else "No", inline=False)
                embed.add_field(name="Imagen del perfil", value=user_responses.get('imagen_perfil', 'No respondió'), inline=False)
                embed.set_footer(text=f"Para aprobar: !aprobar {author_id} | Para rechazar: !rechazar {author_id}")
                await admin_verification_channel.send(embed=embed)
            del pending_verifications[author_id]

    await bot.process_commands(message)

@bot.command()
async def aprobar(ctx, user_id: int):
    if any(role.id in ADMIN_ROLE_IDS for role in ctx.author.roles):
        guild = ctx.guild
        member = guild.get_member(user_id)
        if member:
            approved_role = guild.get_role(APPROVED_ROLE_ID)
            removed_role = guild.get_role(REMOVED_ROLE_ID)
            if approved_role:
                await member.add_roles(approved_role)
                message_content = f"¡{member.mention} ha sido aprobado y se le ha asignado el rol <@&{APPROVED_ROLE_ID}>!"
                if removed_role:
                    await member.remove_roles(removed_role)
                    message_content += f" También se le ha removido el rol <@&{REMOVED_ROLE_ID}>."
                await ctx.send(message_content)
            else:
                await ctx.send(f"Error: No se encontró el rol con ID {APPROVED_ROLE_ID}.")
        else:
            await ctx.send(f"Error: No se encontró ningún miembro con ID {user_id}.")
    else:
        await ctx.send("No tienes permiso para usar este comando.")

@bot.command()
async def rechazar(ctx, user_id: int):
    if any(role.id in ADMIN_ROLE_IDS for role in ctx.author.roles):
        guild = ctx.guild
        member = guild.get_member(user_id)
        if member and user_id in pending_verifications:
            del pending_verifications[user_id]
            await ctx.send(f"La verificación de {member.mention} ha sido rechazada.")
            await member.send("Tu solicitud de verificación para el servidor ha sido rechazada. Si crees que esto es un error, contacta a un administrador.")
        elif not member:
            await ctx.send(f"Error: No se encontró ningún miembro con ID {user_id}.")
        elif user_id not in pending_verifications:
            await ctx.send(f"No hay ninguna verificación pendiente para el usuario con ID {user_id}.")
    else:
        await ctx.send("No tienes permiso para usar este comando.")

if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: La variable de entorno DISCORD_BOT_TOKEN no está configurada.")