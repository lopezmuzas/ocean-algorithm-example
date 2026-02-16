# Ocean Protocol: Complete Guide — Ocean Node + Compute-to-Data

---

## PART 1: What is an Ocean Node?

Ocean Nodes are the core component of the Ocean Protocol stack. A **single monorepo** that replaces the three previous components (Provider, Aquarius, and Subgraph), radically simplifying deployment: **everything runs with a single command**.

**Integrated functions:**

- **Provider** → Accesses data, verifies on-chain permissions, encrypts/decrypts URLs, streams data, connects to C2D.
- **Aquarius (now "Indexer")** → Caches on-chain metadata in a Typesense database, exposes REST API.
- **Subgraph** → Indexes smart contract events in real-time, provides query API.

**Key technology:** libp2p for peer-to-peer communication, modular layered architecture (network, components, orchestration).

---

## PART 2: How to Create an Ocean Node

### Minimum Requirements

| Resource | Minimum |
|----------|---------|
| CPU | 1 vCPU |
| RAM | 2 GB |
| Storage | 4 GB |
| OS | Ubuntu LTS (recommended), macOS, Windows with WSL2 |
| Software | Docker Engine + Docker Compose |

### Quick Docker Deployment (Recommended Method)

```bash
# 1. Download the quickstart script
curl -O https://raw.githubusercontent.com/oceanprotocol/ocean-node/main/scripts/ocean-node-quickstart.sh

# 2. Set permissions and run
chmod +x ocean-node-quickstart.sh
./ocean-node-quickstart.sh
```

The script will interactively guide you through:

1. **Private Key** — You can generate a new one or use an existing one (format `0x...`)
2. **Wallet address** — Node admin account
3. **HTTP_API_PORT** — Default `8000`
4. **P2P Ports** — Default `9000-9003` (TCP IPv4, WS IPv4, TCP IPv6, WS IPv6)
5. **Public IP or FQDN** — Where your node will be accessible

It automatically generates a `docker-compose.yml`.

```bash
# 3. Start the node
docker-compose up -d

# 4. Verify it's running
docker ps
```

### Generated Configuration (docker-compose.yml)

The file includes two services:

- **ocean-node** — Image `oceanprotocol/ocean-node:latest`, ports 8000, 9000-9003
- **typesense** — Image `typesense/typesense:26.0`, port 8108 (Indexer database)

Key environment variables:

| Variable | Description |
|----------|-------------|
| `PRIVATE_KEY` | Node private key (mandatory, with `0x` prefix) |
| `RPCS` | JSON with RPC configuration for each supported chain |
| `DB_URL` | Typesense database URL |
| `P2P_ANNOUNCE_ADDRESS` | Public IP to announce on the P2P network |

> **Full environment variables reference:** https://github.com/oceanprotocol/ocean-node/blob/main/docs/env.md

### Alternative Deployment (From Source Code)

```bash
git clone https://github.com/oceanprotocol/ocean-node.git
cd ocean-node
nvm use             # Use the correct Node.js version
npm install
npm run build

# Configure environment variables
# Run the helper script to generate .env

npm run start
# Control panel available at http://localhost:8000/controlpanel/
```

### Requirements to Be Eligible for Incentives

To receive rewards from the Ocean Protocol Foundation:

1. **Public IP** — The node must be accessible from the Internet
2. **Exposed ports** — Both HTTP API and P2P ports must be open
3. **Verify accessibility** — From a different device: `telnet {your_ip} {P2P_port}`
4. **Port forwarding** — Configure on your router if behind NAT
5. **Verify on Dashboard** — https://nodes.oceanprotocol.com/ → search for your peerID → green indicator

### Node Update

```bash
chmod +x scripts/ocean-node-update.sh
./scripts/ocean-node-update.sh
```

### Multiple Nodes

You can run multiple nodes on the same IP, each on different ports. There is no node limit.

---

## PART 3: Compute-to-Data (C2D) — Fundamentals

C2D allows you to **monetize sensitive data without exposing it**. Instead of sharing raw data, computational access is offered: algorithms go to the data, not the other way around. This resolves the trade-off between leveraging private data and mitigating exposure risks.

**Typical use case:** If you own sensitive medical records, you can allow an algorithm to calculate the average age of patients without revealing any other individual details.

---

## PART 4: C2D Architecture in Detail

### Actors and Components

| Component | Role |
|-----------|------|
| **Consumer** | End user who initiates the C2D job by selecting dataset + algorithm |
| **Provider (Ocean Node)** | Main interface: validates permissions, verifies datatokens on-chain, coordinates with Operator Service |
| **Operator Service** | Microservice that manages the workflow queue and communicates with K8s |
| **Operator Engine** | Backend agent that orchestrates K8s infrastructure, creates/destroys pods |
| **Pod-Configuration** | Node.js script that downloads datasets and algorithms when starting a job |
| **Execution Pod (Algorithm Pod)** | Isolated K8s container where the algorithm runs |
| **Pod-Publishing** | CLI utility that uploads results to AWS S3 or IPFS |
| **Kubernetes** | K8s cluster where isolated pods are executed |

### Pre-conditions for C2D

Before the flow can begin:

1. The dataset's Asset DDO must have a `compute` type service
2. The compute service must allow algorithms to run on it
3. The DDO must specify an Ocean Provider endpoint exposed by the Publisher

### Detailed Step-by-Step Flow

#### Phase 1: Job Initiation

1. The consumer selects a preferred compute environment from the Provider's list
2. Initiates a job by choosing a dataset-algorithm pair
3. The Provider verifies orders on the blockchain (datatokens for dataset, algorithm, and compute fees)
4. If valid, the Provider calls `start(did, algorithm, additionalDIDs)` and returns a unique **job ID** to the consumer
5. The Provider informs the Operator Service of the new job
6. The Operator Service adds it to its local job queue

#### Phase 2: K8s Cluster and Volume Creation

7. The Operator Engine periodically queries the Operator Service for pending jobs
8. If resources are available, it requests the job list
9. **K8s volumes** are created for the new job
10. Volumes are assigned to the pod
11. The Operator Engine starts the **pod-configuration**

#### Phase 3: Loading Datasets and Algorithms

12. Pod-configuration requests datasets and algorithm from their respective Providers
13. Files are downloaded via the Provider (never direct URLs)
14. Pod-configuration writes datasets to the job volume at the correct paths:
    - Datasets → `/data/inputs/{DID}/{index}` (files named by index: 0, 1, 2...)
    - Algorithm → `/data/transformations/algorithm` (first file), then indexed 1 to X
    - DDOs → `/data/ddos/` (JSON files with DDO structure)
