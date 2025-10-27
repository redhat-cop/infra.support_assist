# infra.support_assist.rh_token_refresh

The `infra.support_assist.rh_token_refresh` Ansible role is designed to **retrieve an access token for the Red Hat API using an offline token**. This token is then cached locally to manage its lifecycle and avoid unnecessary API calls.

This role runs on `localhost`.

## Requirements

None.

## Role Variables

### Input Variables

The behavior of the `rh_token_refresh` role is controlled by the following variables:

* `rh_token_refresh_api_offline_token`:
    * **(Required)** Your **Red Hat offline token**. This token is used by the role to acquire the necessary access token for the Red Hat API.
    * Default: `{{ offline_token | default(lookup('env', 'REDHAT_OFFLINE_TOKEN')) }}` (Inherits `offline_token` var or the `REDHAT_OFFLINE_TOKEN` environment variable)
    * Type: `string`

* `rh_token_refresh_token_cache_file`:
    * The **full path to a file** where the obtained access token and its timestamp will be cached locally.
    * Default: `"/tmp/redhat_refresh_token.json"`
    * Type: `path`

* `rh_token_refresh_token_max_age_seconds`:
    * The **maximum age (in seconds)** of a cached access token before it is considered invalid and a new one must be retrieved.
    * Default: `900` (15 minutes)
    * Type: `int`

* `rh_token_refresh_api_token_url`:
    * The **full URL for the Red Hat SSO token endpoint**.
    * Default: `"https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token"`
    * Type: `string`

### Output Variables

This role sets the following fact, which can be used by subsequent tasks or roles (like `rh_case_update`):

* `rh_token_refresh_api_access_token`:
    * This variable will contain the **valid Red Hat API access token** after the role has successfully run. This token is either retrieved from the local cache or newly obtained from the Red Hat SSO service.

## Dependencies

None.

## Example Playbook

Here's an example of how to use the `infra.support_assist.rh_token_refresh` role directly.

```yaml
- name: Get Red Hat API Access Token
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    # You can provide the token directly (Ansible Vault recommended)
    # offline_token: "YOUR_REDHAT_OFFLINE_TOKEN_HERE"
    # Or, the role will pick it up from the environment variable
    # REDHAT_OFFLINE_TOKEN="YOUR_REDHAT_OFFLINE_TOKEN_HERE"

  tasks:
    - name: Retrieve Red Hat API access token
      ansible.builtin.include_role:
        name: infra.support_assist.rh_token_refresh
      vars:
        # Optional: Customize cache file location or token validity
        rh_token_refresh_token_cache_file: "/home/ansible/.redhat_api_token.json"
        rh_token_refresh_token_max_age_seconds: 3600 # Cache for 1 hour

    - name: Use the retrieved access token in a subsequent task
      ansible.builtin.debug:
        msg: "The access token is: {{ rh_token_refresh_api_access_token }}"
```

## License

This role is licensed under **GPL-3.0-or-later**.

## Author Information

- Lenny Shirley