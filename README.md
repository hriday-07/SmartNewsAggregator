# Download the repository

cd SmartNewsAgrregator

# Set up Python virtual environment

python -m venv venv
source venv/bin/activate # On Windows use `venv\Scripts\activate`

# Install dependencies

pip install -r requirements.txt

# Start PostgreSQL (if not running)

# Ubuntu:

sudo service postgresql start

# macOS:

brew services start postgresql

# Create PostgreSQL database and user

sudo -u postgres psql -c "CREATE DATABASE ir_project;"
sudo -u postgres psql -c "CREATE USER smartnews_user WITH PASSWORD 'random_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ir_project TO smartnews_user;"

# (Optional) Install pgvector from source if not already installed

git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
cd ..

# Enable pgvector extension

psql -U myuser -d mydb -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Run Django migrations

# Manually create a migration to enable the pgvector extension

python manage.py makemigrations news --empty --name enable_pgvector_extension

# Now open the generated migration file in news/migrations/

# and add the following operation at the top of the `operations` list:

# from django.db import migrations

# class Migration(migrations.Migration):

# dependencies = [...]

#

# operations = [

# migrations.RunSQL("CREATE EXTENSION IF NOT EXISTS vector"),

# ...

# ]

python manage.py makemigrations
python manage.py migrate

# Upload data

python manage.py loaddata dumped_data.json

# Run the development server

python manage.py runserver

# App will be live at: http://127.0.0.1:8000/
