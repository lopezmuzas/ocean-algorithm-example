# Ocean Node + Anvil + Compute-to-Data (C2D V2) — Guía completa

## Índice

- [Ocean Node + Anvil + Compute-to-Data (C2D V2) — Guía completa](#ocean-node--anvil--compute-to-data-c2d-v2--guía-completa)
  - [Índice](#índice)
  - [Entendiendo C2D: V1 (legacy) vs V2 (actual)](#entendiendo-c2d-v1-legacy-vs-v2-actual)
    - [C2D V1 — Legacy (componentes externos, pre-Ocean Node)](#c2d-v1--legacy-componentes-externos-pre-ocean-node)
    - [C2D V2 — Actual (embebido en Ocean Node)](#c2d-v2--actual-embebido-en-ocean-node)
    - [¿Entonces qué pasa con Operator Service, Operator Engine y PostgreSQL?](#entonces-qué-pasa-con-operator-service-operator-engine-y-postgresql)
    - [¿Y `OPERATOR_SERVICE_URL`?](#y-operator_service_url)
  - [Arquitectura de este setup](#arquitectura-de-este-setup)
  - [Requisitos](#requisitos)
  - [docker-compose.yml](#docker-composeyml)
  - [Archivo .env](#archivo-env)
  - [Inicio rápido](#inicio-rápido)
  - [Cuentas Anvil pre-configuradas](#cuentas-anvil-pre-configuradas)
  - [Servicios y puertos](#servicios-y-puertos)
  - [Flujo C2D V2 paso a paso](#flujo-c2d-v2-paso-a-paso)
  - [Variables de DOCKER\_COMPUTE\_ENVIRONMENTS explicadas](#variables-de-docker_compute_environments-explicadas)
  - [Roadmap de Compute Engines](#roadmap-de-compute-engines)
  - [Ejemplo: Publicar dataset y lanzar C2D](#ejemplo-publicar-dataset-y-lanzar-c2d)
  - [Troubleshooting](#troubleshooting)
    - [Verificar que Anvil funciona](#verificar-que-anvil-funciona)
    - [Ver compute environments C2D](#ver-compute-environments-c2d)
    - [Docker socket no accesible](#docker-socket-no-accesible)
    - [Logs](#logs)
    - [Resetear todo](#resetear-todo)
  - [Referencias](#referencias)

---

## Entendiendo C2D: V1 (legacy) vs V2 (actual)

Esto es lo más importante de entender antes de montar nada. Ocean Protocol ha tenido **dos arquitecturas de Compute-to-Data** y es fácil confundirlas porque la documentación oficial todavía mezcla ambas.

### C2D V1 — Legacy (componentes externos, pre-Ocean Node)

```
┌──────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Provider │───►│ Operator Service │───►│ Operator Engine  │
│ (Python) │    │ (API en K8s)     │    │ (Python en K8s)  │
└──────────┘    └───────┬──────────┘    └───────┬──────────┘
                        │                       │
                 ┌──────▼──────┐         ┌──────▼──────┐
                 │ PostgreSQL  │         │ K8s Cluster │
                 └─────────────┘         │ pods C2D    │
                                         └─────────────┘
```

- **Todos componentes separados**: Provider (Python), Operator Service, Operator Engine, PostgreSQL.
- Cada pieza se despliega independientemente.
- Operator Service corre **dentro** de Kubernetes.
- Operator Engine también corre **dentro** de K8s y orquesta pods aislados.
- La comunicación es: Provider → `OPERATOR_SERVICE_URL` → Operator Service → K8s API → Pods.
- **Esta arquitectura es legacy.** El Provider Python ya fue reemplazado por Ocean Node.

**Variable asociada:** `OPERATOR_SERVICE_URL`
**Estado:** Puente de compatibilidad con V1, será reemplazado.

### C2D V2 — Actual (embebido en Ocean Node)

```
┌─────────────────────────────────────────────────┐
│                   Ocean Node                     │
│                                                  │
│  ┌──────────┐    ┌────────────────────────────┐ │
│  │ Provider │    │  C2D V2 Orchestrator       │ │
│  │ (HTTP)   │───►│                            │ │
│  └──────────┘    │  ┌──────────────────────┐  │ │
│                  │  │ Docker Engine ✅      │  │ │
│  ┌──────────┐    │  │ (DOCKER_COMPUTE_ENV) │  │ │
│  │ Indexer  │    │  └──────────────────────┘  │ │
│  └──────────┘    │  ┌──────────────────────┐  │ │
│                  │  │ K8s Engine (roadmap)  │  │ │
│                  │  └──────────────────────┘  │ │
│                  │  ┌──────────────────────┐  │ │
│                  │  │ Bacalhau, iExec (TBD)│  │ │
│                  │  └──────────────────────┘  │ │
│                  └────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

- **Todo embebido dentro de ocean-node.** No hay componentes externos.
- Diseño modular: el orchestrator soporta múltiples **compute engines** conectables.
- El motor de compute Docker está **implementado y funcional hoy**.
- El motor K8s nativo (que reemplazará a Operator Service/Engine) está **en roadmap**.
- En el futuro se podrán integrar engines externos (Bacalhau, iExec, etc.).
- Ocean Node gestiona directamente el ciclo de vida de los containers/jobs.

**Variable asociada:** `DOCKER_COMPUTE_ENVIRONMENTS`
**Estado:** Funcional, es lo que se usa actualmente.

### ¿Entonces qué pasa con Operator Service, Operator Engine y PostgreSQL?

| Componente | ¿Se necesita en C2D V2? | Explicación |
|------------|------------------------|-------------|
| **Operator Service** | ❌ No | Era el intermediario entre Provider y K8s. En V2, ocean-node orquesta directamente. |
| **Operator Engine** | ❌ No | Era el worker de K8s. En V2, ocean-node crea/destruye containers directamente. |
| **PostgreSQL** | ❌ No | Era el almacén de estado de jobs. En V2, ocean-node usa Typesense. |
| **Provider (Python)** | ❌ No | Reemplazado completamente por Ocean Node. |
| **Aquarius** | ❌ No | Reemplazado por el Indexer embebido en Ocean Node. |

**Todo está dentro de Ocean Node.** Esa es la filosofía de la nueva arquitectura.

### ¿Y `OPERATOR_SERVICE_URL`?

Existe como **puente de compatibilidad** para quienes aún tienen la infraestructura V1 corriendo. Si lo configuras, ocean-node puede enviar jobs al sistema viejo. Pero no es la dirección del proyecto — será reemplazado cuando el engine K8s nativo de V2 esté completo.

---

## Arquitectura de este setup

Este docker-compose implementa C2D V2 con el Docker Engine nativo. Son **4 servicios**, nada más:

```
┌────────────────────────────────────────────────────────────────┐
│                       Tu máquina local                          │
│                                                                  │
│  ┌──────────┐    ┌─────────────────────────┐   ┌─────────────┐ │
│  │  Anvil   │◄──►│      Ocean Node         │◄─►│  TypeSense  │ │
│  │  :8545   │    │  :8000 (HTTP API)       │   │  :8108      │ │
│  │  chain   │    │  :9000-9003 (P2P)       │   │ (Indexer DB)│ │
│  │  8996    │    │                         │   └─────────────┘ │
│  └──────────┘    │  ┌───────────────────┐  │                    │
│                  │  │ C2D V2 Docker     │  │   ┌─────────────┐ │
│                  │  │ Engine            │  │◄─►│    IPFS     │ │
│                  │  │                   │  │   │  :5001 API  │ │
│                  │  │ docker.sock ──────┼──┼──►│  :8080 GW   │ │
│                  │  │ crea containers   │  │   └─────────────┘ │
│                  │  │ de compute        │  │                    │
│                  │  └───────────────────┘  │                    │
│                  └─────────────────────────┘                    │
└────────────────────────────────────────────────────────────────┘
```

| # | Servicio | Imagen | Función |
|---|----------|--------|---------|
| 1 | **Anvil** | `ghcr.io/foundry-rs/foundry` | Blockchain local, chain-id 8996, block-time 2s |
| 2 | **TypeSense** | `typesense/typesense:26.0` | BD off-chain para el Indexer (cache metadatos) |
| 3 | **IPFS** | `ipfs/kubo` | Almacenamiento: assets, resultados C2D, logs |
| 4 | **Ocean Node** | `oceanprotocol/ocean-node` | Provider + Indexer + C2D V2 Docker Engine |

---

## Requisitos

| Herramienta    | Versión mínima | Notas |
|----------------|----------------|-------|
| Docker Engine  | 24+            | Con Docker socket accesible |
| Docker Compose | v2             | Plugin de Docker (`docker compose`) |
| RAM            | 8 GB+          | Para los 4 servicios + containers C2D |
| Disco          | 20 GB libres   | Imágenes Docker + datos IPFS/Typesense |

No necesitas Node.js, Kubernetes, Minikube ni nada más.

---

## docker-compose.yml

```yaml
services:

  # 1. ANVIL — Blockchain local (Foundry)
  anvil:
    image: ghcr.io/foundry-rs/foundry:latest
    container_name: ocean-anvil
    entrypoint: ["anvil"]
    command:
      - --host=0.0.0.0
      - --port=8545
      - --chain-id=8996
      - --block-time=2
      - --accounts=10
      - --balance=10000
      - --gas-limit=30000000
      - --code-size-limit=300000
    ports:
      - "8545:8545"
    healthcheck:
      test: ["CMD-SHELL", "cast block-number --rpc-url http://localhost:8545 || exit 1"]
      interval: 5s
      timeout: 3s
      retries: 20
      start_period: 5s
    restart: unless-stopped
    networks:
      - ocean-network

  # 2. TYPESENSE — Base de datos off-chain para el Indexer
  typesense:
    image: typesense/typesense:26.0
    container_name: ocean-typesense
    ports:
      - "8108:8108"
    volumes:
      - typesense-data:/data
    command: >
      --data-dir /data
      --api-key=${TYPESENSE_API_KEY:-xyz}
      --enable-cors
    healthcheck:
      test: ["CMD", "curl", "-sf", "http://localhost:8108/health"]
      interval: 5s
      timeout: 3s
      retries: 20
      start_period: 5s
    restart: unless-stopped
    networks:
      - ocean-network

  # 3. IPFS — Almacenamiento descentralizado
  ipfs:
    image: ipfs/kubo:latest
    container_name: ocean-ipfs
    ports:
      - "5001:5001"
      - "8080:8080"
    environment:
      - IPFS_PROFILE=server
    volumes:
      - ipfs-data:/data/ipfs
    healthcheck:
      test: ["CMD-SHELL", "ipfs dag stat /ipfs/QmUNLLsPACCz1vLxQVkXqqLX5R1X345qqfHbsf67hvA3Nn || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 15s
    restart: unless-stopped
    networks:
      - ocean-network

  # 4. OCEAN NODE — Provider + Indexer + C2D V2 Docker Engine
  ocean-node:
    image: oceanprotocol/ocean-node:latest
    pull_policy: always
    container_name: ocean-node
    restart: on-failure
    ports:
      - "8000:8000"
      - "9000:9000"
      - "9001:9001"
      - "9002:9002"
      - "9003:9003"
    environment:
      PRIVATE_KEY: "${PRIVATE_KEY:-0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d}"
      RPCS: >
        {
          "8996": {
            "rpc": "http://anvil:8545",
            "fallbackRPCs": ["http://anvil:8545"],
            "chainId": 8996,
            "network": "development",
            "chunkSize": 100
          }
        }
      DB_URL: "http://typesense:8108/?apiKey=${TYPESENSE_API_KEY:-xyz}"
      IPFS_GATEWAY: "http://ipfs:8080/"
      INDEXER_NETWORKS: '["8996"]'
      INDEXER_INTERVAL: "5000"
      HTTP_API_PORT: "8000"
      P2P_ENABLE_IPV4: "true"
      P2P_ipV4BindAddress: "0.0.0.0"
      P2P_ipV4BindTcpPort: "9000"
      P2P_ipV4BindWsPort: "9001"
      P2P_ipV6BindTcpPort: "9002"
      P2P_ipV6BindWsPort: "9003"
      P2P_ANNOUNCE_PRIVATE: "true"
      INTERFACES: '["HTTP","P2P"]'
      ALLOWED_ADMINS: '["${ADMIN_ADDRESS:-0x70997970C51812dc3A010C7d01b50e0d17dc79C8}"]'
      NODE_ENV: "development"
      LOG_LEVEL: "${LOG_LEVEL:-debug}"
      FEE_TOKENS: >
        {
          "8996": {
            "Ocean": "0x0000000000000000000000000000000000000000"
          }
        }
      FEE_AMOUNT: '{"amount":0,"unit":"MB"}'

      # C2D V2 — Docker Compute Engine
      DOCKER_COMPUTE_ENVIRONMENTS: >
        [
          {
            "socketPath": "/var/run/docker.sock",
            "resources": [
              { "id": "disk", "total": 5368709120 },
              { "id": "cpu", "total": 4 },
              { "id": "ram", "total": 8589934592 }
            ],
            "storageExpiry": 604800,
            "maxJobDuration": 3600,
            "fees": {
              "8996": [
                {
                  "feeToken": "0x0000000000000000000000000000000000000000",
                  "prices": [
                    { "id": "cpu", "price": 0 },
                    { "id": "ram", "price": 0 },
                    { "id": "disk", "price": 0 }
                  ]
                }
              ]
            },
            "free": {
              "maxJobDuration": 300,
              "maxJobs": 3,
              "resources": [
                { "id": "cpu", "max": 2 },
                { "id": "ram", "max": 4294967296 },
                { "id": "disk", "max": 2147483648 }
              ]
            }
          }
        ]

      DOCKER_SOCKET_PATH: "/var/run/docker.sock"
      CRON_CLEANUP_C2D_STORAGE: "*/5 * * * *"

    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on:
      anvil:
        condition: service_healthy
      typesense:
        condition: service_healthy
      ipfs:
        condition: service_healthy
    extra_hosts:
      - "host.docker.internal:host-gateway"
    networks:
      - ocean-network

volumes:
  typesense-data:
  ipfs-data:

networks:
  ocean-network:
    driver: bridge
```

---

## Archivo .env

```bash
# Clave privada del nodo (Anvil Account #1)
PRIVATE_KEY=0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d

# Dirección admin del nodo (Anvil Account #1 address)
ADMIN_ADDRESS=0x70997970C51812dc3A010C7d01b50e0d17dc79C8

# Typesense API Key
TYPESENSE_API_KEY=xyz

# Nivel de log (debug | info | warn | error)
LOG_LEVEL=debug
```

> ⚠️ Las claves privadas son las cuentas públicas de Anvil. **Nunca las uses en mainnet.**

---

## Inicio rápido

```bash
# Levantar
docker compose up -d

# Verificar servicios
curl http://localhost:8000              # Ocean Node
curl http://localhost:8108/health       # TypeSense
curl http://localhost:8080              # IPFS Gateway

# Ver compute environments C2D disponibles
curl http://localhost:8000/api/services/computeEnvironments?chainId=8996

# Dashboard
open http://localhost:8000/controlpanel/

# Logs
docker compose logs -f ocean-node

# Detener
docker compose down -v
```

---

## Cuentas Anvil pre-configuradas

| Rol       | Account # | Dirección                                    | Clave privada |
|-----------|-----------|----------------------------------------------|---------------|
| Deployer  | #0        | `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266` | `0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80` |
| Node      | #1        | `0x70997970C51812dc3A010C7d01b50e0d17dc79C8` | `0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d` |
| Consumer  | #2        | `0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC` | `0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a` |
| Publisher | #3        | `0x90F79bf6EB2c4f870365E785982E1f101E93b906` | `0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6` |

---

## Servicios y puertos

| Servicio        | Puerto    | URL                          |
|-----------------|-----------|------------------------------|
| Anvil RPC       | 8545      | `http://localhost:8545`      |
| Ocean Node HTTP | 8000      | `http://localhost:8000`      |
| Ocean Node P2P  | 9000-9003 | —                            |
| TypeSense       | 8108      | `http://localhost:8108`      |
| IPFS API        | 5001      | `http://localhost:5001`      |
| IPFS Gateway    | 8080      | `http://localhost:8080`      |

---

## Flujo C2D V2 paso a paso

Todo ocurre dentro de Ocean Node. No hay llamadas a servicios externos.

```
Consumer                    Ocean Node                       Docker
   │                            │                               │
   │  1. POST /api/services/    │                               │
   │     compute (start job)    │                               │
   │───────────────────────────►│                               │
   │                            │                               │
   │                            │  2. Valida permisos on-chain  │
   │                            │     (Anvil :8545)             │
   │                            │                               │
   │                            │  3. docker create container   │
   │                            │     (via docker.sock)         │
   │                            │──────────────────────────────►│
   │                            │                               │
   │                            │               4a. Descarga dataset desde IPFS
   │                            │               4b. Descarga algoritmo
   │                            │               4c. Ejecuta algoritmo
   │                            │               4d. Genera output + logs
   │                            │                               │
   │                            │  5. Container finished        │
   │                            │◄──────────────────────────────│
   │                            │                               │
   │                            │  6. Sube resultados a IPFS    │
   │                            │                               │
   │                            │  7. docker rm container       │
   │                            │──────────────────────────────►│
   │                            │                               │
   │  8. GET /api/services/     │                               │
   │     computeResult          │                               │
   │───────────────────────────►│                               │
   │                            │                               │
   │  9. Resultados (IPFS CID)  │                               │
   │◄───────────────────────────│                               │
```

---

## Variables de DOCKER_COMPUTE_ENVIRONMENTS explicadas

```jsonc
[
  {
    // Ruta al Docker socket dentro del container ocean-node
    "socketPath": "/var/run/docker.sock",

    // Recursos TOTALES disponibles para C2D en esta máquina
    "resources": [
      { "id": "disk", "total": 5368709120 },   // 5 GB
      { "id": "cpu",  "total": 4 },            // 4 cores
      { "id": "ram",  "total": 8589934592 }    // 8 GB
    ],

    // Cuánto tiempo se guardan los resultados (segundos)
    "storageExpiry": 604800,    // 7 días

    // Duración máxima de un job pagado (segundos)
    "maxJobDuration": 3600,     // 1 hora

    // Precios por chain (0 = gratis)
    "fees": {
      "8996": [                 // chain-id de Anvil
        {
          "feeToken": "0x000...000",  // dirección del token de pago
          "prices": [
            { "id": "cpu",  "price": 0 },
            { "id": "ram",  "price": 0 },
            { "id": "disk", "price": 0 }
          ]
        }
      ]
    },

    // Entorno GRATUITO (para desarrollo/testing)
    "free": {
      "maxJobDuration": 300,    // 5 minutos máximo
      "maxJobs": 3,             // 3 jobs simultáneos máximo
      "resources": [
        { "id": "cpu",  "max": 2 },            // 2 cores por job
        { "id": "ram",  "max": 4294967296 },   // 4 GB por job
        { "id": "disk", "max": 2147483648 }    // 2 GB por job
      ]
    }
  }
]
```

---

## Roadmap de Compute Engines

La arquitectura C2D V2 de Ocean Node es modular. Los engines se conectan al orchestrator embebido:

| Engine | Variable | Estado |
|--------|----------|--------|
| **Docker** | `DOCKER_COMPUTE_ENVIRONMENTS` | ✅ Funcional |
| **Kubernetes** (nativo) | TBD | 🚧 En desarrollo |
| **Bacalhau** | TBD | 📋 Planificado |
| **iExec** | TBD | 📋 Planificado |
| **V1 bridge** | `OPERATOR_SERVICE_URL` | ⚠️ Compatibilidad legacy |

Cuando el engine K8s nativo esté listo, se configurará con una variable similar a `DOCKER_COMPUTE_ENVIRONMENTS` pero apuntando a un cluster K8s — sin necesidad de Operator Service ni Operator Engine.

---

## Ejemplo: Publicar dataset y lanzar C2D

```javascript
const { Aquarius, Provider, Datatoken, Config } = require('@oceanprotocol/lib');

const config = {
  chainId: 8996,
  nodeUri: 'http://localhost:8545',
  providerUri: 'http://localhost:8000',
  metadataCacheUri: 'http://localhost:8000',
};

// 1. Publicar dataset con servicio compute
// 2. Publicar algoritmo
// 3. Consultar environments disponibles:
//    GET http://localhost:8000/api/services/computeEnvironments?chainId=8996
// 4. Iniciar job de compute
// 5. Ocean Node crea container Docker, ejecuta algo, sube resultados a IPFS
// 6. Descargar resultados
```

---

## Troubleshooting

### Verificar que Anvil funciona

```bash
docker exec ocean-node curl -s http://anvil:8545 \
  -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

### Ver compute environments C2D

```bash
curl -s http://localhost:8000/api/services/computeEnvironments?chainId=8996 | jq
```

### Docker socket no accesible

```bash
# Verificar que el socket existe y tiene permisos
ls -la /var/run/docker.sock

# Si da error de permisos, añadir tu usuario al grupo docker
sudo usermod -aG docker $USER
```

### Logs

```bash
docker compose logs -f ocean-node     # Nodo principal
docker compose logs -f ocean-anvil    # Blockchain
docker compose logs -f ocean-typesense # Base de datos
docker compose logs -f ocean-ipfs     # IPFS
```

### Resetear todo

```bash
docker compose down -v
docker volume prune -f
docker compose up -d
```

---

## Referencias

| Recurso | URL |
|---------|-----|
| Ocean Node repo | https://github.com/oceanprotocol/ocean-node |
| Variables de entorno | https://github.com/oceanprotocol/ocean-node/blob/main/docs/env.md |
| Docker deployment | https://github.com/oceanprotocol/ocean-node/blob/main/docs/dockerDeployment.md |
| C2D V2 architecture | https://github.com/oceanprotocol/ocean-node/blob/develop/docs/C2DV2.md |
| Node architecture | https://docs.oceanprotocol.com/developers/ocean-node/node-architecture |
| Ocean Node docs | https://docs.oceanprotocol.com/developers/ocean-node |
