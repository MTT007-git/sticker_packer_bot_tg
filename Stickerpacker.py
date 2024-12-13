# Этот файл будет изменяться.
# Бот использует файлы "Stickerpacker.txt" и "log.txt" для работы.
# В репозитории предоставленны минимальные данные в них для правильной работы.
# Для работы кода вставьте токен в переменную TOKEN и id Вашего чата с ботом в переменную OWNER_CHAT (необязательно).
# Также нужно заменить все '_by_sticker_packer_bot' на '_by_username Вашего бота в Телеграме'

import telebot, os, cv2, sys, time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputSticker, InputFile, Message, User, CallbackQuery
from telebot.util import smart_split
from PIL import Image

lang: dict = {'Back': ['Back', 'Назад'], 'Edit stickerpacks': ['Edit stickerpacks', 'Редактировать стикерпаки'], 'Please clear your history and reload the bot using /start':  ['Please clear your history and reload the bot using /start', 'Пожалуйста, очистите историю и перезапустите бота с помощью /start'], ', welcome to Stickerpacker bot.I will help you create telegram stickerpacks.To start, send me an image/gif/sticker with corresponding emojis.Document format is recommended fo quality reasons.': [', welcome to Stickerpacker bot.\nI will help you create telegram stickerpacks.\n\nTo start, send me an image/gif/sticker with corresponding emojis.\nDocument format is recommended for quality reasons.', ', добро пожаловать в бота Стикерпакера.\nЯ помогу Вам создавать телеграм-стикерпаки.\n\nДля начала пришлите мне изображение/гифку/стикер с подходящими эмодзи.\nРекомендуется формат "документ" всвязи с качеством.'], 'You currently have no stickerpacks.': ['You currently have no stickerpacks.', 'У Вас пока что нет ни одного стикерпака.'], 'You have': ['You have', 'У Вас'], 'stickerpacks': ['stickerpacks', 'стикерпаков'], 'Message sent': ['Message sent', 'Сообщение отправлено.'], 'Could not send message': ['Could not send message', 'Не получилось отпавить сообщение'], 'No stickerpacks yet': ['No stickerpacks yet', 'Еще нет стикерпаков'], 'Delete sticker from pack': ['Delete sticker from stickerpack', 'Удалить стикер из стикерпака'], 'Delete stickerpack': ['Delete stickerpack', 'Удалить стикерпак'], 'Send me the sticker you want to delete.': ['Send me the sticker you want to delete.', 'Пришлите мне стикер, который хотите удалить.'], 'Which stickerpack do you want to delete?': ['Which stickerpack do you want to delete?', 'Какой стикерпак Вы хотите удалить?'], 'Please wait... (resizing)': ['Please wait... (resizing)', 'Пожалуйста, подождите... (масштабируем)'], 'Please wait... (making GIF)': ['Please wait... (making GIF)', 'Пожалуйста, подождите... (делаем GIF)'], 'Please wait... (converting to WEBM)': ['Please wait... (converting to WEBM)', 'Пожалуйста, подождите... (конвертируем в WEBM)'], 'Choose a name for your stickerpack': ['Choose a name for your stickerpack', 'Выберете название для своего стикерпака'], 'Choose the unique indentifier for your stickerpack': ['Choose the unique indentifier for your stickerpack', 'Выберете идентификатор для своего стикерпака'], 'It must start with a letter and must only contain letters from the English alphabet, numbers and underscores.No double underscores are allowed.Underscore at the end is not allowed.': ['It must start with a letter and must only contain letters from the English alphabet, numbers and underscores.\nNo double underscores are allowed.\nUnderscore at the end is not allowed.', 'Он должен начинаться с буквы и содержать только буквы английского алфавита, цифры и знаки подчеркивания.\nДвойные знаки подчеркивания не допускаются.\nВ конце не допускается добавление знаков подчеркивания.'], 'Create new stickerpack': ['Create new stickerpack', 'Создать новый стикерпак'], 'Add to': ['Add to', 'Добавить в'], 'Please send 1-20 emojis.': ['Please send 1-20 emojis.', 'Пожалуйста, пришлите 1-20 эмодзи.'], 'has_': ['', 'В '], 'has ': ['has ', ''], 'emojis - it has to be 1 - 20.': ['emojis - it has to be 1 - 20.', 'эмодзи - должно быть 1 - 20'], 'The unique identifier': ['The unique identifier', 'Идентификатор'], 'for your stickerpack': ['for your stickerpack', 'для Вашего стикерпака'], 'is invalid.': ['is invalid.', 'не подходит.'], 'Stickerpack with': ['Stickerpack with', 'Стикерпак с'], 'uid already exists.': ['uid already exists.', 'иднтификатором уже существует.'], 'stickerpack_': ['', 'В стикерпаке '], 'stickerpack only has 1 sticker.': ['stickerpack only has 1 sticker.', 'только 1 стикер.'], 'stickerpack__': ['', 'Стикерпак '], 'stickerpack is either not yours or was not made by stickerpacker bot.': ['stickerpack is either not yours or was not made by Stickerpacker bot.', 'либо не Ваш, либо не был сделан этим ботом.'], 'Cannot delete sticker from set': ['Cannot delete sticker from stickerpack', 'Не получилось удалить стикер из стикерпака'], 's elapsed': ['s elapsed', 'с прошло'], 's left': ['s left', 'с осталось'], 'NOTE: photo type is not recommended for better quality of stickers.': ['NOTE: photo type is not recommended to improve the quality of stickers.', 'ПРИМЕЧАНИЕ: для улучшения качества стикеров тип фото не рекомендуется.'], 'Please wait... (Waiting for the stickerpack to be created)': ['Please wait... (Waiting for the stickerpack to be created)', 'Пожалуйста, подождите... (Ждем, пока стикерпак создается)'], 'Please wait...': ['Please wait...', 'Пожалуйста, подождите...'], 'Error': ['Error', 'Ошибка']}

TIMEOUT: int = 3
TIMEOUT_LONG: int = 60

OWNER_CHAT: int = 0 # id чата со мной для команд, доступных только для меня

TOKEN: str = '' # токен от бота
bot = telebot.TeleBot(TOKEN, num_threads=100)

cb: str | None = None
last: dict = {}
new_packs: dict = {}
packs: dict = {}
queue: list[str] = []

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    test: bool = True
else:
    test: bool = False

def update_packs() -> None:
    global packs
    a: dict = {}
    with open('Stickerpacker.txt', 'r') as f:
        exec(f'a = {f.read()}', a)
    packs = a['a']

def set_packs() -> None:
    global packs
    with open('Stickerpacker.txt', 'w') as f:
        print(packs, file=f, end='')

def update_start(chatid: int, start: bool = False, msg: Message | None = None, from_user: User | None = None) -> None:
    global packs
    update_packs()
    markup = InlineKeyboardMarkup()
    if chatid in packs:
        if packs[chatid][0][4] == 0:
            markup.add(InlineKeyboardButton('RU', callback_data='lang_1'))
        elif packs[chatid][0][4] == 1:
            markup.add(InlineKeyboardButton('EN', callback_data='lang_0'))
        markup.add(InlineKeyboardButton(lang['Edit stickerpacks'][packs[chatid][0][4]], callback_data='edit'))
    else:
        markup.add(InlineKeyboardButton('RU', callback_data='lang_1'))
        markup.add(InlineKeyboardButton(lang['Edit stickerpacks'][0], callback_data='edit'))
    markup.add(InlineKeyboardButton('ᐯ', callback_data='ᐯ'))
    if chatid in packs:
        if start:
            try:
                bot.delete_messages(chatid, [packs[chatid][0][0], packs[chatid][0][1]])
            except Exception as ex:
                print(type(ex).__name__+':', ex)
                avt = time.time()
                while time.time()-avt < TIMEOUT:
                    try:
                        lst: Message = log(bot.send_message(chatid, lang['Please clear your history and reload the bot using /start'][packs[chatid][0][4]]))
                        break
                    except:
                        pass
                else:
                    print('Could not send message: timeout reached')
                delete_last(msg.chat.id, lst)
            if len(packs[chatid]) == 1:
                avt = time.time()
                while time.time()-avt < TIMEOUT:
                    try:
                        packs[chatid][0] = [log(bot.send_message(chatid, text=f'{msg.from_user.first_name}{lang[", welcome to Stickerpacker bot.I will help you create telegram stickerpacks.To start, send me an image/gif/sticker with corresponding emojis.Document format is recommended fo quality reasons."][packs[chatid][0][4]]}')).message_id, log(bot.send_message(chatid, text=lang['You currently have no stickerpacks.'][packs[chatid][0][4]], reply_markup=markup)).message_id, packs[chatid][0][2], packs[chatid][0][3] if packs[chatid][0][3] != None else from_user, packs[chatid][0][4]]
                        break
                    except:
                        pass
                else:
                    print('Could not send message: timeout reached')
            else:
                n = '\n'
                avt = time.time()
                while time.time()-avt < TIMEOUT:
                    try:
                        packs[chatid][0] = [log(bot.send_message(chatid, text=f'{msg.from_user.first_name}{lang[", welcome to Stickerpacker bot.I will help you create telegram stickerpacks.To start, send me an image/gif/sticker with corresponding emojis.Document format is recommended fo quality reasons."][packs[chatid][0][4]]}')).message_id, log(bot.send_message(chatid, text=f'{lang["You have"][packs[chatid][0][4]]} {len(packs[chatid])-1} {lang["stickerpacks"][packs[chatid][0][4]]}:\n{n.join([f"{i[0]}: t.me/addstickers/{i[1]}_by_sticker_packer_bot" for i in packs[chatid][1:]])}', reply_markup=markup)).message_id, packs[chatid][0][2], packs[chatid][0][3] if packs[chatid][0][3] != None else from_user, packs[chatid][0][4]]
                        break
                    except:
                        pass
                else:
                    print('Could not send message: timeout reached')
        else:
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    packs[chatid][0][0] = log(bot.edit_message_text(f'{packs[chatid][0][3]}{lang[", welcome to Stickerpacker bot.I will help you create telegram stickerpacks.To start, send me an image/gif/sticker with corresponding emojis.Document format is recommended fo quality reasons."][packs[chatid][0][4]]}', chatid, packs[chatid][0][0])).message_id
                    break
                except Exception as ex:
                    if str(ex) == 'A request to the Telegram API was unsuccessful. Error code: 400. Description: Bad Request: message is not modified: specified new message content and reply markup are exactly the same as a current content and reply markup of the message':
                        break
            else:
                print('Could not edit message: timeout reached')
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    if len(packs[chatid]) == 1:
                        packs[chatid][0][1] = log(bot.edit_message_text(lang['You currently have no stickerpacks.'][packs[chatid][0][4]], chatid, packs[chatid][0][1], reply_markup=markup)).message_id
                    else:
                        n = '\n'
                        packs[chatid][0][1] = log(bot.edit_message_text(f'{lang["You have"][packs[chatid][0][4]]} {len(packs[chatid])-1} {lang["stickerpacks"][packs[chatid][0][4]]}:\n{n.join([f"{i[0]}: t.me/addstickers/{i[1]}_by_sticker_packer_bot" for i in packs[chatid][1:]])}', chatid, packs[chatid][0][1], reply_markup=markup)).message_id
                    break
                except Exception as ex:
                    if str(ex) == 'A request to the Telegram API was unsuccessful. Error code: 400. Description: Bad Request: message is not modified: specified new message content and reply markup are exactly the same as a current content and reply markup of the message':
                        break
            else:
                print('Could not edit message: timeout reached')
    else:
        avt = time.time()
        while time.time()-avt < TIMEOUT:
            try:
                packs[chatid] = [[log(bot.send_message(chatid, text=f'{msg.from_user.first_name}{lang[", welcome to Stickerpacker bot.I will help you create telegram stickerpacks.To start, send me an image/gif/sticker with corresponding emojis.Document format is recommended fo quality reasons."][0]}')).message_id, log(bot.send_message(chatid, text=lang['You currently have no stickerpacks.'][0], reply_markup=markup)).message_id, [], from_user, 0]]
                break
            except:
                pass
        else:
            print('Could not send message: timeout reached')
    set_packs()

