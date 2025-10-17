"""
Action Balance Tracker for AI Happenings
Tracks and reports action balance/credits usage with AgentBill
"""

from typing import Dict, List
from datetime import datetime
import json


class ActionBalanceTracker:
    """Tracks action balance and usage metrics."""

    def __init__(self, agentbill_tracker):
        """
        Initialize action balance tracker.

        Args:
            agentbill_tracker: AgentBill instance for tracking
        """
        self.agentbill = agentbill_tracker

        # Action costs (in credits)
        self.action_costs = {
            "scrape_source": 1,
            "extract_content": 0.5,
            "analyze_article": 10,
            "generate_summary": 15,
            "prioritize_batch": 2,
            "api_call": 5
        }

        # Session tracking
        self.session_actions = []
        self.session_start = datetime.now()

    def track_action(self, action_name: str, metadata: Dict = None) -> Dict:
        """
        Track an action and its cost.

        Args:
            action_name: Name of the action
            metadata: Additional metadata

        Returns:
            Action tracking result
        """
        cost = self.action_costs.get(action_name, 1)

        action_record = {
            "action": action_name,
            "cost": cost,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        self.session_actions.append(action_record)

        # Track with AgentBill
        self.agentbill.track_signal(
            event_name=f"action_{action_name}",
            revenue=0,
            data={
                "action_type": action_name,
                "action_cost": cost,
                "session_id": id(self),
                "cumulative_cost": self.get_session_cost(),
                **action_record["metadata"]
            }
        )

        return action_record

    def get_session_cost(self) -> float:
        """
        Calculate total cost for current session.

        Returns:
            Total session cost in credits
        """
        return sum(action["cost"] for action in self.session_actions)

    def get_action_breakdown(self) -> Dict[str, Dict]:
        """
        Get breakdown of actions by type.

        Returns:
            Dictionary with action statistics
        """
        breakdown = {}

        for action in self.session_actions:
            action_name = action["action"]
            if action_name not in breakdown:
                breakdown[action_name] = {
                    "count": 0,
                    "total_cost": 0,
                    "unit_cost": action["cost"]
                }

            breakdown[action_name]["count"] += 1
            breakdown[action_name]["total_cost"] += action["cost"]

        return breakdown

    def get_balance_report(self) -> str:
        """
        Generate action balance report.

        Returns:
            Formatted balance report string
        """
        duration = (datetime.now() - self.session_start).total_seconds()
        total_cost = self.get_session_cost()
        breakdown = self.get_action_breakdown()

        report = f"""
╔══════════════════════════════════════════════════════════╗
║              ACTION BALANCE REPORT                       ║
╠══════════════════════════════════════════════════════════╣
║  Session Start: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}          ║
║  Duration: {duration:.1f}s                                      ║
║  Total Actions: {len(self.session_actions)}                                 ║
║  Total Cost: {total_cost:.1f} credits                           ║
╠══════════════════════════════════════════════════════════╣
║  ACTION BREAKDOWN                                        ║
╠══════════════════════════════════════════════════════════╣
"""

        for action_name, stats in sorted(breakdown.items()):
            report += f"║  {action_name:<20} x{stats['count']:>3}  =  {stats['total_cost']:>6.1f} credits  ║\n"

        report += """╠══════════════════════════════════════════════════════════╣
║  COST EFFICIENCY                                         ║
╠══════════════════════════════════════════════════════════╣
"""

        if duration > 0:
            actions_per_sec = len(self.session_actions) / duration
            cost_per_sec = total_cost / duration
            report += f"║  Actions/sec: {actions_per_sec:.2f}                                 ║\n"
            report += f"║  Credits/sec: {cost_per_sec:.2f}                                 ║\n"

        report += "╚══════════════════════════════════════════════════════════╝\n"

        # Track report generation
        self.agentbill.track_signal(
            event_name="balance_report_generated",
            revenue=0,
            data={
                "total_actions": len(self.session_actions),
                "total_cost": total_cost,
                "duration_seconds": duration,
                "breakdown": breakdown
            }
        )

        return report

    def export_session_data(self) -> Dict:
        """
        Export complete session data.

        Returns:
            Dictionary with all session data
        """
        return {
            "session_id": id(self),
            "session_start": self.session_start.isoformat(),
            "session_end": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - self.session_start).total_seconds(),
            "total_actions": len(self.session_actions),
            "total_cost": self.get_session_cost(),
            "actions": self.session_actions,
            "breakdown": self.get_action_breakdown()
        }

    def check_balance_threshold(self, threshold: float) -> bool:
        """
        Check if session cost exceeds threshold.

        Args:
            threshold: Cost threshold in credits

        Returns:
            True if under threshold, False if exceeded
        """
        current_cost = self.get_session_cost()
        exceeded = current_cost >= threshold

        if exceeded:
            self.agentbill.track_signal(
                event_name="balance_threshold_exceeded",
                revenue=0,
                data={
                    "threshold": threshold,
                    "current_cost": current_cost,
                    "overage": current_cost - threshold
                }
            )

        return not exceeded

    def estimate_action_cost(self, planned_actions: Dict[str, int]) -> Dict:
        """
        Estimate cost for planned actions.

        Args:
            planned_actions: Dictionary of action_name: count

        Returns:
            Cost estimation dictionary
        """
        estimation = {
            "planned_actions": planned_actions,
            "estimated_costs": {},
            "total_estimated_cost": 0
        }

        for action_name, count in planned_actions.items():
            unit_cost = self.action_costs.get(action_name, 1)
            total_cost = unit_cost * count
            estimation["estimated_costs"][action_name] = {
                "count": count,
                "unit_cost": unit_cost,
                "total_cost": total_cost
            }
            estimation["total_estimated_cost"] += total_cost

        # Track estimation
        self.agentbill.track_signal(
            event_name="cost_estimation_requested",
            revenue=0,
            data=estimation
        )

        return estimation


class UsageLimiter:
    """Enforces usage limits based on action balance."""

    def __init__(self, agentbill_tracker, daily_limit: float = 1000):
        """
        Initialize usage limiter.

        Args:
            agentbill_tracker: AgentBill instance
            daily_limit: Daily credit limit
        """
        self.agentbill = agentbill_tracker
        self.daily_limit = daily_limit
        self.daily_usage = 0
        self.day_start = datetime.now().date()

    def check_limit(self, required_credits: float) -> bool:
        """
        Check if action is within daily limit.

        Args:
            required_credits: Credits required for action

        Returns:
            True if within limit, False otherwise
        """
        # Reset daily counter if new day
        today = datetime.now().date()
        if today != self.day_start:
            self.daily_usage = 0
            self.day_start = today

        if self.daily_usage + required_credits > self.daily_limit:
            self.agentbill.track_signal(
                event_name="daily_limit_exceeded",
                revenue=0,
                data={
                    "daily_limit": self.daily_limit,
                    "current_usage": self.daily_usage,
                    "required_credits": required_credits
                }
            )
            return False

        return True

    def consume_credits(self, credits: float):
        """
        Consume credits from daily balance.

        Args:
            credits: Number of credits to consume
        """
        self.daily_usage += credits

        self.agentbill.track_signal(
            event_name="credits_consumed",
            revenue=0,
            data={
                "credits_consumed": credits,
                "remaining_balance": self.daily_limit - self.daily_usage,
                "daily_usage": self.daily_usage,
                "daily_limit": self.daily_limit
            }
        )

    def get_remaining_balance(self) -> float:
        """
        Get remaining daily balance.

        Returns:
            Remaining credits
        """
        return max(0, self.daily_limit - self.daily_usage)
