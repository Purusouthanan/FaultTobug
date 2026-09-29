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

export interface SuiteExecution {
  id: number;
  total_tests: number;
  passed_tests: number;
  failed_tests: number;
  execution_time?: number;
  logs?: string;
  created_at: string;
}

export interface Test {
  id: number;
  incident_id: number;
  test_code: string;
  registered_at?: string;
  created_at?: string;
}

export interface SandboxStatus {
  mode: string;
  ast_scanning: string;
  timeout_seconds: number;
  secret_sanitization: string;
}

export interface MetricsSummary {
  total_incidents: number;
  status_counts: {
    open: number;
    analyzed: number;
    reproduced: number;
    generated: number;
    executed: number;
  };
  manual_triage_time_per_incident_mins: number;
  automated_conversion_avg_seconds: number;
  speedup_multiplier: number;
  total_engineer_hours_saved: number;
  prototype_conversion_rate: number;
  baseline_conversion_rate: number;
  registered_regression_tests: number;
  rbac_roles_supported: string[];
  rbac_matrix_coverage_pct: number;
  sandbox_status: SandboxStatus;
}
