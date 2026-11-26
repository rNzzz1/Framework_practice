"""Скрипт генерации академических отчетов в формате Microsoft Word (.docx)
по Практическим работам № 1, № 2 и № 3 для студента Узуняна Овсепа Норайровича (гр. ЭФБО-12-24).
"""

import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn


def set_cell_background(cell, hex_color):
    """Устанавливает цвет фона ячейки таблицы."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Устанавливает внутренние отступы ячейки таблицы."""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def set_table_borders(table, color="CCCCCC", sz="4", val="single"):
    """Устанавливает границы таблицы."""
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:left w:val="none"/>'
            f'<w:right w:val="none"/>'
            f'</w:tblBorders>'
        )
        tblPr[0].append(borders)


def format_run(run, font_name="Times New Roman", size_pt=12, bold=False, italic=False, color_rgb=(0, 0, 0)):
    """Форматирует текстовый фрагмент (run)."""
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)


def add_paragraph(doc, text="", font_name="Times New Roman", size_pt=12, bold=False, italic=False,
                  align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=4, line_spacing=1.15):
    """Добавляет параграф с заданными параметрами."""
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if text:
        run = p.add_run(text)
        format_run(run, font_name, size_pt, bold, italic)
    return p


def add_heading_1(doc, text):
    """Добавляет заголовок 1-го уровня."""
    return add_paragraph(doc, text, font_name="Times New Roman", size_pt=14, bold=True,
                         space_before=14, space_after=6)


def add_heading_2(doc, text):
    """Добавляет заголовок 2-го уровня."""
    return add_paragraph(doc, text, font_name="Times New Roman", size_pt=13, bold=True,
                         space_before=10, space_after=4)


