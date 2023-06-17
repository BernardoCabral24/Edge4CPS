# Edge4CPS
In this repository Edge4CPS System Components are stored

# Abstract
Cyber-Physical Systems (CPS) play a vital role in the operation of intelligent interconnected systems. CPS integrates physical and software components capable of sensing, monitoring, and controlling physical assets and processes. 
However, developing distributed and scalable CPSs that efficiently handle large volumes of data while ensuring high performance and reliability remains a challenging task. Moreover, existing commercial solutions are often costly and not suitable for certain applications, limiting developers and researchers in experimenting and deploying CPSs on a larger scale.
The development of this project aims to contribute to the design and implementation of a solution to the CPS challenges. To achieve this goal, the Edge4CPS system was developed.
Edge4CPS system is an open source, distributed, multi-architecture solution that leverages Kubernetes for managing distributed edge computing clusters. It facilitates the deployment of applications across multiple computing nodes. It also offers services such as data pipeline, which includes data processing, classification, and visualization, as well as a middleware for messaging protocol translation.

Keywords (Theme):	Edge, Cloud, Fog, Scalable system, open source, Cluster, Data Pipeline
Keywords (Technologies):	Python, Kubernetes, REST, React, Docker

# Analysis

![image](https://github.com/BernardoCabral24/Edge4CPS/assets/104025833/69c126ed-a0c1-494b-a5eb-980217c496e2)

# Master Node:
The Master Node class represents the node that is responsible for managing and distributing tasks to all the other nodes in the system.  
  •	Edge4CPS API: The Edge4CPS API class represents the API responsible for interacting with the cluster console. It is responsible for deploying applications and services and checking for exposed ports. This API provides an endpoint for users to deploy applications within the cluster.
  •	Edge4CPS UI: The Edge4CPS UI class represents the user interface that will be exposed to users. It is responsible for abstracting the Edge4CPS API and providing users with a graphical and simple way to deploy applications and services, as well as check the exposed ports of their applications.
# Worker Node: 
The Worker Node class, symbolized in the domain model, represents a crucial component within the system architecture. It encompasses all the individual nodes that are dedicated to executing tasks delegated by the master node.
  •	Data Pipeline: The Data Pipeline class, represented in the domain model, embodies the core functionality related to data processing, classification, and visualization within the system. It serves as a pivotal component that orchestrates these tasks, and it operates as a service running on a dedicated worker node.
  •	Users Applications & Services: This class, depicted in the domain model, encompasses all the services and applications that are deployed and run within the worker node. These services and applications are deployed by users utilizing either the Web Interface or the API.
  •	Brokers: The Brokers class, depicted in the domain model, represents the messaging protocols that operate within the system, specifically within the worker node. These protocols facilitate communication between devices and applications within the system.
  •	Middleware: The Middleware class represents a service that can translate multiple messaging protocols. It interacts with the brokers to handle the translation between protocols. This class is running on the worker node.
# Kubernetes Framework: 
The Kubernetes class represents the component that runs within both the master node and the worker node. This framework enables the implementation of the system in a clustered manner. 
  •	Containerized environment: The Containerized Environment class represents the primary environment where most applications and services will run within the cluster. It virtualizes the applications, providing a separate and isolated runtime environment for each. This environment is essential for the proper functioning of the cluster framework.