15. If there's any provisioning failure, the script updates the job status in PostgreSQL and logs the errors
16. Pod-configuration signals the Operator Engine that it's ready

#### Phase 4: Algorithm Execution

17. The Operator Engine launches the **algorithm pod** in K8s with the mounted volume (datasets + algorithm)
18. K8s executes the algorithm pod
19. The Operator Engine **monitors** the algorithm and stops it if it exceeds the time limit of the chosen environment
20. When results are available, the Operator Engine starts **pod-publishing**
21. Pod-publishing uploads results, logs, and admin logs to the output volume (S3 or IPFS)
22. Notifies the Operator Engine that the upload was successful

#### Phase 5: Cleanup

23. The Operator Engine **deletes the K8s volumes**
24. K8s removes all used volumes
25. The Operator Engine finalizes the job and notifies the Operator Service

#### Phase 6: Result Retrieval

26. The consumer calls `getJobDetails(jobID)` to the Provider
27. The Provider queries the Operator Service
28. With the details, the consumer can download the results from the executed job
29. Results are served from the output volume (S3/IPFS) via the Provider

### Internal Components in Depth

#### Operator Service

Main responsibilities:
- Expose HTTP API for access and compute endpoints
- Interact with infrastructure (cloud/on-premise) using Publisher's credentials
- Start/stop/execute compute instances with user-provided algorithms
- Retrieve execution logs
- Register new compute jobs in K8s
- List current jobs and get detailed results per job
- Stop a running job

> **Does not store state:** Everything is saved directly in the K8s cluster.

Can be integrated from the Ocean Provider or called independently.

#### Operator Engine

Responsibilities:
- Orchestrate the complete execution flow
- Start the configuration pod (dependency download)
- Start the algorithm pod
- Start the publishing pod (new assets to the network)
- Monitor execution times

**Operator Engine configuration variables:**

| Variable | Description |
|----------|-------------|
| `OPERATOR_PRIVATE_KEY` | Unique operator private key (future: account to receive fees) |
| `IPFS_OUTPUT` | IPFS gateway for uploading output data |
| `IPFS_OUTPUT_PREFIX` | Prefix for IPFS URLs |
| `IPFS_ADMINLOGS` | Gateway for admin logs |
| `AWS_ACCESS_KEY_ID` | S3 credentials for log and output buckets |
| `AWS_SECRET_ACCESS_KEY` | S3 credentials |
| `BUCKET_OUTPUT` | S3 bucket for algorithm output |
| `BUCKET_ADMINLOGS` | S3 bucket for admin logs |
| `STORAGE_CLASS` | K8s storage class to use |
| `NOTIFY_START_URL` | Callback URL when a job starts |
| `NOTIFY_STOP_URL` | Callback URL when a job ends |
| `MAX_JOB_DURATION` | Maximum duration in hours. `0` = no expiration |
| `SERVICE_ACCOUNT` | K8s account to run pods (default: `default`) |
| `IPFS_TYPE` | `CLUSTER` or `CLIENT` (default: CLIENT) |

#### Pod-Configuration

Node.js script that on startup:
1. **Downloads datasets** → `/data/inputs/{DID}/{index}`
2. **Downloads algorithm** → `/data/transformations/algorithm`
3. **Downloads DDOs** → `/data/ddos/`
4. **Error handling**: Updates status in PostgreSQL if it fails
5. **Completion signal**: Notifies the Operator Engine to start the algorithm pod

#### Pod-Publishing

Three functional areas:
1. **Interaction with Operator Service**: Uploads outputs to S3 or IPFS, logs steps, updates PostgreSQL
2. **Role in the Publishing Pod**: Publishes new assets created in the Ocean Protocol network
3. **Output Management**: Stores results according to configuration (IPFS or AWS S3)

> Does not provide its own storage; all state lives in K8s or the chosen data storage solution.

---

## PART 5: Datasets & Algorithms — Classification & Permissions

### Algorithm Types

Algorithms in C2D are classified by their accessibility by setting `attributes.main.type` in the DDO:

| Type | Meaning |
|------|---------|
| `"access"` | **Public.** Can be downloaded with the appropriate datatoken |
| `"compute"` | **Private.** Only available to run as part of a C2D job, with no way to download it. Must be published on the same Ocean Provider as the target dataset |

### Permission Levels for Datasets

By **default, all datasets are published as private** (no algorithms allowed). This prevents data leakage by malicious algorithms. The publisher can configure:

| Configuration | Behavior |
|---------------|----------|
| **Allow specific algorithms** | Only algorithms referenced by DID can run |
| **Allow all published** | Any published algorithm on the network can run (using wildcard `*`) |
| **Allow raw algorithms** | Raw code can run (higher data escape risk) |
| **Allow by publisher** | Only algorithms from specific publishers (by address) |

### Permission Configuration in the DDO (Compute Options)

A `compute` type asset includes an additional `compute` object in its service:

```json
{
  "services": [
    {
      "id": "2",
      "type": "compute",
      "files": "0x6dd05e0edb460623c843a263291ebe757c1eb3...",
      "name": "Compute service",
      "datatokenAddress": "0x124",
      "serviceEndpoint": "https://myprovider.com",
      "timeout": 0,
      "compute": {
        "allowRawAlgorithm": false,
        "allowNetworkAccess": true,
        "publisherTrustedAlgorithmPublishers": ["0x234", "0x235"],
        "publisherTrustedAlgorithms": [
          {
            "did": "did:op:123",
            "filesChecksum": "100",
            "containerSectionChecksum": "200"
          }
        ]
      }
    }
  ]
}
```

### Compute Object Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `allowRawAlgorithm`* | boolean | If `true`, raw text is accepted. Useful for drag & drop but escape risk. **Default: `false`** |
| `allowNetworkAccess`* | boolean | If `true`, the job will have network access |
| `publisherTrustedAlgorithmPublishers`* | string[] | Trusted publisher addresses. If contains `*`, all allowed. If empty or undefined, restricted access |
| `publisherTrustedAlgorithms`* | object[] | Array of trusted algorithms. If contains `*`, all published algorithms allowed. If empty or undefined, **none allowed** |

### Trusted Algorithms: Integrity Verification

Each entry in `publisherTrustedAlgorithms` includes:

