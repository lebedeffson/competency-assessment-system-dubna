from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import numpy as np
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# Модели базы данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student, teacher, admin
    full_name = db.Column(db.String(100))
    faculty = db.Column(db.String(100))
    course = db.Column(db.Integer)
    profile_visibility = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    test_results = db.relationship('TestResult', backref='user', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    competency = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50))
    active = db.Column(db.Boolean, default=True)
    order_num = db.Column(db.Integer)
    options = db.relationship('QuestionOption', backref='question', lazy=True, cascade='all, delete-orphan')

class QuestionOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    order_num = db.Column(db.Integer)

class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_date = db.Column(db.DateTime, default=datetime.utcnow)
    answers = db.Column(db.Text)  # JSON строка с ответами
    scores = db.Column(db.Text)  # JSON строка с баллами по компетенциям
    recommendations = db.Column(db.Text)
    profile_data = db.Column(db.Text)  # JSON данные для визуализации

# Модель надпрофессиональных компетенций
# Объединены компетенции: problem_solving + digital_literacy -> critical_thinking
# creativity -> critical_thinking (креативное решение проблем)
# adaptability + self_regulation -> emotional_intelligence (адаптивность и саморегуляция)
COMPETENCIES = {
    'critical_thinking': {
        'name': 'Критическое мышление и решение проблем',
        'description': 'Способность анализировать информацию, выявлять причинно-следственные связи, принимать обоснованные решения, системно решать сложные задачи. Включает креативный подход к проблемам и цифровую грамотность',
        'career_fields': ['Аналитика', 'Исследования', 'Консалтинг', 'IT', 'Финансы', 'Юриспруденция', 'Инжиниринг', 'Наука', 'Бизнес-аналитика', 'Data Science', 'Кибербезопасность', 'R&D', 'Продуктовая разработка']
    },
    'communication': {
        'name': 'Коммуникация',
        'description': 'Эффективное взаимодействие, способность ясно излагать мысли и работать в команде',
        'career_fields': ['HR', 'Продажи', 'PR', 'Менеджмент', 'Журналистика', 'Образование', 'Маркетинг', 'Реклама']
    },
    'emotional_intelligence': {
        'name': 'Эмоциональный интеллект и саморегуляция',
        'description': 'Понимание своих и чужих эмоций, эмпатия, управление межличностными отношениями. Включает способность контролировать эмоции, адаптироваться к изменениям, стрессоустойчивость и мотивацию',
        'career_fields': ['Психология', 'Образование', 'Социальная работа', 'Управление', 'Медицина', 'Коучинг', 'Стартапы', 'Проектный менеджмент', 'Высоконагруженные позиции', 'Руководство', 'Кризисное управление']
    },
    'time_management': {
        'name': 'Управление временем и адаптивность',
        'description': 'Планирование, приоритизация и эффективная организация рабочего процесса. Включает способность быстро адаптироваться к изменениям и управлять приоритетами',
        'career_fields': ['Управление проектами', 'Администрирование', 'Операционный менеджмент', 'Любая сфера', 'Стартапы', 'IT', 'Консалтинг', 'Торговля', 'Сервис']
    },
    'teamwork': {
        'name': 'Командная работа',
        'description': 'Способность продуктивно работать в коллективе и достигать общих целей',
        'career_fields': ['Любая сфера с командной работой', 'Спорт', 'Производство', 'Сервис', 'Менеджмент', 'HR']
    }
}

COMPETENCY_ALIASES = {
    'creativity': 'critical_thinking',
    'problem_solving': 'critical_thinking',
    'digital_literacy': 'critical_thinking',
    'self_regulation': 'emotional_intelligence',
    'adaptability': 'time_management'
}

def resolve_competency_key(comp_key: str) -> str:
    """Возвращает актуальный ключ компетенции с учётом исторических данных."""
    return COMPETENCY_ALIASES.get(comp_key, comp_key)

def get_competency_display_map() -> dict:
    """Возвращает словарь для отображения компетенций (включая алиасы)."""
    display_map = {key: value for key, value in COMPETENCIES.items()}
    for alias, target in COMPETENCY_ALIASES.items():
        if target in COMPETENCIES:
            display_map[alias] = COMPETENCIES[target]
    return display_map

def merge_scores_to_current_model(raw_scores: dict) -> dict:
    """
    Приводит сохранённые результаты (в том числе старого формата) к текущей модели компетенций.
    Для объединённых компетенций используется среднее значение.
    """
    aggregated = {key: [] for key in COMPETENCIES.keys()}
    for key, value in raw_scores.items():
        resolved = resolve_competency_key(key)
        if resolved in aggregated:
            aggregated[resolved].append(value)
    normalized = {}
    for key, values in aggregated.items():
        if values:
            normalized[key] = round(sum(values) / len(values), 1)
        else:
            normalized[key] = 0
    return normalized

