export interface McpServerConfig {
  server_id: string;
  name: string;
  url: string;
  has_api_key: boolean;
  created_at: string;
  status?: "online" | "offline" | "unknown";
  tools_count?: number;
}

export interface McpServerCreateRequest {
  name: string;
  url: string;
  api_key?: string;
}
