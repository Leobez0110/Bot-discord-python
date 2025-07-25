import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from discord.ui import View, Button
from discord import ButtonStyle, Embed
import random
import time


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)

# IDs dos canais e cargo
CANAL_PROVA_DE_META_ID = 1396638697319038996
CANAL_ANUNCIOS_ID = 1396632953802461365
CANAL_ANALISE_SUPERIOR_ID = 1398322930487787531
CARGO_000_ID = 1391469132750258238
CANAL_AUSENCIAS_ID = 1393658232614162442


start_time = time.time()

# ============================
# EVENTO: reação automática a prints no canal de prova de meta
# ============================
@bot.event
async def on_message(message):
    if message.channel.id == CANAL_PROVA_DE_META_ID and not message.author.bot:
        if message.attachments:
            try:
                await message.add_reaction("✅")
            except Exception as e:
                print(f"Erro ao reagir: {e}")
    await bot.process_commands(message)

# ============================
# VIEW: botões estilizados para análise superior
# ============================
class AprovarMetaView(View):
    def __init__(self, autor, original_msg, msg_id=None):
        super().__init__(timeout=None)
        self.autor = autor
        self.original_msg = original_msg
        self.msg_id = msg_id  # usado se for editável futuramente

    @discord.ui.button(label="✅ Aprovar", style=ButtonStyle.green, emoji="✅")
    async def aceitar(self, interaction: discord.Interaction, button: Button):
        if interaction.user.guild_permissions.administrator:
            await self.original_msg.add_reaction("🟢")
            await interaction.response.send_message("Meta aprovada ✅", ephemeral=True)
        else:
            await interaction.response.send_message("Você não tem permissão para aprovar metas.", ephemeral=True)

    @discord.ui.button(label="❌ Recusar", style=ButtonStyle.red, emoji="❌")
    async def negar(self, interaction: discord.Interaction, button: Button):
        if interaction.user.guild_permissions.administrator:
            await self.original_msg.add_reaction("🔴")
            await interaction.response.send_message("Meta recusada ❌", ephemeral=True)
        else:
            await interaction.response.send_message("Você não tem permissão para recusar metas.", ephemeral=True)

# ============================
# COMANDO: editar mensagem da análise (admin)
# ============================
@bot.command()
@commands.has_permissions(administrator=True)
async def editar_meta(ctx, msg_id: int, *, novo_texto: str):
    """Permite que um superior edite uma mensagem de análise enviada"""
    canal_analise = bot.get_channel(CANAL_ANALISE_SUPERIOR_ID)
    try:
        mensagem = await canal_analise.fetch_message(msg_id)
        if mensagem.embeds:
            embed = mensagem.embeds[0]
            embed.description = novo_texto + "\n\n───────────────"
            await mensagem.edit(embed=embed)
            await ctx.send("✅ Mensagem editada com sucesso.")
        else:
            await ctx.send("❌ Mensagem não contém embed.")
    except Exception as e:
        await ctx.send(f"❌ Erro ao editar a mensagem: {e}")

