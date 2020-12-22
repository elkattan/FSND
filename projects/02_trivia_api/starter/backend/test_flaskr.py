import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
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
    @TODO: DONE
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_questions_pagination(self):
        """Test Questions pagination endpoint"""
        res = self.client().get('/questions?page=1')
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_question_delete(self):
        """Test deleting a Question endpoint"""
        res = self.client().get('/questions?page=1')
        data = res.get_json()
        res = self.client().delete(
            '/questions/' + str(data["questions"][0]["id"]))
        data = res.get_json()

        self.assertEqual(res.status_code, 201)
        self.assertFalse(data["error"])

    def test_question_add(self):
        """Test Adding new Question endpoint"""
        newQuestion = {
            "question": "How is the database ?",
            "answer": "Performing as expected",
            "category": 2,
            "difficulty": 4
        }

        res = self.client().post('/questions/create', json=newQuestion)
        data = res.get_json()

        self.assertEqual(res.status_code, 201)
        self.assertFalse(data["error"])

    def test_question_search(self):
        """Test Searching for a Question endpoint"""
        res = self.client().post('/questions/search',
                                 json={"searchTerm": "database"})
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]))

    def test_category_questions(self):
        """Test Grabbing Questions with category is endpoint"""
        res = self.client().get('/categories/3/questions')
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]))

    def test_quiz(self):
        """Test Quiz endpoint"""
        previous_questions = []
        quiz_category = {"id": 0}
        for r in range(5):
            res = self.client().post('/quizzes', json={
                "previous_questions": previous_questions,
                "quiz_category": quiz_category,
            })
            data = res.get_json()

            self.assertEqual(res.status_code, 200)
            self.assertTrue(len(previous_questions) ==
                            len(set(previous_questions)))
            previous_questions.append(data["question"]["id"])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
