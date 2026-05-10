# models/base_media.py
# Абстрактный базовый класс для всех медиа-ресурсов библиотеки.
# Определяет контракт, который обязаны реализовать Track и Playlist.

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseMedia(ABC):
    """Абстрактный медиа-ресурс с обязательными свойствами."""

    @property
    @abstractmethod
    def duration_str(self) -> str:
        """Строковое представление длительности, напр. «3:47» или «42m 10s»."""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Короткое читаемое имя для отображения в списках."""
