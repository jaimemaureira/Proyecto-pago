import os
from dotenv import load_dotenv


load_dotenv()


class Config: 
       
	SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
	SQLALCHEMY_TRACK_MODIFICATIONS = False	
 	
	SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

	SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", "pwd-reset-salt")


