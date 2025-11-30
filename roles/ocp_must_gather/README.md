# infra.support_assist.ocp_must_gather

This role runs **`oc adm must-gather`** against a target OpenShift cluster, compresses the resulting directory into a `.tar.gz` archive, and prepares it for upload to a Red Hat Support Case.

This role is designed to run on `localhost` (or wherever the `oc` CLI is installed and configured).

## Requirements

* **On Control Node (Execution Host):**
    * The **OpenShift CLI (`oc`)** must be installed and in the system's `PATH`.
    * Must be logged in to the target OpenShift cluster. The role attempts to log in using the provided token.

* **Ansible Collections:**
    * `community.general`: Required for the `community.general.archive` module to compress the must-gather output.

---

## Role Variables

### Input Variables

The following variables control the behavior of this role:

* **`case_id`**:
    * **(Optional)** The Red Hat Support Case number (e.g., `01234567`), This is only needed if you want to automatically upload the gathered archive to an existing case.
    * Type: `string`

* **`ocp_must_gather_token`**:
    * **(Required)** The OpenShift API token for logging in (e.g., `sha256~...`).
    * Type: `string`

* **`ocp_must_gather_server_url`**:
    * **(Required)** The URL of the OpenShift API server (e.g., `https://api.my-ocp-cluster.com:6443`).
    * Type: `string`

* **`ocp_must_gather_dest_dir`**:
    * A temporary directory on the execution host where `oc adm must-gather` will write its output. This directory is also where the final `.tar.gz` archive will be created.
    * Default: `"/tmp/must-gather-output"`
    * Type: `path`

* **`ocp_must_gather_image`**:
    * **Custom Feature Collection:** The acronym for the specific component collection to run (e.g., `"AAP"` for Ansible Automation Platform, or `"DEFAULT"` for the standard collection).
    * Default: `"DEFAULT"`
    * Type: `string`

> **NOTE on Component Selection:** This variable expects a short **acronym** (e.g., **`AAP`**, **`ODF`**, **`CNV`**). Use **`DEFAULT`** for the standard collection. The role automatically looks up the corresponding technical image URL. **Consult the component map in:** [MUST\_GATHER\_IMAGE\_OPTIONS.md](./docs/MUST_GATHER_IMAGE_OPTIONS.md) **for all valid acronyms and their purposes.**

* **`ocp_must_gather_since`**:
    * **Time Window (`--since`):** Limits log collection to a specific time range (e.g., **`"12h"`**, **`"7d"`**). Options include: **`"1h"`**, **`"3h"`**, **`"6h"`**, **`"12h"`**, **`"24h"`**, **`"3d"`**, **`"7d"`**, **`"14d"`**, **`"30d"`**, or blank for "Full History".
    * Default: `""` (Collects full history)
    * Type: `string`

* **`ocp_disconnected_mode`**:
    * **Disconnected Environment Flag:** Set to `true` if the cluster is air-gapped. Activates logic to use the custom mirror registry address.
    * Default: `false`
    * Type: `bool`

* **`ocp_disconnected_registry`**:
    * **Mirror Registry Address:** The full address of the mirror registry containing the must-gather image (e.g., `my.mirror.registry.com/ocp/mirror`). **Required if `ocp_disconnected_mode` is true.**
    * Default: `""`
    * Type: `string`

* **`ocp_must_gather_options`**:
    * A string of any additional options to pass to the `oc adm must-gather` command (e.g., `-- /usr/bin/gather_network_logs`). This is for advanced CLI usage beyond standard collection profiles.
    * Default: `""`
    * Type: `string`

* **`ocp_must_gather_validate_ssl`**:
    * Whether to use the `--insecure-skip-tls-verify` flag during `oc login`.
    * Default: `true`
    * Type: `bool`

### Output Variables

This role generates the following fact, which is used by the `rh_case_update` role:

* `case_updates_needed`:
    * A list containing an object that describes the fetched archive to be uploaded.
    * Example:
        ~~~yaml
        case_updates_needed:
          - attachment: /tmp/must-gather-output/must-gather-my-ocp-cluster-2025-10-27-150000.tar.gz
            attachmentDescription: "OpenShift must-gather collected from 'my-ocp-cluster' cluster accessed via execution host control-node.example.com using the 'infra.support_assist' collection."
            hostname: "my-ocp-cluster"
        ~~~

---

## Dependencies

* `community.general`: Required for the `archive` module.

## Role Features and Safety Checks

