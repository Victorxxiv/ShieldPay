# Import necessary modules
from sqlalchemy.orm import sessionmaker
from models.basemodel import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from os import getenv
from dotenv import load_dotenv
from models.basemodel import Base
from urllib.parse import quote_plus
import logging

# Load the environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a DB class
class DB:
    """
    DB class
    """

    __engine = None
    __session = None

    def __init__(self):
        """
        Constructor
        """

        user = getenv('PG_USER')
        password = getenv('PG_PWD')
        host = getenv('PG_HOST')
        port = getenv('PG_PORT', '5432') 
        db_name = getenv('PG_DB')
        env = getenv('APP_ENV')
        # Check if any required environment variable is missing
        if not all([user, password, host, db_name]):
            logger.error("Missing environment variables.")
            raise ValueError("Required environment variables are not set.")

        # URL encode the password if necessary
        password = quote_plus(password)

        try:
            # Create the engine with URL-encoded password
            self.__engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db_name}')
            self.reload()

            if env == 'test':
                Base.metadata.drop_all(self.__engine)
        except SQLAlchemyError as e:
            logger.error(f"Error initializing database engine: {e}")
            raise e


    def reload(self):
        """
        Reload
        """
        # Create all tables
        Base.metadata.create_all(self.__engine)
        # Create a session maker
        session_maker = sessionmaker(bind=self.__engine, expire_on_commit=False)
        # Create a scoped session
        self.__session = scoped_session(session_maker)



    def add(self, obj):
        """
        Add
        """
        # Add the object to the session
        self.__session.add(obj)

    def save(self):
        """
        Save
        """
        # Commit the session to save changes
        self.__session.commit()

    def delete(self, obj=None):
        """
        Delete
        """
        if obj:
            # Delete the object from the session
            self.__session.delete(obj)

    def query(self, cls):
        """
        Query
        """
        # Perform a query on the session
        return self.__session.query(cls)

    def close(self):
        """calls remove() method on the private session attr to close the session and stop using it"""
        # Close the session
        self.__session.remove()

    def begin(self):
        """calls begin() method on the private session attr to start a transaction"""
        # Begin a transaction
        self.__session.begin()

    def rollback(self):
        """calls rollback() method on the private session attr to roll back a transaction"""
        # Roll back a transaction
        self.__session.rollback()
