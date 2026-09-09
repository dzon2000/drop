# Copilot Instructions

## Project overview

Simple self-hosted file sharing service deployed as Docker container. Follow [Project Documentation](../docs/project_documentation.md) for details.

## Python conventions

- Target a current supported Python 3 release and use the standard library where it is sufficient.
- Use type hints for functions, methods, and important variables.
- Follow PEP 8 and use clear, descriptive names.
- Keep functions focused and avoid hidden global state.
- Handle expected errors explicitly; do not use broad `except Exception` blocks or silently ignore failures.
- Read configuration from environment variables when deployment-specific values are needed. Provide sensible development defaults.
- Do not commit secrets, local environment files, generated artifacts, or runtime data.

## Web application guidelines

- Validate all data received from clients at the application boundary.
- Return appropriate HTTP status codes and user-facing error messages.
- Escape or safely render user-provided content. Never assume pasted text is trusted HTML or JavaScript.
- Keep routes and business logic separate where that improves readability, but do not introduce unnecessary layers.
- Preserve privacy by avoiding unnecessary logging of user-provided paste contents.

## Testing

- Add focused tests for new behavior and important edge cases.
- Tests must be deterministic and must not depend on external services or wall-clock timing.
- Prefer testing public application behavior over implementation details.
- Run the narrowest relevant test command after changes, then expand validation when needed.

## Dependencies and tooling

- Check existing project configuration before adding a dependency or tool.
- Keep dependency changes minimal and pin or lock versions when the project’s packaging workflow supports it.
- Do not add a framework, database, frontend build system, or background worker unless the feature requires it.

## Documentation and changes

- Update the README when setup, configuration, or runtime behavior changes.
- Keep Docker configuration reproducible, small, and suitable for non-root execution where practical.
- Make surgical changes and avoid reformatting unrelated files.
