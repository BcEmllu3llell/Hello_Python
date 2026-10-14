import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()

# Каталог магазина
PRODUCTS = {
    "lemons": {
        "name": "🍋 Лимоны",
        "price": 100,
        "currency": "BTC",
        "description": "Свежие лимоны с ярким цитрусовым вкусом.",
    },
    "apples": {
        "name": "🍎 Яблоки",
        "price": 399,
        "currency": "EUR",
        "description": "Сочные яблоки для любителей фруктов.",
    },
    "bananas": {
        "name": "🍌 Бананы",
        "price": 5,
        "currency": "EUR",
        "description": "Сладкие бананы на каждый день.",
    },
}

# Корзины пользователей хранятся в памяти
carts = {}


def get_cart(user_id: int) -> dict:
    return carts.setdefault(user_id, {})


def format_price(price: float, currency: str) -> str:
    if currency == "BTC":
        return f"{price:g} BTC"
    return f"{price:.2f} €"


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🍋 Лимоны",
                    callback_data="product:lemons",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🍎 Яблоки",
                    callback_data="product:apples",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🍌 Бананы",
                    callback_data="product:bananas",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🛒 Моя корзина",
                    callback_data="cart",
                )
            ],
        ]
    )


def product_keyboard(product_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Добавить в корзину",
                    callback_data=f"add:{product_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Вернуться в каталог",
                    callback_data="catalog",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🛒 Моя корзина",
                    callback_data="cart",
                )
            ],
        ]
    )


def cart_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🍋 Добавить лимоны",
                    callback_data="add:lemons",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🍎 Добавить яблоки",
                    callback_data="add:apples",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🍌 Добавить бананы",
                    callback_data="add:bananas",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑️ Очистить корзину",
                    callback_data="clear_cart",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📦 Оформить заказ",
                    callback_data="checkout",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ В каталог",
                    callback_data="catalog",
                )
            ],
        ]
    )


def payment_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="₿ Оплата Bitcoin",
                    callback_data="pay:btc",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💶 Оплата в евро",
                    callback_data="pay:eur",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Вернуться в корзину",
                    callback_data="cart",
                )
            ],
        ]
    )


def render_cart(user_id: int) -> str:
    cart = get_cart(user_id)

    if not cart:
        return (
            "🛒 <b>Ваша корзина пуста</b>\n\n"
            "Выберите товары в каталоге, "
            "чтобы добавить их сюда."
        )

    lines = ["🛒 <b>Ваша корзина</b>\n"]
    totals = {}

    for product_id, quantity in cart.items():
        product = PRODUCTS[product_id]
        name = product["name"]
        price = product["price"]
        currency = product["currency"]
        subtotal = price * quantity

        lines.append(
            f"{name}\n"
            f"Количество: {quantity}\n"
            f"Цена за единицу: {format_price(price, currency)}\n"
            f"Сумма: {format_price(subtotal, currency)}\n"
        )

        totals[currency] = totals.get(currency, 0) + subtotal

    lines.append("━━━━━━━━━━━━━━")
    lines.append("<b>Итого:</b>")

    for currency, total in totals.items():
        lines.append(format_price(total, currency))

    if len(totals) > 1:
        lines.append(
            "\nℹ️ В корзине товары с разными валютами. "
            "Окончательный расчёт будет настроен "
            "при подключении оплаты."
        )

    return "\n".join(lines)


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🛍️ <b>Добро пожаловать в наш магазин!</b>\n\n"
        "Здесь вы можете выбрать товары, добавить их "
        "в корзину и подготовить заказ.\n\n"
        "🍋 Лимоны — 100 BTC\n"
        "🍎 Яблоки — 399 €\n"
        "🍌 Бананы — 5 €\n\n"
        "👇 <b>Выберите интересующий вас товар:</b>",
        reply_markup=main_menu(),
        parse_mode="HTML",
    )


@dp.message(Command("catalog"))
async def catalog_command(message: Message):
    await message.answer(
        "🛍️ <b>Каталог товаров</b>\n\nВыберите товар:",
        reply_markup=main_menu(),
        parse_mode="HTML",
    )


@dp.message(Command("cart"))
async def cart_command(message: Message):
    await message.answer(
        render_cart(message.from_user.id),
        reply_markup=cart_keyboard(),
        parse_mode="HTML",
    )


