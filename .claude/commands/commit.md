---
name: /commit
description: Smart commit workflow - analyze changes and generate conventional commit messages
usage: /commit [type]
example: /commit or /commit feat
---

# Smart Commit Workflow Command

When receiving `/commit [type]` command, follow these steps:

## Step 1: Analyze Changes
1. Run `git status` to see all changed files
2. Run `git diff` to see specific changes
3. Distinguish between staged and unstaged changes

## Step 2: Determine Commit Type
Auto-detect type based on changes (if user not specified):
- `test` - Test file changes
- `doc` - Documentation changes
- `chore` - Build, config, dependency related
- `feat` - New feature (default)
- `fix` - Bug fix
- `refactor` - Code refactoring
- `style` - Code style adjustments
- `perf` - Performance optimization

## Step 3: Determine Scope
Infer scope from file paths:
- `automation` - Browser automation and form filling related
- `workflow` - Workflow view and controller related
- `history` - History management related
- `models` - Data models related
- `views` - PyQt6 UI views related
- `controllers` - MVC controllers related
- `utils` - Utility functions related
- `docs` - Documentation related
- `core` - Core functionality
- `rules` - YAML rule configuration related

## Step 4: Generate Commit Message
Follow [Conventional Commits](https://www.conventionalcommits.org/) format:
```
<type>[optional scope]: <summary>

<bullet list of changes>
```

The commit message must include:
1. **Summary line**: One-line description in `<type>[optional scope]: <summary>` format
2. **Body bulleted list**: Each significant change listed as a separate bullet point

### Commit Message Structure:
```
<type>[optional scope]: <summary>

- <Bullet point 1>

- <Bullet point 2>

- <Bullet point 3>
...
```

### Bullet Point Format:
- Start with capital letter
- Use imperative mood ("Add", "Fix", "Move", not "Adds", "Fixed", "Moving")
- Be specific and concise
- No period at the end
- Maximum 80 characters per line

### Example:
```
refactor(automation): restructure form filler to support dropdown questions

- Add dropdown_selection method to FormFiller class

- Update fill_questions to handle dropdown question type

- Add CSS selector for WJX dropdown elements

- Update workflow controller to pass dropdown config
```

## Step 5: Wait for Confirmation
1. Display generated commit message
2. Ask user to confirm
3. Cancel if not accepted

## Step 6: Execute Commit
1. If unstaged changes exist, run `git add` first
2. Execute `git commit`
3. Display commit result

**IMPORTANT**: Do NOT include `Co-Authored-By:` in commit messages.

## Commit Message Format Reference
Based on project `cliff.toml` commit_parsers:

| Pattern | Group |
|---------|-------|
| `^feat` | 🚀 Features |
| `^fix` | 🐛 Bug Fixes |
| `^doc` | 📚 Documentation |
| `^perf` | ⚡ Performance |
| `^refactor` | 🚜 Refactor |
| `^style` | 🎨 Styling |
| `^test` | 🧪 Testing |
| `^chore` | ⚙️ Miscellaneous Tasks |

## Examples

### Example 1:
Input: `/commit`
- Analyze changes: `Codes/automation/form_filler.py`
- Auto-detect type: `feat`
- Auto-detect scope: `automation`
- Generate:
```
feat(automation): add dropdown selection support for WJX questionnaires

- Implement dropdown_selection method in FormFiller class

- Add probability-based option selection for dropdown questions

- Update fill_questions to handle dropdown type

- Add proper CSS selector for WJX dropdown elements
```
- Execute commit after confirmation

### Example 2:
Input: `/commit test`
- Specified type: `test`
- Generate:
```
test(automation): add unit tests for form filler dropdown functionality

- Test dropdown option selection with probability weights

- Verify CSS selector correctly targets WJX dropdown elements

- Test edge cases with empty and single-option dropdowns
```

### Example 3:
Input: `/commit doc`
- Analyze changes: `README.md`
- Generate:
```
doc: add comprehensive README documentation for V5

- Add project overview and feature description

- Document YAML configuration syntax

- Add installation and usage instructions

- Include troubleshooting section
```
