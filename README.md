# Ansible Collection - infra.support_assist

[![GitHub last commit](https://img.shields.io/github/last-commit/redhat-cop/infra.support_assist.svg)](https://github.com/redhat-cop/infra.support_assist/commits/main) [![GitHub license](https://img.shields.io/github/license/redhat-cop/infra.support_assist.svg)](https://github.com/redhat-cop/infra.support_assist/blob/main/LICENSE) [![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](https://github.com/redhat-cop/infra.support_assist/pulls) ![GitHub contributors](https://img.shields.io/github/contributors/redhat-cop/infra.support_assist) ![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/redhat-cop/infra.support_assist/tests.yml) ![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/redhat-cop/infra.support_assist)

This Ansible Collection will gather various reports/outputs that are commonly asked for in Red Hat Support Cases, and can optionally upload them directly to the Support Case Portal.

This collection currently includes the following playbooks and roles:
* `sos_report`: Gathers a `sosreport` from one or more target hosts.
* `ocp_must_gather`: Gathers an `oc adm must-gather` archive from an OpenShift cluster.
* `rh_case_update`: Uploads files and/or adds comments to a Red Hat Support Case.
* `rh_token_refresh`: Handles Red Hat API token authentication.

## Requirements

### Ansible Collections
This collection requires the following Ansible Collections to be installed:
* `community.general` (for the `archive` module used in the `ocp_must_gather` role)

### System Dependencies
This collection requires the following packages to be installed:

* **On the Target Hosts** (for the `sos_report` role):
    * `sos`: This is required to generate the `sosreport` and is installed by the role.

* **On the Control Node** (or execution node):
    * `curl` (for the `rh_case_update` role): This is required to upload large files to the Red Hat support portal. The role uses `ansible.builtin.shell` to execute `curl` for robust, streaming uploads.
    * `oc` (for the `ocp_must_gather` role): The OpenShift CLI (`oc`) must be installed and in the system's `PATH`. This role runs on `localhost` (the control node) to execute `oc` commands.

## Installing this collection

You can install the `infra.support_assist` collection with the Ansible Galaxy CLI:

```shell
ansible-galaxy collection install git+https://github.com/redhat-cop/infra.support_assist.git
```

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: infra.support_assist
    source: https://github.com/redhat-cop/infra.support_assist.git
    type: git
    # If you need a specific version of the collection, you can specify like this:
    # version: ...
```

## Usage

This collection includes primary playbooks that orchestrate the roles in the correct order. For detailed information on role-specific variables and advanced usage, please see the `README.md` file within each role's directory.

### Preparing Your Offline Token
> **💡 How to Generate a Red Hat Offline Token**
>
> 1.  Navigate to the Red Hat API Token management page: [https://access.redhat.com/management/api](https://access.redhat.com/management/api)
> 2.  Click the **"Generate Token"** button.
> 3.  Log in with your Red Hat customer portal credentials if prompted.
> 4.  A new offline token will be generated. **Copy this token immediately**, as Red Hat notes, "Tokens are only displayed once and are not stored. They will expire after 30 days of inactivity".

All playbooks that upload to a support case require a Red Hat Offline Token. The playbooks will look for it in this order:
1.  An extra-var named `offline_token`.
2.  An environment variable named `REDHAT_OFFLINE_TOKEN`.

### Playbooks

This collection provides three main playbooks for common operations:

* **`infra.support_assist.sos_report`**: Gathers `sosreport`s from all hosts in your inventory, fetches them to the control node, and uploads them to the specified case.
    * **Role-specific documentation:** [roles/sos_report/README.md](roles/sos_report/README.md)
    * **Example (using an environment variable):**
        ```shell
        export REDHAT_OFFLINE_TOKEN="YOUR_OFFLINE_TOKEN_HERE"
        
        ansible-playbook -i inventory infra.support_assist.sos_report \
          -e case_id=01234567 \
          -e upload=true \
          -e clean=true
        ```

* **`infra.support_assist.ocp_must_gather`**: Runs `oc adm must-gather` against a target OpenShift cluster, archives the result, and uploads it to the specified case. This playbook runs on `localhost`.
    * **Role-specific documentation:** [roles/ocp_must_gather/README.md](roles/ocp_must_gather/README.md)
    * **Example (passing token as an extra-var):**
        ```shell
        ansible-playbook -i inventory infra.support_assist.ocp_must_gather \
          -e case_id=01234567 \
          -e cluster_name=my-ocp-cluster \
          -e ocp_must_gather_server_url="https://api.my-ocp-cluster.com:6443" \
          -e ocp_must_gather_token="sha256~..." \
          -e offline_token=YOUR_OFFLINE_TOKEN_HERE
        ```

* **`infra.support_assist.rh_case_update`**: A utility playbook to upload local files or add comments to a case without gathering new diagnostics. This playbook runs on `localhost`.
    * **Role-specific documentation:** [roles/rh_case_update/README.md](roles/rh_case_update/README.md)
    * **Example (uploading a local file):**
      ```shell
      # Assuming REDHAT_OFFLINE_TOKEN is set as an environment variable
      ansible-playbook infra.support_assist.rh_case_update \
        -e case_id=01234567 \
        -e "case_updates_needed=[{'attachment': '/path/to/local/file.log', 'attachmentDescription': 'Manual log file upload.'}]"
      ```

    * **Example (adding a comment):**
      ```shell
      # Assuming REDHAT_OFFLINE_TOKEN is set as an environment variable
      ansible-playbook infra.support_assist.rh_case_update \
        -e case_id=01234567 \
        -e "case_updates_needed=[{'comment': 'Adding a comment via playbook.', 'commentType': 'plaintext'}]"
      ```

### Roles

You can also use the roles individually in your own custom playbooks. For detailed variable lists, requirements, and usage examples, see the README in each role's directory.

* **[sos_report](roles/sos_report/README.md)**: Installs `sos`, generates a `sosreport` on target hosts, and fetches it.
* **[ocp_must_gather](roles/ocp_must_gather/README.md)**: Logs into an OpenShift cluster, runs `oc adm must-gather`, and archives the result.
* **[rh_case_update](roles/rh_case_update/README.md)**: Uploads files or adds comments to a Red Hat Support Case.
* **[rh_token_refresh](roles/rh_token_refresh/README.md)**: Handles Red Hat API token authentication and caching.

## Release and Upgrade Notes

For details on changes between versions, please see [the changelog for this collection](https://github.com/redhat-cop/infra.support_assist/blob/devel/CHANGELOG.rst).

## Releasing, Versioning and Deprecation

This collection follows [Semantic Versioning](https://semver.org/). More details on versioning can be found [in the Ansible docs](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html#collection-versions).

We plan to regularly release new minor or bugfix versions once new features or bugfixes have been implemented.

Releasing the current major version happens from the `devel` branch.

## To Do / Roadmap (in no specific order)

  - [x] Add a role to use an offline token to get a refresh token for the Red Hat API
  - [x] Add a role that can upload files, or add comments to a Red Hat Support Case
  - [x] Add a role that will run `sos report` on one or more hosts
  - [x] Add a role that will run `oc adm must-gather` on an OpenShift cluster
  - [x] Add a playbook that can be used to attach other requested files to a Red Hat Support Case
  - [x] Add a playbook that can be used to add comments in either `markdown` or `plaintext` to a Red Hat Support Case
  - [ ] Add a role for grabbing output from one or more Ansible Automation Platform API endpoints
  - [ ] Add more CLI parameter options to the `sos_report` role (particularly `clean|mask`, etc.)
  - [ ] Make it easier to pick a defined scope if needed to the `ocp_must_gather` role (would replace/compliment the `container image` option)
  - [ ] Add the ability to actually open a **NEW** Red Hat Support Case (might warrant a role rename on `rh_case_update`)

## Contributing to this collection

We welcome community contributions to this collection. If you find problems, please open an issue or create a PR.

More information about contributing can be found in our [Contribution Guidelines.](https://github.com/redhat-cop/infra.support_assist/blob/devel/.github/CONTRIBUTING.md)

## Code of Conduct

This collection follows the Ansible project's [Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html). Please read and familiarize yourself with this document.

## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](https://github.com/redhat-cop/infra.support_assist/blob/devel/LICENSE) to see the full text.