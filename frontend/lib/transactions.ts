import API from './api';

export interface Transaction {
  id: string;
  user_id: string;
  raw_input: string;
  parsed_json: any;
  source: string;
  created_at: string;
  updated_at: string;
}

export interface TransactionsResponse {
  success: boolean;
  transactions: Transaction[];
  total: number;
  limit: number;
  offset: number;
  error?: string;
}

export interface TransactionFilters {
  start_date?: string;
  end_date?: string;
  source?: string;
  limit?: number;
  offset?: number;
}

export const transactionsAPI = {
  // Get user's transaction history with optional filters
  getTransactions: async (filters: TransactionFilters = {}): Promise<TransactionsResponse> => {
    try {
      const params = new URLSearchParams();
      
      if (filters.start_date) params.append('start_date', filters.start_date);
      if (filters.end_date) params.append('end_date', filters.end_date);
      if (filters.source) params.append('source', filters.source);
      if (filters.limit) params.append('limit', filters.limit.toString());
      if (filters.offset) params.append('offset', filters.offset.toString());

      const response = await API.get(`/api/v1/transactions?${params.toString()}`);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        transactions: [],
        total: 0,
        limit: 0,
        offset: 0,
        error: error.response?.data?.detail || 'Failed to fetch transactions',
      };
    }
  },

  // Get transactions for last 7 days
  getRecentTransactions: async (days: number = 7) => {
    const endDate = new Date().toISOString().split('T')[0];
    const startDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    return transactionsAPI.getTransactions({
      start_date: startDate,
      end_date: endDate,
      limit: 100,
    });
  },

  // Get monthly transactions
  getMonthlyTransactions: async (year: number, month: number) => {
    const startDate = `${year}-${month.toString().padStart(2, '0')}-01`;
    const endDate = new Date(year, month, 0).toISOString().split('T')[0];
    
    return transactionsAPI.getTransactions({
      start_date: startDate,
      end_date: endDate,
      limit: 1000,
    });
  },

  // Get transaction statistics
  getTransactionStats: async () => {
    try {
      const response = await API.get('/api/v1/transactions/stats');
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        stats: {},
        error: error.response?.data?.detail || 'Failed to fetch transaction stats',
      };
    }
  },

  // Export transactions to CSV
  exportTransactionsCSV: async (filters: TransactionFilters = {}) => {
    try {
      const params = new URLSearchParams();
      
      if (filters.start_date) params.append('start_date', filters.start_date);
      if (filters.end_date) params.append('end_date', filters.end_date);
      if (filters.source) params.append('source', filters.source);

      const response = await API.get(`/api/v1/transactions/export?${params.toString()}`, {
        responseType: 'blob',
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `transactions-${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      return { success: true };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Export failed',
      };
    }
  },
};
