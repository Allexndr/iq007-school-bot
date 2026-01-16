import datetime
import json
import random
import string
import os
import logging
import tempfile
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, FSInputFile, CallbackQuery
from PIL import Image, ImageDraw, ImageFont
import app.keyboards as kb

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

router = Router()

# Пути к файлам
# Пути к файлам
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(BASE_DIR, "content", "font", "OpenSans_Condensed-Bold.ttf")
CONTENT_PATH = os.path.join(BASE_DIR, "content")
APP_PATH = os.path.join(BASE_DIR, "app")
USERS_PASSWORD_PATH = os.path.join(APP_PATH, "user_passwords.json")
STUDENT_PASSWORD_PATH = os.path.join(APP_PATH, "student_passwords.json")

# Настройка шрифтов и координат
try:
    font_fio = ImageFont.truetype(FONT_PATH, 80)
except Exception as e:
    logging.error(f"Не удалось загрузить шрифт: {e}")
    font_fio = None

fio_coords = (408, 1350)  # Позиция ФИО
number_coords_five_year = (100, 100)

def choose_year_template(year, fio, courses, delete_after_creation=False):
    templates = {
        "1_m": "1year_man.png",
        "1_w": "1year_woman.png",
        "2_m": "2year_man.png",
        "2_w": "2year_woman.png",
        "3_m": "3year_man.png",
        "3_w": "3year_woman.png",
        "4_m": "4year_man.png",
        "4_w": "4year_woman.png",
        "5_m": "5year_man.png",
        "5_w": "5year_woman.png",
    }
    template_file = templates.get(year)
    if not template_file:
        logging.error(f"Некорректный ключ шаблона: {year}")
        return None

    template_path = os.path.join(CONTENT_PATH, template_file)
    if not os.path.exists(template_path):
        logging.error(f"Файл шаблона не найден: {template_path}")
        return None

    try:
        image = Image.open(template_path)
    except Exception as e:
        logging.error(f"Не удалось открыть шаблон изображения: {e}")
        return None

    draw = ImageDraw.Draw(image)

    # Проверка шрифта
    try:
        font = ImageFont.truetype(FONT_PATH, 80)
        font_five_fio = ImageFont.truetype(FONT_PATH, 65)
    except Exception as e:
        logging.error(f"Не удалось загрузить шрифт: {e}")
        return None

    # Добавление ФИО
    if year.startswith(('1', '2', '3', '4', '5')):
        try:
            draw.text(fio_coords, fio, fill=(233, 77, 9), font=font_five_fio)
        except Exception as e:
            logging.error(f"Не удалось нарисовать текст (ФИО): {e}")
            return None

    # Добавление курсов
    courses_coords = [
        (408, 1800),
        (408, 1900),
        (408, 2000),
        (408, 2100)
    ]
    for i, course in enumerate(courses):
        if i >= len(courses_coords):
            logging.warning("Превышено максимальное количество курсов для размещения на сертификате.")
            break
        try:
            draw.text(courses_coords[i], course, fill=(17, 93, 104), font=font)
        except Exception as e:
            logging.error(f"Не удалось нарисовать текст (курс): {e}")
            return None

    unique_filename = generate_unique_filename()
    output_path = os.path.join(CONTENT_PATH, f"{unique_filename}.pdf")
    try:
        image.save(output_path, "PDF", resolution=100.0)
    except Exception as e:
        logging.error(f"Не удалось сохранить изображение: {e}")
        return None

    if delete_after_creation:
        try:
            os.remove(template_path)
        except Exception as e:
            logging.error(f"Не удалось удалить файл шаблона: {e}")

    return output_path

def generate_unique_filename():
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return f"certificate_{timestamp}_{random_string}"

def load_credentials(file_path):
    if not os.path.exists(file_path):
        logging.error(f"Файл {file_path} не найден.")
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        logging.error(f"Ошибка декодирования JSON в файле {file_path}: {e}")
        return {}
    except Exception as e:
        logging.error(f"Не удалось загрузить файл {file_path}: {e}")
        return {}

