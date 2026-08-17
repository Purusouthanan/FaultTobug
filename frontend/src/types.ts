export interface Incident {
  id: number;
  description: string;
  status: string;
  failure_category?: string;
  extracted_role?: string;
  extracted_action?: string;
  extracted_method?: string;
  extracted_endpoint?: string;
  expected_result?: string;
  actual_result?: string;
  reproduction_steps?: string;
  generated_test_code?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Execution {
  id: number;
  incident_id: number;
  execution_time: number;
  status: string;
  logs: string;
  created_at: string;
}