def calculate_competency_profile(answers):
    """
    Алгоритм построения личностной карты компетенций
    на основе методики оценки надпрофессиональных компетенций
    
    Психометрический подход:
    - Нормализация результатов к шкале 0-100%
    - Максимальный балл за вопрос: 4 (шкала 1-4)
    - Для каждой компетенции: (сумма_баллов / (количество_вопросов * 4)) * 100
    """
    scores = {comp: 0 for comp in COMPETENCIES.keys()}
    max_scores = {comp: 0 for comp in COMPETENCIES.keys()}
    
    # Подсчёт баллов по каждой компетенции
    for answer in answers:
        question = Question.query.get(answer['question_id'])
        if question:
            resolved_key = resolve_competency_key(question.competency)
            if resolved_key in COMPETENCIES:
                option = QuestionOption.query.get(answer['option_id'])
                if option:
                    scores[resolved_key] += option.score
                    max_scores[resolved_key] += 4  # Максимальный балл за вопрос (шкала 1-4)
    
    # Нормализация (в процентах) - психометрический подход
    normalized_scores = {}
    for comp in COMPETENCIES.keys():
        if max_scores[comp] > 0:
            # Формула: (набранные_баллы / максимально_возможные_баллы) * 100
            normalized_scores[comp] = round((scores[comp] / max_scores[comp]) * 100, 1)
        else:
            normalized_scores[comp] = 0
    
    return normalized_scores

def generate_recommendations(scores):
    """
    Алгоритм формирования персонализированных рекомендаций
    на основе профиля надпрофессиональных компетенций
    
    Психологическая методика:
    - Сильные стороны: топ-3 компетенции с баллом >= 70%
    - Зоны развития: компетенции с баллом < 60%
    - Карьерные траектории: на основе топ-3 компетенций
    - Персонализированные курсы и активности для компетенций < 70%
    """
    normalized_scores = merge_scores_to_current_model(scores)

    recommendations = {
        'strong_competencies': [],
        'development_areas': [],
        'career_paths': [],
        'courses': [],
        'activities': []
    }
    
    # Сортировка компетенций по уровню (только те, для которых есть вопросы)
    sorted_comps = sorted([(comp, score) for comp, score in normalized_scores.items() if score > 0],
                         key=lambda x: x[1], reverse=True)
    
    # Сильные стороны (топ-3, балл >= 70%)
    for comp, score in sorted_comps[:3]:
        if score >= 70:
            recommendations['strong_competencies'].append({
                'name': COMPETENCIES[comp]['name'],
                'score': score,
                'description': COMPETENCIES[comp]['description']
            })
    
    # Области развития (низкие баллы, < 60%)
    for comp, score in sorted_comps:
        if score < 60:
            recommendations['development_areas'].append({
                'name': COMPETENCIES[comp]['name'],
                'score': score,
                'description': COMPETENCIES[comp]['description']
            })
    
    # Рекомендации по карьере (на основе топ-3 компетенций)
    career_fields = set()
    for comp, score in sorted_comps[:3]:
        if comp in COMPETENCIES:
            career_fields.update(COMPETENCIES[comp]['career_fields'])
    recommendations['career_paths'] = list(career_fields)[:8]
    
    # Рекомендации по развитию (объединены из влитых компетенций)
    development_map = {
        'critical_thinking': {
            'courses': ['Логика и аргументация', 'Анализ данных', 'Системное мышление', 'Алгоритмы', 'Системный анализ', 'Цифровые инструменты', 'Data Science', 'Дизайн-мышление', 'ТРИЗ'],
            'activities': ['Решение кейсов', 'Участие в дискуссионных клубах', 'Чтение научной литературы', 'Олимпиады', 'Кейс-чемпионаты', 'Научные проекты', 'Онлайн-курсы', 'IT-проекты', 'Хакатоны', 'Творческие проекты']
        },
        'communication': {
            'courses': ['Публичные выступления', 'Деловое общение', 'Переговоры', 'Маркетинг и реклама'],
            'activities': ['Дебаты', 'Волонтёрство', 'Студенческие конференции', 'Творческие проекты']
        },
        'emotional_intelligence': {
            'courses': ['Психология общения', 'Управление конфликтами', 'Эмпатия', 'Майндфулнесс', 'Стресс-менеджмент', 'Самоорганизация', 'Управление изменениями', 'Agile'],
            'activities': ['Тренинги по EQ', 'Групповая терапия', 'Менторство', 'Медитация', 'Спорт', 'Йога', 'Дыхательные практики', 'Работа в стартапах', 'Новые хобби']
        },
        'time_management': {
            'courses': ['Тайм-менеджмент', 'GTD', 'Продуктивность', 'Управление изменениями', 'Agile'],
            'activities': ['Планирование дня', 'Pomodoro техника', 'Ведение дневника', 'Путешествия', 'Новые хобби']
        },
        'teamwork': {
            'courses': ['Командная работа', 'Управление проектами', 'Фасилитация'],
            'activities': ['Групповые проекты', 'Спортивные команды', 'Волонтёрство']
        }
    }
    
    # Персонализированные рекомендации (для компетенций < 70%)
    for comp, score in sorted_comps:
        if score < 70 and comp in development_map:
            recommendations['courses'].extend(development_map[comp]['courses'][:3])
            recommendations['activities'].extend(development_map[comp]['activities'][:3])
    
    # Удаление дубликатов с сохранением порядка
    recommendations['courses'] = list(dict.fromkeys(recommendations['courses']))[:6]
    recommendations['activities'] = list(dict.fromkeys(recommendations['activities']))[:6]
    
    return recommendations

