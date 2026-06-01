MODEL_NAME = "google/vit-base-patch16-224"


class VisionClassifier:
    def __init__(self):

        import torch
        from transformers import ViTImageProcessor, ViTForImageClassification

        self._torch = torch

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[*] Yapay Zeka Modeli Yükleniyor... Kullanılan Donanım: {self.device}")

        self.processor = ViTImageProcessor.from_pretrained(MODEL_NAME)

        self.model = ViTForImageClassification.from_pretrained(MODEL_NAME).to(self.device)
        self.model.eval()

    def predict(self, image_path: str):

        try:
            from PIL import Image

            torch = self._torch

            image = Image.open(image_path).convert("RGB")

            inputs = self.processor(images=image, return_tensors="pt").to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)

            logits = outputs.logits

            predicted_class_idx = logits.argmax(-1).item()

            predicted_label = self.model.config.id2label[predicted_class_idx]

            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            confidence_score = probabilities[0][predicted_class_idx].item()

            return {
                "success": True,
                "label": predicted_label,
                "confidence": round(confidence_score * 100, 2)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


_classifier = None


def get_classifier() -> VisionClassifier:
    global _classifier
    if _classifier is None:
        _classifier = VisionClassifier()
    return _classifier