# ============================
# COMANDO: verificar e anunciar metas
# ============================
async def verificar_metas():
    canal_prova = bot.get_channel(CANAL_PROVA_DE_META_ID)
    canal_anuncio = bot.get_channel(CANAL_ANUNCIOS_ID)

    if not canal_prova or not canal_anuncio:
        print('Canais não encontrados')
        return

    guild = canal_prova.guild
    membros = [m for m in guild.members if not m.bot and any(role.id == CARGO_000_ID for role in m.roles)]

    agora = datetime.utcnow() - timedelta(hours=3)
    ontem = agora.date() - timedelta(days=1)
    dois_dias_atras = agora.date() - timedelta(days=2)

    mensagens_ontem = []
    async for msg in canal_prova.history(limit=1000,
                                         after=datetime.combine(ontem, datetime.min.time()),
                                         before=datetime.combine(ontem + timedelta(days=1), datetime.min.time())):
        if msg.attachments and not msg.author.bot:
            mensagens_ontem.append(msg)
    ids_ontem = {msg.author.id for msg in mensagens_ontem}

    mensagens_ult_2dias = []
    async for msg in canal_prova.history(limit=2000,
                                         after=datetime.combine(dois_dias_atras, datetime.min.time()),
                                         before=datetime.combine(ontem + timedelta(days=1), datetime.min.time())):
        if msg.attachments and not msg.author.bot:
            mensagens_ult_2dias.append(msg)
    ids_ult_2dias = {msg.author.id for msg in mensagens_ult_2dias}

    texto_inicial = (
        f'**METAS DIÁRIAS**\nMeta para dia {agora.strftime("%d/%m/%Y")}\n\n'
        'Para provar a sua meta, o jogador terá de ir no chat ⁠💸・prova_de_meta mandar print da sua meta paga.\n\n'
        'Segue embaixo a lista de membros:\n\n'
        '✅  (PAGO)\n❌  (NÃO PAGO)\n⚠️  (AUSENTE +2 dias)\n\n'
    )

    linhas = []
    for membro in membros:
        if membro.id in ids_ontem:
            status = "✅"
        elif membro.id in ids_ult_2dias:
            status = "❌"
        else:
            status = "⚠️"
        linhas.append(f'{membro.mention} = {status}')

    bloco = texto_inicial
    for linha in linhas:
        if len(bloco) + len(linha) + 1 > 1900:
            await canal_anuncio.send(bloco)
            bloco = ''
        bloco += linha + '\n'
    if bloco:
        await canal_anuncio.send(bloco)

# ============================
# TASK: tarefa diária às 00:01
# ============================
@tasks.loop(minutes=1)
async def tarefa_meta_diaria():
    agora = datetime.utcnow()
    horario_local = agora - timedelta(hours=3)
    if horario_local.hour == 0 and horario_local.minute == 1:
        await verificar_metas()

# ============================
# COMANDO: teste manual
# ============================
@bot.command()
async def testar_meta(ctx):
    await ctx.send("🟡 Teste manual da verificação de metas iniciado...")
    await verificar_metas()
    await ctx.send("🟢 Teste manual finalizado.")

# ============================
# COMANDO: falar no canal atual
# ============================
@bot.command()
async def falar(ctx, *, texto: str):
    await ctx.channel.send(texto)

# ============================
# COMANDO: processar prints do dia e mandar para superiores
# ============================
@bot.command()
async def verificar_hoje(ctx):
    canal_prova = bot.get_channel(CANAL_PROVA_DE_META_ID)
    canal_analise = bot.get_channel(CANAL_ANALISE_SUPERIOR_ID)

    agora = datetime.utcnow() - timedelta(hours=3)
    hoje = agora.date()
    prints_hoje = 0

    async for msg in canal_prova.history(limit=1000, after=datetime.combine(hoje, datetime.min.time())):
        if not msg.author.bot and msg.attachments:
            try:
                await msg.add_reaction("✅")
                embed = Embed(
                    title="📸 Nova transação enviada",
                    description=f"Enviada por {msg.author.mention}\n\n───────────────",
                    color=0x2B2D31,
                    timestamp=msg.created_at
                )
                embed.set_image(url=msg.attachments[0].url)
                embed.set_footer(text="Clique abaixo para aprovar ou negar")

                view = AprovarMetaView(autor=msg.author, original_msg=msg)
                await canal_analise.send(embed=embed, view=view)
                prints_hoje += 1
            except Exception as e:
                print(f"Erro ao processar mensagem {msg.id}: {e}")

    await ctx.send(f"🔎 {prints_hoje} prints processadas do dia {hoje.strftime('%d/%m/%Y')}.")

