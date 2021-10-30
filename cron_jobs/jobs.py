from pulumi_kubernetes.batch.v1 import JobSpecArgs
from pulumi_kubernetes.batch.v1beta1 import (
    CronJob,
    CronJobSpecArgs,
    JobTemplateSpecArgs,
)
from pulumi_kubernetes.core.v1 import ContainerArgs, PodSpecArgs, PodTemplateSpecArgs


def cron_job_test():
    CronJob(
        resource_name="failing-cron",
        metadata={"name": "failing-cron"},
        spec=CronJobSpecArgs(
            schedule="*/5 * * * *",
            job_template=JobTemplateSpecArgs(
                spec=JobSpecArgs(
                    template=PodTemplateSpecArgs(
                        spec=PodSpecArgs(
                            restart_policy="Never",
                            containers=[
                                ContainerArgs(
                                    name="failing-cron",
                                    image="ubuntu",
                                    image_pull_policy="IfNotPresent",
                                    command=["/bin/bash", "-c", "exit 1;"],
                                )
                            ],
                        )
                    )
                )
            ),
        ),
    )

    CronJob(
        resource_name="failing-cron-single",
        metadata={"name": "failing-cron-single"},
        spec=CronJobSpecArgs(
            schedule="*/5 * * * *",
            concurrency_policy="Forbid",
            failed_jobs_history_limit=1,
            job_template=JobTemplateSpecArgs(
                spec=JobSpecArgs(
                    backoff_limit=0,
                    template=PodTemplateSpecArgs(
                        spec=PodSpecArgs(
                            restart_policy="Never",
                            containers=[
                                ContainerArgs(
                                    name="failing-cron-single",
                                    image="ubuntu",
                                    image_pull_policy="IfNotPresent",
                                    command=["/bin/bash", "-c", "exit 1;"],
                                )
                            ],
                        )
                    ),
                )
            ),
        ),
    )

    CronJob(
        resource_name="successful-cron",
        metadata={"name": "successful-cron"},
        spec=CronJobSpecArgs(
            schedule="*/5 * * * *",
            job_template=JobTemplateSpecArgs(
                spec=JobSpecArgs(
                    template=PodTemplateSpecArgs(
                        spec=PodSpecArgs(
                            restart_policy="Never",
                            containers=[
                                ContainerArgs(
                                    name="successful-cron",
                                    image="ubuntu",
                                    image_pull_policy="IfNotPresent",
                                    command=["/bin/bash", "-c", "exit 0;"],
                                )
                            ],
                        )
                    )
                )
            ),
        ),
    )
    return
