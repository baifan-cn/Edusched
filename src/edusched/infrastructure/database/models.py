"""数据库模型定义。

使用SQLAlchemy 2.0风格定义数据库表结构，支持多租户和审计日志。
"""

from datetime import datetime, time
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    JSON,
    Numeric,
    Enum as SQLEnum,
    Index,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from edusched.domain.models import (
    WeekDay,
    PeriodType,
    ConstraintType,
    SchedulingStatus,
)

Base = declarative_base()


class BaseTable(Base):
    """基础表类。"""
    
    __abstract__ = True
    
    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    created_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


class School(BaseTable):
    """学校表。"""
    
    __tablename__ = "schools"
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="Asia/Shanghai")
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False)
    semester: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # 关系
    campuses: Mapped[List["Campus"]] = relationship("Campus", back_populates="school")
    calendars: Mapped[List["Calendar"]] = relationship("Calendar", back_populates="school")
    
    __table_args__ = (
        Index("idx_schools_tenant_code", "tenant_id", "code"),
        Index("idx_schools_academic_year", "tenant_id", "academic_year"),
    )


class Campus(BaseTable):
    """校区表。"""
    
    __tablename__ = "campuses"
    
    school_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("schools.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    travel_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_main: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # 关系
    school: Mapped["School"] = relationship("School", back_populates="campuses")
    buildings: Mapped[List["Building"]] = relationship("Building", back_populates="campus")
    
    __table_args__ = (
        Index("idx_campuses_school_code", "school_id", "code"),
        Index("idx_campuses_tenant_school", "tenant_id", "school_id"),
    )


class Building(BaseTable):
    """建筑表。"""
    
    __tablename__ = "buildings"
    
    campus_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("campuses.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    floors: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 关系
    campus: Mapped["Campus"] = relationship("Campus", back_populates="buildings")
    rooms: Mapped[List["Room"]] = relationship("Room", back_populates="building")
    
    __table_args__ = (
        Index("idx_buildings_campus_code", "campus_id", "code"),
        Index("idx_buildings_tenant_campus", "tenant_id", "campus_id"),
    )


class Room(BaseTable):
    """教室表。"""
    
    __tablename__ = "rooms"
    
    building_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("buildings.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    floor: Mapped[int] = mapped_column(Integer, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    room_type: Mapped[str] = mapped_column(String(50), nullable=False, default="classroom")
    features: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # 关系
    building: Mapped["Building"] = relationship("Building", back_populates="rooms")
    assignments: Mapped[List["Assignment"]] = relationship("Assignment", back_populates="room")
    
    __table_args__ = (
        Index("idx_rooms_building_code", "building_id", "code"),
        Index("idx_rooms_tenant_building", "tenant_id", "building_id"),
        Index("idx_rooms_capacity", "tenant_id", "capacity"),
        Index("idx_rooms_type", "tenant_id", "room_type"),
    )


class Teacher(BaseTable):
    """教师表。"""
    
    __tablename__ = "teachers"
    
    employee_id: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    max_hours_per_day: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    max_hours_per_week: Mapped[int] = mapped_column(Integer, nullable=False, default=40)
    preferred_time_slots: Mapped[List[time]] = mapped_column(
        JSON, nullable=False, default=list
    )
    unavailable_time_slots: Mapped[List[time]] = mapped_column(
        JSON, nullable=False, default=list
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # 关系
    sections: Mapped[List["Section"]] = relationship("Section", back_populates="teacher")
    homeroom_classes: Mapped[List["ClassGroup"]] = relationship(
        "ClassGroup", back_populates="homeroom_teacher"
    )
    
    __table_args__ = (
        Index("idx_teachers_employee_id", "tenant_id", "employee_id"),
        Index("idx_teachers_email", "tenant_id", "email"),
        Index("idx_teachers_department", "tenant_id", "department"),
    )


class Subject(BaseTable):
    """学科表。"""
    
    __tablename__ = "subjects"
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # 关系
    courses: Mapped[List["Course"]] = relationship("Course", back_populates="subject")
    
    __table_args__ = (
        Index("idx_subjects_code", "tenant_id", "code"),
        Index("idx_subjects_category", "tenant_id", "category"),
    )


class Course(BaseTable):
    """课程表。"""
    
    __tablename__ = "courses"
    
    subject_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    credits: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    hours_per_week: Mapped[int] = mapped_column(Integer, nullable=False)
    total_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # 关系
    subject: Mapped["Subject"] = relationship("Subject", back_populates="courses")
    sections: Mapped[List["Section"]] = relationship("Section", back_populates="course")
    
    __table_args__ = (
        Index("idx_courses_subject_code", "subject_id", "code"),
        Index("idx_courses_tenant_subject", "tenant_id", "subject_id"),
    )


class Grade(BaseTable):
    """年级表。"""
    
    __tablename__ = "grades"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 关系
    class_groups: Mapped[List["ClassGroup"]] = relationship("ClassGroup", back_populates="grade")
    
    __table_args__ = (
        Index("idx_grades_code", "tenant_id", "code"),
        Index("idx_grades_level", "tenant_id", "level"),
    )


class ClassGroup(BaseTable):
    """班级表。"""
    
    __tablename__ = "class_groups"
    
    grade_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("grades.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    student_count: Mapped[int] = mapped_column(Integer, nullable=False)
    homeroom_teacher_id: Mapped[Optional[UUID]] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("teachers.id"), nullable=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 关系
    grade: Mapped["Grade"] = relationship("Grade", back_populates="class_groups")
    homeroom_teacher: Mapped[Optional["Teacher"]] = relationship(
        "Teacher", back_populates="homeroom_classes"
    )
    sections: Mapped[List["Section"]] = relationship("Section", back_populates="class_group")
    
    __table_args__ = (
        Index("idx_class_groups_grade_code", "grade_id", "code"),
        Index("idx_class_groups_tenant_grade", "tenant_id", "grade_id"),
    )


class Section(BaseTable):
    """教学段表。"""
    
    __tablename__ = "sections"
    
    course_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("courses.id"), nullable=False
    )
    class_group_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("class_groups.id"), nullable=False
    )
    teacher_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("teachers.id"), nullable=False
    )
    room_id: Mapped[Optional[UUID]] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("rooms.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    hours_per_week: Mapped[int] = mapped_column(Integer, nullable=False)
    period_type: Mapped[PeriodType] = mapped_column(
        SQLEnum(PeriodType), nullable=False, default=PeriodType.REGULAR
    )
    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 关系
    course: Mapped["Course"] = relationship("Course", back_populates="sections")
    class_group: Mapped["ClassGroup"] = relationship("ClassGroup", back_populates="sections")
    teacher: Mapped["Teacher"] = relationship("Teacher", back_populates="sections")
    room: Mapped[Optional["Room"]] = relationship("Room", back_populates="assignments")
    assignments: Mapped[List["Assignment"]] = relationship("Assignment", back_populates="section")
    
    __table_args__ = (
        Index("idx_sections_course_code", "course_id", "code"),
        Index("idx_sections_teacher", "tenant_id", "teacher_id"),
        Index("idx_sections_class_group", "tenant_id", "class_group_id"),
        Index("idx_sections_period_type", "tenant_id", "period_type"),
    )


class Timeslot(BaseTable):
    """时间段表。"""
    
    __tablename__ = "timeslots"
    
    week_day: Mapped[WeekDay] = mapped_column(SQLEnum(WeekDay), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    period_number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_break: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 关系
    assignments: Mapped[List["Assignment"]] = relationship("Assignment", back_populates="timeslot")
    
    __table_args__ = (
        Index("idx_timeslots_week_day", "tenant_id", "week_day"),
        Index("idx_timeslots_period_number", "tenant_id", "period_number"),
        CheckConstraint("end_time > start_time", name="check_end_time_after_start"),
    )


class WeekPattern(BaseTable):
    """周模式表。"""
    
    __tablename__ = "week_patterns"
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_alternating: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    weeks: Mapped[List[int]] = mapped_column(JSON, nullable=False, default=list)
    
    # 关系
    assignments: Mapped[List["Assignment"]] = relationship("Assignment", back_populates="week_pattern")
    
    __table_args__ = (
        Index("idx_week_patterns_name", "tenant_id", "name"),
        Index("idx_week_patterns_alternating", "tenant_id", "is_alternating"),
    )


class Calendar(BaseTable):
    """日历表。"""
    
    __tablename__ = "calendars"
    
    school_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("schools.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False)
    semester: Mapped[str] = mapped_column(String(20), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    week_patterns: Mapped[List[UUID]] = mapped_column(JSON, nullable=False, default=list)
    holidays: Mapped[List[datetime]] = mapped_column(JSON, nullable=False, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # 关系
    school: Mapped["School"] = relationship("School", back_populates="calendars")
    timetables: Mapped[List["Timetable"]] = relationship("Timetable", back_populates="calendar")
    
    __table_args__ = (
        Index("idx_calendars_school_academic", "school_id", "academic_year", "semester"),
        Index("idx_calendars_tenant_school", "tenant_id", "school_id"),
        CheckConstraint("end_date > start_date", name="check_end_date_after_start"),
    )


class Constraint(BaseTable):
    """约束表。"""
    
    __tablename__ = "constraints"
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    constraint_type: Mapped[ConstraintType] = mapped_column(
        SQLEnum(ConstraintType), nullable=False
    )
    weight: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    __table_args__ = (
        Index("idx_constraints_name", "tenant_id", "name"),
        Index("idx_constraints_type", "tenant_id", "constraint_type"),
        CheckConstraint("weight >= 0 AND weight <= 1", name="check_weight_range"),
    )


class Timetable(BaseTable):
    """时间表表。"""
    
    __tablename__ = "timetables"
    
    calendar_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("calendars.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[SchedulingStatus] = mapped_column(
        SQLEnum(SchedulingStatus), nullable=False, default=SchedulingStatus.DRAFT
    )
    constraints: Mapped[List[UUID]] = mapped_column(JSON, nullable=False, default=list)
    meta_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    published_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # 关系
    calendar: Mapped["Calendar"] = relationship("Calendar", back_populates="timetables")
    assignments: Mapped[List["Assignment"]] = relationship("Assignment", back_populates="timetable")
    scheduling_jobs: Mapped[List["SchedulingJob"]] = relationship(
        "SchedulingJob", back_populates="timetable"
    )
    
    __table_args__ = (
        Index("idx_timetables_calendar", "calendar_id"),
        Index("idx_timetables_status", "tenant_id", "status"),
        Index("idx_timetables_tenant_calendar", "tenant_id", "calendar_id"),
    )


class Assignment(BaseTable):
    """分配表。"""
    
    __tablename__ = "assignments"
    
    timetable_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("timetables.id"), nullable=False
    )
    section_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("sections.id"), nullable=False
    )
    timeslot_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("timeslots.id"), nullable=False
    )
    room_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("rooms.id"), nullable=False
    )
    week_pattern_id: Mapped[Optional[UUID]] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("week_patterns.id"), nullable=True
    )
    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 关系
    timetable: Mapped["Timetable"] = relationship("Timetable", back_populates="assignments")
    section: Mapped["Section"] = relationship("Section", back_populates="assignments")
    timeslot: Mapped["Timeslot"] = relationship("Timeslot", back_populates="assignments")
    room: Mapped["Room"] = relationship("Room", back_populates="assignments")
    week_pattern: Mapped[Optional["WeekPattern"]] = relationship(
        "WeekPattern", back_populates="assignments"
    )
    
    __table_args__ = (
        Index("idx_assignments_timetable_section", "timetable_id", "section_id"),
        Index("idx_assignments_timeslot_room", "timeslot_id", "room_id"),
        Index("idx_assignments_tenant_timetable", "tenant_id", "timetable_id"),
        # 唯一约束：同一时间表下，教学段不能重复分配
        CheckConstraint(
            "EXISTS (SELECT 1 FROM assignments a2 WHERE a2.timetable_id = timetable_id AND a2.section_id = section_id AND a2.id != id)",
            name="check_unique_section_per_timetable"
        ),
    )


class SchedulingJob(BaseTable):
    """调度任务表。"""
    
    __tablename__ = "scheduling_jobs"
    
    timetable_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("timetables.id"), nullable=False
    )
    status: Mapped[SchedulingStatus] = mapped_column(
        SQLEnum(SchedulingStatus), nullable=False
    )
    progress: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False, default=0.0)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    result_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    worker_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # 关系
    timetable: Mapped["Timetable"] = relationship("Timetable", back_populates="scheduling_jobs")
    
    __table_args__ = (
        Index("idx_scheduling_jobs_timetable", "timetable_id"),
        Index("idx_scheduling_jobs_status", "tenant_id", "status"),
        Index("idx_scheduling_jobs_worker", "tenant_id", "worker_id"),
        CheckConstraint("progress >= 0 AND progress <= 1", name="check_progress_range"),
    )