| Field | Description |
|-------|-------------|
| `did` | DID of the trusted algorithm |
| `filesChecksum` | Hash of the algorithm files. Obtained by calling the Provider FileInfoEndpoint with `withChecksum=True`. If multiple files, it's the concatenation of checksums |
| `containerSectionChecksum` | Hash calculated as: `sha256(entrypoint + docker_image_checksum)` |

This ensures the algorithm has not been modified after being authorized.

---

## PART 6: Writing Algorithms for C2D

### Algorithm Components

Every C2D algorithm has three parts:

1. **Algorithm code** — Your logic (Python, Node.js, R, Julia, etc.)
2. **Docker image** — Runtime environment (base image + tag)
3. **Entry point** — Command that initiates execution

### Environment Object in Metadata

```json
{
  "algorithm": {
    "container": {
      "entrypoint": "python3.9 $ALGO",
      "image": "python",
      "tag": "3.9.4-alpine3.13",
      "checksum": "sha256:xxxxx"
    },
    "language": "Python",
    "version": "1.0.0",
    "consumerParameters": []
  }
}
```

- `$ALGO` is a **macro** that is automatically replaced with the path where your code was downloaded inside the pod.
- `image` + `tag` define the Docker container.
- `checksum` is the SHA256 digest of the Docker image.
- `entrypoint` defines your entry point. If you have multiple Python versions, specify the correct one: `python3.6 $ALGO`.

### Complete Algorithm Metadata (DDO)

```json
{
  "metadata": {
    "created": "2020-11-15T12:27:48Z",
    "updated": "2021-05-17T21:58:02Z",
    "description": "Sample description",
    "name": "Sample algorithm asset",
    "type": "algorithm",
    "author": "OPF",
    "license": "https://market.oceanprotocol.com/terms",
    "algorithm": {
      "language": "Node.js",
      "version": "1.0.0",
      "container": {
        "entrypoint": "node $ALGO",
        "image": "ubuntu",
        "tag": "latest",
        "checksum": "sha256:44e10daa6637893f4276bb8d7301eb35306ece50f61ca34dcab550"
      },
      "consumerParameters": {}
    }
  }
}
```

### Available Docker Images

Standard Ocean images: https://github.com/oceanprotocol/algo_dockers

| Environment | image | tag | entrypoint |
|-------------|-------|-----|------------|
| Python 3.9 | `python` | `3.9.4-alpine3.13` | `python3.9 $ALGO` |
| Node.js 14 | `node` | `14` | `node $ALGO` |
| Node.js 12 | `node` | `12` | `node $ALGO` |
| Python + SQL | `oceanprotocol/algo_dockers` | `python-sql` | `python3.6 $ALGO` |

**Need custom dependencies?** Create your own Docker image:

```dockerfile
FROM python:3.9.4-alpine3.13
RUN pip install pandas numpy scikit-learn matplotlib
# The image must support "pip" or your language's package manager
```

Publish it on DockerHub and reference the image/tag in your metadata.

### Data Storage in the Pod (Volumes)

| Path | Permissions | Content |
|------|-------------|---------|
| `/data/inputs` | Read | Input datasets. Structure: `/data/inputs/{did}/{service_id}`. Files named by index (0, 1, 2...) |
| `/data/ddos` | Read | JSON files with the complete DDO structure of each asset (dataset + algorithm) |
| `/data/outputs` | Read/Write | **Write your results here.** Uploaded to S3/IPFS and returned to the consumer |
| `/data/logs/` | Read/Write | All algorithm output (print, console.log, etc.) is saved here and sent to the consumer |
| `/data/transformations/` | Read | Where the downloaded algorithm code is stored |
| `/data/inputs/algoCustomData.json` | Read | Consumer custom parameters (if `consumerParameters` were defined) |

> **Important note:** When using local Providers or Metadata Caches, DDOs may not transfer correctly to C2D, but inputs are still available. If your algorithm relies on DDO JSON content, make sure to use a public Provider and Metadata Cache.

### Environment Variables Available in the Pod

| Variable | Content |
|----------|---------|
| `DIDS` | JSON array with the DIDs of input datasets |
| `TRANSFORMATION_DID` | DID of the algorithm being executed |

### Consumer Parameters

Allow the dataset or algorithm publisher to define **inputs that the buyer must fill in** before running the job.

**Supported parameter types:**

| Type | Description |
|------|-------------|
| `text` | Free text field |
| `number` | Numeric field |
| `boolean` | true/false checkbox |
| `select` | Dropdown list with predefined options |

**Structure of each parameter:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Parameter name (key in the JSON) |
| `type` | string | Yes | text, number, boolean, select |
| `label` | string | Yes | Label visible to the user |
| `required` | boolean | Yes | Whether it's mandatory |
| `description` | string | Yes | Field description |
| `default` | string/number/boolean | Yes | Default value. For select: string key of the option |
| `options` | object[] | Select only | List of options `{key: value}` |

**Complete definition example:**

```json
[
  {
    "name": "hometown",
    "type": "text",
    "label": "Hometown",
    "required": true,
    "description": "What is your hometown?",
    "default": "Nowhere"
  },
  {
    "name": "age",
    "type": "number",
    "label": "Age",
    "required": false,
    "description": "Please fill your age",
    "default": 0
  },
  {
    "name": "developer",
    "type": "boolean",
    "label": "Developer",
    "required": false,
    "description": "Are you a developer?",
    "default": false
  },
  {
    "name": "languagePreference",
    "type": "select",
    "label": "Language",
    "required": false,
    "description": "Do you like NodeJs or Python",
    "default": "nodejs",
    "options": [
      { "nodejs": "I love NodeJs" },
      { "python": "I love Python" }
    ]
  }
]
```

**Resulting JSON file in the pod** (`/data/inputs/algoCustomData.json`):

```json
{
  "hometown": "São Paulo",
  "age": 10,
  "developer": true,
  "languagePreference": "nodejs"
}
```

**Use case for datasets:** If the publisher needs to know the sampling interval, they define a `sampling` parameter. The value is added as a query parameter to the dataset URL: `https://example.com/mydata?sampling=10`.

**Use case for algorithms:** An algorithm that needs to know the number of iterations defines an `iterations` field. The buyer enters the value, which is stored in `algoCustomData.json` for the algorithm to read.

### Complete Example: Python Algorithm with Job Details

