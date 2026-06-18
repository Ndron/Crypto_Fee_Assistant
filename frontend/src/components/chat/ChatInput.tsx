import { useState, useRef, KeyboardEvent } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import ModelSelector from "./ModelSelector";
import type { ModelConfig } from "@/types/models";
import type { McpServerConfig } from "@/types/mcp-servers";

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
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

const ChatInput = ({
  onSend,
  isLoading,
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
}: ChatInputProps) => {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    const textarea = e.target;
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + "px";
  };

  return (
    <div className="border-t border-border p-4">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-end gap-2">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder="Ask about crypto fees, breakeven, order book..."
            rows={1}
            className="flex-1 resize-none rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring scrollbar-thin"
            disabled={isLoading}
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            size="icon"
            className="shrink-0"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <div className="mt-2">
          <ModelSelector
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
      </div>
    </div>
  );
};

export default ChatInput;
