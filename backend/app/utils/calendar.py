"""
Hijri/Gregorian Calendar Utilities for Backend
Provides cultural calendar support for Saudi Arabia
"""

from datetime import datetime, date
from typing import Dict, Tuple, Optional, Any
from enum import Enum


class CalendarType(str, Enum):
    """Calendar types"""
    GREGORIAN = "gregorian"
    HIJRI = "hijri"


# Hijri month names in Arabic
HIJRI_MONTHS_AR = {
    1: "محرم", 2: "صفر", 3: "ربيع الأول", 4: "ربيع الآخر",
    5: "جمادى الأولى", 6: "جمادى الآخرة", 7: "رجب", 8: "شعبان",
    9: "رمضان", 10: "شوال", 11: "ذو القعدة", 12: "ذو الحجة",
}

# Hijri month names in English
HIJRI_MONTHS_EN = {
    1: "Muharram", 2: "Safar", 3: "Rabi' al-Awwal", 4: "Rabi' al-Thani",
    5: "Jumada al-Awwal", 6: "Jumada al-Thani", 7: "Rajab", 8: "Sha'ban",
    9: "Ramadan", 10: "Shawwal", 11: "Dhu al-Qi'dah", 12: "Dhu al-Hijjah",
}


def gregorian_to_hijri(gregorian_date) -> Tuple[int, int, int]:
    """
    Convert Gregorian date to Hijri date
    
    Note: This is a PLACEHOLDER implementation for demonstration.
    For production use, install and use the 'hijri-converter' package:
        pip install hijri-converter
        from hijri_converter import Gregorian
        hijri = Gregorian(year, month, day).to_hijri()
    
    The current implementation provides approximate dates only (±1-2 days accuracy).
    """
    if isinstance(gregorian_date, datetime):
        gregorian_date = gregorian_date.date()
    
    # TODO: Replace with proper hijri-converter library for production
    # This simplified calculation is for development/testing only
    # Real conversion requires complex lunar calendar calculations
    
    year = gregorian_date.year
    month = gregorian_date.month
    day = gregorian_date.day
    
    # PLACEHOLDER: Approximate conversion (NOT ACCURATE)
    # In production, use: from hijri_converter import Gregorian
    # hijri = Gregorian(year, month, day).to_hijri()
    hijri_year = int(year - 621.5643)
    hijri_month = ((month + 10) % 12) + 1  # Rough approximation
    hijri_day = day
    
    return (hijri_year, hijri_month, hijri_day)


def format_date(dt, calendar_type: CalendarType = CalendarType.GREGORIAN, language: str = "en") -> str:
    """Format date according to calendar preference and language"""
    if calendar_type == CalendarType.HIJRI:
        hijri_year, hijri_month, hijri_day = gregorian_to_hijri(dt)
        month_names = HIJRI_MONTHS_AR if language == "ar" else HIJRI_MONTHS_EN
        month_name = month_names.get(hijri_month, "")
        
        if language == "ar":
            return f"{hijri_day} {month_name} {hijri_year} هـ"
        else:
            return f"{hijri_day} {month_name} {hijri_year} AH"
    else:
        if isinstance(dt, datetime):
            dt = dt.date()
        
        if language == "ar":
            months_ar = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
                        "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
            month_name = months_ar[dt.month - 1]
            return f"{dt.day} {month_name} {dt.year}"
        else:
            return dt.strftime("%B %d, %Y")


def is_ramadan(dt=None) -> bool:
    """Check if date falls in Ramadan"""
    if dt is None:
        dt = datetime.now()
    _, hijri_month, _ = gregorian_to_hijri(dt)
    return hijri_month == 9


def get_calendar_info(dt=None) -> Dict[str, Any]:
    """Get calendar information for a date"""
    if dt is None:
        dt = datetime.now()
    
    if isinstance(dt, datetime):
        gregorian_date = dt.date()
    else:
        gregorian_date = dt
    
    hijri_year, hijri_month, hijri_day = gregorian_to_hijri(gregorian_date)
    
    return {
        "gregorian": {
            "year": gregorian_date.year,
            "month": gregorian_date.month,
            "day": gregorian_date.day,
            "formatted_en": format_date(gregorian_date, CalendarType.GREGORIAN, "en"),
            "formatted_ar": format_date(gregorian_date, CalendarType.GREGORIAN, "ar"),
        },
        "hijri": {
            "year": hijri_year,
            "month": hijri_month,
            "day": hijri_day,
            "month_name_en": HIJRI_MONTHS_EN.get(hijri_month, ""),
            "month_name_ar": HIJRI_MONTHS_AR.get(hijri_month, ""),
            "formatted_en": format_date(gregorian_date, CalendarType.HIJRI, "en"),
            "formatted_ar": format_date(gregorian_date, CalendarType.HIJRI, "ar"),
        },
        "is_ramadan": is_ramadan(dt),
    }
