from enum import Enum
from os import getenv

from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import CallbackQuery
from deta import Base
from utils.logging import log_to_deta
from typing import Optional, TypedDict
from aiogram import Bot


class CocktailType(Enum):
    ALCOHOLIC = "Алкогольный"
    NON_ALCOHOLIC = "Безалкогольный"


class CocktailRecipe(TypedDict):
    name: str
    type: CocktailType
    recipe: str
    mark: float
    mark_count: int


router = Router()
database = Base("cocktails")
database_requests = Base("requests")

menu = [
    [
        InlineKeyboardButton(text="💳 Алкогольные напитки", callback_data="get_alco"),
        InlineKeyboardButton(text="💰 Безалкогольные напитки", callback_data="get_bezalco"),
    ],
    [
        InlineKeyboardButton(text="О нас", callback_data="about"),
    ],
    [
        InlineKeyboardButton(text="🔎 Помощь", callback_data="help"),
    ],
    [
        InlineKeyboardButton(text="Предложить коктейль", callback_data="offer"),
    ],
    [
        InlineKeyboardButton(text="Глубокий поиск", callback_data="deep_search"),
    ]

]

menu_markup = InlineKeyboardMarkup(inline_keyboard=menu)
go_back = InlineKeyboardButton(text="Назад", callback_data="menu")
# offer = InlineKeyboardButton(text="Предложить", callback_data="offer")
confirm_drink = InlineKeyboardButton(text="Подтвердить", callback_data="confirm_drink")
unconfirm_drink = InlineKeyboardButton(text="Отклонить", callback_data="unconfirm_drink")
mark_drink = InlineKeyboardButton(text="Поставить оценку", callback_data="mark_drink")

cocktail_recipes = database.fetch().items


class MenuCallback(CallbackData, prefix="menu"):
    pass

class MarkDrinkCallback(CallbackData, prefix="mark_drink"):
    pass

class OfferCallback(CallbackData, prefix="offer"):
    pass

class DeepSearchCallback(CallbackData, prefix="deep_search"):
    pass

class ConfirmOfferCallback(CallbackData, prefix="confirm_offer"):
    confirm: str


class ConfirmDrinkCallback(CallbackData, prefix="confirm_drink"):
    request_key: str

class UnconfirmDrinkCallback(CallbackData, prefix="unconfirm_drink"):
    request_key: str


class GetAlcoCallback(CallbackData, prefix="get_alco"):
    pass


class GetBezalcoCallback(CallbackData, prefix="get_bezalco"):
    pass


class AboutCallback(CallbackData, prefix="about"):
    pass


class HelpCallback(CallbackData, prefix="help"):
    pass


class CocktailSelectCallback(CallbackData, prefix="select_cocktail"):
    name: str

class MarkSelectCallback(CallbackData, prefix="mark_cocktail"):
    mark: int

class SelectCoctailTypeCallback(CallbackData, prefix="select_coctail_type"):
    type: str

class SelectFilterCallback(CallbackData, prefix="select_filter"):
    filter_name: str

class ResetFilterCallback(CallbackData, prefix="reset_filter"):
    pass

class ConfirmFilterCallback(CallbackData, prefix="confirm_filter"):
    pass

drinks_filter = [
    [
        InlineKeyboardButton(text="Горький ❌", callback_data=SelectFilterCallback(filter_name="bitter").pack()),
        InlineKeyboardButton(text="Сладкий ❌", callback_data=SelectFilterCallback(filter_name="sweet").pack()),
        InlineKeyboardButton(text="Кислый ❌", callback_data=SelectFilterCallback(filter_name="sour").pack()),
    ],
    [
        InlineKeyboardButton(text="Крепкий ❌", callback_data=SelectFilterCallback(filter_name="strong").pack()),
        InlineKeyboardButton(text="Фруктовый ❌", callback_data=SelectFilterCallback(filter_name="fruity").pack()),
    ],
    [
        InlineKeyboardButton(text="Сбросить фильтр", callback_data="reset_filter"),
        InlineKeyboardButton(text="Подтвердить фильтр", callback_data="confirm_filter"),
        InlineKeyboardButton(text="Назад", callback_data="menu")
    ]
]



@router.message(CommandStart())
async def start(message: Message):
    # print user's chat id
    await message.answer(f"Привет, {message.from_user.full_name}! Я бот для приготовления коктейлей 🍹", reply_markup=menu_markup)

# Menu command handler


@router.callback_query(MenuCallback.filter())
async def show_menu(query: CallbackQuery):
    await query.message.edit_text("Главное меню", reply_markup=menu_markup)


@router.callback_query(OfferCallback.filter())
async def offer_drink(query: CallbackQuery):
    await query.message.edit_text("Предложить коктейль")
    await query.message.answer("Хотите отправить рецепт коктейля на рассмотрение админу?", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Да", callback_data=ConfirmOfferCallback(confirm="yes").pack())],
            [InlineKeyboardButton(
                text="Нет", callback_data=ConfirmOfferCallback(confirm="no").pack())]
        ]
    ))

