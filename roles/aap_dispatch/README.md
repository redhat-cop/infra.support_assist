# infra.support_assist.aap_dispatch

## Description

An Ansible Role designed to create and manage the required AAP resources (Projects and Job Templates) needed to run the other roles and playbooks in the `infra.support_assist` collection. This role processes YAML files from `vars/job_templates.d/` and `vars/projects.d/` directories to set up the necessary AAP infrastructure for the collection's automation workflows.

**Note:** While this role could technically be used to manage other AAP projects and job templates, it is specifically designed and maintained for the `infra.support_assist` collection's internal use.

## Requirements

ansible-galaxy collection install -r tests/collections/requirements.yml to be installed

## Variables

|Variable Name|Default Value|Required|Description|Example|
|:---|:---:|:---:|:---|:---|
|`platform_state`|"present"|no|The state all objects will take unless overridden by object default|'absent'|
|`aap_hostname`|""|yes|URL to the Ansible Automation Platform Server.|127.0.0.1|
|`aap_validate_certs`|`true`|no|Whether or not to validate the Ansible Automation Platform Server's SSL certificate.||
|`aap_username`|""|no|Admin User on the Ansible Automation Platform Server. Either username / password or oauthtoken need to be specified.||
|`aap_password`|""|no|Platform Admin User's password on the Server.  This should be stored in an Ansible Vault at vars/platform-secrets.yml or elsewhere and called from a parent playbook.||
|`aap_token`|""|no|Controller Admin User's token on the Ansible Automation Platform Server. This should be stored in an Ansible Vault at or elsewhere and called from a parent playbook. Either username / password or oauthtoken need to be specified.||
|`aap_request_timeout`|`10`|no|Specify the timeout in seconds Ansible should use in requests to the Ansible Automation Platform host.||
|`aap_dispatch_collect_logs`|`false`|no|Specify whether to collect async results and continue for all failed async tasks instead of failing on the first error. Collected results are available in the `aap_dispatch_role_errors` variable.||

### Enforcing defaults

The following Variables complement each other.
If Both variables are not set, enforcing default values is not done.
Enabling these variables enforce default values on options that are optional in the controller API.
This should be enabled to enforce configuration and prevent configuration drift. It is recommended to be enabled, however it is not enforced by default.

Enabling this will enforce configuration without specifying every option in the configuration files.

|Variable Name|Default Value|Required|Description|
|:---:|:---:|:---:|:---:|
|`aap_dispatch_enforce_defaults`|`false`|no|Whether or not to enforce default option values for all resources managed by this role.|

### Secure Logging Variables

The following Variables control secure logging for the role.
If the variable is not set, secure logging defaults to false.
The role defaults to false as normally the tasks do not include sensitive information.

|Variable Name|Default Value|Required|Description|
|:---:|:---:|:---:|:---:|
|`aap_dispatch_secure_logging`|`false`|no|Whether or not to include the sensitive role tasks in the log. Set this value to `true` if you will be providing your sensitive values from elsewhere.|

### Asynchronous Retry Variables

The following Variables set asynchronous retries for the role.
If neither of the retries or delay or retries are set, they will default to their respective defaults.
This allows for all items to be created, then checked that the task finishes successfully.
This also speeds up the overall role.

|Variable Name|Default Value|Required|Description|
|:---:|:---:|:---:|:---:|
|`aap_dispatch_async_retries`|50|no|This variable sets the number of retries to attempt for the role globally.|
|`aap_dispatch_async_delay`|1|no|This sets the delay between retries for the role globally.|
|`aap_dispatch_loop_delay`|0|no|This sets the pause between each item in the loop for the roles globally. To help when API is getting overloaded.|
|`aap_dispatch_async_dir`|`null`|no|Sets the directory to write the results file for async tasks. The default value is set to `null` which uses the Ansible Default of `/root/.ansible_async/`.|

## File-Based Configuration

This role uses a file-based approach for managing the AAP resources required by the `infra.support_assist` collection. Configuration files are placed in the following directories:

- **Job Templates**: `vars/job_templates.d/` - YAML files containing job template definitions for collection workflows
- **Projects**: `vars/projects.d/` - YAML files containing project definitions for the collection's source code

Each file in these directories is processed independently. The role will:
1. Find all YAML files (`.yml` or `.yaml`) in each directory
2. Process each file sequentially
3. Include variables from each file
4. Create/update the resources defined in that file

These resources are specifically configured to support the execution of roles and playbooks within the `infra.support_assist` collection.

### File Structure

