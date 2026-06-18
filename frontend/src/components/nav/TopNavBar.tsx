import { TrendingUp } from "lucide-react";

const TopNavBar = () => {
  return (
    <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-sidebar">
      <div className="flex items-center gap-2">
        <div className="w-7 h-7 rounded-full bg-amber-500/20 flex items-center justify-center">
          <TrendingUp className="h-4 w-4 text-amber-400" />
        </div>
        <span className="font-semibold text-sm gradient-text">Crypto Assistant</span>
      </div>
      <span className="text-xs text-muted-foreground">Local • Read-only</span>
    </div>
  );
};

export default TopNavBar;