def save_credentials(file_path, data):
    try:
        # Создаем временный файл в той же директории, что и целевой файл
        with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8', dir=os.path.dirname(file_path)) as tmpfile:
            json.dump(data, tmpfile, indent=4, ensure_ascii=False)
            temp_name = tmpfile.name
        # Переименовываем временный файл в целевой
        os.replace(temp_name, file_path)
    except Exception as e:
        logging.error(f"Не удалось сохранить файл {file_path}: {e}")


def reset_issued_passwords_if_needed(user_credential):
    last_reset_date_str = user_credential.get("last_reset_date")
    if last_reset_date_str:
        try:
            last_reset_date = datetime.datetime.fromisoformat(last_reset_date_str)
            if datetime.datetime.now() - last_reset_date > datetime.timedelta(days=10):
                user_credential["issued_count"] = 0
                user_credential["last_reset_date"] = datetime.datetime.now().isoformat()
                logging.info(f"Счетчик выданных паролей сброшен для пользователя {user_credential['login']}.")
        except Exception as e:
            logging.error(f"Ошибка при обработке даты сброса для пользователя {user_credential['login']}: {e}")
    else:
        user_credential["last_reset_date"] = datetime.datetime.now().isoformat()
        user_credential["issued_count"] = 0
        logging.info(f"Установлена начальная дата сброса и счетчик для пользователя {user_credential['login']}.")

