import os
from dotenv import load_dotenv

load_dotenv()

class Config:
  # Database
  DB_HOST = os.getenv('DB_HOST', 'localhost')
  DB_PORT = os.getenv('DB_PORT', '5432')
  DB_NAME = os.getenv('DB_NAME', 'book_api_dev')
  DB_USER = os.getenv('DB_USER', 'api_user')
  DB_PASSWORD = os.getenv('DB_PASSWORD', 'secure_password')
  
  # Flask
  SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
  DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'
  
  @property
  def DATABASE_URL(self):
      return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

config = Config()