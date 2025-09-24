"""领域事件处理器。

处理领域产生的事件，执行相应的业务逻辑。
"""

import logging
from typing import List, Optional
from uuid import UUID

from ...domain.models import School, Teacher, Timetable, Assignment
from ...infrastructure.cache import CacheService
from ...infrastructure.external import NotificationService
from ..base import DomainEvent, IEventHandler

logger = logging.getLogger(__name__)


class SchoolEventHandler(IEventHandler):
    """学校相关事件处理器。"""

    def __init__(
        self,
        cache_service: CacheService,
        notification_service: NotificationService
    ):
        self.cache_service = cache_service
        self.notification_service = notification_service

    async def handle(self, event: DomainEvent) -> None:
        """处理学校事件。"""
        try:
            if event.event_type == "school_created":
                await self._handle_school_created(event)
            elif event.event_type == "school_updated":
                await self._handle_school_updated(event)
            elif event.event_type == "school_deleted":
                await self._handle_school_deleted(event)
            elif event.event_type == "school_activated":
                await self._handle_school_activated(event)
            elif event.event_type == "school_deactivated":
                await self._handle_school_deactivated(event)

        except Exception as e:
            logger.error(f"Error handling school event {event.event_type}: {e}", exc_info=True)

    async def _handle_school_created(self, event: DomainEvent) -> None:
        """处理学校创建事件。"""
        school_data = event.data
        logger.info(f"School created: {school_data.get('name')}")

        # 清除相关缓存
        await self.cache_service.delete_pattern(f"schools:*")

        # 发送通知
        if school_data.get("created_by"):
            await self.notification_service.send_notification(
                recipient=school_data["created_by"],
                title="学校创建成功",
                message=f"学校 {school_data['name']} 已成功创建",
                data={"event": event.dict()}
            )

    async def _handle_school_updated(self, event: DomainEvent) -> None:
        """处理学校更新事件。"""
        school_data = event.data
        logger.info(f"School updated: {school_data.get('name')}")

        # 清除相关缓存
        await self.cache_service.delete_pattern(f"schools:*")
        await self.cache_service.delete(f"school:{event.aggregate_id}")

    async def _handle_school_deleted(self, event: DomainEvent) -> None:
        """处理学校删除事件。"""
        logger.info(f"School deleted: {event.aggregate_id}")

        # 清除相关缓存
        await self.cache_service.delete_pattern(f"schools:*")
        await self.cache_service.delete(f"school:{event.aggregate_id}")

    async def _handle_school_activated(self, event: DomainEvent) -> None:
        """处理学校激活事件。"""
        logger.info(f"School activated: {event.aggregate_id}")

        # 清除相关缓存
        await self.cache_service.delete_pattern(f"schools:*")
        await self.cache_service.delete(f"school:{event.aggregate_id}")

    async def _handle_school_deactivated(self, event: DomainEvent) -> None:
        """处理学校停用事件。"""
        logger.info(f"School deactivated: {event.aggregate_id}")

        # 清除相关缓存
        await self.cache_service.delete_pattern(f"schools:*")
        await self.cache_service.delete(f"school:{event.aggregate_id}")


