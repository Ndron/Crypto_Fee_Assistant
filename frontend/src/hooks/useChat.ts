import { useState, useCallback, useEffect, useRef } from "react";
import type { ChatMessage, ChatSession, ChatResponse } from "@/types/chat";

const API_BASE = "/api";

const WELCOME_MESSAGE: ChatMessage = {
  id: "welcome",
  role: "assistant",
  content:
    "Hello! I'm your **Crypto Assistant**. I can help you with:\n\n" +
    "- Calculating trading fees\n- Breakeven price analysis\n- Order book imbalance\n- Funding rate opportunities\n- Exchange comparisons\n\nAsk me anything about crypto trading!",
  timestamp: new Date().toISOString(),
};

export function useChat() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const [isLoading, setIsLoading] = useState(false);
  const [tokenPercent, setTokenPercent] = useState(0);
  const abortRef = useRef<AbortController | null>(null);

  const loadSessions = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/conversations`);
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
      }
    } catch (err) {
      console.error("Failed to load sessions:", err);
    }
  }, []);

  const loadSession = useCallback(async (sessionId: string) => {
    try {
      const res = await fetch(`${API_BASE}/conversations/${sessionId}`);
      if (res.ok) {
        const session: ChatSession = await res.json();
        setMessages(session.messages?.length ? session.messages : [WELCOME_MESSAGE]);
        setCurrentSessionId(sessionId);
      }
    } catch (err) {
      console.error("Failed to load session:", err);
    }
  }, []);

  const sendMessage = useCallback(
    async (content: string, modelId?: string) => {
      if (abortRef.current) {
        abortRef.current.abort();
      }
      const controller = new AbortController();
      abortRef.current = controller;

      setIsLoading(true);
      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);

      try {
        const res = await fetch(`${API_BASE}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: content,
            session_id: currentSessionId || undefined,
            model_id: modelId || undefined,
          }),
          signal: controller.signal,
        });

        if (!res.ok) throw new Error(`Chat request failed: ${res.status}`);

        const data: ChatResponse = await res.json();
        setCurrentSessionId(data.session_id);
        const assistantMsg: ChatMessage = {
          ...data.assistant_message,
          charts: data.charts || undefined,
        };
        setMessages((prev) => [...prev, assistantMsg]);
        setTokenPercent(data.token_percent || 0);
        await loadSessions();
        return data;
      } catch (err: any) {
        if (err.name === "AbortError") return;
        console.error("Failed to send message:", err);
        const errorMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: "Sorry, an error occurred while processing your request. Please try again.",
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, errorMsg]);
      } finally {
        setIsLoading(false);
        abortRef.current = null;
      }
    },
    [currentSessionId, loadSessions]
  );

  const createNewChat = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
    }
    setCurrentSessionId(null);
    setMessages([WELCOME_MESSAGE]);
    setTokenPercent(0);
  }, []);

  const deleteSession = useCallback(
    async (sessionId: string) => {
      try {
        await fetch(`${API_BASE}/conversations/${sessionId}`, { method: "DELETE" });
        if (currentSessionId === sessionId) {
          createNewChat();
        }
        await loadSessions();
      } catch (err) {
        console.error("Failed to delete session:", err);
      }
    },
    [currentSessionId, createNewChat, loadSessions]
  );

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  return {
    sessions,
    currentSessionId,
    messages,
    isLoading,
    tokenPercent,
    loadSessions,
    loadSession,
    sendMessage,
    createNewChat,
    deleteSession,
  };
}
