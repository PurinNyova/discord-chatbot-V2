from sqlalchemy import create_engine, Column, String, JSON, ARRAY, Integer, VARCHAR, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

# Create a Base class for defining your ORM models
Base = declarative_base()

# Database setup (change this URL to match your database setup)
DATABASE_URL = "sqlite:///main.db"  # Example for SQLite, change to your DB URL
engine = create_engine(DATABASE_URL)

# Create a sessionmaker
Session = sessionmaker(bind=engine)

# Define the Cache model class
class Cache(Base): 
    __tablename__="userMessageCache"
    origin = Column(Integer, primary_key=True)
    activeSessions = Column(String, nullable=True)
    globalChatTask = Column(String, nullable=True)
    activeModel = Column(VARCHAR(1), nullable=True)
    requireReply = Column(Boolean, nullable=False)

class Persona(Base):
    __tablename__="personalities"
    id = Column(Integer, primary_key=True)
    origin = Column(Integer)
    name = Column(String)
    profilePicture = Column(String)
    personality = Column(String)

# Create the table in the database if it doesn't exist (useful for testing)
# Base.metadata.create_all(engine)

# Function to query and print records from the Cache table
def read_cache_data():
    # Create a session to interact with the database
    session = Session()

    try:
        # Query all records from the Cache table
        cache_records = session.query(Cache).all()  # .all() returns a list of all rows
        cache_records2 = session.query(Persona).all()

        # Iterate over the records and print them
        if cache_records:
            for record in cache_records:
                print(f"Origin: {record.origin}")
                print(f"Active Sessions: {record.activeSessions}")
                print(f"Global Chat Task: {record.globalChatTask}")
                print(f"Active Model: {record.activeModel}")
                print(f"requireReply: {record.requireReply}")
                print("=" * 40)  # Separator for better readability
        else:
            print("No records found in the Cache table.")
        if cache_records2:
            for persona in cache_records2:
                print(f"Origin: {persona.origin}")
                print(f"Name: {persona.name}")
                print(f"PFP Link: {persona.profilePicture}")
                print(f"Personality: {persona.personality}")
                print("="*40)
        else:
            print("No records found in Persona table")

    except SQLAlchemyError as e:
        print(f"Error querying the database: {str(e)}")
    
    finally:
        # Close the session
        session.close()

# Main code execution
if __name__ == "__main__":
    read_cache_data()
