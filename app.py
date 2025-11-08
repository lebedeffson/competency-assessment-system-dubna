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
COMPETENCIES = {
    'critical_thinking': {
        'name': 'Критическое мышление',
        'description': 'Способность анализировать информацию, выявлять причинно-следственные связи и принимать обоснованные решения',
        'career_fields': ['Аналитика', 'Исследования', 'Консалтинг', 'IT', 'Финансы', 'Юриспруденция']
    },
    'communication': {
        'name': 'Коммуникация',
        'description': 'Эффективное взаимодействие, способность ясно излагать мысли и работать в команде',
        'career_fields': ['HR', 'Продажи', 'PR', 'Менеджмент', 'Журналистика', 'Образование']
    },
    'creativity': {
        'name': 'Креативность',
        'description': 'Генерация новых идей, нестандартное мышление и инновационный подход',
        'career_fields': ['Маркетинг', 'Дизайн', 'R&D', 'Продуктовая разработка', 'Реклама', 'Искусство']
    },
    'emotional_intelligence': {
        'name': 'Эмоциональный интеллект',
        'description': 'Понимание своих и чужих эмоций, эмпатия и управление межличностными отношениями',
        'career_fields': ['Психология', 'Образование', 'Социальная работа', 'Управление', 'Медицина', 'Коучинг']
    },
    'adaptability': {
        'name': 'Адаптивность',
        'description': 'Гибкость мышления, способность быстро подстраиваться под изменения',
        'career_fields': ['Стартапы', 'Проектный менеджмент', 'IT', 'Консалтинг', 'Торговля', 'Сервис']
    },
    'time_management': {
        'name': 'Управление временем',
        'description': 'Планирование, приоритизация и эффективная организация рабочего процесса',
        'career_fields': ['Управление проектами', 'Администрирование', 'Операционный менеджмент', 'Любая сфера']
    },
    'teamwork': {
        'name': 'Командная работа',
        'description': 'Способность продуктивно работать в коллективе и достигать общих целей',
        'career_fields': ['Любая сфера с командной работой', 'Спорт', 'Производство', 'Сервис']
    },
    'problem_solving': {
        'name': 'Решение проблем',
        'description': 'Системный подход к поиску решений сложных задач',
        'career_fields': ['Инжиниринг', 'IT', 'Наука', 'Бизнес-аналитика', 'Консалтинг', 'Исследования']
    },
    'self_regulation': {
        'name': 'Саморегуляция',
        'description': 'Контроль эмоций, мотивация, стрессоустойчивость',
        'career_fields': ['Высоконагруженные позиции', 'Руководство', 'Кризисное управление', 'Медицина', 'Спорт']
    },
    'digital_literacy': {
        'name': 'Цифровая грамотность',
        'description': 'Уверенное владение цифровыми инструментами и технологиями',
        'career_fields': ['IT', 'Digital-маркетинг', 'Медиа', 'Data Science', 'Кибербезопасность', 'Любая современная сфера']
    }
}

def calculate_competency_profile(answers):
    """
    Алгоритм построения личностной карты компетенций
    на основе методики оценки надпрофессиональных компетенций
    """
    scores = {comp: 0 for comp in COMPETENCIES.keys()}
    max_scores = {comp: 0 for comp in COMPETENCIES.keys()}
    
    # Подсчёт баллов по каждой компетенции
    for answer in answers:
        question = Question.query.get(answer['question_id'])
        if question:
            option = QuestionOption.query.get(answer['option_id'])
            if option:
                scores[question.competency] += option.score
                max_scores[question.competency] += 5  # Максимальный балл за вопрос
    
    # Нормализация (в процентах)
    normalized_scores = {}
    for comp in COMPETENCIES.keys():
        if max_scores[comp] > 0:
            normalized_scores[comp] = round((scores[comp] / max_scores[comp]) * 100, 1)
        else:
            normalized_scores[comp] = 0
    
    return normalized_scores