# ============================
# COMANDO: ranking de prints
# ============================
@bot.command()
async def ranking_prints(ctx):
    """Mostra o ranking dos membros que mais enviaram prints no canal de meta"""
    canal_prova = bot.get_channel(CANAL_PROVA_DE_META_ID)
    contagem = {}
    async for msg in canal_prova.history(limit=2000):
        if not msg.author.bot and msg.attachments:
            contagem[msg.author] = contagem.get(msg.author, 0) + 1
    if not contagem:
        await ctx.send("Nenhuma print encontrada.")
        return
    ranking = sorted(contagem.items(), key=lambda x: x[1], reverse=True)
    texto = "**🏆 Ranking de Envios de Prints:**\n"
    for i, (user, count) in enumerate(ranking[:10], 1):
        texto += f"{i}. {user.mention}: {count} prints\n"
    await ctx.send(texto)

# ============================
# COMANDO: informações do servidor
# ============================
@bot.command()
async def infos(ctx):
    """Mostra informações básicas do servidor"""
    guild = ctx.guild
    embed = discord.Embed(
        title=f"Informações do servidor {guild.name}",
        color=0x7289DA,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="👥 Membros", value=guild.member_count)
    embed.add_field(name="💬 Canais de texto", value=len(guild.text_channels))
    embed.add_field(name="🔊 Canais de voz", value=len(guild.voice_channels))
    embed.add_field(name="🆔 ID", value=guild.id)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)

# ============================
# COMANDO: avatar de um usuário
# ============================
@bot.command()
async def avatar(ctx, membro: discord.Member = None):
    """Mostra o avatar de um membro"""
    membro = membro or ctx.author
    embed = discord.Embed(title=f"Avatar de {membro}", color=0x2B2D31)
    if membro.avatar:
        embed.set_image(url=membro.avatar.url)
    else:
        embed.set_image(url=membro.default_avatar.url)
    await ctx.send(embed=embed)

# ============================
# COMANDO: sorteio simples
# ============================
@bot.command()
async def sortear(ctx, *membros: discord.Member):
    """Sorteia um membro entre os mencionados"""
    if not membros:
        await ctx.send("Mencione pelo menos um membro para sortear.")
        return
    vencedor = random.choice(membros)
    await ctx.send(f"🎉 O vencedor é: {vencedor.mention}!")

# ============================
# COMANDO: ping (latência)
# ============================
@bot.command()
async def ping(ctx):
    """Mostra a latência do bot"""
    latencia = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latência: {latencia}ms")

# ============================
# COMANDO: ajuda personalizada
# ============================
@bot.command()
async def ajuda(ctx):
    """Mostra os comandos disponíveis"""
    comandos = [
        ".testar_meta - Teste manual da verificação de metas",
        ".falar <texto> - Bot fala no canal",
        ".verificar_hoje - Processa prints do dia",
        ".editar_meta <msg_id> <novo_texto> - Edita análise (admin)",
        ".ranking_prints - Ranking de prints enviadas",
        ".infos - Informações do servidor",
        ".avatar [@membro] - Mostra avatar",
        ".sortear @m1 @m2 ... - Sorteia um membro",
        ".ping - Mostra latência do bot",
        ".userinfo [@membro] - Info detalhada de um usuário",
        ".servericon - Mostra o ícone do servidor",
        ".limpar <qtd> - Limpa mensagens (admin)",
        ".uptime - Mostra há quanto tempo o bot está online",
        ".oi - O bot te cumprimenta",
        ".dm @membro <mensagem> - Envia DM para alguém",
        ".dado [lados] - Rola um dado",
        ".moeda - Cara ou coroa",
        ".agora - Mostra o horário atual",
        ".serverbanner - Mostra o banner do servidor",
        ".cargos - Lista todos os cargos",
        ".emojis - Lista todos os emojis",
        ".enquete <pergunta> <opções...> - Cria uma enquete",
        ".canalinfo [#canal] - Info de canal",
        ".cargoinfo <cargo> - Info de cargo",
        ".online - Quantos membros online",
        ".offline - Quantos membros offline",
        ".emcall - Quantos membros em call",
        ".serveravatar - Avatar do servidor",
        ".latency - Tempo de resposta do bot",
        ".reverso <texto> - Texto ao contrário",
        ".membroscargo <cargo> - Quantos membros em um cargo",
        ".bots - Lista todos os bots",
        ".boosters - Lista todos os boosters",
        ".cor <hex> <texto> - Mensagem colorida",
        ".analisar_ausencias - Ele verifica todas as mensagens criadas até o momento no chat #ausencias"
    ]
    embed = discord.Embed(
        title="🤖 Ajuda - Comandos disponíveis",
        description="\n".join(comandos),
        color=0x5865F2
    )
    await ctx.send(embed=embed)