Each configuration file should contain either:
- `controller_templates` or `job_templates` - for job template definitions
- `controller_projects` or `projects` - for project definitions

## Data Structure

### Job Template Variables

|Variable Name|Default Value|Required|Type|Description|
|:---:|:---:|:---:|:---:|:---:|
|`name`|""|yes|str|Name of Job Template|
|`new_name`|""|no|str|Setting this option will change the existing name (looked up via the name field).|
|`copy_from`|""|no|str|Name or id to copy the job template from. This will copy an existing credential and change any parameters supplied.|
|`description`|`false`|no|str|Description to use for the job template.|
|`execution_environment`|""|no|str|Execution Environment to use for the job template.|
|`job_type`|`run`|no|str|The job type to use for the job template(run, check).|
|`inventory`|""|no|str|Name of the inventory to use for the job template.|
|`organization`|""|no|str|Organization the job template exists in. Used to help lookup the object, cannot be modified using this module. The Organization is inferred from the associated project|
|`project`|""|no|str|Name of the project to use for the job template.|
|`playbook`|""|no|str|Path to the playbook to use for the job template within the project provided.|
|`credentials`|""|no|list|List of credentials to use for the job template.|
|`forks`|""|no|int|The number of parallel or simultaneous processes to use while executing the playbook.|
|`limit`|""|no|str|A host pattern to further constrain the list of hosts managed or affected by the playbook|
|`verbosity`|""|no|int|Control the output level Ansible produces as the playbook runs. 0 - Normal, 1 - Verbose, 2 - More Verbose, 3 - Debug, 4 - Connection Debug .|
|`extra_vars`|""|no|dict|Specify extra_vars for the template.|
|`job_tags`|""|no|str|Comma separated list of the tags to use for the job template.|
|`force_handlers`|""|no|bool|Enable forcing playbook handlers to run even if a task fails.|
|`skip_tags`|""|no|str|Comma separated list of the tags to skip for the job template.|
|`start_at_task`|""|no|str|Start the playbook at the task matching this name.|
|`diff_mode`|""|no|bool|Enable diff mode for the job template |
|`use_fact_cache`|""|no|bool|Enable use of fact caching for the job template.|
|`host_config_key`|""|no|str|Allow provisioning callbacks using this host config key.|
|`ask_scm_branch_on_launch`|""|no|bool|Prompt user for scm branch on launch.|
|`ask_diff_mode_on_launch`|""|no|bool|Prompt user to enable diff mode show changes to files when supported by modules.|
|`ask_variables_on_launch`|""|no|bool|Prompt user for extra_vars on launch.|
|`ask_limit_on_launch`|""|no|bool|Prompt user for a limit on launch.|
|`ask_tags_on_launch`|""|no|bool|Prompt user for job tags on launch.|
|`ask_skip_tags_on_launch`|""|no|bool|Prompt user for job tags to skip on launch.|
|`ask_job_type_on_launch`|""|no|bool|Prompt user for job type on launch.|
|`ask_verbosity_on_launch`|""|no|bool|Prompt user to choose a verbosity level on launch.|
|`ask_inventory_on_launch`|""|no|bool|Prompt user for inventory on launch.|
|`ask_credential_on_launch`|""|no|bool|Prompt user for credential on launch.|
|`ask_execution_environment_on_launch`|""|no|bool|Prompt user for execution environment on launch.|
|`ask_forks_on_launch`|""|no|bool|Prompt user for forks on launch.|
|`ask_instance_groups_on_launch`|""|no|bool|Prompt user for instance groups on launch.|
|`ask_job_slice_count_on_launch`|""|no|bool|Prompt user for job slice count on launch.|
|`ask_labels_on_launch`|""|no|bool|Prompt user for labels on launch.|
|`ask_timeout_on_launch`|""|no|bool|Prompt user for timeout on launch.|
|`prevent_instance_group_fallback`|""|no|bool|Prevent falling back to instance groups set on the associated inventory or organization.|
|`survey_enabled`|""|no|bool|Enable a survey on the job template.|
|`survey_spec`|""|no|dict|JSON/YAML dict formatted survey definition.|
|`survey`|""|no|dict|JSON/YAML dict formatted survey definition. Alias of survey_spec|
|`become_enabled`|""|no|bool|Activate privilege escalation.|
|`allow_simultaneous`|""|no|bool|Allow simultaneous runs of the job template.|
|`timeout`|""|no|int|Maximum time in seconds to wait for a job to finish (server-side).|
|`instance_groups`|""|no|list|list of Instance Groups for this Job Template to run on.|
|`job_slice_count`|""|no|int|The number of jobs to slice into at runtime. Will cause the Job Template to launch a workflow if value is greater than 1.|
|`webhook_service`|""|no|str|Service that webhook requests will be accepted from (github, gitlab)|
|`webhook_credential`|""|no|str|Personal Access Token for posting back the status to the service API|
|`scm_branch`|""|no|str|Branch to use in job run. Project default used if blank. Only allowed if project allow_override field is set to true.|
|`labels`|""|no|list|The labels applied to this job template. NOTE: Labels must be created with the [labels](https://github.com/redhat-cop/job_templates/tree/devel/roles/controller_labels) role first, an error will occur if the label supplied to this role does not exist.|
|`custom_virtualenv`|""|no|str|Local absolute file path containing a custom Python virtualenv to use.|
|`notification_templates_started`|""|no|list|The notifications on started to use for this organization in a list.|
|`notification_templates_success`|""|no|list|The notifications on success to use for this organization in a list.|
|`notification_templates_error`|""|no|list|The notifications on error to use for this organization in a list.|
|`state`|`present`|no|str|Desired state of the resource.|

### Project Variables

|Variable Name|Default Value|Required|Type|Description|
|:---:|:---:|:---:|:---:|:---:|
|`name`|""|yes|str|Name of Project|
|`new_name`|""|no|str|Setting this option will change the existing name (looked up via the name field).|
|`copy_from`|""|no|str|Name or id to copy the project from. This will copy an existing project and change any parameters supplied.|
|`description`|""|no|str|Description to use for the project.|
|`scm_type`|`manual`|no|str|Type of SCM resource. Choices: manual, git, hg, svn, insights|
|`scm_url`|""|no|str|The location where the project is stored.|
|`default_environment`|""|no|str|Default execution environment to use for jobs running using this project.|
|`local_path`|""|no|str|Local filesystem path where the project is stored.|
|`scm_branch`|""|no|str|The branch to use for the SCM resource.|
|`scm_refspec`|""|no|str|The refspec to use for the SCM resource.|
|`credential`|""|no|str|Name of the credential to use with this SCM resource.|
|`scm_credential`|""|no|str|Alias for credential.|
|`signature_validation_credential`|""|no|str|Credential to use for validating signatures of the project.|
|`scm_clean`|`false`|no|bool|Remove local modifications before updating.|
|`scm_delete_on_update`|`false`|no|bool|Delete the project before syncing.|
|`scm_track_submodules`|`false`|no|bool|Track submodules latest commit on any branch.|
|`scm_update_on_launch`|`false`|no|bool|Update the project when a job is launched.|
|`scm_update_cache_timeout`|`0`|no|int|Cache timeout in seconds for the project.|
|`allow_override`|`false`|no|bool|Allow branch/refspec override for job templates.|
|`timeout`|`0`|no|int|Maximum time in seconds to wait for a project update job to finish.|
|`job_timeout`|`0`|no|int|Alias for timeout.|
|`custom_virtualenv`|""|no|str|Local absolute file path containing a custom Python virtualenv to use.|
|`organization`|""|no|str|Organization the project exists in.|
|`state`|`present`|no|str|Desired state of the resource.|
|`wait`|`true`|no|bool|Wait for the project update job to finish.|
|`update_project`|`false`|no|bool|Trigger a project update after creating/updating.|
|`interval`|`1`|no|int|Interval in seconds to check for project update job completion.|
|`notification_templates_started`|""|no|list|The notifications on started to use for this project in a list.|
|`notification_templates_success`|""|no|list|The notifications on success to use for this project in a list.|
|`notification_templates_error`|""|no|list|The notifications on error to use for this project in a list.|

### Surveys

Refer to the [controller Api Guide](https://docs.ansible.com/ansible-tower/latest/html/towerapi/api_ref.html#/Job_Templates/Job_Templates_job_templates_survey_spec_create) for more information about forming surveys

|Variable Name|Variable Description|
|:---:|:---:|
|`name`|Name of the survey|
|`description`|Description of the survey|
|`spec`|List of survey items, each a dictionary containing the following fields|
|`question_name`|Name of the field/item|
|`question_description`|Longer description|
|`required`|Boolean expressing if an answer is required|
|`type`|One of `text`, `password`, `integer`, `float`, `multiplechoice`or `multiselect`|
|`variable`|Name of Ansible Variable where to put the answer|
|`default`|Default value for the variable|
|`min`|Minimum value for a number type|
|`max`|Maximum value for a number type|
|`choices`|List of choices for a "multi" type|
|`new_question`|Boolean|

## Data Structure Examples

### Job Template File Example

Place this in `vars/job_templates.d/my-job-template.yml`:

```yaml
---
controller_templates:
  - name: Survey Template with vars
    job_type: run
    inventory: Demo Inventory
    execution_environment: my_exec_env
    survey_enabled: true
    survey: "{{ lookup('template', 'template_surveys/basic_survey.json') | regex_replace('\\n', '') }}"
    project: controller Config
    playbook: helloworld.yml
    credentials:
      - Demo Credential
    extra_vars: "{{ survey_extra_vars }}"
    notification_templates_error:
      - Slack_for_testing
  - name: No Survey Template no vars
    job_type: run
    inventory: Demo Inventory
    project: controller Config
    playbook: helloworld.yml
    credentials:
      - Demo Credential
    survey: {}
    extra_vars: "{{ empty_master_vars }}"
    notification_templates_error:
      - Slack_for_testing
```

### Project File Example

Place this in `vars/projects.d/my-project.yml`:

```yaml
---
controller_projects:
  - name: 'My Project'
    description: 'My Project Description'
    organization: 'My Organization'
    scm_type: 'git'
    scm_url: 'https://github.com/user/repo.git'
    scm_credential: 'GitHub Credential'
    scm_branch: 'main'
    scm_clean: false
    scm_delete_on_update: false
    scm_update_on_launch: true
    scm_update_cache_timeout: 0
    scm_refspec: ''
    allow_override: false
    update_project: true
    timeout: 0
```

### Survey Data Structure Example

```json
{
    "name": "Basic Survey",
    "description": "Basic Survey",
    "spec": [
      {
        "question_description": "Name",
        "min": 0,
        "default": "",
        "max": 128,
        "required": true,
        "choices": "",
        "new_question": true,
        "variable": "basic_name",
        "question_name": "Basic Name",
        "type": "text"
      },
      {
        "question_description": "Choosing yes or no.",
        "min": 0,
        "default": "yes",
        "max": 0,
        "required": true,
        "choices": "yes\nno",
        "new_question": true,
        "variable": "option_true_false",
        "question_name": "Choose yes or no?",
        "type": "multiplechoice"
      },
      {
        "question_description": "",
        "min": 0,
        "default": "",
        "max": 0,
        "required": true,
        "choices": "group1\ngroup2\ngroup3",
        "new_question": true,
        "variable": "target_groups",
        "question_name": "Select Group:",
        "type": "multiselect"
      }
    ]
  }
```

## Playbook Examples

### Standard Role Usage

This role is typically used as part of the `infra.support_assist` collection setup to create the necessary AAP infrastructure:

```yaml
---
- name: Setup AAP infrastructure for infra.support_assist collection
  hosts: localhost
  connection: local
  # Define following vars here, or in aap_configs/auth.yml
  # aap_hostname: aap.example.com
  # aap_username: admin
  # aap_password: changeme
  roles:
    - role: infra.support_assist.aap_dispatch
```

The role will automatically:
1. Process all YAML files in `vars/projects.d/` to create/update the collection's required projects
2. Process all YAML files in `vars/job_templates.d/` to create/update the collection's job templates

These job templates are designed to execute the playbooks and roles from the `infra.support_assist` collection, enabling automated execution of support case management, must-gather operations, and other collection workflows.

### Using with Custom Variable Files

```yaml
---
- name: Setup AAP infrastructure for infra.support_assist collection
  hosts: localhost
  connection: local
  vars:
    aap_hostname: aap.example.com
    aap_username: admin
    aap_password: "{{ vault_aap_password }}"
    aap_dispatch_enforce_defaults: true
    aap_dispatch_secure_logging: true
  roles:
    - role: infra.support_assist.aap_dispatch
```

**Purpose:** This role sets up the AAP projects and job templates that are required to run the other roles in the `infra.support_assist` collection, such as:
- Red Hat Support Case creation and updates
- OpenShift must-gather operations
- SOS report generation
- AAP API data gathering

## Credits

This role is based on and adapted from code in the [infra.aap_configuration](https://github.com/redhat-cop/infra.aap_configuration) collection. Specifically:

- The job template and project management task structures were adapted from the `infra.aap_configuration` collection roles
- The async handling and error management patterns follow the same approach used in the collection
- Variable naming conventions and defaults are based on patterns from the collection

The file-based configuration approach (processing YAML files from `vars/job_templates.d/` and `vars/projects.d/`) is a custom enhancement for this role.

## License

[GPL-3.0-or-later](LICENSE)

## Author

[Lenny Shirley](https://github.com/lennysh)
