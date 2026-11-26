"""Скрипт инспекции структуры базы данных SQLite (ПР9, подраздел 5.8.1).

Исследует таблицы, типы полей, ограничения первичных ключей и количество строк.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db.sqlite3"


def inspect_database():
    print(f"=== Инспекция базы данных SQLite: {DB_PATH.name} ===")
    if not DB_PATH.exists():
        print(f"База данных {DB_PATH} не найдена.")
        return

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        tables = conn.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()

        for (table_name,) in [(t["name"],) for t in tables]:
            print(f"\nТаблица: {table_name}")
            columns = conn.execute(f'PRAGMA table_info("{table_name}")').fetchall()
            print("  Столбцы:")
            for col in columns:
                print(
                    f"    - имя={col['name']}, тип={col['type']}, "
                    f"NOT NULL={col['notnull']}, PK={col['pk']}"
                )
            count = conn.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[0]
            print(f"  Количество записей: {count}")


if __name__ == "__main__":
    inspect_database()
