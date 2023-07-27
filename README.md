# Installation

1. install latest version of docker and run it
2. open a terminal and cd in the directory you want the project to be in
3. run `git clone https://github.com/noel-ellis/bug-tracker`
4. run `cd bug-tracker` to open the root directory of the project
5. create .env file and fill it with:
   - required for the project to work at all; generate your own secure key:
     - SECRET_KEY=(your secret key)
   - required for oauth2:
     - ALGORITHM=(algorithm of your choosing, HS256 for example)
     - ACCESS_TOKEN_EXPIRE_MINUTES=(amount of minutes user will be logged in)
   - required for the db:
     - DATABASE_PASSWORD=(password, any)
     - DATABASE_NAME=(name, any)
     - DATABASE_HOSTNAME=bugtracker_db
     - DATABASE_PORT=(port, any available)
     - DATABASE_USERNAME=(username, any)

## Running the App
* use `docker-compose up` to run with logs appearing in the console
* use `docker-compose up -d` to run in the background
* use `docker-compose down` to shut down the app

## Troubleshooting
- If for some reason server can't find any tables in the database, you'll need to create them:
    - run `docker exec -it bug-tracker-api-1 bash` to open the terminal inside the api container
    - from it, run `alembic upgrade head` to apply database migrations
