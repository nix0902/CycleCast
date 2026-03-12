#!/usr/bin/env python3
"""
Auto Assignment - Автоматическое распределение задач

Usage:
    python scripts/auto_assign.py assign <task_id>
    python scripts/auto_assign.py candidates <task_id>
    python scripts/auto_assign.py stats
    python scripts/auto_assign.py history
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml

BASE_DIR = Path(__file__).parent.parent
AGENT_SKILLS_FILE = BASE_DIR / "agent_skills.yaml"
TASKS_FILE = BASE_DIR / "tasks.yaml"
SESSION_FILE = BASE_DIR / "session.yaml"


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_yaml(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def calculate_skills_match(required: list, agent_skills: list) -> float:
    """Calculate skills match score."""
    if not required:
        return 1.0
    
    agent_dict = {s["name"]: s["level"] for s in agent_skills}
    total_score = 0
    
    for req in required:
        skill_name = req.get("name", "")
        min_level = req.get("min_level", 5)
        
        if skill_name in agent_dict:
            level = agent_dict[skill_name]
            if level >= min_level:
                total_score += 1.0
            else:
                total_score += level / min_level
        else:
            total_score += 0
    
    return total_score / len(required)


def calculate_specialization_match(task_tags: list, agent_specs: list) -> float:
    """Calculate specialization match."""
    if not task_tags or not agent_specs:
        return 0.5
    
    matches = sum(1 for tag in task_tags if tag in agent_specs)
    return matches / len(task_tags)


def calculate_load_balance(agent_data: dict) -> float:
    """Calculate load balance score (lower load = higher score)."""
    current_load = agent_data.get("current_load", {})
    active = current_load.get("active_tasks", 0)
    max_tasks = 3
    
    return max(0, 1 - (active / max_tasks))


def score_agent(task: dict, agent_name: str, agent_data: dict) -> float:
    """Calculate total score for an agent."""
    config = load_yaml(AGENT_SKILLS_FILE).get("config", {})
    weights = config.get("scoring_weights", {
        "skills_match": 0.40,
        "specialization_match": 0.25,
        "performance_score": 0.20,
        "load_balance": 0.15
    })
    
    # Skills match
    required_skills = task.get("required_skills", [])
    agent_skills = agent_data.get("skills", [])
    skills_score = calculate_skills_match(required_skills, agent_skills)
    
    # Specialization match
    task_tags = task.get("tags", [])
    agent_specs = agent_data.get("specializations", [])
    spec_score = calculate_specialization_match(task_tags, agent_specs)
    
    # Performance score
    performance = agent_data.get("performance", {})
    perf_score = performance.get("success_rate", 0.85)
    
    # Load balance
    load_score = calculate_load_balance(agent_data)
    
    # Total score
    total = (
        skills_score * weights.get("skills_match", 0.40) +
        spec_score * weights.get("specialization_match", 0.25) +
        perf_score * weights.get("performance_score", 0.20) +
        load_score * weights.get("load_balance", 0.15)
    )
    
    return total


def find_candidates(task_id: str) -> list:
    """Find best candidates for a task."""
    tasks_config = load_yaml(TASKS_FILE)
    skills_config = load_yaml(AGENT_SKILLS_FILE)
    
    # Find task
    task = None
    for t in tasks_config.get("tasks", []):
        if t.get("id") == task_id:
            task = t
            break
    
    if not task:
        print(f"❌ Task not found: {task_id}")
        return []
    
    # Score all agents
    candidates = []
    for agent_name, agent_data in skills_config.get("agents", {}).items():
        if not agent_data.get("current_load", {}).get("available", True):
            continue
        
        score = score_agent(task, agent_name, agent_data)
        candidates.append({
            "agent": agent_name,
            "score": score,
            "model_id": agent_data.get("model_id"),
            "skills": {s["name"]: s["level"] for s in agent_data.get("skills", [])}
        })
    
    # Sort by score
    candidates.sort(key=lambda x: x["score"], reverse=True)
    
    return candidates


def assign_task(task_id: str) -> Optional[dict]:
    """Auto-assign a task to the best agent."""
    candidates = find_candidates(task_id)
    
    if not candidates:
        print(f"❌ No suitable agents found for task: {task_id}")
        return None
    
    best = candidates[0]
    
    config = load_yaml(AGENT_SKILLS_FILE)
    min_threshold = config.get("config", {}).get("min_score_threshold", 0.5)
    
    if best["score"] < min_threshold:
        print(f"⚠️ Best candidate score ({best['score']:.2f}) below threshold ({min_threshold})")
        return None
    
    print(f"\n✅ Task {task_id} assigned to: {best['agent']}")
    print(f"   Score: {best['score']:.2%}")
    print(f"   Model: {best['model_id']}")
    
    return best


def show_candidates(task_id: str) -> None:
    """Show candidates for a task."""
    candidates = find_candidates(task_id)
    
    print(f"\n📋 Candidates for task: {task_id}\n")
    print(f"{'Agent':<30} {'Score':<10} {'Model':<20}")
    print("-" * 65)
    
    for c in candidates[:5]:
        print(f"{c['agent'][:29]:<30} {c['score']:<10.2%} {c['model_id'][:19]:<20}")
    
    print()


def show_stats() -> None:
    """Show assignment statistics."""
    config = load_yaml(AGENT_SKILLS_FILE)
    stats = config.get("statistics", {})
    
    print("\n📊 Auto-Assignment Statistics\n")
    print(f"  Total assignments: {stats.get('total_assignments', 0)}")
    print(f"  Successful: {stats.get('successful_assignments', 0)}")
    print(f"  Declined: {stats.get('declined_assignments', 0)}")
    print(f"  Auto-reassigned: {stats.get('auto_reassigned', 0)}")
    print()


def show_history() -> None:
    """Show assignment history."""
    config = load_yaml(AGENT_SKILLS_FILE)
    history = config.get("statistics", {}).get("assignment_history", [])
    
    print("\n📜 Assignment History\n")
    
    if not history:
        print("  No assignments yet.\n")
        return
    
    for entry in history[-10:]:
        print(f"  {entry}")
    
    print()


def main():
    parser = argparse.ArgumentParser(description="Auto Assignment")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # assign
    assign_parser = subparsers.add_parser("assign", help="Assign task to best agent")
    assign_parser.add_argument("task_id", help="Task ID")
    
    # candidates
    cand_parser = subparsers.add_parser("candidates", help="Show candidates")
    cand_parser.add_argument("task_id", help="Task ID")
    
    # stats
    subparsers.add_parser("stats", help="Show statistics")
    
    # history
    subparsers.add_parser("history", help="Show history")
    
    args = parser.parse_args()
    
    if args.command == "assign":
        assign_task(args.task_id)
    elif args.command == "candidates":
        show_candidates(args.task_id)
    elif args.command == "stats":
        show_stats()
    elif args.command == "history":
        show_history()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
