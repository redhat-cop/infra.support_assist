# SOS Report Role — E2E Validation Matrix

End-to-end test evidence for the `sos_report` role restructure.
All tests were executed against real infrastructure — no mocked targets.

## Test Environment

| Component          | Version / Detail                         |
| ------------------ | ---------------------------------------- |
| Ansible Core       | 2.21.x                                   |
| Collection         | `infra.support_assist` 1.2.0 (fork)      |
| `oc` CLI           | 4.22.x                                   |
| Control Node OS    | Fedora Linux 44                          |
| Container Runtime  | Podman (rootless)                        |

---

## Test Case 1 — `ocp_debug` Mode: Single Worker Node

**Objective:** Validate the full `oc debug` pipeline — login, node discovery,
SOS generation via support-tools container, fetch via `oc debug -- cat`,
cleanup, and summary report rendering.

### Parameters

```yaml
# Playbook used
playbook: playbooks/sos_report_ocp.yml

# Extra variables
sos_report_mode: ocp_debug
sos_report_ocp_token: "<redacted>"                          # valid cluster token
sos_report_ocp_server_url: "https://api.<cluster>.<region>.aroapp.io:6443"
sos_report_ocp_nodes:
  - "<cluster>-<id>-worker-<zone>-<suffix>"                 # single worker node
sos_report_ocp_validate_ssl: true
sos_report_dest: /tmp/sos_reports
sos_report_cleanup: true
upload: false                                               # skip Red Hat Case upload
```

### Execution Command

```bash
ansible-playbook playbooks/sos_report_ocp.yml \
  -e '{"sos_report_ocp_token":"<redacted>","sos_report_ocp_server_url":"https://api.<cluster>.<region>.aroapp.io:6443","sos_report_ocp_nodes":["<worker-node-name>"],"upload":false}'
```

### Target Infrastructure

| Property              | Value (Generic)                                   |
| --------------------- | ------------------------------------------------- |
| Platform              | Azure Red Hat OpenShift (ARO)                     |
| OCP Version           | 4.20.x                                            |
| Kubernetes Version    | v1.33.x                                            |
| Cluster Auth          | `kube:admin`                                       |
| Region                | Azure East US                                      |
| Node Role             | Worker                                             |
| Node Count (targeted) | 1                                                  |

### Results

| Metric                  | Value                  |
| ----------------------- | ---------------------- |
| Playbook Result         | `ok=41, changed=5, failed=0, skipped=15` |
| SOS Report Size         | ~25 MB (`.tar.xz`)    |
| Collection Duration     | ~4 minutes             |
| Report Destination      | `/tmp/sos_reports/<node-name>/` |
| Summary Report Rendered | Yes                    |
| Cleanup Executed        | Yes (confirmed no leftover files on node) |

### Stage Validation

| Stage                       | Status | Notes                                        |
| --------------------------- | ------ | -------------------------------------------- |
| `[STAGE 00 - Setup]`       | PASS   | Destination directory created on control node |
| `[Preflight - OCP Assert]` | PASS   | Mode, image, token, server URL, `oc` binary  |
| `[STAGE 01 - OCP Login]`   | PASS   | `oc login` + `oc whoami` succeeded           |
| `[STAGE 02 - Node Discovery]` | PASS | User-provided node validated via `oc get node` |
| `[STAGE 03 - Collect] 3.1` | PASS   | SOS generated on node via `oc debug` + `podman run` |
| `[STAGE 03 - Collect] 3.3` | PASS   | Report filename located via `oc debug -- ls` |
| `[STAGE 03 - Collect] 3.6` | PASS   | Binary fetched via `oc debug -- cat`, size > 0 |
| `[STAGE 03 - Collect] 3.7` | PASS   | Cleanup removed `sosreport-*.tar.xz` from node |
| Summary Report             | PASS   | Template rendered with correct mode, cluster, node info |
| Banner Rendering           | PASS   | Dynamic separators rendered at start/end of each stage |

### Artifacts

