import services.tasks as tasks
from db.models import ImageTask
from tests.conftest import TestingSessionLocal


class FakeClassifier:
    def __init__(self, result):
        self.result = result

    def predict(self, image_path):
        return self.result


def _create_task(filename="uploads/test.png"):
    db = TestingSessionLocal()
    task = ImageTask(user_id=1, filename=filename, status="pending")
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id
    db.close()
    return task_id


def _reload(task_id):
    db = TestingSessionLocal()
    task = db.query(ImageTask).filter(ImageTask.id == task_id).first()
    db.close()
    return task


def test_process_image_task_success(monkeypatch):
    monkeypatch.setattr(tasks, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(
        tasks,
        "get_classifier",
        lambda: FakeClassifier({"success": True, "label": "Egyptian cat", "confidence": 88.4}),
    )

    task_id = _create_task()
    result = tasks.process_image_task(task_id)

    assert result["status"] == "completed"
    saved = _reload(task_id)
    assert saved.status == "completed"
    assert saved.prediction_label == "Egyptian cat"
    assert saved.confidence_score == 88.4
    assert saved.error_message is None


def test_process_image_task_failure_records_error(monkeypatch):
    monkeypatch.setattr(tasks, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(
        tasks,
        "get_classifier",
        lambda: FakeClassifier({"success": False, "error": "cannot read image"}),
    )

    task_id = _create_task()
    result = tasks.process_image_task(task_id)

    assert result["status"] == "failed"
    saved = _reload(task_id)
    assert saved.status == "failed"
    assert saved.error_message == "cannot read image"


def test_process_image_task_missing_task(monkeypatch):
    monkeypatch.setattr(tasks, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(
        tasks,
        "get_classifier",
        lambda: FakeClassifier({"success": True, "label": "x", "confidence": 1.0}),
    )

    result = tasks.process_image_task(123456)
    assert result["status"] == "error"
