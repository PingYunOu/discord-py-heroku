import re
import os
import random
import time
import pandas as pd
import matplotlib.pyplot as plt
import requests
import discord

from bs4 import BeautifulSoup
from discord.ext import commands, tasks

description = '''A bot auto post fantasy league dailey scoring leaders.'''
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='FAN ', description=description, intents=intents)
TOKEN = os.getenv("DISCORD_TOKEN")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}({bot.user.id})")

@bot.command()
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, num = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, num)) for r in range(rolls))
    await ctx.send(result)


# In[6]:


def nbaget(count):
#     get the url

    stat_page = requests.get(f'https://basketball.fantasysports.yahoo.com/nba/4577/players?status=ALL&pos=P&cut_type=33&stat1=S_L&myteam=0&sort=PTS&sdir=1&count={count}') 
    content = stat_page.content

# find the id by beautiful soup

    soup = BeautifulSoup(content, 'html.parser')
    table = soup.find('table')
    html_str = str(table)
    # covert html to dataframe

    data = pd.read_html(html_str)[0]
    data.columns=data.columns.droplevel()
    data['FanPts']=data['Fan Pts']
    data = data.loc[:,['Players','Roster Status','FanPts','FGM','FGA','3PTM','FTM','FTA','PTS','REB','AST','ST','BLK','TO']]
    for i in range(len(data)):
        play=re.findall(r'Notes? (.+)',data.iloc[i,0])[0]
        data.iloc[i,0]=play
    return data


# In[7]:
def get_colwidth(df):
    col_width = []
    for col in df:
        if col in ['Players', 'Roster Status']:
            temp = []
            for i in df[col]:
                temp.append(len(str(i)))
            temp = max(temp)
            if col == 'Players':
                temp = 0.6*temp
        else:
            temp = len(col)
        col_width.append(temp)
    col_width = [i/sum(col_width) for i in col_width]
    return col_width

def draw_table(df):
    col_width = get_colwidth(df)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    fig, ax = plt.subplots(figsize=(15, 15)) # set size frame
    ax.xaxis.set_visible(False)  # hide the x axis
    ax.yaxis.set_visible(False)  # hide the y axis
    ax.set_frame_on(False)  # no visible frame, uncomment if size is ok
    tabla = pd.plotting.table(ax, df, colWidths=col_width, loc='center', cellLoc='left')#, colWidths=[0.17]*len(df.columns))  # where df is your data frame
    tabla.auto_set_font_size(False) # Activate set fontsize manually
    tabla.set_fontsize(12) # if ++fontsize is necessary ++colWidths
    tabla.scale(1.2, 1.2) # change size table
    plt.savefig('table.png', transparent=True)



def dailey_score(limit:int):
    count=0
    df=nbaget(count)
    count+=25
    while count<=limit:
        print(count)
        data=nbaget(count)
        df=pd.concat([df,data], ignore_index=True)
        count+=25
    #path='C://users/s9304/downloads/'
    
    draw_table(df)
    return df


# In[8]:

target_channel_id = 880452946029076490
@tasks.loop(minutes=10)
async def called_once_a_day():
    t = time.gmtime()
    hour = t.tm_hour
    minute = t.tm_min
    if hour == 7:
        if minute < 59 and minute >= 50:
            message_channel = bot.get_channel(target_channel_id)
            print(f"Got channel {message_channel}")
            df= dailey_score(limit=25)
            await message_channel.send(file=discord.File('table.png'))



called_once_a_day.start()
# In[9]:


if __name__ == "__main__":
    bot.run(TOKEN)
