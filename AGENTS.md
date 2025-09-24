# Edusched Agent Guidelines

## Build/Lint/Test Commands

### Backend (Python)
- **Run tests**: `pytest` or `pytest tests/`  
- **Run single test**: `pytest tests/test_specific_file.py::test_function_name`
- **Run with coverage**: `pytest --cov=edusched --cov-report=term-missing`
- **Lint**: `black . && isort . && flake8 .`
- **Type check**: `mypy src/edusched`
- **Format**: `black . && isort .`

### Frontend (Vue/TypeScript)
- **Run tests**: `npm run test` or `vitest`
- **Run single test**: `vitest path/to/test.spec.ts`
- **Test coverage**: `npm run test:coverage`
- **Lint**: `npm run lint`
- **Type check**: `npm run type-check`
- **Format**: `npm run format`

## Code Style Guidelines

### Python
- **Imports**: Use `isort` with black profile, group imports (stdlib, third-party, first-party)
- **Formatting**: Black formatter, 88 line length, 4-space indentation
- **Types**: Strict mypy, type hints required, no untyped definitions
- **Naming**: snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants
- **Error handling**: Use specific exceptions, log errors with context, return structured error responses

### TypeScript/Vue
- **Imports**: Use auto-imports for Vue, Vue Router, Pinia; manual imports for others
- **Formatting**: Prettier, 2-space indentation, single quotes
- **Types**: Strict TypeScript, define interfaces/types, avoid `any`
- **Naming**: camelCase for variables/functions, PascalCase for components/interfaces
- **Vue patterns**: Composition API with `<script setup>`, reactive refs, proper typing

### General
- **Documentation**: Chinese docstrings for Python, JSDoc comments for TypeScript
- **Testing**: pytest for backend, vitest for frontend, aim for 80%+ coverage
- **Environment**: Use .env files, never commit secrets, validate config with pydantic