# ============================
# COMANDO: informações detalhadas de usuário
# ============================
@bot.command()
async def userinfo(ctx, membro: discord.Member = None):
    """Mostra informações detalhadas de um usuário"""
    membro = membro or ctx.author
    embed = discord.Embed(
        title=f"Informações de {membro}",
        color=0x3498db,
        timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url=membro.avatar.url if membro.avatar else membro.default_avatar.url)
    embed.add_field(name="ID", value=membro.id)
    embed.add_field(name="Entrou em", value=membro.joined_at.strftime('%d/%m/%Y %H:%M'))
    embed.add_field(name="Criou a conta em", value=membro.created_at.strftime('%d/%m/%Y %H:%M'))
    embed.add_field(name="Cargo mais alto", value=membro.top_role.mention)
    embed.add_field(name="Bot?", value="Sim" if membro.bot else "Não")
    await ctx.send(embed=embed)

# ============================
# COMANDO: mostrar ícone do servidor
# ============================
@bot.command()
async def servericon(ctx):
    """Mostra o ícone do servidor"""
    if ctx.guild.icon:
        await ctx.send(ctx.guild.icon.url)
    else:
        await ctx.send("O servidor não possui ícone.")

# ============================
# COMANDO: limpar mensagens (admin)
# ============================
@bot.command()
@commands.has_permissions(manage_messages=True)
async def limpar(ctx, quantidade: int = 10):
    """Limpa mensagens do canal (padrão: 10)"""
    if quantidade < 1 or quantidade > 100:
        await ctx.send("Escolha um valor entre 1 e 100.")
        return
    await ctx.channel.purge(limit=quantidade+1)
    msg = await ctx.send(f"🧹 {quantidade} mensagens limpas!")
    await msg.delete(delay=3)

# ============================
# COMANDO: uptime do bot
# ============================
@bot.command()
async def uptime(ctx):
    """Mostra há quanto tempo o bot está online"""
    segundos = int(time.time() - start_time)
    horas, resto = divmod(segundos, 3600)
    minutos, segundos = divmod(resto, 60)
    await ctx.send(f"⏱️ Uptime: {horas}h {minutos}m {segundos}s")

# ============================
# COMANDO: dizer oi
# ============================
@bot.command()
async def oi(ctx):
    """O bot te cumprimenta"""
    await ctx.send(f"Olá, {ctx.author.mention}! 👋")

# ============================
# COMANDO: enviar DM
# ============================
@bot.command()
async def dm(ctx, membro: discord.Member, *, mensagem: str):
    """Envia uma mensagem privada para o membro"""
    try:
        await membro.send(f"Mensagem de {ctx.author.mention}: {mensagem}")
        await ctx.send("Mensagem enviada com sucesso!")
    except Exception:
        await ctx.send("Não foi possível enviar a mensagem.")

# ============================
# COMANDO: rolar dado
# ============================
@bot.command()
async def dado(ctx, lados: int = 6):
    """Rola um dado com o número de lados escolhido"""
    if lados < 2:
        await ctx.send("O dado precisa ter pelo menos 2 lados.")
        return
    resultado = random.randint(1, lados)
    await ctx.send(f"🎲 Você rolou: {resultado}")

# ============================
# COMANDO: moeda
# ============================
@bot.command()
async def moeda(ctx):
    """Cara ou coroa"""
    resultado = random.choice(["Cara", "Coroa"])
    await ctx.send(f"🪙 Deu: **{resultado}**!")

# ============================
# COMANDO: tempo atual
# ============================
@bot.command()
async def agora(ctx):
    """Mostra o horário atual"""
    agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    await ctx.send(f"🕒 Agora são: {agora}")

