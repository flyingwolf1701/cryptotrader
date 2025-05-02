
# Product Manager Instructions

This project uses a structured two-level planning system to track all development work across epics and detailed tickets.

---

## 📁 Folder Structure Overview

```
project_plan/
├── project_roadmap.yaml          # Master list of all epics
└── epics/
    ├── 1_not_yet_started_epics/  # Epics not yet scoped in detail
    ├── 2_in_progress_epics/      # Currently active epic ticket files
    └── 3_completed_epics/        # Archived epics that are fully completed
```

---

## 🗺️ 1. Master Roadmap File — `project_roadmap.yaml`

This file contains the **complete list of epics**, regardless of status.

### Each epic entry includes:
- `id`: Unique identifier for referencing and tracking (e.g., `roadmap-3`)
- `title`: A short name for the epic
- `status`: One of `not yet started`, `in progress`, or `complete`
- `priority`: Priority level (`high`, `medium`, `low`)
- `domain`: Keywords to describe the area of work (e.g. `GUI`, `Trading`, `Analytics`)
- `reference_file`: A relative path to the YAML file with tickets for the epic, or `N/A` if not yet defined
- `description`: A one-line summary of the epic’s purpose

### Example Entry:
```yaml
- id: roadmap-2
  title: Wallet Database Persistence
  status: not yet started
  priority: high
  domain: Data Engineering, Wallet Sync
  reference_file: epics/1_not_yet_started_epics/wallet_database_persistence.yaml
  description: Store wallet balances in a local PostgreSQL database for sync and analysis.
```

---

## 🧱 2. Epic Ticket Files — `epics/<folder>/<epic_name>.yaml`

Each epic, when ready to be developed, gets its own ticket file placed inside one of the three status folders. These files contain detailed task breakdowns.

### Ticket Structure:
```yaml
tickets:
  - id: 1
    title: Set up local PostgreSQL
    status: not yet started
    description: Install and configure PostgreSQL for local development.
    acceptance_criteria:
      - PostgreSQL is installed
      - Accessible with default credentials via SQLAlchemy
```

- Use `status` to track progress (`not yet started`, `in progress`, `complete`)
- Add `acceptance_criteria` for clarity and handoff confidence
- IDs are scoped per-epic (they don’t need to be globally unique)

---

## 🧭 Workflow Guidelines

### Epic Lifecycle
1. **New ideas** → Add as an entry in `project_roadmap.yaml`, set `status: not yet started`, and `reference_file: N/A`.
2. **Prioritized work** → Move epic to `epics/2_in_progress_epics/` and create its ticket YAML file.
3. **Completed work** → Move epic file to `epics/3_completed_epics/` and update its `status: complete` in the roadmap.

### Best Practices
- Keep `project_roadmap.yaml` as the source of truth for high-level planning.
- Only create ticket YAMLs when you’re ready to break down the work.
- Be descriptive but concise—avoid cluttering roadmap with full details.
- Keep domain tags consistent for easy filtering (e.g., `DEX`, `ML`, `Research`, `CEX`, `Bot`, `Storage`).
- Use `reference_file` to directly link epic entries to their breakdowns.
- Update epic status and locations as work progresses.

---

## 🎯 Benefits of This Structure

- Provides clear, modular visibility into future, active, and finished work
- Prevents overplanning by deferring detail until it's needed
- Keeps your workspace clean, scalable, and easily browsable
- Facilitates use of automation later (e.g., generating boards or views)