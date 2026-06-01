from fastapi import APIRouter, HTTPException
from api.deps import get_db, db_dependency, user_dependency, bcrypt_context
from starlette import status
from api.schemas import UserVerification, UserResponse
from db.models import Users


router = APIRouter(
    prefix="/user",
    tags = ["user"]
)


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user(user: user_dependency,
                   db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not found.")

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not found in database.")

    return user_model


@router.put("/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency,
                          db: db_dependency,
                          user_ver: UserVerification):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not found.")

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not found in database.")

    if not bcrypt_context.verify(user_ver.password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password doesn't match.")

    user_model.hashed_password = bcrypt_context.hash(user_ver.new_password)

    db.add(user_model)
    db.commit()