```python
import pandas as pd
import numpy as np
import os
import json

def get_job_details():
    """Reads metadata of assets used by the algorithm"""
    job = dict()
    job['dids'] = json.loads(os.getenv('DIDS', None))
    job['metadata'] = dict()
    job['files'] = dict()
    job['algo'] = dict()
    job['secret'] = os.getenv('secret', None)
    algo_did = os.getenv('TRANSFORMATION_DID', None)
    
    if job['dids'] is not None:
        for did in job['dids']:
            filename = '/data/ddos/' + did
            print(f'Reading json from {filename}')
            with open(filename) as json_file:
                ddo = json.load(json_file)
                for service in ddo['service']:
                    if service['type'] == 'metadata':
                        job['files'][did] = list()
                        index = 0
                        for file in service['attributes']['main']['files']:
                            job['files'][did].append(
                                '/data/inputs/' + did + '/' + str(index))
                            index = index + 1
    if algo_did is not None:
        job['algo']['did'] = algo_did
        job['algo']['ddo_path'] = '/data/ddos/' + algo_did
    return job

def line_counter(job_details):
    """Executes line counting based on inputs"""
    print('Starting compute job with the following input information:')
    print(json.dumps(job_details, sort_keys=True, indent=4))
    first_did = job_details['dids'][0]
    filename = job_details['files'][first_did][0]
    non_blank_count = 0
    with open(filename) as infp:
        for line in infp:
            if line.strip():
                non_blank_count += 1
    print('number of non-blank lines found %d' % non_blank_count)
    f = open("/data/outputs/result", "w")
    f.write(str(non_blank_count))
    f.close()

if __name__ == '__main__':
    line_counter(get_job_details())
```

### Complete Example: Node.js Algorithm (Input Scan)

```javascript
const fs = require('fs')
const inputFolder = '/data/inputs'
const outputFolder = '/data/outputs'

async function countrows(file) {
  console.log('Start counting for ' + file)
  const fileBuffer = fs.readFileSync(file)
  const toString = fileBuffer.toString()
  const splitLines = toString.split('\n')
  const rows = splitLines.length - 1
  fs.appendFileSync(outputFolder + '/output.log', file + ',' + rows + '\r\n')
  console.log('Finished. We have ' + rows + ' lines')
}

async function processfolder(folder) {
  const files = fs.readdirSync(folder)
  for (const i = 0; i < files.length; i++) {
    const file = files[i]
    const fullpath = folder + '/' + file
    if (fs.statSync(fullpath).isDirectory()) {
      await processfolder(fullpath)
    } else {
      await countrows(fullpath)
    }
  }
}

processfolder(inputFolder)
```

> This example does not use environment variables — it directly scans `/data/inputs`. It generates `/data/outputs/output.log` and `/data/logs/algo.log`.

---

## PART 7: C2D Flow with ocean.py (Practical Development)

### Publish Dataset with Compute Service

```python
from ocean_lib.structures.file_objects import UrlFile

DATA_url_file = UrlFile(
    url="https://raw.githubusercontent.com/oceanprotocol/c2d-examples/main/branin_and_gpr/branin.arff"
)
name = "Branin dataset"

(DATA_data_nft, DATA_datatoken, DATA_ddo) = ocean.assets.create_url_asset(
    name, DATA_url_file.url, {"from": alice},
    with_compute=True,
    wait_for_aqua=True
)
```

> To customize privacy and accessibility, add `compute_values` to `create_url_asset` according to the DDO specs.

### Publish Algorithm

To replace the sample algorithm:
1. Use one of the standard `algo_dockers` images or publish a custom Docker image
2. Use the image name and tag in the `container` part of the algorithm metadata
3. The image must support dependency installation (e.g., `pip` for Python)
4. You can use any language

### Pay and Execute

```python
# pay_for_compute_service() automates:
# - Order initiation
# - Reuse of previous orders (if transfer_tx_id exists)
# - If provider fees expired but the order is still valid → reuses on-chain
# - If no transfer_tx_id or the order expired → creates a new order

# To upgrade compute resources, use a paid C2D environment:
environments = ocean.ocean_compute.get_c2d_environments(
    service.service_endpoint,
    DATA_ddo.chain_id
)
fees = ocean.retrieve_provider_fees_for_compute(
    datasets, algorithm_data,
    consumer_address, compute_environment, duration
)
```

---

## PART 8: Deploying Your Own C2D Environment

### Hardware Requirements

| Resource | Recommended |
|----------|-------------|
| CPUs | 8 |
| RAM | 16 GB |
| Storage | 100 GB SSD |
| Network | Fast Internet connection |

### Deployment Steps

#### 1. Install Minikube (if you don't have K8s)

```bash
wget -q --show-progress https://github.com/kubernetes/minikube/releases/download/v1.22.0/minikube_1.22.0-0_amd64.deb
sudo dpkg -i minikube_1.22.0-0_amd64.deb
minikube config set kubernetes-version v1.16.0
minikube start --cni=calico --driver=docker --container-runtime=docker
```

#### 2. Install kubectl

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

#### 3. Clone Repositories

```bash
mkdir computeToData && cd computeToData
git clone https://github.com/oceanprotocol/operator-service
git clone https://github.com/oceanprotocol/operator-engine
```

#### 4. Configure PostgreSQL and storage (IPFS or S3)

#### 5. Deploy Operator Service

```bash
kubectl config set-context --current --namespace ocean-operator
kubectl apply -f operator-service/kubernetes/deployment.yaml
```

#### 6. Initialize and create compute environment

```bash
curl -X POST "https://compute.example.com/api/v1/operator/pgsqlinit" \
  -H "accept: application/json" -H "Admin: myAdminPass"
```

> **Automated script:** https://github.com/oceanprotocol/c2d_barge

---

## PART 9: Development Tools

| Tool | Use | URL |
|------|-----|-----|
| **Ocean.py** | Python library to publish, consume, and run C2D | https://github.com/oceanprotocol/ocean.py |
| **Ocean.js** | JavaScript/TypeScript equivalent library | https://github.com/oceanprotocol/ocean.js |
| **Ocean CLI** | CLI tool for publish, consume, C2D | https://docs.oceanprotocol.com/developers/ocean-cli |
| **Barge** | Complete local environment for development and testing | https://docs.oceanprotocol.com/developers/barge |
| **c2d-examples** | Algorithm and dataset examples for C2D | https://github.com/oceanprotocol/c2d-examples |
| **algo_dockers** | Pre-configured Docker images | https://github.com/oceanprotocol/algo_dockers |

---

## PART 10: Quick Checklists

### To Set Up an Ocean Node

- [ ] Server with 1 vCPU, 2 GB RAM, 4 GB disk minimum
- [ ] Docker + Docker Compose installed
- [ ] Public IP available
- [ ] Run `ocean-node-quickstart.sh`
- [ ] Open ports 8000, 9000-9003
- [ ] Verify at https://nodes.oceanprotocol.com/

