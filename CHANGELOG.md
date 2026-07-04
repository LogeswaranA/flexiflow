# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.1] - 2026-07-04

### Added
- Unit test suite for the core engine: `WorkflowManager` (registration,
  event-driven and graph execution modes, missing-agent errors, empty
  graph) and `Agent.execute_task` (data_fetcher and summarizer roles,
  AI-provider and fallback paths, unknown role) — 17 tests.

### Fixed
- Removed stray debug `print()` calls from `Agent.execute_task`,
  guarded by a no-debug-output regression test.

## [0.1.0]

- Initial release.
