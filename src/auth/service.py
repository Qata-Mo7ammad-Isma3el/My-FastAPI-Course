from src.db.models import User
from src.auth.schemas import UserCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from src.auth.utils import generate_password_hash, verify_password


class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession) -> User | None:
        statement = select(User).where(User.email == email)
        results = await session.exec(statement)
        user = results.first()
        return user

    async def user_exists(self, email: str, session: AsyncSession) -> bool:
        user = await self.get_user_by_email(email, session)
        return True if user is not None else False

    async def create_user(
        self, user_data: UserCreateModel, session: AsyncSession
    ) -> User:
        user_data_dict = user_data.model_dump(exclude_unset=True)
        # Add password_hash before creating the User object
        user_data_dict["password_hash"] = generate_password_hash(user_data.password)
        user_data_dict["role"] = "user"

        new_user = User.model_validate(user_data_dict)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

    async def update_user(self, user: User, session: AsyncSession) -> User:
        for key, value in user.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
