"""Вспомогательный модуль для безопасного ввода данных с консоли."""

from datetime import datetime, date
from typing import Optional


def input_int(
    prompt: str,
    min_val: Optional[int] = None,
    max_val: Optional[int] = None,
) -> int:
    """Запрашивает у пользователя целое число с проверкой диапазона и повтором при ошибке."""
    while True:
        raw_value = input(prompt).strip()
        try:
            val = int(raw_value)
            if min_val is not None and val < min_val:
                print(f"[!] Значение не должно быть меньше {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"[!] Значение не должно быть больше {max_val}.")
                continue
            return val
        except ValueError:
            print("[!] Ошибка: введите корректное целое число.")


def input_float(
    prompt: str,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
) -> float:
    """Запрашивает у пользователя вещественное число с проверкой диапазона."""
    while True:
        raw_value = input(prompt).strip().replace(",", ".")
        try:
            val = float(raw_value)
            if min_val is not None and val < min_val:
                print(f"[!] Значение не должно быть меньше {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"[!] Значение не должно быть больше {max_val}.")
                continue
            return val
        except ValueError:
            print("[!] Ошибка: введите число (например, 4.5).")


def input_date(prompt: str) -> date:
    """Запрашивает у пользователя дату в формате ДД.ММ.ГГГГ или ГГГГ-ММ-ДД."""
    while True:
        raw_value = input(prompt).strip()
        for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(raw_value, fmt)
                return dt.date()
            except ValueError:
                pass
        print("[!] Ошибка: введите дату в формате ДД.ММ.ГГГГ (например, 24.09.2026).")


def input_str(prompt: str, allow_empty: bool = False) -> str:
    """Запрашивает непустую строку у пользователя."""
    while True:
        val = input(prompt).strip()
        if not val and not allow_empty:
            print("[!] Поле не может быть пустым. Повторите ввод.")
            continue
        return val
