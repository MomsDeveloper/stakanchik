from os import getenv

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.types import CallbackQuery

router = Router()
menu = [[InlineKeyboardButton(text="💳 Алкогольные напитки", callback_data="get_alco"),
    InlineKeyboardButton(text="💰 Безалкогольные напитки", callback_data="get_bezalco")],
[InlineKeyboardButton(text="О нас", callback_data="about")], 
[InlineKeyboardButton(text="🔎 Помощь", callback_data="help")]]
menu_markup = InlineKeyboardMarkup(inline_keyboard=menu)

cocktail_recipes = {
    "get_alco": [
        {"name": "Mojito", "recipe": "Muddle mint leaves, lime wedges, and simple syrup in a glass. Fill the glass with ice, add white rum, and top with soda water. Stir well and garnish with mint leaves and a lime wedge."},
        {"name": "Cosmopolitan", "recipe": "Shake vodka, triple sec, cranberry juice, and lime juice with ice. Strain into a martini glass and garnish with a lime wheel."},
    ],
    "get_bezalco": [
        {"name": "Virgin Mojito", "recipe": "Muddle mint leaves, lime wedges, and simple syrup in a glass. Fill the glass with ice and top with soda water. Stir well and garnish with mint leaves and a lime wedge."},
        {"name": "Mocktail", "recipe": "Shake pineapple juice, orange juice, and grenadine with ice. Strain into a glass filled with ice and garnish with a cherry and an orange slice."},
    ]
}
    
@router.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Привет, {message.from_user.full_name}! Я бот для приготовления коктейлей 🍹", reply_markup=menu_markup)

# Menu command handler
@router.message(Command("menu"))
async def show_menu(message: Message):
    await message.answer("Главное меню", reply_markup=menu_markup)


class GetAlcoCallback(CallbackData, prefix="get_alco"):
    pass

class GetBezalcoCallback(CallbackData, prefix="get_bezalco"):
    pass

class AboutCallback(CallbackData, prefix="about"):
    pass

class HelpCallback(CallbackData, prefix="help"):
    pass


@router.callback_query(GetAlcoCallback.filter())
async def get_alco(call: CallbackQuery):
    await call.message.answer("Алкогольные напитки")
    for cocktail in cocktail_recipes["get_alco"]:
        await call.message.answer(f"{cocktail['name']}\n{cocktail['recipe']}")
        
@router.callback_query(GetBezalcoCallback.filter())
async def get_bezalco(call: CallbackQuery):
    await call.message.answer("Безалкогольные напитки")
    for cocktail in cocktail_recipes["get_bezalco"]:
        await call.message.answer(f"{cocktail['name']}\n{cocktail['recipe']}")

@router.callback_query(AboutCallback.filter())
async def about(call: CallbackQuery):
    await call.message.answer("О нас")
    await call.message.answer("Мы - команда разработчиков, которая создала этого бота для вас. Надеемся, что вам понравится наше приложение!")
    
@router.callback_query(HelpCallback.filter())
async def help(call: CallbackQuery):
    await call.message.answer("Помощь")
    await call.message.answer("Если у вас возникли вопросы или проблемы с ботом, пожалуйста, напишите нам на почту: georgiy.khabner@mail.ru")
    