class TeacherEventHandler(IEventHandler):
    """教师相关事件处理器。"""

    def __init__(
        self,
        cache_service: CacheService,
        notification_service: NotificationService
    ):
        self.cache_service = cache_service
        self.notification_service = notification_service

    async def handle(self, event: DomainEvent) -> None:
        """处理教师事件。"""
        try:
            if event.event_type == "teacher_created":
                await self._handle_teacher_created(event)
            elif event.event_type == "teacher_updated":
                await self._handle_teacher_updated(event)
            elif event.event_type == "teacher_deleted":
                await self._handle_teacher_deleted(event)
            elif event.event_type == "teacher_workload_updated":
                await self._handle_teacher_workload_updated(event)

        except Exception as e:
            logger.error(f"Error handling teacher event {event.event_type}: {e}", exc_info=True)

    async def _handle_teacher_created(self, event: DomainEvent) -> None:
        """处理教师创建事件。"""
        teacher_data = event.data
        logger.info(f"Teacher created: {teacher_data.get('name')}")

        # 清除相关缓存
        await self.cache_service.delete_pattern(f"teachers:*")
        await self.cache_service.delete_pattern(f"departments:*")

    async def _handle_teacher_updated(self, event: DomainEvent) -> None:
        """处理教师更新事件。"""
        teacher_data = event.data
        logger.info(f"Teacher updated: {teacher_data.get('name')}")

        # 清除相关缓存
        await self.cache_service.delete_pattern(f"teachers:*")
        await self.cache_service.delete(f"teacher:{event.aggregate_id}")

    async def _handle_teacher_deleted(self, event: DomainEvent) -> None:
        """处理教师删除事件。"""
        logger.info(f"Teacher deleted: {event.aggregate_id}")

        # 清除相关缓存
        await self.cache_service.delete_pattern(f"teachers:*")
        await self.cache_service.delete(f"teacher:{event.aggregate_id}")

    async def _handle_teacher_workload_updated(self, event: DomainEvent) -> None:
        """处理教师工作量更新事件。"""
        logger.info(f"Teacher workload updated: {event.aggregate_id}")

        # 清除相关缓存
        await self.cache_service.delete(f"teacher:{event.aggregate_id}:workload")


