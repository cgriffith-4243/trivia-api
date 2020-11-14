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
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r'/*': {'origins': '*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, PATCH, POST, DELETE, OPTIONS')

    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
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

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
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

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
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

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
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

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
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

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
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
    

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
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

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
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

    