> **NEW FEATURES:**
> * **Privilege Pre-Check (Safety):** The role now includes an **assertion task** to verify that the authenticated user/Service Account possesses the required **`cluster-admin`** privileges **`before`** executing the long-running **`must-gather`** command, failing early with a custom formatted message if permissions are inadequate.
> * **Disk Space Check (Safety):** An **assertion validation** has been implemented to verify the **available disk space** on the Execution Host (EE) filesystem where the Must-Gather output directory resides. This prevents mid-execution failures due to the large size of the raw collection.
> * **Case Comment Template:** The content of the automatic comment posted after the Must-Gather upload can be customized via the Jinja2 template: **[roles/ocp_must_gather/templates/support_case_comment.j2](roles/ocp_must_gather/templates/support_case_comment.j2)**.
> * **Time Window (`--since`):** Use the `ocp_must_gather_since` variable (e.g., `"12h"`, `"3d"`, `"7d"`) to limit log collection to a specific time range, optimizing file size and relevance. Options include: `"1h"`, `"3h"`, `"6h"`, `"12h"`, `"24h"`, `"3d"`, `"7d"`, `"14d"`, `"30d"`, or blank for "Full History".
> * **Custom Feature Collection:** The `ocp_must_gather_image` variable allows selecting specialized component collections. Examples include **DEFAULT** (Default Must Gather Collection), **AAP** (Ansible Automation Platform), **OSSM** (OpenShift Service Mesh), **CNV** (Container Native Virtualization), and **ODF** (OpenShift Data Foundation). **All available options are listed in:** [roles/ocp_must_gather/vars/main.yml](roles/ocp_must_gather/vars/main.yml).
> * **Disconnected Environment:** Use the `ocp_disconnected_mode: true` flag and provide the `ocp_disconnected_registry` address (e.g., `my.mirror.registry.com/ocp/mirror`) to point the collection to your mirror registry. (See KCS article on disconnected must-gather: [https://access.redhat.com/solutions/4647561](https://access.redhat.com/solutions/4647561)).

---

## Example Playbook

### Required Case Variables (for pipeline use)

| Variable | Description | Default Value | Notes |
| :--- | :--- | :--- | :--- |
| **`case_product`** | The specific Red Hat product for the case. | `OpenShift Container Platform` | This value is typically **hardcoded** in the pipeline playbook. |
| **`case_description`** | Detailed explanation of the issue, including steps to reproduce, observed behavior, and expected results. | (Required String) | Provides detailed context for the case. |

### Simple example (running just the role)

~~~yaml
- name: Gather OpenShift Must Gather
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    case_id: "01234567"
    case_product: "OpenShift Container Platform"
    case_description: "The attached Must-Gather shows issues with AAP components failing to start"
    ocp_must_gather_server_url: "https://api.my-ocp-cluster.com:6443"
    ocp_must_gather_token: "sha256~..."  # Use Ansible Vault!
    # --- ADVANCED OPTIONS ---
    ocp_must_gather_since: "6h"
    ocp_must_gather_image: "AAP"
    ocp_disconnected_mode: true
    ocp_disconnected_registry: "registry.local/must-gather-mirror:latest"
    ocp_must_gather_validate_ssl: false # Example of overriding default SSL check
    ocp_must_gather_options: ""

  tasks:
    - name: Call ocp_must_gather role
      ansible.builtin.include_role:
        name: infra.support_assist.ocp_must_gather
~~~

### Recommended example (using the main collection playbook)

The recommended way to use this role is via the main `ocp_must_gather` playbook, which handles token refresh and upload logic.

~~~shell
# Set your Red Hat token as an environment variable
export REDHAT_OFFLINE_TOKEN="YOUR_OFFLINE_TOKEN_HERE"

# Run the main playbook
ansible-playbook infra.support_assist.ocp_must_gather \
  -e case_id=00000000 \
  -e ocp_must_gather_server_url="https://api.my-ocp-cluster.com:6443" \
  -e ocp_must_gather_token="sha256~..." \
  -e ocp_must_gather_image="AAP" \
  -e ocp_must_gather_since="6h" \
  -e ocp_disconnected_mode=false \
  -e ocp_disconnected_registry="" \
  -e ocp_must_gather_options="" \
  -e upload=true
~~~

You can use a playbook as an example as [playbooks/ocp-case-mustgather-pipeline.yml](../../playbooks/ocp-case-mustgather-pipeline.yml).

## License

GPL-3.0-or-later

## Author Information

- Lenny Shirley

## Code Contributors

- Diego Felipe Mateus