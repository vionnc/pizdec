import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import random
import os
import asyncio
import time
from discord import FFmpegPCMAudio
import glob

# ========== НАСТРОЙКИ ==========
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)

DATA_FILE = 'aura_data.json'
INVENTORY_FILE = 'inventory_data.json'
BUSINESS_FILE = 'business_data.json'
MUSIC_FOLDER = 'aura_phonk'

# ========== РОЛЕВЫЕ БОНУСЫ ==========
role_bonuses = {
    'Фонкер': {
        'multiplier': 1.1,
        'daily_limit': 1500,
        'color': 0x00ff00
    },
    'Легенда Аура Череп': {
        'multiplier': 1.2,
        'daily_limit': 2000,
        'color': 0xffd700
    },
    'Троллфейс': {
        'multiplier': 2.0,
        'daily_limit': 15000,
        'color': 0xff4500
    }
}

# ========== БИЗНЕСЫ ==========
businesses = {
    'kiosk': {
        'name': 'Блядушник',
        'price': 5000,
        'income': 100,
        'cooldown': 3600,
        'emoji': '🏪'
    },
    'bank': {
        'name': 'Банк',
        'price': 50000,
        'income': 1500,
        'cooldown': 7200,
        'emoji': '🏦'
    },
    'factory': {
        'name': 'Завод',
        'price': 200000,
        'income': 10000,
        'cooldown': 21600,
        'emoji': '🏭'
    }
}

# ========== ЗАЩИТА ОТ АВТОКЛИКЕРА ==========
last_click = {}
tax_counter = {}

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

