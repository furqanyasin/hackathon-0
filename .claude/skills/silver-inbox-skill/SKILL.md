# Silver Inbox Processor Skill

## Description
Full Silver-tier inbox processing: reads Needs_Action/, creates detailed Plan.md files,
routes sensitive actions to Pending_Approval/, posts to LinkedIn (with approval),
and updates Dashboard.md with a full activity summary.

## Usage
```
/process-inbox-silver
```

## Steps
1. Scan `obsidian_vault/Needs_Action/` for all `.md` files with `status: pending`
2. Read `obsidian_vault/Company_Handbook.md` for rules
3. For each pending item:
   - Create detailed `PLAN_*.md` in `obsidian_vault/Plans/` with typed checkbox steps
   - Route to `obsidian_vault/Pending_Approval/` if: email reply, payment, social post
   - Auto-process if: reading, summarizing, logging
4. Check `obsidian_vault/Approved/` for approved actions and execute via MCP
5. Generate a LinkedIn post draft from `obsidian_vault/Business_Goals.md` → route to approval
6. Update `obsidian_vault/Dashboard.md` with full activity summary
7. Move all processed files to `obsidian_vault/Done/`

## Output
- `obsidian_vault/Plans/PLAN_*.md` — detailed action plans
- `obsidian_vault/Pending_Approval/` — items needing human sign-off
- `obsidian_vault/Dashboard.md` — updated with latest activity
- `obsidian_vault/Done/` — archived processed items
- `obsidian_vault/Logs/YYYY-MM-DD.json` — audit trail
