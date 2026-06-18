import { useState, useCallback, useEffect } from "react";
import type { ModelConfig, ModelCreateRequest } from "@/types/models";

const API_BASE = "/api";
const STORAGE_KEY = "crypto_assistant_selected_model";

export function useModels() {
  const [models, setModels] = useState<ModelConfig[]>([]);
  const [selectedModelId, setSelectedModelId] = useState<string>(() => {
    return localStorage.getItem(STORAGE_KEY) || "";
  });

  const loadModels = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/models`);
      if (res.ok) {
        const data = await res.json();
        setModels(data);
        if (!selectedModelId && data.length > 0) {
          const defaultModel = data.find((m: ModelConfig) => m.is_default) || data[0];
          setSelectedModelId(defaultModel.model_id);
        }
      }
    } catch (err) {
      console.error("Failed to load models:", err);
    }
  }, [selectedModelId]);

  const addModel = useCallback(async (request: ModelCreateRequest) => {
    const res = await fetch(`${API_BASE}/models`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || "Failed to add model");
    }
    const newModel = await res.json();
    await loadModels();
    return newModel;
  }, [loadModels]);

  const deleteModel = useCallback(async (modelId: string) => {
    await fetch(`${API_BASE}/models/${modelId}`, { method: "DELETE" });
    if (selectedModelId === modelId) {
      setSelectedModelId("");
    }
    await loadModels();
  }, [loadModels, selectedModelId]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, selectedModelId);
  }, [selectedModelId]);

  return {
    models,
    selectedModelId,
    setSelectedModelId,
    loadModels,
    addModel,
    deleteModel,
  };
}