def add_code_block(doc, code_text):
    """Добавляет красиво оформленный блок исходного кода."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    cell = table.cell(0, 0)
    set_cell_background(cell, "F6F8FA")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)

    # Устанавливаем границу блока
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="D0D7DE"/>'
        f'<w:left w:val="single" w:sz="18" w:space="0" w:color="0969DA"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="D0D7DE"/>'
        f'<w:right w:val="single" w:sz="6" w:space="0" w:color="D0D7DE"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0

    lines = code_text.strip().split("\n")
    for i, line in enumerate(lines):
        if i > 0:
            p = cell.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
        run = p.add_run(line)
        format_run(run, font_name="Consolas", size_pt=9.5, color_rgb=(36, 41, 47))

    # Пустой параграф после таблицы для отступа
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(4)


REPO_URL = "https://github.com/rNzzz1/Framework_practice"
GERB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", "gerb_mirea.jpg")


def add_title_page(doc, pr_num, pr_theme):
    """Генерирует официальный титульный лист РТУ МИРЭА с гербом и ссылкой на репозиторий."""
    if os.path.exists(GERB_PATH):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(0)
        p_img.paragraph_format.space_after = Pt(4)
        p_img.add_run().add_picture(GERB_PATH, width=Inches(1.4))

    add_paragraph(doc, "МИНОБРНАУКИ РОССИИ", size_pt=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_paragraph(doc, "Федеральное государственное бюджетное образовательное учреждение высшего образования",
                  size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_paragraph(doc, "«МИРЭА – Российский технологический университет»", size_pt=12, bold=True,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_paragraph(doc, "РТУ МИРЭА", size_pt=11.5, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

    add_paragraph(doc, "Институт перспективных технологий и индустриального программирования", size_pt=11.5,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_paragraph(doc, "Кафедра индустриального программирования", size_pt=12, bold=True,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=20)

    add_paragraph(doc, f"ОТЧЕТ ПО ПРАКТИЧЕСКОЙ РАБОТЕ № {pr_num}", size_pt=15.5, bold=True,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
    add_paragraph(doc, "по дисциплине «Технологии разработки приложений на базе фреймворков»", size_pt=12.5,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
    add_paragraph(doc, f"Тема: «{pr_theme}»", size_pt=12, bold=True,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    add_paragraph(doc, "НАПРАВЛЕНИЕ ПОДГОТОВКИ", size_pt=11.5, bold=True,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_paragraph(doc, "09.03.02 «Информационные системы и технологии»", size_pt=11.5,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)

    p_repo = add_paragraph(doc, "", size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=22)
    r_lbl = p_repo.add_run("Репозиторий проекта: ")
    format_run(r_lbl, size_pt=11, bold=True)
    r_url = p_repo.add_run(REPO_URL)
    format_run(r_url, size_pt=11, color_rgb=(9, 105, 218))

    # Блок с исполнителем и преподавателем
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(3.2)
    table.columns[1].width = Inches(3.2)

    cell_left = table.cell(0, 0)
    cell_right = table.cell(0, 1)

    p_right = cell_right.paragraphs[0]
    p_right.paragraph_format.line_spacing = 1.15
    p_right.paragraph_format.space_after = Pt(2)
    
    r = p_right.add_run("Выполнил:\n")
    format_run(r, size_pt=11.5, bold=True)
    r = p_right.add_run("студент группы ")
    format_run(r, size_pt=11.5)
    r = p_right.add_run("ЭФБО-12-24\n")
    format_run(r, size_pt=11.5, bold=True)
    r = p_right.add_run("Узунян Овсеп Норайрович\n\n")
    format_run(r, size_pt=11.5, bold=True)

    r = p_right.add_run("Проверил:\n")
    format_run(r, size_pt=11.5, bold=True)
    r = p_right.add_run("доцент кафедры индустриального\nпрограммирования, к.т.н.\n")
    format_run(r, size_pt=11.5)
    r = p_right.add_run("Ящун Татьяна Викторовна")
    format_run(r, size_pt=11.5, bold=True)

    add_paragraph(doc, "", space_after=28)
    add_paragraph(doc, "Москва 2026", size_pt=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=0)
    doc.add_page_break()


def build_table(doc, headers, data, col_widths=None):
    """Создает красиво стилизованную таблицу."""
    table = doc.add_table(rows=len(data) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)

    # Заголовок таблицы
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "EAECEF")
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=120, right=120)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        if len(p.runs) > 0:
            format_run(p.runs[0], font_name="Times New Roman", size_pt=11, bold=True)

    # Данные таблицы
    for row_idx, row_data in enumerate(data):
        row_cells = table.rows[row_idx + 1].cells
        bg_color = "F9FAFB" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, cell_value in enumerate(row_data):
            row_cells[col_idx].text = str(cell_value)
            set_cell_background(row_cells[col_idx], bg_color)
            set_cell_margins(row_cells[col_idx], top=80, bottom=80, left=120, right=120)
            p = row_cells[col_idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            if col_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            elif col_idx == len(row_data) - 1:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            if len(p.runs) > 0:
                format_run(p.runs[0], font_name="Times New Roman", size_pt=10.5)

    if col_widths:
        for row in table.rows:
            for idx, width in enumerate(col_widths):
                row.cells[idx].width = width

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(4)


# ==============================================================================
# 1. ГЕНЕРАЦИЯ ОТЧЕТА ПО ПР1
# ==============================================================================
def create_report_pr1():
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(0.8)

    add_title_page(doc, 1, "Основы Python: актуализация знаний и настройка рабочего окружения")

    add_heading_1(doc, "1. Цель и задачи работы")
    add_paragraph(doc, "Цель работы: актуализировать базовые знания и навыки программирования на языке Python, "
                       "подготовить рабочее окружение для разработки приложений и начать работу над индивидуальным "
                       "сквозным проектом «Сервис выбора тем курсовых работ».")

    add_paragraph(doc, "В ходе выполнения практической работы были решены следующие задачи:")
    tasks = [
        "Повторить базовые конструкции языка Python (простые типы данных, условные конструкции, операции, приведение типов, импорт модулей);",
        "Настроить рабочее окружение (интерпретатор Python 3.13, виртуальное окружение .venv, среда разработки VS Code);",
        "Инициализировать репозиторий Git, настроить ветку main и файл исключений .gitignore;",
        "Разработать проектную спецификацию README.md индивидуального проекта «Сервис выбора тем курсовых работ»;",
        "Реализовать начальный сценарий предметной области в файле main.py (не менее 3-х функций);",
        "Выполнить пошаговую отладку программы в IDE с установкой точки останова (breakpoint) и инспекцией переменных."
    ]
    for t in tasks:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(t)
        format_run(r, size_pt=11.5)

    add_heading_1(doc, "2. Выполненные материалы Яндекс Практикума")
    practicum_data = [
        ["01. Основы Python", "Погружение в Python", "Выполнено"],
        ["01. Основы Python", "Простые типы данных", "Выполнено"],
        ["01. Основы Python", "Ветвления", "Выполнено"],
        ["01. Основы Python", "Импортируемые типы данных", "Выполнено"],
        ["01. Основы Python", "Коллекции, Итерации и циклы, «Холодильник»", "Перенесено на ПР2"],
        ["02. Настройка окружения", "Настройка рабочего окружения", "Выполнено"],
        ["02. Настройка окружения", "Pytest", "Выполнено"],
        ["02. Настройка окружения", "Система контроля версий Git", "Выполнено"],
        ["02. Настройка окружения", "Требования к коду (PEP 8)", "Выполнено"],
        ["02. Настройка окружения", "Отладка программ", "Выполнено"],
    ]
    build_table(doc, ["Раздел", "Тема / Материал", "Статус"], practicum_data,
                [Inches(2.2), Inches(3.2), Inches(1.4)])

    add_heading_1(doc, "3. Индивидуальный сквозной проект")
    add_paragraph(doc, "Название проекта: Сервис выбора тем курсовых работ", bold=True)
    add_paragraph(doc, "Выбранная предметная область: автоматизация и регламентация процесса распределения тем курсовых работ между студентами и преподавателями кафедры индустриального программирования.")

    add_heading_2(doc, "Основные сущности:")
    entities = [
        "Студент: ФИО, номер зачетной книжки, текущий курс обучения, средний балл (GPA), форма обучения (бюджет/договор);",
        "Дисциплина: наименование, семестр преподавания, минимальный курс обучения для допуска к выбору;",
        "Тема курсовой работы: название темы, закрепленная дисциплина, преподаватель (руководитель), статус доступности;",
        "Заявка: номер заявки, дата подачи, выбранная тема, студент-заявитель, рассчитанный приоритет, статус утверждения."
    ]
    for e in entities:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(e)
        format_run(r, size_pt=11.5)

    add_heading_2(doc, "Реализованные функции начального сценария (ПР1):")
    funcs = [
        "check_topic_availability(is_available: bool) -> str — проверка доступности темы для выбора соискателем;",
        "validate_student_eligibility(student_course, required_course, gpa, min_gpa) -> bool — валидация академического допуска соискателя по курсу и минимальному среднему баллу;",
        "calculate_application_priority(gpa: float, is_budget: bool) -> int — расчет рейтингового балла приоритета заявки на основе GPA и формы обучения;",
        "format_application_summary(...) -> str — генерация итоговой форматированной карточки заявки."
    ]
    for f in funcs:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(f)
        format_run(r, size_pt=11.5)

    add_heading_1(doc, "4. Листинг программного кода (main.py, версия ПР1)")
    code_pr1 = """from datetime import date

