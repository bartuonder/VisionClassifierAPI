from fastapi import APIRouter, UploadFile, File, HTTPException, status
from api.deps import db_dependency, user_dependency
from db.models import ImageTask
import shutil
import os
import uuid
from api.schemas import TaskSubmitResponse, TaskStatusResponse
from services.tasks import process_image_task

router = APIRouter(
    prefix="/classify",
    tags=["vision"]
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/", status_code=status.HTTP_202_ACCEPTED, response_model=TaskSubmitResponse)
async def upload_image_for_classification(
        user: user_dependency,
        db: db_dependency,
        file: UploadFile = File(...)
):

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload image files only.")

    if not file.filename or "." not in file.filename:
        raise HTTPException(status_code=400, detail="Invalid file name.")

    file_extension = file.filename.rsplit(".", 1)[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = f"{UPLOAD_DIR}/{unique_filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_task = ImageTask(
        user_id=user.get("id"),
        filename=file_path,
        status="pending"
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    process_image_task.delay(new_task.id)

    return {
        "message": "The image was successfully captured and added to the AI queue.",
        "task_id": new_task.id,
        "status_url": f"/classify/status/{new_task.id}"
    }


@router.get("/status/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskStatusResponse)
async def get_classification_status(
        task_id: int,
        user: user_dependency,
        db: db_dependency
):

    task = db.query(ImageTask).filter(ImageTask.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task is not found.")

    if task.user_id != user.get("id"):
        raise HTTPException(status_code=403, detail="You don't have permission to see task's result.")

    return {
        "task_id": task.id,
        "status": task.status,
        "prediction": task.prediction_label,
        "confidence": task.confidence_score,
        "created_at": task.created_at
    }