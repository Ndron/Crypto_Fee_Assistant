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

interface AddModelModalProps {
  open: boolean;
  onClose: () => void;
  onAdd: (data: { name: string; endpoint_url: string; api_key: string }) => void;
}

const AddModelModal = ({ open, onClose, onAdd }: AddModelModalProps) => {
  const [name, setName] = useState("");
  const [endpointUrl, setEndpointUrl] = useState("");
  const [apiKey, setApiKey] = useState("ollama");
  const [error, setError] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!name.trim() || !endpointUrl.trim()) {
      setError("Name and endpoint URL are required");
      return;
    }

    try {
      new URL(endpointUrl);
    } catch {
      setError("Invalid endpoint URL");
      return;
    }

    onAdd({ name: name.trim(), endpoint_url: endpointUrl.trim(), api_key: apiKey.trim() });
    setName("");
    setEndpointUrl("");
    setApiKey("ollama");
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add Model</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="model-name">Name</Label>
            <Input
              id="model-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Llama 3.1"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="model-endpoint">Endpoint URL</Label>
            <Input
              id="model-endpoint"
              value={endpointUrl}
              onChange={(e) => setEndpointUrl(e.target.value)}
              placeholder="http://ollama:11434/v1"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="model-api-key">API Key</Label>
            <Input
              id="model-api-key"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="ollama"
            />
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit">Add Model</Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default AddModelModal;
