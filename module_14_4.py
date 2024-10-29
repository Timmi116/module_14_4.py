from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from crud_functions import *

get_all_products()


api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Рассчитать'),
            KeyboardButton(text='Информация')
        ],
        [
            KeyboardButton(text='Купить')
        ]
    ], resize_keyboard=True
)

kb_inl = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Рассчитать', callback_data='calories')],
        [InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')]
    ]
)

kb_prod = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Vitamin-A', callback_data='product_buying'),
            InlineKeyboardButton(text='Vitamin-B', callback_data='product_buying'),
            InlineKeyboardButton(text='Vitamin-B2', callback_data='product_buying'),
            InlineKeyboardButton(text='Vitamin-C', callback_data='product_buying')
        ]
    ]
)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    gender = State()


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer(
        'Привет! Я бот помогающий твоему здоровью.'
        'Что бы посчитать суточную норму калорий нажмите - Рассчитать', reply_markup=kb
    )


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb_inl)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer(
        'Упрощенная формула Миффлина-Сан Жеора:'
        '\n 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161'
    )
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост в смантиметрах:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_growth(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес в киллограммах:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=float(message.text))
    data = await state.get_data()
    norm_cal = (10.0 * int(data['weight'])) + (6.25 * int(data['growth'])) - (5.0 * int(data['age'])) - 161.0
    await message.answer(f'Ваша норма калорий, необходимая для функцйонирования организма - {norm_cal} калорий.')
    await state.finish()


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    pictures = ['vitamin-A.jpg', 'vitamin-B.jpg', 'vitamin-B2.jpg', 'vitamin-C.jpg']
    products_list = get_all_products()
    count = 0

    for product in products_list:
        with open(pictures[count], "rb") as p:
            await message.answer_photo(
                p, f"Название: {product[1]} | Описание: {product[2]} | Цена: {product[3]}"
            )
        count += 1
    await message.answer("Выберите продукт для покупки:", reply_markup=kb_prod)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


@dp.message_handler()
async def all_messages(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