def generate_recommendations(scores):
    """
    Алгоритм формирования персонализированных рекомендаций
    на основе профиля надпрофессиональных компетенций
    """
    recommendations = {
        'strong_competencies': [],
        'development_areas': [],
        'career_paths': [],
        'courses': [],
        'activities': []
    }
    
    # Сортировка компетенций по уровню
    sorted_comps = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Сильные стороны (топ-3)
    for comp, score in sorted_comps[:3]:
        if score >= 70:
            recommendations['strong_competencies'].append({
                'name': COMPETENCIES[comp]['name'],
                'score': score,
                'description': COMPETENCIES[comp]['description']
            })
    
    # Области развития (низкие баллы)
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
        career_fields.update(COMPETENCIES[comp]['career_fields'])
    recommendations['career_paths'] = list(career_fields)[:6]
    
    # Рекомендации по развитию
    development_map = {
        'critical_thinking': {
            'courses': ['Логика и аргументация', 'Анализ данных', 'Системное мышление'],
            'activities': ['Решение кейсов', 'Участие в дискуссионных клубах', 'Чтение научной литературы']
        },
        'communication': {
            'courses': ['Публичные выступления', 'Деловое общение', 'Переговоры'],
            'activities': ['Дебаты', 'Волонтёрство', 'Студенческие конференции']
        },
        'creativity': {
            'courses': ['Дизайн-мышление', 'ТРИЗ', 'Креативные индустрии'],
            'activities': ['Хакатоны', 'Творческие проекты', 'Мозговые штурмы']
        },
        'emotional_intelligence': {
            'courses': ['Психология общения', 'Управление конфликтами', 'Эмпатия'],
            'activities': ['Тренинги по EQ', 'Групповая терапия', 'Менторство']
        },
        'adaptability': {
            'courses': ['Управление изменениями', 'Agile', 'Стресс-менеджмент'],
            'activities': ['Работа в стартапах', 'Путешествия', 'Новые хобби']
        },
        'time_management': {
            'courses': ['Тайм-менеджмент', 'GTD', 'Продуктивность'],
            'activities': ['Планирование дня', 'Pomodoro техника', 'Ведение дневника']
        },
        'teamwork': {
            'courses': ['Командная работа', 'Управление проектами', 'Фасилитация'],
            'activities': ['Групповые проекты', 'Спортивные команды', 'Волонтёрство']
        },
        'problem_solving': {
            'courses': ['Алгоритмы', 'Системный анализ', 'Инженерное мышление'],
            'activities': ['Олимпиады', 'Кейс-чемпионаты', 'Научные проекты']
        },
        'self_regulation': {
            'courses': ['Майндфулнесс', 'Стресс-менеджмент', 'Самоорганизация'],
            'activities': ['Медитация', 'Спорт', 'Йога', 'Дыхательные практики']
        },
        'digital_literacy': {
            'courses': ['Цифровые инструменты', 'Data Science', 'Кибербезопасность'],
            'activities': ['Онлайн-курсы', 'IT-проекты', 'Сертификации']
        }
    }
    
    # Персонализированные рекомендации
    for comp, score in sorted_comps:
        if score < 70 and comp in development_map:
            recommendations['courses'].extend(development_map[comp]['courses'][:2])
            recommendations['activities'].extend(development_map[comp]['activities'][:2])
    
    # Удаление дубликатов
    recommendations['courses'] = list(dict.fromkeys(recommendations['courses']))[:5]
    recommendations['activities'] = list(dict.fromkeys(recommendations['activities']))[:5]
    
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
    return render_template('test.html', questions=questions, competencies=COMPETENCIES)

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
    
    scores = json.loads(result.scores)
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
    
    # Открытые профили студентов
    public_students = User.query.filter_by(role='student', profile_visibility=True).all()
    
    return render_template('teacher_dashboard.html', stats=stats, students=public_students, competencies=COMPETENCIES)

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
    
    return render_template('admin_dashboard.html', users=users, questions=questions, stats=stats, competencies=COMPETENCIES)

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
            for comp, score in scores.items():
                if comp in all_scores:
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
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
