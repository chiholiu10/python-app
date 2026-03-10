from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
from datetime import datetime
from contextlib import asynccontextmanager

from models import Book, BookCreate, BookUpdate
from database import init_db, execute_query, book_from_row, db_pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("FastAPI app stated with database connection")
    yield
    # Shutdown: close database pool
    if db_pool:
        await db_pool.close()
        print("Database connectie closed")

app = FastAPI(
    title="Books API",
    description="""
    ## Books API
    This API gives you access to book collection.
    """,
    version="1.0.0",
    contact={
        "name": "Chiho",
        "email": "chiholiu10@gmail.com",
    },
    lifespan=lifespan
)

@app.get("/", tags=["Root"])
async def home():
    """Welkom bij de Books API"""
    return {
        "name": "Books API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "GET /api/books": "Alle boeken (met paginatie)",
            "GET /api/books/{id}": "Specifiek boek",
            "POST /api/books": "Nieuw boek toevoegen",
            "PUT /api/books/{id}": "Boek updaten",
            "DELETE /api/books/{id}": "Boek verwijderen",
            "GET /api/books/search": "Zoeken in boeken"
        }
    }

@app.get("/api/books", response_model=dict, tags=["Boeken"])
async def get_books(
    page: int = Query(1, ge=1, description="Pagina nummer"),
    limit: int = Query(10, ge=1, le=100, description="Items per pagina")
):
    """
    📖 **Alle boeken ophalen**
    
    Parameters:
    - **page**: Welke pagina (start bij 1)
    - **limit**: Hoeveel boeken per pagina (max 100)
    
    Returns:
    - **data**: Lijst van boeken
    - **pagination**: Metadata voor navigatie
    """
    offset = (page - 1) * limit
    
    # Totaal aantal boeken
    total = await execute_query("SELECT COUNT(*) as count FROM books", fetch_one=True)
    total_count = total['count'] if total else 0
    
    # Boeken voor deze pagina
    rows = await execute_query(
        "SELECT * FROM books ORDER BY created_at DESC LIMIT $1 OFFSET $2",
        limit, offset,
        fetch_all=True
    )
    
    books = [book_from_row(row).dict() for row in rows]
    
    return {
        "success": True,
        "data": books,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total_count,
            "pages": (total_count + limit - 1) // limit
        }
    }

@app.get("/api/books/{book_id}", response_model=dict, tags=["Boeken"])
async def get_book(book_id: int):
    """
    🔍 **Specifiek boek ophalen op ID**
    
    Parameters:
    - **book_id**: Het ID van het boek
    
    Returns:
    - **data**: Het gevraagde boek
    """
    row = await execute_query(
        "SELECT * FROM books WHERE id = $1",
        book_id,
        fetch_one=True
    )
    
    if not row:
        raise HTTPException(status_code=404, detail="Book not found")
    
    book = book_from_row(row)
    return {
        "success": True,
        "data": book.dict()
    }

@app.post("/api/books", response_model=dict, status_code=201, tags=["Boeken"])
async def create_book(book: BookCreate):
    """
    ➕ **Nieuw boek toevoegen**
    
    Request body:
    - **title**: Titel (verplicht)
    - **author**: Auteur (verplicht)
    - **year**: Jaartal (tussen 1450-2100)
    - **isbn**: ISBN nummer (optioneel, uniek)
    
    Returns:
    - **data**: Het aangemaakte boek
    - **message**: Bevestiging
    """
    try:
        row = await execute_query("""
            INSERT INTO books (title, author, year, isbn)
            VALUES ($1, $2, $3, $4)
            RETURNING id, title, author, year, isbn, created_at
        """, book.title, book.author, book.year, book.isbn, fetch_one=True)
        
        return {
            "success": True,
            "data": dict(row),
            "message": "Book created successfully"
        }
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=400, detail="ISBN already exists")

@app.put("/api/books/{book_id}", response_model=dict, tags=["Boeken"])
async def update_book(book_id: int, book_update: BookUpdate):
    existing = await execute_query(
        "SELECT id FROM books WHERE id = $1",
        book_id,
        fetch_one=True
    )
    
    if not existing:
        raise HTTPException(status_code=404, detail="Book not found")
    
    update_fields = []
    values = []
    param_index = 1
    
    update_data = book_update.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    for field, value in update_data.items():
        update_fields.append(f"{field} = ${param_index}")
        values.append(value)
        param_index += 1
    
    values.append(book_id)
    
    row = await execute_query(f"""
        UPDATE books 
        SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = ${param_index}
        RETURNING id, title, author, year, isbn, created_at, updated_at
    """, *values, fetch_one=True)
    
    return {
        "success": True,
        "data": dict(row),
        "message": "Book updated successfully"
    }

@app.delete("/api/books/{book_id}", response_model=dict, tags=["Boeken"])
async def delete_book(book_id: int):
    result = await execute_query(
        "DELETE FROM books WHERE id = $1 RETURNING id",
        book_id,
        fetch_one=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return {
        "success": True,
        "message": "Book deleted successfully"
    }

@app.get("/api/books/search", response_model=dict, tags=["Boeken"])
async def search_books(
    q: str = Query(..., min_length=2, description="Zoekterm (minimaal 2 karakters)")
):
    rows = await execute_query("""
        SELECT * FROM books 
        WHERE title ILIKE $1 OR author ILIKE $1
        ORDER BY 
            CASE 
                WHEN title ILIKE $1 THEN 1
                WHEN author ILIKE $1 THEN 2
                ELSE 3
            END
    """, f'%{q}%', fetch_all=True)
    
    books = [book_from_row(row).dict() for row in rows]
    
    return {
        "success": True,
        "data": books,
        "query": q,
        "count": len(books)
    }

@app.get("/health", tags=["System"])
async def health_check():
    try:
        await execute_query("SELECT 1", fetch_one=True)
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")