@dp.callback_query(F.data == "catalog")
async def show_catalog(callback: CallbackQuery):
    await callback.message.answer(
        "🛍️ <b>Каталог товаров</b>\n\nВыберите товар:",
        reply_markup=main_menu(),
        parse_mode="HTML",
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("product:"))
async def show_product(callback: CallbackQuery):
    product_id = callback.data.split(":", 1)[1]
    product = PRODUCTS.get(product_id)

    if product is None:
        await callback.answer("Товар не найден.", show_alert=True)
        return

    text = (
        f"<b>{product['name']}</b>\n\n"
        f"{product['description']}\n\n"
        f"💰 Цена: "
        f"{format_price(product['price'], product['currency'])}\n\n"
        "Нажмите кнопку ниже, чтобы добавить товар "
        "в корзину."
    )

    await callback.message.answer(
        text,
        reply_markup=product_keyboard(product_id),
        parse_mode="HTML",
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("add:"))
async def add_product(callback: CallbackQuery):
    product_id = callback.data.split(":", 1)[1]

    if product_id not in PRODUCTS:
        await callback.answer("Товар не найден.", show_alert=True)
        return

    cart = get_cart(callback.from_user.id)
    cart[product_id] = cart.get(product_id, 0) + 1

    product = PRODUCTS[product_id]

    await callback.answer(
        f"{product['name']} добавлены в корзину!"
    )

    await callback.message.answer(
        f"✅ <b>Товар добавлен!</b>\n\n"
        f"{product['name']}\n"
        f"Количество: {cart[product_id]}\n"
        f"Цена: {format_price(product['price'], product['currency'])}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🛒 Открыть корзину",
                        callback_data="cart",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🛍️ Продолжить покупки",
                        callback_data="catalog",
                    )
                ],
            ]
        ),
        parse_mode="HTML",
    )


@dp.callback_query(F.data == "cart")
async def show_cart(callback: CallbackQuery):
    await callback.message.answer(
        render_cart(callback.from_user.id),
        reply_markup=cart_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@dp.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
    carts[callback.from_user.id] = {}

    await callback.message.answer(
        "🗑️ Корзина очищена.\n\n"
        "Вы можете выбрать новые товары в каталоге.",
        reply_markup=main_menu(),
    )
    await callback.answer("Корзина очищена.")


@dp.callback_query(F.data == "checkout")
async def checkout(callback: CallbackQuery):
    cart = get_cart(callback.from_user.id)

    if not cart:
        await callback.answer(
            "Сначала добавьте товары в корзину.",
            show_alert=True,
        )
        return

    await callback.message.answer(
        "📦 <b>Оформление заказа</b>\n\n"
        f"{render_cart(callback.from_user.id)}\n\n"
        "Выберите предполагаемый способ оплаты.\n\n"
        "⚠️ Сейчас доступен демонстрационный режим. "
        "Деньги пока не принимаются.",
        reply_markup=payment_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("pay:"))
async def payment_demo(callback: CallbackQuery):
    method = callback.data.split(":", 1)[1]

    if method == "btc":
        payment_name = "Bitcoin"
    elif method == "eur":
        payment_name = "евро"
    else:
        await callback.answer("Неизвестный способ оплаты.")
        return

    cart = get_cart(callback.from_user.id)

    if not cart:
        await callback.message.answer(
            "Корзина пуста. Сначала выберите товары.",
            reply_markup=main_menu(),
        )
        await callback.answer()
        return

    await callback.message.answer(
        "🧾 <b>Заказ подготовлен к оплате!</b>\n\n"
        f"Способ оплаты: {payment_name}\n\n"
        f"{render_cart(callback.from_user.id)}\n\n"
        "🛠️ <b>Следующий этап разработки:</b>\n"
        "подключение платёжного механизма, "
        "создание уникального заказа, получение "
        "платёжных реквизитов и автоматическая "
        "проверка поступления средств.\n\n"
        "Это демонстрация интерфейса. "
        "Оплата ещё не подключена, "
        "переводить деньги не нужно.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🛍️ Вернуться в магазин",
                        callback_data="catalog",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🛒 Вернуться в корзину",
                        callback_data="cart",
                    )
                ],
            ]
        ),
        parse_mode="HTML",
    )
    await callback.answer()


async def main():
    if not TOKEN:
        raise RuntimeError("Не задан BOT_TOKEN")

    bot = Bot(token=TOKEN)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
