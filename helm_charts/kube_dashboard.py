from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts


def kube_dashboard(hostname: str):
    Chart(
        "kubernetes-dashboard",
        config=ChartOpts(
            chart="kubernetes-dashboard",
            version="5.0.0",
            fetch_opts=FetchOpts(
                repo="https://kubernetes.github.io/dashboard/",
            ),
            values={"ingress": {"enabled": "true", "hosts": [f"kube-dash.{hostname}"]}},
        ),
    )
    return
