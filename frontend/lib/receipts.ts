import API from './api';

export interface ReceiptItem {
  name: string;
  quantity: number;
  price: number;
  total: number;
}

export interface ReceiptData {
  items: ReceiptItem[];
  total: number;
  date: string;
  store: string;
  source: string;
}

export interface UploadResponse {
  success: boolean;
  transaction_id: string;
  result: ReceiptData;
  error?: string;
}

export const receiptsAPI = {
  // Upload receipt image for OCR processing
  uploadReceipt: async (file: File, source: string = 'image'): Promise<UploadResponse> => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('source', source);

      const response = await API.post('/api/v1/upload_receipt', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error: any) {
      return {
        success: false,
        transaction_id: '',
        result: { items: [], total: 0, date: '', store: '', source: '' },
        error: error.response?.data?.detail || 'Upload failed',
      };
    }
  },

  // Get user's transaction history
  getTransactions: async (limit: number = 50, offset: number = 0) => {
    try {
      const response = await API.get(`/api/v1/transactions?limit=${limit}&offset=${offset}`);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        transactions: [],
        error: error.response?.data?.detail || 'Failed to fetch transactions',
      };
    }
  },

  // Get specific transaction by ID
  getTransaction: async (transactionId: string) => {
    try {
      const response = await API.get(`/api/v1/transactions/${transactionId}`);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        transaction: null,
        error: error.response?.data?.detail || 'Failed to fetch transaction',
      };
    }
  },

  // Delete transaction
  deleteTransaction: async (transactionId: string) => {
    try {
      const response = await API.delete(`/api/v1/transactions/${transactionId}`);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to delete transaction',
      };
    }
  },
};