@router.callback_query(DeepSearchCallback.filter())
async def deep_search(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text("Глубокий поиск", reply_markup=InlineKeyboardMarkup(inline_keyboard=drinks_filter))

@router.callback_query(SelectFilterCallback.filter())
async def select_filter(query: CallbackQuery, callback_data: SelectFilterCallback, state: FSMContext):
    filter_map = {
        "bitter": "Горький",
        "sweet": "Сладкий",
        "sour": "Кислый",
        "strong": "Крепкий",
        "fruity": "Фруктовый"
    }

    filter_name = callback_data.filter_name
    if filter_name in filter_map:
        await state.update_data({filter_name: not (await state.get_data()).get(filter_name)})

    data = await state.get_data()
    buttons = [
        [InlineKeyboardButton(
            text=f"{filter_map[key]} {'✅' if data.get(key) else '❌'}",
            callback_data=SelectFilterCallback(filter_name=key).pack()
        ) for key in ["bitter", "sweet", "sour"]],
        [InlineKeyboardButton(
            text=f"{filter_map[key]} {'✅' if data.get(key) else '❌'}",
            callback_data=SelectFilterCallback(filter_name=key).pack()
        ) for key in ["strong", "fruity"]],
        [InlineKeyboardButton(text="Сбросить фильтр", callback_data="reset_filter")],
        [InlineKeyboardButton(text="Подтвердить фильтр", callback_data="confirm_filter")],
        [InlineKeyboardButton(text="Назад", callback_data="menu")]
    ]

    await query.message.edit_text("Фильтр установлен", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(ResetFilterCallback.filter())
async def reset_filter(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text("Фильтр сброшен", reply_markup=InlineKeyboardMarkup(inline_keyboard=drinks_filter))

@router.callback_query(ConfirmFilterCallback.filter())
async def confirm_filter(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    filters_list = ["bitter", "sweet", "sour", "strong", "fruity"]
    filters = {key: value for key, value in data.items() if key in filters_list and value}
    
    if filters:
        cocktail_recipes = database.fetch(filters).items
        await send_cocktail_menu(query.message, cocktail_recipes)
    await state.clear()

class OfferState(StatesGroup):
    wait_for_name = State()
    wait_for_type = State()
    wait_for_description = State()


@router.callback_query(ConfirmOfferCallback.filter())
async def confirm_offer(query: CallbackQuery, callback_data: ConfirmOfferCallback, state: FSMContext):
    if callback_data.confirm == "yes":
        # Получите рецепт коктейля от пользователя и отправьте админу
        await query.message.answer("Введите название коктейля")

        user_id = query.message.chat.id
        await state.update_data(user=user_id)
        await state.set_state(OfferState.wait_for_name)
    else:
        await query.message.answer("Отправка отменена")


def check_recipe(recipe: str):
    return True


@router.message(OfferState.wait_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.answer("Введите тип коктейля",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Алкогольный", callback_data=SelectCoctailTypeCallback(type="Алкогольный").pack()), InlineKeyboardButton(text="Безалкогольный", callback_data=SelectCoctailTypeCallback(type="Безалкогольный").pack())]]))
    await state.set_state(OfferState.wait_for_type)


@router.callback_query(OfferState.wait_for_type, SelectCoctailTypeCallback.filter())
async def process_type(query: CallbackQuery, callback_data: SelectCoctailTypeCallback, state: FSMContext):
    cocktail_type = callback_data.type
    await state.update_data(type=cocktail_type)
    await query.message.answer("Введите рецепт коктейля")
    await state.set_state(OfferState.wait_for_description)

@router.message(OfferState.wait_for_description)
async def process_recipe(message: Message, state: FSMContext, bot: Bot):
    # Отправьте рецепт коктейля админу

    recipe = message.text
    await state.update_data(recipe=recipe)

    current_state = await state.get_state()

    if current_state == OfferState.wait_for_description.state:
        data = await state.get_data()
        await message.answer(data["user"])
        database_requests.put(key=str(data["user"]), data={"name": data["name"], "type": data["type"], "recipe": data["recipe"], "user": data["user"]})
        await message.answer(data["user"])
        await bot.send_message(
            f"{getenv('ADMIN_ID')}", f"Пользователь {message.from_user.full_name} предложил {data['type']} коктейль {data['name']} с рецептом: {data['recipe']}", 
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Подтвердить", callback_data=ConfirmDrinkCallback(request_key=data["user"]).pack()),
                    InlineKeyboardButton(
                        text="Отклонить", callback_data=UnconfirmDrinkCallback(request_key=data["user"]).pack())
                ]
            ]))
        await state.clear()
        await message.answer("Рецепт коктейля отправлен администратору на рассмотрение.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[go_back]]))
    else:
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте еще раз.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[go_back]]))
        await state.clear()


@router.callback_query(ConfirmDrinkCallback.filter())
async def confirm_user_drink(query: CallbackQuery, callback_data: ConfirmDrinkCallback, bot: Bot):
    request_drink = database_requests.get(callback_data.request_key)
    
    if request_drink is not None:
        database.insert({"key": request_drink["name"], "name": request_drink["name"], "type": request_drink["type"], "recipe": request_drink["recipe"], "mark": "0", "mark_count": "0"})
        await query.message.edit_text("Коктейль успешно добавлен!", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[go_back]]))
        await bot.send_message(request_drink["user"], "Ваш коктейль был добавлен в базу данных.")
        database_requests.delete(callback_data.request_key)
    else:
        await query.message.edit_text("Ошибка: информация о коктейле не найдена.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[go_back]]))


@router.callback_query(UnconfirmDrinkCallback.filter())
async def unconfirm_user_drink(query: CallbackQuery, callback_data: UnconfirmDrinkCallback, bot: Bot):
    request_drink = database_requests.get(callback_data.request_key)
    if request_drink is not None:
        await query.message.edit_text("Коктейль не был добавлен.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[go_back]]))
        await bot.send_message(request_drink["user"], "Ваш коктейль не был добавлен в базу данных.")
        database_requests.delete(callback_data.request_key)
    else:
        await query.message.edit_text("Ошибка: информация о коктейле не найдена.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[go_back]]))

@router.callback_query(CocktailSelectCallback.filter())
async def select_cocktail(query: CallbackQuery, callback_data: CocktailSelectCallback, state: FSMContext):
    await state.update_data(name=callback_data.name)
    # Retrieve cocktail information from the database based on its name
    cocktail: Optional[CocktailRecipe] = database.get(
        callback_data.name)  # type: ignore
    if cocktail is not None:
        await query.message.edit_text(f"Информация о коктейле \"{callback_data.name}\":\n{cocktail['recipe']}\n Оценка: {cocktail['mark']}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[mark_drink, go_back]]))
    else:
        await query.message.edit_text("Извините, информация о коктейле не найдена.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[go_back]]))


async def send_cocktail_menu(message: Message, cocktails: list):
    await message.edit_text(
        "Выберите коктейль:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=cocktail["name"],
                        callback_data=CocktailSelectCallback(
                            name=cocktail["name"]).pack(),
                    )
                ]
                for cocktail in cocktails
            ]  + [[go_back]]
        )
    )


@router.callback_query(MarkDrinkCallback.filter())
async def mark_user_drink(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text("Поставить оценку", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="1", callback_data=MarkSelectCallback(mark=1).pack()), 
            InlineKeyboardButton(
                text="2", callback_data=MarkSelectCallback(mark=2).pack()),
            InlineKeyboardButton(
                text="3", callback_data=MarkSelectCallback(mark=3).pack()),
            InlineKeyboardButton(
                text="4", callback_data=MarkSelectCallback(mark=4).pack()),
            InlineKeyboardButton(
                text="5", callback_data=MarkSelectCallback(mark=5).pack()),
        ]] + [[go_back]]))
    
