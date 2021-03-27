# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

APP_ROOT = os.path.join(os.path.dirname(__file__), '.')  
dotenv_path = os.path.join(APP_ROOT, '../docker/dev.env')
load_dotenv(dotenv_path)
print( os.getenv('IS_LOADED') + ", .env file path: " + dotenv_path )

PORT=os.environ.get('PORT', os.getenv('PORT'))
LOG_LEVEL=os.environ.get('LOG_LEVEL', os.getenv('LOG_LEVEL'))
LOG_FOLDER_PATH=os.environ.get('LOG_FOLDER_PATH', os.getenv('LOG_FOLDER_PATH'))

DB_HOST=os.environ.get('DB_HOST', os.getenv('DB_HOST'))
DB_PORT=os.environ.get('DB_PORT', os.getenv('DB_PORT'))
DB_ACCOUNT=os.environ.get('DB_ACCOUNT', os.getenv('DB_ACCOUNT')).replace("'", "")
DB_PASSWORD=os.environ.get('DB_PASSWORD', os.getenv('DB_PASSWORD')).replace("'", "")
