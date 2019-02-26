from uuid import uuid4

import boto3
import pytest

from task_event import DNSEntry, DNSRegistrator, wait_for_route53_change_completion

__data = {
    "task_definition": {
        "taskDefinitionArn": "arn:aws:ecs:eu-central-1:1234567890:task-definition/paas-monitor:25",
        "containerDefinitions": [
            {
                "name": "paas-monitor",
                "image": "mvanholsteijn/paas-monitor:latest",
                "cpu": 0,
                "links": [],
                "portMappings": [
                    {"containerPort": 1337, "hostPort": 1337, "protocol": "tcp"}
                ],
                "essential": True,
                "entryPoint": [],
                "command": [],
                "environment": [],
                "mountPoints": [],
                "volumesFrom": [],
                "dnsServers": [],
                "dnsSearchDomains": [],
                "extraHosts": [],
                "dockerSecurityOptions": [],
                "dockerLabels": {
                    "DNSHostedZoneId": "Z3AUN8X7OGVNVQ",
                    "DNSName": "paas-monitor.fargate.example",
                    "DNSUsePublicIP": "true",
                },
                "ulimits": [],
            }
        ],
        "family": "paas-monitor",
        "executionRoleArn": "arn:aws:iam::1234567890:role/fargate-dns-registrator-demo-TaskRole-SBM8JCAIATFH",
        "networkMode": "awsvpc",
        "revision": 25,
        "volumes": [],
        "status": "ACTIVE",
        "requiresAttributes": [
            {"name": "com.amazonaws.ecs.capability.docker-remote-api.1.17"},
            {"name": "com.amazonaws.ecs.capability.docker-remote-api.1.18"},
            {"name": "ecs.capability.task-eni"},
        ],
        "placementConstraints": [],
        "compatibilities": ["EC2", "FARGATE"],
        "requiresCompatibilities": ["FARGATE"],
        "cpu": "256",
        "memory": "512",
    },
    "network_interfaces": [
        {
            "Association": {
                "AllocationId": "eipalloc-36462a18",
                "AssociationId": "eipassoc-138bfe3d",
                "IpOwnerId": "1234567890",
                "PublicDnsName": "ec2-18-194-71-107.eu-central-1.compute.amazonaws.com",
                "PublicIp": "18.194.71.107",
            },
            "Attachment": {
                "AttachmentId": "ela-attach-38862c51",
                "DeleteOnTermination": False,
                "DeviceIndex": 1,
                "InstanceOwnerId": "amazon-aws",
                "Status": "attached",
            },
            "AvailabilityZone": "eu-central-1b",
            "Description": "Interface for NAT Gateway nat-02d216882c09db8e6",
            "Groups": [],
            "InterfaceType": "nat_gateway",
            "Ipv6Addresses": [],
            "MacAddress": "06:12:a0:4f:bd:82",
            "NetworkInterfaceId": "eni-d56720fd",
            "OwnerId": "1234567890",
            "PrivateDnsName": "ip-172-31-25-220.eu-central-1.compute.internal",
            "PrivateIpAddress": "172.31.25.220",
            "PrivateIpAddresses": [
                {
                    "Association": {
                        "AllocationId": "eipalloc-36462a18",
                        "AssociationId": "eipassoc-138bfe3d",
                        "IpOwnerId": "1234567890",
                        "PublicDnsName": "ec2-18-194-71-107.eu-central-1.compute.amazonaws.com",
                        "PublicIp": "18.194.71.107",
                    },
                    "Primary": True,
                    "PrivateDnsName": "ip-172-31-25-220.eu-central-1.compute.internal",
                    "PrivateIpAddress": "172.31.25.220",
                }
            ],
            "RequesterId": "128792236543",
            "RequesterManaged": True,
            "SourceDestCheck": False,
            "Status": "in-use",
            "SubnetId": "subnet-9f0e04e4",
            "TagSet": [],
            "VpcId": "vpc-2ed2df47",
        },
        {
            "Association": {
                "IpOwnerId": "amazon",
                "PublicDnsName": "ec2-18-184-214-52.eu-central-1.compute.amazonaws.com",
                "PublicIp": "18.184.214.52",
            },
            "Attachment": {
                "AttachTime": "2019-02-25T19:15:41.000Z",
                "AttachmentId": "eni-attach-0dec5ba850b1f7693",
                "DeleteOnTermination": False,
                "DeviceIndex": 1,
                "InstanceOwnerId": "843547988961",
                "Status": "attached",
            },
            "AvailabilityZone": "eu-central-1c",
            "Description": "arn:aws:ecs:eu-central-1:1234567890:attachment/f6d9fc22-dbaf-4bff-b501-a41b41f27826",
            "Groups": [
                {
                    "GroupName": "cfn-fargate-dns-registrator-demo-SecurityGroup-1RMI6SSPRH54F",
                    "GroupId": "sg-0a5b136c2e7b29b0a",
                }
            ],
            "InterfaceType": "interface",
            "Ipv6Addresses": [],
            "MacAddress": "0a:63:44:b6:55:1a",
            "NetworkInterfaceId": "eni-1f9ed840",
            "OwnerId": "1234567890",
            "PrivateDnsName": "ip-172-31-89-154.eu-central-1.compute.internal",
            "PrivateIpAddress": "172.31.89.154",
            "PrivateIpAddresses": [
                {
                    "Association": {
                        "IpOwnerId": "amazon",
                        "PublicDnsName": "ec2-18-184-214-52.eu-central-1.compute.amazonaws.com",
                        "PublicIp": "18.184.214.52",
                    },
                    "Primary": True,
                    "PrivateDnsName": "ip-172-31-89-154.eu-central-1.compute.internal",
                    "PrivateIpAddress": "172.31.89.154",
                }
            ],
            "RequesterId": "628676013162",
            "RequesterManaged": True,
            "SourceDestCheck": True,
            "Status": "in-use",
            "SubnetId": "subnet-008b704d",
            "TagSet": [],
            "VpcId": "vpc-2ed2df47",
        },
    ],
    "task": {
        "taskArn": "arn:aws:ecs:eu-central-1:1234567890:task/5568b6f6-78ec-43b2-8c05-be3bc117c96e",
        "clusterArn": "arn:aws:ecs:eu-central-1:1234567890:cluster/fargate-dns-registrator-demo-Cluster-N7RLZ81CJ1RJ",
        "taskDefinitionArn": "arn:aws:ecs:eu-central-1:1234567890:task-definition/paas-monitor:25",
        "overrides": {"containerOverrides": [{"name": "paas-monitor"}]},
        "lastStatus": "RUNNING",
        "desiredStatus": "RUNNING",
        "cpu": "256",
        "memory": "512",
        "containers": [
            {
                "containerArn": "arn:aws:ecs:eu-central-1:1234567890:container/fa9ffe57-ad06-4488-8917-05e39bc73aec",
                "taskArn": "arn:aws:ecs:eu-central-1:1234567890:task/5568b6f6-78ec-43b2-8c05-be3bc117c96e",
                "name": "paas-monitor",
                "lastStatus": "RUNNING",
                "networkBindings": [],
                "networkInterfaces": [
                    {
                        "attachmentId": "5a6df8af-ca05-4601-a3eb-d16fc842f27f",
                        "privateIpv4Address": "172.31.93.207",
                    }
                ],
                "healthStatus": "UNKNOWN",
            }
        ],
        "startedBy": "ecs-svc/9223370485734112013",
        "version": 3,
        "connectivity": "CONNECTED",
        "connectivityAt": 1551120672.256,
        "pullStartedAt": 1551120683.202,
        "pullStoppedAt": 1551120686.202,
        "createdAt": 1551120668.353,
        "startedAt": 1551120687.202,
        "group": "service:paas-monitor",
        "launchType": "FARGATE",
        "platformVersion": "1.3.0",
        "attachments": [
            {
                "id": "5a6df8af-ca05-4601-a3eb-d16fc842f27f",
                "type": "ElasticNetworkInterface",
                "status": "ATTACHED",
                "details": [
                    {"name": "subnetId", "value": "subnet-008b704d"},
                    {"name": "networkInterfaceId", "value": "eni-9890d6c7"},
                    {"name": "macAddress", "value": "0a:83:d9:e7:00:54"},
                    {"name": "privateIPv4Address", "value": "172.31.93.207"},
                ],
            }
        ],
        "healthStatus": "UNKNOWN",
        "tags": [],
    },
}


