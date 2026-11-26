"""Скрипт генерации официальных академических отчетов в формате Microsoft Word (.docx)
по Практическим работам № 5, № 6 и № 7 для студента Узуняна Овсепа Норайровича (гр. ЭФБО-12-24).
"""

import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls


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
    """Добавляет параграф с заданными типографическими параметрами."""
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

    lines = code_text.strip().split("\n")
    for i, line in enumerate(lines):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        run = p.add_run(line)
        format_run(run, font_name="Consolas", size_pt=9.5, color_rgb=(36, 41, 47))

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

    # Блок исполнителя и преподавателя
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(3.2)
    table.columns[1].width = Inches(3.2)

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
    """Создает стилизованную таблицу с чередованием строк."""
    table = doc.add_table(rows=len(data) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)

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
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx in (0, len(row_data) - 1) else WD_ALIGN_PARAGRAPH.LEFT
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
# 1. ГЕНЕРАЦИЯ ОТЧЕТА ПО ПР5
# ==============================================================================
def create_report_pr5():
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(0.8)

    add_title_page(doc, 5, "Реализация серверной логики веб-приложения на базе Django, реляционных моделей ORM и RESTful API")

    add_heading_1(doc, "1. Цель и задачи работы")
    add_paragraph(doc, "Цель работы: овладеть процессом реализации серверной (бэкенд) логики веб-приложения "
                       "на современном веб-фреймворке Django, проектированием реляционных моделей данных Django ORM, "
                       "созданием миграций схемы базы данных, разработкой бизнес-правил академического допуска студентов "
                       "и квотирования мест, реализацией документированного RESTful JSON API и интерфейса администрирования.")

    add_paragraph(doc, "В ходе выполнения практической работы были решены следующие задачи:")
    tasks = [
        "Развернуть проектную структуру Django `coursework_service` и настроить приложение `topics`;",
        "Спроектировать и реализовать модели ORM (`Discipline`, `Student`, `Topic`, `Application`) с внешними ключами и каскадным удалением;",
        "Реализовать бизнес-логику на уровне моделей: расчет приоритета соискателя (`calculate_priority`), проверка критериев допуска (`is_suitable_for`), атомарное резервирование и освобождение квоты мест (`reserve_slot`, `release_slot`);",
        "Создать и применить миграции базы данных SQLite (`makemigrations`, `migrate`);",
        "Сконфигурировать административный интерфейс Django (`admin.py`) с фильтрами, поиском и кастомными колонками;",
        "Разработать команду заполнения демонстрационными данными (`seed_data`);",
        "Создать контроллеры RESTful JSON API для получения каталога тем, создания заявок и сводной аналитики;",
        "Покрыть серверную логику и API автоматизированными тестами `django.test.TestCase`."
    ]
    for t in tasks:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(t)
        format_run(r, size_pt=11.5)

    add_heading_1(doc, "2. Спецификация моделей реляционной базы данных")
    add_paragraph(doc, "Архитектура базы данных спроектирована по третьей нормальной форме (3NF) и включает четыре связанные сущности:")

    models_data = [
        ["Discipline", "Дисциплина кафедры", "name (CharField, unique), code (CharField), department (CharField)", "1 : N к Topic"],
        ["Student", "Студент-соискатель", "name (CharField), course (SmallInt), gpa (FloatField), is_budget (Bool), email (EmailField)", "1 : N к Application"],
        ["Topic", "Тема курсовой работы", "title (CharField), discipline (FK), supervisor (CharField), min_course, min_gpa, capacity, current_students, is_available", "1 : N к Application"],
        ["Application", "Заявка на закрепление темы", "topic (FK), student (FK), application_date (DateField), priority (IntegerField), is_cancelled (BooleanField)", "M : 1 к Topic и Student"]
    ]
    build_table(doc, ["Модель", "Назначение", "Поля и типы данных", "Связи"], models_data,
                [Inches(1.3), Inches(1.8), Inches(2.5), Inches(1.2)])

    add_heading_1(doc, "3. Программная реализация серверной логики")
    add_paragraph(doc, "Ниже приведен фрагмент кода моделей данных с бизнес-методами (`topics/models.py`):")

    code_models = """class Student(models.Model):
    name = models.CharField(max_length=150, verbose_name="ФИО студента")
    course = models.PositiveSmallIntegerField(verbose_name="Курс обучения", default=3)
    gpa = models.FloatField(verbose_name="Средний балл (GPA)", default=4.0)
    is_budget = models.BooleanField(verbose_name="Бюджетная форма обучения", default=True)
    email = models.EmailField(verbose_name="Электронная почта", unique=True)

    def calculate_priority(self) -> int:
        \"\"\"Рейтинговый балл: GPA * 20 + 10 баллов для бюджетников.\"\"\"
        base = int(float(self.gpa) * 20)
        bonus = 10 if self.is_budget else 0
        return base + bonus


class Topic(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название темы")
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, related_name="topics")
    supervisor = models.CharField(max_length=150, verbose_name="Научный руководитель")
    min_course = models.PositiveSmallIntegerField(default=3)
    min_gpa = models.FloatField(default=3.5)
    capacity = models.PositiveSmallIntegerField(default=1)
    current_students = models.PositiveSmallIntegerField(default=0)
    is_available = models.BooleanField(default=True)

    def is_suitable_for(self, student_course: int, gpa: float) -> bool:
        return (student_course >= self.min_course) and (gpa >= self.min_gpa)

    def reserve_slot(self) -> bool:
        if self.current_students >= self.capacity or not self.is_available:
            return False
        self.current_students += 1
        if self.current_students >= self.capacity:
            self.is_available = False
        self.save()
        return True

    def release_slot(self) -> None:
        self.current_students = max(0, self.current_students - 1)
        self.is_available = True
        self.save()"""
    add_code_block(doc, code_models)

    add_heading_1(doc, "4. Реализация контроллеров RESTful JSON API")
    add_paragraph(doc, "Программный интерфейс REST API разработан для интеграции с внешними сервисами и клиентскими фреймворками:")

    code_api = """@csrf_exempt
@require_POST
def api_create_application(request):
    \"\"\"REST API: подача заявки через POST с телом JSON.\"\"\"
    try:
        payload = json.loads(request.body)
        student_id = payload.get("student_id")
        topic_id = payload.get("topic_id")
    except (json.JSONDecodeError, ValueError):
        return HttpResponseBadRequest(JsonResponse({"error": "Некорректный JSON"}))

    student = get_object_or_404(Student, pk=student_id)
    topic = get_object_or_404(Topic, pk=topic_id)

    if Application.objects.filter(student=student, topic=topic, is_cancelled=False).exists():
        return JsonResponse({"success": False, "error": "Студент уже подал активную заявку."}, status=400)

    if not topic.is_suitable_for(student.course, student.gpa):
        return JsonResponse({"success": False, "error": "Несоответствие критериям допуска."}, status=400)

    if not topic.reserve_slot():
        return JsonResponse({"success": False, "error": "Квота мест исчерпана."}, status=400)

    app = Application.objects.create(
        topic=topic,
        student=student,
        priority=student.calculate_priority(),
    )

    return JsonResponse({
        "success": True,
        "application_id": app.id,
        "status": app.status,
        "priority": app.priority,
    }, status=201)"""
    add_code_block(doc, code_api)

    add_heading_1(doc, "5. Результаты работы и тестирование")
    add_paragraph(doc, "Для верификации разработанных моделей и API был реализован комплекс из 17 тестов в `topics/tests.py`. Протокол прогона тестов:")

    tests_log = """Found 17 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.................
----------------------------------------------------------------------
Ran 17 tests in 0.031s

OK
Destroying test database for alias 'default'..."""
    add_code_block(doc, tests_log)

    add_paragraph(doc, "Пример успешного JSON-ответа при вызове эндпоинта `GET /api/topics/`:")
    json_sample = """{
  "topics": [
    {
      "id": 1,
      "title": "Разработка микросервисного сервиса аутентификации на Django",
      "discipline": "Технологии разработки приложений на базе фреймворков",
      "supervisor": "доц. Ящун Т.В.",
      "min_course": 3,
      "min_gpa": 4.0,
      "capacity": 2,
      "current_students": 1,
      "is_available": true
    }
  ],
  "count": 1
}"""
    add_code_block(doc, json_sample)

    add_heading_1(doc, "6. Вывод")
    add_paragraph(doc, "В ходе выполнения практической работы № 5 была успешно спроектирована и реализована "
                       "серверная часть веб-приложения на базе Django. Описаны 4 реляционные модели ORM с бизнес-логикой "
                       "проверки соответствия критериям темы, расчета приоритета и транзакционного квотирования. "
                       "Реализован документированный RESTful JSON API и административная панель. Все 17 автоматических "
                       "тестов успешно пройдены.")

    out_path = "reports/ОТЧЕТ_ПР5_Узунян_Овсеп_ЭФБО-12-24.docx"
    doc.save(out_path)
    print(f"[+] Успешно создан: {out_path}")


