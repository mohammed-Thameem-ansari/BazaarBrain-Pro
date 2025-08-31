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

  // Export transactions to CSV with enhanced data processing
  exportTransactionsCSV: async (filters: TransactionFilters = {}) => {
    try {
      // First get the transactions data
      const transactionsResponse = await transactionsAPI.getTransactions(filters);
      
      if (!transactionsResponse.success || !transactionsResponse.transactions.length) {
        throw new Error('No transactions to export');
      }

      // Import Papa Parse dynamically to avoid SSR issues
      const Papa = (await import('papaparse')).default;

      // Enhanced CSV data with business insights
      const csvData = transactionsResponse.transactions.map((transaction: Transaction) => {
        const items = transaction.parsed_json?.items || [];
        const totalItems = items.reduce((sum: number, item: any) => sum + (item.quantity || 1), 0);
        const avgItemPrice = items.length > 0 ? (transaction.parsed_json?.total || 0) / totalItems : 0;
        
        return {
          Date: new Date(transaction.created_at).toLocaleDateString(),
          Time: new Date(transaction.created_at).toLocaleTimeString(),
          Source: transaction.source,
          Store: transaction.parsed_json?.store_name || 'Unknown',
          TotalItems: totalItems,
          TotalAmount: transaction.parsed_json?.total ? `$${transaction.parsed_json.total.toFixed(2)}` : '$0.00',
          AverageItemPrice: `$${avgItemPrice.toFixed(2)}`,
          Items: items.map((item: any) => `${item.name} (${item.quantity || 1})`).join('; '),
          PaymentMethod: transaction.parsed_json?.payment_method || 'Unknown',
          TaxAmount: transaction.parsed_json?.tax ? `$${transaction.parsed_json.tax.toFixed(2)}` : '$0.00',
          Discount: transaction.parsed_json?.discount ? `$${transaction.parsed_json.discount.toFixed(2)}` : '$0.00',
          RawInput: transaction.raw_input,
          CreatedAt: transaction.created_at,
          UpdatedAt: transaction.updated_at
        };
      });

      // Add summary row
      const summary = {
        Date: 'SUMMARY',
        Time: '',
        Source: '',
        Store: '',
        TotalItems: csvData.reduce((sum, row) => sum + (parseInt(row.TotalItems) || 0), 0),
        TotalAmount: `$${csvData.reduce((sum, row) => sum + parseFloat(row.TotalAmount.replace('$', '') || 0), 0).toFixed(2)}`,
        AverageItemPrice: '',
        Items: '',
        PaymentMethod: '',
        TaxAmount: '',
        Discount: '',
        RawInput: '',
        CreatedAt: '',
        UpdatedAt: ''
      };

      const finalData = [...csvData, summary];
      const csv = Papa.unparse(finalData, {
        header: true,
        delimiter: ',',
        quotes: true,
        quoteStrings: true,
        skipEmptyLines: true
      });

      // Create and download the CSV file
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = window.URL.createObjectURL(blob);
      
      link.setAttribute('href', url);
      link.setAttribute('download', `bazaarbrain_transactions_${new Date().toISOString().split('T')[0]}_${new Date().getTime()}.csv`);
      link.style.visibility = 'hidden';
      
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      return { 
        success: true, 
        message: 'CSV exported successfully', 
        count: csvData.length,
        filename: `bazaarbrain_transactions_${new Date().toISOString().split('T')[0]}_${new Date().getTime()}.csv`
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Export failed',
      };
    }
  },
};
