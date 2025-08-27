# Data Model

## Core entities

- School, Campus, Term, WeekPattern, Calendar
- Grade, ClassGroup, StudentGroup
- Subject, CourseOffering, Section
- Teacher, TeacherAvailability, TeacherContract
- Room, RoomFeature
- Timeslot, PeriodTemplate
- Constraint, WeightProfile
- Timetable, Assignment, Lock/Pin, SwapSuggestion

## Relationships

- One School → many Campuses → Rooms
- Term → Calendar → WeekPattern
- CourseOffering → multiple Sections
- Section ↔ Teacher(s) ↔ Room(s)
- StudentGroup ↔ Sections (avoid clashes)

## Storage strategy

- Postgres normalized core; JSONB extensions for flexible constraints
- Index lookup‑heavy columns; optimistic locking on timetables
- Event audit tables for changes
