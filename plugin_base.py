# plugin_base.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class LinkManagerPlugin(ABC):
    @staticmethod
    @abstractmethod
    def plugin_info() -> Dict[str, Any]:
        """
        Возвращает информацию о плагине.
        Должен возвращать словарь с ключами: 'name', 'version', 'description', 'author'.
        """
        pass

    @abstractmethod
    def run(self, url_links: Dict[str, Dict[str, str]], action: str = None, key: str = None, **kwargs: Any) -> Any:
        """
        Основной метод плагина, вызываемый Link Manager.

        Args:
            url_links: Словарь всех URL-ссылок.
            action: Действие, вызвавшее плагин (например, 'open', 'add', 'delete', 'export').
            key: Ключ URL, если действие связано с конкретной ссылкой.
            kwargs: Дополнительные аргументы, которые могут быть переданы плагину.

        Returns:
            Может возвращать любые данные в зависимости от назначения плагина.
        """
        pass
