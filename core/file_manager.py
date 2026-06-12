from __future__ import annotations

import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Iterable

from utils.logger import get_logger


logger = get_logger(__name__)


class FileManager:
    EXT_RULES = {
        ".jpg": "images",
        ".jpeg": "images",
        ".png": "images",
        ".gif": "images",
        ".pdf": "documents",
        ".doc": "documents",
        ".docx": "documents",
        ".txt": "documents",
        ".md": "documents",
        ".mp4": "videos",
        ".mp3": "audio",
        ".zip": "archives",
        ".py": "code",
        ".js": "code",
    }

    def _safe_path(self, path: str | Path) -> Path:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"Path does not exist: {p}")
        return p

    def list_items(self, target: str | Path) -> list[Path]:
        path = self._safe_path(target)
        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")
        return sorted(path.iterdir(), key=lambda p: p.name.lower())

    def create_folder(self, target: str | Path) -> Path:
        path = Path(target).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)
        logger.info("Created folder: %s", path)
        return path

    def rename(self, source: str | Path, new_name: str) -> Path:
        src = self._safe_path(source)
        dst = src.with_name(new_name)
        src.rename(dst)
        logger.info("Renamed %s -> %s", src, dst)
        return dst

    def move(self, source: str | Path, destination_dir: str | Path) -> Path:
        src = self._safe_path(source)
        dst_dir = Path(destination_dir).expanduser().resolve()
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / src.name
        shutil.move(str(src), str(dst))
        logger.info("Moved %s -> %s", src, dst)
        return dst

    def delete(self, target: str | Path) -> None:
        path = self._safe_path(target)
        if path == Path("/"):
            raise ValueError("Refusing to delete root directory")
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        logger.info("Deleted: %s", path)

    def organize(self, folder: str | Path, mode: str = "type") -> dict[str, int]:
        base = self._safe_path(folder)
        if not base.is_dir():
            raise NotADirectoryError(f"Not a directory: {base}")

        moved = Counter()
        for item in base.iterdir():
            if not item.is_file():
                continue
            if mode == "date":
                bucket = datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m")
            elif mode == "type":
                bucket = self.EXT_RULES.get(item.suffix.lower(), "others")
            else:
                bucket = mode
            target_dir = base / bucket
            target_dir.mkdir(exist_ok=True)
            shutil.move(str(item), str(target_dir / item.name))
            moved[bucket] += 1
        logger.info("Organized folder=%s mode=%s moved=%s", base, mode, dict(moved))
        return dict(moved)

    def search(self, folder: str | Path, query: str, include_content: bool = False) -> list[Path]:
        base = self._safe_path(folder)
        if not base.is_dir():
            raise NotADirectoryError(f"Not a directory: {base}")

        matches: list[Path] = []
        q = query.lower()
        for item in base.rglob("*"):
            if not item.is_file():
                continue
            if q in item.name.lower():
                matches.append(item)
                continue
            if include_content:
                try:
                    if q in item.read_text(encoding="utf-8", errors="ignore").lower():
                        matches.append(item)
                except OSError:
                    continue
        return matches

    def analyze(self, folder: str | Path) -> dict[str, object]:
        base = self._safe_path(folder)
        files = [p for p in base.rglob("*") if p.is_file()]
        size_by_ext: Counter[str] = Counter()
        duplicate_basenames: Counter[str] = Counter()

        for f in files:
            size_by_ext[f.suffix.lower() or "<no_ext>"] += f.stat().st_size
            duplicate_basenames[f.name] += 1

        duplicates = [name for name, count in duplicate_basenames.items() if count > 1]
        recommendations: list[str] = []
        if duplicates:
            recommendations.append("Duplicate filenames detected in different folders.")
        if len(files) > 1000:
            recommendations.append("Large file count; consider archive cleanup.")

        return {
            "total_files": len(files),
            "largest_extensions": sorted(size_by_ext.items(), key=lambda i: i[1], reverse=True)[:5],
            "duplicate_filenames": duplicates,
            "recommendations": recommendations,
        }

    def clean_empty_dirs(self, folder: str | Path) -> int:
        base = self._safe_path(folder)
        removed = 0
        for path in sorted((p for p in base.rglob("*") if p.is_dir()), reverse=True):
            if not any(path.iterdir()):
                path.rmdir()
                removed += 1
        logger.info("Cleaned empty directories under %s: %s", base, removed)
        return removed
