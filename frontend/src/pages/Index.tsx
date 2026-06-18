import { useState, useEffect } from "react";
import ChatWindow from "@/components/chat/ChatWindow";
import ChatHistory from "@/components/history/ChatHistory";
import TopNavBar from "@/components/nav/TopNavBar";
import { useChat } from "@/hooks/useChat";
import { useModels } from "@/hooks/useModels";
import { useMcpServers } from "@/hooks/useMcpServers";
import { PanelLeftClose, PanelLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

const Index = () => {
  const {
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
  } = useChat();

  const {
    models,
    selectedModelId,
    setSelectedModelId,
    loadModels,
    addModel,
    deleteModel,
  } = useModels();

  const {
    servers: mcpServers,
    loadServers: loadMcpServers,
    addServer: addMcpServer,
    deleteServer: deleteMcpServer,
    testServer: testMcpServer,
  } = useMcpServers();

  const [showHistory, setShowHistory] = useState(true);

  useEffect(() => {
    loadModels();
    loadMcpServers();
  }, [loadModels, loadMcpServers]);

  const handleSend = (message: string) => {
    sendMessage(message, selectedModelId || undefined);
  };

  const handleSuggestionClick = (text: string) => {
    handleSend(text);
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      <TopNavBar />
      <div className="flex flex-1 overflow-hidden">
        {showHistory && (
          <div className="w-64 border-r border-border bg-sidebar flex-shrink-0">
            <ChatHistory
              sessions={sessions}
              currentSessionId={currentSessionId}
              onSelectSession={loadSession}
              onNewChat={createNewChat}
              onDeleteSession={deleteSession}
            />
          </div>
        )}
        <div className="flex-1 flex flex-col min-w-0 min-h-0">
          <div className="flex items-center px-2 py-1 border-b border-border">
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={() => setShowHistory(!showHistory)}
            >
              {showHistory ? (
                <PanelLeftClose className="h-4 w-4" />
              ) : (
                <PanelLeft className="h-4 w-4" />
              )}
            </Button>
          </div>
          <ChatWindow
            messages={messages}
            isLoading={isLoading}
            onSend={handleSend}
            models={models}
            mcpServers={mcpServers}
            selectedModelId={selectedModelId}
            onModelSelect={setSelectedModelId}
            onAddModel={addModel}
            onDeleteModel={deleteModel}
            onAddMcpServer={addMcpServer}
            onDeleteMcpServer={deleteMcpServer}
            onTestMcpServer={testMcpServer}
            tokenPercent={tokenPercent}
          />
        </div>
      </div>
    </div>
  );
};

export default Index;