# API endpoints
@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif user.role == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.json
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'success': False, 'message': 'Пользователь с таким именем уже существует'})
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'message': 'Пользователь с таким email уже существует'})
        
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            role=data.get('role', 'student'),
            full_name=data.get('full_name'),
            faculty=data.get('faculty'),
            course=data.get('course')
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Регистрация успешна'})
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        user = User.query.filter_by(username=data['username']).first()
        if user and check_password_hash(user.password_hash, data['password']):
            session['user_id'] = user.id
            session['role'] = user.role
            return jsonify({'success': True, 'role': user.role})
        return jsonify({'success': False, 'message': 'Неверные данные'})
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    results = TestResult.query.filter_by(user_id=user.id).order_by(TestResult.test_date.desc()).all()
    return render_template('student_dashboard.html', user=user, results=results)

@app.route('/test/start')
def start_test():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    questions = Question.query.filter_by(active=True).order_by(Question.order_num).all()
    if not questions:
        return render_template('error.html', message='Тест пока не настроен. Обратитесь к администратору.')
    competency_display_map = get_competency_display_map()
    for question in questions:
        question.display_competency = resolve_competency_key(question.competency)
    return render_template(
        'test.html',
        questions=questions,
        competency_display_map=competency_display_map
    )

@app.route('/test/submit', methods=['POST'])
def submit_test():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Не авторизован'})
    
    data = request.json
    answers = data['answers']
    
    # Расчёт профиля компетенций
    scores = calculate_competency_profile(answers)
    
    # Генерация рекомендаций
    recommendations = generate_recommendations(scores)
    
    # Сохранение результатов
    result = TestResult(
        user_id=session['user_id'],
        answers=json.dumps(answers, ensure_ascii=False),
        scores=json.dumps(scores, ensure_ascii=False),
        recommendations=json.dumps(recommendations, ensure_ascii=False),
        profile_data=json.dumps({'scores': scores, 'timestamp': datetime.now().isoformat()}, ensure_ascii=False)
    )
    db.session.add(result)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'result_id': result.id,
        'scores': scores,
        'recommendations': recommendations
    })

