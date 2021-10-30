from common.helpers import create_pvc
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts


def ml_flow(
    hostname: str,
    uid=1000,
    gid=1000,
):
    minio_access_key = "minio"
    minio_secret_key = "minio123"  # pragma: allowlist secret

    _, minio_pvc, _ = create_pvc(
        name="mlflow-minio",
        path="/mnt/500G_SSD/kube_config/config/mlflow_minio",
        size="8Gi",
        access_mode="ReadWriteOnce",
    )

    Chart(
        "minio",
        config=ChartOpts(
            chart="minio",
            version="8.1.9",
            fetch_opts=FetchOpts(
                repo="https://charts.bitnami.com/bitnami",
            ),
            values={
                "podSecurityContext": {
                    "fsGroup": 1000,
                },
                "containerSecurityContext": {
                    "runAsUser": 1000,
                },
                "accessKey": {
                    "password": minio_access_key,
                },
                "secretKey": {
                    "password": minio_secret_key,
                },
                # "mode": "standalone",
                "ingress": {
                    "enabled": "true",
                    "hostname": f"minio.{hostname}",
                },
                "persistence": {
                    "enabled": "false",
                    "existingClaim": minio_pvc.metadata.apply(lambda v: v["name"]),
                },
                "statefulset": {
                    "replicaCount": 1,
                },
                # "podAnnotations": {
                #     "prometheus.io/scrape": "true",
                #     "prometheus.io/path": "/minio/v2/metrics/cluster",
                #     "prometheus.io/port": 9000,
                # }
            },
        ),
    )

    # user = pulumi_minio.IamUser("python-user")

    mysql_root_password = "mlflow123"  # pragma: allowlist secret
    mysql_database = "mlflow"
    mysql_username = "mlflow"
    mysql_password = "mlflow123"  # pragma: allowlist secret

    if True:

        mlflow_mysql_pv, mlflow_mysql_pvc, _ = create_pvc(
            name="mlflow-mysql",
            path="/mnt/500G_SSD/kube_config/config/mlflow_mysql",
            size="8Gi",
            access_mode="ReadWriteOnce",
            storage_class_name="microk8s-hostpath",
        )

        Chart(
            "mysql",
            config=ChartOpts(
                chart="mysql",
                version="8.8.12",
                fetch_opts=FetchOpts(
                    repo="https://charts.bitnami.com/bitnami",
                ),
                values={
                    "image": {
                        "pullPolicy": "Always",
                    },
                    "nameOverride": "mlflow",
                    "architecture": "standalone",
                    "auth": {
                        "rootPassword": mysql_root_password,
                        "database": mysql_database,
                        "username": mysql_username,
                        "password": mysql_password,
                    },
                    "primary": {
                        "podSecurityContext": {
                            "fsGroup": gid,
                        },
                        "startupProbe": {"initialDelaySeconds": 90},
                        "containerSecurityContext": {
                            "runAsUser": uid,
                        },
                        "persistence": {
                            "existingClaim": mlflow_mysql_pvc.metadata.apply(
                                lambda v: v["name"]
                            ),
                        },
                    },
                    "secondary": {
                        "replicaCount": 0,
                    },
                },
            ),
        )

    if False:
        Chart(
            "mlflow",
            config=ChartOpts(
                chart="mlflow",
                version="1.5.1",
                fetch_opts=FetchOpts(
                    repo="https://cetic.github.io/helm-charts",
                ),
                values={
                    "image": {
                        "repository": "adacotechjp/mlflow",  # "ayadi05/mlflow",
                        "tag": "1.20.2",
                    },
                    "db": {
                        "default": {
                            "enabled": True,
                        },
                        "host": "mysql-mlflow",
                        "port": 3306,
                        "user": mysql_username,
                        "password": mysql_password,
                        "database": mysql_database,
                        "type": "mysql",
                    },
                    "minio": {
                        "url": "minio.default.svc.cluster.local:9000",
                        "accessKey": minio_access_key,
                        "secretKey": minio_secret_key,
                    },
                    # "ingress": {
                    #     "enabled": "true",
                    #     "hosts": [f"mlflow.{KUBE_NODE_HOST}"],
                    # },
                },
            ),
        )
    return
