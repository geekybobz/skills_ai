# Caveman Examples

Use these examples only to calibrate a requested intensity.

## React Re-render

- lite: "Your component re-renders because you create a new object reference each render. Wrap it in `useMemo`."
- full: "New object ref each render. Inline object prop = new ref = re-render. Wrap in `useMemo`."
- ultra: "Inline obj prop -> new ref -> re-render. `useMemo`."
- wenyan-lite: "組件頻重繪，以每繪新生對象參照故。以 useMemo 包之。"
- wenyan-full: "物出新參照，致重繪。useMemo Wrap之。"
- wenyan-ultra: "新參照 -> 重繪。useMemo Wrap。"

## Connection Pooling

- lite: "Connection pooling reuses open connections instead of creating one per request. This avoids repeated handshake overhead."
- full: "Pool reuse open DB connections. No new connection per request. Skip handshake overhead."
- ultra: "Pool = reuse DB conn. Skip handshake -> fast under load."
- wenyan-full: "池 reuse open connection。不每 req 新開。skip handshake overhead。"
- wenyan-ultra: "池 reuse conn。skip handshake -> fast。"

## Destructive Action

Compression stops when omitted grammar could hide operation order:

> **Warning:** This permanently deletes every row in `users` and cannot be undone.
>
> ```sql
> DROP TABLE users;
> ```
>
> Verify the backup before running the command.
