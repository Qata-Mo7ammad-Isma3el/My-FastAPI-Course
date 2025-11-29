from src.auth.models import User
from src.auth.schemas import UserCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from src.auth.utils import generate_password_hash, verify_password


class user_service:
    async def get_user_by_email(self, email: str, session: AsyncSession) -> User | None:
        statement = select(User).where(User.email == email)
        results = await session.exec(statement)
        user = results.first()
        return user

    async def user_exists(self, email: str, session: AsyncSession) -> bool:
        user = await self.get_user_by_email(email, session)
        return True if user is not None else False

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession) -> User:
        user_data_dict = user_data.model_dump(exclude_unset=True)
        #//new_user = User.model_validate(user_data_dict)
        new_user = User(**user_data_dict)
        new_user.password_hash = generate_password_hash(user_data.password)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