### To Develop a C2D Algorithm

- [ ] Choose language and Docker image (or create your own)
- [ ] Read data from `/data/inputs/{did}/{index}`
- [ ] Optionally read DDOs from `/data/ddos/{did}`
- [ ] Optionally read consumer params from `/data/inputs/algoCustomData.json`
- [ ] Write results to `/data/outputs/`
- [ ] Define metadata: `container.entrypoint`, `container.image`, `container.tag`, `container.checksum`
- [ ] Publish as `algorithm` type asset
- [ ] Verify the dataset allows your algorithm (trusted algorithms)

### To Deploy a C2D Environment

- [ ] Powerful server (8 CPU, 16 GB RAM, 100 GB SSD)
- [ ] Kubernetes or Minikube installed
- [ ] PostgreSQL deployed in K8s
- [ ] IPFS or AWS S3 configured for outputs
- [ ] Operator Service deployed and initialized
- [ ] Operator Engine configured with unique PRIVATE_KEY
- [ ] StorageClass in the same zone as pods
- [ ] Provider (Ocean Node) accessible and connected

---

## PART 11: Programmatic Integration via API — Connecting an External Program to the Ocean Node

This section details how to connect **your own Python program** directly to the Ocean Node HTTP API to execute C2D jobs without using the marketplace. Two approaches are covered: the node's direct HTTP API and the `ocean.py` library as a high-level wrapper.

### Complete Flow Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────┐
│ Your Python  │────→│  Ocean Node  │────→│  Operator    │────→│   K8s    │
│   program    │←────│  (Provider)  │←────│  Service     │←────│  C2D Pod │
│              │     │  HTTP API    │     │              │     │          │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────┘
       │                    │
       │  1. GET environments │
       │  2. Pay on-chain     │
       │  3. POST /compute    │
       │  4. GET /compute     │ (polling status)
       │  5. GET /computeResult│
       ▼                    ▼
```

---

### 11.1 Ocean Node HTTP API — Compute Endpoints

The Ocean Node exposes the same endpoints as the former Provider, now integrated into a single service. All compute endpoints are under `/api/services/`.

#### List Available Compute Environments

```
GET /api/services/computeEnvironments?chainId={chainId}
```

**Parameters:**
- `chainId` (int, required) — Chain ID (e.g., 1 for Mainnet, 137 for Polygon, 8996 for development)

**Response:**

```json
[
  {
    "id": "ocean-compute",
    "cpuType": "AMD Ryzen 7 5800X 8-Core Processor",
    "nCPU": 2,
    "ramGB": 1,
    "diskGB": 2,
    "gpuType": "AMD RX570",
    "nGPU": 0,
    "priceMin": 2.3,
    "maxJobs": 10,
    "currentJobs": 0,
    "desc": "Compute environment description"
  }
]
```

#### Start a Compute Job

```
POST /api/services/compute
```

**Body (JSON):**

```json
{
  "signature": "0x...",
  "consumerAddress": "0xYourWalletAddress",
  "nonce": 1,
  "environment": "ocean-compute",
  "dataset": {
    "documentId": "did:op:DATASET_DID",
    "serviceId": "compute",
    "transferTxId": "0xOnChainOrderTxHash",
    "userdata": {}
  },
  "algorithm": {
    "documentId": "did:op:ALGORITHM_DID",
    "serviceId": "compute",
    "transferTxId": "0xAlgorithmOrderTxHash",
    "algocustomdata": {
      "iterations": 100,
      "learning_rate": 0.01
    }
  },
  "additionalDatasets": []
}
```

**Key fields:**

| Field | Description |
|-------|-------------|
| `signature` | Consumer's signed message (authentication) |
| `consumerAddress` | Consumer's Ethereum address |
| `nonce` | Nonce to prevent replay attacks |
| `environment` | Compute environment ID (obtained from the previous endpoint) |
| `dataset.documentId` | Dataset DID |
| `dataset.serviceId` | Compute service ID in the DDO |
| `dataset.transferTxId` | On-chain transaction hash for datatoken approval |
| `dataset.userdata` | Consumer parameters for the dataset (optional) |
| `algorithm.documentId` | Algorithm DID (one of `documentId` or `meta` is required) |
| `algorithm.meta` | Alternative: raw algorithm metadata (if not using DID) |
| `algorithm.transferTxId` | On-chain transaction hash for the algorithm |
| `algorithm.algocustomdata` | **Consumer Parameters** — the JSON with parameters your algorithm will read from `/data/inputs/algoCustomData.json` |
| `additionalDatasets` | Array of additional dataset objects (optional) |

**Response:**

```json
[
  {
    "jobId": "0x1111:001",
    "status": 1,
    "statusText": "Job started"
  }
]
```

#### Query Job Status

```
GET /api/services/compute?signature={sig}&consumerAddress={addr}&jobId={jobId}&documentId={did}
```

At least one of `documentId`, `jobId` is required.

**Response:**

```json
[
  {
    "owner": "0x1111",
    "documentId": "did:op:2222",
    "jobId": "3333",
    "dateCreated": "2020-10-01T01:00:00Z",
    "dateFinished": "2020-10-01T01:00:00Z",
    "status": 70,
    "statusText": "Job completed",
    "algorithmLogUrl": "http://example.net/logs/algo.log",
    "resultsUrls": [
      "http://example.net/logs/output/0",
      "http://example.net/logs/output/1"
    ],
    "resultsDid": "did:op:87bdaabb..."
  }
]
```

**Status codes:**

| Status | Text | Meaning |
|--------|------|---------|
| 1 | Warming up | Starting |
| 10 | Job started | Job begun |
| 20 | Configuring volumes | Configuring K8s volumes |
| 30 | Provisioning success | Data downloaded successfully |
| 31 | Data provisioning failed | **Error:** failed to download data |
| 32 | Algorithm provisioning failed | **Error:** failed to download algorithm |
| 40 | Running algorithm | Algorithm executing |
| 50 | Filtering results | Filtering results |
| 60 | Publishing results | Publishing results |
| 70 | Job completed | **Completed** |

#### Download Results

```
GET /api/services/computeResult?jobId={jobId}&index={index}&consumerAddress={addr}&nonce={nonce}&signature={sig}
```

**Parameters:**
- `jobId` — Job ID
- `index` — Index of the result to download (0 for first output)
- `consumerAddress`, `nonce`, `signature` — Authentication

**Response:** Byte string containing the compute result.

#### Stop a Job

```
PUT /api/services/compute?signature={sig}&documentId={did}&jobId={jobId}
```

#### Delete a Job

```
DELETE /api/services/compute?signature={sig}&documentId={did}&jobId={jobId}&consumerAddress={addr}
```

---

### 11.2 Complete Integration with ocean.py (Recommended Method)

`ocean.py` abstracts all the complexity of signatures, on-chain transactions, and HTTP calls. This is the recommended method for an external program.

#### Installation

```bash
pip install ocean-lib
```

#### Initial Configuration

```python
import os
from ocean_lib.ocean.ocean import Ocean
from ocean_lib.web3_internal.wallet import Wallet
from ocean_lib.example_config import get_config_dict

