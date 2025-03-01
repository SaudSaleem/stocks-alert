Create a virtual environment:
python -m venv venv

Activate the virtual environment:
source venv/bin/activate

Install dependencies:
pip install -r requirements.txt

Create the database tables:
python -m app.init_db

Run the FastAPI application:
uvicorn app.main:app --reload

api test:
python -m app.test_api

run scrapper:
python -m app.psx_scrapper

run scheduler:
python -m app.tasks

Delete andRecreate the Database
rm ./stocks_alert.db
python -m app.init_db

truncate db:
python -m app.truncate_db