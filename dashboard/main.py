#!/usr/bin/env python3
"""
Crush Dashboard — TUI de monitoring pour l'écosystème opencode-kit.

Lancement :
    python3 ~/opencode-kit/dashboard/main.py
    ou si symlinké : crush-dash

Tabs : Overview | Pouls | Mémoire | Système | Logs
Auto-refresh toutes les 5 secondes.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll, Container
from textual.widgets import (
    Footer, Header, TabbedContent, TabPane, Static, Label,
    DataTable, RichLog, Rule,
)
from textual.reactive import var
from textual.theme import Theme
from textual.binding import Binding
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.console import RenderableType

from collectors import get_snapshot, check_alive, read_file, HEARTBEAT_LOG, SCHEDULER_LOG

# ── Theme ──────────────────────────────────────────────
CRUSH_THEME = Theme(
    name="crush",
    primary="#00d4aa",       # cyan-vert
    secondary="#7c3aed",     # violet
    accent="#f59e0b",        # amber
    success="#10b981",       # green
    warning="#f59e0b",       # amber
    error="#ef4444",         # red
    surface="#1e1b2e",       # dark purple
    panel="#252236",
    background="#13111c",
    dark=True,
)


# ── Reusable Status Badge ──────────────────────────────
def status_badge(label: str, value: str, color: str = "primary") -> RenderableType:
    """Rich renderable: small labeled stat."""
    t = Table.grid(padding=(1, 2))
    t.add_column(style="dim")
    t.add_column(style=f"bold {color}")
    t.add_row(label, str(value))
    return t


# ── Main App ───────────────────────────────────────────
class CrushDashboard(App):
    CSS = """
    Screen {
        background: $surface;
    }

    TabbedContent {
        padding: 0 1;
    }

    TabPane {
        padding: 0 1;
    }

    /* ── Overview ── */
    #overview-grid {
        layout: grid;
        grid-size: 3;
        grid-columns: 1fr 1fr 1fr;
        grid-rows: auto;
        grid-gutter: 1 2;
        margin: 1 2;
    }

    .card {
        background: $panel;
        border: solid $primary;
        padding: 1 2;
        height: auto;
    }

    .card-title {
        text-style: bold underline;
        color: $primary;
        margin-bottom: 1;
    }

    .stat-value {
        color: $text;
    }

    .alive {
        color: $success;
        text-style: bold;
    }
    .dead {
        color: $error;
        text-style: bold;
    }
    .muted {
        color: $text-disabled;
    }

    /* ── DataTable styling ── */
    DataTable {
        height: 1fr;
        margin: 1 0;
    }

    RichLog {
        height: 1fr;
        margin: 1 0;
        background: $surface;
        border: solid $primary;
    }

    #pouls-grid, #memory-grid, #system-grid {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 1fr;
        grid-gutter: 1 2;
        margin: 1 2;
    }

    .full-width {
        column-span: 2;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quitter", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("1", "show_tab('overview')", "Overview", show=False),
        Binding("2", "show_tab('pouls')", "Pouls", show=False),
        Binding("3", "show_tab('memoire')", "Mémoire", show=False),
        Binding("4", "show_tab('systeme')", "Système", show=False),
        Binding("5", "show_tab('logs')", "Logs", show=False),
    ]

    data = var({})

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with TabbedContent(initial="overview"):
            # ── Tab 1: Overview ──
            with TabPane("🏠 Overview", id="overview"):
                with Vertical(id="overview-grid"):
                    yield Static("En attente des données...", id="overview-status")
                    yield Static("", id="overview-model")
                    yield Static("", id="overview-memory")
                    yield Static("", id="overview-heartbeat")
                    yield Static("", id="overview-config")
                    yield Static("", id="overview-cycles")

            # ── Tab 2: Pouls ──
            with TabPane("💓 Pouls", id="pouls"):
                with Vertical(id="pouls-grid"):
                    yield Static("", id="pouls-status")
                    yield Static("", id="pouls-rates")
                yield Label("Historique des battements", classes="card-title")
                yield DataTable(id="pouls-table", cursor_type="row")

            # ── Tab 3: Mémoire ──
            with TabPane("🧠 Mémoire", id="memoire"):
                with Vertical(id="memory-grid"):
                    yield Static("", id="mem-l1")
                    yield Static("", id="mem-l3")
                    yield Static("", id="mem-l2")
                    yield Static("", id="mem-consolidation")
                yield Label("Sessions archivées (L3)", classes="card-title")
                yield DataTable(id="mem-sessions", cursor_type="row")

            # ── Tab 4: Système ──
            with TabPane("⚙️ Système", id="systeme"):
                with Vertical(id="system-grid"):
                    yield Static("", id="sys-agents")
                    yield Static("", id="sys-skills")
                    yield Static("", id="sys-config")
                    yield Static("", id="sys-tasks-db")
                yield Label("Scheduler (dernières lignes)", classes="card-title")
                yield RichLog(id="sys-scheduler-log", highlight=True, markup=True)

            # ── Tab 5: Logs bruts ──
            with TabPane("📋 Logs", id="logs"):
                yield Label("heartbeat.log", classes="card-title")
                yield RichLog(id="logs-heartbeat", highlight=True, markup=True)
                yield Label("scheduler.log", classes="card-title")
                yield RichLog(id="logs-scheduler", highlight=True, markup=True)

        yield Footer()

    # ── Lifecycle ──
    def on_mount(self) -> None:
        self.register_theme(CRUSH_THEME)
        self.theme = "crush"
        self.refresh_data()
        self.set_interval(5, self.refresh_data)

    # ── Data Refresh ──
    @work(thread=True)
    def refresh_data(self) -> None:
        """Fetch snapshot in background thread."""
        snap = get_snapshot()
        self.data = snap

    def watch_data(self, snap: dict) -> None:
        """React to new snapshot data."""
        if not snap:
            return
        self._update_overview(snap)
        self._update_pouls(snap)
        self._update_memory(snap)
        self._update_system(snap)
        self._update_logs(snap)

    # ── Overview ──
    def _update_overview(self, snap: dict) -> None:
        hb = snap["heartbeat"]
        mem = snap["memory"]
        cfg = snap["config"]
        ag = snap["agents"]
        sk = snap["skills"]

        alive = "🟢 EN LIGNE" if hb["is_alive"] else "🔴 OFFLINE"
        alive_class = "alive" if hb["is_alive"] else "dead"

        self.query_one("#overview-status", Static).update(
            Panel(
                f"[{alive_class}]{alive}[/]\n"
                f"Dernier battement : {hb['last_beat_age']}\n"
                f"Modèle heartbeat : {cfg.get('heartbeat_model', 'N/A')}",
                title="⚡ Statut Agent",
            )
        )
        self.query_one("#overview-model", Static).update(
            Panel(
                f"Modèle : [bold]{cfg.get('model_id', 'N/A')}[/]\n"
                f"Provider : {cfg.get('provider_id', 'N/A')}\n"
                f"Agent : {cfg.get('default_agent', 'N/A')}",
                title="🤖 Modèle",
            )
        )
        self.query_one("#overview-memory", Static).update(
            Panel(
                f"L1 : {mem['l1']['lines']} lignes\n"
                f"L2 : {mem['l2'].get('note', 'N/A')}\n"
                f"L3 : {mem['l3']['count']} sessions ({mem['l3']['total_size_kb']} Ko)",
                title="🧠 Mémoire",
            )
        )
        self.query_one("#overview-heartbeat", Static).update(
            Panel(
                f"Cycles : {hb['total_cycles']}\n"
                f"Consolidation : il y a {hb['last_consolidation_age']}",
                title="💓 Pouls",
            )
        )
        self.query_one("#overview-config", Static).update(
            Panel(
                f"MCP : [bold]{cfg['mcp_count']}[/] connectés\n"
                + "\n".join(f"  • {n}" for n in cfg["mcp_names"]),
                title="🔌 MCP Servers",
            )
        )
        self.query_one("#overview-cycles", Static).update(
            Panel(
                f"Agents : [bold]{ag['count']}[/]\n"
                f"Skills : [bold]{sk['count']}[/]\n"
                f"Repos whitelist : {len(snap['whitelist'])}",
                title="📦 Resources",
            )
        )

    # ── Pouls ──
    def _update_pouls(self, snap: dict) -> None:
        hb = snap["heartbeat"]
        rl = snap["rate_limits"]

        self.query_one("#pouls-status", Static).update(
            Panel(
                f"Dernier battement : [bold]{hb['last_beat_age']}[/]\n"
                f"Timestamp : {hb['last_beat_raw'][:19] if hb['last_beat_raw'] else 'N/A'}\n"
                f"Dernier fullCompact : {hb['last_consolidation_age']}",
                title="📡 Statut Pouls",
            )
        )

        limits_str = "Aucune limite active"
        if rl.get("available", True) and not rl.get("error"):
            limits_str = json.dumps(rl, indent=2, ensure_ascii=False)
        self.query_one("#pouls-rates", Static).update(
            Panel(limits_str, title="🚦 Rate Limits")
        )

        # Heartbeat log table
        table = self.query_one("#pouls-table", DataTable)
        if not table.columns:
            table.add_columns("Timestamp", "Mails", "Traitées", "OK?", "Consolidation", "Journal")
        table.clear()
        for entry in hb["entries"]:
            if entry.get("type") == "test":
                table.add_row(entry["ts"], "TEST", "", "", "", "")
            else:
                table.add_row(
                    entry.get("ts", "")[:19],
                    entry.get("checked", "?"),
                    f"{entry.get('processed', '?')}/{entry.get('total', '?')}",
                    entry.get("status", ""),
                    entry.get("consolidation", "").strip()[:40],
                    entry.get("journal", "").strip()[:30],
                )

    # ── Mémoire ──
    def _update_memory(self, snap: dict) -> None:
        mem = snap["memory"]
        hb = snap["heartbeat"]

        self.query_one("#mem-l1", Static).update(
            Panel(
                f"Fichier : preferences.md\n"
                f"Lignes : [bold]{mem['l1']['lines']}[/]\n"
                f"Taille : {mem['l1']['size_bytes']} octets",
                title="📜 L1 — Règles",
            )
        )
        self.query_one("#mem-l2", Static).update(
            Panel(
                mem["l2"].get("note", "N/A"),
                title="🕸️ L2 — Knowledge Graph",
            )
        )
        self.query_one("#mem-l3", Static).update(
            Panel(
                f"Sessions : [bold]{mem['l3']['count']}[/]\n"
                f"Taille totale : {mem['l3']['total_size_kb']} Ko\n"
                f"Dossier : memory/sessions/",
                title="📁 L3 — Archives",
            )
        )
        self.query_one("#mem-consolidation", Static).update(
            Panel(
                f"Dernier fullCompact : [bold]{hb['last_consolidation_age']}[/]\n"
                f"Lock : consolidation.lock",
                title="🔄 Consolidation",
            )
        )

        # Sessions table
        tbl = self.query_one("#mem-sessions", DataTable)
        if not tbl.columns:
            tbl.add_columns("Fichier", "Date")
        tbl.clear()
        for f in mem["l3"]["files"]:
            date = f.replace(".md", "")
            tbl.add_row(f, date)

    # ── Système ──
    def _update_system(self, snap: dict) -> None:
        ag = snap["agents"]
        sk = snap["skills"]
        cfg = snap["config"]
        tdb = snap["system"]["tasks_db"]
        sys = snap["system"]

        self.query_one("#sys-agents", Static).update(
            Panel(
                f"[bold]{ag['count']} agents[/]\n"
                + "\n".join(f"  • {n}" for n in ag["names"][:12])
                + (f"\n  ... +{len(ag['names'])-12}" if len(ag["names"]) > 12 else ""),
                title="🤖 Agents",
            )
        )
        self.query_one("#sys-skills", Static).update(
            Panel(
                f"[bold]{sk['count']} skills[/]\n"
                + "\n".join(f"  • {n}" for n in sk["names"]),
                title="🎯 Skills",
            )
        )
        self.query_one("#sys-config", Static).update(
            Panel(
                f"Agent : {cfg['default_agent']}\n"
                f"Modèle : {cfg['model_id']}\n"
                f"MCP : {cfg['mcp_count']} serveurs",
                title="⚙️ Configuration",
            )
        )
        self.query_one("#sys-tasks-db", Static).update(
            Panel(
                f".tasks.db : [bold]{tdb['db']} Ko[/]\n"
                f"WAL : {tdb['wal']} Ko\n"
                f"Total : ~{tdb['db'] + tdb['wal']} Ko",
                title="🗄️ Tasks DB",
            )
        )

        log = self.query_one("#sys-scheduler-log", RichLog)
        log.clear()
        for line in sys["scheduler_log"]:
            log.write(line)

    # ── Logs bruts ──
    def _update_logs(self, snap: dict) -> None:
        hb_raw = read_file(HEARTBEAT_LOG) or "Aucun log"
        sched_raw = read_file(SCHEDULER_LOG) or "Aucun log"

        hb_log = self.query_one("#logs-heartbeat", RichLog)
        hb_log.clear()
        hb_log.write(hb_raw[-2000:] if len(hb_raw) > 2000 else hb_raw)

        sched_log = self.query_one("#logs-scheduler", RichLog)
        sched_log.clear()
        sched_log.write(sched_raw[-2000:] if len(sched_raw) > 2000 else sched_raw)

    # ── Actions ──
    def action_refresh(self) -> None:
        self.refresh_data()

    def action_show_tab(self, tab_id: str) -> None:
        self.query_one(TabbedContent).active = tab_id


# ── Entry point ──
if __name__ == "__main__":
    app = CrushDashboard()
    app.run()
