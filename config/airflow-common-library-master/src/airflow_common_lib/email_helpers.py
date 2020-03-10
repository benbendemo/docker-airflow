from airflow.configuration import conf
from airflow.utils.email import send_email

TIME_DURATION_UNITS = (
    ('week', 60*60*24*7),
    ('day', 60*60*24),
    ('hour', 60*60),
    ('min', 60),
    ('sec', 1)
)

def human_time_duration(seconds):
    if seconds == 0:
        return 'inf'
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append('{} {}{}'.format(amount, unit, "" if amount == 1 else "s"))
    return ', '.join(parts)

def render_template(template, context, extra=None):
    ti = context.get('task_instance')
    jinja_env = ti.task.get_template_env()
    jinja_context = context
    if extra is not None:
        jinja_context.update(extra)

    return jinja_env.from_string(template).render(**jinja_context)

class EmailHelpers():
    def __init__(self, email_list):
        self.email_list = email_list
        
    def __render(self, key, context):
        exception = context.get('exception')
        ti = context.get('task_instance')

        jinja_context = context
        dag_run = jinja_context['dag_run']
        start_date = dag_run.start_date 
        end_date = dag_run.end_date or ti.end_date

        duration = human_time_duration((end_date - start_date).total_seconds())
        jinja_context.update(dict(duration=duration))

        if exception is not None:
            jinja_context.update(dict(
                exception=exception,
                exception_html=str(exception).replace('\n', '<br>'),
            ))

        jinja_env = ti.task.get_template_env()

        if conf.has_option('email', key):
            path = conf.get('email', key)
            with open(path) as f:
                content = f.read()

        return jinja_env.from_string(content).render(**jinja_context)

    def __render_subject(self, context):
        return self.__render('subject_template', context)

    def __render_content(self, context):
        return self.__render('html_content_template', context)

    def success_callback(self, context):
        """
        Callback that can be used in DAG to send an email on successful dag completion
        Args:
            context (dict): Context variable passed in from Airflow
        Returns:
            None: Calls the send_email method internally
        """

        subject = self.__render_subject(context)
        html_content = self.__render_content(context)

        return send_email(self.email_list, subject, html_content)

    def failure_callback(self, context):
        """
        Callback that can be used in DAG to alert of failure dag completion
        Args:
            context (dict): Context variable passed in from Airflow
        Returns:
            None: Calls the send_email method internally
        """

        subject = self.__render_subject(context)
        html_content = self.__render_content(context)
        
        return send_email(self.email_list, subject, html_content)