# Configuration — pointing to your Ocean Node
config = get_config_dict("polygon")  # or "mainnet", "sepolia", etc.

# Override the Provider URL with your own Ocean Node
config["PROVIDER_URL"] = "http://YOUR_OCEAN_NODE_IP:8000"

ocean = Ocean(config)

# Your wallet (consumer)
consumer_wallet = Wallet(
    ocean.web3,
    private_key=os.getenv("CONSUMER_PRIVATE_KEY"),  # 0x...
)
print(f"Consumer address: {consumer_wallet.address}")
```

#### Step 1: Resolve Dataset and Algorithm

```python
# Get DDOs by DID
DATA_ddo = ocean.assets.resolve("did:op:YOUR_DATASET_DID")
ALGO_ddo = ocean.assets.resolve("did:op:YOUR_ALGORITHM_DID")

# Get the dataset's compute service
compute_service = DATA_ddo.services[0]  # or search by type="compute"
assert compute_service.type == "compute", "Service is not of type compute"

# Get the algorithm service
algo_service = ALGO_ddo.services[0]

print(f"Dataset: {DATA_ddo.did}")
print(f"Algorithm: {ALGO_ddo.did}")
print(f"Provider endpoint: {compute_service.service_endpoint}")
```

#### Step 2: Select Compute Environment

```python
# List all available C2D environments
environments = ocean.compute.get_c2d_environments(
    compute_service.service_endpoint,
    DATA_ddo.chain_id
)

print("Available environments:")
for env in environments:
    print(f"  ID: {env['id']}, CPU: {env['nCPU']}, RAM: {env['ramGB']}GB, "
          f"GPU: {env['nGPU']}, Min price: {env['priceMin']}")

# Choose environment (e.g., the first available, or the free one)
compute_env = environments[0]["id"]

# Or for a free environment:
# free_env = ocean.compute.get_free_c2d_environment(
#     compute_service.service_endpoint, DATA_ddo.chain_id
# )
# compute_env = free_env["id"]
```

#### Step 3: Pay for the Compute Service (On-Chain)

```python
from ocean_lib.models.compute_input import ComputeInput

# Create ComputeInput objects
dataset_compute = ComputeInput(DATA_ddo, compute_service)
algo_compute = ComputeInput(ALGO_ddo, algo_service)

# Get provider fee preview
datasets = [dataset_compute]
algorithm_data = algo_compute

# Pay — this automatically handles:
# - Datatoken approval for dataset
# - Datatoken approval for algorithm
# - Provider fees
# - Reuse of previous orders if still valid
datasets, algorithm_data = ocean.assets.pay_for_compute_service(
    datasets=datasets,
    algorithm_data=algorithm_data,
    consumer_address=consumer_wallet.address,
    compute_environment=compute_env,
    valid_until=0,  # 0 = use environment's default duration
    consume_market_order_fee_address=consumer_wallet.address,
    consume_market_order_fee_token=DATA_ddo.datatokens[0]["address"],
    consume_market_order_fee_amount=0,
    wallet=consumer_wallet,
)
```

#### Step 4: Start the C2D Job with Consumer Parameters

```python
# Define your consumer parameters (algocustomdata)
# These will arrive at the algorithm in /data/inputs/algoCustomData.json
my_algo_params = {
    "iterations": 100,
    "learning_rate": 0.01,
    "model_type": "random_forest",
    "output_format": "json"
}

# Start the compute job
job_id = ocean.compute.start(
    consumer_wallet=consumer_wallet,
    dataset=dataset_compute,
    compute_environment=compute_env,
    algorithm=algo_compute,
    algorithm_algocustomdata=my_algo_params,  # ← your consumer parameters
    additional_datasets=[],  # additional datasets if any
)

print(f"Job started! ID: {job_id}")
```

#### Step 5: Monitor Status (Polling)

```python
import time

# Poll status until the job finishes
while True:
    status = ocean.compute.status(
        ddo=DATA_ddo,
        service=compute_service,
        job_id=job_id,
        wallet=consumer_wallet
    )
    
    print(f"Status: {status['statusText']} (code: {status['status']})")
    
    # Job completed
    if status["status"] == 70:
        print("Job completed successfully!")
        break
    
    # Errors
    if status["status"] in (31, 32):
        print(f"ERROR: {status['statusText']}")
        break
    
    time.sleep(15)  # Wait 15 seconds before the next check
```

#### Step 6: Download Results

```python
# Get job result (index 0 = first output)
result = ocean.compute.result(
    ddo=DATA_ddo,
    service=compute_service,
    job_id=job_id,
    index=0,
    wallet=consumer_wallet
)

print(f"Result DID: {result.get('did', 'N/A')}")
print(f"Result URLs: {result.get('urls', [])}")
print(f"Log URLs: {result.get('logs', [])}")

# Get algorithm logs
logs = ocean.compute.compute_job_result_logs(
    ddo=DATA_ddo,
    service=compute_service,
    job_id=job_id,
    wallet=consumer_wallet,
    log_type="output"  # "output" or "algorithmLog"
)
print(f"Logs: {logs}")
```

#### Step 7 (Optional): Stop a Running Job

```python
stop_result = ocean.compute.stop(
    ddo=DATA_ddo,
    service=compute_service,
    job_id=job_id,
    wallet=consumer_wallet
)
print(f"Job stopped: {stop_result['statusText']}")
```

---

### 11.3 End-to-End Example: Complete Script

```python
#!/usr/bin/env python3
"""
Complete example: Connect external program to Ocean Node C2D
No marketplace — everything via programmatic API.
"""

import os
import time
from ocean_lib.ocean.ocean import Ocean
from ocean_lib.web3_internal.wallet import Wallet
from ocean_lib.example_config import get_config_dict
from ocean_lib.models.compute_input import ComputeInput

