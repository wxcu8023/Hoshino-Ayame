import random
from datetime import timedelta

from nonebot import on_command
from hoshino import util
from hoshino.res import R
from hoshino.service import Service, Privilege as Priv

# basic function for debug, not included in Service('chat')
@on_command('zai?', aliases=('在?', '在？', '在吗', '在么？', '在嘛', '在嘛？'))
async def say_hello(session):
    await session.send('はい！私はいつも貴方の側にいますよ！')

sv = Service('chat', manage_priv=Priv.SUPERUSER, visible=False)

@sv.on_command('沙雕机器人', aliases=('沙雕機器人',), only_to_me=False)
async def say_sorry(session):
    await session.send('ごめんなさい！嘤嘤嘤(〒︿〒)')

@sv.on_command('老婆', aliases=('waifu', 'laopo'), only_to_me=True)
async def chat_waifu(session):
    if not sv.check_priv(session.ctx, Priv.SUPERUSER):
        await session.send(R.img('laopo.jpg').cqcode)
    else:
        await session.send('mua~')

@sv.on_command('老公', only_to_me=True)
async def chat_laogong(session):
    await session.send('你给我滚！', at_sender=True)

@sv.on_command('mua', only_to_me=True)
async def chat_mua(session):
    await session.send('笨蛋~', at_sender=True)

@sv.on_command('来点星奏', only_to_me=False)
async def seina(session):
    await session.send(R.img('星奏.png').cqcode)

@sv.on_command('我有个朋友说他好了', aliases=('我朋友说他好了', ), only_to_me=False)
async def ddhaole(session):
    await session.send('那个朋友是不是你弟弟？')
    await util.silence(session.ctx, 30)

@sv.on_command('我好了', only_to_me=False)
async def nihaole(session):
    await session.send('不许好，憋回去！')
    await util.silence(session.ctx, 30)
	
@sv.on_command('炼铜', only_to_me=False)
async def liantong(session):
    await session.send('炼铜退散！！！！')
    await util.silence(session.ctx, 30)

# ============================================ #

@sv.on_keyword(('确实', '有一说一', 'u1s1', 'yysy'))
async def chat_queshi(bot, ctx):
    if random.random() < 0.15:
        await bot.send(ctx, R.img('确实.jpg').cqcode)

@sv.on_keyword(('会战', '刀'))
async def chat_clanba(bot, ctx):
    if random.random() < 0.0:
        await bot.send(ctx, R.img('我的天啊你看看都几点了.jpg').cqcode)

@sv.on_keyword(('内鬼'))
async def chat_neigui(bot, ctx):
    if random.random() < 0.17:
        await bot.send(ctx, R.img('内鬼.png').cqcode)

@sv.on_keyword(('夜夜'))
async def chat_yeye2(bot, ctx):
    if random.random() < 0.02:
        pic = random.randint(1, 3)
        await bot.send(ctx, R.img('yeye{pic}.jpg').cqcode)

@sv.on_keyword(('熬夜','通宵','这么晚','还不睡'))
async def chat_yeye4(bot, ctx):
    if random.random() < 0.05:
        await bot.send(ctx, R.img('aoye.jpg').cqcode)

@sv.on_keyword(('会战'))
async def chat_huizhan(bot, ctx):
    if random.random() < 0.02:
        pic = random.randint(1, 3)
        await bot.send(ctx, R.img('huizhan{pic}.jpg').cqcode)

@sv.on_keyword(('变态'))
async def chat_yeye8(bot, ctx):
    if random.random() < 0.05:
        await bot.send(ctx, R.img('biantai.jpg').cqcode)

@sv.on_keyword(('没钱','穷','穷死了','最穷'))
async def chat_yeye9(bot, ctx):
    if random.random() < 0.01:
        await bot.send(ctx, R.img('meiqian.jpg').cqcode)

@sv.on_keyword(('狗叫','我出货了','我狗了','我出了','我抽到了'))
async def chat_goujiao(bot, ctx):
    if random.random() < 0.05:
        await bot.send(ctx, R.img('goujiao.jpg').cqcode)

@sv.on_keyword(('大佬','带我'))
async def chat_dalao(bot, ctx):
    if random.random() < 0.05:
        await bot.send(ctx, R.img('dalao.jpg').cqcode)
