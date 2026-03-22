"""Structured logging module with agent execution tracing.

Provides structured JSON logging for production use and rich console
logging for development. Each log entry can be tagged with agent context.
"""

import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured log output."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add agent context if present
        if hasattr(record, "agent"):
            log_entry["agent"] = record.agent
        if hasattr(record, "task_id"):
            log_entry["task_id"] = record.task_id
        if hasattr(record, "project"):
            log_entry["project"] = record.project
        if hasattr(record, "step"):
            log_entry["step"] = record.step

        # Add exception info if present
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


class RichDevFormatter(logging.Formatter):
    """Human-readable formatter for development console output."""

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        timestamp = datetime.now().strftime("%H:%M:%S")

        agent_tag = ""
        if hasattr(record, "agent"):
            agent_tag = f" [{record.agent}]"

        step_tag = ""
        if hasattr(record, "step"):
            step_tag = f" → {record.step}"

        return (
            f"{color}{timestamp} {record.levelname:8s}{self.RESET}"
            f"{agent_tag}{step_tag} {record.getMessage()}"
        )


_logging_initialized = False


def setup_logging(level: str = "INFO", structured: bool = False) -> None:
    """Initialize the logging system.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        structured: If True, output JSON logs. If False, use rich dev format.
    """
    global _logging_initialized
    if _logging_initialized:
        return
    _logging_initialized = True

    root_logger = logging.getLogger("work_buddy")
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    handler = logging.StreamHandler(sys.stderr)
    if structured:
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(RichDevFormatter())

    root_logger.addHandler(handler)

    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("playwright").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for the given module name.

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance under the work_buddy namespace
    """
    if name.startswith("work_buddy."):
        return logging.getLogger(name)
    return logging.getLogger(f"work_buddy.{name}")
