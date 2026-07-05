import sys

from sqlmodel import Session

from app.database import engine
from app.repositories import users as user_repository


def make_admin(email: str) -> int:
    with Session(engine) as session:
        user = user_repository.get_user_by_email(
            session=session,
            email=email,
        )

        if user is None:
            print(f"No user found with email: {email}")
            return 1

        user_repository.update_user_role(
            session=session,
            user=user,
            role="admin",
        )

        print(f"User promoted to admin: {user.email}")
        return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/make_admin.py user@example.com")
        raise SystemExit(1)

    email_argument = sys.argv[1]
    raise SystemExit(make_admin(email_argument))