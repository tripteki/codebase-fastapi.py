from contextvars import ContextVar, Token
from pathlib import Path
from typing import Dict, Optional
from typing_extensions import Self
import json
from src.app.configs.app_config import AppConfig

_requestLocale: ContextVar[Optional[str]] = ContextVar ("app_i18n_request_locale", default=None)

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
            locale = _requestLocale.get () or cls._locale or config.locale
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
        return _requestLocale.get () or cls._locale

    @classmethod
    def resolveLocale (cls, acceptLanguage: Optional[str]) -> Optional[str]:
        """
        Args:
            acceptLanguage (Optional[str])
        Returns:
            Optional[str]
        """
        for part in (acceptLanguage or "").split (","):
            locale = part.split (";")[0].strip ().split ("-")[0].lower ()
            if locale and (cls.langPath () / f"{locale}.json").is_file ():
                return locale
        return None

    @classmethod
    def useRequestLocale (cls, locale: Optional[str]) -> Token:
        """
        Args:
            locale (Optional[str])
        Returns:
            Token
        """
        return _requestLocale.set (locale)

    @classmethod
    def resetRequestLocale (cls, token: Token) -> None:
        """
        Args:
            token (Token)
        Returns:
            None
        """
        _requestLocale.reset (token)

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
