# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

REVIEW_COMMENT

## Endpoints
```
GET '/questions'
GET '/categories'
GET '/categories/{id}/questions'
POST '/questions/create'
POST '/questions/search'
POST '/quizzes'
DELETE '/questions/{id}'
```

### GET '/questions'
- Fetches a dictionary that contains list of questions of specified page, object of category id as keys and type as values, total questions and current category
- Request Arguments: page as an integer that specifies the required page
- Returns: An object with questions: `List<Question>`, categories: `Object<Int, String>`, total_questions: `Int`, current_category: `Category`

```
{
    "categories": Object { 1: "Science", 2: "Art", 3: "Geography", … },
    "current_category": null,
    "questions": [ <Question>, <Question>,... ],
    "total_questions": 18
}
```

### GET '/categories'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs. 

```
{
    "1" : "Science",
    "2" : "Art",
    "3" : "Geography",
    "4" : "History",
    "5" : "Entertainment",
    "6" : "Sports"
}
```

### GET '/categories/{id}/questions'
- Fetches a dictionary that contains list of questions related to specified category in URL parameter `id`, total questions and current category
- Request Arguments: None
- Returns: An object with questions: `List<Question>`, total_questions: `Int`, current_category: `Category`

```
{
    "current_category": null
    "questions": [ <Question>, <Question>,... ]
    "total_questions": 17
}
```

### POST '/questions/create'
- Takes question, answer, category and difficulty to craete a new question record
- Request Arguments: None
- Request Body: question: `String`, answer: `String`, category: `Int` (valid category ID), difficulty: `Int`
- Returns: A Boolean that indicates that request failed or not (error: `Bool`) and a message (msg: `String`) that specify the error reason if occured

```
{
    "error": true,
    "msg": "Reason Text"

}
```

### POST '/questions/search'
- Takes searchTerm to fetch questions including that search term
- Request Arguments: None
- Request Body: searchTerm: `String`
- Returns: An object with questions: `List<Question>`, total_questions: `Int`, current_category: `Category`

```
{
    "current_category": null,
    "questions": [ <Question>, <Question>,... ],
    "total_questions": 18
}
```

### POST '/quizzes'
- Takes previous questions list and quiz category selected and return new random question from that category
- Request Arguments: None
- Request Body: previous_questions: `List<Int>` (category IDs), quiz_category: `Int` (valid category ID)
- Returns: An object of new random question: Question

```
{
    "question": Question
}
```

### DELETE '/questions/{id}'
- Deleted a question using the question ID specified in URL parameter `id`
- Request Arguments: None
- Request Body: None
- Returns: A Boolean that indicates that request failed or not (error: `Bool`) and a message (msg: `String`) that specify the error reason if occured

```
{
    "error": false
}
```

## Model Refrence

### `Question`

```
{
    "id": Int,
    "question: "String",
    "answer: "String",
    "category: "String",
    "difficulty: Int
}
```

### `Category`

```
{
    "id": Int,
    "type": "String"
}
```


## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```