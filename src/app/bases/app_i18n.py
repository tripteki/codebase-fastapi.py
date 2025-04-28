from pathlib import Path
from typing import Dict, Optional
from typing_extensions import Self
import json
from src.app.configs.app_config import AppConfig

class AppI18n:
    """
    AppI18n

    Attributes:
        _translations (Dict[str, Dict[str, object]])
        _locale (Optional[str])
        _fallback_locale (Optional[str])
        _lang_path (Optional[Path])
    """
    _translations: Dict[str, Dict[str, object]] = {}
    _locale: Optional[str] = None
    _fallback_locale: Optional[str] = None
    _lang_path: Optional[Path] = None

    @classmethod
    def langPath (cls) -> Path:
        """
        Args:
            cls
        Returns:
            Path
        """
        if cls._lang_path is None:
            cls._lang_path = Path (__file__).parent.parent / "langs"
        return cls._lang_path

    @classmethod
    def loadTranslations (cls, locale: str) -> Dict[str, object]:
        """
        Args:
            locale (str)
        Returns:
            Dict[str, object]
        """
        if locale in cls._translations:
            return cls._translations[locale]
        langPath = cls.langPath ()
        translationFile = langPath / f"{locale}.json"
        if translationFile.exists ():
            try:
                with open (translationFile, "r", encoding="utf-8") as f:
                    cls._translations[locale] = json.load (f)
                    return cls._translations[locale]
            except Exception as e:
                print (f"Error loading translation file {translationFile}: {e}")
        return {}

    @classmethod
    def t (cls, key: str, locale: Optional[str] = None, args: Optional[Dict[str, object]] = None) -> str:
        """
        Args:
            key (str)
            locale (Optional[str])
            args (Optional[Dict[str, object]])
        Returns:
            str
        """
        config = AppConfig.config ()
        if locale is None:
            locale = cls._locale or config.locale
        fallbackLocale = cls._fallback_locale or config.fallback_locale
        translations = cls.loadTranslations (locale)
        fallbackTranslations = cls.loadTranslations (fallbackLocale) if fallbackLocale != locale else {}
        keys = key.split (".")
        value = translations
        fallbackValue = fallbackTranslations
        for k in keys:
            if isinstance (value, dict) and k in value:
                value = value[k]
                if isinstance (fallbackValue, dict) and k in fallbackValue:
                    fallbackValue = fallbackValue[k]
                else:
                    fallbackValue = None
            else:
                value = None
                break
        if value is None:
            if fallbackValue is not None:
                value = fallbackValue
            else:
                return key
        if not isinstance (value, str):
            return key
        if args:
            try:
                return value.format (**args)
            except Exception:
                return value
        return value

    @classmethod
    def setLocale (cls, locale: str) -> None:
        """
        Args:
            locale (str)
        Returns:
            None
        """
        cls._locale = locale

    @classmethod
    def getLocale (cls) -> Optional[str]:
        """
        Args:
            cls
        Returns:
            Optional[str]
        """
        return cls._locale

    @classmethod
    def setFallbackLocale (cls, locale: str) -> None:
        """
        Args:
            locale (str)
        Returns:
            None
        """
        cls._fallback_locale = locale

    @classmethod
    def getFallbackLocale (cls) -> Optional[str]:
        """
        Args:
            cls
        Returns:
            Optional[str]
        """
        return cls._fallback_locale

    @classmethod
    def i18n (cls) -> Self:
        """
        Args:
            cls
        Returns:
            AppI18n
        """
        return cls
