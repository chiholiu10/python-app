import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def get_db_pool():
    return await asyncpg.create_pool(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'book_api_dev'),
        user=os.getenv('DB_USER', 'api_user'),
        password=os.getenv('DB_PASSWORD', 'secure_password'),
        min_size=1,
        max_size=10
    )

db_pool = None

async def init_db():
    global db_pool
    db_pool = await get_db_pool()
    
    async with db_pool.acquire() as conn:
        exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'books'
            )
        """)
        
        if not exists:
            print("📚 Boeken tabel wordt aangemaakt...")
            await conn.execute("""
                CREATE TABLE books (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    author VARCHAR(100) NOT NULL,
                    year INTEGER NOT NULL CHECK (year >= 1450 AND year <= 2100),
                    isbn VARCHAR(13) UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await conn.execute("""
                INSERT INTO books (title, author, year, isbn) VALUES
                ('De Hobbit', 'J.R.R. Tolkien', 1937, '9789027468476'),
                ('1984', 'George Orwell', 1949, '9789046706808'),
                ('De Alchemist', 'Paulo Coelho', 1988, '9789044626119')
            """)
            print("✅ Voorbeeld boeken toegevoegd!")
        
        count = await conn.fetchval("SELECT COUNT(*) FROM books")
        print(f"📖 {count} boeken in database")

async def execute_query(query, *args, fetch_one=False, fetch_all=False):
    async with db_pool.acquire() as conn:
        if fetch_one:
            return await conn.fetchrow(query, *args)
        elif fetch_all:
            return await conn.fetch(query, *args)
        else:
            return await conn.execute(query, *args)

def book_from_row(row):
    if not row:
        return None
    return Book(
        id=row['id'],
        title=row['title'],
        author=row['author'],
        year=row['year'],
        isbn=row.get('isbn'),
        created_at=row['created_at'],
        updated_at=row['updated_at']
    )