def progressbar(now: int | str, end: int | str, length: int = 20) -> str:
    try:
        return '|'+chr(9608)*int(length/(end/now))+chr(9612)*((length/(end/now))%1 > 0.4)+'   '*(length-(int(length/(end/now))+((length/(end/now))%1 > 0.4)))+f'|{str(int(now/end*100))}%|{str(now)}/{str(end)}|'
    except:
        return '|'+' '*length*3+f'|0%|0/{end}|'

def delete_last(chatid: int, lst: Message | None = None, msg: Message | None = None) -> None:
    global packs
    update_packs()
    if chatid not in packs:
        update_start(chatid, True)
    update_packs()
    if msg != None:
        packs[chatid][0][2] += [msg.message_id]
    if len(packs[chatid][0][2]) > 0:
        avt = time.time()
        while time.time()-avt < TIMEOUT:
            try:
                bot.delete_messages(chatid, packs[chatid][0][2])
                break
            except:
                pass
        else:
            print('Could not delete message: timeout reached')
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    bot.send_message(chatid, lang['Please clear your history and reload the bot using /start'][packs[chatid][0][4]])
                    break
                except:
                    pass
            else:
                print('Could not send message: timeout reached')
    if lst != None:
        if type(lst).__name__ == 'list':
            for i in lst:
                packs[chatid][0][2] += [i.message_id]
        else:
            packs[chatid][0][2] = [lst.message_id]
    else:
        packs[chatid][0][2] = []
    set_packs()

def log(msg: Message | str, chatid: int | None = None) -> Message | str:
    global error
    error = None
    a: str = ''
    if type(msg) == str:
        update_packs()
        a = str(packs[chatid][0][3])+': '+msg
    else:
        try:
            a = msg.from_user.first_name+': '+msg.text.replace('\n', '\n'+' '*(len(msg.from_user.first_name)+2))
        except:
            try:
                a = msg.from_user.first_name+': [Image/Document] '+msg.caption.replace('\n', '\n'+' '*(len(msg.from_user.first_name)+2))
            except:
                if msg.sticker:
                    a = msg.from_user.first_name+f': [Sticker:{msg.sticker.set_name}:{msg.sticker.emoji}]'
                else:
                    a = msg.from_user.first_name+': NO TEXT'
    print(a)
    with open('log.txt', 'a', encoding='utf-8') as f:
        print(a, file=f)
    return msg

@bot.message_handler(commands=['start'])
def start(msg: Message) -> None:
    update_start(msg.chat.id, True, msg, msg.from_user.first_name)
    log(msg)    
    delete_last(msg.chat.id, msg=msg)

@bot.message_handler(commands=['user'])
def send_user(msg: Message) -> None:
    global packs
    if msg.chat.id != OWNER_CHAT:
        text(msg)
        return
    markup = InlineKeyboardMarkup()
    update_packs()
    markup.add(InlineKeyboardButton(lang['Back'][packs[msg.chat.id][0][4]], callback_data='back'))
    log(msg)
    try:
        lst: Message = log(bot.send_message(msg.chat.id, '@'+bot.get_chat_member(msg.text.split(' ')[1], msg.text.split(' ')[1]).user.username, reply_markup=markup))
    except Exception as ex:
        lst: Message = log(bot.send_message(msg.chat.id, f'{lang["Error"][packs[msg.chat.id][0][4]]}:\n'+type(ex).__name__+': '+str(ex), reply_markup=markup))
    delete_last(msg.chat.id, lst, msg)

@bot.message_handler(commands=['msg'])
def send_msg(msg: Message) -> None:
    global packs
    if msg.chat.id != OWNER_CHAT:
        text(msg)
        return
    markup = InlineKeyboardMarkup()
    update_packs()
    markup.add(InlineKeyboardButton(lang['Back'][packs[msg.chat.id][0][4]], callback_data='back'))
    log(msg)
    avt = time.time()
    while time.time()-avt < TIMEOUT:
        try:
            lst: Message = log(bot.send_message(int(msg.text.split(' ')[1]), ' '.join(msg.text.split(' ')[2:]), reply_markup=markup))
            delete_last(int(msg.text.split(' ')[1]), lst)
            lst: Message = log(bot.send_message(msg.chat.id, lang['Message sent'][packs[msg.chat.id][0][4]], reply_markup=markup))
            break
        except:
            pass
    else:
        print('Could not send message: timeout reached')
        try:
            lst: Message = log(bot.send_message(int(msg.text.split(' ')[1]), ' '.join(msg.text.split(' ')[2:]), reply_markup=markup))
            delete_last(int(msg.text.split(' ')[1]), lst)
            lst: Message = log(bot.send_message(msg.chat.id, lang['Message sent'][packs[msg.chat.id][0][4]], reply_markup=markup))
        except Exception as ex:
            try:
                lst: Message = log(bot.send_message(msg.chat.id, f'{lang["Could not send message"][packs[msg.chat.id][0][4]]}:\n'+type(ex).__name__+': '+str(ex), reply_markup=markup))
            except:
                pass
    delete_last(msg.chat.id, lst, msg)

@bot.message_handler(commands=['see'])
def send_see(msg: Message) -> None:
    global packs
    if msg.chat.id != OWNER_CHAT:
        text(msg)
        return
    update_packs()
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(lang['Back'][packs[msg.chat.id][0][4]], callback_data='back'))
    log(msg)
    t: str = ''
    for chatid in packs:
        try:
            if len(packs[chatid]) == 1:
                t += f'{chr(183)} {packs[chatid][0][3]}: {lang["No stickerpacks yet"][packs[msg.chat.id][0][4]]}\n'
            else:
                n = '\n'
                t += f'{chr(183)} {packs[chatid][0][3]}:\n{n.join([f"  {i[0]}: t.me/addstickers/{i[1]}_by_sticker_packer_bot" for i in packs[chatid][1:]])}\n'
        except:
            pass
    avt = time.time()
    while time.time()-avt < TIMEOUT:
        try:
            lst: Message = log(bot.send_message(msg.chat.id, t, reply_markup=markup))
            break
        except:
            pass
    else:
        print('Could not send message: timeout reached')
    delete_last(msg.chat.id, lst, msg)

@bot.message_handler(commands=['log'])
def send_log(msg: Message) -> None:
    global packs
    if msg.chat.id != OWNER_CHAT:
        text(msg)
        return
    markup = InlineKeyboardMarkup()
    update_packs()
    markup.add(InlineKeyboardButton(lang['Back'][packs[msg.chat.id][0][4]], callback_data='back'))
    log(msg)
    lst: list[Message] = []
    with open('log.txt', 'r', encoding='utf-8') as f:
        a = f.read()
        a = '\n'.join(a.split('\n')[1:])[int(a.split('\n')[0]):]
        for i in smart_split(a)[:-1]:
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    lst += [bot.send_message(msg.chat.id, text=i)]
                    break
                except:
                    pass
            else:
                print('Could not send message: timeout reached')
        avt = time.time()
        while time.time()-avt < TIMEOUT:
            try:
                lst += [bot.send_message(msg.chat.id, text=smart_split(a)[-1], reply_markup=markup)]
                break
            except:
                pass
        else:
            print('Could not send message: timeout reached')
    delete_last(msg.chat.id, lst, msg)

@bot.message_handler(commands=['clrlog'])
def clr_log(msg: Message) -> None:
    if msg.chat.id != OWNER_CHAT:
        text(msg)
        return
    with open('log.txt', 'r', encoding='utf-8') as f:
        a = f.read()
    with open('log.txt', 'w', encoding='utf-8') as f:
        n = '\n'.join(a.split('\n')[1:])
        f.write(f'{len(n)}\n'+n)
    log(msg)
    delete_last(msg.chat.id, msg=msg)

@bot.message_handler(commands=['alllog'])
def all_log(msg: Message) -> None:
    if msg.chat.id != OWNER_CHAT:
        text(msg)
        return
    with open('log.txt', 'r', encoding='utf-8') as f:
        a = f.read()
    with open('log.txt', 'w', encoding='utf-8') as f:
        f.write('0\n'+'\n'.join(a.split('\n')[1:]))
    delete_last(msg.chat.id, msg=msg)
    send_log(msg)

