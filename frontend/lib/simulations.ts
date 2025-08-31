import API from './api';

export interface SimulationParameters {
  scenario: string;
  item: string;
  change: string;
  quantity?: number;
  current_price?: number;
}

export interface SimulationResult {
  scenario: string;
  item: string;
  change: string;
  before: {
    revenue: number;
    profit: number;
    quantity: number;
    price: number;
  };
  after: {
    revenue: number;
    profit: number;
    quantity: number;
    price: number;
  };
  impact: {
    revenue_change: number;
    profit_change: number;
    percentage_change: number;
  };
  recommendations: string[];
  assumptions: string[];
  confidence: number;
  gpt_response?: any;
  gemini_response?: any;
  arbitration_result?: any;
}

export interface SimulationResponse {
  success: boolean;
  simulation_id: string;
  query: string;
  result: SimulationResult;
  error?: string;
}

export const simulationsAPI = {
  // Run business simulation
  runSimulation: async (query: string): Promise<SimulationResponse> => {
    try {
      const response = await API.post('/api/v1/simulate', { query });
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        simulation_id: '',
        query,
        result: {} as SimulationResult,
        error: error.response?.data?.detail || 'Simulation failed',
      };
    }
  },

  // Get user's simulation history
  getSimulations: async (limit: number = 50, offset: number = 0) => {
    try {
      const response = await API.get(`/api/v1/simulations?limit=${limit}&offset=${offset}`);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        simulations: [],
        error: error.response?.data?.detail || 'Failed to fetch simulations',
      };
    }
  },

  // Get specific simulation by ID
  getSimulation: async (simulationId: string) => {
    try {
      const response = await API.get(`/api/v1/simulations/${simulationId}`);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        simulation: null,
        error: error.response?.data?.detail || 'Failed to fetch simulation',
      };
    }
  },

  // Get available simulation scenarios
  getAvailableScenarios: async () => {
    try {
      const response = await API.get('/api/v1/simulations/scenarios');
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        scenarios: [],
        error: error.response?.data?.detail || 'Failed to fetch scenarios',
      };
    }
  },

  // Delete simulation
  deleteSimulation: async (simulationId: string) => {
    try {
      const response = await API.delete(`/api/v1/simulations/${simulationId}`);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to delete simulation',
      };
    }
  },
};
