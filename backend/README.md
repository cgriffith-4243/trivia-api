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

## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

## API Reference

### Getting Started
- Base URL: The backend is hosted at http://127.0.0.1:5000/

### Errors

The API will return the following errors:

#### 400 Bad request
- Sending invalid JSON will result in a ```400 Bad Request``` response.

    ```
    {
        "success": False,
        "error": 400,
        "message": "Bad request"
    }
    ```

#### 404 Resource not found
- Failure for the server to find the requested url will result in a ```404 Resource Not Found``` response.

    ```
    {
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }
    ```

#### 422 Unprocessable
- Sending invalid fields will result in a ```422 Unprocessable Entity``` response.

    ```
    {
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }
    ```

#### 500 Internal server error 
- Unexpected errors preventing the fullfillment of the request will result in a ```500 Internal Server Error ``` response.

    ```
    {
        "success": False,
        "error": 500,
        "message": "Internal server error"
    }
    ```

### Endpoints

#### GET /categories
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: Response body containing the following key
    '''categories''': A dictionary containing key:value pairs of Category id:Category Type 

```
{
    "categories": {
        "1": "Science", 
        "2": "Art", 
        "3": "Geography", 
        "4": "History", 
        "5": "Entertainment", 
        "6": "Sports"
    }, 
    "success": true
}
```

#### GET /questions?page=1
- Fetches a list of paginated questions, number value indicating total number of questions found, dictionary of categories, and number value indicating Category id of the current category
- Request Arguments: Optional URL query containing the following
    '''page''': A value indicating page number for pagination
- Returns: Response body containing the following keys
    '''questions''': A list containing JSON objects of questions found by the request, restricted to the current page number and limit
    '''total_questions''': A value indicating total number of questions found by the current request
    '''categories''': A dictionary containing key:value pairs of Category id:Category Type
    '''current_category''': A value indicating current Category id. For this url it is always None

```
{
    "questions": [{
        "id": 5,
        "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?",
        "answer": "Maya Angelou",
        "category": 4,
        "difficulty": 2
    }],
    "total_questions": 1,
    "categories": {
        "1": "Science", 
        "2": "Art", 
        "3": "Geography", 
        "4": "History", 
        "5": "Entertainment", 
        "6": "Sports"
    },
    'current_category': None
}
```

#### DELETE /questions/<int:question_id>
- Deletes a question with an id matching the url argument
- Request Arguments: 
    '''question_id''': A number value indicating the Question id of the entry to be deleted
- Returns: Response body containing the following key
    '''deleted''': A number value indicating the Question id of the entry to be deleted

```
{
    "deleted": 3
}
```

#### POST /questions
- Creates and adds a question to the database
- Request Arguments: 
    '''question''': A string value containing the entry question
    '''answer''': A string value containing the answer to the entry question
    '''difficulty''': A number value indicating the difficulty of the entry question
    '''category''': A number value indicating the Category id of the entry question

```
{
  "question": {
    "question": "Hematology is a branch of medicine involving the study of what?",
    "answer": "Blood",
    "category": 1,
    "difficulty": 4
  }
}
```

- Returns: Response body containing the following key
    '''message''': A string indicating the request was handled successfully and the entry was added to the database

```
{
    "message": "Question was successfully created"
}
```

#### POST /questions/search
- Fetches a list of paginated questions with a matching string for the search term, number value indicating total number of questions found, and number value indicating Category id of the current category
- Request Arguments: 
    '''searchTerm''': A string value to be matched with Question entries

```
{
    "searchTerm": "What is"
}
```

- Returns: Response body containing the following keys
    '''questions''': A list containing JSON objects of questions found by the request, restricted to the current page number and limit
    '''total_questions''': A value indicating total number of questions found by the current request
    '''current_category''': A value indicating current Category id. For this url it is always None

```
{
    "questions": [{
        "id": 5,
        "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?",
        "answer": "Maya Angelou",
        "category": 4,
        "difficulty": 2
    }],
    "total_questions": 1,
    'current_category': None
}
```

#### GET /categories/<int:category_id>/questions
- Fetches a list of paginated questions for the requested category, number value indicating total number of questions found, and number value indicating Category id of the current category
- Request Arguments: 
    '''category_id''': A number value indicating the Category id to match

```
{
    "category_id": 2
}
```

- Returns: Response body containing the following keys
    '''questions''': A list containing JSON objects of questions found by the request, restricted to the current page number and limit
    '''total_questions''': A value indicating total number of questions found by the current request
    '''current_category''': A value indicating current Category id

```
{
    "questions": [{
        "id": 5,
        "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?",
        "answer": "Maya Angelou",
        "category": 4,
        "difficulty": 2
    }],
    "total_questions": 1,
    'current_category': 2
}
```

#### POST /quizzes
- Fetches a random question from the database for the current category, such that the question entry had not been retrieved before
- Request Arguments: 
    '''previous_questions''': A list of Question id indicating which questions had been previously retrieved
    '''quiz_category''': A value indicating the Category id of the quiz

```
{
    "previous_questions": [5, 9],
    "quiz_category": 4,
}
```

- Returns: Response body containing the following key
    '''question''': A dictionary containing all values of the selected question entry

```
{
  "question": {
    "id": 12,
    "question": "Who invented Peanut Butter?",
    "answer": "George Washington Carver",
    "category": 4,
    "difficulty": 2
  }
}
```