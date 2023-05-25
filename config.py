import os
from flask import Flask
from flask_cors import CORS
from flask_awscognito import AWSCognitoAuthentication
from dotenv import load_dotenv

app = Flask(__name__)

app.config["MYSQL_DATABASE_HOST"] = os.getenv("MYSQL_DATABASE_HOST")
app.config["MYSQL_DATABASE_PORT"] = int(os.getenv("MYSQL_DATABASE_PORT"))
app.config["MYSQL_DATABASE_USER"] = os.getenv("MYSQL_DATABASE_USER")
app.config["MYSQL_DATABASE_PASSWORD"] = os.getenv("MYSQL_DATABASE_PASSWORD")
app.config["MYSQL_DATABASE_DB"] = os.getenv("MYSQL_DATABASE_DB")

app.config["AWS_DEFAULT_REGION"] = os.getenv("AWS_DEFAULT_REGION")
app.config["AWS_COGNITO_DOMAIN"] = os.getenv("AWS_COGNITO_DOMAIN")
app.config["AWS_COGNITO_USER_POOL_ID"] = os.getenv("AWS_COGNITO_USER_POOL_ID")
app.config["AWS_COGNITO_USER_POOL_CLIENT_ID"] = os.getenv(
    "AWS_COGNITO_USER_POOL_CLIENT_ID"
)
app.config["AWS_COGNITO_USER_POOL_CLIENT_SECRET"] = os.getenv(
    "AWS_COGNITO_USER_POOL_CLIENT_SECRET"
)
app.config["AWS_COGNITO_REDIRECT_URL"] = os.getenv("AWS_COGNITO_REDIRECT_URL")

CORS(app)
aws_auth = AWSCognitoAuthentication(app)
load_dotenv()
