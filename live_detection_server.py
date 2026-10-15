"""
live_detection_server.py
-------------------------
Production-Ready Real-Time Live Detection Web & WebSocket Server.
Built with aiohttp for high-performance async streaming & low-latency WebSocket broadcasts.

Endpoints:
  - GET  /                           -> Serves Live Dashboard (dashboard.html)
  - GET  /dashboard.html             -> Serves Live Dashboard
  - GET  /Executive_Anomaly_Report.html -> Serves Executive Audit Report
  - GET  /ws                         -> Real-Time WebSocket Channel for Live Detections
  - GET  /api/status                 -> Current server & streamer status
  - GET  /api/initial_data           -> Full initial payload (KPIs, Products, Recent Records, ML)
  - POST /api/stream/start           -> Resume / Start live transaction generator
  - POST /api/stream/pause           -> Pause live transaction generator
  - POST /api/stream/speed           -> Adjust live stream interval in seconds
  - POST /api/stream/step            -> Execute 1 live transaction on demand
  - POST /api/stream/inject          -> Inject a user-specified anomaly immediately

Author: Krishna — B.Tech CSE (Data Science)
"""

import asyncio
import json
import os
import sys
import webbrowser
import argparse
from aiohttp import web, WSMsgType

from live_detection_engine import LiveDetectionEngine

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PORT = int(os.environ.get("PORT",5000))
HOST = "0.0.0.0"


@web.middleware
async def cors_middleware(request, handler):
    if request.method == "OPTIONS":
        resp = web.Response(status=200)
    else:
        resp = await handler(request)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "*"
    return resp


