# Process Inbox Skill

## Description
Processes all pending items in the Obsidian vault `/Needs_Action/` folder.
For each item: reads the file, creates a `PLAN_*.md` in `/Plans/`, and updates `Dashboard.md`.
Sensitive actions (emails, payments) go to `/Pending_Approval/` instead of being executed directly.

## Usage
```
/process-inbox
```

## Steps
1. Scan `obsidian_vault/Needs_Action/` for all `.md` files with `status: pending`
2. For each file:
   - Read and understand the content
   - Create a `PLAN_<timestamp>_<name>.md` in `obsidian_vault/Plans/` with checkbox steps
   - If action requires sending email/payment/post → write to `obsidian_vault/Pending_Approval/` instead
   - Update `obsidian_vault/Dashboard.md` with the new activity
3. Move processed files from `Needs_Action/` to `Done/`

## Output
- New plan files in `obsidian_vault/Plans/`
- Updated `obsidian_vault/Dashboard.md`
- Approval requests in `obsidian_vault/Pending_Approval/` (for sensitive actions)
- Processed files moved to `obsidian_vault/Done/`
