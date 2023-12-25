import os
from flask import Flask
from flask_cors import CORS
from flask_awscognito import AWSCognitoAuthentication
from flaskext.mysql import MySQL
import pymysql
from pymongo import MongoClient
from arango import ArangoClient
from dotenv import load_dotenv

active_profile = os.getenv("ACTIVE_PROFILE")
if active_profile == "prod":
    load_dotenv(dotenv_path=".env.prod", override=True)

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

CORS(app, expose_headers=["Content-Disposition"])
mysql = MySQL(app, cursorclass=pymysql.cursors.DictCursor)
mongo = MongoClient(
    username=os.getenv("MONGODB_USERNAME"), password=os.getenv("MONGODB_PASSWORD")
)
arango = ArangoClient(hosts=os.getenv("ARANGODB_HOST"))
aws_auth = AWSCognitoAuthentication(app)
