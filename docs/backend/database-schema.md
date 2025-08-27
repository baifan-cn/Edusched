# Database Schema

## Overview

- Postgres 16+ as primary store
- Normalized core with JSONB extensions for constraints/preferences
- Event/audit tables for changes

## ERD (to be drafted)

- Entities: School, Campus, Term, WeekPattern, Calendar, Grade, ClassGroup, StudentGroup, Subject, CourseOffering, Section, Teacher, TeacherAvailability, TeacherContract, Room, RoomFeature, Timeslot, PeriodTemplate, Constraint, WeightProfile, Timetable, Assignment, Lock, SwapSuggestion

## Migration policy

- Alembic versioned migrations
- Backwards-compatible changes first; destructive changes gated