@bot.callback_query_handler(func=lambda call: call.data == 'ᐯ')
def unwrap(call: CallbackQuery) -> None:
    global packs
    log('[ᐯ]', call.message.chat.id)
    bot.answer_callback_query(call.id)
    markup = InlineKeyboardMarkup()
    update_packs()
    markup.add(InlineKeyboardButton(lang['Back'][packs[call.message.chat.id][0][4]], callback_data='back'))
    avt = time.time()
    while time.time()-avt < TIMEOUT:
        try:
            lst: list[Message] = [log(bot.send_message(call.message.chat.id, f'{i[0]}: t.me/addstickers/{i[1]}_by_sticker_packer_bot')) for i in packs[call.message.chat.id][1:][:-1]]
            break
        except:
            pass
    else:
        print('Could not send message: timeout reached')
    avt = time.time()
    while time.time()-avt < TIMEOUT:
        try:
            lst += [log(bot.send_message(call.message.chat.id, f'{packs[call.message.chat.id][1:][-1][0]}: t.me/addstickers/{packs[call.message.chat.id][1:][-1][1]}_by_sticker_packer_bot', reply_markup=markup))]
            break
        except:
            pass
    else:
        print('Could not send message: timeout reached')
    delete_last(call.message.chat.id, lst)

@bot.callback_query_handler(func=lambda call: call.data == 'edit')
def edit(call: CallbackQuery) -> None:
    global packs
    markup = InlineKeyboardMarkup()
    update_packs()
    markup.add(InlineKeyboardButton(lang['Back'][packs[call.message.chat.id][0][4]], callback_data='back'))
    markup.add(InlineKeyboardButton(lang['Delete sticker from pack'][packs[call.message.chat.id][0][4]], callback_data='sticker_del'))
    markup.add(InlineKeyboardButton(lang['Delete stickerpack'][packs[call.message.chat.id][0][4]], callback_data='pack_del'))
    log('[Edit stickerpacks]', call.message.chat.id)
    avt = time.time()
    while time.time()-avt < TIMEOUT:
        try:
            lst: Message = log(bot.send_message(call.message.chat.id, f'{lang["Edit stickerpacks"][packs[call.message.chat.id][0][4]]}:', reply_markup=markup))
            break
        except:
            pass
    else:
        print('Could not send message: timeout reached')
    bot.answer_callback_query(call.id)
    delete_last(call.message.chat.id, lst)

@bot.callback_query_handler(func=lambda call: call.data[:5] == 'lang_')
def switch_lang(call: CallbackQuery) -> None:
    global packs
    if call.data[5:] == 0:
        log('[EN]', call.message.chat.id)
    else:
        log('[RU]', call.message.chat.id)
    bot.answer_callback_query(call.id)
    update_packs()
    packs[call.message.chat.id][0][4] = int(call.data[5:])
    set_packs()
    update_start(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == 'sticker_del')
def sticker_del(call: CallbackQuery) -> None:
    global cb, packs
    markup = InlineKeyboardMarkup()
    update_packs()
    markup.add(InlineKeyboardButton(lang['Back'][packs[call.message.chat.id][0][4]], callback_data='back'))
    log('[Delete sticker from pack]', call.message.chat.id)
    avt = time.time()
    while time.time()-avt < TIMEOUT:
        try:
            lst: Message = log(bot.send_message(call.message.chat.id, text=lang['Send me the sticker you want to delete.'][packs[call.message.chat.id][0][4]], reply_markup=markup))
            break
        except:
            pass
    else:
        print('Could not send message: timeout reached')
    cb = 'sticker_del'
    bot.answer_callback_query(call.id)
    delete_last(call.message.chat.id, lst)

