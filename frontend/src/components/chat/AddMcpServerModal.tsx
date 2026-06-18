import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface AddMcpServerModalProps {
  open: boolean;
  onClose: () => void;
  onAdd: (data: { name: string; url: string; api_key?: string }) => void;
}

const AddMcpServerModal = ({ open, onClose, onAdd }: AddMcpServerModalProps) => {
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState("");

  const normalizeUrl = (value: string): string => {
    let normalized = value.trim();
    if (normalized && !normalized.startsWith("http://") && !normalized.startsWith("https://")) {
      normalized = "http://" + normalized;
    }
    normalized = normalized.replace(/\/sse$/, "");
    return normalized;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!name.trim() || !url.trim()) {
      setError("Name and URL are required");
      return;
    }

    const normalizedUrl = normalizeUrl(url);
    try {
      new URL(normalizedUrl);
    } catch {
      setError("Invalid URL");
      return;
    }

    onAdd({
      name: name.trim(),
      url: normalizedUrl,
      api_key: apiKey.trim() || undefined,
    });
    setName("");
    setUrl("");
    setApiKey("");
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add MCP Server</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="mcp-name">Name</Label>
            <Input
              id="mcp-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Crypto Tools"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="mcp-url">URL</Label>
            <Input
              id="mcp-url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="http://mcp-server:9000"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="mcp-api-key">API Key (optional)</Label>
            <Input
              id="mcp-api-key"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Leave empty if not required"
            />
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit">Add Server</Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default AddMcpServerModal;
