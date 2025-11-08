"""
Скрипт инициализации базы данных с тестовыми вопросами
"""
from app import app, db, User, Question, QuestionOption
from werkzeug.security import generate_password_hash

# Тестовые вопросы для каждой компетенции (по 5 вопросов на компетенцию)
SAMPLE_QUESTIONS = [
    # Критическое мышление
    {
        'text': 'При решении сложной задачи вы в первую очередь:',
        'competency': 'critical_thinking',
        'options': [
            {'text': 'Разбиваю на подзадачи и анализирую каждую', 'score': 5},
            {'text': 'Ищу похожие решения в интернете или литературе', 'score': 3},
            {'text': 'Пробую разные варианты наугад', 'score': 2},
            {'text': 'Обращаюсь за помощью к коллегам', 'score': 1}
        ]
    },
    {
        'text': 'Когда вы слышите новую информацию, вы:',
        'competency': 'critical_thinking',
        'options': [
            {'text': 'Анализирую источники и проверяю факты', 'score': 5},
            {'text': 'Сравниваю с уже известной информацией', 'score': 4},
            {'text': 'Принимаю на веру, если источник авторитетный', 'score': 2},
            {'text': 'Принимаю без проверки', 'score': 1}
        ]
    },
    {
        'text': 'При принятии важного решения вы:',
        'competency': 'critical_thinking',
        'options': [
            {'text': 'Собираю все факты, анализирую плюсы и минусы', 'score': 5},
            {'text': 'Советуюсь с несколькими людьми', 'score': 3},
            {'text': 'Доверяю интуиции', 'score': 2},
            {'text': 'Выбираю первый попавшийся вариант', 'score': 1}
        ]
    },
    {
        'text': 'Когда сталкиваетесь с противоречивой информацией:',
        'competency': 'critical_thinking',
        'options': [
            {'text': 'Изучаю оба источника и ищу истину', 'score': 5},
            {'text': 'Выбираю более авторитетный источник', 'score': 3},
            {'text': 'Принимаю ту версию, которая мне ближе', 'score': 2},
            {'text': 'Игнорирую противоречия', 'score': 1}
        ]
    },
    {
        'text': 'Ваш подход к анализу проблемы:',
        'competency': 'critical_thinking',
        'options': [
            {'text': 'Системный, с рассмотрением всех аспектов', 'score': 5},
            {'text': 'Фокусируюсь на ключевых моментах', 'score': 4},
            {'text': 'Рассматриваю только очевидные факты', 'score': 2},
            {'text': 'Действую по ситуации', 'score': 1}
        ]
    },
    
    # Коммуникация
    {
        'text': 'При общении с группой людей вы:',
        'competency': 'communication',
        'options': [
            {'text': 'Легко нахожу общий язык со всеми', 'score': 5},
            {'text': 'Общаюсь с теми, кто мне интересен', 'score': 3},
            {'text': 'Предпочитаю общаться один на один', 'score': 2},
            {'text': 'Избегаю группового общения', 'score': 1}
        ]
    },
    {
        'text': 'Когда нужно объяснить сложную тему:',
        'competency': 'communication',
        'options': [
            {'text': 'Адаптирую объяснение под аудиторию', 'score': 5},
            {'text': 'Использую примеры и аналогии', 'score': 4},
            {'text': 'Объясняю как знаю', 'score': 2},
            {'text': 'Показываю на практике', 'score': 3}
        ]
    },
    {
        'text': 'В конфликтной ситуации вы:',
        'competency': 'communication',
        'options': [
            {'text': 'Стремлюсь найти компромисс', 'score': 5},
            {'text': 'Выслушиваю все стороны', 'score': 4},
            {'text': 'Отстаиваю свою позицию', 'score': 2},
            {'text': 'Избегаю конфликтов', 'score': 1}
        ]
    },
    {
        'text': 'При публичном выступлении вы:',
        'competency': 'communication',
        'options': [
            {'text': 'Чувствую себя уверенно и свободно', 'score': 5},
            {'text': 'Волнуюсь, но справляюсь', 'score': 3},
            {'text': 'Сильно нервничаю', 'score': 2},
            {'text': 'Избегаю публичных выступлений', 'score': 1}
        ]
    },
    {
        'text': 'Ваш стиль письменного общения:',
        'competency': 'communication',
        'options': [
            {'text': 'Чёткий, структурированный, понятный', 'score': 5},
            {'text': 'Детальный и подробный', 'score': 4},
            {'text': 'Краткий и по делу', 'score': 3},
            {'text': 'Спонтанный и неструктурированный', 'score': 1}
        ]
    },
    
    # Креативность
    {
        'text': 'При поиске решения проблемы вы:',
        'competency': 'creativity',
        'options': [
            {'text': 'Генерирую множество нестандартных идей', 'score': 5},
            {'text': 'Ищу необычные подходы', 'score': 4},
            {'text': 'Использую проверенные методы', 'score': 2},
            {'text': 'Копирую чужие решения', 'score': 1}
        ]
    },
    {
        'text': 'Ваше отношение к новым идеям:',
        'competency': 'creativity',
        'options': [
            {'text': 'Всегда открыт к экспериментам', 'score': 5},
            {'text': 'Пробую после анализа', 'score': 3},
            {'text': 'Предпочитаю проверенное', 'score': 2},
            {'text': 'Избегаю новшеств', 'score': 1}
        ]
    },
    {
        'text': 'В свободное время вы:',
        'competency': 'creativity',
        'options': [
            {'text': 'Занимаюсь творческими проектами', 'score': 5},
            {'text': 'Изучаю что-то новое', 'score': 4},
            {'text': 'Отдыхаю и развлекаюсь', 'score': 2},
            {'text': 'Ничего особенного', 'score': 1}
        ]
    },
    {
        'text': 'Когда нужно придумать что-то новое:',
        'competency': 'creativity',
        'options': [
            {'text': 'Провожу мозговой штурм', 'score': 5},
            {'text': 'Изучаю аналоги и вдохновляюсь', 'score': 3},
            {'text': 'Жду вдохновения', 'score': 2},
            {'text': 'Копирую существующие решения', 'score': 1}
        ]
    },
    {
        'text': 'Ваш подход к рутинным задачам:',
        'competency': 'creativity',
        'options': [
            {'text': 'Ищу способы сделать интереснее', 'score': 5},
            {'text': 'Пробую разные подходы', 'score': 4},
            {'text': 'Делаю как обычно', 'score': 2},
            {'text': 'Автоматически выполняю', 'score': 1}
        ]
    },
    
    # Эмоциональный интеллект
    {
        'text': 'Когда видите, что коллега расстроен:',
        'competency': 'emotional_intelligence',
        'options': [
            {'text': 'Подхожу и предлагаю помощь', 'score': 5},
            {'text': 'Замечаю, но не вмешиваюсь', 'score': 3},
            {'text': 'Не обращаю внимания', 'score': 1},
            {'text': 'Избегаю общения', 'score': 1}
        ]
    },
    {
        'text': 'Ваше понимание своих эмоций:',
        'competency': 'emotional_intelligence',
        'options': [
            {'text': 'Всегда понимаю причину своих эмоций', 'score': 5},
            {'text': 'Часто понимаю', 'score': 4},
            {'text': 'Иногда понимаю', 'score': 2},
            {'text': 'Редко задумываюсь об этом', 'score': 1}
        ]
    },
    {
        'text': 'При работе в команде вы:',
        'competency': 'emotional_intelligence',
        'options': [
            {'text': 'Чувствую настроение команды', 'score': 5},
            {'text': 'Замечаю основные эмоции', 'score': 3},
            {'text': 'Фокусируюсь на задачах', 'score': 2},
            {'text': 'Не обращаю внимания на эмоции', 'score': 1}
        ]
    },
    {
        'text': 'В стрессовой ситуации вы:',
        'competency': 'emotional_intelligence',
        'options': [
            {'text': 'Сохраняю спокойствие и контролирую эмоции', 'score': 5},
            {'text': 'Стараюсь не показывать волнение', 'score': 3},
            {'text': 'Трудно контролировать эмоции', 'score': 2},
            {'text': 'Паникую', 'score': 1}
        ]
    },
    {
        'text': 'Ваша способность к эмпатии:',
        'competency': 'emotional_intelligence',
        'options': [
            {'text': 'Легко понимаю чувства других', 'score': 5},
            {'text': 'Часто понимаю', 'score': 4},
            {'text': 'Иногда понимаю', 'score': 2},
            {'text': 'Трудно понять чувства других', 'score': 1}
        ]
    },
    
    # Адаптивность
    {
        'text': 'Когда планы резко меняются:',
        'competency': 'adaptability',
        'options': [
            {'text': 'Быстро адаптируюсь и нахожу новые решения', 'score': 5},
            {'text': 'Принимаю изменения после небольшой паузы', 'score': 3},
            {'text': 'Расстраиваюсь, но адаптируюсь', 'score': 2},
            {'text': 'Трудно принять изменения', 'score': 1}
        ]
    },
    {
        'text': 'Ваше отношение к новым технологиям:',
        'competency': 'adaptability',
        'options': [
            {'text': 'Стремлюсь изучить и использовать', 'score': 5},
            {'text': 'Изучаю при необходимости', 'score': 3},
            {'text': 'Использую только необходимое', 'score': 2},
            {'text': 'Предпочитаю привычное', 'score': 1}
        ]
    },
    {
        'text': 'При смене рабочего места/проекта:',
        'competency': 'adaptability',
        'options': [
            {'text': 'Быстро вливаюсь в новую среду', 'score': 5},
            {'text': 'Адаптируюсь за несколько дней', 'score': 3},
            {'text': 'Нужно время для привыкания', 'score': 2},
            {'text': 'Долго адаптируюсь', 'score': 1}
        ]
    },
    {
        'text': 'Ваша гибкость в работе:',
        'competency': 'adaptability',
        'options': [
            {'text': 'Легко переключаюсь между задачами', 'score': 5},
            {'text': 'Переключаюсь, но нужно время', 'score': 3},
            {'text': 'Предпочитаю фокус на одной задаче', 'score': 2},
            {'text': 'Трудно переключаться', 'score': 1}
        ]
    },
    {
        'text': 'При неожиданных изменениях в проекте:',
        'competency': 'adaptability',
        'options': [
            {'text': 'Вижу новые возможности', 'score': 5},
            {'text': 'Адаптирую план', 'score': 4},
            {'text': 'Стараюсь вернуться к исходному плану', 'score': 2},
            {'text': 'Расстраиваюсь из-за изменений', 'score': 1}
        ]
    },
    
    # Управление временем
    {
        'text': 'Ваш подход к планированию дня:',
        'competency': 'time_management',
        'options': [
            {'text': 'Составляю детальный план с приоритетами', 'score': 5},
            {'text': 'Планирую основные задачи', 'score': 3},
            {'text': 'Держу задачи в голове', 'score': 2},
            {'text': 'Не планирую', 'score': 1}
        ]
    },
    {
        'text': 'При работе с дедлайнами:',
        'competency': 'time_management',
        'options': [
            {'text': 'Всегда укладываюсь в срок', 'score': 5},
            {'text': 'Обычно укладываюсь', 'score': 3},
            {'text': 'Иногда опаздываю', 'score': 2},
            {'text': 'Часто не успеваю', 'score': 1}
        ]
    },
    {
        'text': 'Ваша способность к приоритизации:',
        'competency': 'time_management',
        'options': [
            {'text': 'Чётко определяю важность задач', 'score': 5},
            {'text': 'Понимаю приоритеты', 'score': 4},
            {'text': 'Иногда путаюсь в приоритетах', 'score': 2},
            {'text': 'Трудно определить приоритеты', 'score': 1}
        ]
    },
    {
        'text': 'При множестве задач вы:',
        'competency': 'time_management',
        'options': [
            {'text': 'Систематизирую и выполняю по плану', 'score': 5},
            {'text': 'Выполняю по мере поступления', 'score': 3},
            {'text': 'Делаю то, что проще', 'score': 2},
            {'text': 'Теряюсь и делаю всё хаотично', 'score': 1}
        ]
    },
    {
        'text': 'Ваше отношение к прокрастинации:',
        'competency': 'time_management',
        'options': [
            {'text': 'Редко откладываю важные дела', 'score': 5},
            {'text': 'Иногда откладываю, но контролирую', 'score': 3},
            {'text': 'Часто откладываю', 'score': 2},
            {'text': 'Постоянно откладываю дела', 'score': 1}
        ]
    },
    
    # Командная работа
    {
        'text': 'В командной работе вы:',
        'competency': 'teamwork',
        'options': [
            {'text': 'Активно участвую и поддерживаю команду', 'score': 5},
            {'text': 'Выполняю свою часть работы', 'score': 3},
            {'text': 'Предпочитаю работать самостоятельно', 'score': 2},
            {'text': 'Избегаю командной работы', 'score': 1}
        ]
    },
    {
        'text': 'При конфликтах в команде:',
        'competency': 'teamwork',
        'options': [
            {'text': 'Стремлюсь разрешить конфликт', 'score': 5},
            {'text': 'Помогаю найти компромисс', 'score': 4},
            {'text': 'Остаюсь в стороне', 'score': 2},
            {'text': 'Усиливаю конфликт', 'score': 1}
        ]
    },
    {
        'text': 'Ваша роль в команде:',
        'competency': 'teamwork',
        'options': [
            {'text': 'Активный участник, поддерживаю других', 'score': 5},
            {'text': 'Надёжный исполнитель', 'score': 4},
            {'text': 'Работаю независимо', 'score': 2},
            {'text': 'Минимальное участие', 'score': 1}
        ]
    },
    {
        'text': 'При распределении задач в команде:',
        'competency': 'teamwork',
        'options': [
            {'text': 'Учитываю сильные стороны каждого', 'score': 5},
            {'text': 'Распределяю справедливо', 'score': 4},
            {'text': 'Беру свою часть', 'score': 2},
            {'text': 'Избегаю ответственности', 'score': 1}
        ]
    },
    {
        'text': 'Ваше отношение к успеху команды:',
        'competency': 'teamwork',
        'options': [
            {'text': 'Общий успех важнее личного', 'score': 5},
            {'text': 'Важны и личные, и командные цели', 'score': 4},
            {'text': 'Личные цели в приоритете', 'score': 2},
            {'text': 'Только личные интересы', 'score': 1}
        ]
    },
    
    # Решение проблем
    {
        'text': 'При столкновении с проблемой вы:',
        'competency': 'problem_solving',
        'options': [
            {'text': 'Анализирую проблему системно', 'score': 5},
            {'text': 'Ищу несколько вариантов решения', 'score': 4},
            {'text': 'Пробую первое пришедшее решение', 'score': 2},
            {'text': 'Обращаюсь за помощью сразу', 'score': 1}
        ]
    },
    {
        'text': 'Ваш подход к сложным задачам:',
        'competency': 'problem_solving',
        'options': [
            {'text': 'Разбиваю на части и решаю пошагово', 'score': 5},
            {'text': 'Изучаю проблему и ищу решение', 'score': 4},
            {'text': 'Пробую разные подходы', 'score': 3},
            {'text': 'Избегаю сложных задач', 'score': 1}
        ]
    },
    {
        'text': 'Когда решение не работает:',
        'competency': 'problem_solving',
        'options': [
            {'text': 'Анализирую причину и пробую другой подход', 'score': 5},
            {'text': 'Пробую альтернативные решения', 'score': 4},
            {'text': 'Повторяю попытки', 'score': 2},
            {'text': 'Сдаюсь', 'score': 1}
        ]
    },
    {
        'text': 'Ваша способность находить корень проблемы:',
        'competency': 'problem_solving',
        'options': [
            {'text': 'Всегда нахожу первопричину', 'score': 5},
            {'text': 'Часто нахожу', 'score': 4},
            {'text': 'Иногда нахожу', 'score': 2},
            {'text': 'Фокусируюсь на симптомах', 'score': 1}
        ]
    },
    {
        'text': 'При решении технических проблем:',
        'competency': 'problem_solving',
        'options': [
            {'text': 'Использую системный подход и логику', 'score': 5},
            {'text': 'Проверяю по чек-листу', 'score': 4},
            {'text': 'Пробую наугад', 'score': 2},
            {'text': 'Сразу ищу готовое решение', 'score': 1}
        ]
    },
    
    # Саморегуляция
    {
        'text': 'Ваш контроль над эмоциями:',
        'competency': 'self_regulation',
        'options': [
            {'text': 'Всегда контролирую свои реакции', 'score': 5},
            {'text': 'Часто контролирую', 'score': 4},
            {'text': 'Иногда теряю контроль', 'score': 2},
            {'text': 'Трудно контролировать', 'score': 1}
        ]
    },
    {
        'text': 'При стрессе вы:',
        'competency': 'self_regulation',
        'options': [
            {'text': 'Использую техники управления стрессом', 'score': 5},
            {'text': 'Стараюсь сохранять спокойствие', 'score': 3},
            {'text': 'Трудно справляться', 'score': 2},
            {'text': 'Паникую', 'score': 1}
        ]
    },
    {
        'text': 'Ваша мотивация к работе:',
        'competency': 'self_regulation',
        'options': [
            {'text': 'Всегда нахожу внутреннюю мотивацию', 'score': 5},
            {'text': 'Мотивирован большинством задач', 'score': 4},
            {'text': 'Нужна внешняя мотивация', 'score': 2},
            {'text': 'Часто теряю мотивацию', 'score': 1}
        ]
    },
    {
        'text': 'Ваша способность к самодисциплине:',
        'competency': 'self_regulation',
        'options': [
            {'text': 'Высокая самодисциплина', 'score': 5},
            {'text': 'Хорошая самодисциплина', 'score': 4},
            {'text': 'Средняя самодисциплина', 'score': 2},
            {'text': 'Низкая самодисциплина', 'score': 1}
        ]
    },
    {
        'text': 'При неудачах вы:',
        'competency': 'self_regulation',
        'options': [
            {'text': 'Анализирую и извлекаю уроки', 'score': 5},
            {'text': 'Не сдаюсь и продолжаю', 'score': 4},
            {'text': 'Расстраиваюсь, но восстанавливаюсь', 'score': 2},
            {'text': 'Долго переживаю', 'score': 1}
        ]
    },
    
    # Цифровая грамотность
    {
        'text': 'Ваше отношение к новым цифровым инструментам:',
        'competency': 'digital_literacy',
        'options': [
            {'text': 'Быстро осваиваю и активно использую', 'score': 5},
            {'text': 'Изучаю при необходимости', 'score': 3},
            {'text': 'Использую только базовые функции', 'score': 2},
            {'text': 'Избегаю новых инструментов', 'score': 1}
        ]
    },
    {
        'text': 'Ваша способность к поиску информации в интернете:',
        'competency': 'digital_literacy',
        'options': [
            {'text': 'Эффективно нахожу нужную информацию', 'score': 5},
            {'text': 'Обычно нахожу то, что нужно', 'score': 4},
            {'text': 'Иногда трудно найти', 'score': 2},
            {'text': 'Трудно искать информацию', 'score': 1}
        ]
    },
    {
        'text': 'Ваше использование облачных сервисов:',
        'competency': 'digital_literacy',
        'options': [
            {'text': 'Активно использую для работы и хранения', 'score': 5},
            {'text': 'Использую основные сервисы', 'score': 3},
            {'text': 'Использую редко', 'score': 2},
            {'text': 'Не использую', 'score': 1}
        ]
    },
    {
        'text': 'Ваша работа с данными:',
        'competency': 'digital_literacy',
        'options': [
            {'text': 'Уверенно работаю с таблицами и базами данных', 'score': 5},
            {'text': 'Базовые навыки работы с данными', 'score': 3},
            {'text': 'Минимальные навыки', 'score': 2},
            {'text': 'Не работаю с данными', 'score': 1}
        ]
    },
    {
        'text': 'Ваша цифровая безопасность:',
        'competency': 'digital_literacy',
        'options': [
            {'text': 'Соблюдаю все правила безопасности', 'score': 5},
            {'text': 'Знаю основные правила', 'score': 3},
            {'text': 'Минимальные знания', 'score': 2},
            {'text': 'Не задумываюсь о безопасности', 'score': 1}
        ]
    },
]