@bot.callback_query_handler(func=lambda call: call.data == 'pack_del')
def pack_del(call: CallbackQuery) -> None:
    global packs
    update_packs()
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(lang['Back'][packs[call.message.chat.id][0][4]], callback_data='back'))
    log('[Delete stickerpack]', call.message.chat.id)
    if call.message.chat.id in packs:
        for i in range((len(packs[call.message.chat.id])-1)//2):
            markup.add(InlineKeyboardButton(f'{packs[call.message.chat.id][i*2+1][0]} ({packs[call.message.chat.id][i*2+1][1]})', callback_data=f'del_{packs[call.message.chat.id][i*2+1][1]}'), InlineKeyboardButton(f'{packs[call.message.chat.id][i*2+2][0]} ({packs[call.message.chat.id][i*2+2][1]})', callback_data=f'del_{packs[call.message.chat.id][i*2+2][1]}'))
        if len(packs[call.message.chat.id])%2 == 0:
            markup.add(InlineKeyboardButton(f'{packs[call.message.chat.id][len(packs[call.message.chat.id])-1][0]} ({packs[call.message.chat.id][len(packs[call.message.chat.id])-1][1]})', callback_data=f'del_{packs[call.message.chat.id][len(packs[call.message.chat.id])-1][1]}'))
    avt = time.time()
    while time.time()-avt < TIMEOUT:
        try:
            lst: Message = log(bot.send_message(call.message.chat.id, text=lang['Which stickerpack do you want to delete?'][packs[call.message.chat.id][0][4]], reply_markup=markup))
            break
        except:
            pass
    else:
        print('Could not send message: timeout reached')
    bot.answer_callback_query(call.id)
    delete_last(call.message.chat.id, lst)

@bot.callback_query_handler(func=lambda call: call.data[:3] == 'del')
def del_pack(call: CallbackQuery) -> None:
    global packs
    try:
        bot.delete_sticker_set(f'{call.data[4:]}_by_sticker_packer_bot')
    except:
        pass
    update_packs()
    for i in range(1, len(packs[call.message.chat.id])):
        if packs[call.message.chat.id][i][1] == call.data[4:]:
            del packs[call.message.chat.id][i]
            break
    set_packs()
    update_start(call.message.chat.id)
    log(f'[{call.data[4:]}]', call.message.chat.id)
    bot.answer_callback_query(call.id)
    delete_last(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data[:3] == 'add')
def add(call: CallbackQuery) -> None:
    global new_packs, packs, cb, queue
    a = {}
    exec('a = '+call.data[4:], a)
    a, b = a['a'], a['user_id']
    log(f'[Add to {a[0]} ({a[1]})]', call.message.chat.id)
    bot.answer_callback_query(call.id)
    new_packs_local: dict = new_packs.copy()
    update_packs()
    for i in range(len(packs[call.message.chat.id])):
        j = packs[call.message.chat.id][i]
        if j[1] == a[1]:
            num: int = j[2]+1
            packs[call.message.chat.id][i][2] += 1
            break
    else:
        print('Error')
        return
    set_packs()
    try:
        cb = None
        if new_packs_local[call.message.chat.id][4]:
            delete_last(call.message.chat.id)
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    lst = log(bot.send_message(call.message.chat.id, lang['Please wait...'][packs[call.message.chat.id][0][4]]))
                    break
                except:
                    pass
            else:
                print('Could not send message: timeout reached')
            with open(f'{call.message.chat.id}_{a[1]}_{num}.tgs', 'wb') as f:
                f.write(bot.download_file(bot.get_file(new_packs_local[call.message.chat.id][0].file_id).file_path))
            if a[1] in queue:
                avt = time.time()
                while time.time()-avt < TIMEOUT:
                    try:
                        lst = log(bot.edit_message_text(lang['Please wait... (Waiting for the stickerpack to be created)'][packs[call.message.chat.id][0][4]], call.message.chat.id, lst.message_id))
                        break
                    except:
                        pass
                else:
                    print('Could not edit message: timeout reached')
                while a[1] in queue:
                    pass
                update_packs()
                for i in packs[call.message.chat.id]:
                    if i[1] == a[1]:
                        break
                else:
                    os.remove(f'{call.message.chat.id}_{a[1]}_{num}.tgs')
                    avt = time.time()
                    while time.time()-avt < TIMEOUT:
                        try:
                            bot.delete_message(call.message.chat.id, lst.message_id)
                            break
                        except:
                            pass
                    else:
                        print('Could not delete message: timeout reached.')
                    return
            else:
                try:
                    lst = log(bot.edit_message_text(lang['Please wait...'][packs[call.message.chat.id][0][4]], call.message.chat.id, lst.message_id))
                except:
                    pass
            avt = time.time()
            while time.time()-avt < TIMEOUT_LONG:
                try:
                    with open(f'{call.message.chat.id}_{a[1]}_{num}.tgs', 'rb') as f:
                        bot.add_sticker_to_set(b, f'{a[1]}_by_sticker_packer_bot', new_packs_local[call.message.chat.id][1], sticker=InputSticker(InputFile(f), emoji_list=new_packs_local[call.message.chat.id][1], format='animated'))
                    break
                except:
                    pass
            else:
                print('Could not add sticker to stickerpack: timeout reached.')
            cb = None
            os.remove(f'{call.message.chat.id}_{a[1]}_{num}.tgs')
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    bot.delete_message(call.message.chat.id, lst.message_id)
                    break
                except:
                    pass
            else:
                print('Could not delete message: timeout reached.')
        elif new_packs_local[call.message.chat.id][3]:
            pb = progressbar(0, '...')
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    lst: Message = log(bot.send_message(call.message.chat.id, f'{lang["Please wait... (resizing)"][packs[call.message.chat.id][0][4]]}\n{pb}'))
                    break
                except:
                    pass
            else:
                print('Could not send message: timeout reached')
            delete_last(call.message.chat.id)
            with open(f'{call.message.chat.id}_{a[1]}_{num}.mp4', 'wb') as f:
                f.write(bot.download_file(bot.get_file(new_packs_local[call.message.chat.id][0].file_id).file_path))
            video_capture: cv2.VideoCapture = cv2.VideoCapture(f'{call.message.chat.id}_{a[1]}_{num}.mp4')
            still_reading, image = video_capture.read()
            frame_count: int = 0
            frames_all: int = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            if frames_all == 8:
                frames_all = 120
            frames = []
            while still_reading:
                cv2.imwrite(f'{call.message.chat.id}_{a[1]}_{num}.png', image)
                frame = Image.open(f'{call.message.chat.id}_{a[1]}_{num}.png')
                size = frame.size
                if size[1] > size[0]:
                    frames += [frame.resize((int(size[0]*(512/size[1])), 512))]
                else:
                    frames += [frame.resize((512, int(size[1]*(512/size[0]))))]
                still_reading, image = video_capture.read()
                frame_count += 1
                if pb.split('|')[1] != progressbar(frame_count, frames_all).split('|')[1]:
                    pb = progressbar(frame_count, frames_all)
                    try:
                        update_packs()
                        lst = bot.edit_message_text(f'{lang["Please wait... (resizing)"][packs[call.message.chat.id][0][4]]}\n{pb}', call.message.chat.id, lst.message_id)
                    except:
                        pass
                    else:
                        print('Could not edit message: timeout reached')
            frames_all = frame_count
            video_capture.release()
            os.remove(f'{call.message.chat.id}_{a[1]}_{num}.mp4')
            os.remove(f'{call.message.chat.id}_{a[1]}_{num}.png')
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    update_packs()
                    lst = log(bot.edit_message_text(lang['Please wait... (making GIF)'][packs[call.message.chat.id][0][4]], call.message.chat.id, lst.message_id))
                    break
                except:
                    pass
            else:
                print('Could not edit message: timeout reached')
            frames[0].save(f'{call.message.chat.id}_{a[1]}_{num}.gif', save_all=True, append_images=frames, duration=50, loop=0)
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    update_packs()
                    lst = log(bot.edit_message_text(f'{lang["Please wait... (converting to WEBM)"][packs[call.message.chat.id][0][4]]}\n{progressbar(0, int(packs["average_video_time"]*frames_all))}', call.message.chat.id, lst.message_id))
                    set_packs()
                    break
                except:
                    pass
            else:
                print('Could not edit message: timeout reached')
            os.system(f'start "Stickerpacker converter (tgradish)" /i /min tgradish convert -fr 20 -it 1 -t {len(frames)/20} -i {call.message.chat.id}_{a[1]}_{num}.gif')
            avt: float = time.time()
            pb: str = progressbar(0, int(packs["average_video_time"]*frames_all))
            while not os.path.exists(f'{call.message.chat.id}_{a[1]}_{num}.webm'):
                if progressbar(int(time.time()-avt), int(packs["average_video_time"]*frames_all)).split('|')[1] != pb.split('|')[1]:
                    try:
                        update_packs()
                        lst = bot.edit_message_text(f'{lang["Please wait... (converting to WEBM)"][packs[call.message.chat.id][0][4]]}\n{progressbar(int(time.time()-avt), int(packs["average_video_time"]*frames_all))}{int(time.time()-avt)}{lang["s elapsed"][packs[call.message.chat.id][0][4]]}|~{int(packs["average_video_time"]*frames_all)-int(time.time()-avt)}{lang["s left"][packs[call.message.chat.id][0][4]]}|', call.message.chat.id, lst.message_id)
                    except:
                        pass
                pb = progressbar(int(time.time()-avt), int(packs["average_video_time"]*frames_all))
            update_packs()
            packs['average_video_time'] = (packs['average_video_time']+(time.time()-avt)/frames_all)/2
            set_packs()
            if a[1] in queue:
                avt = time.time()
                while time.time()-avt < TIMEOUT:
                    try:
                        lst = log(bot.edit_message_text(lang['Please wait... (Waiting for the stickerpack to be created)'][packs[call.message.chat.id][0][4]], call.message.chat.id, lst.message_id))
                        break
                    except:
                        pass
                else:
                    print('Could not edit message: timeout reached')
                while a[1] in queue:
                    pass
                update_packs()
                for i in packs[call.message.chat.id]:
                    if i[1] == a[1]:
                        break
                else:
                    os.remove(f'{call.message.chat.id}_{a[1]}_{num}.gif')
                    os.remove(f'{call.message.chat.id}_{a[1]}_{num}.webm')
                    os.remove('ffmpeg2pass-0.log')
                    #os.remove('tmp')
                    avt = time.time()
                    while time.time()-avt < TIMEOUT:
                        try:
                            bot.delete_message(call.message.chat.id, lst.message_id)
                            break
                        except:
                            pass
                    else:
                        print('Could not delete message: timeout reached.')                    
                    return
            else:
                avt = time.time()
                while time.time()-avt < TIMEOUT:
                    try:
                        lst = log(bot.edit_message_text(lang['Please wait...'][packs[call.message.chat.id][0][4]], call.message.chat.id, lst.message_id))
                        break
                    except:
                        pass
                else:
                    print('Could not edit message: timeout reached')
            avt = time.time()
            while time.time()-avt < TIMEOUT_LONG:
                try:
                    with open(f'{call.message.chat.id}_{a[1]}_{num}.webm', 'rb') as f:
                        bot.add_sticker_to_set(b, f'{a[1]}_by_sticker_packer_bot', new_packs_local[call.message.chat.id][1], sticker=InputSticker(InputFile(f), emoji_list=new_packs_local[call.message.chat.id][1], format='video'))
                    break
                except:
                    pass
            else:
                print('Could not add sticker to stickerpack: timeout reached.')
            cb = None
            os.remove(f'{call.message.chat.id}_{a[1]}_{num}.gif')
            os.remove(f'{call.message.chat.id}_{a[1]}_{num}.webm')
            os.remove('ffmpeg2pass-0.log')
            #os.remove('tmp')
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    bot.delete_message(call.message.chat.id, lst.message_id)
                    break
                except:
                    pass
            else:
                print('Could not delete message: timeout reached.')
        else:
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    lst: Message = log(bot.send_message(call.message.chat.id, lang['Please wait... (resizing)'][packs[call.message.chat.id][0][4]]))
                    break
                except:
                    pass
            else:
                print('Could not send message: timeout reached')
            delete_last(call.message.chat.id)
            with open(f'{call.message.chat.id}_{a[1]}_{num}.png', 'wb') as f:
                f.write(bot.download_file(bot.get_file(new_packs_local[call.message.chat.id][0].file_id).file_path))
            img = Image.open(f'{call.message.chat.id}_{a[1]}_{num}.png')
            img.save(f'{call.message.chat.id}_{a[1]}_{num}.png')
            size = img.size
            if size[1] > size[0]:
                img = img.resize((int(size[0]*(512/size[1])), 512))
            else:
                img = img.resize((512, int(size[1]*(512/size[0]))))
            img.save(f'{call.message.chat.id}_{a[1]}_{num}.png')
            if a[1] in queue:
                avt = time.time()
                while time.time()-avt < TIMEOUT:
                    try:
                        lst = log(bot.edit_message_text(lang['Please wait... (Waiting for the stickerpack to be created)'][packs[call.message.chat.id][0][4]], call.message.chat.id, lst.message_id))
                        break
                    except:
                        pass
                else:
                    print('Could not edit message: timeout reached')
                while a[1] in queue:
                    pass
                update_packs()
                for i in packs[call.message.chat.id]:
                    if i[1] == a[1]:
                        break
                else:
                    os.remove(f'{call.message.chat.id}_{a[1]}_{num}.png')
                    avt = time.time()
                    while time.time()-avt < TIMEOUT:
                        try:
                            bot.delete_message(call.message.chat.id, lst.message_id)
                            break
                        except:
                            pass
                    else:
                        print('Could not delete message: timeout reached.')
                    return
            else:
                avt = time.time()
                while time.time()-avt < TIMEOUT:
                    try:
                        lst = log(bot.edit_message_text(lang['Please wait...'][packs[call.message.chat.id][0][4]], call.message.chat.id, lst.message_id))
                        break
                    except:
                        pass
                else:
                    print('Could not edit message: timeout reached')
            avt = time.time()
            while time.time()-avt < TIMEOUT_LONG:
                try:
                    with open(f'{call.message.chat.id}_{a[1]}_{num}.png', 'rb') as f:
                        bot.add_sticker_to_set(b, f'{a[1]}_by_sticker_packer_bot', new_packs_local[call.message.chat.id][1], sticker=InputSticker(InputFile(f), emoji_list=new_packs_local[call.message.chat.id][1], format='static'))
                    break
                except:
                    pass
            else:
                print('Could not add sticker to stickerpack: timeout reached.')
            cb = None
            delete_last(call.message.chat.id)
            os.remove(f'{call.message.chat.id}_{a[1]}_{num}.png')
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    bot.delete_message(call.message.chat.id, lst.message_id)
                    break
                except:
                    pass
            else:
                print('Could not delete message: timeout reached.')
    except Exception as ex:
        if os.path.exists(f'{call.message.chat.id}_{a[1]}_{num}.png'):
            os.remove(f'{call.message.chat.id}_{a[1]}_{num}.png')
        if os.path.exists(f'{call.message.chat.id}_{a[1]}_{num}.gif'):
            os.remove(f'{call.message.chat.id}_{a[1]}_{num}.gif')
        if os.path.exists(f'{call.message.chat.id}_{a[1]}_{num}.webm'):
            os.remove(f'{call.message.chat.id}_{a[1]}_{num}.webm')
        if os.path.exists('ffmpeg2pass-0.log'):
            os.remove('ffmpeg2pass-0.log')
        if os.path.exists(f'{call.message.chat.id}_{a[1]}_{num}.tgs'):
            os.remove(f'{call.message.chat.id}_{a[1]}_{num}.tgs')
        #if os.path.exists('tmp'):
        #    os.remove(f'tmp')
        update_packs()
        for i in range(1, len(packs[call.message.chat.id])):
            if packs[call.message.chat.id][i][1] == a[1]:
                packs[call.message.chat.id][i][2] -= 1
                break
        set_packs()
        avt = time.time()
        while time.time()-avt < TIMEOUT:
            try:
                bot.delete_message(call.message.chat.id, lst.message_id)
                break
            except:
                pass
        else:
            print('Could not delete message: timeout reached.')
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(lang['Back'][packs[call.message.chat.id][0][4]], callback_data='back'))
        avt = time.time()
        while time.time()-avt < TIMEOUT:
            try:
                lst: Message = log(bot.send_message(call.message.chat.id, f'{type(ex).__name__}: {str(ex)}', reply_markup=markup))
                break
            except:
                pass
        else:
            print('Could not send message: timeout reached')
        cb = 'new_title'
        delete_last(call.message.chat.id, lst)