# ============================
# COMANDO: banner do servidor
# ============================
@bot.command()
async def serverbanner(ctx):
    """Mostra o banner do servidor"""
    if ctx.guild.banner:
        await ctx.send(ctx.guild.banner.url)
    else:
        await ctx.send("O servidor não possui banner.")

# ============================
# COMANDO: lista de cargos
# ============================
@bot.command()
async def cargos(ctx):
    """Lista todos os cargos do servidor"""
    cargos = [role.name for role in ctx.guild.roles if role.name != "@everyone"]
    await ctx.send("Cargos do servidor:\n" + ", ".join(cargos))

# ============================
# COMANDO: listar emojis
# ============================
@bot.command()
async def emojis(ctx):
    """Lista todos os emojis do servidor"""
    if ctx.guild.emojis:
        await ctx.send("Emojis: " + " ".join(str(e) for e in ctx.guild.emojis))
    else:
        await ctx.send("O servidor não possui emojis personalizados.")

# ============================
# COMANDO: criar enquete
# ============================
@bot.command()
async def enquete(ctx, pergunta: str, *opcoes):
    """Cria uma enquete rápida (máx 10 opções)"""
    if len(opcoes) < 2 or len(opcoes) > 10:
        await ctx.send("Forneça entre 2 e 10 opções.")
        return
    emojis = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']
    descricao = ""
    for i, opcao in enumerate(opcoes):
        descricao += f"{emojis[i]} {opcao}\n"
    embed = discord.Embed(title=pergunta, description=descricao, color=0x00ff00)
    msg = await ctx.send(embed=embed)
    for i in range(len(opcoes)):
        await msg.add_reaction(emojis[i])

# ============================
# COMANDO: info de canal
# ============================
@bot.command()
async def canalinfo(ctx, canal: discord.TextChannel = None):
    """Mostra informações de um canal"""
    canal = canal or ctx.channel
    embed = discord.Embed(
        title=f"Canal: {canal.name}",
        color=0x7289DA
    )
    embed.add_field(name="ID", value=canal.id)
    embed.add_field(name="Criado em", value=canal.created_at.strftime('%d/%m/%Y %H:%M'))
    embed.add_field(name="Categoria", value=canal.category.name if canal.category else "Nenhuma")
    embed.add_field(name="NSFW", value="Sim" if canal.is_nsfw() else "Não")
    await ctx.send(embed=embed)

# ============================
# COMANDO: info de cargo
# ============================
@bot.command()
async def cargoinfo(ctx, *, cargo: discord.Role):
    """Mostra informações de um cargo"""
    embed = discord.Embed(
        title=f"Cargo: {cargo.name}",
        color=cargo.color
    )
    embed.add_field(name="ID", value=cargo.id)
    embed.add_field(name="Membros", value=len(cargo.members))
    embed.add_field(name="Cor", value=str(cargo.color))
    embed.add_field(name="Menção", value=cargo.mention)
    embed.add_field(name="Criado em", value=cargo.created_at.strftime('%d/%m/%Y %H:%M'))
    await ctx.send(embed=embed)

# ============================
# COMANDO: membros online
# ============================
@bot.command()
async def online(ctx):
    """Mostra quantos membros estão online"""
    online = sum(1 for m in ctx.guild.members if m.status == discord.Status.online and not m.bot)
    await ctx.send(f"👤 Membros online: {online}")

# ============================
# COMANDO: membros offline
# ============================
@bot.command()
async def offline(ctx):
    """Mostra quantos membros estão offline"""
    offline = sum(1 for m in ctx.guild.members if m.status == discord.Status.offline and not m.bot)
    await ctx.send(f"👤 Membros offline: {offline}")

# ============================
# COMANDO: membros em call
# ============================
@bot.command()
async def emcall(ctx):
    """Mostra quantos membros estão em call"""
    emcall = sum(len(vc.members) for vc in ctx.guild.voice_channels)
    await ctx.send(f"🔊 Membros em call: {emcall}")

