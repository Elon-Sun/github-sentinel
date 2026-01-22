"""
任务调度器
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.main import GitHubSentinel


class Scheduler:
    """任务调度器"""
    
    def __init__(self, config, sentinel: 'GitHubSentinel'):
        self.config = config
        self.sentinel = sentinel
        self.scheduler = BlockingScheduler()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """设置定时任务"""
        interval = self.config.get("schedule.interval", "daily")
        
        if interval == "daily":
            # 每日任务
            daily_time = self.config.get("schedule.daily_time", "09:00")
            hour, minute = map(int, daily_time.split(':'))
            
            # 添加更新仓库任务
            self.scheduler.add_job(
                self.sentinel.update_repositories,
                CronTrigger(hour=hour, minute=minute),
                id='daily_update',
                name='每日更新任务',
                replace_existing=True
            )
            logger.info(f"已设置每日更新任务: {daily_time}")
            
            # 添加生成每日报告任务（在更新后30分钟执行）
            report_hour = hour if minute < 30 else (hour + 1) % 24
            report_minute = (minute + 30) % 60
            
            self.scheduler.add_job(
                self.sentinel.generate_daily_reports,
                CronTrigger(hour=report_hour, minute=report_minute),
                id='daily_report',
                name='每日报告生成任务',
                replace_existing=True
            )
            logger.info(f"已设置每日报告生成任务: {report_hour:02d}:{report_minute:02d}")
            
        elif interval == "weekly":
            # 每周任务
            weekly_day = self.config.get("schedule.weekly_day", 0)  # 0 = Monday
            weekly_time = self.config.get("schedule.weekly_time", "09:00")
            hour, minute = map(int, weekly_time.split(':'))
            
            # 添加更新仓库任务
            self.scheduler.add_job(
                self.sentinel.update_repositories,
                CronTrigger(day_of_week=weekly_day, hour=hour, minute=minute),
                id='weekly_update',
                name='每周更新任务',
                replace_existing=True
            )
            logger.info(f"已设置每周更新任务: 星期{weekly_day} {weekly_time}")
            
            # 添加生成每周报告任务（在更新后30分钟执行）
            report_hour = hour if minute < 30 else (hour + 1) % 24
            report_minute = (minute + 30) % 60
            
            self.scheduler.add_job(
                self.sentinel.generate_daily_reports,
                CronTrigger(day_of_week=weekly_day, hour=report_hour, minute=report_minute),
                id='weekly_report',
                name='每周报告生成任务',
                replace_existing=True
            )
            logger.info(f"已设置每周报告生成任务: 星期{weekly_day} {report_hour:02d}:{report_minute:02d}")
        
        else:
            logger.warning(f"未知的调度间隔: {interval}，使用默认每日任务")
    
    def start(self):
        """启动调度器"""
        logger.info("任务调度器启动中...")
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("任务调度器已停止")
    
    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        logger.info("任务调度器已停止")
    
    def list_jobs(self):
        """列出所有任务"""
        jobs = self.scheduler.get_jobs()
        for job in jobs:
            logger.info(f"任务: {job.name} - 下次运行: {job.next_run_time}")
        return jobs
