# Component Architecture

## Structure

- `pages/` for route views
- `components/` for reusable UI (grid, dialogs, forms)
- `stores/` Pinia modules per domain
- `services/` API layer (OpenAPI client wrappers)

## Timetable workspace

- Virtualized grid with drag-drop
- Conflict overlays, filters, undo/redo
