"""
Скрипт инициализации базы данных с тестовыми вопросами
"""
from app import app, db, User, Question, QuestionOption
from werkzeug.security import generate_password_hash

# Тестовые вопросы для каждой компетенции (по 5 вопросов на компетенцию)
SAMPLE_QUESTIONS = [
    # Критическое мышление (варианты: частота, согласие, предпочтения)
    {
        'text': 'Мне нравится разбирать сложные задачи на составные части для анализа',
        'competency': 'critical_thinking',
        'options': [
            {'text': 'всегда', 'score': 4},
            {'text': 'часто', 'score': 3},
            {'text': 'редко', 'score': 2},
            {'text': 'никогда', 'score': 1}
        ]
    },
    {
        'text': 'Когда я слышу новую информацию, мне нравится проверять её из разных источников',
        'competency': 'critical_thinking',
        'options': [
            {'text': 'полностью согласен', 'score': 4},
            {'text': 'скорее согласен', 'score': 3},
            {'text': 'скорее не согласен', 'score': 2},
            {'text': 'полностью не согласен', 'score': 1}
        ]
    },
    {
        'text': 'Мне нравится собирать и взвешивать все факты перед важным решением',
        'competency': 'critical_thinking',
        'options': [
            {'text': 'предпочитаю', 'score': 4},
            {'text': 'скорее предпочитаю', 'score': 3},
            {'text': 'скорее не предпочитаю', 'score': 2},
            {'text': 'не предпочитаю', 'score': 1}
        ]
    },
    {
        'text': 'Я предпочитаю изучать все стороны противоречий, а не выбирать одну',
        'competency': 'critical_thinking',
        'options': [
            {'text': 'полностью верно', 'score': 4},
            {'text': 'скорее верно', 'score': 3},
            {'text': 'скорее неверно', 'score': 2},
            {'text': 'полностью неверно', 'score': 1}
        ]
    },
    {
        'text': 'Мне нравится системный подход к анализу проблем с учетом всех аспектов',
        'competency': 'critical_thinking',
        'options': [
            {'text': 'всегда', 'score': 4},
            {'text': 'часто', 'score': 3},
            {'text': 'редко', 'score': 2},
            {'text': 'никогда', 'score': 1}
        ]
    },
    {
        'text': 'Когда я решаю задачи, мне легко выявлять скрытые предположения',
        'competency': 'critical_thinking',
        'options': [
            {'text': 'очень легко', 'score': 4},
            {'text': 'достаточно легко', 'score': 3},
            {'text': 'довольно сложно', 'score': 2},
            {'text': 'очень сложно', 'score': 1}
        ]
    },
    {
        'text': 'Я чувствую себя комфортно, оценивая качество доводов и аргументов',
        'competency': 'critical_thinking',
        'options': [
            {'text': 'полностью уверен', 'score': 4},
            {'text': 'в основном уверен', 'score': 3},
            {'text': 'в основном не уверен', 'score': 2},
            {'text': 'совсем не уверен', 'score': 1}
        ]
    },
    {
        'text': 'Мне интересно находить логические ошибки в рассуждениях',
        'competency': 'critical_thinking',
        'options': [
            {'text': 'предпочитаю', 'score': 4},
            {'text': 'скорее предпочитаю', 'score': 3},
            {'text': 'скорее не предпочитаю', 'score': 2},
            {'text': 'не предпочитаю', 'score': 1}
        ]
    },
    {
        'text': 'Я предпочитаю переосмысливать проблемы под новым углом зрения',
        'competency': 'critical_thinking',
        'options': [
            {'text': 'полностью верно', 'score': 4},
            {'text': 'скорее верно', 'score': 3},
            {'text': 'скорее неверно', 'score': 2},
            {'text': 'полностью неверно', 'score': 1}
        ]
    },
    {
        'text': 'Когда я принимаю решения, мне нравится анализировать долгосрочные последствия',
        'competency': 'critical_thinking',
        'options': [
            {'text': 'всегда', 'score': 4},
            {'text': 'часто', 'score': 3},
            {'text': 'редко', 'score': 2},
            {'text': 'никогда', 'score': 1}
        ]
    },
    
    # Коммуникация (варианты: уверенность, сложность, частота)
    {
        'text': 'Мне нравится общаться с большими группами людей',
        'competency': 'communication',
        'options': [
            {'text': 'полностью уверен', 'score': 4},
            {'text': 'в основном уверен', 'score': 3},
            {'text': 'в основном не уверен', 'score': 2},
            {'text': 'совсем не уверен', 'score': 1}
        ]
    },
    {
        'text': 'Когда объясняю сложное, мне нравится адаптировать язык под аудиторию',
        'competency': 'communication',
        'options': [
            {'text': 'очень легко', 'score': 4},
            {'text': 'достаточно легко', 'score': 3},
            {'text': 'довольно сложно', 'score': 2},
            {'text': 'очень сложно', 'score': 1}
        ]
    },
    {
        'text': 'Мне нравится разрешать конфликты через диалог',
        'competency': 'communication',
        'options': [
            {'text': 'всегда', 'score': 4},
            {'text': 'часто', 'score': 3},
            {'text': 'редко', 'score': 2},
            {'text': 'никогда', 'score': 1}
        ]
    },
    {
        'text': 'Я предпочитаю публичные выступления и презентации группе людей',
        'competency': 'communication',
        'options': [
            {'text': 'полностью согласен', 'score': 4},
            {'text': 'скорее согласен', 'score': 3},
            {'text': 'скорее не согласен', 'score': 2},
            {'text': 'полностью не согласен', 'score': 1}
        ]
    },
    {
        'text': 'Мне нравится писать четкие и структурированные сообщения',
        'competency': 'communication',
        'options': [
            {'text': 'предпочитаю', 'score': 4},
            {'text': 'скорее предпочитаю', 'score': 3},
            {'text': 'скорее не предпочитаю', 'score': 2},
            {'text': 'не предпочитаю', 'score': 1}
        ]
    },
    {
        'text': 'Когда я общаюсь, мне легко активно слушать собеседника',
        'competency': 'communication',
        'options': [
            {'text': 'полностью верно', 'score': 4},
            {'text': 'скорее верно', 'score': 3},
            {'text': 'скорее неверно', 'score': 2},
            {'text': 'полностью неверно', 'score': 1}
        ]
    },
    {
        'text': 'Я чувствую себя комфортно, давая конструктивную обратную связь',
        'competency': 'communication',
        'options': [
            {'text': 'очень легко', 'score': 4},
            {'text': 'достаточно легко', 'score': 3},
            {'text': 'довольно сложно', 'score': 2},
            {'text': 'очень сложно', 'score': 1}
        ]
    },
    {
        'text': 'Мне интересно работать с трудными собеседниками',
        'competency': 'communication',
        'options': [
            {'text': 'полностью уверен', 'score': 4},
            {'text': 'в основном уверен', 'score': 3},
            {'text': 'в основном не уверен', 'score': 2},
            {'text': 'совсем не уверен', 'score': 1}
        ]
    },
    {
        'text': 'Я предпочитаю создавать убедительные аргументы в дискуссиях',
        'competency': 'communication',
        'options': [
            {'text': 'всегда', 'score': 4},
            {'text': 'часто', 'score': 3},
            {'text': 'редко', 'score': 2},
            {'text': 'никогда', 'score': 1}
        ]
    },
    {
        'text': 'Когда нужно договориться, мне нравится проводить переговоры',
        'competency': 'communication',
        'options': [
            {'text': 'полностью согласен', 'score': 4},
            {'text': 'скорее согласен', 'score': 3},
            {'text': 'скорее не согласен', 'score': 2},
            {'text': 'полностью не согласен', 'score': 1}
        ]
    },
    
    # Эмоциональный интеллект (варианты: согласие, сложность, уверенность)
    {
        'text': 'Мне нравится поддерживать коллег, когда им трудно',
        'competency': 'emotional_intelligence',
        'options': [
            {'text': 'полностью верно', 'score': 4},
            {'text': 'скорее верно', 'score': 3},
            {'text': 'скорее неверно', 'score': 2},
            {'text': 'полностью неверно', 'score': 1}
        ]
    },
    {
        'text': 'Я предпочитаю понимать причины своих эмоций',
        'competency': 'emotional_intelligence',
        'options': [
            {'text': 'очень легко', 'score': 4},
            {'text': 'достаточно легко', 'score': 3},
            {'text': 'довольно сложно', 'score': 2},
            {'text': 'очень сложно', 'score': 1}
        ]
    },
    {
        'text': 'Мне нравится чувствовать эмоциональный фон в команде',
        'competency': 'emotional_intelligence',
        'options': [
            {'text': 'полностью уверен', 'score': 4},
            {'text': 'в основном уверен', 'score': 3},
            {'text': 'в основном не уверен', 'score': 2},
            {'text': 'совсем не уверен', 'score': 1}
        ]
    },
    {
        'text': 'Когда я в стрессе, мне нравится сохранять спокойствие',
        'competency': 'emotional_intelligence',
        'options': [
            {'text': 'всегда', 'score': 4},
            {'text': 'часто', 'score': 3},
            {'text': 'редко', 'score': 2},
            {'text': 'никогда', 'score': 1}
        ]
    },
    {
        'text': 'Я чувствую себя комфортно, сопереживая и понимая чувства других',
        'competency': 'emotional_intelligence',
        'options': [
            {'text': 'полностью согласен', 'score': 4},
            {'text': 'скорее согласен', 'score': 3},
            {'text': 'скорее не согласен', 'score': 2},
            {'text': 'полностью не согласен', 'score': 1}
        ]
    },
    {
        'text': 'Мне интересно разрешать конфликты, учитывая эмоции всех сторон',
        'competency': 'emotional_intelligence',
        'options': [
            {'text': 'предпочитаю', 'score': 4},
            {'text': 'скорее предпочитаю', 'score': 3},
            {'text': 'скорее не предпочитаю', 'score': 2},
            {'text': 'не предпочитаю', 'score': 1}
        ]
    },
    {
        'text': 'Я предпочитаю работать с людьми разных характеров и настроений',
        'competency': 'emotional_intelligence',
        'options': [
            {'text': 'очень легко', 'score': 4},
            {'text': 'достаточно легко', 'score': 3},
            {'text': 'довольно сложно', 'score': 2},
            {'text': 'очень сложно', 'score': 1}
        ]
    },
    {
        'text': 'Мне легко регулировать свое эмоциональное состояние',
        'competency': 'emotional_intelligence',
        'options': [
            {'text': 'полностью уверен', 'score': 4},
            {'text': 'в основном уверен', 'score': 3},
            {'text': 'в основном не уверен', 'score': 2},
            {'text': 'совсем не уверен', 'score': 1}
        ]
    },
    {
        'text': 'Когда я вижу эмоции других, мне нравится понимать их потребности',
        'competency': 'emotional_intelligence',
        'options': [
            {'text': 'полностью верно', 'score': 4},
            {'text': 'скорее верно', 'score': 3},
            {'text': 'скорее неверно', 'score': 2},
            {'text': 'полностью неверно', 'score': 1}
        ]
    },
    {
        'text': 'Я предпочитаю помогать людям справляться с их эмоциями',
        'competency': 'emotional_intelligence',
        'options': [
            {'text': 'всегда', 'score': 4},
            {'text': 'часто', 'score': 3},
            {'text': 'редко', 'score': 2},
            {'text': 'никогда', 'score': 1}
        ]
    },
    
    # Командная работа (варианты: предпочтения, частота, согласие)
    {
        'text': 'Мне нравится активное участие в командных проектах',
        'competency': 'teamwork',
        'options': [
            {'text': 'предпочитаю', 'score': 4},
            {'text': 'скорее предпочитаю', 'score': 3},
            {'text': 'скорее не предпочитаю', 'score': 2},
            {'text': 'не предпочитаю', 'score': 1}
        ]
    },
    {
        'text': 'Когда в команде конфликт, мне нравится его разрешать',
        'competency': 'teamwork',
        'options': [
            {'text': 'всегда', 'score': 4},
            {'text': 'часто', 'score': 3},
            {'text': 'редко', 'score': 2},
            {'text': 'никогда', 'score': 1}
        ]
    },
    {
        'text': 'Мне нравится поддерживать и мотивировать коллег',
        'competency': 'teamwork',
        'options': [
            {'text': 'полностью согласен', 'score': 4},
            {'text': 'скорее согласен', 'score': 3},
            {'text': 'скорее не согласен', 'score': 2},
            {'text': 'полностью не согласен', 'score': 1}
        ]
    },
    {
        'text': 'Я предпочитаю распределять задачи с учетом сильных сторон каждого',
        'competency': 'teamwork',
        'options': [
            {'text': 'очень легко', 'score': 4},
            {'text': 'достаточно легко', 'score': 3},
            {'text': 'довольно сложно', 'score': 2},
            {'text': 'очень сложно', 'score': 1}
        ]
    },
    {
        'text': 'Мне нравится достигать командных целей больше, чем личных',
        'competency': 'teamwork',
        'options': [
            {'text': 'полностью уверен', 'score': 4},
            {'text': 'в основном уверен', 'score': 3},
            {'text': 'в основном не уверен', 'score': 2},
            {'text': 'совсем не уверен', 'score': 1}
        ]
    },
    {
        'text': 'Я чувствую себя комфортно в совместных обсуждениях идей',
        'competency': 'teamwork',
        'options': [
            {'text': 'предпочитаю', 'score': 4},
            {'text': 'скорее предпочитаю', 'score': 3},
            {'text': 'скорее не предпочитаю', 'score': 2},
            {'text': 'не предпочитаю', 'score': 1}
        ]
    },
    {
        'text': 'Мне интересно брать на себя ответственность за командный результат',
        'competency': 'teamwork',
        'options': [
            {'text': 'полностью верно', 'score': 4},
            {'text': 'скорее верно', 'score': 3},
            {'text': 'скорее неверно', 'score': 2},
            {'text': 'полностью неверно', 'score': 1}
        ]
    },
    {
        'text': 'Я предпочитаю учитывать мнения всех членов команды',
        'competency': 'teamwork',
        'options': [
            {'text': 'всегда', 'score': 4},
            {'text': 'часто', 'score': 3},
            {'text': 'редко', 'score': 2},
            {'text': 'никогда', 'score': 1}
        ]
    },
    {
        'text': 'Мне легко работать в команде с разными типами людей',
        'competency': 'teamwork',
        'options': [
            {'text': 'полностью согласен', 'score': 4},
            {'text': 'скорее согласен', 'score': 3},
            {'text': 'скорее не согласен', 'score': 2},
            {'text': 'полностью не согласен', 'score': 1}
        ]
    },
    {
        'text': 'Когда коллеги просят помощи, мне нравится им помогать',
        'competency': 'teamwork',
        'options': [
            {'text': 'очень легко', 'score': 4},
            {'text': 'достаточно легко', 'score': 3},
            {'text': 'довольно сложно', 'score': 2},
            {'text': 'очень сложно', 'score': 1}
        ]
    },
    
    # Управление временем (варианты: сложность, уверенность, согласие)
    {
        'text': 'Мне нравится планировать свой день с деталями и приоритетами',
        'competency': 'time_management',
        'options': [
            {'text': 'полностью уверен', 'score': 4},
            {'text': 'в основном уверен', 'score': 3},
            {'text': 'в основном не уверен', 'score': 2},
            {'text': 'совсем не уверен', 'score': 1}
        ]
    },
    {
        'text': 'Я предпочитаю работать с дедлайнами и успевать в срок',
        'competency': 'time_management',
        'options': [
            {'text': 'очень легко', 'score': 4},
            {'text': 'достаточно легко', 'score': 3},
            {'text': 'довольно сложно', 'score': 2},
            {'text': 'очень сложно', 'score': 1}
        ]
    },
    {
        'text': 'Мне нравится определять важность задач и расставлять приоритеты',
        'competency': 'time_management',
        'options': [
            {'text': 'полностью согласен', 'score': 4},
            {'text': 'скорее согласен', 'score': 3},
            {'text': 'скорее не согласен', 'score': 2},
            {'text': 'полностью не согласен', 'score': 1}
        ]
    },
    {
        'text': 'Когда много задач, мне нравится систематизировать их и работать по плану',
        'competency': 'time_management',
        'options': [
            {'text': 'предпочитаю', 'score': 4},
            {'text': 'скорее предпочитаю', 'score': 3},
            {'text': 'скорее не предпочитаю', 'score': 2},
            {'text': 'не предпочитаю', 'score': 1}
        ]
    },
    {
        'text': 'Мне нравится бороться с прокрастинацией и откладыванием дел',
        'competency': 'time_management',
        'options': [
            {'text': 'всегда', 'score': 4},
            {'text': 'часто', 'score': 3},
            {'text': 'редко', 'score': 2},
            {'text': 'никогда', 'score': 1}
        ]
    },
    {
        'text': 'Я чувствую себя комфортно, используя инструменты для трекинга времени',
        'competency': 'time_management',
        'options': [
            {'text': 'полностью уверен', 'score': 4},
            {'text': 'в основном уверен', 'score': 3},
            {'text': 'в основном не уверен', 'score': 2},
            {'text': 'совсем не уверен', 'score': 1}
        ]
    },
    {
        'text': 'Мне интересно многозадачность и переключение между делами',
        'competency': 'time_management',
        'options': [
            {'text': 'очень легко', 'score': 4},
            {'text': 'достаточно легко', 'score': 3},
            {'text': 'довольно сложно', 'score': 2},
            {'text': 'очень сложно', 'score': 1}
        ]
    },
    {
        'text': 'Я предпочитаю откладывать менее важные дела ради критичных',
        'competency': 'time_management',
        'options': [
            {'text': 'полностью согласен', 'score': 4},
            {'text': 'скорее согласен', 'score': 3},
            {'text': 'скорее не согласен', 'score': 2},
            {'text': 'полностью не согласен', 'score': 1}
        ]
    },
    {
        'text': 'Мне нравится начинать день с планирования задач',
        'competency': 'time_management',
        'options': [
            {'text': 'предпочитаю', 'score': 4},
            {'text': 'скорее предпочитаю', 'score': 3},
            {'text': 'скорее не предпочитаю', 'score': 2},
            {'text': 'не предпочитаю', 'score': 1}
        ]
    },
    {
        'text': 'Я чувствую себя комфортно, отслеживая сроки выполнения задач',
        'competency': 'time_management',
        'options': [
            {'text': 'всегда', 'score': 4},
            {'text': 'часто', 'score': 3},
            {'text': 'редко', 'score': 2},
            {'text': 'никогда', 'score': 1}
        ]
    }
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

