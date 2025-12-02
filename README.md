# Ansible Collection - infra.support_assist

[![GitHub last commit](https://img.shields.io/github/last-commit/redhat-cop/infra.support_assist.svg)](https://github.com/redhat-cop/infra.support_assist/commits/main) [![GitHub license](https://img.shields.io/github/license/redhat-cop/infra.support_assist.svg)](https://github.com/redhat-cop/infra.support_assist/blob/main/LICENSE) [![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](https://github.com/redhat-cop/infra.support_assist/pulls) ![GitHub contributors](https://img.shields.io/github/contributors/redhat-cop/infra.support_assist) ![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/redhat-cop/infra.support_assist/tests.yml) ![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/redhat-cop/infra.support_assist)

This Ansible Collection will gather various reports/outputs that are commonly asked for in Red Hat Support Cases, and can optionally **create the case**, and then upload the diagnostics directly to the Support Case Portal.

This collection currently includes the following playbooks and roles:

* **`aap_api_dump`**: Gathers diagnostic output from Ansible Automation Platform (AAP) component APIs (Controller, Hub, EDA) and creates compressed archives for case upload.
* **`aap_api_token`**: Obtains and manages OAuth2 API tokens for Ansible Automation Platform (AAP).
* **`ocp_must_gather`**: Gathers an `oc adm must-gather` archive from an OpenShift cluster.
* **`rh_case`**: Unified role for creating and updating Red Hat Support Cases via API (creates cases, uploads files, adds comments).
* **`rh_token_refresh`**: Handles Red Hat API token authentication and caching.
* **`sos_report`**: Gathers a `sosreport` from one or more target hosts.

---

## Requirements

### Ansible Collections
This collection requires the following Ansible Collections to be installed:
* `community.general` (for the `archive` module used in the `ocp_must_gather` role)

### System Dependencies
This collection requires the following packages to be installed:

* **On the Target Hosts** (for the `sos_report` role):
    * `sos`: This is required to generate the `sosreport` and is installed by the role.

* **On the Control Node** (or execution node):
    * `curl` (for the `rh_case` role): Required for robust, streaming file uploads to the Red Hat support portal.
    * `oc` (for the `ocp_must_gather` role): The OpenShift CLI (`oc`) must be installed and in the system's `PATH`.

---

## Installing this collection

You can install the `infra.support_assist` collection with the Ansible Galaxy CLI:

~~~shell
ansible-galaxy collection install git+https://github.com/redhat-cop/infra.support_assist.git
~~~

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

~~~yaml
---
collections:
  - name: infra.support_assist
    source: https://github.com/redhat-cop/infra.support_assist.git
    type: git
    # If you need a specific version of the collection, you can specify like this:
    # version: ...
~~~

---

## Usage

This collection includes primary playbooks that orchestrate the roles in the correct order. All playbooks that access the Red Hat API require a valid **Red Hat Offline Token** (see generation instructions below).

### Preparing Your Offline Token
> **💡 How to Generate a Red Hat Offline Token**
>
> 1.  Navigate to the Red Hat API Token management page: [https://access.redhat.com/management/api](https://access.redhat.com/management/api)
> 2.  Click the **"Generate Token"** button.
> 3.  Log in with your Red Hat customer portal credentials if prompted.
> 4.  A new offline token will be generated. **Copy this token immediately**, as Red Hat notes, "Tokens are only displayed once and are not stored. They will expire after 30 days of inactivity".

All playbooks that access the Red Hat API will look for the token in this order:
1. An extra-var named `offline_token`.
2. An environment variable named `REDHAT_OFFLINE_TOKEN`.

---

# 📚 AAP Lessons Learned for Must-Gather Pipeline

This document summarizes critical configuration settings and resource warnings necessary for the **`ocp_must_gather`** pipeline to run successfully on the Red Hat Ansible Automation Platform (AAP).

## 1. ⚙️ Project Synchronization and Collection Download

To ensure your Project Synchronization successfully downloads the necessary Ansible Collections (e.g., `infra.support_assist`), the correct settings must be enabled, and credentials must be configured at the Organizational level.

### Required AAP Configuration Steps

| Location (Left Navigation Menu) | Setting to **Enable** | Purpose |
| :--- | :--- | :--- |
| **Settings** > **Automation Execution** > **Job** | **Enable Role Download** | Allows the Execution Environment to pull dependent Ansible Roles defined outside of a Collection. |
| **Settings** > **Automation Execution** > **Job** | **Enable Collection(s) Download** | Allows the Execution Environment to pull Collections (e.g., `infra.support_assist`) from configured sources. |

### Organizational Access Check

Under **Access Management** > **Organizations** > **[Your Organization Name]**:

* Ensure that the **Galaxy Credentials** field has an **Ansible Galaxy Credential** (or a similar credential pointing to a collection source) properly set. If this is missing, the **Project Sync** will fail to download the required collections, causing the Job Template to fail with "Collection not found" errors.

---

## 2. ⚠️ Must-Gather Resource Warning: Ephemeral Storage (Disk Space)

When running the **`ocp_must_gather`** pipeline on an AAP instance hosted on OpenShift, the default Execution Environment (EE) Pod resource limits are often insufficient. Uncompressed Must-Gather output can easily exceed **10–20 GiB**, leading to an **"`No space left on device`"** error.

### Solution: Create High-Storage Instance Group

To allocate sufficient storage for the collection, you must create a specialized **Instance Group** with a **Pod Spec Override**.

| Setting | Recommendation | Rationale |
| :--- | :--- | :--- |
| **Instance Group Name** | **`MUST-GATHER-HIGH-STORAGE`** | Clear, descriptive name for easy assignment. |
| **Resource to Increase** | **`ephemeral-storage`** | Must-Gather relies heavily on temporary disk space. |
| **Pod Spec Override** | Modify the **`resources.limits`** and **`resources.requests`** for the **`main`** container. | A minimum of **`20Gi`** to **`30Gi`** is often necessary for a full OCP collection. |

### Resource Adjustment References

| Customization Option | Reference Link |
| :--- | :--- |
| **Customizing Pod Specs via Instance Group** (Specific jobs) | [Customizing the pod specification](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/performance_considerations_for_operator_environments/assembly-pod-spec-modifications_performance-considerations#proc-customizing-pod-specs_performance-considerations) |
| **Global Control Plane Adjustments** (All jobs) | [Chapter 2. Control plane adjustments](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/performance_considerations_for_operator_environments/assembly-control-plane-adjustments_performance-considerations) |

### Pod Spec Override Example Snippet

This YAML snippet should be used in the **Pod Spec Override** field of the new Instance Group:

~~~yaml
spec:
  containers:
  - name: main
    resources:
      limits:
        ephemeral-storage: 30Gi  # Set limit high enough for full collection
      requests:
        ephemeral-storage: 30Gi  # Request sufficient storage to ensure scheduling
~~~

---

## Playbooks

This collection provides five main playbooks for common operations:

* **`infra.support_assist.aap_api_dump`**: Gathers diagnostic output from AAP component APIs (Controller, Hub, EDA), creates a compressed archive, and optionally uploads it to a Red Hat Support Case.
    * **Role-specific documentation:** [roles/aap_api_dump/README.md](roles/aap_api_dump/README.md)
    * **Example (with case upload):**
        ~~~shell
        export REDHAT_OFFLINE_TOKEN="YOUR_OFFLINE_TOKEN_HERE"
        export AAP_CONTROLLER_URL="https://aap-controller.example.com"
        export AAP_HUB_URL="https://aap-hub.example.com"
        
        ansible-playbook playbooks/aap_api_dump.yml \
          -e case_id=01234567 \
          -e upload=true
        ~~~
    * **Example (standalone dump without upload):**
        ~~~shell
        export AAP_CONTROLLER_URL="https://aap-controller.example.com"
        
        ansible-playbook playbooks/aap_api_dump.yml \
          -e upload=false
        ~~~

* **`infra.support_assist.sos_report`**: Gathers `sosreport`s from all hosts in your inventory, fetches them to the control node, and uploads them to the specified case.
    * **Role-specific documentation:** [roles/sos_report/README.md](roles/sos_report/README.md)
    * **Example (using an environment variable):**
        ~~~shell
        export REDHAT_OFFLINE_TOKEN="YOUR_OFFLINE_TOKEN_HERE"
        
        ansible-playbook -i inventory infra.support_assist.sos_report \
          -e case_id=01234567 \
          -e upload=true \
          -e clean=true
        ~~~

* **`infra.support_assist.ocp_must_gather` (Pipeline)**: **The primary automation playbook.** This runs the full workflow: **Token Refresh** → **Case Creation (optional)** → **Must-Gather Execution** → **Upload/Comment**. This playbook runs on `localhost`.
    * **Role-specific documentation:** [roles/ocp_must_gather/README.md](roles/ocp_must_gather/README.md)
    * **Example (creating a case and uploading with all advanced options):**
        ~~~shell
        ansible-playbook -i inventory infra.support_assist.ocp_must_gather \
          -e ocp_must_gather_server_url="https://api.my-ocp-cluster.com:6443" \
          -e ocp_must_gather_token="sha256~..." \
          -e ocp_must_gather_since="12h" \
          -e ocp_must_gather_image="AAP" \
          -e ocp_disconnected_mode=true \
          -e ocp_disconnected_registry="my.mirror.registry.com/ocp/mirror" \
          -e case_summary="Automated creation of case for OCP diagnostics" \
          -e case_severity="3 (Normal)" \
          -e offline_token=YOUR_OFFLINE_TOKEN_HERE
        ~~~
    > **Note:** To use this playbook to **create** a case, you must provide **all six mandatory variables**: `case_summary`, `case_description`, `case_product`, `case_product_version`, `case_type`, and `case_severity`. Crucially, you must also **omit** the `case_id` variable. If `case_id` is provided, the playbook skips creation and proceeds directly to upload.

### Valid Case Input Options

For the fields `case_product`, `case_type`, and `case_severity`, the acceptable values must exactly match the Red Hat Support API's lookup tables.

Please consult the dedicated documentation file for the full list of valid options:

[**Full Case Option Lists:** `roles/rh_case/docs/CASE_OPTIONS.md`](roles/rh_case/docs/CASE_OPTIONS.md)

* **`infra.support_assist.rh_case` (Utility)**: A unified playbook for creating and updating Red Hat Support Cases via the API. Automatically detects operation mode (create, update, or hybrid).
    * **Role-specific documentation:** [roles/rh_case/README.md](roles/rh_case/README.md)
    * **Example (creating a new case):**
        ~~~shell
        ansible-playbook -i inventory infra.support_assist.rh_case \
          -e case_summary="Request for documentation update" \
          -e case_description="Need clarification on X." \
          -e case_severity="4 (Low)" \
          -e case_product="Red Hat Ansible Automation Platform" \
          -e case_product_version="2.4" \
          -e offline_token=YOUR_OFFLINE_TOKEN_HERE
        ~~~
        > **Note:** The `case_product_version` must be provided as the **normalized base version** (e.g., `4.16`, `8.9`) and not the full patch version (e.g., `4.16.48`).

    * **Example (updating an existing case - uploading a file):**
      ~~~shell
      # Assuming REDHAT_OFFLINE_TOKEN is set as an environment variable
      ansible-playbook infra.support_assist.rh_case \
        -e case_id=01234567 \
        -e "case_updates_needed=[{'attachment': '/path/to/local/file.log', 'attachmentDescription': 'Manual log file upload.'}]"
      ~~~

    * **Example (updating an existing case - adding a comment):**
      ~~~shell
      # Assuming REDHAT_OFFLINE_TOKEN is set as an environment variable
      ansible-playbook infra.support_assist.rh_case \
        -e case_id=01234567 \
        -e "case_updates_needed=[{'comment': 'Adding a comment via playbook.', 'commentType': 'plaintext'}]"
      ~~~

    * **Example (hybrid mode - create case and upload in one operation):**
      ~~~shell
      ansible-playbook infra.support_assist.rh_case \
        -e case_summary="Issue with cluster" \
        -e case_description="Experiencing connectivity issues." \
        -e case_product="OpenShift Container Platform" \
        -e case_product_version="4.16" \
        -e case_type="Configuration Issue" \
        -e case_severity="3 (Normal)" \
        -e "case_updates_needed=[{'attachment': '/path/to/file.log', 'attachmentDescription': 'Diagnostic log'}]" \
        -e offline_token=YOUR_OFFLINE_TOKEN_HERE
      ~~~

---

## Roles

* **[aap_api_dump](roles/aap_api_dump/README.md)**: Gathers diagnostic output from Ansible Automation Platform (AAP) component APIs (Controller, Hub, EDA) and saves them as JSON files. Creates a compressed archive and prepares it for upload to a Red Hat Support Case via the `rh_case` role.
* **[aap_api_token](roles/aap_api_token/README.md)**: Obtains and manages OAuth2 API tokens for Ansible Automation Platform (AAP). Automatically detects Controller version and uses the appropriate collection (`ansible.controller` or `ansible.platform`).
* **[ocp_must_gather](roles/ocp_must_gather/README.md)**: Logs into an OpenShift cluster, runs `oc adm must-gather`, and archives the result.
    > **NEW FEATURES:**
    > * **Privilege Pre-Check (Safety):** The role now includes an **assertion task** to verify that the authenticated user/Service Account possesses the required **`cluster-admin`** privileges **`before`** executing the long-running **`must-gather`** command, failing early with a custom formatted message if permissions are inadequate.
    > * **Disk Space Check (Safety):** An **assertion validation** has been implemented to verify the **available disk space** on the Execution Host (EE) filesystem where the Must-Gather output directory resides. This prevents mid-execution failures due to the large size of the raw collection.
    > * **Case Comment Template:** The content of the automatic comment posted after the Must-Gather upload can be customized via the Jinja2 template: **[roles/ocp_must_gather/templates/support_case_comment.j2](roles/ocp_must_gather/templates/support_case_comment.j2)**.
    > * **Time Window (`--since`):** Use the `ocp_must_gather_since` variable (e.g., `"12h"`, `"3d"`, `"7d"`) to limit log collection to a specific time range, optimizing file size and relevance. Options include: `"1h"`, `"3h"`, `"6h"`, `"12h"`, `"24h"`, `"3d"`, `"7d"`, `"14d"`, `"30d"`, or blank for "Full History".
    > * **Custom Feature Collection:** The `ocp_must_gather_image` variable allows selecting specialized component collections using their acronyms. Examples include **DEFAULT** (Default Must Gather Collection), **AAP** (Ansible Automation Platform), **OSSM** (OpenShift Service Mesh), **CNV** (Container Native Virtualization), and **ODF** (OpenShift Data Foundation). **All available options are listed in:** [ocp_must_gather/docs/MUST_GATHER_IMAGE_OPTIONS.md](./roles/ocp_must_gather/docs/MUST_GATHER_IMAGE_OPTIONS.md).
    > * **Disconnected Environment:** Use the `ocp_disconnected_mode: true` flag and provide the `ocp_disconnected_registry` address (e.g., `my.mirror.registry.com/ocp/mirror`) to point the collection to your mirror registry. (See KCS solutions on disconnected must-gather: [https://access.redhat.com/solutions/4647561](https://access.redhat.com/solutions/4647561)).
    > * **Cluster Name Extraction:** The role now automatically extracts the OpenShift cluster name from the provided API server URL, ensuring accurate identification in case comments and uploads.
* **[rh_case](roles/rh_case/README.md)**: Unified role for creating and updating Red Hat Support Cases via API. Automatically detects operation mode (create, update, or hybrid) based on provided variables.
    > * **Case Comment Template:** The content of the automatic comment posted after case creation can be customized via the Jinja2 template: **[roles/rh_case/templates/support_case_comment.j2](roles/rh_case/templates/support_case_comment.j2)**.
    > **Input Variable Options:** The full list of valid options for `case_product`, `case_type`, and `case_severity` are maintained in the dedicated documentation file: [roles/rh_case/docs/CASE_OPTIONS.md](roles/rh_case/docs/CASE_OPTIONS.md).
* **[rh_token_refresh](roles/rh_token_refresh/README.md)**: Handles Red Hat API token authentication and caching.
* **[sos_report](roles/sos_report/README.md)**: Generates `sosreport` on target hosts, fetches to control node, and prepares for upload.

---

## Release and Upgrade Notes

For details on changes between versions, please see [the changelog for this collection](https://github.com/redhat-cop/infra.support_assist/blob/devel/CHANGELOG.rst).

## Releasing, Versioning and Deprecation

This collection follows [Semantic Versioning](https://semver.org/). More details on versioning can be found [in the Ansible docs](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html#collection-versions).

We plan to regularly release new minor or bugfix versions once new features or bugfixes have been implemented.

Releasing the current major version happens from the `devel` branch.

## To Do / Roadmap (in no specific order)

  - [x] Add a role to use an offline token to get a refresh token for the Red Hat API
  - [x] Add a unified role (`rh_case`) that can create cases, upload files, or add comments to a Red Hat Support Case
  - [x] Add a role that will run `sos report` on one or more hosts
  - [x] Add a role that will run `oc adm must-gather` on an OpenShift cluster
  - [x] Add a playbook that can be used to attach other requested files to a Red Hat Support Case
  - [x] Add a playbook that can be used to add comments in either `markdown` or `plaintext` to a Red Hat Support Case
  - [x] Add a role for grabbing output from one or more Ansible Automation Platform API endpoints
  - [ ] Add more CLI parameter options to the `sos_report` role (particularly `clean|mask`, etc.)
  - [x] Make it easier to pick a defined scope if needed to the `ocp_must_gather` role (would replace/compliment the `container image` option)
  - [x] Add Custom Feature Collection (acronyms): The `ocp_must_gather_image` variable allows selecting specialized component collections to the `ocp_must_gather` role - **All available options are listed in:** [ocp_must_gather/docs/MUST_GATHER_IMAGE_OPTIONS.md](./roles/ocp_must_gather/docs/MUST_GATHER_IMAGE_OPTIONS.md)
  - [x] Add the ability to actually open a NEW Red Hat Support Case (Implemented by the unified role: [**`rh_case`**](roles/rh_case/README.md))
  - [ ] Add the ability to the `sos_report` role to automatically/dynamically add more hosts to the running inventory if discovered running against a cluster (and some of the cluster hosts are missing)
  - [x] Add Privilege Pre-Check (Safety) to verify that the authenticated user/Service Account possesses the required **`cluster-admin`** privileges **`before`** executing the long-running **`must-gather`** to the `ocp_must_gather` role
  - [x] Add Disk Space Check (Safety) assertion validation to verify the **available disk space** on the Execution Host (EE) filesystem where the Must-Gather output directory resides to the `ocp_must_gather` role
  - [x] Add Case Comment Template (Jinja2 customization) to the `ocp_must_gather` role
  - [x] Add Time Window (`--since`): Use the `ocp_must_gather_since` variable to limit log collection to the `ocp_must_gather` role
  - [x] Add Disconnected/Air-Gapp Environment flag to the `ocp_must_gather` role to point the collection to custom mirror registry. (See KCS solutions on disconnected must-gather: [https://access.redhat.com/solutions/4647561](https://access.redhat.com/solutions/4647561)).
  - [x] Add Case Comment Template (Jinja2 customization) to the `rh_case` role
  - [x] Add documentation for valid Case Input Options (Product, Type, Severity) - [**Full Case Option Lists:** `roles/rh_case/docs/CASE_OPTIONS.md`](roles/rh_case/docs/CASE_OPTIONS.md)
  - [x] Add Cluster Name Extraction - The role now automatically extracts the OpenShift cluster name from the provided API server URL, ensuring accurate identification in case comments and uploads, to avoid user needs to be inserted manually.
  - [ ] Add options to the `sos_report` role to gather data from an OCP nodes using the official method as guidance from Red Hat KCS: [Method 1 - Using SSH](https://access.redhat.com/solutions/3820762) or [Method 2 - Using oc debug](https://access.redhat.com/solutions/4387261) - keep in mind the SOS Report from an OCP node is different from a standard Linux host sosreport.
  - [ ] Add an option to the `ocp_must_gather` or create a new role to gather data for one or more namespace using `oc adm inspect`
  - [ ] Add some lessons learn and tips how to use this automation on Ansible Automation Platform (Implemented above some useful tips/guidance: **[AAP Lessons Learned for Must-Gather Pipeline](#-aap-lessons-learned-for-must-gather-pipeline))**

## Getting Help

We are on the Ansible Forums, if you want to discuss something, ask for help, or participate in the community, please use the `#infra-support-assist` tag on the forum.

[Ansible Forums](https://forum.ansible.com/tag/infra-support-assist)

## Contributing to this collection

We welcome community contributions to this collection. If you find problems, please open an issue or create a PR.

More information about contributing can be found in our [Contribution Guidelines.](https://github.com/redhat-cop/infra.support_assist/blob/devel/.github/CONTRIBUTING.md)

## Contributors

A big thank you to all the contributors who have helped improve this project! You can see a full list of everyone who has contributed on the [contributors page](https://github.com/redhat-cop/infra.support_assist/graphs/contributors).

<img src="https://github.com/lennysh.png" width="60px;"/><img src="https://github.com/dfmateus.png" width="60px;"/>

## Code of Conduct

This collection follows the Ansible project's [Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html). Please read and familiarize yourself with this document.

## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](https://github.com/redhat-cop/infra.support_assist/blob/devel/LICENSE) to see the full text.