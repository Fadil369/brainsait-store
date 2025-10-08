/**
 * Hijri/Gregorian Calendar Integration
 * Supports cultural calendar preferences for Saudi Arabia
 */

export interface CalendarDate {
  gregorian: {
    year: number;
    month: number;
    day: number;
    formatted: string;
  };
  hijri: {
    year: number;
    month: number;
    day: number;
    formatted: string;
    monthName: string;
  };
}

/**
 * Hijri month names in Arabic
 */
const HIJRI_MONTHS_AR = [
  'محرم',
  'صفر',
  'ربيع الأول',
  'ربيع الآخر',
  'جمادى الأولى',
  'جمادى الآخرة',
  'رجب',
  'شعبان',
  'رمضان',
  'شوال',
  'ذو القعدة',
  'ذو الحجة',
];

/**
 * Hijri month names in English
 */
const HIJRI_MONTHS_EN = [
  'Muharram',
  'Safar',
  'Rabi\' al-Awwal',
  'Rabi\' al-Thani',
  'Jumada al-Awwal',
  'Jumada al-Thani',
  'Rajab',
  'Sha\'ban',
  'Ramadan',
  'Shawwal',
  'Dhu al-Qi\'dah',
  'Dhu al-Hijjah',
];

/**
 * Convert Gregorian date to Hijri date
 * Using simplified conversion algorithm
 */
export function gregorianToHijri(date: Date): CalendarDate['hijri'] {
  // Simplified conversion - In production, use a proper library like moment-hijri
  const gregorianYear = date.getFullYear();
  const gregorianMonth = date.getMonth() + 1;
  const gregorianDay = date.getDate();

  // Approximate conversion (simplified)
  // In production, use accurate conversion library
  const hijriYear = Math.floor(gregorianYear - 621.5643);
  const hijriMonth = gregorianMonth;
  const hijriDay = gregorianDay;

  return {
    year: hijriYear,
    month: hijriMonth,
    day: hijriDay,
    formatted: `${hijriDay}/${hijriMonth}/${hijriYear}`,
    monthName: HIJRI_MONTHS_AR[hijriMonth - 1] || '',
  };
}

/**
 * Get full calendar date (both Gregorian and Hijri)
 */
export function getCalendarDate(date: Date = new Date()): CalendarDate {
  const gregorian = {
    year: date.getFullYear(),
    month: date.getMonth() + 1,
    day: date.getDate(),
    formatted: date.toLocaleDateString('en-US'),
  };

  const hijri = gregorianToHijri(date);

  return {
    gregorian,
    hijri,
  };
}

/**
 * Format date based on calendar preference
 */
export function formatDate(
  date: Date,
  calendar: 'gregorian' | 'hijri' = 'gregorian',
  language: 'ar' | 'en' = 'en'
): string {
  const calendarDate = getCalendarDate(date);

  if (calendar === 'hijri') {
    const monthName = language === 'ar' 
      ? HIJRI_MONTHS_AR[calendarDate.hijri.month - 1]
      : HIJRI_MONTHS_EN[calendarDate.hijri.month - 1];

    if (language === 'ar') {
      return `${calendarDate.hijri.day} ${monthName} ${calendarDate.hijri.year} هـ`;
    } else {
      return `${calendarDate.hijri.day} ${monthName} ${calendarDate.hijri.year} AH`;
    }
  } else {
    if (language === 'ar') {
      return date.toLocaleDateString('ar-SA');
    } else {
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    }
  }
}

/**
 * Format date range
 */
export function formatDateRange(
  startDate: Date,
  endDate: Date,
  calendar: 'gregorian' | 'hijri' = 'gregorian',
  language: 'ar' | 'en' = 'en'
): string {
  const start = formatDate(startDate, calendar, language);
  const end = formatDate(endDate, calendar, language);
  const separator = language === 'ar' ? ' إلى ' : ' to ';
  return `${start}${separator}${end}`;
}

/**
 * Get Hijri month name
 */
export function getHijriMonthName(
  month: number,
  language: 'ar' | 'en' = 'en'
): string {
  const months = language === 'ar' ? HIJRI_MONTHS_AR : HIJRI_MONTHS_EN;
  return months[month - 1] || '';
}

/**
 * Check if date is in Ramadan
 */
export function isRamadan(date: Date = new Date()): boolean {
  const hijri = gregorianToHijri(date);
  return hijri.month === 9; // Ramadan is the 9th month
}

/**
 * Check if date is in Hajj season (Dhu al-Hijjah)
 */
export function isHajjSeason(date: Date = new Date()): boolean {
  const hijri = gregorianToHijri(date);
  return hijri.month === 12; // Dhu al-Hijjah is the 12th month
}

/**
 * Get Islamic holidays
 */
export function getIslamicHolidays(year: number): Array<{
  name: string;
  nameAr: string;
  month: number;
  day: number;
}> {
  return [
    { name: 'Islamic New Year', nameAr: 'رأس السنة الهجرية', month: 1, day: 1 },
    { name: 'Ashura', nameAr: 'عاشوراء', month: 1, day: 10 },
    { name: 'Mawlid al-Nabi', nameAr: 'المولد النبوي', month: 3, day: 12 },
    { name: 'Ramadan Begins', nameAr: 'بداية رمضان', month: 9, day: 1 },
    { name: 'Eid al-Fitr', nameAr: 'عيد الفطر', month: 10, day: 1 },
    { name: 'Arafat Day', nameAr: 'يوم عرفة', month: 12, day: 9 },
    { name: 'Eid al-Adha', nameAr: 'عيد الأضحى', month: 12, day: 10 },
  ];
}

export default {
  getCalendarDate,
  formatDate,
  formatDateRange,
  gregorianToHijri,
  getHijriMonthName,
  isRamadan,
  isHajjSeason,
  getIslamicHolidays,
};
