import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from cred import TOKEN, MAIN_CHANNEL, DELAY, ADMINS, EXTENSIONS
from aiogram.types import FSInputFile
from Database import DataBase

bot = Bot(token=TOKEN)
dp = Dispatcher()
print("bot started")


async def check(message: CallbackQuery, chatId: str = None):
    try:
        status = await bot.get_chat_member(chatId, message.from_user.id)
        return False if status.status == "left" else True
    except:
        return False


async def giftMessage(message: Message):
    await asyncio.sleep(DELAY)
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Я подписался. Хочу сессию!", callback_data="subscribe"))
    giftText = f'''{message.from_user.first_name}, если Вы не просто скачали подарок, но и подписались на мой канал, то для подписчиков у меня есть подарок - я дам обратную связь Вам, как руководителю, в рамках Диагностической сессии по итогам Опросника

Пройти Опросник <a href='https://forms.gle/hFEDJfsViUrckn4U6'>здесь</a>

Подписывайтесь на мой канал, если еще этого не сделали, и забирайте бесплатно <b>Диагностическую сессию</b>! ⬇️⬇️⬇️ '''

    await message.answer(text=giftText, reply_markup=kb.as_markup(), parse_mode="HTML", disable_web_page_preview=True)


@dp.message(Command("start"))
async def start(message: Message):
    await message.delete()
    userName = message.from_user.first_name
    startText = f"""Ваш подарок для лидеров команд здесь 🎁
{userName}, добрый день! Я Ольга Седакова
Я помогаю руководителям настроить эффективную работу в командах и почувствовать себя лидерами

Возьмите Ваш подарок здесь - https://t.me/sedakovacoach (в закрепленном сообщении в канале)

Познакомимся поближе?

Я в коучинге с 2019г., имею статус коуча PCC ICF
Как агент изменений выступаю в ролях:
• Executive-коуч
• Командный коуч
• Agile Coach

Более 800 часов коуч-сессий с руководителями проектных офисов, ИТ подразделений, директорами региональных отделений и VIP офисов банка, начальниками управлений и вице-президентами
Опыт проведения командного коучинга в компаниях JTI, Газпромбанк, ВТБ
В Executive-коучинге использую как коучинговые инструменты, так и инструменты НЛП
Выбор инструментария согласовываю с клиентом
При необходимости могу предложить консультацию по проектному менеджменту, Agile и групповым динамикам в команде

Обо мне также можно почитать на сайте www.olgasedakova.ru

Скорее забирайте Ваш подарок – нажмите кнопку"""

    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(url="https://t.me/sedakovacoach", text="Получить подарок", callback_data="subscribe"))

    await message.answer_photo(photo=FSInputFile("Photo/photo.jpg"), caption=startText[:1024],
                               reply_markup=kb.as_markup())
    await asyncio.create_task(giftMessage(message))


@dp.message(Command("send"))
async def makePost(message: Message):
    await message.delete()
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Подарок 🎁", callback_data="gift"))
    await bot.send_message(chat_id=MAIN_CHANNEL, text="Здесь Вы можете забрать свой подарок. Нажмите кнопку Подарок 🎁",
                           reply_markup=kb.as_markup())


# ---------------------------------Admin Panel---------------------------------#
@dp.message(Command("mailing"))
async def mailing(message: Message):
    if message.from_user.id in ADMINS:
        mailing = " ".join(message.text.split(" ")[1:])
        if "" != mailing:
            db = DataBase()
            usersIds: list = db.getUserIds()
            for id_ in usersIds:
                try:
                    await bot.send_message(chat_id=id_, text=mailing)
                except:
                    pass
            await message.answer(text="🟢 Рассылка успешно выполнена!")
        else:
            await message.answer(text="⚠️ Сообщение для рассылки не введено или введено некорректно")


@dp.message(Command("new_lead"))
async def uploadLeadMagnet(message: Message):
    await message.delete()
    try:
        file_ = await bot.get_file(message.document.file_id)
        assert file_.file_path.split(".")[-1] in EXTENSIONS
        files = os.listdir('./Document')
        for file in files:
            os.remove(os.path.join('./Document', file))
        await bot.download_file(file_.file_path, f'Document/lead.{file_.file_path.split(".")[-1]}')
        await message.answer(text="🟢 Лид-магнит успешно обновлён")
    except:
        await message.answer(text="⚠️ Отсутсвует файл для загрузки или файл имеет некорректное расширение")


# ---------------------------------Gift Check---------------------------------#
@dp.callback_query(F.data == "gift")
async def sendGift(callback: CallbackQuery):
    if not await check(callback, MAIN_CHANNEL):
        await callback.answer(show_alert=True, text="Для получения подарка подпишитесь на канал!")
    else:
        db = DataBase()
        db.addUserId(str(callback.from_user.id))
        lead = os.path.join('./Document', *os.listdir('./Document'))
        await callback.answer(show_alert=True, text="Ваш подарок был выслан в личные сообщения!!")
        await bot.send_document(chat_id=callback.from_user.id, document=FSInputFile(lead))


# ---------------------------------Subscribe Check---------------------------------#
@dp.callback_query()
async def checkMessage(callback: CallbackQuery):
    if not await check(callback, MAIN_CHANNEL):
        await callback.answer(show_alert=True, text="Вы ещё не подписались на канал!")
    else:
        text = f"{callback.from_user.first_name}, чтобы забронировать <b>Диагностическую сессию</b> (Kick-off meeting), \n" \
               f"выберите удобное для Вас время в календаре ⬇️⬇️⬇️\n" \
               f"<a href='https://olga-sedakova.reservio.com/'>Календарь</a> \n \n" \
               f"Если у Вас появились вопросы, со мной можно продолжить общение в чате WhatsApp"
        kb = InlineKeyboardBuilder().add(
            InlineKeyboardButton(url="https://wa.me/+79774916345", text="Перейти в WhatsApp"))
        await callback.message.answer(text=text, reply_markup=kb.as_markup(),
                                      parse_mode="HTML", disable_web_page_preview=True)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
