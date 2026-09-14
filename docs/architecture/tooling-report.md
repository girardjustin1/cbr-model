# Backtest Tooling Report (Trader.dev MCP and alternatives)

Checked 2026-09-14. Every claim below was verified by a live call or by reading the tool's own
documentation/source; nothing is assumed from memory.

## Trader.dev MCP: NOT AVAILABLE (server-side outage)

| Check | Result |
|---|---|
| Config | Project-scoped `.mcp.json` → `trader-dev`, HTTP `https://mcp.trader.dev/mcp`, `Authorization: Bearer <key>`. File is gitignored (`git check-ignore` confirmed). |
| Reachability | First attempt: Cloudflare **403 (error 1010)**, blocked by client signature. With a standard client user-agent: request reaches origin. |
| MCP `initialize` | **HTTP 502 Bad Gateway**, 3 of 3 retries (Cloudflare → origin failure). `trader.dev` website returns 200. |
| Key validity | **Unknown.** The origin fails before authentication. |
| Tools | **Not discoverable** until `initialize` succeeds. No tool names are assumed. |
| Retry (later, 2026-09-14) | Still **502** on every variant: POST `/mcp` with and without key, `/mcp/`, GET `/mcp` and `/sse` (SSE), GET `/` and `/.well-known/oauth-protected-resource`. The whole `mcp.trader.dev` origin is failing, independent of path, method or credentials, so it isn't a client configuration problem. |
| Action items | Retry before Phase 14. **Rotate the API key** once connected: it appeared in the assistant's context through a file-change notification. |

## Alternatives evaluated

| Tool | What it actually is | Runs custom Pine strategies? | Bulk XAUUSD/DXY history? | Verdict |
|---|---|---|---|---|
| **PineTS** (`QuantForgeOrg/PineTS`, AGPL-3.0; used by LuxAlgo `Vela-pinets`) | Open-source Pine Script transpiler/runtime for Node.js | **Yes**: README: runs `indicator()` and `strategy()` with a broker emulator emitting order fills; `request.security()` supported | n/a (bring your own bars) | **Proposed primary Pine runner** (local, no vendor dependency). Must pass a TradingView parity gate; strategy-API coverage is partial (check against scripts). |
| **LuxAlgo MCP** (`https://mcp.luxalgo.com/mcp`, v1.4.1, 42 tools; verified live) | Library, prop-firm directory + Monte Carlo challenge simulator, market trackers, Edge Stats, user journal | No | No: Edge Stats covers BTCUSDT/ETHUSDT only; "no raw vendor bars are published" | Optional later: `propfirms_simulate_trades` on out-of-sample R-series; journal tools for Phase 29 |
| **LuxAlgo Quant** (app.luxalgo.com/quant) | AI strategy builder with backtests | Generates its own strategies | Its own data | **Secondary channel** only if its generated code is audited against the machine spec and full trade lists are exported |
| **LuxAlgo edge-stats** | Session-statistics engine with data adapters | No | Dukascopy / Databento / CSV adapters (1m) | Reference implementation for data adapters |
| `atilaahmettaner/tradingview-mcp` | Unofficial TA/screener MCP (public endpoints, Yahoo) | No: 9 built-in strategies, 1d/1h | No bulk bars | Not useful |
| `tradesdontlie/tradingview-mcp` | Drives your logged-in TradingView Desktop | Via your TradingView UI | Plan-limited | Possible fallback; unofficial, drives your account, ToS review required |
| FX Replay | Manual chart-replay backtesting (5s candles on Pro) | No (FXR Script indicators) | In-app only | Optional manual parity checks |
| Unusual Whales API | Options flow / dark pool / equities data | No | Not listed | Not useful |
| TradingView Strategy Tester | Native Pine backtests | Yes | Plan-limited bars | **Parity reference** for PineTS; manual export of trade list |

## Recommendation

1. **Python reference engine is the source of truth** for signals and trades (tick-built 5s + 1m, UTC).
2. **Pine strategies run locally through PineTS** for automated sweeps. Before any PineTS result is trusted, the
   same script on the same bars must reproduce TradingView Strategy Tester trades (entry/exit time and price
   within one tick) on a fixed parity window.
3. **Trader.dev** remains an option once its server works; it gets the same parity gate.
4. **LuxAlgo Quant** results are accepted only with audited code and full trade lists.
