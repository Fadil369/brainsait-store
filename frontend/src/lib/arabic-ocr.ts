/**
 * Arabic OCR for Invoices and Batch Tracking
 * Extracts text from images containing Arabic text
 */

export interface OCRResult {
  text: string;
  confidence: number;
  language: string;
  blocks: OCRBlock[];
}

export interface OCRBlock {
  text: string;
  confidence: number;
  boundingBox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

export interface InvoiceData {
  invoiceNumber?: string;
  date?: string;
  total?: number;
  vat?: number;
  vendor?: string;
  items?: InvoiceItem[];
}

export interface InvoiceItem {
  description: string;
  quantity: number;
  unitPrice: number;
  total: number;
}

/**
 * Arabic OCR Handler
 */
export class ArabicOCRHandler {
  private apiKey: string | null = null;

  constructor(apiKey?: string) {
    this.apiKey = apiKey || null;
  }

  /**
   * Process image and extract text
   */
  async extractText(
    imageFile: File | string,
    language: 'ar' | 'en' | 'auto' = 'auto'
  ): Promise<OCRResult> {
    try {
      // In production, this would call an OCR API (e.g., Google Vision, Azure Cognitive Services, or Tesseract.js)
      // For now, we return a mock result
      console.log('Processing OCR for:', imageFile, 'Language:', language);

      // Mock OCR result
      return {
        text: 'Sample extracted text / نص عينة مستخرج',
        confidence: 0.95,
        language: language === 'auto' ? 'ar' : language,
        blocks: [
          {
            text: 'Sample text',
            confidence: 0.95,
            boundingBox: { x: 0, y: 0, width: 100, height: 50 },
          },
        ],
      };
    } catch (error) {
      console.error('OCR extraction failed:', error);
      throw new Error('Failed to extract text from image');
    }
  }

  /**
   * Extract invoice data from image
   */
  async extractInvoiceData(imageFile: File | string): Promise<InvoiceData> {
    try {
      const ocrResult = await this.extractText(imageFile, 'ar');
      return this.parseInvoiceText(ocrResult.text);
    } catch (error) {
      console.error('Invoice extraction failed:', error);
      throw new Error('Failed to extract invoice data');
    }
  }

  /**
   * Parse extracted text to extract invoice fields
   */
  private parseInvoiceText(text: string): InvoiceData {
    const invoiceData: InvoiceData = {};

    // Extract invoice number (English and Arabic patterns)
    const invoiceNumberPatterns = [
      /invoice\s*#?\s*[:\-]?\s*(\d+)/i,
      /رقم\s*الفاتورة\s*[:\-]?\s*(\d+)/i,
      /فاتورة\s*رقم\s*(\d+)/i,
    ];

    for (const pattern of invoiceNumberPatterns) {
      const match = text.match(pattern);
      if (match) {
        invoiceData.invoiceNumber = match[1];
        break;
      }
    }

    // Extract total amount
    const totalPatterns = [
      /total\s*[:\-]?\s*(\d+(?:\.\d{2})?)/i,
      /المجموع\s*[:\-]?\s*(\d+(?:\.\d{2})?)/i,
      /الإجمالي\s*[:\-]?\s*(\d+(?:\.\d{2})?)/i,
    ];

    for (const pattern of totalPatterns) {
      const match = text.match(pattern);
      if (match) {
        invoiceData.total = parseFloat(match[1]);
        break;
      }
    }

    // Extract VAT
    const vatPatterns = [
      /vat\s*[:\-]?\s*(\d+(?:\.\d{2})?)/i,
      /ضريبة\s*[:\-]?\s*(\d+(?:\.\d{2})?)/i,
      /القيمة\s*المضافة\s*[:\-]?\s*(\d+(?:\.\d{2})?)/i,
    ];

    for (const pattern of vatPatterns) {
      const match = text.match(pattern);
      if (match) {
        invoiceData.vat = parseFloat(match[1]);
        break;
      }
    }

    // Extract date (simplified)
    const datePatterns = [
      /date\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})/i,
      /التاريخ\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})/i,
    ];

    for (const pattern of datePatterns) {
      const match = text.match(pattern);
      if (match) {
        invoiceData.date = match[1];
        break;
      }
    }

    return invoiceData;
  }

  /**
   * Extract batch tracking information
   */
  async extractBatchInfo(imageFile: File | string): Promise<{
    batchNumber?: string;
    productCode?: string;
    expiryDate?: string;
    manufacturingDate?: string;
  }> {
    try {
      const ocrResult = await this.extractText(imageFile, 'ar');
      const text = ocrResult.text;

      return {
        batchNumber: this.extractPattern(text, [
          /batch\s*#?\s*[:\-]?\s*([A-Z0-9]+)/i,
          /دفعة\s*رقم\s*([A-Z0-9]+)/i,
        ]),
        productCode: this.extractPattern(text, [
          /product\s*code\s*[:\-]?\s*([A-Z0-9\-]+)/i,
          /رمز\s*المنتج\s*[:\-]?\s*([A-Z0-9\-]+)/i,
        ]),
        expiryDate: this.extractPattern(text, [
          /exp(?:iry)?\s*date?\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})/i,
          /تاريخ\s*الانتهاء\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})/i,
        ]),
        manufacturingDate: this.extractPattern(text, [
          /mfg\s*date?\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})/i,
          /تاريخ\s*الإنتاج\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})/i,
        ]),
      };
    } catch (error) {
      console.error('Batch info extraction failed:', error);
      throw new Error('Failed to extract batch information');
    }
  }

  /**
   * Helper to extract pattern from text
   */
  private extractPattern(text: string, patterns: RegExp[]): string | undefined {
    for (const pattern of patterns) {
      const match = text.match(pattern);
      if (match) {
        return match[1];
      }
    }
    return undefined;
  }

  /**
   * Validate Arabic text detection
   */
  isArabicText(text: string): boolean {
    // Check if text contains Arabic characters
    return /[\u0600-\u06FF]/.test(text);
  }

  /**
   * Get text direction from detected language
   */
  getTextDirection(text: string): 'rtl' | 'ltr' {
    return this.isArabicText(text) ? 'rtl' : 'ltr';
  }
}

/**
 * Singleton instance
 */
export const arabicOCR = new ArabicOCRHandler();

/**
 * Helper function to process invoice
 */
export async function processInvoice(imageFile: File): Promise<InvoiceData> {
  return arabicOCR.extractInvoiceData(imageFile);
}

/**
 * Helper function to process batch label
 */
export async function processBatchLabel(imageFile: File): Promise<{
  batchNumber?: string;
  productCode?: string;
  expiryDate?: string;
  manufacturingDate?: string;
}> {
  return arabicOCR.extractBatchInfo(imageFile);
}

export default ArabicOCRHandler;