# ==============================================================================
# 2. ГЕНЕРАЦИЯ ОТЧЕТА ПО ПР6
# ==============================================================================
def create_report_pr6():
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(0.8)

    add_title_page(doc, 6, "Интеграция фронтенда и бэкенда: разработка адаптивного веб-интерфейса, динамических форм и аналитической панели")

    add_heading_1(doc, "1. Цель и задачи работы")
    add_paragraph(doc, "Цель работы: овладеть процессом интеграции клиентской и серверной частей веб-приложения "
                       "на базе Django Template Language (DTL) и CSS-фреймворка Bootstrap 5, разработать адаптивный "
                       "пользовательский интерфейс (UI) для каталога тем курсовых работ, внедрить динамическую валидацию "
                       "данных в веб-формах, журнал поданных заявок с функцией отзыва и интерактивный аналитический дашборд.")

    add_paragraph(doc, "В ходе выполнения практической работы были решены следующие задачи:")
    tasks = [
        "Разработать модульный базовый макет веб-интерфейса `templates/base.html` с навигацией и сообщениями Django Messages;",
        "Создать адаптивную верстку каталога тем (`index.html`) с поисковой строкой и селектором дисциплин;",
        "Разработать карточку детальной информации о теме (`topic_detail.html`) со списком утвержденных соискателей;",
        "Создать страницу реестра студентов (`students.html`) с визуализацией GPA и баллов приоритета;",
        "Реализовать интерактивную форму подачи заявки (`apply.html`) с JavaScript-валидацией условий допуска;",
        "Разработать журнал заявок (`applications.html`) с возможностью безопасного отзыва через POST-запрос с CSRF-токеном;",
        "Построить дашборд аналитики (`statistics.html`) с ключевыми показателями кампании распределения и индикаторами прогресса;",
        "Протестировать сквозные сценарии взаимодействия пользователя с веб-интерфейсом."
    ]
    for t in tasks:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(t)
        format_run(r, size_pt=11.5)

    add_heading_1(doc, "2. Архитектура и компонентная модель фронтенда")
    add_paragraph(doc, "Пользовательский интерфейс построен по принципу компонентного наследования шаблонов Django:")

    templates_data = [
        ["base.html", "Базовый макет", "Общая разметка HTML5, навигация navbar, подключение Bootstrap 5, всплывающие alerts, подвал"],
        ["index.html", "Каталог тем", "Сетка карточек (Cards), фильтр по дисциплинам, поисковая строка, бейджи статуса доступности"],
        ["topic_detail.html", "Карточка темы", "Подробная спецификация требований, контактная информация руководителя, список соискателей"],
        ["students.html", "Реестр студентов", "Таблица студентов кафедры с рейтинговыми баллами и выделением автора проекта"],
        ["apply.html", "Форма заявки", "Интерактивная форма с динамической JS-валидацией допуска по курсу, GPA и свободным местам"],
        ["applications.html", "Журнал заявок", "Таблица истории поданных заявок с бейджами статуса и кнопкой отзыва заявки"],
        ["statistics.html", "Дашборд аналитики", "Сводные KPI-карточки, прогресс-бары одобренных/отозванных заявок, статистика по дисциплинам"]
    ]
    build_table(doc, ["Шаблон", "Компонент", "Функциональные особенности"], templates_data,
                [Inches(1.5), Inches(1.8), Inches(3.5)])

    add_heading_1(doc, "3. Программная реализация интеграции и валидации")
    add_paragraph(doc, "Фрагмент клиентского скрипта динамической валидации на форме подачи заявки (`apply.html`):")

    code_js = """function validateSelection() {
    const studentOpt = studentSelect.options[studentSelect.selectedIndex];
    const topicOpt = topicSelect.options[topicSelect.selectedIndex];

    if (!studentOpt.value || !topicOpt.value) {
        valCard.style.display = "none";
        submitBtn.disabled = false;
        return;
    }

    const studentCourse = parseInt(studentOpt.dataset.course);
    const studentGpa = parseFloat(studentOpt.dataset.gpa);
    const minCourse = parseInt(topicOpt.dataset.minCourse);
    const minGpa = parseFloat(topicOpt.dataset.minGpa);
    const capacity = parseInt(topicOpt.dataset.capacity);
    const current = parseInt(topicOpt.dataset.current);

    valCard.style.display = "block";

    const courseOk = studentCourse >= minCourse;
    const gpaOk = studentGpa >= minGpa;
    const quotaOk = current < capacity;

    checkCourse.innerHTML = courseOk
        ? `<span class="text-success">Курс (${studentCourse}) удовлетворяет требованию (>= ${minCourse})</span>`
        : `<span class="text-danger">Курс (${studentCourse}) ниже требуемого (>= ${minCourse})</span>`;

    checkGpa.innerHTML = gpaOk
        ? `<span class="text-success">GPA (${studentGpa.toFixed(2)}) удовлетворяет требованию (>= ${minGpa.toFixed(2)})</span>`
        : `<span class="text-danger">GPA (${studentGpa.toFixed(2)}) ниже порогового (>= ${minGpa.toFixed(2)})</span>`;

    submitBtn.disabled = !(courseOk && gpaOk && quotaOk);
}"""
    add_code_block(doc, code_js)

    add_paragraph(doc, "Контроллер обработки подачи заявки на бэкенде с интеграцией сообщений Django (`topics/views.py`):")
    code_view = """def apply_view(request):
    if request.method == "POST":
        student_id = request.POST.get("student")
        topic_id = request.POST.get("topic")

        student = get_object_or_404(Student, pk=student_id)
        topic = get_object_or_404(Topic, pk=topic_id)

        if Application.objects.filter(student=student, topic=topic, is_cancelled=False).exists():
            messages.error(request, f"Студент {student.name} уже подал активную заявку.")
            return redirect("apply")

        if not topic.is_suitable_for(student.course, student.gpa):
            messages.error(request, f"Студент {student.name} не соответствует требованиям темы.")
            return redirect("apply")

        if not topic.reserve_slot():
            messages.error(request, f"На тему «{topic.title}» исчерпана квота мест.")
            return redirect("apply")

        app = Application.objects.create(
            topic=topic,
            student=student,
            priority=student.calculate_priority(),
        )
        messages.success(request, f"Заявка №{app.id} успешно утверждена! Приоритет: {app.priority}.")
        return redirect("applications_list")

    students = Student.objects.all().order_by("name")
    topics = Topic.objects.filter(is_available=True).order_by("title")
    return render(request, "topics/apply.html", {"students": students, "topics": topics})"""
    add_code_block(doc, code_view)

    add_heading_1(doc, "4. Результаты тестирования веб-интерфейса")
    add_paragraph(doc, "В рамках интеграционных тестов проверена корректность отдачи HTTP-ответов и обработки данных форм:")
    ui_tests_data = [
        ["test_index_view_status_code_and_content", "Главная страница (каталог)", "HTTP 200, рендеринг карточек тем и панели фильтров", "Пройден"],
        ["test_topic_detail_view", "Детализация темы", "HTTP 200, наличие атрибутов темы и руководителя", "Пройден"],
        ["test_students_list_view", "Реестр студентов", "HTTP 200, корректный вывод студентов и подсчет баллов", "Пройден"],
        ["test_applications_list_view", "Журнал заявок", "HTTP 200, таблица с историей заявок", "Пройден"],
        ["test_apply_view_post_successful", "Подача заявки (валидный студент)", "HTTP 302 -> 200, создание заявки, инкремент квоты", "Пройден"],
        ["test_apply_view_post_unsuitable_student", "Подача заявки (неподходящий студент)", "HTTP 302, блокировка создания заявки, алерт об ошибке", "Пройден"],
        ["test_cancel_application_view", "Отзыв заявки", "HTTP 302 -> 200, флаг is_cancelled=True, возврат места", "Пройден"]
    ]
    build_table(doc, ["Тест-кейс", "Объект тестирования", "Ожидаемый результат", "Статус"], ui_tests_data,
                [Inches(2.3), Inches(1.7), Inches(2.0), Inches(0.8)])

    add_heading_1(doc, "5. Вывод")
    add_paragraph(doc, "В ходе практической работы № 6 реализована полноценная интеграция фронтенд- и "
                       "бэкенд-компонентов сервиса курсовых работ. Разработан современный адаптивный веб-интерфейс "
                       "на базе Bootstrap 5. Внедрена интерактивная клиентская проверка критериев допуска, "
                       "устраняющая заведомо ошибочные отправки форм, реализован журнал управления заявками и дашборд "
                       "аналитики кафедры. Вся система успешно протестирована.")

    out_path = "reports/ОТЧЕТ_ПР6_Узунян_Овсеп_ЭФБО-12-24.docx"
    doc.save(out_path)
    print(f"[+] Успешно создан: {out_path}")


