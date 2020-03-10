# Airflow common library
This repo provide a python module that provide some common functions for airflow job.

# API
## Slack
The slack helpers contains two functions:
`task_fail_slack_alert`: Send out an failure message to slack
`task_success_slack_alert`: Send out an success message to slack

### Prerequisite
- Make sure a slack connection is created on airflow.
  - Conn id: `slack`
  - Conn type: `HTTP`
  - Registry URL: `https://hooks.slack.com/services` <-- Base url of the webhook url

### Example
Import these functions in a DAG.
To trigger a message on any task failure, set `task_fail_slack_alert` to `on_failure_callback` in default_args.
To trigger a message on any task success, set `task_success_slack_alert` to `on_success_callback` in default_args.
To trigger a message on a particular task failure, set `task_fail_slack_alert` to `on_failure_callback` in the operator.
To trigger a message on a particular task success, set `task_success_slack_alert` to `on_success_callback` in the operator.

These two function
```python
from airflow_common_lib.slack_helpers import SlackHelpers
task_fail_slack_alert, task_success_slack_alert
slack = SlackHelpers(webhook_token='/TXXXXXXXX/XXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX/')
# ...

default_args = {
    "on_failure_callback": slack.task_fail_slack_alert,
}
# ...
with DAG(
    "dag_id",
    default_args=default_args
) as dag:
# ...
t1 = PythonOperator(
        task_id="task_id",
        python_callable=coin_flip,
        on_success_callback=slack.task_success_slack_alert)

```

To obtain a webhook_token, make sure to create a new incoming webhook for your project.

# Development
## Virtual env
Create virtual env
```sh
python3 -m venv .venv
```

Activate virtual env
```sh
. .venv/bin/activate
```
## Build & Upload
Build
```sh
python3 setup.py sdist
```

Upload
```sh
twine upload --repository-url ${NEXUS_PIP_URL} -u ${NEXUS_USERNAME} -p ${NEXUS_PASSWORD} dist/*
```
