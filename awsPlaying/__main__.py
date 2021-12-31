"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws


# Create a test server behind a jump host that you can then connect to via pycharm
def main():
    config = pulumi.Config()
    ssh_key = config.require("sshPublicKey")

    vpc = pulumi_aws.ec2.Vpc(
        "ec2-vpc", cidr_block="10.0.0.0/16", tags={"Name": "Default VPC"}
    )

    key = pulumi_aws.ec2.KeyPair("key", public_key=ssh_key, key_name="mrsharky")

    public_subnet = pulumi_aws.ec2.Subnet(
        "ec2-public-subnet",
        cidr_block="10.0.101.0/24",
        tags={"Name": "ec2-public"},
        vpc_id=vpc.id,
    )

    security_group_jump_host = pulumi_aws.ec2.SecurityGroup(
        "ec2-jump-host-ssh-sg",
        description="Allow SSH traffic to jump-host",
        ingress=[
            {
                "protocol": "tcp",
                "from_port": 22,
                "to_port": 22,
                "cidr_blocks": ["0.0.0.0/0"],
            }
        ],
        egress=[
            {
                "protocol": "-1",
                "from_port": 0,
                "to_port": 0,
                "cidr_blocks": ["0.0.0.0/0"],
            }
        ],
        vpc_id=vpc.id,
    )

    security_group_server = pulumi_aws.ec2.SecurityGroup(
        "ec2-server-ssh-sg",
        description="Allow SSH traffic to server",
        ingress=[
            {
                "protocol": "tcp",
                "from_port": 22,
                "to_port": 22,
                "cidr_blocks": [public_subnet.cidr_block],
            }
        ],
        egress=[
            {
                "protocol": "-1",
                "from_port": 0,
                "to_port": 0,
                "cidr_blocks": ["0.0.0.0/0"],
            }
        ],
        vpc_id=vpc.id,
    )

    igw = pulumi_aws.ec2.InternetGateway(
        "ec2-igw",
        vpc_id=vpc.id,
    )

    route_table_jump_host = pulumi_aws.ec2.RouteTable(
        "ec2-route-table",
        vpc_id=vpc.id,
        routes=[{"cidr_block": "0.0.0.0/0", "gateway_id": igw.id}],
    )

    _ = pulumi_aws.ec2.RouteTableAssociation(
        "ec2-rta", route_table_id=route_table_jump_host.id, subnet_id=public_subnet.id
    )

    ami_aws_instance = pulumi_aws.ec2.get_ami(
        most_recent="true",
        owners=["amazon"],
        filters=[{"name": "name", "values": ["amzn-ami-hvm-*"]}],
    )

    ec2_jump_host_instance = pulumi_aws.ec2.Instance(
        "ec2-jump-host",
        instance_type="t2.micro",
        vpc_security_group_ids=[security_group_jump_host.id],
        ami=ami_aws_instance.id,
        subnet_id=public_subnet.id,
        associate_public_ip_address=True,
        key_name=key.key_name,
    )

    ec2_server_instance = pulumi_aws.ec2.Instance(
        "ec2-server",
        instance_type="t2.micro",
        vpc_security_group_ids=[security_group_server.id],
        ami="ami-0892d3c7ee96c0bf7",  # Ubuntu Server 20.04 LTS
        subnet_id=public_subnet.id,
        associate_public_ip_address=False,
        key_name=key.key_name,
    )

    pulumi.export("ec2-jump-host-ip", ec2_jump_host_instance.public_ip)
    pulumi.export("ec2-server-host-private-ip", ec2_server_instance.private_ip)


if __name__ == "__main__":
    main()
