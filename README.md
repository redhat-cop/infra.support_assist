# Ansible Collection - infra.support_assist

This Ansible Collection will gather various reports/outputs that are commonly asked for in Red Hat Support Cases, and can optionally upload them directly to the Support Case Portal.

## Requirements

### Ansible Collections
This collection has no external Ansible Collection dependencies.

### System Dependencies
This collection requires the following packages to be installed:

* **On the Target Hosts** (for the `sos_report` role):
    * `sos`: This is required to generate the `sosreport` and is installed by the role.

* **On the Control Node** (for the `case_file_upload` role):
    * `curl`: This is required to upload large files to the Red Hat support portal. The role uses `ansible.builtin.shell` to execute `curl` for robust, streaming uploads.

## Installing this collection

You can install the `infra.support_assist` collection with the Ansible Galaxy CLI:

```shell
ansible-galaxy collection install git+https://github.com/redhat-cop/infra.support_assist.git
```

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: https://github.com/redhat-cop/infra.support_assist.git
    type: git
    # If you need a specific version of the collection, you can specify like this:
    # version: ...
```

## Usage

This collection includes a primary playbook, `infra.support_assist.sos_report`, which runs all the roles in the correct order. Here are the recommended ways to run it.

### Option 1: Using ansible-core (CLI)

This method is ideal for local execution or simple, command-line-driven automation.

1.  **Prepare Your Offline Token:**
    You must provide your Red Hat Offline Token. The playbook will look for it in this order:
    1.  An extra-var named `offline_token`.
    2.  An environment variable named `REDHAT_OFFLINE_TOKEN`.

2.  **Run the Playbook:**
    Execute the collection's built-in playbook using its Fully Qualified Collection Name (FQCN).

    **Example (passing token as an extra-var):**
    ```shell
    ansible-playbook -i inventory infra.support_assist.sos_report \
      -e case_id=04288106 \
      -e upload=true \
      -e clean=true \
      -e offline_token=YOUR_OFFLINE_TOKEN_HERE
    ```

    **Example (using an environment variable):**
    ```shell
    export REDHAT_OFFLINE_TOKEN="YOUR_OFFLINE_TOKEN_HERE"
    
    ansible-playbook -i inventory infra.support_assist.sos_report \
      -e case_id=04288106 \
      -e upload=true \
      -e clean=true
    ```

    * `case_id`: (Required) The Red Hat Support Case number to associate the report with.
    * `upload`: (Optional) Set to `true` to upload the report(s). Defaults to `true`.
    * `clean`: (Optional) Set to `true` to remove the `sosreport` from the target hosts after fetching. Defaults to `false`.

### Option 2: Using Ansible Automation Platform (AAP)

This method is recommended for integrating into a larger automated workflow, providing RBAC, and securely managing credentials.

*(Configuration-as-code for AAP is currently in development and will be added to this repository.)*

When complete, this repository will include configuration to automatically create:

* **Custom Credential Type:** A new credential type in AAP specifically for "Red Hat Support Offline Token" to securely store and inject your token at runtime. This will be automatically mapped to the `offline_token` variable.
* **Job Template:** A pre-configured Job Template ready to run the `infra.support_assist.sos_report` playbook.
* **Survey:** The Job Template will include a survey to easily prompt for:
    * `case_id`
    * `upload` (as a checkbox)
    * `clean` (as a checkbox)

## Release and Upgrade Notes

For details on changes between versions, please see [the changelog for this collection](https://github.com/redhat-cop/infra.support_assist/blob/devel/CHANGELOG.rst).

## Releasing, Versioning and Deprecation

This collection follows [Semantic Versioning](https://semver.org/). More details on versioning can be found [in the Ansible docs](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html#collection-versions).

We plan to regularly release new minor or bugfix versions once new features or bugfixes have been implemented.

Releasing the current major version happens from the `devel` branch.

## Roadmap (in no specific order)

  - Add a role for running `must-gather` commands.
  - Add support for attaching other common diagnostic files.
  - Add support for grabbing output from one more more API calls

## Contributing to this collection

We welcome community contributions to this collection. If you find problems, please open an issue or create a PR.

More information about contributing can be found in our [Contribution Guidelines.](https://github.com/redhat-cop/infra.support_assist/blob/devel/.github/CONTRIBUTING.md)

## Code of Conduct

This collection follows the Ansible project's [Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html). Please read and familiarize yourself with this document.

## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](https://github.com/redhat-cop/infra.support_assist/blob/devel/LICENSE) to see the full text.