# Zero Trust AWS Microservices Security Architecture

## 1. Project Overview

This project demonstrates a **Zero Trust security architecture for containerized microservices on AWS**.

The architecture uses Amazon ECS with AWS Fargate, Amazon RDS, Amazon ECR, Amazon VPC, IAM, VPC endpoints, CloudWatch Logs, and AWS Reachability Analyzer.

The main security principle is:

> **Never trust a service simply because it is inside the VPC. Access must be explicitly allowed and restricted.**

The project contains two backend services:

* **Service A** — application/service entry point
* **Service B** — internal service
* **Amazon RDS MySQL** — private database

The services communicate through private networking, with security groups restricting communication to only the required ports.

---

## 2. Architecture

```text
                         AWS VPC
                       10.0.0.0/16
                            │
                 ┌──────────┴──────────┐
                 │                     │
          Private Subnet A       Private Subnet B
                 │                     │
          ┌──────▼──────┐       ┌──────▼──────┐
          │  Service A  │──────►│  Service B  │
          │ ECS Fargate │ 8081  │ ECS Fargate │
          └─────────────┘       └──────┬──────┘
                                       │
                                       │ 3306
                                       ▼
                                ┌─────────────┐
                                │    RDS      │
                                │    MySQL    │
                                └─────────────┘

              Private AWS Service Connectivity
                       │
       ┌───────────────┼────────────────┐
       │               │                │
      ECR          S3 Gateway     CloudWatch Logs
     Endpoint       Endpoint         Endpoint
```

The ECS services do not use public IP addresses.

---

## 3. AWS Components

### Amazon VPC

A dedicated VPC provides isolated network infrastructure for the application.

The workload is deployed into private subnets rather than directly exposing the containers to the public Internet.

### Amazon ECS / AWS Fargate

Both microservices run as ECS Fargate tasks.

* Service A: `zt-service-a`
* Service B: `zt-service-b`

Fargate provides serverless container execution without requiring EC2 instance management.

### Amazon ECR

Container images are stored in Amazon ECR.

The ECS tasks pull their images through private VPC connectivity rather than requiring public Internet access.

### Amazon RDS

The application database is an Amazon RDS MySQL instance.

Database access is restricted through security groups and uses TCP port **3306**.

### VPC Endpoints

Private connectivity is configured for AWS services required by the workloads.

Configured endpoints include:

* Amazon ECR API
* Amazon ECR Docker Registry
* Amazon S3 Gateway Endpoint
* CloudWatch Logs

This allows private workloads to communicate with AWS services without requiring public IP addresses.

---

## 4. Zero Trust Security Model

The project applies Zero Trust principles at the service level.

### Explicit authorization

Service A is allowed to communicate with Service B only through the required application port:

```text
Service A → Service B
TCP 8081
```

Service B does not expose unnecessary inbound application ports.

### Database isolation

Database communication uses:

```text
ECS workload → RDS
TCP 3306
```

The database is not publicly exposed.

### Least privilege

ECS tasks use dedicated IAM task roles rather than relying on broad permissions.

AWS permissions are assigned to the workload that needs them.

### Private networking

The ECS services have no public IP addresses.

Communication with AWS services uses VPC endpoints where required.

### Continuous verification

AWS Reachability Analyzer was used to verify whether specific network paths were reachable.

This provides evidence that permitted communication works while restricted communication is blocked.

---

## 5. Security Groups

Security groups provide service-level network restrictions.

### Service A

Service A permits only the traffic required for the application architecture.

### Service B

Service B permits Service A to reach its application on:

```text
TCP 8081
```

The source is the Service A security group rather than an unrestricted CIDR range.

### VPC Endpoint Security Group

The VPC endpoint security group permits HTTPS traffic:

```text
TCP 443
```

from the authorized ECS service security groups.

This allows the workloads to reach AWS services through private interface endpoints.

---

## 6. Network Security Testing

AWS Reachability Analyzer was used to test important communication paths.

### Test 1 — Service A → Service B

```text
Destination: 10.0.146.232
Port: 8081
Protocol: TCP

Result: Reachable
```

This confirms that Service A can communicate with Service B through the explicitly permitted application port.

### Test 2 — ECS → RDS

```text
Destination: 10.0.132.78
Port: 3306
Protocol: TCP

Result: Reachable
```

This confirms that the application can reach the private database.

### Test 3 — Restricted path

A deliberately restricted network path was analyzed.

```text
Result: Not reachable
```

This demonstrates that the security controls are actively preventing unauthorized network communication.

---

## 7. Container Security and Identity

Each ECS service uses an IAM task role.

This allows AWS API access to be associated with the individual workload.

The architecture therefore avoids treating all workloads inside the VPC as automatically trusted.

The task execution role is used for ECS infrastructure operations such as pulling container images and sending logs.

The distinction between:

* **Task role**
* **Task execution role**

helps maintain separation of application permissions and ECS infrastructure permissions.

---

## 8. Logging and Monitoring

Service B is configured to send container logs to Amazon CloudWatch Logs.

Log group:

```text
/ecs/zt-service-b
```

Log stream prefix:

```text
service-b
```

CloudWatch Logs provides centralized visibility into application activity and supports security monitoring and troubleshooting.

---

## 9. Failure Encountered During Deployment

During deployment, Service B initially failed when CloudWatch logging was enabled.

The error indicated that the task could not reach CloudWatch Logs from the private subnet.

The problem was resolved by creating a private VPC interface endpoint for:

```text
com.amazonaws.us-east-1.logs
```

After the endpoint was created, Service B was redeployed successfully and CloudWatch Logs began receiving container logs.

This demonstrates an important property of private AWS architectures: **removing Internet access requires private connectivity to every AWS service the workload depends on.**

---

## 10. Security Principles Demonstrated

This project demonstrates the following Zero Trust principles:

| Principle                      | Implementation                                         |
| ------------------------------ | ------------------------------------------------------ |
| Never trust, always verify     | Explicit security-group and network-path authorization |
| Least privilege                | Dedicated IAM task roles                               |
| Micro-segmentation             | Separate security controls for Service A and Service B |
| Private access                 | ECS workloads deployed without public IPs              |
| Explicit service authorization | Service A → Service B only on TCP 8081                 |
| Database isolation             | RDS access restricted to TCP 3306                      |
| Secure AWS service access      | VPC endpoints                                          |
| Continuous visibility          | CloudWatch Logs                                        |
| Security validation            | Reachability Analyzer                                  |

---

## 11. Evidence Collected

The project includes evidence showing:

* ECS Service A and Service B running
* Successful Service B deployment
* CloudWatch container logs
* Security-group restrictions
* Available VPC endpoints
* Reachability Analyzer results
* Successful application-to-database connectivity
* Blocked unauthorized network connectivity

---

## 12. Conclusion

The final architecture demonstrates how a small microservice application can be deployed using Zero Trust principles on AWS.

Instead of trusting resources based only on their location inside a VPC, access is explicitly controlled through:

* IAM
* Security groups
* Private subnets
* VPC endpoints
* Restricted service-to-service communication
* Database isolation
* Centralized logging
* Network reachability analysis

The project therefore focuses not simply on running containers, but on demonstrating **why each workload is allowed to communicate with another resource and why unauthorized communication is blocked**.

## Technologies Used

* AWS VPC
* Amazon ECS
* AWS Fargate
* Amazon ECR
* Amazon RDS MySQL
* AWS IAM
* VPC Endpoints
* Amazon CloudWatch Logs
* AWS Reachability Analyzer
* Docker
