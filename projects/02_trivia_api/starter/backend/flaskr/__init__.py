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
    app.config.from_object('config')
    # Setting up database
    setup_db(app)
    # Setting up cors
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def afterRequest(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    '''
    Grab all available categories.
    '''
    @app.route("/categories")
    def getCategories():
        return jsonify(categories={c.id: c.type for c in Category.query.all()})

    '''
    Grabbing all questions chuncked to pages according to `QUESTIONS_PER_PAGE`
    '''
    @app.route("/questions")
    def getQuestuions():
        page = request.args.get("page", 1, type=int)
        questions = Question.query.order_by(Question.id).paginate(
            page, QUESTIONS_PER_PAGE, error_out=False)
        total_questions = questions.total
        questions = [q.format() for q in questions.items]
        categories = {c.id: c.type for c in Category.query.all()}
        current_category = None
        return jsonify(
            total_questions=total_questions,
            questions=questions,
            categories=categories,
            current_category=current_category
        )

    @app.route("/questions/<int:id>", methods=["DELETE"])
    def deleteQuestuions(id):
        try:
            question = Question.query.get(id)
            question.delete()
            return jsonify(error=False), 201
        except BaseException:
            return jsonify(error=True, msg="Question not found"), 404

    @app.route("/questions/create", methods=["POST"])
    def addQuestuions():
        try:
            question = request.json.get("question")
            answer = request.json.get("answer")
            category = int(request.json.get("category"))
            difficulty = int(request.json.get("difficulty"))
            assert isinstance(question, str) and len(question) > 5
            assert isinstance(answer, str) and len(answer) > 1
            assert isinstance(category, int)
            assert isinstance(difficulty, int)
            Question(
                question=question,
                answer=answer,
                category=category,
                difficulty=difficulty,
            ).insert()
        except BaseException:
            return jsonify(error=True, msg="Failed to add question"), 400
        return jsonify(error=False), 201

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

    @app.route("/categories/<int:id>/questions")
    def getQuestuionsOfCategory(id):
        total_questions = Question.query.count()
        questions = [
            q.format() for q in Question.query.filter(
                Question.category == id).all()]
        current_category = None
        return jsonify(
            total_questions=total_questions,
            questions=questions,
            current_category=current_category
        )

    @app.route("/quizzes", methods=["POST"])
    def getQuizQuestuion():
        question = None
        previous_questions = request.json.get("previous_questions", [])
        quiz_category = int(request.json.get("quiz_category", {"id": 0})["id"])
        questions = Question.query
        if quiz_category > 0:
            questions = questions.filter(Question.category == quiz_category)

        questions = list(map(lambda q: q.format(), questions.filter(
            Question.id.notin_(previous_questions)).all()))
        if questions:
            question = random.choice(questions)
        return jsonify(question=question)

    # Error handling
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
    def method_not_allowed(err):
        return jsonify(code=405, error=True, msg="Method Not Allowed"), 405

    @ app.errorhandler(422)
    def unprocessable(err):
        return jsonify(code=422, error=True, msg="Unprocessable Entity"), 422

    @ app.errorhandler(500)
    def unexpected(err):
        return jsonify(code=500, error=True, msg="Something went wrong !"), 500

    return app
