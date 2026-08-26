# SOS Report Role — E2E Validation Matrix

End-to-end test evidence for the `sos_report` role restructure.
All tests ran against real infrastructure — no mocked targets.

> **Full test run logs** (execution output, per-stage results, and bug details)
> are in the [PR comment on #24](https://github.com/redhat-cop/infra.support_assist/pull/24).

## Test Environment

| Component          | Version / Detail                    |
| ------------------ | ----------------------------------- |
| Ansible Core       | 2.21.x                              |
| Collection         | `infra.support_assist` 1.2.0 (fork) |
| `oc` CLI           | 4.22.x                              |
| Control Node OS    | Fedora Linux 44                     |
| Container Runtime  | Podman (rootless)                   |

## Test Results

| # | Test Case                                   | Status  | Notes                       |
|---|---------------------------------------------|---------|-----------------------------|
| 1 | `ocp_debug`: Single Worker Node             | PASS    | SOS collected (~25 MB)      |
| 2 | `ocp_debug`: Happy Path + Fallback Enabled  | PASS    | Fallback not triggered      |
| 3 | SSH Fallback: Triggered, SSH Unreachable    | PASS    | Correct error path          |
| 4 | SSH Fallback: Disabled + `oc debug` Fail    | PASS    | Correct error message       |
| 5 | `ocp_debug`: Auto-Discovery + Label Selector| PASS    | 3 workers, 3 SOS reports    |
| 6 | `ocp_debug`: Auto-Discovery All Nodes       | PASS    | 6 nodes (masters + workers) |
| 7 | `standard`: RHEL Host (+ sub-tests 7b/c/d) | PASS    | 11 MB SOS from RHEL 9.8     |
| 8 | `ocp_ssh`: SSH to RHCOS Node               | Blocked | No direct SSH to RHCOS lab  |
| 9 | `ocp_debug`: Invalid Node Name             | PASS    | Fails fast at Stage 02      |
|10 | `ocp_debug`: Expired Token                 | PASS    | Fails fast at Stage 01      |

**Executed:** 9 / 10 — all passed (1 blocked by lab infrastructure, unmodified code path).

## Bugs Found and Fixed During Testing

| # | Bug Summary                                                        | Fixed |
|---|--------------------------------------------------------------------|-------|
| 1 | `ansible_connection: ssh` missing in `add_host` for SSH fallback   | Yes   |
| 2 | `ignore_unreachable` on `delegate_to` skips all subsequent tasks   | Yes   |
| 3 | `failed_when: false` masks actual failure state in registered var  | Yes   |
| 4 | `wait_for` TCP check incompatible with bastion/ProxyJump           | Yes   |
| 5 | `UNREACHABLE` status bypasses `block/rescue`, hides error message  | Yes   |
| 6 | `delegate_to: localhost` inherits `--become`, root-owned dirs fail | Yes   |