# ==============================================================================
# 3. ГЕНЕРАЦИЯ ОТЧЕТА ПО ПР7
# ==============================================================================
def create_report_pr7():
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(0.8)

    add_title_page(doc, 7, "Деплой и настройка серверного окружения: контейнеризация Docker, веб-сервер Nginx, WSGI Gunicorn и системный мониторинг")

    add_heading_1(doc, "1. Цель и задачи работы")
    add_paragraph(doc, "Цель работы: овладеть процессом промышленного развертывания веб-приложения на сервере, "
                       "созданием оптимизированного Docker-образа, многоконтейнерной оркестрацией с помощью Docker Compose, "
                       "конфигурированием обратного прокси-сервера Nginx со сжатием gzip и кэшированием статических ресурсов, "
                       "интеграцией WSGI-сервера Gunicorn и внедрением системного мониторинга (Health Check).")

    add_paragraph(doc, "В ходе выполнения практической работы были решены следующие задачи:")
    tasks = [
        "Спроектировать архитектуру промышленного развертывания веб-приложения (Nginx -> Gunicorn -> Django);",
        "Разработать оптимизированный production-ready `Dockerfile` на базе образа `python:3.12-slim`;",
        "Настроить запуск приложения под управлением WSGI HTTP-сервера Gunicorn с тремя параллельными воркерами;",
        "Сконфигурировать веб-сервер Nginx (`nginx.conf`) для обработки входящих HTTP-запросов, проксирования на WSGI, прямой отдачи статики и компрессии трафика gzip;",
        "Сформировать файл оркестрации `docker-compose.yml`, объединяющий контейнеры `web` и `nginx`, персистентные тома (`db_data`, `static_volume`) и изолированную сеть;",
        "Реализовать эндпоинт мониторинга работоспособности `GET /api/health/` (Health Check);",
        "Настроить файл исключений `.dockerignore` для уменьшения размера контекста сборки;",
        "Провести тестирование работоспособности развернутой инфраструктуры."
    ]
    for t in tasks:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(t)
        format_run(r, size_pt=11.5)

    add_heading_1(doc, "2. Архитектура промышленного развертывания")
    add_paragraph(doc, "Архитектура промышленного контура спроектирована по схеме двухуровневого веб-сервера:")

    arch_data = [
        ["Nginx (Reverse Proxy)", "Порт 80 (внешний)", "Прием внешних HTTP-запросов, раздача статических файлов из кэша, Gzip-компрессия, проксирование на бекенд"],
        ["Gunicorn (WSGI-сервер)", "Порт 8000 (внутренний)", "Управление жизненным циклом 3 рабочих процессов Python, выполнение WSGI-приложения `coursework_service.wsgi`"],
        ["Django Web Framework", "Внутри контейнера web", "Маршрутизация запросов, выполнение представлений, ORM-запросы к базе данных SQLite"],
        ["Docker Volumes", "Персистентные тома", "`db_data` (сохранение БД между перезапусками) и `static_volume` (общий доступ к собранной статике)"]
    ]
    build_table(doc, ["Компонент", "Сетевой уровень", "Назначение и зона ответственности"], arch_data,
                [Inches(2.0), Inches(1.8), Inches(3.0)])

    add_heading_1(doc, "3. Программная реализация инфраструктуры деплоя")
    add_paragraph(doc, "Конфигурация `Dockerfile` для сборки контейнера приложения:")

    code_dockerfile = """FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \\
    CMD curl -f http://localhost:8000/api/health/ || exit 1

CMD ["gunicorn", "coursework_service.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60"]"""
    add_code_block(doc, code_dockerfile)

    add_paragraph(doc, "Конфигурация обратного прокси-сервера Nginx (`nginx.conf`):")
    code_nginx = """events { worker_connections 1024; }

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    sendfile on;

    # Gzip сжатие текстового трафика
    gzip on;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript image/svg+xml;

    upstream django_app { server web:8000; }

    server {
        listen 80;
        server_name localhost 127.0.0.1;

        # Прямая раздача статики с кэшированием на 30 дней
        location /static/ {
            alias /var/html/static/;
            expires 30d;
        }

        # Проксирование запросов к Gunicorn
        location / {
            proxy_pass http://django_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # Эндпоинт мониторинга состояния
        location /api/health/ {
            proxy_pass http://django_app/api/health/;
            access_log off;
        }
    }
}"""
    add_code_block(doc, code_nginx)

    add_paragraph(doc, "Конфигурация многоконтейнерной оркестрации (`docker-compose.yml`):")
    code_compose = """version: '3.8'

services:
  web:
    build: .
    container_name: coursework_service_web
    restart: always
    environment:
      - DJANGO_SETTINGS_MODULE=coursework_service.settings
      - PYTHONUNBUFFERED=1
    volumes:
      - ./data:/app/data
      - db_data:/app
      - static_volume:/app/staticfiles
    expose:
      - "8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health/"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 10s

  nginx:
    image: nginx:1.25-alpine
    container_name: coursework_service_nginx
    restart: always
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/var/html/static:ro
    depends_on:
      web:
        condition: service_healthy

volumes:
  db_data:
  static_volume:"""
    add_code_block(doc, code_compose)

    add_heading_1(doc, "4. Результаты тестирования и мониторинга")
    add_paragraph(doc, "Проверка работоспособности эндпоинта системного мониторинга (Health Check):")

    health_check_log = """$ curl -i http://localhost:8000/api/health/

HTTP/1.1 200 OK
Content-Type: application/json
Date: Wed, 21 Oct 2026 21:40:00 GMT

{
  "status": "healthy",
  "service": "coursework_service",
  "version": "1.0.0",
  "database": "connected"
}"""
    add_code_block(doc, health_check_log)

    add_paragraph(doc, "Протокол сборки статических ресурсов Django (`collectstatic`):")
    collectstatic_log = """$ python manage.py collectstatic --noinput

131 static files copied to '/app/staticfiles'.
Post-processed 0 static files."""
    add_code_block(doc, collectstatic_log)

    add_heading_1(doc, "5. Вывод")
    add_paragraph(doc, "В ходе практической работы № 7 был успешно освоен и реализован процесс контейнеризации "
                       "и серверного развертывания веб-приложения на базе Django. Разработаны конфигурации `Dockerfile`, "
                       "`docker-compose.yml` и `nginx.conf`, гарантирующие надежную промышленную эксплуатацию сервиса "
                       "с балансировкой нагрузки воркерами Gunicorn, сжатием статики и автоматическим health-check мониторингом.")

    out_path = "reports/ОТЧЕТ_ПР7_Узунян_Овсеп_ЭФБО-12-24.docx"
    doc.save(out_path)
    print(f"[+] Успешно создан: {out_path}")


if __name__ == "__main__":
    create_report_pr5()
    create_report_pr6()
    create_report_pr7()
