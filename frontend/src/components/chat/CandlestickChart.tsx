import { useEffect, useRef } from "react";
import { createChart, type IChartApi, ColorType, CandlestickSeries, HistogramSeries } from "lightweight-charts";
import type { ChartData } from "@/types/chat";

interface Props {
  chart: ChartData;
}

const CandlestickChart = ({ chart }: Props) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!containerRef.current || !chart.candles?.length) return;

    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
    }

    const container = containerRef.current;
    const height = 400;

    const ch = createChart(container, {
      layout: {
        background: { type: ColorType.Solid, color: "#1a1a2e" },
        textColor: "#a0a0b0",
      },
      grid: {
        vertLines: { color: "#2a2a3e" },
        horzLines: { color: "#2a2a3e" },
      },
      width: container.clientWidth,
      height,
      timeScale: {
        borderColor: "#3a3a4e",
        timeVisible: true,
        secondsVisible: false,
      },
      rightPriceScale: {
        borderColor: "#3a3a4e",
      },
      crosshair: {
        vertLine: { color: "#f59e0b", width: 1, style: 2 },
        horzLine: { color: "#f59e0b", width: 1, style: 2 },
      },
    });

    chartRef.current = ch;

    const candleSeries = ch.addSeries(CandlestickSeries, {
      upColor: "#22c55e",
      downColor: "#ef4444",
      borderUpColor: "#22c55e",
      borderDownColor: "#ef4444",
      wickUpColor: "#22c55e",
      wickDownColor: "#ef4444",
    });

    candleSeries.setData(
      chart.candles.map((c) => ({
        time: c.time as any,
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
      }))
    );

    const volumeSeries = ch.addSeries(HistogramSeries, {
      priceFormat: { type: "volume" },
      priceScaleId: "volume",
    });

    volumeSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });

    volumeSeries.setData(
      chart.candles.map((c) => ({
        time: c.time as any,
        value: c.volume,
        color: c.close >= c.open ? "rgba(34,197,94,0.3)" : "rgba(239,68,68,0.3)",
      }))
    );

    ch.timeScale().fitContent();

    const handleResize = () => {
      if (containerRef.current && chartRef.current) {
        chartRef.current.applyOptions({ width: containerRef.current.clientWidth });
      }
    };

    const observer = new ResizeObserver(handleResize);
    observer.observe(container);

    return () => {
      observer.disconnect();
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [chart]);

  const intervalLabel: Record<string, string> = {
    "1m": "1 min",
    "3m": "3 min",
    "5m": "5 min",
    "15m": "15 min",
    "30m": "30 min",
    "1h": "1 hour",
    "2h": "2 hours",
    "4h": "4 hours",
    "6h": "6 hours",
    "8h": "8 hours",
    "12h": "12 hours",
    "1d": "1 day",
    "3d": "3 days",
    "1w": "1 week",
    "1M": "1 month",
  };

  return (
    <div className="rounded-lg border border-amber-500/20 overflow-hidden my-2">
      <div className="flex items-center gap-2 px-3 py-2 bg-amber-500/10 border-b border-amber-500/20">
        <span className="text-amber-400 font-bold text-sm">{chart.symbol}</span>
        <span className="text-xs text-muted-foreground">
          {intervalLabel[chart.interval] || chart.interval}
        </span>
        {chart.is_futures && (
          <span className="text-xs bg-orange-500/20 text-orange-400 px-1.5 py-0.5 rounded">
            Futures
          </span>
        )}
        <span className="text-xs text-muted-foreground ml-auto">
          {chart.count} candles
        </span>
      </div>
      <div ref={containerRef} />
    </div>
  );
};

export default CandlestickChart;