@bot.callback_query_handler(func=lambda call: call.data == 'new')
def new(call: CallbackQuery) -> None:
    global cb, new_packs, packs
    markup = InlineKeyboardMarkup()
    update_packs()
    markup.add(InlineKeyboardButton(lang['Back'][packs[call.message.chat.id][0][4]], callback_data='back'))
    log('[Create new stickerpack]', call.message.chat.id)
    avt = time.time()
    while time.time()-avt < TIMEOUT:
        try:
            lst: Message = log(bot.send_message(call.message.chat.id, text=lang['Choose a name for your stickerpack'][packs[call.message.chat.id][0][4]], reply_markup=markup))
            break
        except:
            pass
    else:
        print('Could not send message: timeout reached')
    cb = 'new_name'
    bot.answer_callback_query(call.id)
    delete_last(call.message.chat.id, lst)

@bot.callback_query_handler(func=lambda call: call.data == 'back')
def back(call: CallbackQuery) -> None:
    global cb, packs
    update_packs()
    log('[Back]', call.message.chat.id)
    bot.answer_callback_query(call.id)
    cb = None
    delete_last(call.message.chat.id, msg=call.message)

@bot.callback_query_handler(func=lambda call: True)
def unknown_callback(call: CallbackQuery) -> None:
    bot.answer_callback_query(call.id, 'An error occured')

