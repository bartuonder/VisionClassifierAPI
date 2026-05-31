from services.celery_config import celery_app
from db.database import SessionLocal
from db.models import ImageTask
from ml.model import get_classifier
import logging


logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="process_image_task", max_retries=3)
def process_image_task(self, task_id: int):

    logger.info(f"[*] Worker took task: Task ID {task_id}")

    db = SessionLocal()

    try:
        task = db.query(ImageTask).filter(ImageTask.id == task_id).first()
        if not task:
            logger.error(f"[!] Task is not found: Task ID {task_id}")
            return {"status": "error", "message": "The task is not in the database."}

        task.status = "processing"
        db.commit()

        result = get_classifier().predict(image_path=task.filename)

        if result.get("success"):
            task.prediction_label = result.get("label")
            task.confidence_score = result.get("confidence")
            task.status = "completed"
            logger.info(f"[+] Successful: {task_id} -> {task.prediction_label} (%{task.confidence_score})")
        else:
            task.status = "failed"
            logger.error(f"[-] AI Error: Task {task_id} -> {result.get('error')}")

        db.commit()
        return {"task_id": task_id, "status": task.status}

    except Exception as e:

        db.rollback()
        logger.error(f"[!] Critical Error (Task {task_id}): {str(e)}")

        try:
            raise self.retry(exc=e, countdown=10)
        except self.MaxRetriesExceededError:

            task = db.query(ImageTask).filter(ImageTask.id == task_id).first()
            if task:
                task.status = "failed"
                db.commit()
            return {"status": "failed", "message": "The maximum number of attempts has been reached."}

    finally:
        db.close()