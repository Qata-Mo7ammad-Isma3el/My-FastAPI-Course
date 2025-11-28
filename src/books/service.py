# in this file were going to put the service functions for the books app 
#! any async function you have to call it using await thats not optional
#! every thing starts with async must be used with await
from sqlmodel.ext.asyncio.session import AsyncSession 
from .schemas import BookCreateModel, BookUpdateModel
from sqlmodel import select, desc
from .models import Book
from typing import Optional # Recommended for better type hinting
from datetime import datetime
from uuid import UUID
class BookService:
    async def get_all_books(self, session: AsyncSession) -> list[Book]:
        statement = select(Book).order_by(desc(Book.created_at))
        results = await session.exec(statement)
        return results.all()
    
    #> ... get_book (No change, but added Optional return hint)
    async def get_book(self, book_uid:UUID, session: AsyncSession) -> Optional[Book]:
        statement = select(Book).where(Book.uid == book_uid)
        results = await session.exec(statement)
        book = results.first()
        return book # Returns Book or None
    
    #> ... create_book (Improved refresh call)
    async def create_book(self, book_data:BookCreateModel, session: AsyncSession) -> Book:
        book_data_dict = book_data.model_dump()
        #// new_book = Book.model_validate(book_data_dict)
        new_book = Book(**book_data_dict)
        new_book.published_date = datetime.strptime(str(book_data.published_date), "%Y-%m-%d").date()
        session.add(new_book) #> you dont have to use await with this because it's done in python memory 
        await session.commit()
        await session.refresh(new_book) # <--- Added object to refresh
        return new_book
    
    #> ... update_book (CRITICAL fixes: await, items(), commit/refresh loop)
    async def update_book(self, book_uid:UUID, update_data:BookUpdateModel, session: AsyncSession) -> Optional[Book]:
        book_to_update = await self.get_book(book_uid, session=session) #! <--- ADDED AWAIT
        if book_to_update is not None:
            #! Use exclude_unset=True to only update provided fields
            book_update_dict = update_data.model_dump(exclude_unset=True) 
            
            for k, v in book_update_dict.items(): #> <--- ADDED PARENTHESES ()
                setattr(book_to_update, k, v)
                
            #> Commit and refresh MUST be outside the loop 
            #> and refresh should be on the object
            await session.commit()
            await session.refresh(book_to_update)
            return book_to_update
        return None

    #> ... delete_book (CRITICAL fix: await, and removed unnecessary refresh)
    async def delete_book(self, book_uid:UUID, session: AsyncSession) -> Optional[Book]:
        book_to_delete = await self.get_book(book_uid, session=session) #! <--- ADDED AWAIT
        if book_to_delete is not None:
            await session.delete(book_to_delete)
            await session.commit()
            #// Removed unnecessary await session.refresh()
            return book_to_delete #> Typically returns the deleted object or a status
        return None

