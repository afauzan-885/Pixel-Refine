# Rules: agen_docs Documentation Management

## Overview
The `agen_docs/` folder is the **single source of truth** for all project documentation, memories, experiences, rules, and knowledge for the Pixel Refine project.

## Storage Rules

### 1. Write to agen_docs
All new documentation **MUST** be stored in `agen_docs/` at the project root:
- **Path**: `e:\APP Developer\Pixel Refine\agen_docs\`
- **Format**: Markdown files (`.md`)
- **Naming**: Use descriptive names with numeric prefixes (e.g., `01_project_overview.md`)

### 2. Document Types
The following must be documented in `agen_docs/`:
- Project architecture and design decisions
- Technical implementations and algorithms
- Development practices and coding rules
- Known bugs, pitfalls, and solutions
- Build/compilation procedures
- Environment configuration
- API documentation
- Performance benchmarks and test results
- Lessons learned from development sessions

### 3. Update Policy
- If documentation exists but is outdated → **integrate** new information into existing file
- If documentation doesn't exist → **create** new file with appropriate naming
- **NEVER** delete existing documentation without explicit user approval
- **NEVER** overwrite existing files — always append or integrate

## Retrieval Rules

### 1. Context Loading
When starting a task or conversation, AI agents **SHOULD**:
1. Check `agen_docs/README.md` for documentation index
2. Load relevant documentation based on task context
3. Reference specific sections when explaining decisions

### 2. Memory Recall
Before making decisions or writing code, AI agents **SHOULD**:
1. Search `agen_docs/` for relevant experiences
2. Check `06_pitfalls_and_fixes.md` for known issues
3. Review `05_development_practices.md` for coding rules

### 3. Knowledge Integration
When learning new information during a session:
1. **Immediately** document it in appropriate `agen_docs/` file
2. **Update** memory system to reference `agen_docs/`
3. **Link** related documentation sections

## File Organization

### Current Structure
```
agen_docs/
├── README.md                      ← Index & quick reference
├── 01_project_overview.md         ← Status & capabilities
├── 02_tech_stack.md               ← Taichi AOT architecture
├── 03_mfdenoiser_architecture.md  ← MFDenoiser pipeline
├── 04_optical_flow.md             ← Optical flow modules
├── 05_development_practices.md    ← Coding rules
├── 06_pitfalls_and_fixes.md       ← Bugs & solutions
├── 07_build_and_compile.md        ← Compilation guides
└── 08_environment_config.md       ← Environment setup
```

### Naming Convention
- Use numeric prefix: `01_`, `02_`, etc.
- Use snake_case: `project_overview.md`
- Be descriptive: `optical_flow.md` not `of.md`

## Quality Standards

### 1. Documentation Quality
- **Clear**: Use simple, direct language
- **Complete**: Include all relevant details
- **Accurate**: Verify information before documenting
- **Up-to-date**: Update when information changes

### 2. Code Examples
- Include working code examples when possible
- Use syntax highlighting (```python, ```bash, etc.)
- Add comments for complex logic
- Reference actual file paths in the project

### 3. References
- Link to related documentation sections
- Reference actual source files with full paths
- Include commit hashes or dates for version-specific info

## AI Agent Behavior

### When Writing Code
1. Check `05_development_practices.md` for coding rules
2. Check `06_pitfalls_and_fixes.md` for known issues
3. Document new patterns in appropriate file

### When Debugging
1. Check `06_pitfalls_and_fixes.md` first
2. If issue not found, document solution after fixing
3. Update related documentation if needed

### When Planning
1. Check `03_mfdenoiser_architecture.md` for pipeline understanding
2. Check `04_optical_flow.md` for algorithm options
3. Document architectural decisions in appropriate file

### When Compiling
1. Check `07_build_and_compile.md` for compilation procedures
2. Follow documented compilation order
3. Update if new modules are added

## Migration Policy

### From agen.md (Legacy)
The file `agen.md` at project root is considered **legacy**. Going forward:
- New content goes to `agen_docs/`
- Existing content in `agen.md` should be migrated to appropriate `agen_docs/` files
- `agen.md` will be kept as backup until full migration is complete

### From skill.md (Legacy)
The file `skill.md` at project root is considered **legacy**. Going forward:
- New technical skills go to `agen_docs/`
- Existing content should be integrated into appropriate files
- `skill.md` will be kept as reference

## Enforcement

This rule is **mandatory** for all AI agents working on the Pixel Refine project. Violation of this rule (e.g., not documenting important decisions) will result in knowledge loss and context gaps.

---

**Last Updated**: 2026-06-20  
**Rule Version**: 1.0
