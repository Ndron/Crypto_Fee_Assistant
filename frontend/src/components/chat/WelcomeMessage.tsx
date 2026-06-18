interface WelcomeMessageProps {
  onSuggestionClick?: (text: string) => void;
}

const suggestions = [
  "What are the trading fees on Binance?",
  "Calculate breakeven move for BTC/USDT",
  "Show order book imbalance for ETH",
  "What's the current funding rate?",
];

const WelcomeMessage = ({ onSuggestionClick }: WelcomeMessageProps) => {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-6 px-4">
      <div className="w-16 h-16 rounded-full bg-amber-500/20 flex items-center justify-center">
        <span className="text-amber-400 text-3xl font-bold">₿</span>
      </div>
      <div className="text-center space-y-2">
        <h1 className="text-2xl font-bold gradient-text">Crypto Assistant</h1>
        <p className="text-muted-foreground text-sm">
          Your local AI-powered crypto trading analysis tool
        </p>
      </div>
      <div className="flex flex-wrap justify-center gap-2 max-w-md">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => onSuggestionClick?.(suggestion)}
            className="text-xs px-3 py-1.5 rounded-full border border-border hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
};

export default WelcomeMessage;