# ============================================================
# CONFIGURATION
# ============================================================
NETWORK = "polygon"                           # Blockchain network
OCEAN_NODE_URL = "http://YOUR_NODE_IP:8000"   # Your Ocean Node
DATASET_DID = "did:op:YOUR_DATASET_DID"       # Dataset DID
ALGO_DID = "did:op:YOUR_ALGORITHM_DID"        # Algorithm DID
PRIVATE_KEY = os.getenv("CONSUMER_PRIVATE_KEY")

# Custom parameters for the algorithm
ALGO_PARAMS = {
    "iterations": 500,
    "learning_rate": 0.001,
    "batch_size": 32
}

# ============================================================
# INITIALIZATION
# ============================================================
config = get_config_dict(NETWORK)
config["PROVIDER_URL"] = OCEAN_NODE_URL
ocean = Ocean(config)
wallet = Wallet(ocean.web3, private_key=PRIVATE_KEY)
print(f"[INIT] Consumer: {wallet.address}")

# ============================================================
# RESOLVE ASSETS
# ============================================================
data_ddo = ocean.assets.resolve(DATASET_DID)
algo_ddo = ocean.assets.resolve(ALGO_DID)
compute_svc = data_ddo.services[0]
algo_svc = algo_ddo.services[0]
print(f"[OK] Dataset resolved: {data_ddo.did}")
print(f"[OK] Algorithm resolved: {algo_ddo.did}")

# ============================================================
# SELECT ENVIRONMENT
# ============================================================
envs = ocean.compute.get_c2d_environments(
    compute_svc.service_endpoint, data_ddo.chain_id
)
env_id = envs[0]["id"]
print(f"[OK] Environment selected: {env_id} "
      f"(CPU:{envs[0]['nCPU']}, RAM:{envs[0]['ramGB']}GB)")

# ============================================================
# PAY ON-CHAIN
# ============================================================
dataset_input = ComputeInput(data_ddo, compute_svc)
algo_input = ComputeInput(algo_ddo, algo_svc)

datasets, algo_data = ocean.assets.pay_for_compute_service(
    datasets=[dataset_input],
    algorithm_data=algo_input,
    consumer_address=wallet.address,
    compute_environment=env_id,
    valid_until=0,
    consume_market_order_fee_address=wallet.address,
    consume_market_order_fee_token=data_ddo.datatokens[0]["address"],
    consume_market_order_fee_amount=0,
    wallet=wallet,
)
print("[OK] Payment completed")

# ============================================================
# START C2D JOB WITH CONSUMER PARAMETERS
# ============================================================
job_id = ocean.compute.start(
    consumer_wallet=wallet,
    dataset=dataset_input,
    compute_environment=env_id,
    algorithm=algo_input,
    algorithm_algocustomdata=ALGO_PARAMS,
)
print(f"[OK] Job started: {job_id}")

# ============================================================
# STATUS POLLING
# ============================================================
TERMINAL_STATES = {70, 31, 32}
while True:
    status = ocean.compute.status(data_ddo, compute_svc, job_id, wallet)
    code = status["status"]
    text = status["statusText"]
    print(f"[...] Status: {text} ({code})")
    
    if code in TERMINAL_STATES:
        break
    time.sleep(15)

# ============================================================
# RETRIEVE RESULTS
# ============================================================
if code == 70:
    result = ocean.compute.result(data_ddo, compute_svc, job_id, 0, wallet)
    print(f"\n[RESULT] URLs: {result.get('urls', [])}")
    print(f"[RESULT] DID: {result.get('did', 'N/A')}")
    
    logs = ocean.compute.compute_job_result_logs(
        data_ddo, compute_svc, job_id, wallet
    )
    print(f"[LOGS] {logs}")
else:
    print(f"\n[ERROR] Job failed with status: {text}")
```

---

### 11.4 Integration via Direct HTTP (Without ocean.py)

If you prefer not to use `ocean.py` and make direct HTTP calls (e.g., from another language or a microservice), you need to manually handle signatures and on-chain transactions.

```python
"""
Example of direct HTTP calls to the Ocean Node.
Requires: requests, web3, eth_account
"""

import requests
import json
import time
from web3 import Web3
from eth_account.messages import encode_defunct

OCEAN_NODE = "http://YOUR_NODE_IP:8000"
PRIVATE_KEY = "0x..."
CHAIN_ID = 137  # Polygon

w3 = Web3()
account = w3.eth.account.from_key(PRIVATE_KEY)

def sign_message(message: str) -> str:
    """Signs a message with the consumer's private key."""
    msg = encode_defunct(text=message)
    signed = w3.eth.account.sign_message(msg, private_key=PRIVATE_KEY)
    return signed.signature.hex()


# --- 1. LIST ENVIRONMENTS ---
def get_environments(chain_id: int):
    resp = requests.get(
        f"{OCEAN_NODE}/api/services/computeEnvironments",
        params={"chainId": chain_id}
    )
    return resp.json()


# --- 2. START JOB ---
def start_compute_job(
    dataset_did: str,
    algo_did: str,
    environment_id: str,
    dataset_tx_id: str,
    algo_tx_id: str,
    algo_custom_data: dict = None
):
    nonce = int(time.time())
    message = f"{account.address}{dataset_did}{nonce}"
    signature = sign_message(message)
    
    payload = {
        "signature": signature,
        "consumerAddress": account.address,
        "nonce": nonce,
        "environment": environment_id,
        "dataset": {
            "documentId": dataset_did,
            "serviceId": "compute",
            "transferTxId": dataset_tx_id,
        },
        "algorithm": {
            "documentId": algo_did,
            "serviceId": "compute",
            "transferTxId": algo_tx_id,
        },
    }
    
    if algo_custom_data:
        payload["algorithm"]["algocustomdata"] = algo_custom_data
    
    resp = requests.post(
        f"{OCEAN_NODE}/api/services/compute",
        json=payload
    )
    return resp.json()


# --- 3. QUERY STATUS ---
def get_job_status(job_id: str, dataset_did: str):
    nonce = int(time.time())
    message = f"{account.address}{dataset_did}{job_id}{nonce}"
    signature = sign_message(message)
    
    resp = requests.get(
        f"{OCEAN_NODE}/api/services/compute",
        params={
            "signature": signature,
            "consumerAddress": account.address,
            "jobId": job_id,
            "documentId": dataset_did,
        }
    )
    return resp.json()


