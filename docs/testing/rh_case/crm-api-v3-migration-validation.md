# CRM API v3 migration: validation summary

**Branch:** `feature/crm-api-v3-migration` | **Date:** 2026-08-25/26

> Full test transcripts, curl outputs, and Ansible run logs are in the PR comment.

## Test results

| ID | Scenario | Method | Result | Notes |
|----|----------|--------|--------|-------|
| T3b | REST v3 COMMENT: `POST /v3/cases/{n}/comments` | Ansible playbook | ✅ Pass | Primary path works |
| T3a | REST v3 CREATE: `POST /v3/cases` + GraphQL fallback | Ansible playbook | ✅ Pass | Both paths exercised; case created via fallback |
| T4 | Guard: invalid product name | Ansible playbook | ✅ Pass | Fails with: `"Verify product name and version match the Red Hat product catalog exactly."` |
| T7 | Attachment listing: `GET /v3/cases/{n}/attachments` | curl | ✅ Pass | HTTP 200; endpoint live |
| T8 | `rh_case_manager.py upload`: error handling | Python CLI | ✅ Pass | Non-2xx caught; JSON error to stderr; exit code 1 |
| T5 | Guard: non-existent case ID | Ansible playbook | ⚠️ Not conclusive | API did not reject invalid case; guard relies on downstream lookup |
| T6 | v3 attachment SINGLE_PUT, end to end | Ansible playbook | ⚠️ Not completed | Upload initiation reachable; field validation works. Completion blocked by infrastructure gap (see below) |
| T1 | v1 CREATE regression | n/a | N/A | v1 code paths removed in v1.3.0; test no longer applicable |
| T2 | v1 COMMENT regression | n/a | N/A | v1 code paths removed in v1.3.0; test no longer applicable |

## Gaps: tests not fully exercised

| Gap | Impact |
|-----|--------|
| v3 attachment `caseNumber` lookup service unavailable in test environment | T6 could not complete end to end; field validation and presigned URL flow verified against OpenAPI spec |
| v1 write endpoints not available in test environment | T1/T2 could not run; v1 code paths have since been removed entirely in v1.3.0 |

## Bugs found during testing

| ID | File | Line | Description | Fix applied |
|----|------|------|-------------|-------------|
| B1 | `roles/rh_case/tasks/7-attachment.yml` | 103 | `success_msg` accessed `.stat.size` without `default()`. Ansible pre-renders all task args before evaluating `that:`, so the template fails when the file is absent. | ✅ Added `\| default('?')` |
| B2 | `roles/rh_case/tasks/7-attachment.yml` | n/a | `caseId` used instead of `caseNumber` in POST body (OpenAPI spec requires `caseNumber`) | ✅ Fixed |
| B3 | `roles/rh_case/tasks/7-attachment.yml` | n/a | `uploadUrl` used instead of `presignedUrl` (field name per OpenAPI spec) | ✅ Fixed |
| B4 | `roles/rh_case/tasks/7-attachment.yml` | n/a | `fileSize` sent as string; spec requires integer | ✅ Added `\| int` filter |
