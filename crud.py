import asyncio

from sqlalchemy import select
from sqlalchemy.engine.result import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.models import db_helper, Post, User, Profile


async def create_user(session: AsyncSession, username: str) -> User:
    user = User(username=username)
    session.add(user)
    await session.commit()
    print("user", user)
    return user


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    result: Result = await session.execute(stmt)
    user: User | None = result.scalar_one_or_none()
    print(f"found user", username, user)
    return user


async def create_user_profile(
    session: AsyncSession,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
) -> Profile:
    profile = Profile(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
    )
    session.add(profile)
    await session.commit()
    return profile


async def show_users_with_profiles(session: AsyncSession) -> list["User"]:
    stmt = select(User).options(joinedload(User.profile)).order_by(User.id)
    users = await session.scalars(stmt)
    for user in users:
        print(user)
        if user.profile.last_name == None:
            print(user.profile.first_name)
        else:
            print(user.profile.first_name, user.profile.last_name)


async def create_users_posts(
    session: AsyncSession,
    user_id: int,
    *post_titles: str,
) -> list[Post]:
    posts = [Post(title=title, user_id=user_id) for title in post_titles]
    session.add_all(posts)
    await session.commit()
    print(posts)
    return posts


async def get_users_with_posts(session: AsyncSession):
    stmt = select(User).options(joinedload(User.posts)).order_by(User.id)
    users = await session.scalars(stmt)

    for user in users.unique():
        print("**" * 10)
        print(user)
        for post in user.posts:
            print("-", post)


async def get_posts_with_users(session: AsyncSession):
    stmt = select(Post).options(joinedload(Post.user)).order_by(Post.id)
    posts = await session.scalars(stmt)

    for post in posts:
        print("post", post)
        print("author", post.user)


# вложенные джоины будут тут
async def get_profiles_with_users_and_get_users_with_posts(session: AsyncSession):
    stmt = (
        select(Profile)
        .options(joinedload(Profile.user).selectinload(User.posts))
        .order_by(Profile.id)
    )
    profiles = await session.scalars(stmt)

    for profile in profiles:
        print(profile.first_name, profile.user, f"user_id={profile.user_id}")
        print(profile.user.posts)


async def main():
    async with db_helper.session_factory() as session:
        #        await create_user(session=session, username="matt")
        #        user_matt = await get_user_by_username(session=session, username="matt")
        #        await get_user_by_username(session=session, username="alex")
        # user_john = await get_user_by_username(session=session, username="john")
        #        await create_user_profile(
        #            session=session,
        #            user_id=user_matt.id,
        #            first_name="Matt",
        #        )
        # await create_user_profile(
        #    session=session,
        #    user_id=user_john.id,
        #    first_name="John",
        #    last_name="Black",
        # )
        #   await show_users_with_profiles(session=session)
        # await create_users_posts(
        #    session, user_john.id, "New post by John", "Second post by John"
        # )
        # await get_users_with_posts(session=session)
        # await get_posts_with_users(session=session)
        await get_profiles_with_users_and_get_users_with_posts(session=session)


if __name__ == "__main__":
    asyncio.run(main())
