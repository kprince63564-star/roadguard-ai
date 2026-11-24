"""Database package for ROADGUARD AI."""
from .db import (
    init_db,
    get_connection,
    add_report,
    get_report_by_id,
    get_all_reports,
    get_filtered_reports,
    update_report_status,
    delete_report,
    get_dashboard_stats,
    get_recent_reports,
    seed_demo_data_if_empty,
    create_user,
    authenticate_user
)

__all__ = [
    "init_db",
    "get_connection",
    "add_report",
    "get_report_by_id",
    "get_all_reports",
    "get_filtered_reports",
    "update_report_status",
    "delete_report",
    "get_dashboard_stats",
    "get_recent_reports",
    "seed_demo_data_if_empty",
    "create_user",
    "authenticate_user"
]
