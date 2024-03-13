import disnake

from disnake.ext import commands

import subprocess

import sys

import json

from datetime import datetime

try:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
except subprocess.CalledProcessError as e:
    print(f"Помилка | Сталася помилка під час встановлення залежностей: {e}")
    sys.exit(1)

moderation_only = 1215061455133614122  # id канала для модерации

with open('salary.json', 'r') as jf:
    salary_dict = json.load(jf)

with open('users_info.json', 'r') as jf:
    users_dict = json.load(jf)

with open('bot_token.txt', 'r') as jf:
    TOKEN = jf.read()
bot = commands.Bot(command_prefix='!', help_command=None, intents=disnake.Intents.all(),
                   test_guilds=[1183409537450004621])


def today_sum(user):
    today = datetime.today()
    today = today.strftime("%d.%m.%Y")
    if today in users_dict[user]:
        today_values = users_dict[user][today].values()
        return str(sum(today_values) * salary_dict[user]) + '$'
    return 0


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.slash_command()
async def track(ctx, hours: float):
    """Получаем количетсво рабочих часов"""
    today = datetime.today()
    today = today.strftime("%d.%m.%Y")
    name = ctx.author.name
    channel_name = ctx.channel.name
    if name in users_dict:
        if today in users_dict[name]:
            users_dict[name][today][channel_name] = hours
        else:
            users_dict[name][today] = {channel_name: hours}
    else:
        users_dict[name] = {today: {channel_name: hours}}
    with open('users_info.json', 'w') as jf:
        json.dump(users_dict, jf, indent=4)
    display_name = ctx.author.display_name

    await ctx.send(f"{display_name}: {hours}ч.", ephemeral=True)


@bot.slash_command()
@commands.default_member_permissions(manage_guild=True, moderate_members=True)
async def info(ctx, user: disnake.User, start_date, end_date):
    """Выводит информацию про user"""
    embed = disnake.Embed(
        title=user.display_name,
        description=f"Статистика {start_date}-{end_date}",
        color=disnake.Colour.yellow(),
    )
    if user.name in users_dict:
        if user.name in salary_dict:
            month_salary = 0
            month_hours = 0.0
            start_date = datetime.strptime(start_date, "%d.%m.%Y")
            end_date = datetime.strptime(end_date, "%d.%m.%Y")
            for k, v in users_dict[user.name].items():
                k_d = datetime.strptime(k, "%d.%m.%Y")
                if start_date <= k_d <= end_date:
                    month_hours+=  float(sum(v.values()))
                    month_salary += float(sum(v.values())) * salary_dict[user.name]
            today = datetime.strptime(datetime.today().strftime("%d.%m.%Y"), "%d.%m.%Y")
            if start_date <= today <= end_date:
                today_salary = today_sum(user.name)
                embed.add_field(name='Total day', value=today_salary, inline=True)
            embed.add_field(name='Total month', value=str(month_salary) + '$', inline=True)
            embed.add_field(name='Часовая оплата', value=str(salary_dict[user.name]) + '$')
            embed.add_field(name='Всего часов', value=round(month_hours, 3), inline=True)
            for k, v in users_dict[user.name].items():
                line = ''
                k_d = datetime.strptime(k, "%d.%m.%Y")
                if start_date <= k_d <= end_date:
                    month_salary += sum(v.values()) * salary_dict[user.name]
                    for k_1, v_1 in v.items():
                        if v_1 != 0:
                            line += f'{k_1}: {v_1} ч.\n'
                    if len(line) != 0:
                        embed.add_field(name=k, value=line, inline=False)
            if ctx.channel.id != moderation_only:
                await ctx.send("Сообщение отправлено в moderation only", ephemeral=True)
                channel = bot.get_channel(moderation_only)
                await channel.send(embed=embed)
            else:
                await ctx.send(embed=embed)
        else:
            await ctx.send(f"не установлена часовая оплата для {user.display_name}", ephemeral=True)
    else:
        await ctx.send(f"{user.display_name} ещё не разу не использовал командку /track", ephemeral=True)


