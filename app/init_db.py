from app.database import engine
from app.models import Base

# Create all tables in the database
Base.metadata.create_all(bind=engine)

# Print the list of tables
print("Tables created:")
for table_name in Base.metadata.tables.keys():
    print(f"- {table_name}")


print("Database initialized and tables created.")