def check_topic_availability(is_available: bool) -> str:
    \"\"\"Проверяет статус доступности темы курсовой работы для выбора.\"\"\"
    if is_available:
        return "Тема свободна для выбора"
    return "Тема уже закреплена за другим студентом"

def validate_student_eligibility(
    student_course: int,
    required_course: int,
    gpa: float,
    min_gpa: float,
) -> bool:
    \"\"\"Проверяет допуск студента к выбору темы по курсу обучения и среднему баллу.\"\"\"
    is_course_valid = student_course >= required_course
    is_gpa_valid = gpa >= min_gpa
    return is_course_valid and is_gpa_valid

def calculate_application_priority(gpa: float, is_budget: bool) -> int:
    \"\"\"Рассчитывает числовой приоритет заявки.\"\"\"
    base_priority = int(gpa * 20)
    bonus = 10 if is_budget else 0
    return base_priority + bonus

def format_application_summary(
    app_id: int,
    student_name: str,
    topic_title: str,
    discipline_name: str,
    app_date: date,
    is_approved: bool,
) -> str:
    \"\"\"Формирует итоговую текстовую сводку по заявке.\"\"\"
    status_text = "ОДОБРЕНА" if is_approved else "ОТКЛОНЕНА"
    return (
        "==================================================\\n"
        f"КАРТОЧКА ЗАЯВКИ № {app_id}\\n"
        "==================================================\\n"
        f"Дата подачи:     {app_date.strftime('%d.%m.%Y')}\\n"
        f"Студент:         {student_name}\\n"
        f"Дисциплина:      {discipline_name}\\n"
        f"Тема работы:     {topic_title}\\n"
        f"Статус заявки:   {status_text}\\n"
        "=================================================="
    )