@bot.slash_command()
async def my_info(ctx, start_date, end_date):
    """Выводит информацию про user"""
    embed = disnake.Embed(
        title="Ваша статистика",
        description=f"{start_date}-{end_date}",
        color=disnake.Colour.yellow(),
    )
    if ctx.author.name in users_dict:
        if ctx.author.name in salary_dict:
            month_salary = 0
            month_hours = 0.0
            start_date = datetime.strptime(start_date, "%d.%m.%Y")
            end_date = datetime.strptime(end_date, "%d.%m.%Y")
            for k, v in users_dict[ctx.author.name].items():
                k_d = datetime.strptime(k, "%d.%m.%Y")
                if start_date <= k_d <= end_date:
                    month_hours += sum(v.values())
                    month_salary += sum(v.values()) * salary_dict[ctx.author.name]
            today = datetime.strptime(datetime.today().strftime("%d.%m.%Y"), "%d.%m.%Y")
            if start_date <= today <= end_date:
                today_salary = today_sum(ctx.author.name)
                embed.add_field(name='Total day', value=today_salary, inline=True)
            embed.add_field(name='Total month', value=str(month_salary) + '$', inline=True)
            embed.add_field(name='Часовая оплата', value=str(salary_dict[ctx.author.name]) + '$',  inline=True)
            embed.add_field(name='Всего часов', value=month_hours, inline=True)

            for k, v in users_dict[ctx.author.name].items():
                line = ''
                k_d = datetime.strptime(k, "%d.%m.%Y")
                if start_date <= k_d <= end_date:
                    month_salary += sum(v.values()) * salary_dict[ctx.author.name]
                    for k_1, v_1 in v.items():
                        if v_1 != 0:
                            line += f'{k_1}: {v_1} ч.\n'
                    embed.add_field(name=k, value=line, inline=False)
            await ctx.send(embed=embed, ephemeral=True)
        else:
            await ctx.send(f"Не установлена часовая оплата для вас", ephemeral=True)
    else:
        await ctx.send(f"Вы ещё не разу не использовал командку /track", ephemeral=True)


@bot.slash_command()
@commands.default_member_permissions(manage_guild=True, moderate_members=True)
async def set_salary(ctx, user: disnake.User, value: float):
    """Установить зарплату для user"""
    salary_dict[user.name] = value
    with open('salary.json', 'w', encoding='utf-8') as jf:
        json.dump(salary_dict, jf, indent=4)
    if ctx.channel.id != moderation_only:
        await ctx.send("Сообщение отправлено в moderation only", ephemeral=True)
        channel = bot.get_channel(moderation_only)
        await channel.send(f"Установлена часовая оплата {value}$ для {user.display_name}")
    else:
        await ctx.send(f"Установлена часовая оплата {value}$ для {user.display_name}")


@bot.slash_command()
@commands.default_member_permissions(manage_guild=True, moderate_members=True)
async def edit_track(ctx, user: disnake.User, date, new_value: str):
    if user.name in users_dict:
        if date in users_dict[user.name]:
            if ctx.channel.name in users_dict[user.name][date]:
                if new_value.isdigit():
                    users_dict[user.name][date][ctx.channel.name] = float(new_value)
                elif new_value.strip() == "DEL":
                    del users_dict[user.name][date][ctx.channel.name]
                with open('users_info.json', 'w')as jf:
                    json.dump(users_dict, jf, indent=4)
                await ctx.send("Исправлено!", ephemeral=True)


@bot.slash_command()
async def help(ctx):
    await ctx.send("## Команды для пользывателя\n"
                   "*/track*\n"
                   "* Эта команда предназначена для сохранения количества часов которое вы потратили на задание. "
                   "Писать команду под "
                   "статьей на форуме.\n"
                   "* После ввода команды, укажите количество отработанных часов.\n"
                   "* Число можно писать как целое, так и с дробной частью.\n"
                   "* В случае ошибки при вводе числа, можно повторно использовать эту команду, чтобы скорректировать "
                   "значение.\n"
                   "* Если вам необходимо перезаписать значение за предыдущие дни, обратитесь к администратору.\n"
                   "*/my_info*\n"
                   "* Эта команда выводит вашу статистику за определенный период время.\n"
                   "* Для получения информации, укажите период в формате день.месяц.год - день.месяц.год.\n"
                   "* Пример: */my_info 08.03.2024 10.03.2024*\n"
                   "## Команды для администратора\n"
                   "*/set_salary*\n"
                   "* Команда чтобы установить часовую оплату для человека.\n"
                   "* Пример: */set_salary @User 5*\n"
                   "*/info*\n"
                   "* Выводит статистику человека.\n"
                   "* Пример: */info @User 08.03.2024 10.03.2024*\n"
                   "*/edit_track*\n"
                   "* Команда чтобы редактировать статистику человека за определённую дату по определёному заданию. "
                   "Писать под статьёй на "
                   "форуме.\n"
                   "* Пример: */edit_track @User 03.03.2024 3*\n"
                   "* Вместо нового значения(в прошлом примере это 3) можно написать *DEL*, тогда вы удалите "
                   "информацию по заданию из статистики")


bot.run(TOKEN)
