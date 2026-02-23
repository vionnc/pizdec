import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import random
import os
import asyncio
from discord import FFmpegPCMAudio
import glob
import subprocess

# ========== НАСТРОЙКИ ==========
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)

DATA_FILE = 'aura_data.json'
INVENTORY_FILE = 'inventory_data.json'
MUSIC_FOLDER = 'aura_phonk'
FFMPEG_PATH = 'C:\\Users\\Aura_Farmer3000\\OneDrive\\Desktop\\aura_bot\\ffmpeg.exe'

# ========== МАГАЗИН ==========
shop_items = {
    'fonker': {
        'name': 'Фонкер',
        'price': 10000,
        'description': 'Роль настоящего Аура Фарм Пхонкер',
        'role_name': 'Фонкер',
        'color': 0x00ff00
    },
    'legend': {
        'name': 'Легенда Аура Череп',
        'price': 50000,
        'description': 'Легендарный статус',
        'role_name': 'Легенда Аура Череп',
        'color': 0xffd700
    },
    'troll': {
        'name': 'Троллфейс',
        'price': 100000,
        'description': 'Тот кто знает',
        'role_name': 'Троллфейс',
        'color': 0xff4500
    }
}

# ========== ФУНКЦИИ ЗАГРУЗКИ ==========
def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_inventory():
    try:
        with open(INVENTORY_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_inventory(data):
    with open(INVENTORY_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_music_files(folder=MUSIC_FOLDER):
    music_files = []
    for ext in ['*.mp3', '*.wav', '*.ogg', '*.m4a', '*.flac']:
        music_files.extend(glob.glob(os.path.join(folder, '**', ext), recursive=True))
        music_files.extend(glob.glob(os.path.join(folder, ext)))
    return music_files

# ========== КНОПКА ФАРМА ==========
class AuraFarmButton(Button):
    def __init__(self):
        super().__init__(label="AURA FARM", style=discord.ButtonStyle.green)
    
    async def callback(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        data = load_data()
        
        if user_id not in data:
            data[user_id] = {'name': interaction.user.name, 'aura': 0, 'total_farms': 0}
        
        farm_amount = random.randint(3, 45)
        data[user_id]['aura'] += farm_amount
        data[user_id]['total_farms'] += 1
        save_data(data)
        
        await interaction.response.send_message(
            f"✨ Ты нафармил {farm_amount} Aura!\n💰 Auras: {data[user_id]['aura']} Aura",
            ephemeral=False, delete_after=5
        )

# ========== КОМАНДЫ ФАРМА ==========
@bot.command()
async def farm_panel(ctx):
    button = AuraFarmButton()
    view = View(timeout=None)
    view.add_item(button)
    embed = discord.Embed(title="AURA FARMING", description="Нажми на кнопку чтобы фармить ауру", color=discord.Color.purple())
    await ctx.send(embed=embed, view=view)

@bot.command()
async def balance(ctx):
    user_id = str(ctx.author.id)
    data = load_data()
    if user_id not in data:
        await ctx.send(" Ты еще не фармил! Используй !farm_panel")
    else:
        await ctx.send(f" {ctx.author.name}, у тебя **{data[user_id]['aura']}** Aura")

@bot.command()
async def top(ctx):
    data = load_data()
    sorted_users = sorted(data.items(), key=lambda x: x[1]['aura'], reverse=True)[:5]
    embed = discord.Embed(title="🏆 Топ фармеров", color=discord.Color.gold())
    for i, (user_id, user_data) in enumerate(sorted_users, 1):
        user = await bot.fetch_user(int(user_id))
        embed.add_field(name=f"{i}. {user.name}", value=f"✨ {user_data['aura']} Aura", inline=False)
    await ctx.send(embed=embed)

# ========== КОМАНДЫ МАГАЗИНА ==========
@bot.command()
async def магазин(ctx):
    embed = discord.Embed(title="🛒 Магазин Aura", description="Трать ауру Дрын", color=discord.Color.gold())
    for item_id, item in shop_items.items():
        embed.add_field(
            name=f"**{item['name']}**",
            value=f"💰 {item['price']} Aura\n📝 {item['description']}\n🔹 `!купить {item_id}`",
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command()
async def купить(ctx, item_id: str):
    item_id = item_id.lower()
    if item_id not in shop_items:
        await ctx.send(" Такого товара нет Смотри !магазин")
        return

    item = shop_items[item_id]
    data = load_data()
    user_id = str(ctx.author.id)

    if user_id not in data or data[user_id]['aura'] < item['price']:
        await ctx.send(f" Недостаточно Aura! Нужно {item['price']}")
        return

    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send(" У бота нет прав")
        return

    role = discord.utils.get(ctx.guild.roles, name=item['role_name'])
    if not role:
        try:
            role = await ctx.guild.create_role(name=item['role_name'], color=item['color'], reason="Магазин")
        except:
            await ctx.send(" Не могу создать роль. Проверь права")
            return

    if role.position >= ctx.guild.me.top_role.position:
        await ctx.send(f" Роль бота должна быть выше роли {item['role_name']}!")
        return

    try:
        await ctx.author.add_roles(role)
    except:
        await ctx.send(" Не могу выдать роль")
        return

    data[user_id]['aura'] -= item['price']
    save_data(data)

    inv = load_inventory()
    inv.setdefault(user_id, []).append({
        'item': item_id, 'name': item['name'], 'price': item['price'], 'date': str(ctx.message.created_at)
    })
    save_inventory(inv)

    await ctx.send(f"Ты купил роль **{item['name']}**! Остаток: {data[user_id]['aura']} Aura")

@bot.command()
async def инвентарь(ctx):
    inv = load_inventory()
    user_id = str(ctx.author.id)
    if user_id not in inv or not inv[user_id]:
        await ctx.send("📦 У тебя пока ничего нет.")
        return
    items_list = "\n".join([f"• {i['name']} - {i['price']} Aura" for i in inv[user_id][-10:]])
    embed = discord.Embed(title=f"📦 Инвентарь {ctx.author.name}", color=discord.Color.blue())
    embed.add_field(name="Куплено:", value=items_list, inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def казино(ctx, ставка: int):
    user_id = str(ctx.author.id)
    data = load_data()
    if user_id not in data or data[user_id]['aura'] < ставка:
        await ctx.send(" Недостаточно Aura!")
        return
    if ставка <= 0:
        await ctx.send(" Ставка должна быть больше 0")
        return
    if random.choice([True, False]):
        data[user_id]['aura'] += ставка
        save_data(data)
        await ctx.send(f"🎉 Ты выиграл {ставка} Ауру браза Баланс: {data[user_id]['aura']}")
    else:
        data[user_id]['aura'] -= ставка
        save_data(data)
        await ctx.send(f"😢 Ты проиграл {ставка} Aura нооу Баланс: {data[user_id]['aura']}")

# ========== МУЗЫКА (ЛОКАЛЬНАЯ) ==========
@bot.command()
async def плейлист(ctx):
    files = get_music_files()
    if not files:
        await ctx.send(" В папке aura_phonk нет музыки")
        return
    embed = discord.Embed(title="Локальная медиатека", description=f"Найдено треков: {len(files)}", color=discord.Color.blue())
    tracks = "\n".join([f"{i}. {os.path.basename(f)}" for i, f in enumerate(files[:15], 1)])
    if len(files) > 15:
        tracks += f"\n...и ещё {len(files) - 15}"
    embed.add_field(name="Треки", value=tracks, inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def фонк(ctx, *, запрос=None):
    if not ctx.author.voice:
        await ctx.send("Get in voice chat eblo!")
        return
    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    files = get_music_files()
    if not files:
        await ctx.send(" Сначала добавь музыку в папку aura_phonk")
        return

    if запрос is None:
        chosen = random.choice(files)
        await ctx.send(f" Случайный Пхонк: {os.path.basename(chosen)}")
    else:
        matches = [f for f in files if запрос.lower() in os.path.basename(f).lower()]
        if not matches:
            await ctx.send(f" Пхонк '{запрос}' не найден.")
            return
        chosen = matches[0]
        if len(matches) > 1:
            await ctx.send(f" Нашёл {len(matches)} Пхонков, играю первый: {os.path.basename(chosen)}")
        else:
            await ctx.send(f" Играю: {os.path.basename(chosen)}")

    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    ffmpeg_opts = {'executable': FFMPEG_PATH, 'options': '-vn'}
    ctx.voice_client.play(FFmpegPCMAudio(chosen, **ffmpeg_opts))
    embed = discord.Embed(title="Сейчас играет", description=os.path.basename(chosen), color=discord.Color.green())
    await ctx.send(embed=embed)

@bot.command()
async def стоп(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send(" Музыка остановлена, бот вышел из канала")
    else:
        await ctx.send(" Бот не в голосовом канале")

@bot.command()
async def пауза(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send(" Пауза")

@bot.command()
async def продолжить(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send(" Продолжаем Наху")

@bot.event
async def on_ready():
    print(f'✅ Бот {bot.user} запущен!')
    print(f'Бот на серверах: {len(bot.guilds)}')
    if not os.path.exists(MUSIC_FOLDER):
        os.makedirs(MUSIC_FOLDER)
    else:
        print(f'Найдено локальных треков: {len(get_music_files())}')
    print(f'💰 Магазин загружен: {len(shop_items)} товаров')
    print(f'Команды: !farm_panel, !balance, !top, !фонк, !плейлист, !стоп, !магазин, !купить, !инвентарь, !казино')

# ========== ЗАПУСК ==========
bot.run(os.getenv('TOKEN'))