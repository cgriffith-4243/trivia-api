import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        # check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        # check response body
        self.assertEqual(type(data['categories']), dict)

    def test_questions_pagination(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        # check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        # check response body
        self.assertEqual(type(data['questions']), list)
        self.assertEqual(type(data['total_questions']), int)
        self.assertEqual(type(data['categories']), dict)
        self.assertEqual(data['current_category'], None)
        # check for expected restrictions
        self.assertEqual(len(data['questions']), 10)

    def test_delete_question_valid_id(self):
        test_id = Question.query.order_by(func.random()).first().id
        total_before = len(Question.query.all())
        response = self.client().delete('/questions/{}'.format(test_id))
        data = json.loads(response.data)
        total_after = len(Question.query.all())
        # check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        # check response body
        self.assertEqual(data['deleted'], test_id)
        # check database changes
        self.assertEqual(total_before - 1, total_after)

    def test_delete_question_invalid_id(self):
        test_id = 1000000
        total_before = len(Question.query.all())
        response = self.client().delete('/questions/{}'.format(test_id))
        data = json.loads(response.data)
        total_after = len(Question.query.all())
        # check response
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        # check response body
        self.assertEqual(type(data['message']), str)
        # check database changes
        self.assertEqual(total_before, total_after)

    def test_create_question_valid_data(self):
        test_question = {
            'question': 'test question description',
            'answer': 'test question answer',
            'difficulty': 1,
            'category': 5
        }
        total_before = len(Question.query.all())
        response = self.client().post('/questions', json=test_question)
        data = json.loads(response.data)
        total_after = len(Question.query.all())
        # check response
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        # check response body
        self.assertEqual(type(data['message']), str)
        # check database changes
        self.assertEqual(total_before + 1, total_after)
    
    def test_create_question_invalid_data(self):
        test_question = {
            'question': 'this question is',
            'answer': 'missing fields'
        }
        total_before = len(Question.query.all())
        response = self.client().post('/questions', json=test_question)
        data = json.loads(response.data)
        total_after = len(Question.query.all())
        # check response
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        # check response body
        self.assertEqual(type(data['message']), str)
        # check database changes
        self.assertEqual(total_before, total_after)
        
    def test_search_questions_valid_json(self):
        test_search = {
            'searchTerm': 'e'
        }
        response = self.client().post('/questions/search', json=test_search)
        data = json.loads(response.data)
        # check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        # check response body
        self.assertEqual(type(data['questions']), list)
        self.assertEqual(type(data['total_questions']), int)
        self.assertEqual(data['current_category'], None)

    def test_search_questions_invalid_json(self):
        test_search = {}
        response = self.client().post('/questions/search', json=test_search)
        data = json.loads(response.data)
        # check response
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        # check response body
        self.assertEqual(type(data['message']), str)

    def test_show_category_questions_valid_id(self):
        response = self.client().get('/categories/2/questions')
        data = json.loads(response.data)
        # check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        # check response body
        self.assertEqual(type(data['questions']), list)
        self.assertEqual(type(data['total_questions']), int)
        self.assertEqual(type(data['current_category']), int)
    
    def test_show_category_questions_invalid_id(self):
        response = self.client().get('/categories/z/questions')
        data = json.loads(response.data)
        # check response
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        # check response body
        self.assertEqual(type(data['message']), str)

    def test_show_quiz_questions_valid_json(self):
        test_quiz = {
            'previous_questions': [],
            'quiz_category': {
                'id': 2
                }
        }
        response = self.client().post('/quizzes', json=test_quiz)
        data = json.loads(response.data)
        # check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        # check response body
        self.assertEqual(type(data['question']), dict)

    def test_show_quiz_questions_valid_json_no_results(self):
        test_quiz = {
            'previous_questions': [20, 21, 22],
            'quiz_category': {
                'id': 1
                }
        }
        response = self.client().post('/quizzes', json=test_quiz)
        data = json.loads(response.data)
        # check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        # check response body
        self.assertFalse(data.get('questions', False))

    def test_show_quiz_questions_invalid_json_missing_quiz(self):
        test_quiz = {
            'previous_questions': []
        }
        response = self.client().post('/quizzes', json=test_quiz)
        data = json.loads(response.data)
        # check response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        # check response body
        self.assertEqual(type(data['message']), str)

    def test_show_quiz_questions_invalid_json_missing_previous(self):
        test_quiz = {
            'quiz_category': {
                'id': 2
                }
        }
        response = self.client().post('/quizzes', json=test_quiz)
        data = json.loads(response.data)
        # check response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        # check response body
        self.assertEqual(type(data['message']), str)

    def test_show_quiz_questions_invalid_json_type_previous(self):
        test_quiz = {
            'previous_questions': '',
            'quiz_category': {
                'id': 2
                }
        }
        response = self.client().post('/quizzes', json=test_quiz)
        data = json.loads(response.data)
        # check response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        # check response body
        self.assertEqual(type(data['message']), str)

    def test_show_quiz_questions_invalid_json_quiz_id(self):
        test_quiz = {
            'previous_questions': [],
            'quiz_category': {
                'id': -1
                }
        }
        response = self.client().post('/quizzes', json=test_quiz)
        data = json.loads(response.data)
        # check response
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        # check response body
        self.assertEqual(type(data['message']), str)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()