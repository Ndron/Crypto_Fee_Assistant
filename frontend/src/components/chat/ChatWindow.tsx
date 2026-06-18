import { useRef, useEffect } from "react";
import type { ChatMessage as ChatMessageType } from "@/types/chat";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import WelcomeMessage from "./WelcomeMessage";
import type { ModelConfig } from "@/types/models";
import type { McpServerConfig } from "@/types/mcp-servers";

interface ChatWindowProps {
  messages: ChatMessageType[];
  isLoading: boolean;
  onSend: (message: string) => void;
  models: ModelConfig[];
  mcpServers: McpServerConfig[];
  selectedModelId: string;
  onModelSelect: (id: string) => void;
  onAddModel: (data: { name: string; endpoint_url: string; api_key: string }) => void;
  onDeleteModel: (id: string) => void;
  onAddMcpServer: (data: { name: string; url: string; api_key?: string }) => void;
  onDeleteMcpServer: (id: string) => void;
  onTestMcpServer: (id: string) => void;
  tokenPercent: number;
}

const ChatWindow = ({
  messages,
  isLoading,
  onSend,
  models,
  mcpServers,
  selectedModelId,
  onModelSelect,
  onAddModel,
  onDeleteModel,
  onAddMcpServer,
  onDeleteMcpServer,
  onTestMcpServer,
  tokenPercent,
}: ChatWindowProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const hasMessages = messages.some((m) => m.role === "user");

  return (
    <div className="flex flex-col h-full min-h-0">
      <div className="flex-1 overflow-y-auto scrollbar-thin min-h-0">
        {!hasMessages ? (
          <WelcomeMessage />
        ) : (
          <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex items-center gap-1 pl-4 text-muted-foreground">
                <div className="w-2 h-2 rounded-full bg-current animate-bounce [animation-delay:-0.3s]" />
                <div className="w-2 h-2 rounded-full bg-current animate-bounce [animation-delay:-0.15s]" />
                <div className="w-2 h-2 rounded-full bg-current animate-bounce" />
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      <ChatInput
        onSend={onSend}
        isLoading={isLoading}
        models={models}
        mcpServers={mcpServers}
        selectedModelId={selectedModelId}
        onModelSelect={onModelSelect}
        onAddModel={onAddModel}
        onDeleteModel={onDeleteModel}
        onAddMcpServer={onAddMcpServer}
        onDeleteMcpServer={onDeleteMcpServer}
        onTestMcpServer={onTestMcpServer}
        tokenPercent={tokenPercent}
      />
    </div>
  );
};

export default ChatWindow;
