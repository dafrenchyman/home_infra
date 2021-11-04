from common.helpers import create_pvc
from pulumi_kubernetes.core.v1 import Namespace
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts


def prometheus(
    config_folder_root: str, hostname: str, grafana_password: str, uid=1000, gid=1000
):
    Namespace(
        "monitor",
        metadata={
            "name": "monitor",
        },
    )

    Chart(
        "kube-state-metrics",
        config=ChartOpts(
            namespace="monitor",
            chart="kube-state-metrics",
            version="4.0.0",
            fetch_opts=FetchOpts(
                repo="https://prometheus-community.github.io/helm-charts/",
            ),
            values={
                "securityContext": {
                    "enabled": True,
                    "runAsGroup": gid,
                    "runAsUser": uid,
                    "fsGroup": gid,
                },
                "selfMonitor": {"enabled": True},
            },
        ),
    )

    Chart(
        "prometheus",
        config=ChartOpts(
            namespace="monitor",
            chart="prometheus",
            version="14.11.0",
            fetch_opts=FetchOpts(
                repo="https://prometheus-community.github.io/helm-charts/",
            ),
            values={
                "alertmanager": {"enabled": False},
                "kubeStateMetrics": {"enabled": False},
                "nodeExporter": {"enabled": False},
                "pushgateway": {"enabled": False},
                "server": {
                    "global": {"scrape_interval": "30s"},
                    "ingress": {"enabled": True, "hosts": [f"prometheus.{hostname}"]},
                },
                "serverFiles": {
                    "prometheus.yml": {
                        "scrape_configs": [
                            {
                                "job_name": "kubernetes-pods",
                                "kubernetes_sd_configs": [{"role": "pod"}],
                                "relabel_configs": [
                                    {
                                        "source_labels": [
                                            "__meta_kubernetes_pod_annotation_prometheus_io_scrape"
                                        ],
                                        "action": "keep",
                                        "regex": True,
                                    },
                                    {
                                        "source_labels": [
                                            "__meta_kubernetes_pod_annotation_prometheus_io_path"
                                        ],
                                        "action": "replace",
                                        "target_label": "__metrics_path__",
                                        "regex": "(.+)",
                                    },
                                    {
                                        "source_labels": [
                                            "__address__",
                                            "__meta_kubernetes_pod_annotation_prometheus_io_port",
                                        ],
                                        "action": "replace",
                                        "regex": "([^:]+)(?::\\d+)?;(\\d+)",
                                        "replacement": "$1:$2",
                                        "target_label": "__address__",
                                    },
                                    {
                                        "action": "labelmap",
                                        "regex": "__meta_kubernetes_pod_label_(.+)",
                                    },
                                    {
                                        "source_labels": [
                                            "__meta_kubernetes_namespace"
                                        ],
                                        "action": "replace",
                                        "target_label": "kubernetes_namespace",
                                    },
                                    {
                                        "source_labels": ["__meta_kubernetes_pod_name"],
                                        "action": "replace",
                                        "target_label": "kubernetes_pod_name",
                                    },
                                ],
                            },
                            {
                                "job_name": "kubernetes-service-endpoints",
                                "kubernetes_sd_configs": [{"role": "endpoints"}],
                                "relabel_configs": [
                                    {
                                        "source_labels": [
                                            "__meta_kubernetes_service_annotation_prometheus_io_scrape"
                                        ],
                                        "action": "keep",
                                        "regex": True,
                                    },
                                    {
                                        "source_labels": [
                                            "__meta_kubernetes_service_annotation_prometheus_io_scheme"
                                        ],
                                        "action": "replace",
                                        "target_label": "__scheme__",
                                        "regex": "(https?)",
                                    },
                                    {
                                        "source_labels": [
                                            "__meta_kubernetes_service_annotation_prometheus_io_path"
                                        ],
                                        "action": "replace",
                                        "target_label": "__metrics_path__",
                                        "regex": "(.+)",
                                    },
                                    {
                                        "source_labels": [
                                            "__address__",
                                            "__meta_kubernetes_service_annotation_prometheus_io_port",
                                        ],
                                        "action": "replace",
                                        "target_label": "__address__",
                                        "regex": "([^:]+)(?::\\d+)?;(\\d+)",
                                        "replacement": "$1:$2",
                                    },
                                    {
                                        "action": "labelmap",
                                        "regex": "__meta_kubernetes_service_label_(.+)",
                                    },
                                    {
                                        "source_labels": [
                                            "__meta_kubernetes_namespace"
                                        ],
                                        "action": "replace",
                                        "target_label": "kubernetes_namespace",
                                    },
                                    {
                                        "source_labels": [
                                            "__meta_kubernetes_service_name"
                                        ],
                                        "action": "replace",
                                        "target_label": "kubernetes_name",
                                    },
                                ],
                            },
                        ]
                    }
                },
            },
        ),
    )

    if True:
        _, grafana_pvc, _ = create_pvc(
            name="grafana-config",
            path=f"{config_folder_root}/grafana",
            size="3Gi",
            access_mode="ReadWriteOnce",
            mount_path="/config",
            namespace="monitor",
        )

        Chart(
            "grafana",
            config=ChartOpts(
                namespace="monitor",
                chart="grafana",
                version="6.17.4",
                fetch_opts=FetchOpts(
                    repo="https://grafana.github.io/helm-charts",
                ),
                values={
                    "adminUser": "admin",
                    "adminPassword": grafana_password,
                    "ingress": {
                        "enabled": True,
                        "hosts": [f"grafana.{hostname}"],
                    },
                    "persistence": {
                        "enabled": True,
                        "type": "pvc",
                        "existingClaim": grafana_pvc.metadata.apply(
                            lambda v: v["name"]
                        ),
                    },
                    "securityContext": {
                        "enabled": True,
                        "runAsUser": int(uid),
                        "runAsGroup": int(gid),
                        "fsGroup": int(gid),
                    },
                },
            ),
        )
    return
