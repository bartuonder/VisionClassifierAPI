from fastapi import APIRouter
from api.deps import get_db, db_dependency, authenticate_user, create_access_token, get_current_user, user_dependency, bcrypt_context, form_dependency
from starlette import status
from api.schemas import CreateUser, Token
from db.models import Users
from fastapi import HTTPException
from datetime import timedelta


router = APIRouter(
    prefix = "/auth",
    tags = ["auth"]
)


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def register_user(db: db_dependency,
                        user_data: CreateUser):

    existing_user = db.query(Users).filter(
        (Users.username == user_data.username) | (Users.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or Email already registered.")

    user_model = Users(
        username=user_data.username,
        email=user_data.email,
        hashed_password=bcrypt_context.hash(user_data.password)
    )

    db.add(user_model)
    db.commit()


@router.post("/login", response_model=Token)
async def login_for_token(form: form_dependency,
                          db: db_dependency):
    user = authenticate_user(form.username, form.password, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldn't authorize.")

    token = create_access_token(user.username, user.id, timedelta(minutes=30))

    return {"access_token": token, "token_type": "bearer"}