@pytest.fixture
def hosted_zone():
    route53 = boto3.client("route53")
    response = route53.create_hosted_zone(
        Name="fargate.example.", CallerReference=str(uuid4())
    )
    id = response["HostedZone"]["Id"]
    wait_for_route53_change_completion(route53, response)
    yield id
    for page in route53.get_paginator("list_resource_record_sets").paginate(
        HostedZoneId=id
    ):
        rr_sets = list(filter(
            lambda r: not (
                (r["Type"] == "SOA" or r["Type"] == "NS")
                and r["Name"] == "fargate.example."
            ),
            page["ResourceRecordSets"],
        ))

        if rr_sets:
            response = route53.change_resource_record_sets(
                HostedZoneId=id,
                ChangeBatch={
                    "Changes": [
                        {"Action": "DELETE", "ResourceRecordSet": rr_set}
                        for rr_set in rr_sets
                    ]
                },
            )
            wait_for_route53_change_completion(route53, response)
    response = route53.delete_hosted_zone(Id=id)
    wait_for_route53_change_completion(route53, response)


def test_get_ip_addresses():
    registrator = DNSRegistrator("task-arn", "cluster-arn", "task-definition-arn")
    registrator.network_interfaces = __data["network_interfaces"].copy()

    ip_addresses = registrator.get_ip_addresses(True)
    assert ["18.194.71.107", "18.184.214.52"] == ip_addresses

    ip_addresses = registrator.get_ip_addresses(False)
    assert ["172.31.25.220", "172.31.89.154"] == ip_addresses


