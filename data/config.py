from environs import Env
from colorama import Fore
import colorama
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from errors import ConfigError

colorama.init(autoreset=True)
env = Env()

cfg_absloc = os.path.abspath(__file__)
cfg_loc = os.path.dirname(cfg_absloc)

# Launch: MODE=prod python run.py
MODE = os.getenv("MODE")

if MODE:
    MODE = MODE.lower()

if MODE == "prod":
    env.read_env(os.path.join(cfg_loc, ".env.prod"))
elif MODE == "test":
    env.read_env(os.path.join(cfg_loc, ".env.test"))
else:
    print(f"{Fore.RED}ConfigError: {Fore.CYAN}You must choose one of the modes! Mode is not set{Fore.RESET}")
    raise ConfigError(f"You must choose one of the modes! Mode is not set.")

print(f"{Fore.GREEN}✅ Loaded configuration for MODE={MODE.upper()}{Fore.RESET}")

class Config():
    def __init__(self):
        self.BOT_API_KEY: str = env.str("BOT_API_KEY")
        self.BOT_ID: str = self.BOT_API_KEY.split(":", maxsplit=1)[0]
        self.BOT_USERNAME: str = env.str("BOT_USERNAME", None)
        self.TERMS_PATH = "/home/kiyoshima/All_Work_Folders/Projects/PythonProjects/Bots/HitoriLink/terms_and_consent.pdf"

        self.INTERESTS: list[str] = [
            "Спорт",
            "Игры",
            "Музыка",
            "Фильмы",
            "Сериалы",
            "Книги",
            "Путешествия",
            "Природа",
            "Животные",
            "Кулинария",
            "Танцы",
            "Фотография",
            "Мода",
            "Искусство",
            "Рисование",
            "Общение",
            "Психология",
            "Саморазвитие",
            "Языки",
            "Учёба",
            "Карьера",
            "Программирование",
            "Технологии",
            "Социальные сети",
            "Блогинг",
            "Юмор",
            "Мемы",
            "Волонтерство",
            "Медицина",
            "Автомобили",
            "Киберспорт",
            "ЗОЖ",
            "Йога",
            "Медитация",
            "Фитнес",
            "Наука",
            "ИИ",
            "Гаджеты",
            "Косплей",
            "Культура",
            "История",
            "Праздники",
            "Настольные игры",
            "Фестивали",
            "Музыкальные инструменты",
            "Рукоделие",
            "Садоводство",
            "Экология",
            "Философия"
        ]

        self.ADMINS:     list = list(map(int, env.list("ADMINS", [])))
        self.OWNER:       int = env.int("OWNER", None)
        self.OWNER_UN:    str = env.str("OWNER_UN", None)
        self.DEVS:       list = env.list("DEVELOPERS", [])

        self.USE_LINK:   bool = env.bool("USE_LINK", False)

        self.LOGGING_LEVEL: int = env.int("LOGGING_LEVEL", 10)

        if self.USE_LINK:
            self.PG_LINK: str = env.str("PG_LINK", None)
        else:
            self.PG_HOST: str = env.str("PG_HOST", None)
            self.PG_PORT: int = env.int("PG_PORT", 5432)
            self.PG_USER: str = env.str("PG_USER", None)
            self.PG_PASSWORD: str = env.str("PG_PASSWORD", None)
            self.PG_DATABASE: str = env.str("PG_DATABASE", None)
            self.PG_SSL: str = env.str("PG_SSL", "require")

        # self.FSM_HOST: str = env.str("FSM_HOST", None)
        # self.FSM_PORT: int = env.int("FSM_PORT", 0)
        # self.FSM_PWD: str = env.str("FSM_PWD", None)

        self.USE_WEBHOOK: bool = env.bool("USE_WEBHOOK", False)
        if self.USE_WEBHOOK:
            self.MAIN_WEBHOOK_ADDR: str = env.str("MAIN_WEBHOOK_ADDR")
            self.MAIN_WEBHOOK_SECRET: str = env.str("MAIN_WEBHOOK_SECRET", None)
            self.MAIN_WEBHOOK_LISTENING_HOST: str = env.str("MAIN_WEBHOOK_LISTENING_HOST", None)
            self.MAIN_WEBHOOK_LISTENING_PORT: int = env.int("MAIN_WEBHOOK_LISTENING_PORT", 0)
            self.MAX_UPDATES_IN_QUEUE: int = env.int("MAX_UPDATES_IN_QUEUE", 100)

        self.DROP_PENDING_UPDATES: bool = env.bool("DROP_PREVIOUS_UPDATES", True)


cfg = Config()
print(f"{Fore.GREEN}✅ Loaded configuration for MODE={MODE.upper()} → BOT {cfg.BOT_USERNAME}{Fore.RESET}")
