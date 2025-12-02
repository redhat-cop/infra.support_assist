# infra.support_assist.aap_api_dump

This role gathers diagnostic output from Ansible Automation Platform (AAP) component APIs (Controller, Hub, EDA) and saves them as JSON files. The role can then create a compressed archive of all collected data and prepare it for upload to a Red Hat Support Case via the `rh_case` role.

## Requirements

* **On Control Node:**
    * `community.general` collection (for the `archive` module used to create the tarball)

* **AAP API Access:**
    * Valid AAP API token (obtained via `aap_api_token` role or provided directly)
    * Network access to AAP component URLs (Controller, Hub, EDA)

## Role Variables

### Input Variables

* `aap_token`:
    * **(Required)** A valid AAP API access token. This is typically provided by running the `infra.support_assist.aap_api_token` role first.
    * Can also be provided via extra-var or environment variable (`AAP_TOKEN` or `aap_token`).
    * Type: `string`

* `aap_gateway_url`:
    * **(Optional)** The base URL for the AAP Gateway. If provided, this will be used as a fallback for component URLs that are not explicitly set.
    * Can be provided via extra-var or environment variable (`AAP_GATEWAY_URL`).
    * Type: `string`

* `aap_controller_url`:
    * **(Required if `controller` is in `aap_api_dump_components`)** The base URL for the AAP Controller API.
    * If not provided, will default to `aap_gateway_url` if available.
    * Can be provided via extra-var or environment variable (`AAP_CONTROLLER_URL`).
    * Type: `string`

* `aap_hub_url`:
    * **(Required if `hub` is in `aap_api_dump_components`)** The base URL for the AAP Hub API.
    * If not provided, will default to `aap_gateway_url` if available.
    * Can be provided via extra-var or environment variable (`AAP_HUB_URL`).
    * Type: `string`

* `aap_eda_url`:
    * **(Required if `eda` is in `aap_api_dump_components`)** The base URL for the AAP EDA API.
    * If not provided, will default to `aap_gateway_url` if available.
    * Can be provided via extra-var or environment variable (`AAP_EDA_URL`).
    * Type: `string`

* `aap_api_dump_components`:
    * List of AAP components to query. Valid options: `controller`, `hub`, `eda`.
    * Default: `['controller', 'hub', 'eda']`
    * Type: `list`

* `aap_api_dump_dest`:
    * Destination directory on the control node where API outputs will be saved.
    * Default: `/tmp/aap_api_dumps`
    * Type: `string`

* `aap_validate_certs`:
    * Whether to validate SSL/TLS certificates when making API requests.
    * Default: `true`
    * Type: `bool`

### Output Variables

* `case_updates_needed`:
    * This fact is set after successful API collection and archive creation.
    * Contains a list with one dictionary entry:
        * `attachment`: Full path to the created tarball archive
        * `attachmentDescription`: Description of the archive including hostname, FQDN, and components queried
    * This fact is ready for use with the `infra.support_assist.rh_case` role.

## Dependencies

* This role **should** be run after `infra.support_assist.aap_api_token` to populate the required `aap_token` fact.
* This role **can** be followed by `infra.support_assist.rh_case` to upload the created archive to a Red Hat Support Case.

## Example Playbook

### Example 1: Basic API Dump (Standalone)

```yaml
- name: Gather AAP API Data
  hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - name: Get AAP API Token
      ansible.builtin.include_role:
        name: infra.support_assist.aap_api_token

    - name: Gather API Data
      ansible.builtin.include_role:
        name: infra.support_assist.aap_api_dump
      vars:
        aap_controller_url: "https://aap-controller.example.com"
        aap_hub_url: "https://aap-hub.example.com"
        aap_api_dump_components:
          - controller
          - hub
```

### Example 2: Full Pipeline (Dump + Case Upload)

```yaml
- name: AAP API Dump and Case Upload
  hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - name: AAP API Dump Block
      block:
        - name: Get AAP API Token
          ansible.builtin.include_role:
            name: infra.support_assist.aap_api_token

        - name: Gather API Data
          ansible.builtin.include_role:
            name: infra.support_assist.aap_api_dump
          vars:
            aap_controller_url: "https://aap-controller.example.com"
            aap_hub_url: "https://aap-hub.example.com"

      always:
        - name: Clear AAP Token
          ansible.builtin.include_role:
            name: infra.support_assist.aap_api_token
            tasks_from: clear_token.yml

    - name: Case Upload Block
      when:
        - upload | default(true) | bool
        - case_updates_needed is defined
        - case_updates_needed | length > 0
      block:
        - name: Get Red Hat API Token
          ansible.builtin.include_role:
            name: infra.support_assist.rh_token_refresh

        - name: Upload to Case
          ansible.builtin.include_role:
            name: infra.support_assist.rh_case
          vars:
            case_id: "01234567"
```

### Example 3: Using Environment Variables

```bash
export AAP_CONTROLLER_URL="https://aap-controller.example.com"
export AAP_HUB_URL="https://aap-hub.example.com"
export AAP_TOKEN="your-token-here"

ansible-playbook playbook.yml
```

## Output

The role creates the following structure on the control node:

```
{{ aap_api_dump_dest }}/{{ inventory_hostname }}/{{ component_name }}/{{ sanitized_endpoint_path }}.json
```

For example:
```
/tmp/aap_api_dumps/localhost/controller/api_controller_v2_ping_.json
/tmp/aap_api_dumps/localhost/controller/api_controller_v2_instances_.json
/tmp/aap_api_dumps/localhost/hub/pulp_api_v3_status_.json
```

After collection, the role creates a compressed tarball:
```
{{ aap_api_dump_dest }}/aap-api-dump-{{ hostname }}-{{ date }}-{{ time }}.tar.gz
```

The tarball contains all JSON files from the collection and is automatically added to `case_updates_needed` for upload via the `rh_case` role.

## API Endpoints

The role queries predefined API endpoints for each component. These are defined in `vars/main.yml`:

* **Controller**: `/api/controller/v2/ping/`, `/api/controller/v2/instances/`, `/api/controller/v2/settings/all/`
* **Hub**: `/pulp/api/v3/status/`, `/pulp/api/v3/tasks/`
* **EDA**: (Currently empty - can be customized)

## Notes

* The role automatically sanitizes endpoint paths to create safe filenames (replacing `/`, `?`, `&`, `=` with `_`).
* Failed API requests are logged but do not stop the collection process (the role uses `ignore_errors: true`).
* The archive creation step only runs if the source directory exists and contains files.
* All operations run on `localhost` (control node) using `delegate_to: localhost` and `run_once: true`.

## License

GPL-3.0-or-later

## Author Information

Lenny Shirley