class LiveServerManager:
    def __init__(self):
        self.engine = LiveDetectionEngine()
        self.active_websockets = set()
        self.is_streaming = True
        self.interval = 1.5  # default 1.5s per transaction
        self.worker_task = None

    async def broadcast(self, payload):
        """Broadcasts a JSON message to all active WebSocket clients."""
        if not self.active_websockets:
            return
        msg = json.dumps(payload)
        dead = set()
        for ws in self.active_websockets:
            try:
                await ws.send_str(msg)
            except Exception:
                dead.add(ws)
        self.active_websockets.difference_update(dead)

    async def stream_worker(self):
        """Continuous background generator producing live transactions and running detection."""
        print("[STREAM] Live POS Transaction Worker started.")
        while True:
            try:
                if self.is_streaming:
                    # Run transaction evaluation
                    record = self.engine.generate_and_evaluate_transaction()
                    summary = self.engine.get_summary_statistics()

                    # Terminal logging
                    sev = record["severity"]
                    flag = record["anomaly_type"]
                    if sev == "CRITICAL":
                        prefix = "[CRITICAL ALERT]"
                    elif sev == "WARNING":
                        prefix = "[WARNING ALERT ]"
                    else:
                        prefix = "[NORMAL RECORD  ]"

                    impact_str = f" | Impact: Rs.{record['financial_impact']:,.2f}" if record["financial_impact"] != 0 else ""
                    print(
                        f"{prefix} ID #{record['id']:<5d} | {record['item']:<16s} | "
                        f"Sales: {record['sales']:>3d} | Z: {record['z_score']:>+5.2f} | "
                        f"Stock: {record['inventory']:>4d} | {flag}{impact_str}"
                    )

                    # Broadcast payload to dashboard
                    payload = {
                        "type": "LIVE_RECORD",
                        "record": record,
                        "stats": summary["stats"],
                        "products_summary": summary["products_summary"]
                    }
                    await self.broadcast(payload)

                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[STREAM ERROR] {e}")
                await asyncio.sleep(2.0)
    # --- HTTP Route Handlers ---

    async def handle_index(self, request):
        if os.path.exists("dashboard.html"):
            return web.FileResponse("dashboard.html")
        return web.Response(text="Dashboard file not found. Run build_html_dashboard.py first.", status=404)

    async def handle_report(self, request):
        if os.path.exists("Executive_Anomaly_Report.html"):
            return web.FileResponse("Executive_Anomaly_Report.html")
        return web.Response(text="Report file not found.", status=404)

    async def handle_status(self, request):
        return web.json_response({
            "is_streaming": self.is_streaming,
            "interval": self.interval,
            "active_clients": len(self.active_websockets),
            "date": self.engine.current_date.isoformat(),
        })

    async def handle_initial_data(self, request):
        """Returns the full initial payload required by dashboard charts and tables."""
        summary = self.engine.get_summary_statistics()
        limit_str = request.query.get("limit", "500")
        try:
            limit = int(limit_str)
        except Exception:
            limit = 500
        records = self.engine.get_recent_records(limit=limit)
        return web.json_response({
            "stats": summary["stats"],
            "products_summary": summary["products_summary"],
            "ml_metrics": summary["ml_metrics"],
            "records": records,
            "is_streaming": self.is_streaming,
            "interval": self.interval
        })

    async def handle_export_csv(self, request):
        """Returns the actual live database records as downloadable CSV."""
        import sqlite3
        conn = sqlite3.connect("retail.db")
        cur = conn.cursor()
        cur.execute("""
            SELECT id, record_date, item, sales, inventory, unit_price, revenue, stock_value,
                   rolling_mean, rolling_std, z_score, inv_rolling_mean, inv_z_score,
                   anomaly_type, is_flagged, severity, financial_impact
            FROM zscore_live_view
            ORDER BY id ASC
        """)
        headers = ["id", "record_date", "item", "sales", "inventory", "unit_price", "revenue", "stock_value",
                   "rolling_mean", "rolling_std", "z_score", "inv_rolling_mean", "inv_z_score",
                   "anomaly_type", "is_flagged", "severity", "financial_impact"]
        lines = [",".join(headers)]
        for row in cur.fetchall():
            lines.append(",".join([str(val) if val is not None else "" for val in row]))
        conn.close()
        csv_text = "\n".join(lines)
        return web.Response(text=csv_text, content_type="text/csv", headers={
            "Content-Disposition": 'attachment; filename="actual_live_data.csv"',
            "Access-Control-Allow-Origin": "*"
        })

    async def handle_stream_start(self, request):
        self.is_streaming = True
        print("[CONTROL] Live streaming resumed by dashboard.")
        await self.broadcast({"type": "STREAM_STATUS", "is_streaming": True, "interval": self.interval})
        return web.json_response({"status": "started", "is_streaming": True})

    async def handle_stream_pause(self, request):
        self.is_streaming = False
        print("[CONTROL] Live streaming paused by dashboard.")
        await self.broadcast({"type": "STREAM_STATUS", "is_streaming": False, "interval": self.interval})
        return web.json_response({"status": "paused", "is_streaming": False})

    async def handle_stream_speed(self, request):
        try:
            data = await request.json()
            interval = float(data.get("interval", 1.5))
            self.interval = max(0.2, min(10.0, interval))
            print(f"[CONTROL] Stream interval updated to {self.interval:.1f}s")
            await self.broadcast({"type": "STREAM_SPEED", "interval": self.interval})
            return web.json_response({"status": "updated", "interval": self.interval})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)

    async def handle_stream_step(self, request):
        """Produces a single transaction on demand (useful during viva testing)."""
        record = self.engine.generate_and_evaluate_transaction()
        summary = self.engine.get_summary_statistics()
        payload = {
            "type": "LIVE_RECORD",
            "record": record,
            "stats": summary["stats"],
            "products_summary": summary["products_summary"]
        }
        await self.broadcast(payload)
        return web.json_response({"status": "step_executed", "record": record})

    async def handle_inject_anomaly(self, request):
        """Injects a chosen anomaly type immediately on demand."""
        try:
            data = await request.json()
            item = data.get("item")
            anomaly_type = data.get("type", "spike")  # spike, drop, shrinkage, stockout

            print(f"[MANUAL INJECT] Injected '{anomaly_type}' on item '{item or 'auto'}'")
            record = self.engine.generate_and_evaluate_transaction(
                item_override=item,
                anomaly_type_override=anomaly_type
            )
            summary = self.engine.get_summary_statistics()
            payload = {
                "type": "LIVE_RECORD",
                "record": record,
                "stats": summary["stats"],
                "products_summary": summary["products_summary"],
                "injected": True
            }
            await self.broadcast(payload)
            return web.json_response({"status": "injected", "record": record})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)

    # --- WebSocket Handler ---

    async def handle_websocket(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.active_websockets.add(ws)
        print(f"[WS] Client connected. Active clients: {len(self.active_websockets)}")

        # Send initial connection handshake
        await ws.send_str(json.dumps({
            "type": "HANDSHAKE",
            "message": "Connected to Retail Anomaly Live Engine",
            "is_streaming": self.is_streaming,
            "interval": self.interval
        }))

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        action = data.get("action")
                        if action == "start":
                            self.is_streaming = True
                            await self.broadcast({"type": "STREAM_STATUS", "is_streaming": True, "interval": self.interval})
                        elif action == "pause":
                            self.is_streaming = False
                            await self.broadcast({"type": "STREAM_STATUS", "is_streaming": False, "interval": self.interval})
                        elif action == "speed":
                            self.interval = float(data.get("interval", 1.5))
                            await self.broadcast({"type": "STREAM_SPEED", "interval": self.interval})
                        elif action == "inject":
                            record = self.engine.generate_and_evaluate_transaction(
                                item_override=data.get("item"),
                                anomaly_type_override=data.get("type", "spike")
                            )
                            summary = self.engine.get_summary_statistics()
                            await self.broadcast({
                                "type": "LIVE_RECORD",
                                "record": record,
                                "stats": summary["stats"],
                                "products_summary": summary["products_summary"],
                                "injected": True
                            })
                    except Exception as err:
                        print(f"[WS MSG ERROR] {err}")
                elif msg.type == WSMsgType.ERROR:
                    print(f"[WS ERROR] Connection closed with exception: {ws.exception()}")
        finally:
            self.active_websockets.discard(ws)
            print(f"[WS] Client disconnected. Remaining: {len(self.active_websockets)}")

        return ws


def make_app(manager):
    app = web.Application(middlewares=[cors_middleware])
    app.router.add_get("/", manager.handle_index)
    app.router.add_get("/dashboard.html", manager.handle_index)
    app.router.add_get("/Executive_Anomaly_Report.html", manager.handle_report)
    app.router.add_get("/ws", manager.handle_websocket)
    app.router.add_get("/api/status", manager.handle_status)
    app.router.add_get("/api/initial_data", manager.handle_initial_data)
    app.router.add_get("/api/export_csv", manager.handle_export_csv)
    app.router.add_post("/api/stream/start", manager.handle_stream_start)
    app.router.add_post("/api/stream/pause", manager.handle_stream_pause)
    app.router.add_post("/api/stream/speed", manager.handle_stream_speed)
    app.router.add_post("/api/stream/step", manager.handle_stream_step)
    app.router.add_post("/api/stream/inject", manager.handle_inject_anomaly)

    # Static route fallback for logs and reports if needed
    if os.path.exists("data_export"):
        app.router.add_static("/data_export", path="data_export")
    if os.path.exists("logs"):
        app.router.add_static("/logs", path="logs")

    return app


async def main():
    parser = argparse.ArgumentParser(description="Retail Anomaly Live Detection Server")
    parser.add_argument("--port", type=int, default=PORT, help="Port to listen on (default 5000)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    parser.add_argument("--interval", type=float, default=1.5, help="Stream interval in seconds (default 1.5)")
    parser.add_argument("--paused", action="store_true", help="Start in paused state")
    args = parser.parse_args()

    manager = LiveServerManager()
    manager.interval = args.interval
    manager.is_streaming = not args.paused

    app = make_app(manager)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, args.port)
    await site.start()

    # Launch background stream worker
    manager.worker_task = asyncio.create_task(manager.stream_worker())

    dashboard_url = f"http://{HOST}:{args.port}/dashboard.html"
    print("=" * 72)
    print("  [OK] RETAIL ANOMALY LIVE DETECTION ENGINE SERVER STARTED")
    print("  Dual-Engine: SQL Windowed Z-Score + Scikit-Learn Isolation Forest")
    print(f"  Author: Krishna -- B.Tech CSE (Data Science) 3rd Year")
    print("=" * 72)
    print(f"  * Dashboard URL:      {dashboard_url}")
    print(f"  * WebSocket Channel:  ws://{HOST}:{args.port}/ws")
    print(f"  * Stream Interval:    {manager.interval}s per transaction")
    print(f"  * Engine State:       {'STREAMING' if manager.is_streaming else 'PAUSED'}")
    print("  Press Ctrl+C to stop the server at any time.")
    print("=" * 72)

    if not args.no_browser:
        webbrowser.open(dashboard_url)

    try:
        while True:
            await asyncio.sleep(3600)
    except (asyncio.CancelledError, KeyboardInterrupt):
        print("\n[SERVER] Shutting down...")
    finally:
        if manager.worker_task:
            manager.worker_task.cancel()
        await runner.cleanup()
        print("[SERVER] Stopped cleanly.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