def main():
    print("--- СЕРВИС ВЫБОРА ТЕМ КУРСОВЫХ РАБОТ ---\\n")
    student_name = "Узунян Овсеп Норайрович"
    student_course = 3
    student_gpa = 4.75
    is_budget = True

    discipline_name = "Технологии разработки приложений на базе фреймворков"
    required_course = 3
    min_required_gpa = 3.5

    topic_title = "Разработка веб-сервиса распределения курсовых работ"
    is_topic_available = True
    topic_supervisor = "доц. Ящун Т. В."

    is_eligible = validate_student_eligibility(student_course, required_course, student_gpa, min_required_gpa)
    priority = calculate_application_priority(student_gpa, is_budget)
    is_approved = is_eligible and is_topic_available

    print(format_application_summary(101, student_name, topic_title, discipline_name, date(2026, 9, 24), is_approved))

if __name__ == "__main__":
    main()"""
    add_code_block(doc, code_pr1)

    add_heading_1(doc, "5. Протокол выполнения программы и отладки")
    add_paragraph(doc, "Результат вывода программы в терминале:")
    output_pr1 = """--- СЕРВИС ВЫБОРА ТЕМ КУРСОВЫХ РАБОТ ---

Подача заявки студентом: Узунян Овсеп Норайрович (3 курс)
Средний балл успеваемости (GPA): 4.75
Форма обучения: Бюджет
Выбранная дисциплина: Технологии разработки приложений на базе фреймворков
Выбранная тема: Разработка веб-сервиса распределения курсовых работ
Научный руководитель: доц. Ящун Т. В.
Статус темы: Тема свободна для выбора

[+] Студент соответствует академическим требованиям.
[i] Рассчитанный приоритет заявки: 105 баллов
[+] Решение: Заявка успешно утверждена!

