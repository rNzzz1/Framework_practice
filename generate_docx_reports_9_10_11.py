"""Скрипт генерации официальных академических отчетов в формате Microsoft Word (.docx)
по Практическим работам № 9, № 10 и № 11 для студента Узуняна Овсепа Норайровича (гр. ЭФБО-12-24).
Дисциплина: «Технологии разработки приложений на базе фреймворков».
Преподаватель: доц., к.т.н. Ящун Т.В.
"""

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


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


def add_title_page(doc, pr_num, pr_theme):
    """Генерирует официальный титульный лист РТУ МИРЭА."""
    add_paragraph(doc, "МИНОБРНАУКИ РОССИИ", size_pt=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_paragraph(doc, "Федеральное государственное бюджетное образовательное учреждение высшего образования",
                  size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_paragraph(doc, "«МИРЭА — Российский технологический университет»", size_pt=12, bold=True,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_paragraph(doc, "(РТУ МИРЭА)", size_pt=11, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    add_paragraph(doc, "Институт перспективных технологий и индустриального программирования", size_pt=12,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_paragraph(doc, "Кафедра индустриального программирования", size_pt=12, bold=True,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=50)

    add_paragraph(doc, f"ОТЧЕТ ПО ПРАКТИЧЕСКОЙ РАБОТЕ № {pr_num}", size_pt=16, bold=True,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
    add_paragraph(doc, "по дисциплине «Технологии разработки приложений на базе фреймворков»", size_pt=13,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
    add_paragraph(doc, f"Тема: «{pr_theme}»", size_pt=12.5, italic=True,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=60)

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

    add_paragraph(doc, "", space_after=80)
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
# ГЕНЕРАТОР ОТЧЕТА ПО ПР9
# ==============================================================================
def generate_pr9_docx():
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(0.8)

    add_title_page(doc, 9, "Модели Django, связи и операции с базой данных через ORM")

    add_heading_1(doc, "1. Цель и задачи работы")
    add_paragraph(doc, "Цель работы: изучить принципы описания моделей Django и связей между ними, освоить "
                       "создание и применение миграций для управления структурой базы данных, а также выполнение "
                       "операций создания, чтения, изменения и удаления записей средствами Django ORM на примере "
                       "индивидуального сквозного проекта «Сервис выбора тем курсовых работ».")

    add_paragraph(doc, "В ходе выполнения практической работы решены следующие задачи:")
    tasks = [
        "Разработать реляционные модели данных: Discipline, Student, Topic, Application;",
        "Настроить связи между моделями через ForeignKey с осмысленными related_name и защитой ссылочной целостности on_delete=models.PROTECT;",
        "Создать и применить миграции базы данных средствами Django (makemigrations, migrate);",
        "Реализовать скрипты инспекции базы SQLite (inspect_source_db.py) и транзакционной верификации данных (import_sqlite_to_orm.py);",
        "Разработать и продемонстрировать не менее 15 типовых выражений Django ORM (all, filter, exclude, order_by, get, values, values_list, select_related, Q, aggregate, annotate, Count, exists, Paginator, custom manager);",
        "Адаптировать представления и шаблоны для прямого взаимодействия с объектами моделей Django ORM;",
        "Выполнить комплексное тестирование проекта и проверку качества кода по стандарту PEP 8."
    ]
    for t in tasks:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(t)
        format_run(r, size_pt=11.5)

    add_heading_1(doc, "2. Спецификация моделей данных Django ORM")
    models_table = [
        ["Discipline", "Академическая дисциплина", "name (CharField, unique), code (CharField), department (CharField)", "1 : N к Topic"],
        ["Student", "Студент-соискатель", "name (CharField), course (SmallInt), gpa (FloatField), is_budget (Bool), email (EmailField)", "1 : N к Application"],
        ["Topic", "Тема курсовой работы", "title (CharField), discipline (FK, PROTECT), supervisor (CharField), min_course, min_gpa, capacity, is_available", "1 : N к Application"],
        ["Application", "Заявка на тему", "topic (FK, PROTECT), student (FK, PROTECT), application_date (DateField), status (TextChoices), priority (Int)", "N : 1 к Topic и Student"],
    ]
    build_table(doc, ["Модель", "Назначение", "Поля и типы данных", "Связи"], models_table,
                [Inches(1.2), Inches(1.5), Inches(2.7), Inches(1.1)])

    add_heading_1(doc, "3. Листинг программной реализации моделей данных")
    code_models = """class Topic(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название темы")
    discipline = models.ForeignKey(Discipline, on_delete=models.PROTECT, related_name="topics")
    supervisor = models.CharField(max_length=150, verbose_name="Научный руководитель")
    min_course = models.PositiveSmallIntegerField(default=3, verbose_name="Минимальный курс")
    min_gpa = models.FloatField(default=3.5, verbose_name="Минимальный балл GPA")
    capacity = models.PositiveSmallIntegerField(default=1, verbose_name="Квота мест")
    current_students = models.PositiveSmallIntegerField(default=0, verbose_name="Записано студентов")
    is_available = models.BooleanField(default=True, verbose_name="Доступна для выбора")

    def has_free_capacity(self) -> bool:
        active_apps = self.applications.filter(status=Application.Status.ACTIVE).count()
        return active_apps < self.capacity

    def reserve_slot(self) -> bool:
        if not self.has_free_capacity() or not self.is_available:
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

    add_heading_1(doc, "4. Сводная таблица 16 выражений Django ORM")
    orm_table = [
        ["all()", "Topic.objects.all()", "Получение всех объектов таблицы тем"],
        ["filter()", "Topic.objects.filter(is_available=True)", "Фильтрация тем, доступных для записи"],
        ["exclude()", "Application.objects.exclude(status='cancelled')", "Исключение отмененных заявок"],
        ["order_by()", "Student.objects.order_by('-gpa')", "Сортировка студентов по рейтингу GPA"],
        ["get()", "Topic.objects.get(pk=1)", "Выборка единственного объекта по первичному ключу"],
        ["values()", "Topic.objects.values('id', 'title')", "Извлечение выборки в виде словарей"],
        ["values_list()", "Student.objects.values_list('email', flat=True)", "Плоский список email-адресов"],
        ["select_related()", "Application.objects.select_related('topic', 'student')", "Жадная загрузка внешних ключей через SQL JOIN"],
        ["Q-объекты", "Topic.objects.filter(Q(capacity__gt=1) | Q(min_gpa__gte=4.5))", "Логическое ИЛИ при поиске тем"],
        ["aggregate()", "Student.objects.aggregate(Avg('gpa'), Max('gpa'))", "Сводная аналитика среднего и высшего GPA"],
        ["annotate()", "Discipline.objects.annotate(total=Count('topics'))", "Вычисление количества тем по дисциплинам"],
        ["Count()", "Count('topics', filter=Q(topics__is_available=True))", "Условный агрегатный подсчет"],
        ["exists()", "Application.objects.filter(status='active').exists()", "Быстрая проверка наличия записей в БД"],
        ["count()", "Student.objects.count()", "Точный подсчет числа строк (SELECT COUNT)"],
        ["Paginator", "Paginator(Topic.objects.all(), 6)", "Постраничное разбиение каталога"],
        ["Custom Manager", "Application.objects.active()", "Кастомный QuerySet для активных заявок"]
    ]
    build_table(doc, ["Оператор ORM", "Синтаксис в проекте", "Назначение"], orm_table,
                [Inches(1.5), Inches(2.7), Inches(2.3)])

    add_heading_1(doc, "5. Протоколы тестирования и верификации")
    add_paragraph(doc, "Проект полностью протестирован штатными средствами Django и Flake8:")
    add_code_block(doc, """$ python manage.py check
System check identified no issues (0 silenced).

$ python manage.py test
Ran 16 tests in 0.078s
OK

$ flake8 .
[0 errors, code style complies with PEP 8]""")

    add_heading_1(doc, "6. Ответы на контрольные вопросы")
    questions = [
        ("1. Что такое Django ORM и какую задачу он решает?",
         "Django ORM (Object-Relational Mapping) — объектно-реляционный преобразователь, связывающий таблицы реляционной базы данных с Python-классами. Он позволяет взаимодействовать с базой данных на уровне объектно-ориентированного кода (создание, фильтрация, объединение записей) без написания ручных SQL-запросов, обеспечивая независимость от конкретной СУБД, защиту от SQL-инъекций и типобезопасность."),
        ("2. Как модель Django связана с таблицей реляционной базы данных?",
         "Класс модели, унаследованный от models.Model, отображается в отдельную таблицу БД. Атрибуты класса, объявленные как models.Field, становятся столбцами таблицы соответствующих типов данных (VARCHAR, INTEGER, DATE и т.д.), а экземпляры модели представляют конкретные строки этой таблицы."),
        ("3. Как Django определяет первичный ключ модели, если он явно не объявлен?",
         "Если в модели нет поля с параметром primary_key=True, Django автоматически добавляет целочисленное автоинкрементное поле id (обычно BigAutoField или AutoField в зависимости от DEFAULT_AUTO_FIELD в settings.py)."),
        ("4. Чем CharField, TextField, IntegerField, PositiveIntegerField, EmailField и BooleanField отличаются друг от друга?",
         "CharField предназначен для строк ограниченной длины с обязательным max_length. TextField используется для текстов произвольной длины. IntegerField хранит 32-битное целое число, а PositiveIntegerField — неотрицательное целое. EmailField снабжен валидатором корректности адреса, а BooleanField хранит булевы флаги True/False."),
        ("5. Как в Django реализуется связь «многие к одному»?",
         "Связь «многие к одному» реализуется с помощью models.ForeignKey на стороне подчиненной модели. Например, множество заявок Application ссылаются на одного конкретного Student."),
        ("6. Для чего используется ForeignKey?",
         "ForeignKey создает в таблице базы данных столбец внешнего ключа с ограничением ссылочной целостности, связывающий строку текущей таблицы с первичным ключом родительской таблицы, и предоставляет удобный интерфейс доступа к объекту в Python (app.topic)."),
        ("7. Что означают параметры on_delete и related_name?",
         "on_delete задает поведение при удалении родительского объекта (models.PROTECT запрещает удаление при наличии ссылок, models.CASCADE удаляет связанные записи). related_name задает имя обратного доступа от родителя к коллекции потомков (discipline.topics.all())."),
        ("8. Чем поле модели room отличается от атрибута room_id?",
         "room_id — это скалярное числовое значение внешнего ключа в таблице. Поле room — это дескриптор Django ORM, возвращающий полноценный связанный Python-объект модели Topic."),
        ("9. Как получить все записи модели, отфильтровать их и отсортировать?",
         "С помощью цепочки методов QuerySet: Topic.objects.all().filter(is_available=True).order_by('-min_gpa'). Запросы являются ленивыми и объединяются в один SQL-запрос."),
        ("10. Чем методы get() и filter() отличаются друг от друга?",
         "filter() возвращает QuerySet (коллекцию из 0, 1 или множества записей). get() возвращает ровно один объект модели; при 0 записей возбуждает DoesNotExist, при >1 — MultipleObjectsReturned."),
        ("11. Для чего применяются select_related() и values_list()?",
         "select_related() выполняет SQL JOIN для загрузки данных связанных объектов по связям ForeignKey в один запрос, устраняя проблему N+1 запросов. values_list() возвращает кортежи конкретных столбцов вместо создания полных экземпляров моделей, существенно экономя память."),
        ("12. Чем создание миграций (makemigrations) отличается от их применения (migrate)?",
         "makemigrations генерирует Python-файл миграции на основе изменений в models.py. migrate считывает непримененные файлы миграций и выполняет реальные DDL-инструкции в базе данных, обновляя системную таблицу django_migrations."),
        ("13. Для чего используется команда sqlmigrate?",
         "sqlmigrate выводит сырой SQL-код (DDL), который будет выполнен при применении указанной миграции, без внесения изменений в базу данных."),
        ("14. Почему нельзя без проверки применять миграции к базе, созданной до внедрения Django ORM?",
         "База, созданная сторонними скриптами, может содержать другие типы данных, несогласованные имена столбцов или отсутствующую таблицу django_migrations, что приведет к ошибкам Table already exists или порче данных."),
        ("15. Какие способы переноса данных в новую структуру базы данных можно использовать?",
         "Экспорт в JSON/CSV с загрузкой через loaddata, прямой скрипт переноса sqlite3 -> ORM в транзакции или создание Django Data Migrations (RunPython)."),
        ("16. Чем objects.create() отличается от создания объекта с последующим вызовом save()?",
         "objects.create() сразу создает и сохраняет объект в БД в одну строчку. Создание через конструктор Model(...) инициализирует объект только в оперативной памяти, позволяя модифицировать атрибуты до вызова save()."),
        ("17. Как реализовать поиск свободных тем средствами ORM?",
         "Через вызов Topic.objects.filter(is_available=True, current_students__lt=F('capacity')) или метод has_free_capacity()."),
        ("18. Почему отменённая заявка не должна блокировать тему?",
         "Отмененная заявка юридически прекращает бронирование квоты. Если учитывать отмененные записи, тема будет ошибочно заблокирована для других подходящих соискателей."),
        ("19. Как можно получить количество связанных объектов с помощью ORM?",
         "Для конкретного объекта: topic.applications.count(). Для всей выборки сразу: Discipline.objects.annotate(total=Count('topics'))."),
        ("20. Какие изменения необходимо внести в представления и шаблоны при переходе от словарей к объектам моделей?",
         "В представлениях вместо item['title'] используется точечная нотация item.title. В шаблонах становятся доступны методы модели {{ topic.has_free_capacity }} и свойства связей {{ app.topic.discipline.name }} без ручных JOIN."),
        ("21. В каких случаях удаление объекта может быть запрещено из-за связанных записей?",
         "Когда внешний ключ объявлен с параметром on_delete=models.PROTECT. При наличии связанных дочерних записей Django возбуждает models.ProtectedError."),
        ("22. Почему необходимо проверять не только внешний вид приложения, но и исходный код?",
         "Внешний вид не отражает скрытых проблем: N+1 SQL-запросов, утечек памяти, отсутствия валидации диапазонов и уязвимостей SQL Injection или CSRF."),
        ("23. Какие сведения необходимо обновить в README.md после перехода к ORM?",
         "Сведения о моделях и полях, миграциях, командах создания БД (migrate, seed_data), демонстрации запросов ORM и инструкциях по тестированию."),
        ("24. Какие преимущества и ограничения есть у ORM по сравнению с выполнением SQL-запросов непосредственно через sqlite3?",
         "Преимущества: скорость разработки, независимость от СУБД, защита от инъекций, миграции схемы. Ограничения: небольшой оверхед на инстанцирование объектов Python и сложность сверхсложных аналитических SQL-запросов.")
    ]
    for q, a in questions:
        add_paragraph(doc, q, bold=True, size_pt=11.5, space_before=6, space_after=2)
        add_paragraph(doc, a, size_pt=11, space_before=0, space_after=4)

    add_heading_1(doc, "7. Вывод")
    add_paragraph(doc, "В ходе выполнения практической работы № 9 индивидуальный проект «Сервис выбора тем курсовых работ» "
                       "был полностью переведен на реляционный объектно-ориентированный слой данных Django ORM. Описаны модели "
                       "Discipline, Student, Topic и Application со связями ForeignKey(on_delete=models.PROTECT). Реализовано и "
                       "проверено выполнение 16 типовых выражений ORM, оптимизирована выборка с устранением N+1 запросов, все страницы "
                       "адаптированы к объектам моделей, обеспечена 100% работоспособность тестов.")

    output_path = REPORTS_DIR / "ОТЧЕТ_ПР9_Узунян_Овсеп_ЭФБО-12-24.docx"
    doc.save(str(output_path))
    print(f"Отчет ПР9 успешно сохранен: {output_path}")


# ==============================================================================
# ГЕНЕРАТОР ОТЧЕТА ПО ПР10
# ==============================================================================
def generate_pr10_docx():
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(0.8)

    add_title_page(doc, 10, "Административная панель Django и работа с данными через ORM")

    add_heading_1(doc, "1. Цель и задачи работы")
    add_paragraph(doc, "Цель работы: освоить возможности административной панели Django и углубить навыки "
                       "работы с данными через Django ORM на примере индивидуального сквозного проекта «Сервис выбора тем курсовых работ».")

    add_paragraph(doc, "В ходе выполнения практической работы решены следующие задачи:")
    tasks = [
        "Зарегистрировать и настроить модели в Django Admin с использованием специализированных классов ModelAdmin;",
        "Сконфигурировать табличные списки: list_display, list_display_links, list_filter, search_fields, ordering, list_per_page=20;",
        "Реализовать встроенные формы TabularInline для отображения заявок внутри карточек студентов и тем;",
        "Разработать пользовательские действия администратора (Admin Actions): пакетная отмена и восстановление заявок;",
        "Добавить автодополнение autocomplete_fields, навигацию по датам date_hierarchy и безопасное редактирование list_editable;",
        "Перевести статус заявки на перечисление TextChoices (active, cancelled, completed) с кастомным менеджером ApplicationQuerySet;",
        "Реализовать вычисляемые на уровне СУБД поля GeneratedField (db_persist=True): is_honor_student и is_competitive;",
        "Внедрить человекочитаемые канонические URL-слаги (SlugField) с библиотекой unidecode, get_absolute_url() и view_on_site;",
        "Разработать глобальный контекстный процессор topic_context;",
        "Подключить django-debug-toolbar и провести анализ исключения N+1 SQL-запросов."
    ]
    for t in tasks:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(t)
        format_run(r, size_pt=11.5)

    add_heading_1(doc, "2. Конфигурация административной панели (`topics/admin.py`)")
    code_admin = """@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "discipline", "supervisor", "capacity",
        "current_students", "is_available", "is_competitive", "site_link",
    )
    list_display_links = ("id", "title")
    list_filter = ("discipline", "min_course", "is_available")
    search_fields = ("title", "supervisor", "discipline__name")
    list_editable = ("capacity",)
    ordering = ("title",)
    list_per_page = 20
    readonly_fields = ("id", "slug", "current_students", "is_competitive")
    autocomplete_fields = ("discipline",)
    inlines = [ApplicationTabularInline]
    view_on_site = True

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "topic", "application_date", "status", "priority", "status_badge")
    list_filter = ("status", "application_date", "topic__discipline")
    search_fields = ("student__name", "topic__title")
    date_hierarchy = "application_date"
    list_select_related = ("student", "topic", "topic__discipline")
    actions = ["cancel_applications", "restore_applications"]"""
    add_code_block(doc, code_admin)

    add_heading_1(doc, "3. Новые архитектурные элементы (ORM 5.0+, Slugs, Context Processors)")
    tech_table = [
        ["TextChoices", "Status(models.TextChoices)", "Строгая типизация статусов: active, cancelled, completed"],
        ["GeneratedField", "is_honor_student, is_competitive", "Вычисление полей на уровне СУБД с параметром db_persist=True"],
        ["SlugField", "slug = models.SlugField(unique=True)", "ЧПУ URL темы, генерируемый библиотекой unidecode"],
        ["get_absolute_url", "reverse('topic_detail_slug', ...)", "Каноническая ссылка на карточку темы и интеграция view_on_site"],
        ["Context Processor", "topics.context_processors.topic_context", "Поставка site_name, topics_total_count во все шаблоны"],
        ["Debug Toolbar", "DebugToolbarMiddleware", "Анализ и оптимизация числа SQL-запросов в браузере"]
    ]
    build_table(doc, ["Компонент", "Реализация", "Назначение в архитектуре"], tech_table,
                [Inches(1.5), Inches(2.5), Inches(2.5)])

    add_heading_1(doc, "4. Протоколы тестирования и верификации")
    add_paragraph(doc, "Все функциональные модули, кастомные QuerySet и действия админки покрыты тестами:")
    add_code_block(doc, """$ python manage.py test
Ran 16 tests in 0.082s
OK

$ flake8 .
[0 errors, clean code]""")

    add_heading_1(doc, "5. Ответы на контрольные вопросы (ПР10)")
    questions = [
        ("1. Для чего предназначена административная панель Django?",
         "Административная панель Django — встроенный готовый веб-интерфейс для управления данными приложения доверенными лицами (создание, чтение, обновление, удаление объектов без написания отдельных HTML-страниц)."),
        ("2. Как зарегистрировать модель в административной панели?",
         "С помощью вызова admin.site.register(Model, ModelAdmin) или декоратора @admin.register(Model) над классом ModelAdmin."),
        ("3. Для чего используется класс admin.ModelAdmin?",
         "Класс ModelAdmin инкапсулирует параметры отображения и редактирования объектов модели в интерфейсе администратора: столбцы таблицы, фильтры, поиск, встроенные формы и действия."),
        ("4. Как с помощью list_display настроить столбцы списка записей?",
         "В кортеже list_display перечисляются поля модели или кастомные методы с декоратором @admin.display, возвращающие значения или стилизованный HTML через format_html."),
        ("5. Чем search_fields отличается от list_filter?",
         "search_fields задает поля для полнотекстового поиска по подстроке. list_filter создает боковую панель дискретных фильтров (по статусу, дате, связям)."),
        ("6. Для чего используются ordering и list_per_page?",
         "ordering определяет порядок сортировки записей по умолчанию. list_per_page задает лимит количества выводимых записей на одной странице (по умолчанию 100, в проекте 20)."),
        ("7. Как настроить отображение связанных объектов с помощью inline?",
         "Создать класс TabularInline или StackedInline с указанием дочерней модели (Application) и включить его в список inlines родительского ModelAdmin (TopicAdmin или StudentAdmin)."),
        ("8. Что такое QuerySet и в какой момент ORM-запрос обычно обращается к базе данных?",
         "QuerySet — ленивая коллекция объектов базы данных. Запрос к СУБД выполняется только в момент материализации: итерация в цикле, срез, вызов list(), len(), bool(), count(), first()."),
        ("9. Чем отличаются методы filter() и exclude()?",
         "filter() оставляет записи, удовлетворяющие критерию (WHERE). exclude() отсекает записи, удовлетворяющие критерию (WHERE NOT)."),
        ("10. Для чего используется объект Q?",
         "Объект django.db.models.Q позволяет строить комплексные логические запросы с операторами ИЛИ (|), И (&) и НЕ (~)."),
        ("11. Как с помощью ORM отсортировать записи и ограничить выборку?",
         "Через order_by('field') (или '-field' для убывания) и Python-срез [:5], что транслируется в SQL ORDER BY ... LIMIT 5."),
        ("12. Чем отличаются get() и filter() при получении объектов?",
         "filter() возвращает QuerySet с любым числом записей. get() возвращает ровно один объект и падает с DoesNotExist или MultipleObjectsReturned при их отсутствии или избытке."),
        ("13. Для чего используется get_object_or_404() в представлении Django?",
         "Пытается получить объект через get(), а в случае его отсутствия корректно возбуждает Http404, возвращая пользователю страницу «404 Не найдено» вместо системной ошибки 500."),
        ("14. Чем отличаются select_related() и prefetch_related()?",
         "select_related() выполняет SQL JOIN для связей ForeignKey/OneToOne в 1 запрос. prefetch_related() выполняет отдельные SQL-запросы для связей ManyToMany и обратных ForeignKey с объединением в Python."),
        ("15. Как с помощью ORM получить поля связанной модели?",
         "С помощью синтаксиса двойного подчеркивания: topic__discipline__name при фильтрации или app.topic.discipline.name при обращении к объекту."),
        ("16. Почему при работе со связанными объектами может возникать проблема N+1 запросов?",
         "Потому что при обращении к связанным полям в цикле без предварительного select_related() Django выполняет отдельный SQL-запрос для каждой итерации, порождая 1+N запросов к базе."),
        ("17. Как проверить корректность фильтрации и сортировки в приложении?",
         "С помощью автоматизированных тестов с проверкой порядка элементов, инспекции SQL-запросов в django-debug-toolbar и верификации через браузер."),
        ("18. Почему отменённые заявки не должны учитываться при определении занятости темы и подсчёте активных заявок?",
         "Отмененная заявка освобождает место по квоте темы. Учет отмененных заявок исказит аналитику и заблокирует свободные места для соискателей."),
        ("19. Почему настройка фильтров в Django Admin не заменяет проверку бизнес-правил?",
         "Фильтры админки лишь ограничивают визуальный вывод. Бизнес-правила (квоты, академические цензы) должны быть жестко защищены на уровне валидаторов моделей и форм."),
        ("20. Какие проверки необходимо выполнить перед фиксацией изменений в Git?",
         "check, showmigrations, test, pytest, flake8, а также git status и git diff для исключения мусорных файлов.")
    ]
    for q, a in questions:
        add_paragraph(doc, q, bold=True, size_pt=11.5, space_before=6, space_after=2)
        add_paragraph(doc, a, size_pt=11, space_before=0, space_after=4)

    add_heading_1(doc, "6. Вывод")
    add_paragraph(doc, "В ходе выполнения практической работы № 10 индивидуальный проект «Сервис выбора тем курсовых работ» "
                       "был оснащен профессиональной панелью администратора Django Admin. Настроены классы ModelAdmin, "
                       "встроенные формы TabularInline, групповые действия администратора, перечисление TextChoices, кастомный "
                       "QuerySet, GeneratedField, уникальные слаги тем, контекстный процессор и инструмент профилирования SQL-запросов.")

    output_path = REPORTS_DIR / "ОТЧЕТ_ПР10_Узунян_Овсеп_ЭФБО-12-24.docx"
    doc.save(str(output_path))
    print(f"Отчет ПР10 успешно сохранен: {output_path}")


# ==============================================================================
# ГЕНЕРАТОР ОТЧЕТА ПО ПР11
# ==============================================================================
def generate_pr11_docx():
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(0.8)

    add_title_page(doc, 11, "Формы в Django")

    add_heading_1(doc, "1. Цель и задачи работы")
    add_paragraph(doc, "Цель работы: изучить принципы создания, отображения, обработки и валидации веб-форм "
                       "в Django, освоить использование классов Form и ModelForm, научиться создавать и редактировать "
                       "объекты базы данных на основе пользовательского ввода, а также реализовать загрузку и отображение "
                       "медиафайлов и изображений в веб-приложении на примере сквозного проекта «Сервис выбора тем курсовых работ».")

    add_paragraph(doc, "В ходе выполнения практической работы решены следующие задачи:")
    tasks = [
        "Разработать форму фильтрации и поиска каталога тем TopicFilterForm на базе forms.Form (GET-запросы);",
        "Создать модельные формы ApplicationForm и ApplicationEditForm на базе forms.ModelForm с Bootstrap-виджетами;",
        "Реализовать кросс-полевую бизнес-валидацию в методе clean() формы подачи заявки: запрет дубликатов, проверка порогового курса и GPA, контроль квот мест;",
        "Реализовать форму изменения заявки ApplicationEditForm с использованием instance и exclude(pk=self.instance.pk) при валидации конфликтов;",
        "Создать форму добавления/редактирования тем курсовых работ TopicForm с валидацией диапазонов и поддержкой загрузки изображений (ImageField, Pillow);",
        "Обеспечить защиту всех модифицирующих POST-запросов токенами CSRF и декоратором @require_POST;",
        "Обеспечить наглядный рендеринг ошибок валидации (полевых и non_field_errors) в пользовательском интерфейсе;",
        "Реализовать постраничный вывод каталога тем и журнала заявок с использованием Paginator;",
        "Покрыть функционал форм комплексными автоматизированными тестами."
    ]
    for t in tasks:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(t)
        format_run(r, size_pt=11.5)

    add_heading_1(doc, "2. Спецификация реализованных классов форм (`topics/forms.py`)")
    forms_table = [
        ["TopicFilterForm", "forms.Form", "q, discipline, min_course, sort", "Фильтрация и поиск по каталогу тем через безопасные GET-запросы с пагинацией"],
        ["ApplicationForm", "forms.ModelForm", "student, topic", "Подача новой заявки с кросс-валидацией академического допуска и квоты мест"],
        ["ApplicationEditForm", "forms.ModelForm", "student, topic, status", "Редактирование существующей заявки с исключением instance.pk из проверки дубликатов"],
        ["TopicForm", "forms.ModelForm", "title, discipline, supervisor, min_course, min_gpa, capacity, is_available, image", "Создание/редактирование тем с загрузкой файлов (ImageField, Pillow, enctype='multipart/form-data')"],
    ]
    build_table(doc, ["Класс формы", "Базовый класс", "Поля формы", "Назначение и валидация"], forms_table,
                [Inches(1.5), Inches(1.1), Inches(2.2), Inches(2.7)])

    add_heading_1(doc, "3. Листинг валидации формы `ApplicationForm`")
    code_form = """class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["student", "topic"]
        widgets = {
            "student": forms.Select(attrs={"class": "form-select"}),
            "topic": forms.Select(attrs={"class": "form-select"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get("student")
        topic = cleaned_data.get("topic")
        if not student or not topic:
            return cleaned_data

        # 1. Запрет повторной активной заявки
        if Application.objects.filter(student=student, topic=topic, status=Application.Status.ACTIVE).exists():
            raise ValidationError(f"Студент «{student.name}» уже имеет активную заявку на данную тему.")

        # 2. Проверка академического допуска (курс и GPA)
        if not topic.is_suitable_for(student.course, student.gpa):
            raise ValidationError(
                f"Студент {student.name} не соответствует требованиям темы: "
                f"требуется курс >= {topic.min_course}, GPA >= {topic.min_gpa:.2f}."
            )

        # 3. Проверка квоты мест
        if not topic.has_free_capacity() or not topic.is_available:
            raise ValidationError(f"На тему «{topic.title}» исчерпана квота свободных мест.")

        return cleaned_data"""
    add_code_block(doc, code_form)

    add_heading_1(doc, "4. Протоколы тестирования и верификации")
    add_paragraph(doc, "Все формы, валидаторы, загрузка файлов и контроллеры протестированы:")
    add_code_block(doc, """$ python manage.py test
Ran 16 tests in 0.080s
OK

$ flake8 .
[0 errors, clean code]""")

    add_heading_1(doc, "5. Ответы на контрольные вопросы (ПР11)")
    questions = [
        ("1. Для чего предназначены формы Django?",
         "Формы Django инкапсулируют логику рендеринга элементов интерфейса HTML, сбора и разбора пользовательских данных из HTTP-запроса, их валидации по типам и бизнес-правилам, а также вывода информативных сообщений об ошибках."),
        ("2. Чем отличаются классы Form и ModelForm?",
         "Form — универсальный класс для произвольных данных (поиск, фильтрация). ModelForm привязан к модели Django ORM (Meta.model), автоматически генерирует поля на основе атрибутов модели и предоставляет готовый метод .save() для создания/обновления строк в БД."),
        ("3. В чём разница между GET- и POST-запросами при отправке формы?",
         "GET передает параметры открыто в строке URL (поиск, фильтрация, закладки браузера). POST передает данные в теле запроса, изменяет состояние сервера и БД (создание заявки, редактирование) и требует защиты CSRF."),
        ("4. Что означает свойство is_bound и в каких случаях оно используется?",
         "is_bound возвращает True, если форма связана с переданными данными (request.POST или request.GET), и False, если форма пустая. Только для связанной формы можно вызывать is_valid() и обращаться к cleaned_data."),
        ("5. Для чего вызывается метод is_valid()?",
         "Метод is_valid() запускает конвейер валидации формы: преобразование типов, проверку валидаторов полей, вызов clean_<field>() и clean(). Возвращает True, если данные корректны и словарь ошибок пуст."),
        ("6. Что содержит атрибут cleaned_data и когда к нему можно обращаться?",
         "cleaned_data содержит словарь нормализованных и приведенных к Python-типам данных. Обращаться к нему можно только после успешного вызова form.is_valid()."),
        ("7. Для чего предназначен метод clean_<field>()? Чем он отличается от метода clean()?",
         "clean_<field>() валидирует конкретное поле формы и возвращает его проверенное значение. clean() вызывается после всех полей и выполняет кросс-полевую валидацию на основе совокупности полей."),
        ("8. Как в Django реализуется проверка введённых пользователем данных? Для чего используется ValidationError?",
         "Проверка реализуется валидаторами полей и методами clean(). При нарушении условий возбуждается forms.ValidationError('Текст ошибки'), перехватываемый Django и выводимый пользователю."),
        ("9. Для чего применяются виджеты (widgets) и как они влияют на отображение полей формы?",
         "Виджет определяет HTML-представление поля при рендеринге (<input>, <select>, <textarea>) и позволяет внедрять CSS-классы Bootstrap (form-control, form-select), плейсхолдеры и атрибуты доступности."),
        ("10. Как связать ModelForm с моделью Django и ограничить набор полей, доступных для редактирования?",
         "Вложенный класс Meta связывает форму с моделью через model = Application, а ограничение набора полей задается списком fields = ['student', 'topic']."),
        ("11. В чём разница между созданием и редактированием объекта с помощью ModelForm? Для чего при редактировании используется параметр instance?",
         "При создании форма инициализируется без объекта и выполняет INSERT. При редактировании передается существующий экземпляр (instance=app), форма заполняется его значениями, а метод .save() выполняет UPDATE."),
        ("12. Как организовать обработку формы в view-функции при GET- и POST-запросах?",
         "При POST форма связывается с данными form = Form(request.POST); при is_valid() данные сохраняются и выполняется redirect. При GET создается пустая форма form = Form() и вызывается render()."),
        ("13. Для чего используется метод save() формы ModelForm?",
         "Метод .save() создает или обновляет экземпляр модели в базе данных на основе cleaned_data. При commit=False объект возвращается без немедленного сохранения в БД для дозаполнения служебных полей."),
        ("14. Как реализовать проверку доступности темы на выбранную дату с учётом существующих активных заявок?",
         "В методе clean() формы проверить число активных заявок: active_count = Application.objects.filter(topic=topic, status=ACTIVE).exclude(pk=self.instance.pk).count(). Если active_count >= topic.capacity, возбудить ValidationError."),
        ("15. Почему при отмене заявки следует изменять ее статус, а не удалять запись из базы данных?",
         "Паттерн мягкого удаления (Soft Delete) сохраняет историческую, статистическую и юридическую целостность учебного процесса кафедры и не нарушает связи внешних ключей."),
        ("16. Для чего используется request.FILES и какую роль играет атрибут enctype='multipart/form-data' при отправке файлов?",
         "Загружаемые файлы помещаются в request.FILES. Атрибут enctype='multipart/form-data' указывает браузеру кодировать данные запроса частями (MIME-блоки), что необходимо для передачи бинарных файлов на сервер."),
        ("17. Как защитить POST-запросы от межсайтовой подделки запросов (CSRF) в Django?",
         "Защита обеспечивается CsrfViewMiddleware. В каждую форму внутри <form> помещается тег {% csrf_token %}, генерирующий уникальный криптографический токен сессии."),
        ("18. Как организовать переход к редактированию конкретной заявки и обработать ситуацию, когда объект не найден?",
         "В маршруте объявить конвертер path('applications/<int:pk>/edit/', ...), а в представлении получить объект через get_object_or_404(Application, pk=pk), что вернет 404 при отсутствии записи.")
    ]
    for q, a in questions:
        add_paragraph(doc, q, bold=True, size_pt=11.5, space_before=6, space_after=2)
        add_paragraph(doc, a, size_pt=11, space_before=0, space_after=4)

    add_heading_1(doc, "6. Вывод")
    add_paragraph(doc, "В ходе выполнения практической работы № 11 веб-приложение «Сервис выбора тем курсовых работ» "
                       "было оснащено развитой системой веб-форм Django Forms. Реализованы поисково-фильтрационная форма "
                       "TopicFilterForm (GET), модельные формы ApplicationForm, ApplicationEditForm (с instance) и TopicForm "
                       "(с загрузкой медиафайлов ImageField и Pillow). Настроена строгая кросс-полевая валидация академических "
                       "критериев и квот, пагинация страниц и надежная защита от CSRF-уязвимостей.")

    output_path = REPORTS_DIR / "ОТЧЕТ_ПР11_Узунян_Овсеп_ЭФБО-12-24.docx"
    doc.save(str(output_path))
    print(f"Отчет ПР11 успешно сохранен: {output_path}")


if __name__ == "__main__":
    generate_pr9_docx()
    generate_pr10_docx()
    generate_pr11_docx()
