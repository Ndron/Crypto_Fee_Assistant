import { useState, useCallback } from "react";
import type { McpServerConfig, McpServerCreateRequest } from "@/types/mcp-servers";

const API_BASE = "/api";
const MAX_SERVERS = 5;

export function useMcpServers() {
  const [servers, setServers] = useState<McpServerConfig[]>([]);

  const loadServers = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/mcp-servers`);
      if (res.ok) {
        const data = await res.json();
        setServers(data);
      }
    } catch (err) {
      console.error("Failed to load MCP servers:", err);
    }
  }, []);

  const addServer = useCallback(async (request: McpServerCreateRequest) => {
    if (servers.length >= MAX_SERVERS) {
      throw new Error(`Maximum ${MAX_SERVERS} MCP servers allowed`);
    }
    const res = await fetch(`${API_BASE}/mcp-servers`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || "Failed to add MCP server");
    }
    const newServer = await res.json();
    await loadServers();
    return newServer;
  }, [loadServers, servers.length]);

  const deleteServer = useCallback(async (serverId: string) => {
    await fetch(`${API_BASE}/mcp-servers/${serverId}`, { method: "DELETE" });
    await loadServers();
  }, [loadServers]);

  const testServer = useCallback(async (serverId: string) => {
    const res = await fetch(`${API_BASE}/mcp-servers/${serverId}/test`, { method: "POST" });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || "Server test failed");
    }
    return res.json();
  }, []);

  return {
    servers,
    loadServers,
    addServer,
    deleteServer,
    testServer,
  };
}
