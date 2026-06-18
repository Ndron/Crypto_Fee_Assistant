import { useState } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Plus, Trash2, Server, Wifi, WifiOff } from "lucide-react";
import AddModelModal from "./AddModelModal";
import AddMcpServerModal from "./AddMcpServerModal";
import type { ModelConfig } from "@/types/models";
import type { McpServerConfig } from "@/types/mcp-servers";

interface ModelSelectorProps {
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

const ModelSelector = ({
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
}: ModelSelectorProps) => {
  const [showAddModel, setShowAddModel] = useState(false);
  const [showAddMcpServer, setShowAddMcpServer] = useState(false);

  return (
    <div className="flex items-center gap-2 flex-wrap">
      <Select value={selectedModelId} onValueChange={onModelSelect}>
        <SelectTrigger className="w-[200px] h-8 text-xs">
          <SelectValue placeholder="Select model" />
        </SelectTrigger>
        <SelectContent>
          {models.map((model) => (
            <SelectItem key={model.model_id} value={model.model_id}>
              {model.name}
              {model.is_default && " (default)"}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <div className="h-4 w-px bg-border" />

      {mcpServers.map((server) => (
        <div key={server.server_id} className="flex items-center gap-1">
          {server.status === "online" ? (
            <Wifi className="h-3 w-3 text-green-500" />
          ) : (
            <WifiOff className="h-3 w-3 text-red-500" />
          )}
          <span className="text-xs text-muted-foreground">
            {server.name} ({server.tools_count ?? "?"} tools)
          </span>
          <Button
            variant="ghost"
            size="icon"
            className="h-5 w-5"
            onClick={() => onDeleteMcpServer(server.server_id)}
          >
            <Trash2 className="h-3 w-3" />
          </Button>
        </div>
      ))}

      <Button
        variant="ghost"
        size="sm"
        className="h-6 text-xs"
        onClick={() => setShowAddModel(true)}
      >
        <Plus className="h-3 w-3 mr-1" /> Model
      </Button>

      <Button
        variant="ghost"
        size="sm"
        className="h-6 text-xs"
        onClick={() => setShowAddMcpServer(true)}
      >
        <Server className="h-3 w-3 mr-1" /> MCP Server
      </Button>

      {tokenPercent > 0 && (
        <span className="text-xs text-muted-foreground ml-auto">
          Context: {tokenPercent.toFixed(0)}%
        </span>
      )}

      <AddModelModal
        open={showAddModel}
        onClose={() => setShowAddModel(false)}
        onAdd={onAddModel}
      />
      <AddMcpServerModal
        open={showAddMcpServer}
        onClose={() => setShowAddMcpServer(false)}
        onAdd={onAddMcpServer}
      />
    </div>
  );
};

export default ModelSelector;
