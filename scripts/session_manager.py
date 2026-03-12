#!/usr/bin/env python3
"""
Session Manager - Управление сессиями ИИ-агентов

Usage:
    python scripts/session_manager.py register <task_id> <agent_name> <model>
    python scripts/session_manager.py heartbeat <session_id>
    python scripts/session_manager.py complete <session_id> <status> <notes>
    python scripts/session_manager.py status
    python scripts/session_manager.py validate
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import yaml

BASE_DIR = Path(__file__).parent.parent
SESSION_FILE = BASE_DIR / "session.yaml"


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_yaml(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def generate_session_id() -> str:
    return f"SESSION-{datetime.now().strftime('%Y%m%d%H%M%S')}"


def register_session(task_id: str, agent_name: str, model: str) -> dict:
    """Register a new agent session."""
    config = load_yaml(SESSION_FILE)
    
    session_id = generate_session_id()
    now = datetime.now().isoformat()
    
    session = {
        "id": session_id,
        "agent": agent_name,
        "model_id": model,
        "task_id": task_id,
        "status": "active",
        "created_at": now,
        "last_heartbeat": now,
        "checkpoint_id": None,
        "progress": {
            "phase": "started",
            "percentage": 0
        }
    }
    
    if "sessions" not in config:
        config["sessions"] = []
    config["sessions"].append(session)
    
    # Add lock
    lock = {
        "task_id": task_id,
        "session_id": session_id,
        "locked_at": now,
        "locked_by": agent_name
    }
    if "locks" not in config:
        config["locks"] = []
    config["locks"].append(lock)
    
    # Update statistics
    if "statistics" not in config:
        config["statistics"] = {}
    config["statistics"]["total_sessions"] = config["statistics"].get("total_sessions", 0) + 1
    config["statistics"]["active_sessions"] = len([s for s in config["sessions"] if s["status"] == "active"])
    
    save_yaml(SESSION_FILE, config)
    
    print(f"✅ Session registered: {session_id}")
    print(f"   Agent: {agent_name}")
    print(f"   Task: {task_id}")
    
    return session


def heartbeat(session_id: str) -> bool:
    """Update session heartbeat."""
    config = load_yaml(SESSION_FILE)
    
    for session in config.get("sessions", []):
        if session["id"] == session_id:
            session["last_heartbeat"] = datetime.now().isoformat()
            save_yaml(SESSION_FILE, config)
            print(f"💓 Heartbeat updated: {session_id}")
            return True
    
    print(f"❌ Session not found: {session_id}")
    return False


def complete_session(session_id: str, status: str, notes: str) -> bool:
    """Complete a session."""
    config = load_yaml(SESSION_FILE)
    
    for session in config.get("sessions", []):
        if session["id"] == session_id:
            session["status"] = status
            session["completed_at"] = datetime.now().isoformat()
            session["notes"] = notes
            
            # Remove lock
            config["locks"] = [l for l in config.get("locks", []) if l["session_id"] != session_id]
            
            # Update statistics
            if status == "success":
                config["statistics"]["completed_sessions"] = config["statistics"].get("completed_sessions", 0) + 1
            
            config["statistics"]["active_sessions"] = len([s for s in config["sessions"] if s["status"] == "active"])
            
            save_yaml(SESSION_FILE, config)
            print(f"✅ Session completed: {session_id} ({status})")
            return True
    
    print(f"❌ Session not found: {session_id}")
    return False


def show_status() -> None:
    """Show session status."""
    config = load_yaml(SESSION_FILE)
    
    print("\n📊 Session Status\n")
    
    sessions = config.get("sessions", [])
    if not sessions:
        print("  No active sessions\n")
        return
    
    print(f"{'ID':<20} {'Agent':<25} {'Task':<15} {'Status':<10}")
    print("-" * 75)
    
    for session in sessions:
        print(f"{session['id']:<20} {session['agent'][:24]:<25} {session['task_id']:<15} {session['status']:<10}")
    
    print(f"\n  Total: {len(sessions)} sessions")
    print(f"  Active: {len([s for s in sessions if s['status'] == 'active'])}")
    print()


def validate_sessions() -> bool:
    """Validate and clean up timed-out sessions."""
    config = load_yaml(SESSION_FILE)
    
    timeout_minutes = config.get("config", {}).get("session_timeout_minutes", 120)
    cutoff = datetime.now() - timedelta(minutes=timeout_minutes)
    
    timed_out = 0
    for session in config.get("sessions", []):
        if session["status"] == "active":
            last_heartbeat = datetime.fromisoformat(session.get("last_heartbeat", "2000-01-01"))
            if last_heartbeat < cutoff:
                session["status"] = "timed_out"
                session["timed_out_at"] = datetime.now().isoformat()
                timed_out += 1
    
    # Remove locks for timed-out sessions
    timed_out_ids = [s["id"] for s in config.get("sessions", []) if s["status"] == "timed_out"]
    config["locks"] = [l for l in config.get("locks", []) if l["session_id"] not in timed_out_ids]
    
    if timed_out > 0:
        config["statistics"]["timed_out_sessions"] = config["statistics"].get("timed_out_sessions", 0) + timed_out
        config["statistics"]["active_sessions"] = len([s for s in config["sessions"] if s["status"] == "active"])
        save_yaml(SESSION_FILE, config)
    
    print(f"✅ Validation complete. Timed out: {timed_out}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Session Manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # register
    reg_parser = subparsers.add_parser("register", help="Register new session")
    reg_parser.add_argument("task_id", help="Task ID")
    reg_parser.add_argument("agent_name", help="Agent name")
    reg_parser.add_argument("model", help="Model ID")
    
    # heartbeat
    hb_parser = subparsers.add_parser("heartbeat", help="Update heartbeat")
    hb_parser.add_argument("session_id", help="Session ID")
    
    # complete
    comp_parser = subparsers.add_parser("complete", help="Complete session")
    comp_parser.add_argument("session_id", help="Session ID")
    comp_parser.add_argument("status", choices=["success", "failed", "cancelled"])
    comp_parser.add_argument("notes", nargs="?", default="")
    
    # status
    subparsers.add_parser("status", help="Show status")
    
    # validate
    subparsers.add_parser("validate", help="Validate sessions")
    
    args = parser.parse_args()
    
    if args.command == "register":
        register_session(args.task_id, args.agent_name, args.model)
    elif args.command == "heartbeat":
        heartbeat(args.session_id)
    elif args.command == "complete":
        complete_session(args.session_id, args.status, args.notes)
    elif args.command == "status":
        show_status()
    elif args.command == "validate":
        validate_sessions()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