# ============================
# COMANDO: avatar do servidor
# ============================
@bot.command()
async def serveravatar(ctx):
    """Mostra o avatar do servidor"""
    if ctx.guild.icon:
        await ctx.send(ctx.guild.icon.url)
    else:
        await ctx.send("O servidor não possui avatar.")

# ============================
# COMANDO: tempo de resposta
# ============================
@bot.command()
async def latency(ctx):
    """Mostra o tempo de resposta do bot"""
    await ctx.send(f"⏱️ Latência: {round(bot.latency * 1000)}ms")

# ============================
# COMANDO: mensagem reversa
# ============================
@bot.command()
async def reverso(ctx, *, texto: str):
    """Retorna o texto ao contrário"""
    await ctx.send(texto[::-1])

# ============================
# COMANDO: contar membros por cargo
# ============================
@bot.command()
async def membroscargo(ctx, *, cargo: discord.Role):
    """Conta quantos membros possuem determinado cargo"""
    await ctx.send(f"O cargo {cargo.mention} possui {len(cargo.members)} membros.")

# ============================
# COMANDO: listar bots
# ============================
@bot.command()
async def bots(ctx):
    """Lista todos os bots do servidor"""
    bots = [m for m in ctx.guild.members if m.bot]
    if bots:
        await ctx.send("Bots do servidor:\n" + ", ".join(m.mention for m in bots))
    else:
        await ctx.send("Não há bots neste servidor.")

# ============================
# COMANDO: listar boosters
# ============================
@bot.command()
async def boosters(ctx):
    """Lista todos os boosters do servidor"""
    boosters = ctx.guild.premium_subscribers
    if boosters:
        await ctx.send("Boosters do servidor:\n" + ", ".join(m.mention for m in boosters))
    else:
        await ctx.send("Não há boosters neste servidor.")

# ============================
# COMANDO: mensagem colorida
# ============================
@bot.command()
async def cor(ctx, cor_hex: str, *, texto: str):
    """Envia uma mensagem embed com a cor escolhida (ex: .cor ff0000 Olá!)"""
    try:
        cor_int = int(cor_hex, 16)
        embed = discord.Embed(description=texto, color=cor_int)
        await ctx.send(embed=embed)
    except:
        await ctx.send("Cor inválida. Use apenas números e letras de A a F.")

# ============================
# EVENTO: reação automática a prints no canal de prova de meta e ausências
# ============================
@bot.event
async def on_message(message):
    # Reage no canal de prova de meta
    if message.channel.id == CANAL_PROVA_DE_META_ID and not message.author.bot:
        if message.attachments:
            try:
                await message.add_reaction("✅")
            except Exception as e:
                print(f"Erro ao reagir: {e}")

    # Reage no canal de ausências
    if message.channel.id == CANAL_AUSENCIAS_ID and not message.author.bot:
        try:
            await message.add_reaction("✅")
            await message.add_reaction("❌")
        except Exception as e:
            print(f"Erro ao reagir no canal de ausências: {e}")

    await bot.process_commands(message)

# ...código existente...

# ============================
# COMANDO: analisar mensagens antigas do canal de ausências
# ============================
@bot.command()
@commands.has_permissions(administrator=True)
async def analisar_ausencias(ctx):
    """Analisa todas as mensagens já enviadas no canal de ausências e reage com ✅ e ❌"""
    canal = bot.get_channel(CANAL_AUSENCIAS_ID)
    if not canal:
        await ctx.send("Canal de ausências não encontrado.")
        return

    total = 0
    async for msg in canal.history(limit=None, oldest_first=True):
        if not msg.author.bot:
            try:
                await msg.add_reaction("✅")
                await msg.add_reaction("❌")
                total += 1
            except Exception as e:
                print(f"Erro ao reagir na mensagem {msg.id}: {e}")
    await ctx.send(f"✅ Reações adicionadas em {total} mensagens no canal de ausências.")


# ============================
# BOT: pronto
# ============================
@bot.event
async def on_ready():
    print(f"🤖 Bot conectado como {bot.user}")
    tarefa_meta_diaria.start()
