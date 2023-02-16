![k8s-eks-with-terraform](images/k8s-eks-with-terraform.png)

## How to provision EKS cluster with terraform


### Prerequisites: Terraform and existing AWS account


### create TF user in AWS account and save creds

```bash

# export AWS creds to envinronment
export AWS_ACCESS_KEY_ID="AWS_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="AWS_SECRET_ACCESS_KEY"
export AWS_DEFAULT_REGION="eu-west-1"
```

### Overview of 'terraform-aws-vpc' module

https://github.com/terraform-aws-modules/terraform-aws-vpc


```terraform
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"

  name                 = "k8s-${var.cluster_name}-vpc"
  cidr                 = "172.16.0.0/16"
  azs                  = data.aws_availability_zones.available.names
  private_subnets      = ["172.16.1.0/24", "172.16.2.0/24"]
  public_subnets       = ["172.16.3.0/24", "172.16.4.0/24"]
  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}
```

### Overview of 'terraform-aws-eks' module

https://github.com/terraform-aws-modules/terraform-aws-eks


```terraform
module "eks" {
  source  = "terraform-aws-modules/eks/aws"

  cluster_name    = "k8s-guides-eks"
  cluster_version = "1.24"
  subnets         = module.vpc.private_subnets

  vpc_id = module.vpc.vpc_id
  write_kubeconfig   = true

  worker_groups = [
    {
        name = "ng-medium"
        instance_type = "t3.medium"
        asg_desired_capacity = 1
        tags = [{
          key                 = "instance-type"
          value               = "on-demand-medium"
          propagate_at_launch = true
        }, {
          key                 = "os-type"
          value               = "linux"
          propagate_at_launch = true
        }]
    },
  ]
}
```


### Create EKS with Terraform

```bash
terraform init

terraform plan

terraform apply
```

### How to interact with your cluster?

```bash
aws eks update-kubeconfig --name k8s-guides
```

### Validate everything works by deploying nginx

```
kubectl run nginx-test --image=nginx 
```