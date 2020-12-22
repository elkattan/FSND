import os
import unittest
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        os.environ["DATABASE_NAME"] = "trivia_test"
        self.app = create_app()
        self.client = self.app.test_client
        setup_db(self.app)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    # Success scenarios

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
        """Test Grabbing Questions of a category endpoint"""
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

    # Failed scenarios

    def test_question_create_error(self):
        """Test Adding new Question error endpoint"""
        newQuestion = {
            "answer": "BAD request: No question",
            "category": 3,
            "difficulty": 2
        }

        res = self.client().post('/questions/create', json=newQuestion)
        data = res.get_json()

        self.assertEqual(res.status_code, 400)
        self.assertTrue(data["error"])

    def test_question_delete_error(self):
        """Test deleting a Question error endpoint"""
        res = self.client().delete('/questions/999')
        data = res.get_json()

        self.assertEqual(res.status_code, 404)
        self.assertTrue(data["error"])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