```text
/tmp/sos_reports/
└── <node-name>/
    └── sosreport-<node-label>-<date>-<hash>.tar.xz   (~25 MB)
```

---

## Test Case 2 — `ocp_debug` Mode: Happy Path with SSH Fallback Enabled

**Status:** Executed — PASS

**Objective:** Validate that enabling `sos_report_ocp_fallback_ssh` does NOT
interfere with the happy path when `oc debug` succeeds. The `block/rescue`
wrapper in `3-collect.yml` must be transparent to the normal flow.

### Parameters

```yaml
sos_report_mode: ocp_debug
sos_report_ocp_nodes:
  - "<worker-node-name>"
sos_report_ocp_fallback_ssh: true                           # enabled but should NOT trigger
upload: false
```

### Results

| Metric              | Value                                        |
| ------------------- | -------------------------------------------- |
| Playbook Result     | `ok=41, changed=4, failed=0, rescued=0`      |
| SOS Report Size     | ~25 MB (`.tar.xz`)                           |
| Fallback Triggered  | No (`rescued=0`)                             |
| Summary Shows       | `SSH Fallback: Enabled` (no fallback nodes)  |

### Key Verification

- `rescued=0` confirms the rescue block was never entered.
- The summary report correctly displays "SSH Fallback: Enabled" without
  listing any fallback nodes.
- All stages executed identically to Test Case 1.

---

## Test Case 3 — SSH Fallback: Triggered, SSH Unreachable (Error Path)

**Status:** Executed — PASS (expected failure with correct error messages)

**Objective:** Validate the SSH fallback mechanism activation when `oc debug`
fails, through to the SSH connectivity pre-check. In this test, the nodes are
in a private Azure VNET without direct network access from the control node,
so SSH is expected to fail — validating the error path and messaging.

The SSH pre-check at step `3.F.4` uses `ansible.builtin.command` with the
`ssh` binary directly on the control node (no `delegate_to`). This avoids
Ansible's `UNREACHABLE` status, which bypasses `block/rescue` and produces
cryptic output. See Bug #5 below for the full context.

### Parameters

```yaml
sos_report_mode: ocp_debug
sos_report_ocp_nodes:
  - "<worker-node-name>"
sos_report_ocp_support_tools_image: "nonexistent-image:latest"  # intentional failure trigger
sos_report_ocp_fallback_ssh: true
upload: false
```

### Results

