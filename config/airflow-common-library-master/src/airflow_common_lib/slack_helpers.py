from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator

SLACK_CONN_ID = "slack"

class SlackHelpers():
    def __init__(self, webhook_token):
        self.webhook_token = webhook_token

    def task_success_alert(self, context):
        """
        Callback task that can be used in DAG to alert of successful task completion
        Args:
            context (dict): Context variable passed in from Airflow
        Returns:
            None: Calls the SlackWebhookOperator execute method internally
        """
        slack_msg = """
                :large_blue_circle: Task Succeeded!
                *Task*: {task}
                *Dag*: {dag}
                *Execution Time*: {exec_date}
                *Log Url*: {log_url}
                """.format(
            task=context.get("task_instance").task_id,
            dag=context.get("task_instance").dag_id,
            ti=context.get("task_instance"),
            exec_date=context.get("execution_date"),
            log_url=context.get("task_instance").log_url,
        )

        success_alert = SlackWebhookOperator(
            task_id="slack_test",
            http_conn_id=SLACK_CONN_ID,
            webhook_token=self.webhook_token,
            message=slack_msg,
            username="airflow",
        )

        return success_alert.execute(context=context)

    def task_fail_alert(self, context):
        """
        Callback task that can be used in DAG to alert of failure task completion
        Args:
            context (dict): Context variable passed in from Airflow
        Returns:
            None: Calls the SlackWebhookOperator execute method internally
        """
        slack_msg = """
                :red_circle: Task Failed.
                *Task*: {task}
                *Dag*: {dag}
                *Execution Time*: {exec_date}
                *Log Url*: {log_url}
                """.format(
            task=context.get("task_instance").task_id,
            dag=context.get("task_instance").dag_id,
            ti=context.get("task_instance"),
            exec_date=context.get("execution_date"),
            log_url=context.get("task_instance").log_url,
        )

        failed_alert = SlackWebhookOperator(
            task_id="slack_test",
            http_conn_id=SLACK_CONN_ID,
            webhook_token=self.webhook_token,
            message=slack_msg,
            username="airflow",
        )

        return failed_alert.execute(context=context)