def load_businesses():
    try:
        with open(BUSINESS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_businesses(data):
    with open(BUSINESS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_user_bonus(member):
    for role_name, bonus in role_bonuses.items():
        if discord.utils.get(member.roles, name=role_name):
            return bonus
    return {'multiplier': 1.0, 'daily_limit': 1000}

def needs_tax_check(user_id):
    if user_id not in tax_counter:
        tax_counter[user_id] = 0
    tax_counter[user_id] += 1
    
    if tax_counter[user_id] >= 75:
        tax_counter[user_id] = 0
        return True
    return False

# ========== КНОПКА ФАРМА ==========
class AuraFarmButton(Button):
    def __init__(self):
        super().__init__(label="AURA FARM", style=discord.ButtonStyle.green)
    
    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        current_time = time.time()
        
        if user_id in last_click:
            if current_time - last_click[user_id] < 1:
                await interaction.response.send_message("Не так быстро! Подожди секунду", ephemeral=True, delete_after=2)
                return
        
        last_click[user_id] = current_time
        
        if needs_tax_check(user_id):
            await interaction.response.send_message("Налоговая проверка! Напиши !налоговая в чат", ephemeral=True)
            return
        
        data = load_data()
        user_id_str = str(user_id)
        
        if user_id_str not in data:
            data[user_id_str] = {
                'name': interaction.user.name,
                'aura': 0,
                'total_farms': 0,
                'daily_farms': 0,
                'last_reset': current_time
            }
        
        if current_time - data[user_id_str].get('last_reset', 0) > 86400:
            data[user_id_str]['daily_farms'] = 0
            data[user_id_str]['last_reset'] = current_time
        
        bonus = get_user_bonus(interaction.user)
        if data[user_id_str]['daily_farms'] >= bonus['daily_limit']:
            await interaction.response.send_message("Дневной лимит исчерпан! Завтра продолжишь", ephemeral=True, delete_after=3)
            return
        
        base_amount = random.randint(100, 500)
        farm_amount = int(base_amount * bonus['multiplier'])
        
        data[user_id_str]['aura'] += farm_amount
        data[user_id_str]['total_farms'] += 1
        data[user_id_str]['daily_farms'] += 1
        save_data(data)
        
        await interaction.response.send_message(
            f"Ты нафармил {farm_amount} Aura!\nБаланс: {data[user_id_str]['aura']} Aura\nДневной лимит: {data[user_id_str]['daily_farms']}/{bonus['daily_limit']}",
            ephemeral=False, delete_after=5
        )

# ========== КОМАНДЫ ==========
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
        await ctx.send("Ты еще не фармил, Используй !farm_panel")
    else:
        bonus = get_user_bonus(ctx.author)
        await ctx.send(f"{ctx.author.name}, у тебя {data[user_id]['aura']} Aura\nМножитель: x{bonus['multiplier']}\nДневной лимит: {data[user_id].get('daily_farms', 0)}/{bonus['daily_limit']}")

@bot.command()
async def налоговая(ctx):
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    answer = a + b
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()
    
    await ctx.send(f"Налоговая проверка: сколько будет {a} + {b}? (у тебя 15 секунд)")
    
    try:
        msg = await bot.wait_for('message', timeout=15.0, check=check)
        if int(msg.content) == answer:
            await ctx.send("Проверка пройдена, Можешь продолжать фармить")
            tax_counter[ctx.author.id] = 0
        else:
            await ctx.send("Неправильно. Доступ к фарму заблокирован полторы минуты")
            last_click[ctx.author.id] = time.time() + 90
    except asyncio.TimeoutError:
        await ctx.send("Время вышло попробуй снова через !налоговая")

@bot.command()
async def бизнесы(ctx):
    embed = discord.Embed(title="Бизнесы", color=discord.Color.gold())
    
    for biz_id, biz in businesses.items():
        embed.add_field(
            name=f"{biz['emoji']} {biz['name']}",
            value=f"Цена: {biz['price']} Aura\nДоход: {biz['income']} Aura/час\nКуплю: !купить_бизнес {biz_id}",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command()
async def купить_бизнес(ctx, biz_id: str):
    if biz_id not in businesses:
        await ctx.send("Такого бизнеса нет")
        return
    
    biz = businesses[biz_id]
    user_id = str(ctx.author.id)
    data = load_data()
    biz_data = load_businesses()
    
    if user_id not in data or data[user_id]['aura'] < biz['price']:
        await ctx.send(f"Недостаточно Aura, Нужно {biz['price']}")
        return
    
    if user_id not in biz_data:
        biz_data[user_id] = []
    
    for b in biz_data[user_id]:
        if b['id'] == biz_id:
            await ctx.send("У тебя уже есть этот бизнес")
            return
    
    biz_data[user_id].append({
        'id': biz_id,
        'name': biz['name'],
        'last_collect': time.time()
    })
    
    data[user_id]['aura'] -= biz['price']
    save_data(data)
    save_businesses(biz_data)
    
    await ctx.send(f"Ты купил {biz['name']}! Используй !собрать_доход")

@bot.command()
async def собрать_доход(ctx):
    user_id = str(ctx.author.id)
    biz_data = load_businesses()
    data = load_data()
    
    if user_id not in biz_data or not biz_data[user_id]:
        await ctx.send("У тебя нет бизнесов, Купи через !бизнесы")
        return
    
    total_income = 0
    current_time = time.time()
    updated_biz = []
    
    for biz in biz_data[user_id]:
        biz_info = businesses[biz['id']]
        time_passed = current_time - biz['last_collect']
        
        if time_passed >= biz_info['cooldown']:
            cycles = int(time_passed / biz_info['cooldown'])
            income = biz_info['income'] * cycles
            total_income += income
            biz['last_collect'] = current_time
            updated_biz.append(biz)
        else:
            updated_biz.append(biz)
    
    if total_income > 0:
        bonus = get_user_bonus(ctx.author)
        total_income = int(total_income * bonus['multiplier'])
        
        data[user_id]['aura'] += total_income
        save_data(data)
        save_businesses({user_id: updated_biz})
        
        hours_left = int((biz_info['cooldown'] - (current_time - biz['last_collect'])) / 3600) if not updated_biz else 0
        await ctx.send(f"Ты собрал {total_income} Aura с бизнесов (x{bonus['multiplier']} от роли)!")
    else:
        next_time = int((biz_info['cooldown'] - (current_time - biz['last_collect'])) / 60)
        await ctx.send(f"Ещё рано собирать доход! Подожди {next_time} минут")

# ========== МАГАЗИН РОЛЕЙ ==========
shop_items = {
    'fonker': {
        'name': 'Фонкер',
        'price': 10000,
        'description': 'Роль настоящего ценителя Пхонка',
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

@bot.command()
async def магазин(ctx):
    embed = discord.Embed(title="Магазин ролей", description="Тут за ауру покупаешь роли йоу", color=discord.Color.gold())
    for item_id, item in shop_items.items():
        embed.add_field(
            name=item['name'],
            value=f"Цена: {item['price']} Aura\n{item['description']}\nКупить: !купить_роль {item_id}",
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command()
async def купить_роль(ctx, item_id: str):
    item_id = item_id.lower()
    if item_id not in shop_items:
        await ctx.send("Такого товара нет, Смотри !магазин")
        return
    
    item = shop_items[item_id]
    data = load_data()
    user_id = str(ctx.author.id)
    
    if user_id not in data or data[user_id]['aura'] < item['price']:
        await ctx.send(f"Недостаточно Aura! Нужно {item['price']}")
        return
    
    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send("У бота нет прав выдавать роли")
        return
    
    role = discord.utils.get(ctx.guild.roles, name=item['role_name'])
    if not role:
        try:
            role = await ctx.guild.create_role(name=item['role_name'], color=item['color'], reason="Магазин")
        except:
            await ctx.send("Не могу создать роль. Проверь права")
            return
    
    if role.position >= ctx.guild.me.top_role.position:
        await ctx.send(f"Роль бота должна быть на боте {item['role_name']}!")
        return
    
    try:
        await ctx.author.add_roles(role)
    except:
        await ctx.send("Не могу выдать роль")
        return
    
    data[user_id]['aura'] -= item['price']
    save_data(data)
    
    await ctx.send(f"Ты купил роль {item['name']}! Остаток: {data[user_id]['aura']} Aura")

# ========== ЗАПУСК ==========
@bot.event
async def on_ready():
    print(f'Бот {bot.user} запущен!')
    print(f'Бот на серверах: {len(bot.guilds)}')
    print(f'Бизнесов: {len(businesses)}')
    print(f'Ролей с бонусами: {len(role_bonuses)}')
    print(f'Команды: !farm_panel, !balance, !налоговая, !бизнесы, !купить_бизнес, !собрать_доход, !магазин, !купить_роль')

bot.run(os.getenv('TOKEN'))