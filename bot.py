import logging
from aiogram import Bot, Dispatcher, executor, types
from oyun import MafiaGame

TOKEN = "8300955831:AAFbm91Fy0tNM_S0Qp1vepQqyt-3jhb4gjU"  # Güvenlik Uyarısı: Token doğrudan kodda saklanmamalı, ortam değişkenleri kullanılmalı.

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

game = MafiaGame(bot)

@dp.message_handler(commands=['start', 'basla'])
async def cmd_start(msg: types.Message):
    await msg.answer("🤖 Mafia oyununa xoş gəlmisiniz!\nYeni oyun başlatmaq üçün /oyun yazın.")

@dp.message_handler(commands=['oyun'])
async def cmd_oyun(msg: types.Message):
    await game.new_game(msg)

@dp.message_handler(commands=['qosul'])
async def cmd_qosul(msg: types.Message):
    await game.join(msg)

@dp.message_handler(commands=['basla_oyun'])
async def cmd_basla_oyun(msg: types.Message):
    await game.start_game(msg)

@dp.message_handler(commands=['rolum'])
async def cmd_rolum(msg: types.Message):
    await game.show_role(msg)

@dp.message_handler(commands=['sesver'])
async def cmd_sesver(msg: types.Message):
    await game.vote(msg)

@dp.message_handler(commands=['oyuncular'])
async def cmd_oyuncular(msg: types.Message):
    await game.show_players(msg)

@dp.message_handler(commands=['legv'])
async def cmd_legv(msg: types.Message):
    await game.cancel_game(msg)

@dp.message_handler(commands=['yardim'])
async def cmd_yardim(msg: types.Message):
    await msg.answer("""
📜 Komandalar:
/oyun - Yeni oyun yaradın
/qosul - Oyuna qoşulun
/basla_oyun - Oyunu başlatın
/rolum - Rolunuzu görün
/sesver @istifadeci - Kimisə öldürmək üçün səs verin
/oyuncular - Oyunçuların siyahısı
/legv - Oyunu ləğv edin
""")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
