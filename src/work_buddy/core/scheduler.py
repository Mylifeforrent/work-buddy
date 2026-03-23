"""Scheduler for automated PVT health checks.

Supports cron-based scheduling with timezone awareness.
Can be enabled/disabled per project via configuration.
"""

import asyncio
import logging
from datetime import datetime
from typing import Callable, Optional
from zoneinfo import ZoneInfo

from croniter import croniter

from work_buddy.core.config import ProjectConfig, PVTScheduleConfig, list_projects, load_project_config

logger = logging.getLogger(__name__)


class PVTScheduler:
    """Manages scheduled PVT health checks for projects."""

    def __init__(self, pvt_runner: Callable[[ProjectConfig], asyncio.Task]):
        """Initialize the scheduler.

        Args:
            pvt_runner: Async function to run PVT for a project
        """
        self.pvt_runner = pvt_runner
        self._running = False
        self._tasks: dict[str, asyncio.Task] = {}
        self._schedules: dict[str, croniter] = {}

    def _get_next_run(self, schedule: PVTScheduleConfig) -> datetime:
        """Get the next run time based on cron schedule and timezone."""
        tz = ZoneInfo(schedule.timezone)
        now = datetime.now(tz)
        cron = croniter(schedule.cron, now)
        return cron.get_next(datetime)

    def _should_run(self, schedule: PVTScheduleConfig) -> bool:
        """Check if a PVT should run now based on schedule."""
        if not schedule.enabled:
            return False

        tz = ZoneInfo(schedule.timezone)
        now = datetime.now(tz)

        # Check if current time matches the cron schedule (within 1 minute tolerance)
        cron = croniter(schedule.cron, now)
        prev_run = cron.get_prev(datetime)
        next_run = cron.get_next(datetime)

        # If we're within 1 minute of the scheduled time
        diff_seconds = abs((now - prev_run).total_seconds())
        return diff_seconds < 60

    async def _schedule_loop(self, project_name: str):
        """Run the scheduling loop for a project."""
        try:
            project = load_project_config(project_name)
            schedule = project.pvt_schedule

            if not schedule.enabled:
                logger.info(f"PVT schedule disabled for {project_name}")
                return

            tz = ZoneInfo(schedule.timezone)
            cron = croniter(schedule.cron, datetime.now(tz))
            next_run = cron.get_next(datetime)

            logger.info(
                f"PVT scheduler started for {project_name}, "
                f"next run at {next_run.isoformat()} ({schedule.timezone})"
            )

            while self._running:
                now = datetime.now(tz)

                # Check if it's time to run
                if now >= next_run:
                    logger.info(f"Running scheduled PVT for {project_name}")
                    try:
                        await self.pvt_runner(project)
                        logger.info(f"Scheduled PVT completed for {project_name}")
                    except Exception as e:
                        logger.error(f"Scheduled PVT failed for {project_name}: {e}")

                    # Schedule next run
                    cron = croniter(schedule.cron, now)
                    next_run = cron.get_next(datetime)
                    logger.info(f"Next PVT run for {project_name}: {next_run.isoformat()}")

                # Sleep for 30 seconds before checking again
                await asyncio.sleep(30)

        except Exception as e:
            logger.error(f"Scheduler loop error for {project_name}: {e}")

    def start(self):
        """Start the scheduler for all enabled projects."""
        self._running = True

        projects = list_projects()
        enabled_count = 0

        for project_name in projects:
            try:
                project = load_project_config(project_name)
                if project.pvt_schedule.enabled:
                    task = asyncio.create_task(self._schedule_loop(project_name))
                    self._tasks[project_name] = task
                    enabled_count += 1
            except Exception as e:
                logger.error(f"Failed to start scheduler for {project_name}: {e}")

        logger.info(f"PVT scheduler started with {enabled_count} enabled projects")
        return enabled_count

    def stop(self):
        """Stop all scheduled tasks."""
        self._running = False

        for project_name, task in self._tasks.items():
            task.cancel()
            logger.info(f"Stopped PVT scheduler for {project_name}")

        self._tasks.clear()
        logger.info("PVT scheduler stopped")

    def get_status(self) -> dict:
        """Get the current scheduler status."""
        status = {
            "running": self._running,
            "projects": {}
        }

        for project_name in list_projects():
            try:
                project = load_project_config(project_name)
                schedule = project.pvt_schedule

                tz = ZoneInfo(schedule.timezone)
                next_run = None
                if schedule.enabled:
                    cron = croniter(schedule.cron, datetime.now(tz))
                    next_run = cron.get_next(datetime).isoformat()

                status["projects"][project_name] = {
                    "enabled": schedule.enabled,
                    "cron": schedule.cron,
                    "timezone": schedule.timezone,
                    "next_run": next_run
                }
            except Exception as e:
                status["projects"][project_name] = {"error": str(e)}

        return status


# Global scheduler instance
_scheduler: Optional[PVTScheduler] = None


def get_scheduler(pvt_runner: Optional[Callable] = None) -> Optional[PVTScheduler]:
    """Get or create the global scheduler instance."""
    global _scheduler

    if _scheduler is None and pvt_runner is not None:
        _scheduler = PVTScheduler(pvt_runner)

    return _scheduler


def start_scheduler(pvt_runner: Callable) -> int:
    """Start the global PVT scheduler.

    Args:
        pvt_runner: Async function to run PVT for a project

    Returns:
        Number of enabled projects
    """
    scheduler = get_scheduler(pvt_runner)
    if scheduler:
        return scheduler.start()
    return 0


def stop_scheduler():
    """Stop the global PVT scheduler."""
    global _scheduler
    if _scheduler:
        _scheduler.stop()
        _scheduler = None


def get_scheduler_status() -> dict:
    """Get the current scheduler status."""
    if _scheduler:
        return _scheduler.get_status()
    return {"running": False, "projects": {}}