class TimetableEventHandler(IEventHandler):
    """时间表相关事件处理器。"""

    def __init__(
        self,
        cache_service: CacheService,
        notification_service: NotificationService
    ):
        self.cache_service = cache_service
        self.notification_service = notification_service

    async def handle(self, event: DomainEvent) -> None:
        """处理时间表事件。"""
        try:
            if event.event_type == "timetable_created":
                await self._handle_timetable_created(event)
            elif event.event_type == "timetable_updated":
                await self._handle_timetable_updated(event)
            elif event.event_type == "timetable_published":
                await self._handle_timetable_published(event)
            elif event.event_type == "timetable_unpublished":
                await self._handle_timetable_unpublished(event)
            elif event.event_type == "scheduling_started":
                await self._handle_scheduling_started(event)
            elif event.event_type == "scheduling_completed":
                await self._handle_scheduling_completed(event)
            elif event.event_type == "scheduling_failed":
                await self._handle_scheduling_failed(event)
            elif event.event_type == "assignment_created":
                await self._handle_assignment_created(event)
            elif event.event_type == "assignment_updated":
                await self._handle_assignment_updated(event)
            elif event.event_type == "assignment_deleted":
                await self._handle_assignment_deleted(event)

        except Exception as e:
            logger.error(f"Error handling timetable event {event.event_type}: {e}", exc_info=True)

    async def _handle_timetable_created(self, event: DomainEvent) -> None:
        """处理时间表创建事件。"""
        timetable_data = event.data
        logger.info(f"Timetable created: {timetable_data.get('name')}")

        # 清除相关缓存
        await self.cache_service.delete_pattern(f"timetables:*")

    async def _handle_timetable_updated(self, event: DomainEvent) -> None:
        """处理时间表更新事件。"""
        logger.info(f"Timetable updated: {event.aggregate_id}")

        # 清除相关缓存
        await self.cache_service.delete(f"timetable:{event.aggregate_id}")
        await self.cache_service.delete_pattern(f"timetable:{event.aggregate_id}:*")

    async def _handle_timetable_published(self, event: DomainEvent) -> None:
        """处理时间表发布事件。"""
        timetable_data = event.data
        logger.info(f"Timetable published: {timetable_data.get('name')}")

        # 清除相关缓存
        await self.cache_service.delete_pattern(f"timetables:*")
        await self.cache_service.delete_pattern(f"published_timetables:*")

        # 发送通知
        if timetable_data.get("published_by"):
            await self.notification_service.send_notification(
                recipient=timetable_data["published_by"],
                title="时间表发布成功",
                message=f"时间表 {timetable_data['name']} 已成功发布",
                data={"event": event.dict()}
            )

    async def _handle_timetable_unpublished(self, event: DomainEvent) -> None:
        """处理时间表取消发布事件。"""
        logger.info(f"Timetable unpublished: {event.aggregate_id}")

        # 清除相关缓存
        await self.cache_service.delete_pattern(f"published_timetables:*")

    async def _handle_scheduling_started(self, event: DomainEvent) -> None:
        """处理调度开始事件。"""
        logger.info(f"Scheduling started for timetable: {event.aggregate_id}")

        # 清除相关缓存
        await self.cache_service.delete(f"timetable:{event.aggregate_id}:status")

    async def _handle_scheduling_completed(self, event: DomainEvent) -> None:
        """处理调度完成事件。"""
        logger.info(f"Scheduling completed for timetable: {event.aggregate_id}")

        # 清除相关缓存
        await self.cache_service.delete(f"timetable:{event.aggregate_id}:*")

    async def _handle_scheduling_failed(self, event: DomainEvent) -> None:
        """处理调度失败事件。"""
        error_message = event.data.get("error_message", "Unknown error")
        logger.error(f"Scheduling failed for timetable {event.aggregate_id}: {error_message}")

        # 清除相关缓存
        await self.cache_service.delete(f"timetable:{event.aggregate_id}:status")

    async def _handle_assignment_created(self, event: DomainEvent) -> None:
        """处理分配创建事件。"""
        logger.info(f"Assignment created: {event.aggregate_id}")

        # 清除相关缓存
        timetable_id = event.data.get("timetable_id")
        if timetable_id:
            await self.cache_service.delete(f"timetable:{timetable_id}:assignments")
            await self.cache_service.delete(f"timetable:{timetable_id}:stats")

    async def _handle_assignment_updated(self, event: DomainEvent) -> None:
        """处理分配更新事件。"""
        logger.info(f"Assignment updated: {event.aggregate_id}")

        # 清除相关缓存
        timetable_id = event.data.get("timetable_id")
        if timetable_id:
            await self.cache_service.delete(f"timetable:{timetable_id}:assignments")
            await self.cache_service.delete(f"timetable:{timetable_id}:stats")

    async def _handle_assignment_deleted(self, event: DomainEvent) -> None:
        """处理分配删除事件。"""
        logger.info(f"Assignment deleted: {event.aggregate_id}")

        # 清除相关缓存
        timetable_id = event.data.get("timetable_id")
        if timetable_id:
            await self.cache_service.delete(f"timetable:{timetable_id}:assignments")
            await self.cache_service.delete(f"timetable:{timetable_id}:stats")


# 事件处理器映射
EVENT_HANDLERS = {
    # School events
    "school_created": SchoolEventHandler,
    "school_updated": SchoolEventHandler,
    "school_deleted": SchoolEventHandler,
    "school_activated": SchoolEventHandler,
    "school_deactivated": SchoolEventHandler,

    # Teacher events
    "teacher_created": TeacherEventHandler,
    "teacher_updated": TeacherEventHandler,
    "teacher_deleted": TeacherEventHandler,
    "teacher_workload_updated": TeacherEventHandler,

    # Timetable events
    "timetable_created": TimetableEventHandler,
    "timetable_updated": TimetableEventHandler,
    "timetable_published": TimetableEventHandler,
    "timetable_unpublished": TimetableEventHandler,
    "scheduling_started": TimetableEventHandler,
    "scheduling_completed": TimetableEventHandler,
    "scheduling_failed": TimetableEventHandler,
    "assignment_created": TimetableEventHandler,
    "assignment_updated": TimetableEventHandler,
    "assignment_deleted": TimetableEventHandler,
}