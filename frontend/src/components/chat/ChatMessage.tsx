import { User } from "lucide-react";
import type { ChatMessage as ChatMessageType } from "@/types/chat";
import CandlestickChart from "./CandlestickChart";

interface ChatMessageProps {
  message: ChatMessageType;
}

const ChatMessage = ({ message }: ChatMessageProps) => {
  const isUser = message.role === "user";
  const isSystem = message.role === "system" || message.role === "tool";

  if (isSystem) return null;

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="shrink-0 w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center">
          <span className="text-amber-400 text-sm font-bold">₿</span>
        </div>
      )}
      <div
        className={`max-w-[80%] rounded-lg px-4 py-2.5 text-sm overflow-hidden ${
          isUser
            ? "bg-chat-user text-foreground"
            : "bg-chat-assistant text-foreground"
        }`}
      >
        <div className="whitespace-pre-wrap break-words">{message.content}</div>
        {message.charts && message.charts.length > 0 && (
          <div className="mt-3 space-y-2">
            {message.charts.map((chart) => (
              <div key={chart.chart_id} className="w-[500px] max-w-full">
                <CandlestickChart chart={chart} />
              </div>
            ))}
          </div>
        )}
      </div>
      {isUser && (
        <div className="shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
          <User className="h-4 w-4 text-muted-foreground" />
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