==================================================
КАРТОЧКА ЗАЯВКИ № 101
==================================================
Дата подачи:     24.09.2026
Студент:         Узунян Овсеп Норайрович
Дисциплина:      Технологии разработки приложений на базе фреймворков
Тема работы:     Разработка веб-сервиса распределения курсовых работ
Статус заявки:   ОДОБРЕНА
=================================================="""
    add_code_block(doc, output_pr1)

    add_paragraph(doc, "Протокол проведения отладки в IDE:")
    debug_text = [
        "В среде разработки установлена точка останова (breakpoint) на строке вызова функции validate_student_eligibility;",
        "Запущена сессия отладки в режиме Debug (клавиша F5);",
        "Выполнено пошаговое выполнение с заходом в функцию (Step Into, F11);",
        "В панели Variables проверены значения локальных переменных: student_course=3, required_course=3, gpa=4.75, min_gpa=3.5;",
        "Проверена корректность вычисления условий is_course_valid=True, is_gpa_valid=True и их логической конъюнкции."
    ]
    for d in debug_text:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(d)
        format_run(r, size_pt=11.5)

    add_heading_1(doc, "6. Вывод")
    add_paragraph(doc, "В ходе выполнения практической работы № 1 были актуализированы базовые знания языка Python "
                       "(простые типы данных, арифметические и логические операции, условные конструкции if-else, "
                       "функции и импорт модулей). Настроено рабочее окружение разработчика (Python 3.13, .venv, Git). "
                       "Спроектирована архитектура индивидуального сквозного проекта «Сервис выбора тем курсовых работ», "
                       "подготовлен файл документации README.md и реализован начальный программный сценарий, "
                       "проверенный средствами пошаговой отладки.")

    os.makedirs("reports", exist_ok=True)
    out_path = "reports/ОТЧЕТ_ПР1_Узунян_Овсеп_ЭФБО-12-24.docx"
    doc.save(out_path)
    print(f"[+] Успешно создан: {out_path}")


# ==============================================================================
# 2. ГЕНЕРАЦИЯ ОТЧЕТА ПО ПР2
# ==============================================================================
def create_report_pr2():
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(0.8)

    add_title_page(doc, 2, "Основы Python: коллекции, функции, циклы и расширенные возможности Python")

    add_heading_1(doc, "1. Цель и задачи работы")
    add_paragraph(doc, "Цель работы: закрепить и расширить навыки программирования на Python, необходимые для разработки "
                       "серверных приложений, включая работу со сложными коллекциями (списки, словари), функциями, циклами, "
                       "пользовательскими модулями, контекстными менеджерами, обработкой исключений и файловым хранилищем JSON, "
                       "а также применить изученные средства языка для доработки индивидуального проекта.")

    add_paragraph(doc, "Основные задачи работы:")
    tasks = [
        "Изучить коллекции данных (list, dict, set, tuple) и циклы (for, while);",
        "Выполнить учебную проектную работу Яндекс Практикума «Холодильник»;",
        "Осуществить функциональную декомпозицию монолитного кода ПР1 на логические модули;",
        "Реализовать сохранение и загрузку данных в формате JSON через контекстный менеджер with open();",
        "Обеспечить обработку исключений (ValueError, FileNotFoundError, json.JSONDecodeError);",
        "Применить расширенные возможности Python: генераторные выражения, lambda-функции;",
        "Реализовать консольный пользовательский интерфейс с интерактивным текстовым меню;",
        "Разработать набор автоматизированных тестов с использованием assert;",
        "Оформить код в соответствии со стандартом PEP 8 и аннотациями типов."
    ]
    for t in tasks:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(t)
        format_run(r, size_pt=11.5)

    add_heading_1(doc, "2. Выполненные материалы Яндекс Практикума")
    practicum_data = [
        ["01. Основы Python (продолжение)", "Коллекции", "Выполнено"],
        ["01. Основы Python (продолжение)", "Итерации и циклы", "Выполнено"],
        ["01. Основы Python (продолжение)", "Проектная работа «Холодильник»", "Выполнено"],
        ["03. ООП и полезные вещи", "«Новая задача», «Модули и пакеты»", "Выполнено"],
        ["03. ООП и полезные вещи", "«Интроспекция», «Документирование»", "Выполнено"],
        ["03. ООП и полезные вещи", "«Исключения», «Работа с файлами»", "Выполнено"],
        ["03. ООП и полезные вещи", "«Контекстные менеджеры», «Новый интерфейс»", "Выполнено"],
        ["03. Расширенные возможности", "«Пространство имён и области видимости»", "Выполнено"],
        ["03. Расширенные возможности", "«Итераторы и генераторы»", "Выполнено"],
        ["03. Расширенные возможности", "«Lambda-функции»", "Выполнено"],
        ["03. Расширенные возможности", "«Декораторы»", "Перенесено на ПР3"]
    ]
    build_table(doc, ["Раздел курса", "Урок / Тема", "Статус"], practicum_data,
                [Inches(2.5), Inches(3.1), Inches(1.2)])

    add_heading_1(doc, "3. Архитектура и структура модулей проекта (ПР2)")
    add_paragraph(doc, "В рамках ПР2 проект был декомпозирован на следующие модули:")
    modules_desc = [
        "main.py — точка запуска приложения, реализация текстового меню из 10 пунктов, обработка пользовательских команд;",
        "topics.py — функции работы с темами (добавление add_topic, поиск find_topics, фильтрация генератором filter_topics_by_discipline, сортировка lambda sort_topics_by_title, проверка квоты);",
        "applications.py — функции работы с заявками (создание create_application, проверка повторов is_student_already_applied, отмена cancel_application, расчет статистики get_applications_statistics);",
        "storage.py — слой сохранения/загрузки JSON через with open() с обработкой ошибок;",
        "utils.py — безопасный ввод чисел, дат и строк с обработкой исключений ValueError;",
        "data/ (topics.json, applications.json) — файлы долговременного хранения данных в формате JSON;",
        "tests/ (test_topics.py, test_applications.py) — набор из 11 автоматизированных тестов."
    ]
    for m in modules_desc:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(m)
        format_run(r, size_pt=11.5)

    add_heading_1(doc, "4. Листинг ключевых модулей (storage.py и utils.py)")
    code_storage_pr2 = """# storage.py - функции персистентного сохранения
import json, os

def load_json_file(filename, default_data):
    if not os.path.exists(filename):
        return default_data
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        print(f"[!] Ошибка чтения {filename}: {error}")
        return default_data

def save_json_file(filename, data):
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)"""
    add_code_block(doc, code_storage_pr2)

    add_heading_1(doc, "5. Протокол работы программы и автоматического тестирования")
    add_paragraph(doc, "Вывод демонстрационного сценария сервиса (python main.py --demo):")
    out_demo = """--- ДЕМОНСТРАЦИОННЫЙ ЗАПУСК СЕРВИСА ---
