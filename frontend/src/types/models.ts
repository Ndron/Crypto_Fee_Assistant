export interface ModelConfig {
  model_id: string;
  name: string;
  endpoint_url: string;
  is_default: boolean;
  created_at: string;
}

export interface ModelCreateRequest {
  name: string;
  endpoint_url: string;
  api_key: string;
}
