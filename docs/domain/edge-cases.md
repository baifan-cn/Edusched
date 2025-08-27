# Edge Cases

- Alternating weeks and block schedules
- Fixed periods and assemblies
- Shared teachers and partial availability
- Labs/equipment dependencies
- Max consecutive lessons; lunch breaks
- Multi‑campus travel times
- Split or combined classes; bilingual/co‑teach
- Exam weeks and special events
- Last‑minute changes and overrides

## Risks and mitigations

- Data quality variability → strong import validation and dry‑run
- Large instance runtime → timeouts, progressive relaxation, warm starts, parallelization
- Change management → training materials and manual override UX
- Complex timetables → flexible constraint DSL with JSONB extensions