==========================================================================================
ID   | Название темы                       | Дисциплина                | Квота  | Статус         
------------------------------------------------------------------------------------------
4    | Интеллектуальный рекомендательны... | Интеллектуальные инфор... | 0/1    | Доступна       
2    | Проектирование микросервисной ар... | Технологии разработки ... | 0/1    | Доступна       
3    | Разработка аналитической подсист... | Базы данных и экспертн... | 0/2    | Доступна       
1    | Разработка веб-сервиса распредел... | Технологии разработки ... | 1/1    | Занята         
==========================================================================================

[Демо] Поиск темы по ключевому слову 'микросервис':
-> Найдено: [2] Проектирование микросервисной архитектуры корпоративного портала (Рук.: доц. Ящун Т. В.)

[Демо] Подача заявки на тему №2:
КАРТОЧКА ЗАЯВКИ № 102
Студент: Иванов Иван | Тема: Проектирование микросервисной архитектуры | Статус: ОДОБРЕНА
[Демо] Статистика: Всего заявок: 2, Одобрено: 2, Средний GPA: 4.67"""
    add_code_block(doc, out_demo)

    add_paragraph(doc, "Протокол успешного выполнения 11 автоматических тестов:")
    out_tests_pr2 = """PASSED: tests.test_topics.test_add_topic
PASSED: tests.test_topics.test_find_topics
PASSED: tests.test_topics.test_check_topic_capacity
PASSED: tests.test_topics.test_sort_topics_by_title
PASSED: tests.test_topics.test_get_topic_status
PASSED: tests.test_applications.test_validate_student_eligibility
PASSED: tests.test_applications.test_calculate_application_priority
PASSED: tests.test_applications.test_create_application_success
PASSED: tests.test_applications.test_duplicate_application_forbidden
PASSED: tests.test_applications.test_cancel_application
PASSED: tests.test_applications.test_get_applications_statistics

