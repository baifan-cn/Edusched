# State Management

## Store strategy

- Pinia stores per domain (teachers, rooms, sections, timetable)
- Derived/computed views for grid rendering

## Data layer

- Typed OpenAPI client
- Composables for queries/mutations
- Optimistic updates where safe; conflict-aware updates for timetable
