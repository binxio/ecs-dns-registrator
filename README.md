# ecs-dns-registrator

An ECS task DNS registrator.

## Installation
To install these custom resources, type:

```sh
aws cloudformation create-stack \
       --capabilities CAPABILITY_IAM \
       --stack-name ecs-dns-registrator \
       --template-body file://cloudformation/template.yaml

aws cloudformation wait stack-create-complete  --stack-name ecs-dns-registrator
```
This CloudFormation template will use our pre-packaged provider from `s3://binxio-public-${AWS_REGION}/lambdas/ecs-dns-registrator-0.1.1.zip`.

or use [![](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=eu-central-1#/stacks/new?stackName=ecs-dns-registrator&templateURL=https://s3.amazonaws.com/binxio-public-eu-central-1/lambdas/ecs-dns-registrator-0.1.1.yaml)

## Demo
To install the simple sample, type:

```sh
aws cloudformation create-stack --stack-name ecs-dns-registrator-demo \
       --template-body file://cloudformation/demo-stack.yaml
aws cloudformation wait stack-create-complete  --stack-name ecs-dns-registrator-demo
```
