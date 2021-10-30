from pulumi_kubernetes.apps.v1 import Deployment
from pulumi_kubernetes.core.v1 import Pod, Service, ServicePortArgs, ServiceSpecArgs
from pulumi_kubernetes.networking.v1 import (
    HTTPIngressPathArgs,
    HTTPIngressRuleValueArgs,
    Ingress,
    IngressBackendArgs,
    IngressRuleArgs,
    IngressSpecArgs,
)


def apple_service(hostname):
    Pod(
        "apple",
        metadata={"name": "apple-app", "labels": {"app": "apple"}},
        spec={
            "containers": [
                {
                    "name": "apple-app",
                    "image": "hashicorp/http-echo",
                    "args": ["-text=apple"],
                }
            ]
        },
    )

    apple_service = Service(
        "apple-service",
        metadata={"name": "apple-service"},
        spec=ServiceSpecArgs(
            ports=[
                ServicePortArgs(
                    port=80,
                    target_port=5678,
                )
            ],
            selector={
                "app": "apple",
            },
        ),
    )

    Ingress(
        "apple-ingress",
        metadata={
            "name": "apple-ingress",
            "annotations": {},
        },
        spec=IngressSpecArgs(
            rules=[
                IngressRuleArgs(
                    host=f"apple.{hostname}",
                    http=HTTPIngressRuleValueArgs(
                        paths=[
                            HTTPIngressPathArgs(
                                path="/",
                                backend=IngressBackendArgs(
                                    service_name=apple_service.metadata.apply(
                                        lambda v: v["name"]
                                    ),
                                    service_port=80,
                                ),
                            ),
                        ]
                    ),
                ),
            ],
        ),
    )
    return


def nginx_service(hostname):
    app_labels = {"app": "nginx"}
    Deployment(
        "nginx",
        metadata={"name": "nginx", "labels": app_labels},
        spec={
            "selector": {"match_labels": app_labels},
            "replicas": 1,
            "template": {
                "metadata": {"labels": app_labels, "name": "nginx"},
                "spec": {"containers": [{"name": "nginx", "image": "nginx"}]},
            },
        },
    )

    nginx_service = Service(
        "nginx-service",
        metadata={"name": "nginx-service"},
        spec=ServiceSpecArgs(
            ports=[ServicePortArgs(port=80, target_port=80)],
            selector={
                "app": "nginx",
            },
        ),
    )

    Ingress(
        "nginx-ingress",
        metadata={
            "name": "nginx-ingress",
            "annotations": {},
        },
        spec=IngressSpecArgs(
            rules=[
                IngressRuleArgs(
                    host=f"nginx.{hostname}",
                    http=HTTPIngressRuleValueArgs(
                        paths=[
                            HTTPIngressPathArgs(
                                path="/",
                                backend=IngressBackendArgs(
                                    service_name=nginx_service.metadata.apply(
                                        lambda v: v["name"]
                                    ),
                                    service_port=80,
                                ),
                            ),
                        ]
                    ),
                ),
            ],
        ),
    )
    return
