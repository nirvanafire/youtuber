import json
import os
from src.models.settings import AppSettings


class SettingsManager:
    def __init__(self, path: str):
        self._path = path

    def load(self) -> AppSettings:
        if os.path.exists(self._path):
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return AppSettings(**data)
        return AppSettings()

    def save(self, settings: AppSettings) -> None:
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(settings.model_dump(), f, ensure_ascii=False, indent=2)

    def update(self, data: dict) -> AppSettings:
        settings = self.load()
        updated = settings.model_copy(update=data)
        self.save(updated)
        return updated