@router.callback_query(MarkSelectCallback.filter())
async def mark_drink_db(query: CallbackQuery, callback_data: MarkSelectCallback, state: FSMContext):
    state_data = await state.get_data()
    cocktail: Optional[CocktailRecipe] = database.get(
    state_data['name']) # type: ignore

    if cocktail is not None:
        new_mark= callback_data.mark
        cocktail['mark'] = (float(cocktail['mark'])*float(cocktail['mark_count'])+new_mark)/(float(cocktail['mark_count'])+1)
        cocktail['mark'] = round(cocktail['mark'], 2)
        cocktail['mark_count'] = int(cocktail['mark_count']) + 1
        database.put(cocktail)
        await query.message.edit_text("Оценка успешно поставлена!", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[go_back]]))
    else:
        await query.message.edit_text("Извините, информация о коктейле не найдена.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[go_back]]))

@router.callback_query(GetAlcoCallback.filter())
async def get_alco(query: CallbackQuery):
    await query.message.edit_text("Алкогольные напитки")
    cocktail_recipes = database.fetch({"type": "Алкогольный"}).items
    await log_to_deta(
        {"fetched_cocktails": cocktail_recipes}
    )
    await send_cocktail_menu(query.message, cocktail_recipes)


@router.callback_query(GetBezalcoCallback.filter())
async def get_bezalco(query: CallbackQuery):
    await query.message.edit_text("Безалкогольные напитки")
    cocktail_recipes = database.fetch({"type": "Безалкогольный"}).items
    await send_cocktail_menu(query.message, cocktail_recipes)


@router.callback_query(AboutCallback.filter())
async def about(query: CallbackQuery):
    await query.message.edit_text("О нас")
    await query.message.edit_text("Мы - команда разработчиков, которая создала этого бота для вас. Надеемся, что вам понравится наше приложение!", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[go_back]]))


@router.callback_query(HelpCallback.filter())
async def help(query: CallbackQuery):
    await query.message.edit_text("Помощь")
    await query.message.edit_text("Если у вас возникли вопросы или проблемы с ботом, пожалуйста, напишите нам на почту: georgiy.khabner@mail.ru", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[go_back]]))
