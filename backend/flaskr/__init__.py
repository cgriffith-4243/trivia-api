import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.sql.expression import func

from models import setup_db, Question, Category, db

PAGINATION_LIMIT = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  CORS(app, resources={r'/*': {'origins': '*'}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, PATCH, POST, DELETE, OPTIONS')

    return response

  @app.route('/categories')
  def categories():
    page_categories = Category.query.order_by(Category.type).all()
    if page_categories:
      categories = {}
      for category in page_categories:
        categories[category.id] = category.type

      return jsonify({
        'success': True,
        'categories': categories
      }), 200
    else:
      abort(404)

  @app.route('/questions')
  def questions():
    current_page = request.args.get('page', default=1, type=int)
    questions_per_page = PAGINATION_LIMIT

    page_questions = Question.query.order_by(Question.category).paginate(current_page, questions_per_page, True)
    all_categories = Category.query.all()
    if all_categories and page_questions:
      questions = []
      for question in page_questions.items:
        questions.append(question.format())

      total_questions = page_questions.total

      categories = {}
      for category in all_categories:
        categories[category.id] = category.type
      
      return jsonify({
        'success': True,
        'questions': questions,
        'total_questions': total_questions,
        'categories': categories,
        'current_category': None
      }), 200
    else:
      abort(404)

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id): 
    question = Question.query.filter(Question.id == question_id).one_or_none()
    if question is None:
      abort(404)

    error = False
    try:
      db.session.delete(question)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
    finally:
      db.session.close()
      if not error:
        return jsonify({
          'success': True,
          'deleted': question_id
        }), 200
      else:
        abort(422)

  @app.route('/questions', methods=['POST'])
  def create_question():
    error = False
    form = request.get_json()

    question = form.get('question', None)
    answer = form.get('answer', None)
    difficulty = form.get('difficulty', None)
    category = form.get('category', None)

    if not (question and answer and difficulty and category):
      abort(422)
    
    try:
      new_question = Question(
        question = question,
        answer = answer,
        difficulty = difficulty,
        category = category
      )

      db.session.add(new_question)
      db.session.commit()
    except:
      error = True
    finally:
      db.session.close()
      if not error:
        return jsonify({
          'success': True,
          'message': 'Question was successfully created'
        }), 201
      else:
        abort(422)

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    search_term = request.json.get('searchTerm', None)
    current_page = request.args.get('page', default=1, type=int)
    questions_per_page = PAGINATION_LIMIT

    if search_term:
      page_questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).paginate(current_page, questions_per_page, True)

      questions = []
      for question in page_questions.items:
        questions.append(question.format())

      total_questions = page_questions.total
      
      return jsonify({
        'success': True,
        'questions': questions,
        'total_questions': total_questions,
        'current_category': None
      }), 200
    else:
      abort(404)

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def show_category_questions(category_id):
    current_page = request.args.get('page', default=1, type=int)
    questions_per_page = PAGINATION_LIMIT

    page_questions = Question.query.filter(Question.category == category_id).paginate(current_page, questions_per_page, True)
    current_category = Category.query.get(category_id).id
    if current_category and page_questions:
      questions = []
      for question in page_questions.items:
        questions.append(question.format())

      total_questions = page_questions.total
      
      return jsonify({
        'success': True,
        'questions': questions,
        'total_questions': total_questions,
        'current_category': current_category
      }), 200
    else:
      abort(404)

  @app.route('/quizzes', methods=['POST'])
  def show_quiz_questions():
    form = request.get_json()
    previous_questions = form.get('previous_questions', None)
    quiz_category = form.get('quiz_category', None)

    if quiz_category is None or previous_questions is None or type(previous_questions) != list or quiz_category.get('id', None) is None:
      abort(400)
    
    if quiz_category['id'] != 0 and Category.query.filter(Category.id == quiz_category['id']).scalar() is None:
       abort(404)

    questions = Question.query
    if quiz_category['id'] != 0:
      questions = questions.filter(Question.category == quiz_category['id'])

    quiz_question = questions.order_by(func.random()).filter(Question.id.notin_(previous_questions)).first()
    
    if quiz_question:
      return jsonify({
        'success': True,
        'question': quiz_question.format()
      }), 200
    else:
      return jsonify({
        'success': True
      }), 200

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad request'
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Resource not found'
    }), 404
  
  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable'
    }), 422

  @app.errorhandler(500)
  def unprocessable_entity(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Internal server error'
    }), 500

  
  return app

    