@app.route('/results/<int:result_id>')
def view_results(result_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    result = TestResult.query.get_or_404(result_id)
    
    # Проверка прав доступа
    if result.user_id != session['user_id'] and session['role'] not in ['teacher', 'admin']:
        return "Доступ запрещён", 403
    
    raw_scores = json.loads(result.scores)
    scores = merge_scores_to_current_model(raw_scores)
    recommendations = json.loads(result.recommendations)
    
    return render_template('results.html',
                         result=result,
                         scores=scores,
                         recommendations=recommendations,
                         competencies=COMPETENCIES)

@app.route('/teacher/dashboard')
def teacher_dashboard():
    if 'user_id' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    # Обезличенная статистика
    all_results = TestResult.query.all()
    stats = calculate_aggregate_stats(all_results)
    
    # Профили всех студентов
    students = User.query.filter_by(role='student').all()
    student_profiles = []
    for student in students:
        ordered_results = sorted(
            student.test_results,
            key=lambda r: r.test_date or datetime.min,
            reverse=True
        )
        last_result = ordered_results[0] if ordered_results else None
        student_profiles.append({
            'id': student.id,
            'display_name': student.full_name or student.username,
            'username': student.username,
            'faculty': student.faculty,
            'course': student.course,
            'profile_visibility': student.profile_visibility,
            'results_count': len(ordered_results),
            'last_result_id': last_result.id if last_result else None,
            'last_result_date': last_result.test_date if last_result else None
        })
    
    return render_template(
        'teacher_dashboard.html',
        stats=stats,
        competencies=COMPETENCIES,
        student_profiles=student_profiles
    )

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    users = User.query.all()
    questions = Question.query.order_by(Question.order_num).all()
    stats = {
        'total_users': User.query.count(),
        'total_tests': TestResult.query.count(),
        'total_questions': Question.query.filter_by(active=True).count()
    }
    competency_display_map = get_competency_display_map()
    questions_payload = []
    for question in questions:
        resolved_key = resolve_competency_key(question.competency)
        question.display_competency = resolved_key
        questions_payload.append({
            'id': question.id,
            'text': question.text,
            'competency': question.competency,
            'resolved_competency': resolved_key,
            'category': question.category,
            'order_num': question.order_num,
            'active': question.active,
            'options': [{
                'id': option.id,
                'text': option.text,
                'score': option.score,
                'order_num': option.order_num
            } for option in sorted(question.options, key=lambda o: o.order_num or 0)]
        })
    
    return render_template(
        'admin_dashboard.html',
        users=users,
        questions=questions,
        stats=stats,
        competencies=COMPETENCIES,
        competency_display_map=competency_display_map,
        questions_data=questions_payload
    )

@app.route('/admin/questions', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_questions():
    if 'user_id' not in session or session['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Доступ запрещён'})
    
    if request.method == 'POST':
        data = request.json
        question = Question(
            text=data['text'],
            competency=data['competency'],
            category=data.get('category'),
            order_num=data.get('order_num', Question.query.count() + 1)
        )
        db.session.add(question)
        db.session.flush()
        
        # Добавление опций ответа
        for opt in data['options']:
            option = QuestionOption(
                question_id=question.id,
                text=opt['text'],
                score=opt['score'],
                order_num=opt.get('order_num')
            )
            db.session.add(option)
        db.session.commit()
        
        return jsonify({'success': True, 'question_id': question.id})
    
    elif request.method == 'GET':
        questions = Question.query.order_by(Question.order_num).all()
        return jsonify([{
            'id': q.id,
            'text': q.text,
            'competency': q.competency,
            'resolved_competency': resolve_competency_key(q.competency),
            'category': q.category,
            'order_num': q.order_num,
            'active': q.active,
            'options': [{
                'id': o.id,
                'text': o.text,
                'score': o.score,
                'order_num': o.order_num
            } for o in q.options]
        } for q in questions])
    
    elif request.method == 'PUT':
        data = request.json
        question = Question.query.get(data['id'])
        if question:
            question.text = data.get('text', question.text)
            question.competency = data.get('competency', question.competency)
            question.category = data.get('category', question.category)
            question.order_num = data.get('order_num', question.order_num)
            question.active = data.get('active', question.active)
            if 'options' in data:
                QuestionOption.query.filter_by(question_id=question.id).delete(synchronize_session=False)
                for idx, opt in enumerate(data['options'], start=1):
                    option = QuestionOption(
                        question_id=question.id,
                        text=opt['text'],
                        score=opt['score'],
                        order_num=opt.get('order_num') or idx
                    )
                    db.session.add(option)
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Вопрос не найден'})
    
    elif request.method == 'DELETE':
        question_id = request.args.get('id')
        question = Question.query.get(question_id)
        if question:
            db.session.delete(question)
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Вопрос не найден'})

@app.route('/api/stats')
def api_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Не авторизован'}), 401
    
    all_results = TestResult.query.all()
    stats = calculate_aggregate_stats(all_results)
    return jsonify(stats)

def calculate_aggregate_stats(results):
    """Расчёт обезличенной статистики для преподавателей"""
    if not results:
        return {}
    
    all_scores = {comp: [] for comp in COMPETENCIES.keys()}
    
    for result in results:
        try:
            scores = json.loads(result.scores)
            merged_scores = merge_scores_to_current_model(scores)
            for comp, score in merged_scores.items():
                if comp in all_scores and score is not None:
                    all_scores[comp].append(score)
        except:
            continue
    
    stats = {}
    for comp, scores_list in all_scores.items():
        if scores_list:
            stats[comp] = {
                'mean': round(np.mean(scores_list), 1),
                'median': round(np.median(scores_list), 1),
                'std': round(np.std(scores_list), 1),
                'min': round(min(scores_list), 1),
                'max': round(max(scores_list), 1),
                'count': len(scores_list)
            }
    
    return stats

@app.route('/api/toggle_visibility', methods=['POST'])
def toggle_visibility():
    if 'user_id' not in session or session['role'] != 'student':
        return jsonify({'success': False, 'message': 'Доступ запрещён'})
    
    user = User.query.get(session['user_id'])
    user.profile_visibility = not user.profile_visibility
    db.session.commit()
    return jsonify({'success': True, 'visibility': user.profile_visibility})

if __name__ == '__main__':
    import os
    with app.app_context():
        db.create_all()
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
