export interface CandleData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface ChartData {
  chart_id: string;
  type: "candlestick";
  symbol: string;
  interval: string;
  is_futures: boolean;
  count: number;
  candles: CandleData[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  timestamp: string;
  charts?: ChartData[];
}

export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  created_at: string;
  updated_at: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  model_id?: string;
}

export interface ChatResponse {
  session_id: string;
  assistant_message: ChatMessage;
  token_percent?: number;
  charts?: ChartData[];
}
