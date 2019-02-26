import logging
import os
import time
from typing import NamedTuple

import boto3
from botocore.exceptions import ClientError


log = logging.getLogger()
log.setLevel(os.getenv("LOG_LEVEL", logging.INFO))


class DNSRegistrator(object):
    def __init__(self, task_arn: str, cluster_arn: str, task_definition_arn):
        self.task_arn = task_arn
        self.task_id = task_arn.split("/")[-1]
        self.cluster_arn = cluster_arn
        self.task_definition_arn = task_definition_arn
        self.task = {}
        self.task_definition = {}
        self.network_interfaces = []
        self.dns_entries = []
        self.dns_entry: DNSEntry = None
        self.ecs = boto3.client("ecs")
        self.ec2 = boto3.client("ec2")
        self.route53 = boto3.client("route53")

    def get_network_interfaces(self):
        attachments = list(
            filter(
                lambda a: a["type"] == "ElasticNetworkInterface"
                and a["status"] == "ATTACHED",
                self.task.get("attachments"),
            )
        )
        self.network_interfaces = []
        for attachment in attachments:
            attachment = attachments[0]
            eni_id = next(map(lambda d: d["value"], filter(lambda d: d['name'] == 'networkInterfaceId', attachment["details"])), 'none')
            try:
                response = self.ec2.describe_network_interfaces(NetworkInterfaceIds=[eni_id])
                self.network_interfaces.append(response["NetworkInterfaces"][0])
            except ClientError as e:
                if e.response['Error']['Code'] != 'InvalidNetworkInterfaceID.NotFound':
                    raise
                else:
                    log.info(
                        'ignoring network interface %s', eni_id
                    )

    def get_ip_addresses(self, public_ip):
        result = []
        for network_interface in self.network_interfaces:
            if public_ip:
                result.append(network_interface.get("Association").get("PublicIp"))
            else:
                result.append(network_interface.get("PrivateIpAddress"))
        return result

    def get_task_definition(self):
        try:
            response = self.ecs.describe_task_definition(
                taskDefinition=self.task_definition_arn
            )
            self.task_definition = response["taskDefinition"]
            self.get_dns_entries()
        except ClientError as e:
            log.error(
                'no task definition found with id "%s, %s', self.task_definition_arn, e
            )
            self.task_definition = {}

    def get_task(self):
        try:
            response = self.ecs.describe_tasks(
                cluster=self.cluster_arn, tasks=[self.task_arn]
            )
            self.task = response["tasks"][0]
        except ClientError as e:
            log.error(
                'no task found with id "%s" on cluster "%s", %s',
                self.task_arn,
                self.cluster_arn,
                e,
            )
            self.task = {}

    def get_dns_entries(self):
        self.dns_entries = []
        for c in self.task_definition.get("containerDefinitions", {}):
            labels = c.get("dockerLabels")
            hosted_zone_id = labels.get("DNSHostedZoneId")
            dns_name = labels.get("DNSName")
            public_ip = "true" == labels.get("DNSRegisterPublicIp", "true")
            if not hosted_zone_id:
                continue
            if not dns_name:
                log.error(
                    'task "%s" tagged with "DNSHostedZonedId", but no label "DNSName"',
                    self.task_arn,
                )
                continue

            self.dns_entries.append(
                DNSEntry(hosted_zone_id, '{}.'.format(dns_name.rstrip('.')), public_ip)
            )

        self.dns_entry = self.dns_entries[0] if self.dns_entries else None

    def register_dns_entry(self, ip_address):
        log.info('registering "%s" for task "%s"', self.dns_entry.name, self.task_arn)
        response = self.route53.change_resource_record_sets(
            HostedZoneId=self.dns_entry.hosted_zone_id,
            ChangeBatch={
                "Comment": "registration of {by ecs-dns-registrator",
                "Changes": [
                    {
                        "Action": "UPSERT",
                        "ResourceRecordSet": {
                            "Name": self.dns_entry.name,
                            "Type": "A",
                            "SetIdentifier": self.task_id,
                            "Weight": 100,
                            "TTL": 30,
                            "ResourceRecords": [{"Value": ip_address}],
                        },
                    }
                ],
            },
        )
        wait_for_route53_change_completion(self.route53, response)

    def get_resource_record_set(self):
        for page in self.route53.get_paginator('list_resource_record_sets').paginate(
            HostedZoneId=self.dns_entry.hosted_zone_id,
            StartRecordType='A',
            StartRecordName=self.dns_entry.name
        ):
            for rr_set in page['ResourceRecordSets']:
                if rr_set['Name'] == self.dns_entry.name and rr_set.get('SetIdentifier') == self.task_id:
                    return rr_set
        return None


    def deregister_dns_entry(self):
        log.info('deregistering "%s" for task "%s"', self.dns_entry.name, self.task_id)
        rr_set = self.get_resource_record_set()
        if rr_set:
            response = self.route53.change_resource_record_sets(
                HostedZoneId=self.dns_entry.hosted_zone_id,
                ChangeBatch={
                    "Comment": "deregistration by ecs-dns-registrator",
                    "Changes": [
                        {
                            "Action": "DELETE",
                            "ResourceRecordSet": self.get_resource_record_set()
                        }
                    ],
                },
            )
            wait_for_route53_change_completion(self.route53, response)

        log.info('DNS record name "%s" for set identifier "%s" deregistered', self.dns_entry.name, self.task_id)

    def handle(self, desired_state, last_state):
        self.get_task_definition()
        if not self.dns_entry:
            # skip task definitions without proper labels.
            return

        self.get_task()
        if not self.task:
            log.error('task "%s" was not found', self.task_arn)
            return

        if desired_state == "RUNNING" and last_state == "RUNNING":
            self.get_network_interfaces()
            ip_addresses = self.get_ip_addresses(self.dns_entry.register_public_ip)
            if ip_addresses:
                self.register_dns_entry(ip_addresses[0])
            else:
                log.error('no ip address was found to register task %s', self.task_arn)
        elif desired_state == "STOPPED":
            self.deregister_dns_entry()


def wait_for_route53_change_completion(route53: object, change: dict):
    id = change['ChangeInfo']['Id'].split('/')[-1]
    while change['ChangeInfo']['Status'] != 'INSYNC':
        log.info(f'waiting for change {id} to complete')
        time.sleep(5)
        change = route53.get_change(Id=id)

class DNSEntry(NamedTuple):
    hosted_zone_id: str
    name: str
    register_public_ip: bool


def handler(event, context):
    if event.get("detail-type") != "ECS Task State Change":
        log.error("unsupported event, %", event.get("detail-type"))
        return

    task_arn = event["detail"]["taskArn"]
    task_definition_arn = event["detail"]["taskDefinitionArn"]
    cluster_arn = event["detail"]["clusterArn"]
    desired_state = event["detail"]["desiredStatus"]
    last_state = event["detail"]["lastStatus"]

    registrator = DNSRegistrator(task_arn, cluster_arn, task_definition_arn)
    registrator.handle(desired_state, last_state)



