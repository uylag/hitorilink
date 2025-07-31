import asyncio
import sys
import os

# Добавляем корневой путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import init_db, reset_db

async def main():
    # Проверяем аргументы
    reset_flag = "--reset" in sys.argv
    
    if reset_flag:
        confirm = input("⚠ Вы уверены, что хотите сбросить БД (drop + create)? [y/N]: ").strip().lower()
        if confirm == "y":
            await reset_db()
        else:
            print("⏩ Отменено пользователем, ничего не сделано.")
    else:
        print("✅ Инициализация БД (create_if_not_exists)...")
        await init_db()
        print("✅ Таблицы проверены/созданы (если их не было).")

if __name__ == "__main__":
    asyncio.run(main())