# --- 4. DOWNLOAD RESULT ---
def get_result(job_id: str, index: int = 0):
    nonce = int(time.time())
    message = f"{account.address}{job_id}{index}{nonce}"
    signature = sign_message(message)
    
    resp = requests.get(
        f"{OCEAN_NODE}/api/services/computeResult",
        params={
            "jobId": job_id,
            "index": index,
            "consumerAddress": account.address,
            "nonce": nonce,
            "signature": signature,
        }
    )
    return resp.content  # Result bytes


# --- USAGE ---
if __name__ == "__main__":
    # List environments
    envs = get_environments(CHAIN_ID)
    print(f"Environments: {json.dumps(envs, indent=2)}")
    
    # NOTE: dataset_tx_id and algo_tx_id are the hashes of the
    # on-chain transactions where you approved the datatokens.
    # This requires prior interaction with the smart contracts.
    
    # Start job with consumer parameters
    result = start_compute_job(
        dataset_did="did:op:DATASET_DID",
        algo_did="did:op:ALGO_DID",
        environment_id=envs[0]["id"],
        dataset_tx_id="0x...",     # From the on-chain transaction
        algo_tx_id="0x...",        # From the on-chain transaction
        algo_custom_data={
            "iterations": 100,
            "model": "linear_regression"
        }
    )
    job_id = result[0]["jobId"]
    print(f"Job ID: {job_id}")
    
    # Polling
    while True:
        status = get_job_status(job_id, "did:op:DATASET_DID")
        print(f"Status: {status[0]['statusText']}")
        if status[0]["status"] in (70, 31, 32):
            break
        time.sleep(15)
    
    # Download result
    if status[0]["status"] == 70:
        output = get_result(job_id, 0)
        with open("c2d_result.bin", "wb") as f:
            f.write(output)
        print(f"Result saved ({len(output)} bytes)")
```

---

### 11.5 How Consumer Parameters Flow

```
Your Python program                   Ocean Node                K8s Pod
       │                                  │                        │
       │ algocustomdata: {                │                        │
       │   "iterations": 100,             │                        │
       │   "learning_rate": 0.01          │                        │
       │ }                                │                        │
       │──── POST /api/services/compute──→│                        │
       │                                  │── Creates Job ────────→│
       │                                  │                        │
       │                                  │   Pod-Configuration    │
       │                                  │   writes the JSON to:  │
       │                                  │   /data/inputs/        │
       │                                  │     algoCustomData.json│
       │                                  │                        │
       │                                  │   Your algorithm reads:│
       │                                  │   json.load(open(      │
       │                                  │     "/data/inputs/     │
       │                                  │     algoCustomData.json│
       │                                  │   ))                   │
       │                                  │                        │
       │                                  │   → {"iterations":100, │
       │                                  │      "learning_rate":  │
       │                                  │       0.01}            │
       │                                  │                        │
       │                                  │   Algorithm writes:    │
       │                                  │   /data/outputs/result │
       │                                  │                        │
       │←── GET /computeResult ───────────│←── S3/IPFS ──────────│
       │    (result bytes)                 │                        │
```

**Inside the algorithm, you read the parameters like this:**

```python
import json

# Read consumer parameters sent by your external program
with open("/data/inputs/algoCustomData.json") as f:
    params = json.load(f)

iterations = params.get("iterations", 10)
learning_rate = params.get("learning_rate", 0.001)

print(f"Running with {iterations} iterations, lr={learning_rate}")
```

---

### 11.6 Important Notes for Integration

**About authentication (signatures):**
- Every API call requires a consumer `signature`
- The signature is generated by signing a message with the consumer's private key
- `ocean.py` handles this automatically; with direct HTTP, you must sign with `eth_account`

**About on-chain payment (transferTxId):**
- Before starting a C2D job, you must have **approved and transferred datatokens** on-chain for both the dataset and the algorithm
- `ocean.py` automates this with `pay_for_compute_service()`
- With direct HTTP, you must interact with ERC20 datatoken smart contracts using `web3.py`

**About `algorithm.meta` vs `algorithm.documentId`:**
- If the algorithm is **published as an asset**, use `algorithm.documentId` (the DID)
- If you want to send **raw** code, use `algorithm.meta` with the container metadata
- `algorithm.meta` takes precedence over `documentId` if both are present
- The dataset must have `allowRawAlgorithm: true` to accept raw code

**About consumer parameters:**
- Sent in `algorithm.algocustomdata` in the HTTP API
- Passed as `algorithm_algocustomdata` in `ocean.compute.start()`
- Arrive at the pod in `/data/inputs/algoCustomData.json`
- Your algorithm reads them with `json.load()`

**About order reuse:**
- `pay_for_compute_service()` automatically reuses valid previous orders
- If provider fees expired but the order is still active, it's reused on-chain
- If everything expired, a new order is created (new expense)

---

## Key Links

| Resource | URL |
|----------|-----|
| Ocean Node main repo | https://github.com/oceanprotocol/ocean-node |
| Node Dashboard | https://nodes.oceanprotocol.com/ |
| Environment variables | https://github.com/oceanprotocol/ocean-node/blob/main/docs/env.md |
| Node API | https://github.com/oceanprotocol/ocean-node/blob/develop/API.md |
| C2D V2 docs | https://github.com/oceanprotocol/ocean-node/blob/develop/docs/C2DV2.md |
| Algorithm Docker images | https://github.com/oceanprotocol/algo_dockers |
| C2D examples | https://github.com/oceanprotocol/c2d-examples |
| Official C2D docs | https://docs.oceanprotocol.com/developers/compute-to-data |
| C2D Architecture | https://docs.oceanprotocol.com/developers/compute-to-data/compute-to-data-architecture |
| Datasets & Algorithms | https://docs.oceanprotocol.com/developers/compute-to-data/compute-to-data-datasets-algorithms |
| C2D Workflow | https://docs.oceanprotocol.com/developers/compute-to-data/compute-workflow |
| Writing Algorithms | https://docs.oceanprotocol.com/developers/compute-to-data/compute-to-data-algorithms |
| Compute Options | https://docs.oceanprotocol.com/developers/compute-to-data/compute-options |
| C2D Minikube deployment | https://docs.oceanprotocol.com/infrastructure/compute-to-data-minikube |
| Ocean.py C2D flow | https://github.com/oceanprotocol/ocean.py/blob/main/READMEs/c2d-flow.md |
| Operator Engine | https://github.com/oceanprotocol/operator-engine |
| Operator Service | https://github.com/oceanprotocol/operator-service |