| Metric                 | Value                                               |
| ---------------------- | --------------------------------------------------- |
| Playbook Result        | `ok=34, changed=2, failed=1, rescued=2, ignored=1`  |
| `oc debug` Outcome     | FAILED (image not found, `rc=1`)                    |
| Rescue Block Activated | Yes, banner displayed correctly                     |
| Node IP Resolved       | Yes, via `oc get node -o jsonpath` -> `10.0.2.x`    |
| `add_host` Executed    | Yes, `ansible_connection: ssh` set correctly        |
| SSH Pre-Check (F.4)    | FAILED, `Connection timed out` (rc=255, ignored)    |
| Assert SSH (F.5)       | FAILED, custom troubleshooting message displayed    |
| `unreachable` count    | **0**, no UNREACHABLE status (Bug #5 fixed)         |

### Stage Validation

| Stage                           | Status | Notes                                                     |
| ------------------------------- | ------ | --------------------------------------------------------- |
| `oc debug` SOS generation       | FAIL   | Intentional, bad image triggers `rc=1`                    |
| `3.R.0` Fallback evaluation     | PASS   | Banner: oc debug FAILED, SSH fallback ENABLED             |
| `3.F.1` Get node IP             | PASS   | Resolved via `oc get node` -> `10.0.2.x`                  |
| `3.F.2` Assert IP resolved      | PASS   | IP is non-empty                                           |
| `3.F.3` Add to inventory        | PASS   | `ansible_connection: ssh` explicitly set                  |
| `3.F.4` SSH pre-check           | FAIL   | Expected, `ssh` command timed out, `...ignoring`          |
| `3.F.5` Assert SSH connectivity | FAIL   | Custom message with 5 troubleshooting steps + SSH stderr  |

### Error Message Produced

```text
❌ FAILED! Oh. No! => SSH fallback cannot connect to node '<node-name>'
(IP: 10.0.2.x). Both 'oc debug' and SSH methods failed for this node.
Troubleshoot:
1) Network: Is the node reachable? Check VPN, VNET peering, bastion (ProxyJump).
2) SSH auth: Is the key correct? (sos_report_ocp_ssh_key or ssh-agent / AAP Machine credential).
3) SSH user: Is 'core' valid on the RHCOS node? (default: 'core').
4) Bastion: Set sos_report_ocp_ssh_extra_args='-o ProxyJump=bastion.example.com' if needed.
5) Firewall: Is port 22 open on the node? (NSG, firewall rules).
SSH output: ssh: connect to host 10.0.2.x port 22: Connection timed out
```

### Prerequisites for SSH Fallback to Succeed

For the SSH fallback to work in production, the following are required:

1. **Network connectivity** — Control node must reach the RHCOS node's
   internal IP on port 22 (via VPN, VNET peering, bastion host, or direct route).
   When using a bastion/jump host, set `sos_report_ocp_ssh_extra_args` to
   `-o ProxyJump=bastion.example.com`.
2. **SSH key** — Key-based auth configured for the `core` user on RHCOS
   (password auth is not available). Provide via `sos_report_ocp_ssh_key`
   or have the key loaded in `ssh-agent`. In AAP, leave `sos_report_ocp_ssh_key`
   empty — Machine credentials inject the key via `ssh-agent` automatically.
3. **`ansible_connection: ssh`** — Must be set explicitly on the dynamic host
   because the `ocp_debug` playbook uses `connection: local`. Without it,
   `delegate_to` inherits the local connection and runs commands on the
   control node instead of the RHCOS node (handled automatically by `add_host`).

---

## Test Case 4 — SSH Fallback: Disabled + `oc debug` Failure

**Status:** Executed — PASS (expected failure with correct error message)

**Objective:** Validate that when `sos_report_ocp_fallback_ssh: false` and
`oc debug` fails, the playbook stops immediately with a clear message
explaining how to enable the fallback.

### Parameters

```yaml
sos_report_mode: ocp_debug
sos_report_ocp_nodes:
  - "<worker-node-name>"
sos_report_ocp_support_tools_image: "nonexistent-image:latest"  # intentional failure trigger
sos_report_ocp_fallback_ssh: false                              # disabled
upload: false
```

### Results

| Metric                 | Value                                         |
| ---------------------- | --------------------------------------------- |
| Playbook Result        | `ok=28, changed=1, failed=1, rescued=2`       |
| Rescue Block Activated | Yes — banner: `SSH fallback DISABLED`          |
| Fallback Attempted     | No — `3.R.1` raised `ansible.builtin.fail`    |

### Error Message Produced

```text
❌ FAILED! Oh. No! => SOS Report collection via 'oc debug' failed on node
'<node-name>' and SSH fallback is disabled (sos_report_ocp_fallback_ssh: false).
Enable it with '-e sos_report_ocp_fallback_ssh=true' and ensure SSH access
to the node is available.
```

---

## Test Case 5 — `ocp_debug`: Auto-Discovery with Label Selector

**Status:** Executed — PASS

**Objective:** Validate auto-discovery of nodes via `sos_report_ocp_node_selector`
when `sos_report_ocp_nodes` is empty.

### Parameters

```yaml
sos_report_mode: ocp_debug
sos_report_ocp_nodes: []                                    # trigger auto-discovery
sos_report_ocp_node_selector: "node-role.kubernetes.io/worker="
upload: false
```

### Results

| Metric              | Value                                     |
| ------------------- | ----------------------------------------- |
| Playbook Result     | `ok=69, changed=12, failed=0, rescued=0`  |
| Nodes Discovered    | 3 workers (label selector match)          |
| Discovery Branch    | `2.1.x` (auto-discover), NOT `2.2.x`     |
| SOS Reports         | 3 collected (25.45, 23.81, 17.47 MB)      |
| Summary Report      | Yes, 3 files listed                       |
| Cleanup Executed    | Yes                                       |

### Stage Validation

| Stage                       | Status | Notes                                           |
| --------------------------- | ------ | ----------------------------------------------- |
| Preflight assertions        | PASS   | Mode, image, token, oc binary                   |
| OCP Login (Stage 01)        | PASS   | Logged in as `kube:admin`                       |
| Auto-Discovery (2.1.1)      | PASS   | `oc get nodes -l worker=` returned 3 nodes      |
| Set node list (2.1.2)       | PASS   | List set to 3 discovered workers                |
| Assert nodes found (2.1.3)  | PASS   | 3 nodes matched selector                        |
| User-provided (2.2.x)       | SKIP   | Skipped (auto-discovery active)                 |
| Collect worker-1 (Stage 03) | PASS   | SOS generated, fetched (25.45 MB), cleaned      |
| Collect worker-2 (Stage 03) | PASS   | SOS generated, fetched (23.81 MB), cleaned      |
| Collect worker-3 (Stage 03) | PASS   | SOS generated, fetched (17.47 MB), cleaned      |
| Summary Report              | PASS   | 3 files listed with correct descriptions        |

### Key Verification

- `rescued=0` confirms no fallback was triggered.
- Step `2.1.x` was used (auto-discover) instead of `2.2.x` (user-provided).
- Step `2.2.3` (validate user-provided nodes) was correctly skipped.
- All 3 workers were collected sequentially via `oc debug`.

---

## Test Case 6 — `ocp_debug`: Auto-Discovery All Nodes (No Selector)

**Status:** Executed — PASS

**Objective:** Validate auto-discovery of all cluster nodes when both
`sos_report_ocp_nodes` and `sos_report_ocp_node_selector` are empty.

### Parameters

```yaml
sos_report_mode: ocp_debug
sos_report_ocp_nodes: []
sos_report_ocp_node_selector: ""
upload: false
```

### Results

| Metric              | Value                                      |
| ------------------- | ------------------------------------------ |
| Playbook Result     | `ok=111, changed=25, failed=0, rescued=0`  |
| Nodes Discovered    | 6 (3 masters + 3 workers, no selector)     |
| Discovery Branch    | `2.1.x` (auto-discover), NOT `2.2.x`      |
| Auth User           | `system:serviceaccount:ansible-automation:ansible-dr-orchestrator` |
| SOS Reports         | 6 collected (see sizes below)              |
| Summary Report      | Yes, 6 files listed                        |
| Cleanup Executed    | Yes                                        |

### Per-Node SOS Report Sizes

| Node (role)            | Size (MB) |
| ---------------------- | --------- |
| master-0               | 40.10     |
| master-1               | 37.68     |
| master-2               | 31.20     |
| worker-eastus1         | 26.63     |
| worker-eastus2         | 25.13     |
| worker-eastus3         | 16.75     |

### Stage Validation

| Stage                       | Status | Notes                                            |
| --------------------------- | ------ | ------------------------------------------------ |
| Preflight assertions        | PASS   | Mode, image, token, oc binary                    |
| OCP Login (Stage 01)        | PASS   | Logged in as SA `ansible-dr-orchestrator`        |
| Auto-Discovery (2.1.1)      | PASS   | `oc get nodes` returned 6 nodes (no selector)   |
| Set node list (2.1.2)       | PASS   | List set to all 6 discovered nodes              |
| Assert nodes found (2.1.3)  | PASS   | 6 nodes discovered                               |
| User-provided (2.2.x)       | SKIP   | Skipped (auto-discovery active)                  |
| Collect master-0 (Stage 03) | PASS   | SOS generated, fetched (40.10 MB), cleaned       |
| Collect master-1 (Stage 03) | PASS   | SOS generated, fetched (37.68 MB), cleaned       |
| Collect master-2 (Stage 03) | PASS   | SOS generated, fetched (31.20 MB), cleaned       |
| Collect worker-1 (Stage 03) | PASS   | SOS generated, fetched (26.63 MB), cleaned       |
| Collect worker-2 (Stage 03) | PASS   | SOS generated, fetched (25.13 MB), cleaned       |
| Collect worker-3 (Stage 03) | PASS   | SOS generated, fetched (16.75 MB), cleaned       |
| Summary Report              | PASS   | 6 files listed with correct descriptions         |

### Key Verification

- `rescued=0` confirms no fallback was triggered.
- Step `2.1.x` was used (auto-discover all) instead of `2.2.x` (user-provided).
- All 6 nodes (masters + workers) were collected sequentially via `oc debug`.
- Master nodes produced larger SOS reports (~31-40 MB) than workers (~17-27 MB),
  which is expected due to etcd, API server, and controller manager data.
- Service account authentication worked correctly across all 6 nodes.

---

## Test Case 7 — `standard` Mode: RHEL Host

**Status:** Executed — PASS

**Objective:** Validate the standard RHEL SOS report pipeline — install `sos`
package, generate report, fetch to control node, cleanup.

### Parameters

```yaml
# Playbook used
playbook: playbooks/sos_report_rhel.yml

sos_report_mode: standard                                   # default
upload: false
```

### Target Infrastructure

| Property           | Value                                             |
| ------------------ | ------------------------------------------------- |
| Platform           | Azure VM (Standard_B2s, 2 vCPU, 4 GB RAM)        |
| OS                 | Red Hat Enterprise Linux 9.8 (Plow)               |
| Kernel             | 5.14.0-687.30.1.el9_8.x86_64                     |
| Resource Group     | `acmdr-lab-sostest-rg` (ephemeral, dedicated)     |
| Region             | Azure East US                                     |
| Auth               | SSH key-based (`azureuser`)                       |

### Results

| Metric              | Value                                     |
| ------------------- | ----------------------------------------- |
| Playbook Result     | `ok=32, changed=4, failed=0, rescued=0`   |
| SOS Report Size     | ~11 MB (`.tar.xz`)                        |
| Collection Duration | ~50 seconds                               |
| Disk Check          | 9557 MB free (minimum: 500 MB)            |
| Summary Report      | Yes, 1 file listed                        |
| Cleanup Executed    | Yes (2 files removed: `.tar.xz` + `.sha256`) |

### Stage Validation

| Stage                       | Status | Notes                                        |
| --------------------------- | ------ | -------------------------------------------- |
| Setup (Stage 00)            | PASS   | Destination directory created on control node |
| Install (1.1)               | PASS   | `sos` package already present                |
| Gather facts (2.1)          | PASS   | Filtered: `ansible_user_id`, `ansible_fqdn`  |
| Disk check (2.1.1-2.1.2)   | PASS   | 9557 MB available, threshold 500 MB          |
| Generate (2.2)              | PASS   | `sos report --batch` completed (~50s)        |
| Find report (Fetch 0.1)     | PASS   | 1 file found in `/var/tmp/`                  |
| Fetch (0.3.2)               | PASS   | 11 MB transferred to control node            |
| Cleanup (0.2)               | PASS   | 2 files removed from target                  |
| Summary Report              | PASS   | FQDN resolved to `acmdr-lab-sostest-01.internal.cloudapp.net` |

### Sub-Test 7b — Disk Space Check Failure (Standard Mode)

Ran with `sos_report_min_disk_mb: 999999` to force the pre-flight to fail.

| Metric           | Value                                              |
| ---------------- | -------------------------------------------------- |
| Playbook Result  | `ok=16, changed=0, failed=1, rescued=1`            |
| Failure Stage    | Stage 02 (Generate) at step 2.1.2                  |
| Error Message    | `Insufficient disk space: 9557 MB < 999999 MB`     |
| SOS Generation   | Not attempted (failed before step 2.2)             |

### Sub-Test 7c — Cleanup Disabled

Ran with `sos_report_cleanup: false` to verify the report remains on the host.

| Metric              | Value                                     |
| ------------------- | ----------------------------------------- |
| Playbook Result     | `ok=27, changed=2, failed=0, rescued=0`   |
| Cleanup Task        | Skipped (`when: sos_report_cleanup`)      |
| Summary Shows       | `Cleanup Enabled: No`                     |
| Report on Host      | Confirmed present after playbook finished |

### Sub-Test 7d — CLI Options: `--clean`, `--case-id`, `--low-priority`, `--since`

Ran with data obfuscation and extended CLI options to validate the new
`sos_report_clean`, `sos_report_case_id`, `sos_report_low_priority`, and
`sos_report_since` variables (roadmap item: "Add more CLI parameter options").

```bash
ansible-playbook playbooks/sos_report_rhel.yml \
  -i 20.228.165.77, -u azureuser --become \
  -e 'upload=false' \
  -e 'sos_report_clean=true' \
  -e 'sos_report_case_id=03999999' \
  -e 'sos_report_low_priority=true' \
  -e 'sos_report_since=20260801'
```

| Metric              | Value                                                  |
| ------------------- | ------------------------------------------------------ |
| Playbook Result     | `ok=32, changed=4, failed=0, rescued=0`                |
| SOS Report Size     | 4.16 MB (vs ~11 MB without `--clean`)                  |
| Collection Duration | ~83 seconds (includes obfuscation pass)                |
| Obfuscation         | Hostname `host0`, IP `172.17.0.13`, 910 files stripped |
| Case ID in filename | `...-03999999-...` embedded                            |
| `--low-priority`    | Passed, no performance impact on test VM               |
| `--since`           | `20260801` filter applied to archived files            |

**Key observations:**

- The `--clean` flag triggers a full post-processing pass that obfuscates
  hostnames, IPs, MAC addresses, and certificate files, then renames the
  output archive with the `-obfuscated` suffix
- The obfuscated report is significantly smaller (4.16 MB vs 11 MB) because
  910 unprocessable binary files are removed during obfuscation
- The `find` pattern in `common/fetch.yml` (`sosreport-*.tar.xz`) still
  matches the obfuscated filename correctly
- The case ID is embedded in both the archive filename and report metadata

### Bugs Found

**Bug #6: `delegate_to: localhost` inherits `--become`, creating root-owned
local directories.** When the playbook runs with `--become` (required for `sos
report` on the remote host), tasks with `delegate_to: localhost` also escalate
privileges on the control node. This creates the SOS report destination
directories as root, and the subsequent `fetch` task fails with `Permission
denied` when writing as the ansible user. Fixed by adding `become: false` on
all `delegate_to: localhost` tasks in `main.yml` and `common/fetch.yml`.

---

## Test Case 8 — `ocp_ssh` Mode: SSH to RHCOS Node

**Status:** Blocked — requires direct SSH access to RHCOS nodes.

**Objective:** Validate SOS collection via SSH to RHCOS nodes using the
support-tools container directly on the node.

### Parameters

```yaml
# Inventory: the target RHCOS node(s) must be reachable via SSH

sos_report_mode: ocp_ssh
upload: false
```

### Expected Behavior

1. OCP pre-flight assertions pass (support-tools image defined).
2. `podman run` with support-tools generates the SOS report on the node.
3. Report fetched via `ansible.builtin.fetch` (SSH-based, not `oc debug`).
4. Cleanup removes `sosreport-*.tar.xz` from `/var/tmp/`.

### Blocker

The ARO cluster nodes are in a private Azure VNET. SSH access from the
control node requires VPN or bastion host, neither of which is configured
in the current lab environment. The `ocp_ssh` mode code path is inherited
from the original role and has not been modified in this restructure.

---

## Test Case 9 — `ocp_debug`: Invalid Node Name

**Status:** Executed — PASS (expected failure with correct error message)

**Objective:** Validate that providing a non-existent node name fails with a
clear error message at the discovery stage (not at collection time).

### Parameters

```yaml
sos_report_mode: ocp_debug
sos_report_ocp_nodes:
  - "this-node-does-not-exist"
upload: false
```

### Results

| Metric             | Value                                    |
| ------------------ | ---------------------------------------- |
| Playbook Result    | `ok=23, changed=1, failed=1, rescued=1`  |
| Failure Stage      | Stage 02 (Node Discovery) at step 2.2.3  |
| SOS Collection     | Not attempted                            |

### Stage Validation

| Stage                        | Status | Notes                                         |
| ---------------------------- | ------ | --------------------------------------------- |
| Preflight assertions         | PASS   | Mode, image, token, oc binary validated       |
| OCP Login (Stage 01)         | PASS   | Logged in as `kube:admin`                     |
| Node Discovery (2.2.1)       | PASS   | User-provided list set                        |
| Node Validation (2.2.2)      | ok     | `oc get node` ran with `failed_when: false`   |
| Node Assert (2.2.3)          | FAIL   | Node not found, clear error message           |

### Error Message Produced

```text
Node 'this-node-does-not-exist' was not found in the cluster.
Please verify the node name is correct (oc get nodes).
```

The Kubernetes API also returned:
`Error from server (NotFound): nodes "this-node-does-not-exist" not found`

---

## Test Case 10 — `ocp_debug`: Expired Token

**Status:** Executed — PASS (expected failure with correct error message)

**Objective:** Validate that an expired or invalid OCP token fails at login
with a clear error, before any node interaction.

### Parameters

```yaml
sos_report_mode: ocp_debug
sos_report_ocp_token: "sha256~expired-or-invalid-token-for-testing"
sos_report_ocp_server_url: "https://api.<cluster>.<region>.aroapp.io:6443"
upload: false
```

### Results

| Metric             | Value                                    |
| ------------------ | ---------------------------------------- |
| Playbook Result    | `ok=16, changed=0, failed=1, rescued=1`  |
| Failure Stage      | Stage 01 (OCP Login) at step 1.3         |
| Node Discovery     | Not attempted                            |
| SOS Collection     | Not attempted                            |

### Stage Validation

| Stage                    | Status | Notes                                      |
| ------------------------ | ------ | ------------------------------------------ |
| Preflight assertions     | PASS   | Mode, image, token format, oc binary       |
| OCP Login (1.1)          | ok     | `oc login` ran with `failed_when: false`   |
| Whoami Verify (1.2)      | ok     | `oc whoami` ran with `failed_when: false`  |
| Login Assert (1.3)       | FAIL   | Clear error about invalid/expired token    |

### Error Message Produced

```text
Failed to authenticate to OpenShift cluster for SOS report collection.
This is often caused by an expired token or incorrect API URL.
Login Error: error: The token provided is invalid or expired.
```

---

## Test Summary

| #  | Test Case                                    | Status  | Outcome                  |
| -- | -------------------------------------------- | ------- | ------------------------ |
| 1  | `ocp_debug`: Single Worker Node              | PASS    | SOS collected ~25 MB     |
| 2  | `ocp_debug`: Happy Path + Fallback Enabled   | PASS    | Fallback NOT triggered   |
| 3  | SSH Fallback: Triggered, SSH Unreachable     | PASS    | Correct error path       |
| 4  | SSH Fallback: Disabled + `oc debug` Fail     | PASS    | Correct error message    |
| 5  | `ocp_debug`: Auto-Discovery + Selector       | PASS    | 3 workers, 3 SOS reports |
| 6  | `ocp_debug`: Auto-Discovery All Nodes        | PASS    | 6 nodes, 6 SOS reports   |
| 7  | `standard`: RHEL Host (+7b/7c/7d sub-tests)  | PASS    | 11 MB SOS from RHEL 9.8  |
| 8  | `ocp_ssh`: SSH to RHCOS Node                 | Blocked | No SSH access to RHCOS   |
| 9  | `ocp_debug`: Invalid Node Name               | PASS    | Fails at Stage 02        |
| 10 | `ocp_debug`: Expired Token                   | PASS    | Fails at Stage 01        |

**Executed:** 9 / 10 — **All passed** (1 blocked by infrastructure).

### Bugs Found and Fixed During Testing

1. **`ansible_connection: ssh` missing in `add_host`** — When the playbook
   runs with `connection: local` (as in `sos_report_ocp.yml`), `delegate_to`
   inherits the local connection unless `ansible_connection: ssh` is set
   explicitly on the dynamic host. Without it, SSH-delegated commands
   (`podman run`, `fetch`) executed on the control node instead of the
   RHCOS node. Fixed by adding `ansible_connection: ssh` to `add_host`.

2. **`ignore_unreachable` with `delegate_to` skips subsequent tasks** —
   Using `ignore_unreachable: true` on a task with `delegate_to` marks the
   delegating host as unreachable internally, causing all subsequent tasks
   to be skipped (even non-delegated ones like asserts). Fixed by replacing
   the SSH connectivity check with `wait_for` (TCP port 22 check on the
   control node) + `ignore_errors: true`, which doesn't pollute Ansible's
   host reachability state.

3. **`failed_when: false` suppresses failure state** — Using
   `failed_when: false` on the `wait_for` task made `is not failed` evaluate
   to `True` even when the connection timed out, allowing the fallback to
   proceed to SSH-delegated tasks that would then fail with an ugly
   `UNREACHABLE` error. Fixed by using `ignore_errors: true` instead, which
   preserves the failed state in the registered variable while still
   allowing execution to continue.

4. **`wait_for` TCP port check incompatible with bastion/ProxyJump** —
   Direct TCP port 22 check from the control node fails when SSH access
   goes through a bastion or ProxyJump, because the control node cannot
   reach the target IP directly. Fixed by removing `wait_for` + assert
   entirely, replacing with `block/rescue` around all SSH-dependent tasks
   and adding the `sos_report_ocp_ssh_extra_args` variable for ProxyJump
   support.

5. **`UNREACHABLE` status bypasses `block/rescue`** — Ansible's `rescue`
   only catches tasks with `FAILED` status, not `UNREACHABLE`. When a
   `delegate_to` task cannot connect via SSH, the task gets `UNREACHABLE`
   status which bypasses the rescue block entirely. The PLAY RECAP showed
   `unreachable=1, rescued=1` but the inner rescue (with the custom
   troubleshooting message) never fired. Fixed by adding an SSH
   connectivity pre-check at step `3.F.4` that runs the `ssh` binary
   directly on the control node via `ansible.builtin.command` (no
   `delegate_to`). This returns `rc != 0` as a normal `FAILED` task
   (caught by `ignore_errors: true`), and the assert at `3.F.5` produces
   the actionable troubleshooting message. After the fix, PLAY RECAP
   shows `unreachable=0`.

6. **`delegate_to: localhost` inherits `--become`, creating root-owned
   directories** — When the playbook runs with `--become` (required for
   `sos report` on the remote RHEL host), tasks with `delegate_to: localhost`
   also escalate privileges on the control node. The SOS report destination
   directories are then created as root, and the `ansible.builtin.fetch` task
   fails with `Permission denied` when writing as the ansible user. Fixed by
   adding explicit `become: false` on all `delegate_to: localhost` tasks in
   `main.yml` and `common/fetch.yml`.

---

## Notes for PR Reviewers

- **Security:** All tokens and API URLs have been replaced with generic
  placeholders in this document. No real credentials were committed.
- **Reproducibility:** Tests can be reproduced on any OCP cluster (ARO, ROSA,
  self-managed) with a valid token and at least one reachable node.
- **Collection install:** The fork was installed locally via
  `ansible-galaxy collection build && ansible-galaxy collection install <tarball> --force --no-deps`
  to test with fully qualified collection names (FQCN).
- **Upload skipped:** All tests used `upload=false` to avoid dependency on
  Red Hat API credentials. The upload pipeline is tested separately via the
  `rh_case` and `rh_token_refresh` roles.
