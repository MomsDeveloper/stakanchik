from enum import Enum
from os import getenv

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.types import CallbackQuery
from deta import Base
from utils.logging import log_to_deta
from typing import Optional, TypedDict


class CocktailType(Enum):
    ALCOHOLIC = "Алкогольный"
    NON_ALCOHOLIC = "Безалкогольный"


class CocktailRecipe(TypedDict):
    name: str
    type: CocktailType
    recipe: str


router = Router()
database = Base("cocktails")

menu = [[InlineKeyboardButton(text="💳 Алкогольные напитки", callback_data="get_alco"),
         InlineKeyboardButton(text="💰 Безалкогольные напитки", callback_data="get_bezalco")],
        [InlineKeyboardButton(text="О нас", callback_data="about")],
        [InlineKeyboardButton(text="🔎 Помощь", callback_data="help")]]
menu_markup = InlineKeyboardMarkup(inline_keyboard=menu)

go_back = InlineKeyboardButton(text="Назад", callback_data="menu")

cocktail_recipes = database.fetch().items


class MenuCallback(CallbackData, prefix="menu"):
    pass


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


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Привет, {message.from_user.full_name}! Я бот для приготовления коктейлей 🍹", reply_markup=menu_markup)

# Menu command handler


@router.callback_query(MenuCallback.filter())
async def show_menu(query: CallbackQuery):
    await query.message.edit_text("Главное меню", reply_markup=menu_markup)


@router.callback_query(CocktailSelectCallback.filter())
async def select_cocktail(query: CallbackQuery, callback_data: CocktailSelectCallback):
    # Retrieve cocktail information from the database based on its name
    cocktail: Optional[CocktailRecipe] = database.get(
        callback_data.name)  # type: ignore
    if cocktail is not None:
        await query.message.edit_text(f"Информация о коктейле \"{callback_data.name}\":\n{cocktail['recipe']}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[go_back]]))
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
            ] + [[go_back]]
        )
    )


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
