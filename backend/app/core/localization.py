"""
Localization middleware and utilities for Arabic/English support
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings

# Translation cache
_translations: Dict[str, Dict[str, str]] = {}
_loaded_languages = set()


class LocalizationMiddleware(BaseHTTPMiddleware):
    """Middleware to handle language localization"""

    async def dispatch(self, request: Request, call_next):
        # Extract language from request
        language = self._extract_language(request)

        # Set language context
        request.state.language = language

        # Add language to response headers
        response = await call_next(request)
        response.headers["Content-Language"] = language

        return response

    def _extract_language(self, request: Request) -> str:
        """Extract language preference from request"""

        # 1. Check query parameter
        lang = request.query_params.get("lang")
        if lang and lang.lower() in settings.SUPPORTED_LANGUAGES:
            return lang.lower()

        # 2. Check custom header
        lang = request.headers.get("X-Language")
        if lang and lang.lower() in settings.SUPPORTED_LANGUAGES:
            return lang.lower()

        # 3. Parse Accept-Language header
        accept_lang = request.headers.get("Accept-Language", "")
        if accept_lang:
            for lang_option in accept_lang.split(","):
                lang_code = lang_option.split(";")[0].strip().lower()
                if lang_code.startswith("ar"):
                    return "ar"
                elif lang_code.startswith("en"):
                    return "en"

        # 4. Default language
        return settings.DEFAULT_LANGUAGE


def load_translations():
    """Load translation files"""
    global _translations, _loaded_languages

    translations_dir = Path(__file__).parent.parent / "translations"

    for lang in settings.SUPPORTED_LANGUAGES:
        if lang in _loaded_languages:
            continue

        translation_file = translations_dir / f"{lang}.json"
        if translation_file.exists():
            try:
                with open(translation_file, "r", encoding="utf-8") as f:
                    translation_data = json.load(f)
                _translations[lang] = translation_data
                _loaded_languages.add(lang)
            except Exception as e:
                print(f"Error loading translation file {translation_file}: {e}")


def _(key: str, language: str = "en", **kwargs) -> str:
    """Get translated string"""

    # Load translations if not already loaded
    if language not in _loaded_languages:
        load_translations()

    # Get translation
    translation = _translations.get(language, {}).get(key, key)

    # Format with kwargs if provided
    if kwargs:
        try:
            translation = translation.format(**kwargs)
        except (KeyError, ValueError):
            pass  # Return unformatted if formatting fails

    return translation


def get_localized_message(
    key: str,
    language: str = "en",
    default_en: str = None,
    default_ar: str = None,
    **kwargs,
) -> str:
    """Get localized message with fallbacks"""

    # Try to get from translation files first
    message = _(key, language, **kwargs)

    # If not found in translation files, use provided defaults
    if message == key:
        if language == "ar" and default_ar:
            message = default_ar
        elif language == "en" and default_en:
            message = default_en
        elif default_en:  # Fallback to English
            message = default_en

    # Format with kwargs
    if kwargs:
        try:
            message = message.format(**kwargs)
        except (KeyError, ValueError):
            pass

    return message


def get_currency_symbol(currency: str = "SAR") -> str:
    """Get currency symbol"""
    symbols = {
        "SAR": "ر.س",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
    }
    return symbols.get(currency, currency)


def format_currency(amount: float, currency: str = "SAR", language: str = "en") -> str:
    """Format currency based on language"""

    symbol = get_currency_symbol(currency)

    if language == "ar":
        # Arabic formatting: amount symbol
        return f"{amount:,.2f} {symbol}"
    else:
        # English formatting: symbol amount
        return f"{symbol}{amount:,.2f}"


def format_date(date_obj, language: str = "en", format_type: str = "short") -> str:
    """Format date based on language"""

    if not date_obj:
        return ""

    try:
        if language == "ar":
            # Arabic date format
            if format_type == "short":
                return date_obj.strftime("%d/%m/%Y")
            else:
                return date_obj.strftime("%d %B %Y")
        else:
            # English date format
            if format_type == "short":
                return date_obj.strftime("%m/%d/%Y")
            else:
                return date_obj.strftime("%B %d, %Y")
    except:
        return str(date_obj)


def get_direction(language: str = "en") -> str:
    """Get text direction for language"""
    return "rtl" if language == "ar" else "ltr"


def get_localized_field(obj: Any, field: str, language: str = "en") -> str:
    """Get localized field from object (e.g., name vs name_ar)"""

    if language == "ar":
        ar_field = f"{field}_ar"
        if hasattr(obj, ar_field) and getattr(obj, ar_field):
            return getattr(obj, ar_field)

    # Fallback to default field
    return getattr(obj, field, "")
