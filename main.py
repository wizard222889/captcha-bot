from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from datetime import datetime, timedelta
from aiogram import types
import captcha_generate
import configparser
import db

config = configparser.ConfigParser()
config.read('settings.ini')
token = config['bot']['token'] #токен бота
private_id = config['bot']['private_id'] #id приватного канала(чата)
admin_channel_id = config['bot']['admin_channel_id'] #канал, куда будут пересылаться информация о банах/получения ссылки.

storage = MemoryStorage()
bot = Bot(token=token)
dp = Dispatcher(bot, storage=storage)

# для первого запуска бота(ДАЛЬШЕ ЗАКОММЕНТИРОВАТЬ). Если заново хотите создать БД
#db.insert_table()

class Check_captcha(StatesGroup):
    answer = State()


class InChannel(BoundFilter):
    async def check(self, message: types.Message):
        user_channel_status = await bot.get_chat_member(chat_id=private_id, user_id=message.from_user.id)
        if user_channel_status.status == "member" or user_channel_status.status == "creator" or user_channel_status.status == "administrator":
            return True
        else:
            return False

# Определить id канала
# @dp.channel_post_handler()
# async def find_id_channel(message: types.Message):
#     print(f'ID канал {message.chat.title}: {message.chat.id}')

# Определить id чата
# @dp.message_handler()
# async def find_id_chat(message: types.Message):
#     print(f'ID чата {message.chat.title}: {message.chat.id}')


@dp.message_handler(InChannel(), content_types=types.ContentType.ANY)
async def in_channel(message: types.Message):
    if message.chat.type == 'private':
        await message.answer('Вы уже в канале!')


@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.answer(f'Привет, {message.from_user.username}. Для получения ссылки реши /captcha')


@dp.message_handler(commands='captcha')
async def check_captcha(message: types.Message):
    timeout = db.gate_timeout(message.from_user.id)
    now = str(datetime.now())
    print(now)
    if timeout and timeout > now:
        await message.answer('Вы заблокированы')
    else:
        if db.gate_user(message.from_user.id):
            db.delete_user(message.from_user.id)
        correct_capthca = captcha_generate.captca(message.from_user.id)
        with open(f'captcha{message.from_user.id}.png', 'rb') as photo:
            await bot.send_photo(message.from_user.id, photo)
        captcha_generate.delete_captcha(message.from_user.id)
        db.insert_user(message, correct_capthca)
        # await message.answer(await generate_invite())
        await Check_captcha.answer.set()


@dp.message_handler(state=Check_captcha.answer)
async def verify(message: types.Message, state: FSMContext):
    correct_captcha = db.gate_captcha(message.from_user.id)
    if message.text != correct_captcha:
        pop = db.gate_pop(message.from_user.id)
        if pop - 1 == 0:
            timeout = datetime.now() + timedelta(hours=2)
            db.update_db_user_timeout(message.from_user.id, timeout)
            await message.answer('Вы заблокированы на 2 часа')
            await bot.send_message(chat_id=admin_channel_id, text=f'Пользователь {message.from_user.username} был заблокирован на 2 часа\
                                   ID пользователя: {message.from_user.id}')
            await state.finish()
        else:
            db.update_db_user_pop(message.from_user.id, pop - 1)
            await message.answer(f'Неправильно, у вас осталось {db.gate_pop(message.from_user.id)} попыток')
            correct_capthca_2 = captcha_generate.captca(message.from_user.id)
            with open(f'captcha{message.from_user.id}.png', 'rb') as photo:
                await bot.send_photo(message.from_user.id, photo)
            captcha_generate.delete_captcha(message.from_user.id)
            db.update_db_user_captcha(
                message.from_user.id, captcha=correct_capthca_2)
    else:
        await message.answer(f'Вот ссылка: {await generate_invite()} ')
        await bot.send_message(chat_id=admin_channel_id, text=f'Пользователь {message.from_user.username} получил ссылку на канал\
                                   ID пользователя: {message.from_user.id}')
        db.delete_user(message.from_user.id)
        await state.finish()


async def generate_invite():
    link = await bot.create_chat_invite_link(private_id, member_limit=1)
    return link.invite_link

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