class AuthStates(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()

class Reg(StatesGroup):
    fio = State()
    gender = State()
    year = State()
    courses = State()

class AdminStates(StatesGroup):
    waiting_for_user_file = State()
    waiting_for_password_file = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    users_credentials = load_credentials(USERS_PASSWORD_PATH)
    telegram_id = message.from_user.id  # Используем целое число

    # Проверка, связан ли уже Telegram ID с пользователем
    user_credential = next(
        (cred for cred in users_credentials.get("logins_passwords", []) if cred.get("telegram_id") == telegram_id),
        None
    )

    if user_credential:
        # Пользователь уже аутентифицирован
        await message.answer(f"Здравствуйте, {message.from_user.first_name}\n", reply_markup=kb.menu)
        logging.info(f"Пользователь {user_credential['login']} уже аутентифицирован.")
    else:
        # Пользователь не аутентифицирован, запрашиваем логин и пароль
        await message.answer("Введите ваш логин:")
        await state.set_state(AuthStates.waiting_for_login)

@router.message(AuthStates.waiting_for_login)
async def process_login(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer("Введите ваш пароль:")
    await state.set_state(AuthStates.waiting_for_password)

@router.message(AuthStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    user_data = await state.get_data()
    login = user_data.get("login")
    password = message.text
    telegram_id = message.from_user.id  # Используем целое число

    # Проверка логина и пароля
    users_credentials = load_credentials(USERS_PASSWORD_PATH)
    user_credential = next(
        (cred for cred in users_credentials.get("logins_passwords", [])
         if cred["login"] == login and cred["password"] == password),
        None
    )

    if user_credential:
        # Связывание Telegram ID с пользователем
        user_credential["telegram_id"] = telegram_id
        # Проверка и сброс счетчика, если прошло более 10 дней
        reset_issued_passwords_if_needed(user_credential)
        # Сохранение изменений
        save_credentials(USERS_PASSWORD_PATH, users_credentials)

        await state.clear()
        await message.answer(f"Здравствуйте, {message.from_user.first_name}\n", reply_markup=kb.menu)
        logging.info(f"Пользователь {login} успешно вошёл в систему.")
    else:
        await message.answer("Неправильный логин или пароль. Попробуйте снова.")
        await state.clear()
        await state.set_state(AuthStates.waiting_for_login)

@router.message(Command('admin'))
async def cmd_admin(message: Message):
    await message.answer("Вы открыли админ панель", reply_markup=kb.admin)

@router.message(F.text.in_({"Внести пользователей"}))
async def add_users(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, отправьте файл user_passwords.json")
    await state.set_state(AdminStates.waiting_for_user_file)

@router.message(F.document, AdminStates.waiting_for_user_file)
async def process_user_file(message: Message, state: FSMContext):
    document = message.document
    if document.file_name == "user_passwords.json":
        file_info = await message.bot.get_file(document.file_id)
        file_path = os.path.join(APP_PATH, document.file_name)
        await message.bot.download_file(file_info.file_path, file_path)
        await message.answer("Файл user_passwords.json успешно загружен и перезаписан.")
        logging.info("Файл user_passwords.json был обновлен администратором.")
    else:
        await message.answer("Неправильный файл. Пожалуйста, отправьте user_passwords.json.")
    await state.clear()

@router.message(F.text.in_({"Внести пароли"}))
async def add_passwords(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, отправьте файл student_passwords.json")
    await state.set_state(AdminStates.waiting_for_password_file)

@router.message(F.text.in_({"Назад"}))
async def back_to_menu(message: Message, state: FSMContext):
    await message.answer("Вы вернулись в главное меню", reply_markup=kb.menu)
    await state.clear()

@router.message(F.document, AdminStates.waiting_for_password_file)
async def process_password_file(message: Message, state: FSMContext):
    document = message.document
    if document.file_name == "student_passwords.json":
        file_info = await message.bot.get_file(document.file_id)
        file_path = os.path.join(APP_PATH, document.file_name)
        await message.bot.download_file(file_info.file_path, file_path)
        await message.answer("Файл student_passwords.json успешно загружен и перезаписан.")
        logging.info("Файл student_passwords.json был обновлен администратором.")
    else:
        await message.answer("Неправильный файл. Пожалуйста, отправьте student_passwords.json.")
    await state.clear()

@router.message(F.text == "Получить сертификат")
async def choose_certificate(message: Message, state: FSMContext):
    # Добавленное состояние для получения ФИО
    await state.set_state(Reg.fio)
    await message.answer("Введите ФИО ученика")

@router.message(Reg.fio)
async def get_fio(message: Message, state: FSMContext):
    # Добавлено обновление данных состояния и переход к выбору пола
    await state.update_data(fio=message.text)
    await message.answer("Укажите пол", reply_markup=kb.gender)
    await state.set_state(Reg.gender)

@router.callback_query(Reg.gender)
async def get_gender(callback_query: CallbackQuery, state: FSMContext):
    # Добавлено обновление данных состояния и переход к выбору года обучения
    await state.update_data(gender=callback_query.data)
    await callback_query.message.answer("Выберите год обучения", reply_markup=kb.years)
    await state.set_state(Reg.year)

@router.callback_query(Reg.year)
async def get_year(callback_query: CallbackQuery, state: FSMContext):
    year_dict = {
        "first_year": "1",
        "second_year": "2",
        "third_year": "3",
        "four_year": "4",
        "five_year": "5"
    }
    year = year_dict.get(callback_query.data, "1")
    await state.update_data(year=year)

    if year == "1":
        await callback_query.message.answer("Выберите курсы для 1 года", reply_markup=kb.courses_year_1)
    elif year == "2":
        await callback_query.message.answer("Выберите курсы для 2 года", reply_markup=kb.courses_year_2)
    elif year == "3":
        await callback_query.message.answer("Выберите курсы для 3 года", reply_markup=kb.courses_year_3)
    elif year == "4":
        await callback_query.message.answer("Выберите курсы для 4 года", reply_markup=kb.courses_year_4)
    elif year == "5":
        await callback_query.message.answer("Выберите курсы для 5 года", reply_markup=kb.courses_year_5)

    await state.set_state(Reg.courses)

@router.callback_query(Reg.courses)
async def get_courses(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    selected_courses = user_data.get('selected_courses', [])

    if callback_query.data == "done":
        fio = user_data.get('fio')
        gender = user_data.get('gender')
        year = user_data.get('year')
        template_key = f"{year}_{gender}"
        output_path = choose_year_template(template_key, fio, selected_courses, delete_after_creation=False)
        if output_path:
            await callback_query.message.answer_document(FSInputFile(output_path))
            os.remove(output_path)  # Удаляем сертификат после отправки
            logging.info(f"Сертификат создан для пользователя с ФИО: {fio}")
        else:
            await callback_query.message.answer("Ошибка при создании сертификата.")
        await state.clear()
    else:
        if len(selected_courses) < 4:
            selected_courses.append(callback_query.data)
            await state.update_data(selected_courses=selected_courses)
            await callback_query.answer("Курс добавлен")
        else:
            await callback_query.answer("Вы достигли максимального количества курсов (4).")

@router.message(F.text.in_({"Получить пароль"}))
async def get_password(message: Message, state: FSMContext):
    telegram_id = message.from_user.id  # Используем целое число

    users_credentials = load_credentials(USERS_PASSWORD_PATH)
    student_credentials = load_credentials(STUDENT_PASSWORD_PATH)

    # Найти пользователя по Telegram ID
    user_credential = next(
        (cred for cred in users_credentials.get("logins_passwords", []) if cred.get("telegram_id") == telegram_id),
        None
    )

    if not user_credential:
        await message.answer("Пожалуйста, войдите в систему сначала.")
        return

    # Проверка и сброс счетчика, если прошло более 10 дней
    reset_issued_passwords_if_needed(user_credential)
    save_credentials(USERS_PASSWORD_PATH, users_credentials)

    issued_count = user_credential.get("issued_count", 0)

    if issued_count >= 4:
        last_reset_date_str = user_credential.get("last_reset_date")
        try:
            last_reset_date = datetime.datetime.fromisoformat(last_reset_date_str)
            days_passed = (datetime.datetime.now() - last_reset_date).days
            days_remaining = 10 - days_passed
            if days_remaining > 0:
                await message.answer(
                    f"Вы достигли лимита на выдачу паролей (4/4). Пожалуйста, подождите {days_remaining} дней для сброса."
                )
                return
            else:
                # Сброс счетчика, если прошло 10 дней
                user_credential["issued_count"] = 0
                user_credential["last_reset_date"] = datetime.datetime.now().isoformat()
                save_credentials(USERS_PASSWORD_PATH, users_credentials)
        except Exception as e:
            logging.error(f"Ошибка при обработке даты сброса для пользователя {user_credential['login']}: {e}")
            await message.answer("Произошла ошибка при проверке вашего состояния. Пожалуйста, попробуйте позже.")
            return

    # Найти невыданный пароль
    available_password = next(
        (pwd for pwd in student_credentials.get("logins_passwords", []) if not pwd.get("issued", False)),
        None
    )

    if not available_password:
        await message.answer("Нет доступных паролей для выдачи.")
        return

    # Выдача пароля
    available_password["issued"] = True
    user_credential["issued_count"] = issued_count + 1
    save_credentials(STUDENT_PASSWORD_PATH, student_credentials)
    save_credentials(USERS_PASSWORD_PATH, users_credentials)

    await message.answer(
        f"Ваш логин: {available_password['login']}\nВаш пароль: {available_password['password']}\n"
        f"Выдано паролей: {user_credential['issued_count']}/4"
    )
    logging.info(f"Пользователю {user_credential['login']} выдан пароль {available_password['login']}.")

@router.message(Command('reset_passwords'))
async def reset_passwords(message: Message, state: FSMContext):
    admin_ids = [5450018125, 226266887]  # Добавьте здесь ID администраторов
    if message.from_user.id not in admin_ids:
        await message.answer("У вас нет прав на выполнение этой команды.")
        return

    users_credentials = load_credentials(USERS_PASSWORD_PATH)

    # Сбрасываем счетчики и дату сброса для всех пользователей
    for cred in users_credentials.get("logins_passwords", []):
        cred["issued_count"] = 0
        cred["last_reset_date"] = datetime.datetime.now().isoformat()

    save_credentials(USERS_PASSWORD_PATH, users_credentials)

    await message.answer("Все счетчики выданных паролей были сброшены, и дата сброса обновлена.")
    logging.info("Администратор сбросил счетчики выданных паролей для всех пользователей.")