def callback(msg: Message) -> bool:
    global cb, new_packs, packs, queue
    update_packs()
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(lang['Back'][packs[msg.chat.id][0][4]], callback_data='back'))
    if cb == 'new_name':
        new_packs[msg.chat.id][2] = msg.text
        avt = time.time()
        while time.time()-avt < TIMEOUT:
            try:
                lst: Message = log(bot.send_message(msg.chat.id, text=f'{lang["Choose the unique indentifier for your stickerpack"][packs[msg.chat.id][0][4]]} "{new_packs[msg.chat.id][2]}".\n{lang["It must start with a letter and must only contain letters from the English alphabet, numbers and underscores.No double underscores are allowed.Underscore at the end is not allowed."][packs[msg.chat.id][0][4]]}', reply_markup=markup))
                break
            except:
                pass
        else:
            print('Could not send message: timeout reached')
        cb = 'new_title'
        delete_last(msg.chat.id, lst, msg)
        return True
    if cb == 'emojis':
        new_packs[msg.chat.id][1] = [i for i in msg.text]
        markup.add(InlineKeyboardButton(lang['Create new stickerpack'][packs[msg.chat.id][0][4]], callback_data='new'))
        if msg.chat.id in packs:
            for i in range((len(packs[msg.chat.id])-1)//2):
                markup.add(InlineKeyboardButton(f'{lang["Add to"][packs[msg.chat.id][0][4]]} {packs[msg.chat.id][i*2+1][0]} ({packs[msg.chat.id][i*2+1][1]})', callback_data=f'add_{packs[msg.chat.id][i*2+1]}\nuser_id = {msg.from_user.id}'), InlineKeyboardButton(f'{lang["Add to"][packs[msg.chat.id][0][4]]} {packs[msg.chat.id][i*2+2][0]} ({packs[msg.chat.id][i*2+2][1]})', callback_data=f'add_{packs[msg.chat.id][i*2+2]}\nuser_id = {msg.from_user.id}'))
            if len(packs[msg.chat.id])%2 == 0:
                markup.add(InlineKeyboardButton(f'{lang["Add to"][packs[msg.chat.id][0][4]]} {packs[msg.chat.id][len(packs[msg.chat.id])-1][0]} ({packs[msg.chat.id][len(packs[msg.chat.id])-1][1]})', callback_data=f'add_{packs[msg.chat.id][len(packs[msg.chat.id])-1]}\nuser_id = {msg.from_user.id}'))
        avt = time.time()
        while time.time()-avt < TIMEOUT:
            try:
                if new_packs[msg.chat.id][5] == 'doc':
                    lst: Message = log(bot.send_document(msg.chat.id, caption=''.join(new_packs[msg.chat.id][1]), document=new_packs[msg.chat.id][0].file_id, reply_markup=markup))
                elif new_packs[msg.chat.id][5] == 'photo':
                    lst: Message = log(bot.send_photo(msg.chat.id, caption=''.join(new_packs[msg.chat.id][1])+'\n\n'+lang['NOTE: photo type is not recommended for better quality of stickers.'][packs[msg.chat.id][0][4]], photo=new_packs[msg.chat.id][0].file_id, reply_markup=markup))
                elif new_packs[msg.chat.id][5] == 'gif':
                    lst: Message = log(bot.send_animation(msg.chat.id, caption=''.join(new_packs[msg.chat.id][1]), animation=new_packs[msg.chat.id][0].file_id, reply_markup=markup))
                elif new_packs[msg.chat.id][5] == 'video':
                    lst: Message = log(bot.send_video(msg.chat.id, caption=''.join(new_packs[msg.chat.id][1]), video=new_packs[msg.chat.id][0].file_id, reply_markup=markup))
                elif new_packs[msg.chat.id][5] == 'sticker':
                    lst: Message = log(bot.send_sticker(msg.chat.id, new_packs[msg.chat.id][0].file_id, reply_markup=markup))
                break
            except:
                pass
        else:
            print('Could not send message: timeout reached')
        cb = None
        delete_last(msg.chat.id, lst, msg)
        return True
    if cb == 'sticker':
        update_packs()
        new_packs[msg.chat.id] = [msg.sticker, [msg.sticker.emoji], 'NameError', msg.sticker.is_video or msg.sticker.is_animated, msg.sticker.is_animated, 'sticker']
        markup.add(InlineKeyboardButton(lang['Create new stickerpack'][packs[msg.chat.id][0][4]], callback_data='new'))
        if msg.chat.id in packs:
            for i in range((len(packs[msg.chat.id])-1)//2):
                markup.add(InlineKeyboardButton(f'{lang["Add to"][packs[msg.chat.id][0][4]]} {packs[msg.chat.id][i*2+1][0]} ({packs[msg.chat.id][i*2+1][1]})', callback_data=f'add_{packs[msg.chat.id][i*2+1]}\nuser_id = {msg.from_user.id}'), InlineKeyboardButton(f'{lang["Add to"][packs[msg.chat.id][0][4]]} {packs[msg.chat.id][i*2+2][0]} ({packs[msg.chat.id][i*2+2][1]})', callback_data=f'add_{packs[msg.chat.id][i*2+2]}\nuser_id = {msg.from_user.id}'))
            if len(packs[msg.chat.id])%2 == 0:
                markup.add(InlineKeyboardButton(f'{lang["Add to"][packs[msg.chat.id][0][4]]} {packs[msg.chat.id][len(packs[msg.chat.id])-1][0]} ({packs[msg.chat.id][len(packs[msg.chat.id])-1][1]})', callback_data=f'add_{packs[msg.chat.id][len(packs[msg.chat.id])-1]}\nuser_id = {msg.from_user.id}'))
        avt = time.time()
        while time.time()-avt < TIMEOUT:
            try:
                lst: Message = log(bot.send_sticker(msg.chat.id, msg.sticker.file_id, reply_markup=markup))
                break
            except:
                pass
        else:
            print('Could not send message: timeout reached')
        cb = None
        delete_last(msg.chat.id, lst, msg)
        return True
    if cb == 'png_doc':
        update_packs()
        new_packs[msg.chat.id] = [msg.document, ['☹️'], 'NameError', False, False, 'doc']
        if msg.caption == None or msg.caption == '':
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    lst: Message = log(bot.send_document(msg.chat.id, msg.document.file_id, caption=lang['Please send 1-20 emojis.'][packs[msg.chat.id][0][4]], reply_markup=markup))
                    break
                except:
                    pass
            else:
                print('Could not send message: timeout reached')
            cb = 'emojis'
            delete_last(msg.chat.id, lst, msg)
            return True
        if len(msg.caption) > 20:
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    lst: Message = log(bot.send_document(msg.chat.id, msg.document.file_id, caption=f'{lang["has_"][packs[msg.chat.id][0][4]]}"{msg.caption}" {lang["has "][packs[msg.chat.id][0][4]]}{len(msg.caption)} {lang["emojis - it has to be 1 - 20."][packs[msg.chat.id][0][4]]}', reply_markup=markup))
                    break
                except:
                    pass
            else:
                print('Could not send message: timeout reached')
            cb = 'emojis'
            delete_last(msg.chat.id, lst, msg)
            return True
        new_packs[msg.chat.id][1] = [i for i in msg.caption]
        markup.add(InlineKeyboardButton(lang['Create new stickerpack'][packs[msg.chat.id][0][4]], callback_data='new'))
        if msg.chat.id in packs:
            for i in range((len(packs[msg.chat.id])-1)//2):
                markup.add(InlineKeyboardButton(f'{lang["Add to"][packs[msg.chat.id][0][4]]} {packs[msg.chat.id][i*2+1][0]} ({packs[msg.chat.id][i*2+1][1]})', callback_data=f'add_{packs[msg.chat.id][i*2+1]}\nuser_id = {msg.from_user.id}'), InlineKeyboardButton(f'{lang["Add to"][packs[msg.chat.id][0][4]]} {packs[msg.chat.id][i*2+2][0]} ({packs[msg.chat.id][i*2+2][1]})', callback_data=f'add_{packs[msg.chat.id][i*2+2]}\nuser_id = {msg.from_user.id}'))
            if len(packs[msg.chat.id])%2 == 0:
                markup.add(InlineKeyboardButton(f'{lang["Add to"][packs[msg.chat.id][0][4]]} {packs[msg.chat.id][len(packs[msg.chat.id])-1][0]} ({packs[msg.chat.id][len(packs[msg.chat.id])-1][1]})', callback_data=f'add_{packs[msg.chat.id][len(packs[msg.chat.id])-1]}\nuser_id = {msg.from_user.id}'))
        avt = time.time()
        while time.time()-avt < TIMEOUT:
            try:
                lst: Message = log(bot.send_document(msg.chat.id, msg.document.file_id, caption=f'{msg.caption}', reply_markup=markup))
                break
            except:
                pass
        else:
            print('Could not send message: timeout reached')
        cb = None
        delete_last(msg.chat.id, lst, msg)
        return True
    if cb == 'png_photo':
        update_packs()
        new_packs[msg.chat.id] = [msg.photo[0], ['☹️'], 'NameError', False, False, 'photo']
        if msg.caption == None:
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    lst: Message = log(bot.send_photo(msg.chat.id, msg.photo[0].file_id, caption=lang['Please send 1-20 emojis.'][packs[msg.chat.id][0][4]]+'\n\n'+lang['NOTE: photo type is not recommended for better quality of stickers.'][packs[msg.chat.id][0][4]], reply_markup=markup))
                    break
                except:
                    pass
            else:
                print('Could not send message: timeout reached')
            cb = 'emojis'
            delete_last(msg.chat.id, lst, msg)
            return True
        if len(msg.caption) > 20:
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    lst: Message = log(bot.send_photo(msg.chat.id, msg.photo[0].file_id, caption=f'{lang["has_"][packs[msg.chat.id][0][4]]}"{msg.caption}" {lang["has "][packs[msg.chat.id][0][4]]}{len(msg.caption)} {lang["emojis - it has to be 1 - 20."][packs[msg.chat.id][0][4]]}\n\n{lang["NOTE: photo type is not recommended for better quality of stickers."][packs[msg.chat.id][0][4]]}', reply_markup=markup))
                    break
                except:
                    pass
            else:
                print('Could not send message: timeout reached')
            cb = 'emojis'
            delete_last(msg.chat.id, lst, msg)
            return True
        new_packs[msg.chat.id][1] = [i for i in msg.caption]
        markup.add(InlineKeyboardButton(lang['Create new stickerpack'][packs[msg.chat.id][0][4]], callback_data='new'))
        if msg.chat.id in packs:
            for i in range((len(packs[msg.chat.id])-1)//2):
                markup.add(InlineKeyboardButton(f'{lang["Add to"][packs[msg.chat.id][0][4]]} {packs[msg.chat.id][i*2+1][0]} ({packs[msg.chat.id][i*2+1][1]})', callback_data=f'add_{packs[msg.chat.id][i*2+1]}\nuser_id = {msg.from_user.id}'), InlineKeyboardButton(f'{lang["Add to"][packs[msg.chat.id][0][4]]} {packs[msg.chat.id][i*2+2][0]} ({packs[msg.chat.id][i*2+2][1]})', callback_data=f'add_{packs[msg.chat.id][i*2+2]}\nuser_id = {msg.from_user.id}'))
            if len(packs[msg.chat.id])%2 == 0:
                markup.add(InlineKeyboardButton(f'{lang["Add to"][packs[msg.chat.id][0][4]]} {packs[msg.chat.id][len(packs[msg.chat.id])-1][0]} ({packs[msg.chat.id][len(packs[msg.chat.id])-1][1]})', callback_data=f'add_{packs[msg.chat.id][len(packs[msg.chat.id])-1]}\nuser_id = {msg.from_user.id}'))
        avt = time.time()
        while time.time()-avt < TIMEOUT:
            try:
                lst: Message = log(bot.send_photo(msg.chat.id, msg.photo[0].file_id, caption=f'{msg.caption}\n\n{lang["NOTE: photo type is not recommended for better quality of stickers."][packs[msg.chat.id][0][4]]}', reply_markup=markup))
                break
            except:
                pass
        else:
            print('Could not send message: timeout reached')
        cb = None
        delete_last(msg.chat.id, lst, msg)
        return True
    if cb == 'gif':
        update_packs()
        new_packs[msg.chat.id] = [msg.animation, ['☹️'], 'NameError', True, False, 'gif']
        if msg.caption == None or msg.caption == '':
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    lst: Message = log(bot.send_animation(msg.chat.id, msg.animation.file_id, caption=lang['Please send 1-20 emojis.'][packs[msg.chat.id][0][4]], reply_markup=markup))
                    break
                except:
                    pass
            else:
                print('Could not send message: timeout reached')
            cb = 'emojis'
            delete_last(msg.chat.id, lst, msg)
            return True
        if len(msg.caption) > 20:
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    lst: Message = log(bot.send_animation(msg.chat.id, msg.animation.file_id, caption=f'{lang["has_"][packs[msg.chat.id][0][4]]}"{msg.caption}" {lang["has "][packs[msg.chat.id][0][4]]}{len(msg.caption)} {lang["emojis - it has to be 1 - 20."][packs[msg.chat.id][0][4]]}', reply_markup=markup))
                    break
                except:
                    pass
            else:
                print('Could not send message: timeout reached')
            cb = 'emojis'
            delete_last(msg.chat.id, lst, msg)
            return True
        new_packs[msg.chat.id][1] = [i for i in msg.caption]
        markup.add(InlineKeyboardButton(lang['Create new stickerpack'][packs[msg.chat.id][0][4]], callback_data='new'))
        if msg.chat.id in packs:
            for i in range((len(packs[msg.chat.id])-1)//2):
                markup.add(InlineKeyboardButton(f'{lang["Add to"][packs[msg.chat.id][0][4]]} {packs[msg.chat.id][i*2+1][0]} ({packs[msg.chat.id][i*2+1][1]})', callback_data=f'add_{packs[msg.chat.id][i*2+1]}\nuser_id = {msg.from_user.id}'), InlineKeyboardButton(f'{lang["Add to"][packs[msg.chat.id][0][4]]} {packs[msg.chat.id][i*2+2][0]} ({packs[msg.chat.id][i*2+2][1]})', callback_data=f'add_{packs[msg.chat.id][i*2+2]}\nuser_id = {msg.from_user.id}'))
            if len(packs[msg.chat.id])%2 == 0:
                markup.add(InlineKeyboardButton(f'{lang["Add to"][packs[msg.chat.id][0][4]]} {packs[msg.chat.id][len(packs[msg.chat.id])-1][0]} ({packs[msg.chat.id][len(packs[msg.chat.id])-1][1]})', callback_data=f'add_{packs[msg.chat.id][len(packs[msg.chat.id])-1]}\nuser_id = {msg.from_user.id}'))
        avt = time.time()
        while time.time()-avt < TIMEOUT:
            try:
                lst: Message = log(bot.send_animation(msg.chat.id, msg.animation.file_id, caption=f'{msg.caption}', reply_markup=markup))
                break
            except:
                pass
        else:
            print('Could not send message: timeout reached')
        cb = None
        delete_last(msg.chat.id, lst, msg)
        return True
    if cb == 'video':
        update_packs()
        new_packs[msg.chat.id] = [msg.video, ['☹️'], 'NameError', True, False, 'video']
        if msg.caption == None or msg.caption == '':
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    lst: Message = log(bot.send_video(msg.chat.id, msg.video.file_id, caption=lang['Please send 1-20 emojis.'][packs[msg.chat.id][0][4]], reply_markup=markup))
                    break
                except:
                    pass
            else:
                print('Could not send message: timeout reached')
            cb = 'emojis'
            delete_last(msg.chat.id, lst, msg)
            return True
        if len(msg.caption) > 20:
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    lst: Message = log(bot.send_video(msg.chat.id, msg.video.file_id, caption=f'{lang["has_"][packs[msg.chat.id][0][4]]}"{msg.caption}" {lang["has "][packs[msg.chat.id][0][4]]}{len(msg.caption)} {lang["emojis - it has to be 1 - 20."][packs[msg.chat.id][0][4]]}', reply_markup=markup))
                    break
                except:
                    pass
            else:
                print('Could not send message: timeout reached')
            cb = 'emojis'
            delete_last(msg.chat.id, lst, msg)
            return True
        new_packs[msg.chat.id][1] = [i for i in msg.caption]
        markup.add(InlineKeyboardButton(lang['Create new stickerpack'][packs[msg.chat.id][0][4]], callback_data='new'))
        if msg.chat.id in packs:
            for i in range((len(packs[msg.chat.id])-1)//2):
                markup.add(InlineKeyboardButton(f'{lang["Add to"][packs[msg.chat.id][0][4]]} {packs[msg.chat.id][i*2+1][0]} ({packs[msg.chat.id][i*2+1][1]})', callback_data=f'add_{packs[msg.chat.id][i*2+1]}\nuser_id = {msg.from_user.id}'), InlineKeyboardButton(f'{lang["Add to"][packs[msg.chat.id][0][4]]} {packs[msg.chat.id][i*2+2][0]} ({packs[msg.chat.id][i*2+2][1]})', callback_data=f'add_{packs[msg.chat.id][i*2+2]}\nuser_id = {msg.from_user.id}'))
            if len(packs[msg.chat.id])%2 == 0:
                markup.add(InlineKeyboardButton(f'{lang["Add to"][packs[msg.chat.id][0][4]]} {packs[msg.chat.id][len(packs[msg.chat.id])-1][0]} ({packs[msg.chat.id][len(packs[msg.chat.id])-1][1]})', callback_data=f'add_{packs[msg.chat.id][len(packs[msg.chat.id])-1]}\nuser_id = {msg.from_user.id}'))
        avt = time.time()
        while time.time()-avt < TIMEOUT:
            try:
                lst: Message = log(bot.send_animation(msg.chat.id, msg.animation.file_id, caption=f'{msg.caption}', reply_markup=markup))
                break
            except:
                pass
        else:
            print('Could not send message: timeout reached')
        cb = None
        delete_last(msg.chat.id, lst, msg)
        return True
    if cb == 'new_title':
        new_packs_local: dict = new_packs.copy()
        for i in range(len(msg.text)):
            if not ((ord(msg.text[i]) >= ord('A') and ord(msg.text[i]) <= ord('Z')) or (ord(msg.text[i]) >= ord('a') and ord(msg.text[i]) <= ord('z')) or (ord(msg.text[i]) >= ord('0') and ord(msg.text[i]) <= ord('9') and i != 0) or (msg.text[i] == '_' and msg.text[i-1] != '_' and i != len(msg.text)-1 and i != 0)):
                avt = time.time()
                while time.time()-avt < TIMEOUT:
                    try:
                        lst: Message = log(bot.send_message(msg.chat.id, f'{lang["The unique identifier"][packs[msg.chat.id][0][4]]} "{msg.text}" {lang["for your stickerpack"][packs[msg.chat.id][0][4]]} "{new_packs_local[msg.chat.id][2]}" {lang["is invalid."][packs[msg.chat.id][0][4]]}\n{lang["It must start with a letter and must only contain letters from the English alphabet, numbers and underscores.No double underscores are allowed.Underscore at the end is not allowed."][packs[msg.chat.id][0][4]]}', reply_markup=markup))
                        break
                    except:
                        pass
                else:
                    print('Could not send message: timeout reached')
                delete_last(msg.chat.id, lst, msg)
                return True
        for i in range(1, len(packs[msg.chat.id])):
            if packs[msg.chat.id][i][1] == msg.text:
                if packs[msg.chat.id][i][2] <= 1:
                    avt = time.time()
                    while time.time()-avt < TIMEOUT:
                        try:
                            lst: Message = log(bot.send_message(msg.chat.id, text=f'{lang["Stickerpack with"][packs[msg.chat.id][0][4]]} "{msg.text}" {lang["uid already exists."][packs[msg.chat.id][0][4]]}', reply_markup=markup))
                            break
                        except:
                            pass
                    else:
                        print('Could not send message: timeout reached')
                    delete_last(msg.chat.id, lst, msg)
                    return True
                break
        queue += [msg.text]
        update_packs()
        if msg.chat.id not in packs:
            packs[msg.chat.id] = []
        packs[msg.chat.id] += [[new_packs_local[msg.chat.id][2], msg.text, 1]]
        set_packs()
        try:
            cb = None
            if new_packs_local[msg.chat.id][4]:
                delete_last(msg.chat.id, msg=msg)
                with open(f'{msg.chat.id}_{msg.text}_1.tgs', 'wb') as f:
                    f.write(bot.download_file(bot.get_file(new_packs_local[msg.chat.id][0].file_id).file_path))
                with open(f'{msg.chat.id}_{msg.text}_1.tgs', 'rb') as f:
                    bot.create_new_sticker_set(msg.from_user.id, msg.text+'_by_sticker_packer_bot', new_packs_local[msg.chat.id][2], stickers=[InputSticker(InputFile(f), emoji_list=new_packs_local[msg.chat.id][1], format='animated')])
                update_start(msg.chat.id)
                cb = None
                os.remove(f'{msg.chat.id}_{msg.text}_1.tgs')
            elif new_packs_local[msg.chat.id][3]:
                pb = progressbar(0, '...')
                delete_last(msg.chat.id, msg=msg)
                avt = time.time()
                while time.time()-avt < TIMEOUT:
                    try:
                        lst: Message = log(bot.send_message(msg.chat.id, f'{lang["Please wait... (resizing)"][packs[msg.chat.id][0][4]]}\n{pb}'))
                        break
                    except:
                        pass
                else:
                    delete_last(msg.chat.id, log(bot.send_message(msg.chat.id, 'Could not send message: timeout reached.')))
                    cb = None
                    return True
                with open(f'{msg.chat.id}_{msg.text}_1.mp4', 'wb') as f:
                    f.write(bot.download_file(bot.get_file(new_packs_local[msg.chat.id][0].file_id).file_path))
                video_capture: cv2.VideoCapture = cv2.VideoCapture(f'{msg.chat.id}_{msg.text}_1.mp4')
                still_reading, image = video_capture.read()
                frame_count: int = 0
                frames_all: int = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
                if frames_all == 8:
                    frames_all = 120
                frames = []
                while still_reading:
                    cv2.imwrite(f'{msg.chat.id}_{msg.text}_1.png', image)
                    frame = Image.open(f'{msg.chat.id}_{msg.text}_1.png')
                    size = frame.size
                    if size[1] > size[0]:
                        frames += [frame.resize((int(size[0]*(512/size[1])), 512))]
                    else:
                        frames += [frame.resize((512, int(size[1]*(512/size[0]))))]
                    still_reading, image = video_capture.read()
                    frame_count += 1
                    if pb.split('|')[1] != progressbar(frame_count, frames_all).split('|')[1]:
                        pb = progressbar(frame_count, frames_all)
                        try:
                            update_packs()
                            lst = bot.edit_message_text(f'{lang["Please wait... (resizing)"][packs[msg.chat.id][0][4]]}\n{pb}', msg.chat.id, lst.message_id)
                            set_packs()
                        except:
                            pass
                frames_all = frame_count
                video_capture.release()
                os.remove(f'{msg.chat.id}_{msg.text}_1.mp4')
                os.remove(f'{msg.chat.id}_{msg.text}_1.png')
                avt = time.time()
                while time.time()-avt < TIMEOUT:
                    try:
                        update_packs()
                        lst = log(bot.edit_message_text(lang['Please wait... (making GIF)'][packs[msg.chat.id][0][4]], msg.chat.id, lst.message_id))
                        break
                    except:
                        pass
                else:
                    print('Could not edit message: timeout reached')
                frames[0].save(f'{msg.chat.id}_{msg.text}_1.gif', save_all=True, append_images=frames, duration=50, loop=0)
                avt = time.time()
                while time.time()-avt < TIMEOUT:
                    try:
                        update_packs()
                        lst = log(bot.edit_message_text(f'{lang["Please wait... (converting to WEBM)"][packs[msg.chat.id][0][4]]}\n{progressbar(0, int(packs["average_video_time"]*frames_all))}', msg.chat.id, lst.message_id))
                        break
                    except:
                        pass
                else:
                    print('Could not edit message: timeout reached')
                os.system(f'start "Stickerpacker converter (tgradish)" /i /min tgradish convert -fr 20 -it 1 -t {len(frames)/20} -i {msg.chat.id}_{msg.text}_1.gif')
                avt: float = time.time()
                pb: str = progressbar(0, int(packs["average_video_time"]*frames_all))
                while not os.path.exists(f'{msg.chat.id}_{msg.text}_1.webm'):
                    if progressbar(int(time.time()-avt), int(packs["average_video_time"]*frames_all)).split('|')[1] != pb.split('|')[1]:
                        try:
                            update_packs()
                            lst = bot.edit_message_text(f'{lang["Please wait... (converting to WEBM)"][packs[msg.chat.id][0][4]]}\n{progressbar(int(time.time()-avt), int(packs["average_video_time"]*frames_all))}{int(time.time()-avt)}{lang["s elapsed"][packs[msg.chat.id][0][4]]}|~{int(packs["average_video_time"]*frames_all)-int(time.time()-avt)}{lang["s left"][packs[msg.chat.id][0][4]]}|', msg.chat.id, lst.message_id)
                        except:
                            pass
                    pb = progressbar(int(time.time()-avt), int(packs["average_video_time"]*frames_all))
                update_packs()
                packs['average_video_time'] = (packs['average_video_time']+(time.time()-avt)/frames_all)/2
                set_packs()
                time.sleep(0.5)
                with open(f'{msg.chat.id}_{msg.text}_1.webm', 'rb') as f:
                    bot.create_new_sticker_set(msg.from_user.id, msg.text+'_by_sticker_packer_bot', new_packs_local[msg.chat.id][2], stickers=[InputSticker(InputFile(f), emoji_list=new_packs_local[msg.chat.id][1], format='video')])
                update_start(msg.chat.id)
                cb = None
                os.remove(f'{msg.chat.id}_{msg.text}_1.gif')
                os.remove(f'{msg.chat.id}_{msg.text}_1.webm')
                os.remove('ffmpeg2pass-0.log')
                #os.remove('tmp')
                avt = time.time()
                while time.time()-avt < TIMEOUT:
                    try:
                        bot.delete_message(msg.chat.id, lst.message_id)
                        break
                    except:
                        pass
                else:
                    print('Could not delete message: timeout reached.')
            else:
                delete_last(msg.chat.id, msg=msg)
                avt = time.time()
                while time.time()-avt < TIMEOUT:
                    try:
                        lst: Message = log(bot.send_message(msg.chat.id, lang['Please wait... (resizing)'][packs[msg.chat.id][0][4]]))
                        break
                    except:
                        pass
                else:
                    print('Could not send message: timeout reached')
                    cb = None
                    return True
                with open(f'{msg.chat.id}_{msg.text}_1.png', 'wb') as f:
                    f.write(bot.download_file(bot.get_file(new_packs_local[msg.chat.id][0].file_id).file_path))
                img = Image.open(f'{msg.chat.id}_{msg.text}_1.png')
                img.save(f'{msg.chat.id}_{msg.text}_1.png')
                size = img.size
                if size[1] > size[0]:
                    img = img.resize((int(size[0]*(512/size[1])), 512))
                else:
                    img = img.resize((512, int(size[1]*(512/size[0]))))
                img.save(f'{msg.chat.id}_{msg.text}_1.png')
                with open(f'{msg.chat.id}_{msg.text}_1.png', 'rb') as f:
                    bot.create_new_sticker_set(msg.from_user.id, msg.text+'_by_sticker_packer_bot', new_packs_local[msg.chat.id][2], stickers=[InputSticker(InputFile(f), emoji_list=new_packs_local[msg.chat.id][1], format='static')])
                update_start(msg.chat.id)
                cb = None
                os.remove(f'{msg.chat.id}_{msg.text}_1.png')
                avt = time.time()
                while time.time()-avt < TIMEOUT:
                    try:
                        bot.delete_message(msg.chat.id, lst.message_id)
                        break
                    except:
                        pass
                else:
                    print('Could not delete message: timeout reached.')
        except Exception as ex:
            if os.path.exists(f'{msg.chat.id}_{msg.text}_1.png'):
                os.remove(f'{msg.chat.id}_{msg.text}_1.png')
            if os.path.exists(f'{msg.chat.id}_{msg.text}_1.gif'):
                os.remove(f'{msg.chat.id}_{msg.text}_1.gif')
            if os.path.exists(f'{msg.chat.id}_{msg.text}_1.webm'):
                os.remove(f'{msg.chat.id}_{msg.text}_1.webm')
            if os.path.exists('ffmpeg2pass-0.log'):
                os.remove('ffmpeg2pass-0.log')
            if os.path.exists(f'{msg.chat.id}_{msg.text}_1.tgs'):
                os.remove(f'{msg.chat.id}_{msg.text}_1.tgs')
            #if os.path.exists('tmp'):
            #    os.remove('tmp')
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    bot.delete_message(msg.chat.id, lst)
                    break
                except:
                    pass
            else:
                print('Could not delete message: timeout reached.')            
            if str(ex) == 'A request to the Telegram API was unsuccessful. Error code: 400. Description: Bad Request: sticker set name is already occupied':
                avt = time.time()
                while time.time()-avt < TIMEOUT:
                    try:
                        lst: Message = log(bot.send_message(msg.chat.id, f'{lang["Stickerpack with"][packs[msg.chat.id][0][4]]} "{msg.text}" {lang["uid already exists."][packs[msg.chat.id][0][4]]}', reply_markup=markup))
                        break
                    except:
                        pass
                else:
                    print('Could not send message: timeout reached')
            else:
                print('{type(ex).__name__}: {str(ex)}')
            cb = 'new_title'
            delete_last(msg.chat.id, lst, msg)
            update_packs()
            for i in range(len(packs[msg.chat.id])):
                if packs[msg.chat.id][i][1] == msg.text:
                    del packs[msg.chat.id][i]
            set_packs()
        del queue[queue.index(msg.text)]
        return True
    if cb == 'sticker_del':
        update_packs()
        n = -1
        for i in range(1, len(packs[msg.chat.id])):
            if f'{packs[msg.chat.id][i][1]}_by_sticker_packer_bot' == msg.sticker.set_name:
                if packs[msg.chat.id][i][2] <= 1:
                    avt = time.time()
                    while time.time()-avt < TIMEOUT:
                        try:
                            lst: Message = log(bot.send_message(msg.chat.id, text=f'{lang["stickerpack_"][packs[msg.chat.id][0][4]]}"{packs[msg.chat.id][i][0]}" {lang["stickerpack only has 1 sticker."][packs[msg.chat.id][0][4]]}', reply_markup=markup))
                            break
                        except:
                            pass
                    else:
                        print('Could not send message: timeout reached')
                    delete_last(msg.chat.id, lst, msg)
                    return True
                n = i
                break
        else:
            avt = time.time()
            while time.time()-avt < TIMEOUT:
                try:
                    lst: Message = log(bot.send_message(msg.chat.id, text=f'{lang["stickerpack__"][packs[msg.chat.id][0][4]]}"{msg.sticker.set_name}" {lang["stickerpack is either not yours or was not made by stickerpacker bot."][packs[msg.chat.id][0][4]]}', reply_markup=markup))
                    break
                except:
                    pass
            else:
                print('Could not send message: timeout reached')
            delete_last(msg.chat.id, lst, msg)
            return True
        if test:
            bot.delete_sticker_from_set(msg.sticker.file_id)
            update_packs()
            packs[msg.chat.id][n][2] -= 1
            set_packs()
            cb = None
            delete_last(msg.chat.id, msg=msg)
        else:
            try:
                bot.delete_sticker_from_set(msg.sticker.file_id)
                update_packs()
                packs[msg.chat.id][n][2] -= 1
                set_packs()
                cb = None
                delete_last(msg.chat.id, msg=msg)
            except Exception as ex:
                avt = time.time()
                while time.time()-avt < TIMEOUT:
                    try:
                        lst: Message = log(bot.send_message(msg.chat.id, text=lang['Cannot delete sticker from set'][packs[msg.chat.id][0][4]], reply_markup=markup))
                        break
                    except:
                        pass
                else:
                    print('Could not send message: timeout reached')
                print(ex)
                delete_last(msg.chat.id, lst, msg)
        return True
    return False

@bot.message_handler(content_types=['text'])
def text(msg: Message) -> None:
    global cb
    log(msg)
    if cb != None and 'png' not in cb and 'sticker' not in cb and 'gif' not in cb and 'video' not in cb and callback(msg):
        return
    print('Stickerpacker: text deleted')
    with open('log.txt', 'a', encoding='utf-8') as f:
        print('Stickerpacker: text deleted', file=f)
    if test:
        bot.delete_message(msg.chat.id, msg.message_id)
    else:
        avt = time.time()
        while time.time()-avt < TIMEOUT:
            try:
                bot.delete_message(msg.chat.id, msg.message_id)
                break
            except:
                pass
        else:
            print('Could not delete message: timeout reached')

@bot.message_handler(content_types=['document'])
def doc(msg: Message) -> None:
    global cb, new_packs
    log(msg)
    if os.path.splitext(bot.get_file(msg.document.file_id).file_path)[-1].lower() == '.png' and msg.chat.id in new_packs:
        del new_packs[msg.chat.id]
    cb = 'png_doc'
    if callback(msg):
        return
    print(f'Stickerpacker: deleted {os.path.splitext(bot.get_file(msg.document.file_id).file_path)[-1].upper()[1:]} document')
    with open('log.txt', 'a', encoding='utf-8') as f:
        print(f'Stickerpacker: deleted {os.path.splitext(bot.get_file(msg.document.file_id).file_path)[-1].upper()[1:]} document', file=f)
    if test:
        bot.delete_message(msg.chat.id, msg.message_id)
    else:
        avt = time.time()
        while time.time()-avt < TIMEOUT:
            try:
                bot.delete_message(msg.chat.id, msg.message_id)
                break
            except:
                pass
        else:
            print('Could not delete message: timeout reached')

@bot.message_handler(content_types=['photo'])
def photo(msg: Message) -> None:
    global cb, new_packs
    log(msg)
    if msg.chat.id in new_packs:
        del new_packs[msg.chat.id]
    cb = 'png_photo'
    if callback(msg):
        return
    print('Stickerpacker: photo deleted')
    with open('log.txt', 'a', encoding='utf-8') as f:
        print('Stickerpacker: photo deleted', file=f)
    if test:
        bot.delete_message(msg.chat.id, msg.message_id)
    else:
        avt = time.time()
        while time.time()-avt < TIMEOUT:
            try:
                bot.delete_message(msg.chat.id, msg.message_id)
                break
            except:
                pass
        else:
            print('Could not delete message: timeout reached')

@bot.message_handler(content_types=['animation'])
def gif(msg: Message) -> None:
    global cb, new_packs
    log(msg)
    if msg.chat.id in new_packs:
        del new_packs[msg.chat.id]
    cb = 'gif'
    if callback(msg):
        return
    print('Stickerpacker: gif deleted')
    with open('log.txt', 'a', encoding='utf-8') as f:
        print('Stickerpacker: gif deleted', file=f)
    if test:
        bot.delete_message(msg.chat.id, msg.message_id)
    else:
        avt = time.time()
        while time.time()-avt < TIMEOUT:
            try:
                bot.delete_message(msg.chat.id, msg.message_id)
                break
            except:
                pass
        else:
            print('Could not delete message: timeout reached')

@bot.message_handler(content_types=['video'])
def video(msg: Message) -> None:
    global cb, new_packs
    log(msg)
    if msg.chat.id in new_packs:
        del new_packs[msg.chat.id]
    cb = 'video'
    if callback(msg):
        return
    print('Stickerpacker: video deleted')
    with open('log.txt', 'a', encoding='utf-8') as f:
        print('Stickerpacker: video deleted', file=f)
    if test:
        bot.delete_message(msg.chat.id, msg.message_id)
    else:
        avt = time.time()
        while time.time()-avt < TIMEOUT:
            try:
                bot.delete_message(msg.chat.id, msg.message_id)
                break
            except:
                pass
        else:
            print('Could not delete message: timeout reached')

@bot.message_handler(content_types=['sticker'])
def sticker(msg: Message) -> None:
    global cb
    log(msg)
    if cb != None and 'sticker' in cb and callback(msg):
        return
    elif not (cb != None and 'sticker' in cb):
        if msg.chat.id in new_packs:
            del new_packs[msg.chat.id]
        cb = 'sticker'
        if callback(msg):
            return
    print('Stickerpacker: sticker deleted')
    with open('log.txt', 'a', encoding='utf-8') as f:
        print('Stickerpacker: sticker deleted', file=f)
    if test:
        bot.delete_message(msg.chat.id, msg.message_id)
    else:
        avt = time.time()
        while time.time()-avt < TIMEOUT:
            try:
                bot.delete_message(msg.chat.id, msg.message_id)
                break
            except:
                pass
        else:
            print('Could not delete message: timeout reached')
@bot.message_handler(content_types=telebot.util.content_type_media)
def unknown(msg: Message) -> None:
    log(msg)
    print('Stickerpacker: unknown deleted')
    with open('log.txt', 'a', encoding='utf-8') as f:
        print('Stickerpacker: unknown deleted', file=f)
    if test:
        bot.delete_message(msg.chat.id, msg.message_id)
    else:
        avt = time.time()
        while time.time()-avt < TIMEOUT:
            try:
                bot.delete_message(msg.chat.id, msg.message_id)
                break
            except:
                pass
        else:
            print('Could not delete message: timeout reached')

print('Started polling.')
polling = True
if test:
    bot.polling()
else:
    error = None
    times = 0
    while True:
        try:
            bot.polling(True)
        except Exception as ex:
            if type(ex).__name__ == error:
                times += 1
                print('Restarted polling. X'+str(times), end='\r')
            else:
                if type(ex) == KeyboardInterrupt:
                    break
                print(ex)
                error = type(ex).__name__
                times = 1
                print('Restarted polling.', end='\r')
print('Stopped polling.')