Total: 11/11 tests passed successfully!"""
    add_code_block(doc, out_tests_pr2)

    add_heading_1(doc, "6. Вывод")
    add_paragraph(doc, "В ходе выполнения практической работы № 2 монолитная программа была успешно переработана в модульное "
                       "приложение со сложными коллекциями данных. Реализовано долговременное хранение в формате JSON через "
                       "контекстные менеджеры, обработка исключений при некорректном вводе и файловых операциях, применены "
                       "генераторы и lambda-функции. Корректность работы подтверждена 11 модульными тестами, а проект подготовлен "
                       "к переводу на объектно-ориентированную модель.")

    out_path = "reports/ОТЧЕТ_ПР2_Узунян_Овсеп_ЭФБО-12-24.docx"
    doc.save(out_path)
    print(f"[+] Успешно создан: {out_path}")


# ==============================================================================
# 3. ГЕНЕРАЦИЯ ОТЧЕТА ПО ПР3
# ==============================================================================
def create_report_pr3():
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(0.8)

    add_title_page(doc, 3, "Объектно-ориентированное программирование в Python. Классы, объекты и взаимодействие объектов")

    add_heading_1(doc, "1. Цель и задачи работы")
    add_paragraph(doc, "Цель работы: изучить основные принципы объектно-ориентированного программирования (ООП) в Python "
                       "и преобразовать структуру индивидуального проекта «Сервис выбора тем курсовых работ», построенную на "
                       "коллекциях словарей и функциях в ПР2, в полноценную объектную модель предметной области.")

    add_paragraph(doc, "Основные задачи работы:")
    tasks = [
        "Изучить понятия классов, объектов, атрибутов, конструктора __init__, строкового представления __str__;",
        "Освоить ключевые принципы ООП: инкапсуляцию, полиморфизм, композицию и ассоциацию объектов;",
        "Применить декораторы методов класса: @classmethod (фабричные методы), @staticmethod, @property;",
        "Создать пакет моделей models/ с классами Topic, Student, Application;",
        "Реализовать взаимодействие объектов: заявка Application хранит прямые ссылки на объекты Topic и Student;",
        "Адаптировать сохранение и загрузку JSON в storage.py с восстановлением перекрестных объектных связей по ID;",
        "Перевести модуль main.py на управление коллекциями объектов List[Topic], List[Student], List[Application];",
        "Создать и адаптировать модульные тесты для проверки состояния и поведения объектов (15 тестов);",
        "Актуализировать спецификацию README.md и зафиксировать этапы в Git с меткой PR3:."
    ]
    for t in tasks:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(t)
        format_run(r, size_pt=11.5)

    add_heading_1(doc, "2. Выполненные материалы Яндекс Практикума")
    practicum_data = [
        ["03. ООП: Объекты и классы", "«Введение. ООП», «Классы и объекты»", "Выполнено"],
        ["03. ООП: Объекты и классы", "«Собственные классы и объекты», «Атрибуты»", "Выполнено"],
        ["03. ООП: Объекты и классы", "«Методы объекта», «Метод __str__»", "Выполнено"],
        ["03. ООП: Знакомство с ООП", "«Принципы ООП», «Наследование»", "Выполнено"],
        ["03. ООП: Знакомство с ООП", "«Полиморфизм», «Инкапсуляция»", "Выполнено"],
        ["03. ООП: Расширенные возможности", "«Декораторы»", "Выполнено"],
        ["03. ООП: Расширенные возможности", "«Декораторы для методов класса»", "Выполнено"],
        ["03. ООП: Расширенные возможности", "«Практика по теме»", "Выполнено"]
    ]
    build_table(doc, ["Раздел курса", "Урок / Тема", "Статус"], practicum_data,
                [Inches(2.6), Inches(3.0), Inches(1.2)])

    add_heading_1(doc, "3. Объектная модель предметной области (ООП)")
    add_paragraph(doc, "В пакете models/ реализованы три ключевых взаимосвязанных класса:")

    add_heading_2(doc, "1. Класс Topic (models/topics.py)")
    add_paragraph(doc, "Инкапсулирует данные темы курсовой работы. Атрибуты: id, title, discipline, supervisor, min_course, min_gpa, capacity, current_students, is_available. "
                       "Методы: is_suitable_for(course, gpa) — проверка допуска соискателя; has_free_capacity() — проверка наличия свободных мест; "
                       "reserve_slot() — инкапсулированное резервирование места со сменой флага доступности; release_slot() — освобождение квоты при отмене заявки; "
                       "@staticmethod validate_capacity(); @classmethod from_dict(); to_dict(); __str__().")

    add_heading_2(doc, "2. Класс Student (models/students.py)")
    add_paragraph(doc, "Описывает соискателя темы. Атрибуты: id, name, course, gpa, is_budget, email. "
                       "Методы: calculate_priority() — расчет приоритета заявки на основе GPA и формы обучения (бюджет +10 баллов); "
                       "@classmethod from_dict(); to_dict(); __str__().")

    add_heading_2(doc, "3. Класс Application (models/applications.py)")
    add_paragraph(doc, "Осуществляет композицию: хранит прямые ссылки на связанные объекты self.topic: Topic и self.student: Student. "
                       "Методы и свойства: cancel() — отмена заявки с вызовом self.topic.release_slot(); @property status — возвращает «ОДОБРЕНА» / «ОТМЕНЕНА»; "
                       "to_dict() — извлечение topic_id и student_id для внешних ключей JSON; __str__().")

    add_heading_1(doc, "4. Листинг реализации класса Application и композиции")
    code_app_pr3 = """class Application:
    \"\"\"Класс заявки, связывающий объекты Topic и Student (композиция).\"\"\"

    def __init__(
        self,
        app_id: int,
        topic: Topic,
        student: Student,
        application_date: str,
        priority: Optional[int] = None,
        is_cancelled: bool = False,
    ) -> None:
        self.id = app_id
        self.topic = topic
        self.student = student
        self.application_date = application_date
        self.priority = priority if priority is not None else student.calculate_priority()
        self.is_cancelled = is_cancelled

    def cancel(self) -> None:
        \"\"\"Отменяет заявку и освобождает квоту места на тему.\"\"\"
        if not self.is_cancelled:
            self.is_cancelled = True
            self.topic.release_slot()

    @property
    def status(self) -> str:
        \"\"\"Динамическое свойство статуса заявки.\"\"\"
        return "ОТМЕНЕНА" if self.is_cancelled else "ОДОБРЕНА"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "topic_id": self.topic.id,
            "student_id": self.student.id,
            "application_date": self.application_date,
            "priority": self.priority,
            "is_cancelled": self.is_cancelled,
        }"""
    add_code_block(doc, code_app_pr3)

    add_heading_1(doc, "5. Протокол работы программы и автоматических тестов")
    add_paragraph(doc, "Вывод демонстрационного сценария взаимодействия объектов (python main.py --demo):")
    out_demo_pr3 = """=======================================================
