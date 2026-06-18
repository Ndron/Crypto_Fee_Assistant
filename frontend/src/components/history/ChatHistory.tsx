import { useState, useMemo } from "react";
import { Search, Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { ChatSession } from "@/types/chat";
import { format, isToday, isYesterday, subDays, isAfter } from "date-fns";

interface ChatHistoryProps {
  sessions: ChatSession[];
  currentSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
  onDeleteSession: (id: string) => void;
}

const ChatHistory = ({
  sessions,
  currentSessionId,
  onSelectSession,
  onNewChat,
  onDeleteSession,
}: ChatHistoryProps) => {
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    if (!search.trim()) return sessions;
    const q = search.toLowerCase();
    return sessions.filter(
      (s) =>
        s.title.toLowerCase().includes(q) ||
        s.messages?.some((m) => m.content.toLowerCase().includes(q))
    );
  }, [sessions, search]);

  const grouped = useMemo(() => {
    const groups: Record<string, ChatSession[]> = {};
    for (const session of filtered) {
      const date = new Date(session.updated_at || session.created_at);
      let label: string;
      if (isToday(date)) label = "Today";
      else if (isYesterday(date)) label = "Yesterday";
      else if (isAfter(date, subDays(new Date(), 7))) label = "This Week";
      else label = "Older";
      if (!groups[label]) groups[label] = [];
      groups[label].push(session);
    }
    return groups;
  }, [filtered]);

  return (
    <div className="flex flex-col h-full">
      <div className="p-3 space-y-2">
        <Button onClick={onNewChat} className="w-full" size="sm">
          <Plus className="h-4 w-4 mr-2" /> New Chat
        </Button>
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search chats..."
            className="pl-8 h-8 text-xs"
          />
        </div>
      </div>
      <div className="flex-1 overflow-y-auto scrollbar-thin px-2">
        {Object.entries(grouped).map(([label, items]) => (
          <div key={label} className="mb-2">
            <div className="px-2 py-1 text-xs font-medium text-muted-foreground uppercase">
              {label}
            </div>
            {items.map((session) => (
              <div
                key={session.id}
                onClick={() => onSelectSession(session.id)}
                className={`group flex items-center justify-between px-2 py-1.5 rounded-md cursor-pointer text-sm hover:bg-sidebar-hover ${
                  currentSessionId === session.id
                    ? "bg-sidebar-hover text-foreground"
                    : "text-sidebar-foreground"
                }`}
              >
                <span className="truncate flex-1">{session.title || "New Chat"}</span>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-5 w-5 opacity-0 group-hover:opacity-100 shrink-0"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(session.id);
                  }}
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            ))}
          </div>
        ))}
        {filtered.length === 0 && (
          <p className="text-xs text-muted-foreground text-center py-4">No chats found</p>
        )}
      </div>
    </div>
  );
};

export default ChatHistory;