def init_database():
    """Инициализация базы данных"""
    with app.app_context():
        # Создание таблиц
        db.create_all()
        
        # Проверка, есть ли уже вопросы
        if Question.query.count() > 0:
            print("База данных уже инициализирована!")
            return
        
        # Создание тестового администратора
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@dubna.ru',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                full_name='Администратор системы'
            )
            db.session.add(admin)
            print("Создан администратор: admin / admin123")
        
        # Создание тестового преподавателя
        teacher = User.query.filter_by(username='teacher').first()
        if not teacher:
            teacher = User(
                username='teacher',
                email='teacher@dubna.ru',
                password_hash=generate_password_hash('teacher123'),
                role='teacher',
                full_name='Тестовый преподаватель'
            )
            db.session.add(teacher)
            print("Создан преподаватель: teacher / teacher123")
        
        # Создание тестового студента
        student = User.query.filter_by(username='student').first()
        if not student:
            student = User(
                username='student',
                email='student@dubna.ru',
                password_hash=generate_password_hash('student123'),
                role='student',
                full_name='ИВАН ПОКРОВСКИЙ',
                faculty='ИСАУ',
                course=1
            )
            db.session.add(student)
            print("Создан студент: student / student123")
            print("   ФИО: ИВАН ПОКРОВСКИЙ")
            print("   Факультет: ИСАУ")
            print("   Курс: 1")
            print("   Группа: 1011")
        
        # Добавление вопросов
        print("Добавление вопросов...")
        for i, q_data in enumerate(SAMPLE_QUESTIONS):
            question = Question(
                text=q_data['text'],
                competency=q_data['competency'],
                order_num=i + 1,
                active=True
            )
            db.session.add(question)
            db.session.flush()
            
            # Добавление вариантов ответа
            for j, opt in enumerate(q_data['options']):
                option = QuestionOption(
                    question_id=question.id,
                    text=opt['text'],
                    score=opt['score'],
                    order_num=j + 1
                )
                db.session.add(option)
        
        db.session.commit()
        print(f"✅ База данных инициализирована!")
        print(f"   - Создано {len(SAMPLE_QUESTIONS)} вопросов")
        print(f"   - Создано {sum(len(q['options']) for q in SAMPLE_QUESTIONS)} вариантов ответов")
        print(f"   - Созданы тестовые пользователи")

if __name__ == '__main__':
    init_database()