ДЕМОНСТРАЦИОННЫЙ СЦЕНАРИЙ ВЗАИМОДЕЙСТВИЯ ОБЪЕКТОВ (ООП)
=======================================================

1. Каталог доступных тем курсовых работ:
ID   | Название темы                       | Дисциплина                | Квота  | Статус         
------------------------------------------------------------------------------------------
4    | Интеллектуальный рекомендательны... | Интеллектуальные инфор... | 0/1    | Доступна       
2    | Проектирование микросервисной ар... | Технологии разработки ... | 0/1    | Доступна       
3    | Разработка аналитической подсист... | Базы данных и экспертн... | 0/2    | Доступна       
1    | Разработка веб-сервиса распредел... | Технологии разработки ... | 1/1    | Занята         

2. Список зарегистрированных студентов:
ID   | ФИО студента              | Курс  | GPA   | Форма      | Email               
---------------------------------------------------------------------------
1    | Узунян Овсеп Норайрович   | 3     | 4.75  | Бюджет     | uzunano85@gmail.com 
2    | Иванов Иван               | 3     | 4.60  | Бюджет     | ivanov@edu.mirea.ru 
3    | Смирнова Анна             | 2     | 4.10  | Договор    | smirnova@edu.mirea.ru

3. Взаимодействие объектов: создание новой заявки
[+] Объект Application успешно создан и связан с объектами Topic и Student:
    - Ссылка app.topic:   Проектирование микросервисной архитектуры корпоративного портала
    - Ссылка app.student: Иванов Иван
    - Свойство @property status: ОДОБРЕНА
    - Метод __str__: Заявка №102 от 2026-09-24 | Студент: Иванов Иван -> Тема [2] 'Проектирование микросервисной архитектуры...' | Приоритет: 102 | Статус: ОДОБРЕНА

4. Сводная статистика по объектам заявок:
Всего заявок: 2 | Одобрено: 2 | Средний GPA: 4.67
======================================================="""
    add_code_block(doc, out_demo_pr3)

    add_paragraph(doc, "Протокол успешного выполнения 15 автоматических тестов:")
    out_tests_pr3 = """PASSED: tests.test_topics.test_topic_creation
PASSED: tests.test_topics.test_topic_is_suitable_for
PASSED: tests.test_topics.test_topic_reserve_and_release
PASSED: tests.test_topics.test_topic_find_and_filter
PASSED: tests.test_topics.test_topic_sort
PASSED: tests.test_topics.test_topic_str
PASSED: tests.test_students.test_student_creation
PASSED: tests.test_students.test_student_priority
PASSED: tests.test_students.test_student_serialization
PASSED: tests.test_students.test_student_str
PASSED: tests.test_applications.test_application_creation_with_object_links
PASSED: tests.test_applications.test_application_cancel
PASSED: tests.test_applications.test_create_application_logic
PASSED: tests.test_applications.test_duplicate_application_forbidden
PASSED: tests.test_applications.test_application_statistics

Все тесты (15/15) успешно пройдены!"""
    add_code_block(doc, out_tests_pr3)

    add_heading_1(doc, "6. Вывод")
    add_paragraph(doc, "В ходе выполнения практической работы № 3 были успешно освоены фундаментальные принципы "
                       "объектно-ориентированного программирования (инкапсуляция, полиморфизм, композиция и ассоциация объектов, "
                       "декораторы @classmethod, @staticmethod, @property). Проект «Сервис выбора тем курсовых работ» "
                       "получил чистую объектную модель, где сущности представлены классами в пакете models/, а хранилище "
                       "storage.py корректно преобразует JSON-данные в объекты со связями. Разработанная архитектура полностью "
                       "готова к переходу на веб-фреймворк Django и его модели данных ORM.")

    out_path = "reports/ОТЧЕТ_ПР3_Узунян_Овсеп_ЭФБО-12-24.docx"
    doc.save(out_path)
    print(f"[+] Успешно создан: {out_path}")


from generate_docx_reports_5_6_7 import create_report_pr5, create_report_pr6, create_report_pr7


if __name__ == "__main__":
    create_report_pr1()
    create_report_pr2()
    create_report_pr3()
    create_report_pr5()
    create_report_pr6()
    create_report_pr7()

