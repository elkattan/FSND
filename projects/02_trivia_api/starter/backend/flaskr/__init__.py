import os
from flask import Flask, json, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.config['CORS_HEADERS'] = 'Content-Type'

    setup_db(app)

    '''
    @TODO: DONE Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    '''
    @TODO: DONE Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def afterRequest(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    '''
    @TODO: DONE
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route("/categories")
    def getCategories():
        return jsonify(categories={c.id: c.type for c in Category.query.all()})

    '''
  @TODO: DONE
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
    @app.route("/questions")
    def getQuestuions():
        page = int(request.args.get("page", 1))
        total_questions = Question.query.count()
        questions = [q.format() for q in Question.query.offset(
            (page - 1) * QUESTIONS_PER_PAGE).limit(QUESTIONS_PER_PAGE)]
        categories = {c.id: c.type for c in Category.query.all()}
        current_category = None
        return jsonify(
            total_questions=total_questions,
            questions=questions,
            categories=categories,
            current_category=current_category
        )

    '''
  @TODO: DONE
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route("/questions/<int:id>", methods=["DELETE"])
    def deleteQuestuions(id):
        try:
            question = Question.query.get(id)
            question.delete()
            return jsonify(error=False), 201
        except:
            return jsonify(error=True, msg="Question not found"), 404

    '''
  @TODO: DONE
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
    @app.route("/questions/create", methods=["POST"])
    def addQuestuions():
        try:
            question = request.json.get("question")
            answer = request.json.get("answer")
            category = request.json.get("category")
            difficulty = request.json.get("difficulty")
            Question(
                question=question,
                answer=answer,
                category=category,
                difficulty=difficulty,
            ).insert()
        except:
            return jsonify(error=True, msg="Failed to add question"), 400
        return jsonify(error=False), 201

    '''
  @TODO: DONE
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
    @app.route("/questions/search", methods=["POST"])
    def searchQuestuions():
        query = request.json.get("searchTerm")
        total_questions = Question.query.count()
        questions = [q.format() for q in Question.query.filter(
            Question.question.ilike(f"%{query}%"))]
        current_category = None
        return jsonify(
            total_questions=total_questions,
            questions=questions,
            current_category=current_category
        )

    '''
  @TODO: DONE
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
    @app.route("/categories/<int:id>/questions")
    def getQuestuionsOfCategory(id):
        total_questions = Question.query.count()
        questions = [q.format()
                     for q in Question.query.filter(Question.category == id)]
        current_category = None
        return jsonify(
            total_questions=total_questions,
            questions=questions,
            current_category=current_category
        )

    '''
  @TODO: DONE
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
    @app.route("/quizzes", methods=["POST"])
    def getQuizQuestuion():
        question = None
        previous_questions = request.json.get("previous_questions", [])
        quiz_category = int(request.json.get("quiz_category", {"id": 0})["id"])
        questions = Question.query
        if quiz_category > 0:
            questions = questions.filter(Question.category == quiz_category)
        questions = questions.filter(
            Question.category.notin_(previous_questions)).all()
        if questions:
            question = random.choice(questions)
        return jsonify(question=question.format())

    '''
  @TODO: DONE
  Create error handlers for all expected errors
  including 404 and 422 (Why 422 ?).
  '''

    @ app.errorhandler(400)
    def invalid(err):
        return jsonify(code=400, error=True, msg="Invalid Data"), 400

    @ app.errorhandler(401)
    def unauthorized(err):
        return jsonify(code=401, error=True, msg="Unauthorized request"), 401

    @ app.errorhandler(404)
    def page_not_found(err):
        return jsonify(code=404, error=True, msg="Page Not Found"), 404

    @ app.errorhandler(405)
    def page_not_found(err):
        return jsonify(code=405, error=True, msg="Method Not Allowed"), 405

    @ app.errorhandler(422)
    def unprocessable(err):
        return jsonify(code=422, error=True, msg="Unprocessable Entity"), 422

    @ app.errorhandler(500)
    def unprocessable(err):
        return jsonify(code=500, error=True, msg="Something went wrong !"), 500

    return app
