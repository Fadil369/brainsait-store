/**
 * Saudi Riyal Currency Configuration
 * Implements the new 2025 official SAR symbol and formatting
 */

export const SAR_CODE = 'SAR';
export const SAR_NAME = 'Saudi Riyal';
export const SAR_NAME_AR = 'ريال سعودي';

export interface CurrencyConfig {
  code: string;
  name: string;
  nameAr: string;
  position: 'before' | 'after';
  decimalPlaces: number;
  thousandsSeparator: string;
  decimalSeparator: string;
  useNewSymbol: boolean;
}

export const CURRENCY_CONFIG: CurrencyConfig = {
  code: SAR_CODE,
  name: SAR_NAME,
  nameAr: SAR_NAME_AR,
  position: 'before', // New SAR Symbol 1,500.00
  decimalPlaces: 2,
  thousandsSeparator: ',',
  decimalSeparator: '.',
  useNewSymbol: true, // Use the new 2025 Saudi Riyal icon
};

/**
 * Format amount with Saudi Riyal - returns object for flexible rendering
 */
export function formatSAR(amount: number, options?: {
  showSymbol?: boolean;
  showCode?: boolean;
  isArabic?: boolean;
  compact?: boolean;
}): {
  amount: string;
  currency: string;
  formatted: string;
  useNewSymbol: boolean;
} {
  const {
    showSymbol = true,
    showCode = false,
    isArabic = false,
    compact = false
  } = options || {};

  // Format the number with Arabic-Saudi locale for proper number formatting
  const formattedAmount = new Intl.NumberFormat(isArabic ? 'ar-SA' : 'en-SA', {
    style: 'decimal',
    minimumFractionDigits: compact ? 0 : CURRENCY_CONFIG.decimalPlaces,
    maximumFractionDigits: CURRENCY_CONFIG.decimalPlaces,
  }).format(amount);

  // Determine currency display
  let currency = '';
  if (showCode) {
    currency = isArabic ? CURRENCY_CONFIG.nameAr : CURRENCY_CONFIG.code;
  }

  // Build the display string
  let formatted = formattedAmount;
  if (currency) {
    formatted = isArabic 
      ? `${formattedAmount} ${currency}`
      : `${formattedAmount} ${currency}`;
  }

  return {
    amount: formattedAmount,
    currency,
    formatted,
    useNewSymbol: showSymbol && CURRENCY_CONFIG.useNewSymbol,
  };
}

/**
 * Parse SAR string back to number
 */
export function parseSAR(sarString: string): number {
  // Remove currency symbols and codes
  const cleanString = sarString
    .replace(SAR_CODE, '')
    .replace(SAR_NAME, '')
    .replace(SAR_NAME_AR, '')
    .replace(/[,\s]/g, '')
    .trim();

  return parseFloat(cleanString) || 0;
}

/**
 * Convert USD to SAR (you might want to fetch live rates)
 * Current rate as of 2025: ~3.75 SAR per USD
 */
export function convertUSDToSAR(usdAmount: number, exchangeRate: number = 3.75): number {
  return Math.round((usdAmount * exchangeRate) * 100) / 100; // Round to 2 decimal places
}

/**
 * Convert SAR to USD
 */
export function convertSARToUSD(sarAmount: number, exchangeRate: number = 3.75): number {
  return Math.round((sarAmount / exchangeRate) * 100) / 100;
}

/**
 * Get currency display for different contexts
 */
export function getCurrencyDisplay(context: 'short' | 'long' | 'symbol', isArabic: boolean = false) {
  switch (context) {
    case 'symbol':
      return { useNewSymbol: true, text: 'SAR' }; // Will render the new icon
    case 'short':
      return { useNewSymbol: false, text: SAR_CODE };
    case 'long':
      return { useNewSymbol: false, text: isArabic ? SAR_NAME_AR : SAR_NAME };
    default:
      return { useNewSymbol: true, text: 'SAR' };
  }
}

/**
 * Validate SAR amount
 */
export function isValidSARAmount(amount: number): boolean {
  return !isNaN(amount) && isFinite(amount) && amount >= 0;
}

/**
 * Format for different payment gateways
 */
export function formatForPaymentGateway(
  amount: number, 
  gateway: 'stripe' | 'paypal' | 'mada' | 'stc' | 'apple_pay'
): { amount: number; currency: string; formatted: string; displayAmount: string } {
  const sarFormatted = formatSAR(amount, { isArabic: gateway === 'mada' || gateway === 'stc' });
  
  switch (gateway) {
    case 'stripe':
      // Stripe expects amounts in smallest currency unit (halalas for SAR)
      return {
        amount: Math.round(amount * 100), // Convert to halalas
        currency: 'sar',
        formatted: sarFormatted.formatted,
        displayAmount: sarFormatted.amount
      };
    case 'paypal':
      return {
        amount: amount,
        currency: 'SAR',
        formatted: sarFormatted.formatted,
        displayAmount: sarFormatted.amount
      };
    case 'apple_pay':
      return {
        amount: amount,
        currency: 'SAR',
        formatted: sarFormatted.formatted,
        displayAmount: sarFormatted.amount
      };
    case 'mada':
    case 'stc':
      return {
        amount: amount,
        currency: 'SAR',
        formatted: formatSAR(amount, { isArabic: true }).formatted,
        displayAmount: sarFormatted.amount
      };
    default:
      return {
        amount: amount,
        currency: 'SAR',
        formatted: sarFormatted.formatted,
        displayAmount: sarFormatted.amount
      };
  }
}

/**
 * Get current exchange rate (in real app, fetch from API)
 */
export async function getCurrentExchangeRate(): Promise<number> {
  // In production, fetch from a real exchange rate API
  // For now, return the fixed rate
  return 3.75;
}

/**
 * Format compact amounts (for dashboards)
 */
export function formatCompactSAR(amount: number, isArabic: boolean = false): string {
  if (amount >= 1000000) {
    const millions = amount / 1000000;
    const suffix = isArabic ? 'م.ر.س' : 'M SAR';
    return `${millions.toFixed(1)}${suffix}`;
  } else if (amount >= 1000) {
    const thousands = amount / 1000;
    const suffix = isArabic ? 'ألف ر.س' : 'K SAR';
    return `${thousands.toFixed(1)}${suffix}`;
  }
  return formatSAR(amount, { compact: true, isArabic }).formatted;
}

const CurrencyUtils = {
  CURRENCY_CONFIG,
  formatSAR,
  parseSAR,
  convertUSDToSAR,
  convertSARToUSD,
  getCurrencyDisplay,
  isValidSARAmount,
  formatForPaymentGateway,
  getCurrentExchangeRate,
  formatCompactSAR,
  SAR_CODE,
  SAR_NAME,
  SAR_NAME_AR,
};

export default CurrencyUtils;