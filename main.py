import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import token                        # импортируем токен бота
from rateparser import get_parse_rate_main      # импортируем функцию для парсинга

storage = MemoryStorage()
bot = Bot(token=token)
dp = Dispatcher(bot, storage=storage)

# создаём три переменные
# с курсом из рублей в тенге,
# названием валюты,
# и курсом из тенге в рубли
raterubkz, rates_name, ratekzrub = 0, 0, 0  # см. строку 147

# создаём основную клавиатуру с тремя кнопками Курс, Перевести, Ссылки
keyboard1 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
keyboard1.add("Курс \U0001F4C8", "Перевести \U0001F503", "Ссылки \U0001F50E")

# создаём клавиатуру отмены
keyboard2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard2.add("Отмена \U0001F6AB")

# создаём инлайн клавиатуру для выбора с двумя кнопками 'Рубли в тенге' и 'Тенге в рубли',
# с коллбеками 'rubkz' и 'kzrub' соответственно
inline_rubkz_button = InlineKeyboardButton('Рубли в тенге', callback_data='rubkz')
inline_kzrub_button = InlineKeyboardButton('Тенге в рубли', callback_data='kzrub')
inline_keybord = InlineKeyboardMarkup().add(inline_rubkz_button, inline_kzrub_button)

# создаём инлайн клавиатуру с url пересылками на сайт с курсом валют и киви
url_button1 = InlineKeyboardButton(text='Курсы валют', url='https://mironline.ru/support/list/kursy_mir/')
url_button2 = InlineKeyboardButton(text='Спонсировать', url='qiwi.com/n/ABOBUS227')
urlkb = InlineKeyboardMarkup(row_width=1).add(url_button1, url_button2)


# создаём класс с двумя переменными для машины состояний
class Form(StatesGroup):
    choosing_rate1 = State()  # первое состояние для ответа на коллбек 'rubkz'
    choosing_rate2 = State()  # второе состояние для ответа на коллбек 'kzrub'


# хендлер для ответа на комманду '/start'
@dp.message_handler(commands="start")
async def start(message: types.Message):
    # выводим сообщение и вызываем основную клавиатуру
    await message.answer("Привет \U0001F919 \nЯ могу рассказать тебе актуальный курс и перевести любую сумму из тенге в рубли и наоборот!", reply_markup=keyboard1)


# хендлер для ответа на нажатие кнопки 'Ссылки'
@dp.message_handler(Text(equals="Ссылки \U0001F50E"))
async def urls(message: types.Message):
    # выводим сообщение с прикреплённой инлайн клавиатурой с url пересылками
    await message.answer('Полезные ссылки:', reply_markup=urlkb)


# хендлер для ответа на нажатие кнопки 'Курс'
@dp.message_handler(Text(equals="Курс \U0001F4C8"))
async def getparserate(message: types.Message):
    # вы
    await message.answer(str(rates_name) + '\n' + '1\U0001F1F7\U0001F1FA = ' + str(round(raterubkz, 4)) + "\U0001F1F0\U0001F1FF")


# хендлер для ответа на нажатие кнопки 'Перевести'
@dp.message_handler(Text(equals="Перевести \U0001F503"))
async def perevod(message: types.Message):
    # выводим сообщение с прикреплённой инлайн клавиатурой для выбора перевода валюты
    await message.answer("Выбирете вариант", reply_markup=inline_keybord)


# хендлер для ответа на коллбек 'rubkz'
@dp.callback_query_handler(text='rubkz')
async def perevodrubkz(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    # выводим сообщение, вызываем клавиатуру отмены
    await bot.send_message(callback_query.from_user.id, 'Введите сумму перевода', reply_markup=keyboard2)
    # переводим в состояние choosing_rate1 ождания ответа
    await Form.choosing_rate1.set()


# хендлер для ответа на коллбек 'kzrub'
@dp.callback_query_handler(text='kzrub')
async def perevodrubkz(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    # выводим сообщение, вызываем клавиатуру отмены
    await bot.send_message(callback_query.from_user.id, 'Введите сумму перевода', reply_markup=keyboard2)
    # переводим в состояние choosing_rate2 ождания ответа
    await Form.choosing_rate2.set()


# хендлер для ответа на нажатие кнопки 'Отмена'
@dp.message_handler(Text(equals="Отмена \U0001F6AB"), state='*')
async def cancel(message: types.Message, state: FSMContext):
    # завершаем все состояния
    await state.finish()
    # выводим сообщение и возвращаем основную клавиатуру
    await message.answer("Хорошо, нажми любую кнопку", reply_markup=keyboard1)


# хендлер для состояния choosing_rate1
@dp.message_handler(state=Form.choosing_rate1)
async def exhcange_func(message: types.Message, state: FSMContext):
    # честно, не знаю, что точно делают эти строки, полагаю ловят сообщение от пользователя
    async with state.proxy() as proxy:
        proxy['choosing_rate1'] = message.text
    # создаём исключение, чтобы при расчёте суммы перевода не крашился бот
    try:
        # переводим текст сообщения от пользователя во float
        number_of_rubles = float(message.text)
        # выводим посчитанную сумму и возвращаем основную клавиатуру
        await message.answer(str(round(raterubkz * number_of_rubles, 2)) + ' тенге', reply_markup=keyboard1)
    # если пользователь ввёл не число, вызываем исключение
    except Exception:
        # выводим сообщение и вызываем основную клавиатуру
        await message.answer('⚠Пожалуйста, введите сумму перевода одним числом, без букв и других символов⚠',
                             reply_markup=keyboard1)
    # завершаем состояние
    await state.finish()


# хендлер для состояния choosing_rate2
@dp.message_handler(state=Form.choosing_rate2)
async def exhcange_func(message: types.Message, state: FSMContext):
    # честно, не знаю, что точно делают эти строки, полагаю ловят сообщение от пользователя
    async with state.proxy() as proxy:
        proxy['choosing_rate2'] = message.text
    # создаём исключение, чтобы при расчёте суммы перевода не крашился бот
    try:
        # переводим текст сообщения от пользователя во float
        number_of_rubles = float(message.text)
        # выводим посчитанную сумму и возвращаем основную клавиатуру
        await message.answer(str(round(ratekzrub * number_of_rubles, 2)) + ' рублей', reply_markup=keyboard1)
    # если пользователь ввёл не число, вызываем исключение
    except Exception:
        # выводим сообщение и вызываем основную клавиатуру
        await message.answer('⚠Пожалуйста, введите сумму перевода одним числом, без букв и других символов⚠',
                             reply_markup=keyboard1)
    # завершаем состояние
    await state.finish()


# создаём функцию для автоматического парсинга
async def kzrate_update():
    global rates_name, raterubkz, ratekzrub     # объявляем глобальные переменные
    while True:
        # присваиваем имя валюты из функции get_parse_rate_main() (см. файл rateparser)
        rates_name = get_parse_rate_main()[0]
        # присваиваем курс из рублей в тенге из функции get_parse_rate_main() (см. файл rateparser)
        raterubkz = get_parse_rate_main()[1]
        # присваиваем курс из тенге в рубли из функции get_parse_rate_main() (см. файл rateparser)
        ratekzrub = get_parse_rate_main()[2]
        await asyncio.sleep(3600)


if __name__ == '__main__':
    asyncio.get_event_loop().create_task(kzrate_update())   # добавляем функцию kzrate_update() в луп
    executor.start_polling(dp)