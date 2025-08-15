import { 
  SAR_CODE, 
  SAR_NAME, 
  SAR_NAME_AR, 
  CURRENCY_CONFIG,
  formatSAR,
  parseSAR,
  convertUSDToSAR,
  convertSARToUSD,
  getCurrencyDisplay,
  isValidSARAmount,
  formatForPaymentGateway,
  formatCompactSAR
} from '@/lib/currency';

describe('Currency Library', () => {
  describe('Constants', () => {
    it('should have correct SAR constants', () => {
      expect(SAR_CODE).toBe('SAR');
      expect(SAR_NAME).toBe('Saudi Riyal');
      expect(SAR_NAME_AR).toBe('ريال سعودي');
    });

    it('should have correct currency configuration', () => {
      expect(CURRENCY_CONFIG.code).toBe('SAR');
      expect(CURRENCY_CONFIG.position).toBe('before');
      expect(CURRENCY_CONFIG.decimalPlaces).toBe(2);
      expect(CURRENCY_CONFIG.useNewSymbol).toBe(true);
    });
  });

  describe('formatSAR', () => {
    it('should format SAR amounts in English', () => {
      const result = formatSAR(1000);
      expect(result.amount).toBe('1,000.00');
      expect(result.formatted).toBe('1,000.00');
      expect(result.useNewSymbol).toBe(true);
    });

    it('should format SAR amounts in Arabic', () => {
      const result = formatSAR(1000, { isArabic: true });
      expect(result.amount).toContain('١');
      expect(result.useNewSymbol).toBe(true);
    });

    it('should show currency code when requested', () => {
      const result = formatSAR(1000, { showCode: true });
      expect(result.currency).toBe('SAR');
      expect(result.formatted).toContain('SAR');
    });

    it('should show Arabic currency name when requested', () => {
      const result = formatSAR(1000, { showCode: true, isArabic: true });
      expect(result.currency).toBe('ريال سعودي');
      expect(result.formatted).toContain('ريال سعودي');
    });

    it('should handle compact formatting', () => {
      const result = formatSAR(1000, { compact: true });
      expect(result.amount).toBe('1,000');
    });

    it('should handle zero values', () => {
      const result = formatSAR(0);
      expect(result.amount).toBe('0.00');
      expect(result.formatted).toBe('0.00');
    });

    it('should handle negative values', () => {
      const result = formatSAR(-1000);
      expect(result.formatted).toContain('-');
    });

    it('should handle decimal values', () => {
      const result = formatSAR(1000.99);
      expect(result.amount).toBe('1,000.99');
    });
  });

  describe('parseSAR', () => {
    it('should parse SAR formatted strings', () => {
      expect(parseSAR('1,000.00 SAR')).toBe(1000);
      expect(parseSAR('500.99 ريال سعودي')).toBe(500.99);
    });

    it('should handle plain numbers', () => {
      expect(parseSAR('1000')).toBe(1000);
      expect(parseSAR('999.99')).toBe(999.99);
    });

    it('should handle invalid input', () => {
      expect(parseSAR('invalid')).toBe(0);
      expect(parseSAR('')).toBe(0);
    });

    it('should remove whitespace and commas', () => {
      expect(parseSAR('1, 000.00 SAR')).toBe(1000);
      expect(parseSAR(' 500 ')).toBe(500);
    });
  });

  describe('convertUSDToSAR', () => {
    it('should convert USD to SAR with default rate', () => {
      expect(convertUSDToSAR(100)).toBe(375);
    });

    it('should convert USD to SAR with custom rate', () => {
      expect(convertUSDToSAR(100, 4.0)).toBe(400);
    });

    it('should handle decimal amounts', () => {
      expect(convertUSDToSAR(100.50)).toBe(376.88);
    });

    it('should handle zero amounts', () => {
      expect(convertUSDToSAR(0)).toBe(0);
    });

    it('should round to 2 decimal places', () => {
      expect(convertUSDToSAR(33.33, 3.75)).toBe(124.99);
    });
  });

  describe('convertSARToUSD', () => {
    it('should convert SAR to USD with default rate', () => {
      expect(convertSARToUSD(375)).toBe(100);
    });

    it('should convert SAR to USD with custom rate', () => {
      expect(convertSARToUSD(400, 4.0)).toBe(100);
    });

    it('should handle decimal amounts', () => {
      expect(convertSARToUSD(376.88, 3.75)).toBe(100.5);
    });

    it('should handle zero amounts', () => {
      expect(convertSARToUSD(0)).toBe(0);
    });

    it('should round to 2 decimal places', () => {
      expect(convertSARToUSD(125, 3.75)).toBe(33.33);
    });
  });

  describe('getCurrencyDisplay', () => {
    it('should return symbol display', () => {
      const result = getCurrencyDisplay('symbol');
      expect(result.useNewSymbol).toBe(true);
      expect(result.text).toBe('SAR');
    });

    it('should return short display', () => {
      const result = getCurrencyDisplay('short');
      expect(result.useNewSymbol).toBe(false);
      expect(result.text).toBe('SAR');
    });

    it('should return long display in English', () => {
      const result = getCurrencyDisplay('long', false);
      expect(result.useNewSymbol).toBe(false);
      expect(result.text).toBe('Saudi Riyal');
    });

    it('should return long display in Arabic', () => {
      const result = getCurrencyDisplay('long', true);
      expect(result.useNewSymbol).toBe(false);
      expect(result.text).toBe('ريال سعودي');
    });
  });

  describe('isValidSARAmount', () => {
    it('should validate positive amounts', () => {
      expect(isValidSARAmount(100)).toBe(true);
      expect(isValidSARAmount(0)).toBe(true);
      expect(isValidSARAmount(0.99)).toBe(true);
    });

    it('should reject negative amounts', () => {
      expect(isValidSARAmount(-100)).toBe(false);
    });

    it('should reject invalid numbers', () => {
      expect(isValidSARAmount(NaN)).toBe(false);
      expect(isValidSARAmount(Infinity)).toBe(false);
      expect(isValidSARAmount(-Infinity)).toBe(false);
    });
  });

  describe('formatForPaymentGateway', () => {
    const testAmount = 100.50;

    it('should format for Stripe (in halalas)', () => {
      const result = formatForPaymentGateway(testAmount, 'stripe');
      expect(result.amount).toBe(10050); // 100.50 * 100 halalas
      expect(result.currency).toBe('sar');
      expect(result.displayAmount).toBe('100.50');
    });

    it('should format for PayPal', () => {
      const result = formatForPaymentGateway(testAmount, 'paypal');
      expect(result.amount).toBe(100.50);
      expect(result.currency).toBe('SAR');
    });

    it('should format for Apple Pay', () => {
      const result = formatForPaymentGateway(testAmount, 'apple_pay');
      expect(result.amount).toBe(100.50);
      expect(result.currency).toBe('SAR');
    });

    it('should format for Mada with Arabic formatting', () => {
      const result = formatForPaymentGateway(testAmount, 'mada');
      expect(result.amount).toBe(100.50);
      expect(result.currency).toBe('SAR');
    });

    it('should format for STC Pay with Arabic formatting', () => {
      const result = formatForPaymentGateway(testAmount, 'stc');
      expect(result.amount).toBe(100.50);
      expect(result.currency).toBe('SAR');
    });
  });

  describe('formatCompactSAR', () => {
    it('should format millions', () => {
      expect(formatCompactSAR(2500000)).toBe('2.5M SAR');
      expect(formatCompactSAR(2500000, true)).toBe('2.5م.ر.س');
    });

    it('should format thousands', () => {
      expect(formatCompactSAR(2500)).toBe('2.5K SAR');
      expect(formatCompactSAR(2500, true)).toBe('2.5ألف ر.س');
    });

    it('should format smaller amounts normally', () => {
      const result = formatCompactSAR(500);
      expect(result).toContain('500');
    });

    it('should handle exact millions', () => {
      expect(formatCompactSAR(1000000)).toBe('1.0M SAR');
    });

    it('should handle exact thousands', () => {
      expect(formatCompactSAR(1000)).toBe('1.0K SAR');
    });
  });

  describe('Edge cases and error handling', () => {
    it('should handle very large numbers', () => {
      const largeNumber = 999999999.99;
      const result = formatSAR(largeNumber);
      expect(result.amount).toContain('999,999,999.99');
    });

    it('should handle very small decimal numbers', () => {
      const smallNumber = 0.01;
      const result = formatSAR(smallNumber);
      expect(result.amount).toBe('0.01');
    });

    it('should handle floating point precision', () => {
      const result = formatSAR(0.1 + 0.2);
      expect(result.amount).toBe('0.30');
    });

    it('should handle conversion edge cases', () => {
      expect(convertUSDToSAR(0.01)).toBe(0.04);
      expect(convertSARToUSD(0.01)).toBe(0);
    });
  });
});