def test_get_network_interface():
    registrator = DNSRegistrator(
        __data["task"]["taskArn"],
        __data["task"]["clusterArn"],
        __data["task"]["taskDefinitionArn"],
    )
    registrator.task = __data["task"].copy()
    registrator.get_network_interfaces()


def test_get_task_id():
    registrator = DNSRegistrator(
        __data["task"]["taskArn"],
        __data["task"]["clusterArn"],
        __data["task"]["taskDefinitionArn"],
    )
    assert "5568b6f6-78ec-43b2-8c05-be3bc117c96e" == registrator.task_id

    registrator = DNSRegistrator(
        __data["task"]["taskArn"] + "/5568b6f678ec43b28c05be3bc117c96e",
        __data["task"]["clusterArn"],
        __data["task"]["taskDefinitionArn"],
    )
    assert "5568b6f678ec43b28c05be3bc117c96e" == registrator.task_id


def test_get_dns_entries():
    registrator = DNSRegistrator(
        __data["task"]["taskArn"],
        __data["task"]["clusterArn"],
        __data["task"]["taskDefinitionArn"],
    )
    registrator.task_definition = __data["task_definition"].copy()

    registrator.get_dns_entries()
    assert registrator.dns_entries
    assert registrator.dns_entry.hosted_zone_id == "Z3AUN8X7OGVNVQ"
    assert registrator.dns_entry.name == "paas-monitor.fargate.example."
    assert registrator.dns_entry.register_public_ip == True


def test_get_task():
    registrator = DNSRegistrator(
        __data["task"]["taskArn"],
        __data["task"]["clusterArn"],
        __data["task"]["taskDefinitionArn"],
    )

    # will not find the specified task
    registrator.get_task()
    assert {} == registrator.task


def test_get_task_definition():
    registrator = DNSRegistrator(
        __data["task"]["taskArn"],
        __data["task"]["clusterArn"],
        __data["task"]["taskDefinitionArn"],
    )

    # will not find the specified task
    registrator.get_task_definition()
    assert {} == registrator.task


def test_register_dns_entry(hosted_zone):
    registrator = DNSRegistrator(
        __data["task"]["taskArn"],
        __data["task"]["clusterArn"],
        __data["task"]["taskDefinitionArn"],
    )

    registrator.task = __data["task"].copy()
    registrator.task_definition = __data["task_definition"].copy()
    registrator.get_dns_entries()
    registrator.dns_entry = DNSEntry(hosted_zone, registrator.dns_entry.name, True)
    registrator.register_dns_entry("1.1.1.1")
    rr_set = registrator.get_resource_record_set()
    assert rr_set is not None
    registrator.deregister_dns_entry()
