# Ocean Protocol: Guía Completa — Ocean Node + Compute-to-Data

---

## PARTE 1: ¿Qué es un Ocean Node?

Ocean Nodes son el componente central del stack de Ocean Protocol. Un **único monorepo** que reemplaza los tres componentes anteriores (Provider, Aquarius y Subgraph), simplificando radicalmente el despliegue: **todo corre con un solo comando**.

**Funciones que integra:**

- **Provider** → Accede a datos, verifica permisos on-chain, encripta/desencripta URLs, hace streaming de datos, conecta con C2D.
- **Aquarius (ahora "Indexer")** → Cachea metadatos on-chain en una base de datos Typesense, expone API REST.
- **Subgraph** → Indexa eventos de smart contracts en tiempo real, proporciona API de consultas.

**Tecnología clave:** libp2p para comunicación peer-to-peer, arquitectura modular por capas (red, componentes, orquestación).

---

## PARTE 2: Cómo Crear un Ocean Node

### Requisitos Mínimos

| Recurso | Mínimo |
|---------|--------|
| CPU | 1 vCPU |
| RAM | 2 GB |
| Almacenamiento | 4 GB |
| SO | Ubuntu LTS (recomendado), macOS, Windows con WSL2 |
| Software | Docker Engine + Docker Compose |

### Despliegue Rápido con Docker (Método Recomendado)

```bash
# 1. Descargar el script de quickstart
curl -O https://raw.githubusercontent.com/oceanprotocol/ocean-node/main/scripts/ocean-node-quickstart.sh

# 2. Dar permisos y ejecutar
chmod +x ocean-node-quickstart.sh
./ocean-node-quickstart.sh
```

El script te guiará interactivamente pidiendo:

1. **Private Key** — Puedes generar una nueva o usar una existente (formato `0x...`)
2. **Wallet address** — Cuenta admin del nodo
3. **HTTP_API_PORT** — Por defecto `8000`
4. **P2P Ports** — Por defecto `9000-9003` (TCP IPv4, WS IPv4, TCP IPv6, WS IPv6)
5. **IP pública o FQDN** — Donde será accesible tu nodo

Genera automáticamente un `docker-compose.yml`.

```bash
# 3. Levantar el nodo
docker-compose up -d

# 4. Verificar que está corriendo
docker ps
```

### Configuración Generada (docker-compose.yml)

El archivo incluye dos servicios:

- **ocean-node** — Imagen `oceanprotocol/ocean-node:latest`, puertos 8000, 9000-9003
- **typesense** — Imagen `typesense/typesense:26.0`, puerto 8108 (base de datos del Indexer)

Variables de entorno clave:

| Variable | Descripción |
|----------|-------------|
| `PRIVATE_KEY` | Clave privada del nodo (obligatoria, con prefijo `0x`) |
| `RPCS` | JSON con configuración de RPCs para cada cadena soportada |
| `DB_URL` | URL de la base Typesense |
| `P2P_ANNOUNCE_ADDRESS` | IP pública para anunciarse en la red P2P |

> **Referencia completa de variables:** https://github.com/oceanprotocol/ocean-node/blob/main/docs/env.md

### Despliegue Alternativo (Desde Código Fuente)

```bash
git clone https://github.com/oceanprotocol/ocean-node.git
cd ocean-node
nvm use             # Usar versión de Node.js correcta
npm install
npm run build

# Configurar variables de entorno
# Ejecutar el helper script para generar .env

npm run start
# Panel de control disponible en http://localhost:8000/controlpanel/
```

### Requisitos para ser Elegible a Incentivos

Para recibir recompensas del Ocean Protocol Foundation:

1. **IP pública** — El nodo debe ser accesible desde Internet
2. **Puertos expuestos** — Tanto HTTP API como puertos P2P deben estar abiertos
3. **Verificar accesibilidad** — Desde otro dispositivo: `telnet {tu_ip} {P2P_port}`
4. **Port forwarding** — Configurar en tu router si estás detrás de NAT
5. **Verificar en Dashboard** — https://nodes.oceanprotocol.com/ → buscar tu peerID → indicador verde

### Actualización del Nodo

```bash
chmod +x scripts/ocean-node-update.sh
./scripts/ocean-node-update.sh
```

### Múltiples Nodos

Se pueden correr múltiples nodos en la misma IP, cada uno en puertos diferentes. No hay límite de nodos.

---

## PARTE 3: Compute-to-Data (C2D) — Fundamentos

C2D permite **monetizar datos sensibles sin exponerlos**. En lugar de compartir datos crudos, se ofrece acceso computacional: los algoritmos van a los datos, no al revés. Esto resuelve el trade-off entre aprovechar datos privados y mitigar riesgos de exposición.

**Caso de uso típico:** Si posees registros médicos sensibles, puedes permitir que un algoritmo calcule la edad media de los pacientes sin revelar ningún otro detalle individual.

---

## PARTE 4: Arquitectura C2D en Detalle

### Actores y Componentes

| Componente | Rol |
|------------|-----|
| **Consumer** | Usuario final que inicia el job C2D seleccionando dataset + algoritmo |
| **Provider (Ocean Node)** | Interfaz principal: valida permisos, verifica datatokens on-chain, coordina con Operator Service |
| **Operator Service** | Microservicio que gestiona la cola de workflows y se comunica con K8s |
| **Operator Engine** | Agente backend que orquesta la infraestructura K8s, crea/destruye pods |
| **Pod-Configuration** | Script Node.js que descarga datasets y algoritmos al iniciar un job |
| **Pod de Ejecución (Algorithm Pod)** | Contenedor aislado de K8s donde corre el algoritmo |
| **Pod-Publishing** | Utilidad CLI que sube resultados a AWS S3 o IPFS |
| **Kubernetes** | Cluster K8s donde se ejecutan los pods aislados |

### Pre-condiciones para C2D

Antes de que el flujo pueda comenzar:

1. El Asset DDO del dataset debe tener un servicio de tipo `compute`
2. El servicio compute debe permitir que algoritmos se ejecuten sobre él
3. El DDO debe especificar un endpoint de Ocean Provider expuesto por el Publisher

### Flujo Detallado Paso a Paso

#### Fase 1: Inicio del Job

1. El consumidor selecciona un entorno de compute preferido de la lista del Provider
2. Inicia un job eligiendo un par dataset-algoritmo
3. El Provider verifica las órdenes en la blockchain (datatokens para dataset, algoritmo y fees de compute)
4. Si son válidas, el Provider llama a `start(did, algorithm, additionalDIDs)` y devuelve un **job ID** único al consumidor
5. El Provider informa al Operator Service del nuevo job
6. El Operator Service lo añade a su cola local de jobs

#### Fase 2: Creación del Cluster K8s y Volúmenes

7. El Operator Engine periódicamente consulta al Operator Service para ver si hay jobs pendientes
8. Si hay recursos disponibles, solicita la lista de jobs
9. Se crean **volúmenes en K8s** para el nuevo job
10. Los volúmenes se asignan al pod
11. El Operator Engine inicia el **pod-configuration**

#### Fase 3: Carga de Datasets y Algoritmos

12. Pod-configuration solicita los datasets y el algoritmo a sus respectivos Providers
13. Los archivos se descargan vía el Provider (nunca URLs directas)
14. Pod-configuration escribe los datasets en el volumen del job en las rutas correctas:
    - Datasets → `/data/inputs/{DID}/{index}` (archivos nombrados por índice: 0, 1, 2...)
    - Algoritmo → `/data/transformations/algorithm` (primer archivo), luego indexados 1 a X
    - DDOs → `/data/ddos/` (archivos JSON con la estructura DDO)
15. Si hay algún fallo en el aprovisionamiento, el script actualiza el estado del job en PostgreSQL y registra los errores
16. Pod-configuration señala al Operator Engine que está listo

#### Fase 4: Ejecución del Algoritmo

17. El Operator Engine lanza el **algorithm pod** en K8s con el volumen montado (datasets + algoritmo)
18. K8s ejecuta el pod del algoritmo
19. El Operator Engine **monitoriza** el algoritmo y lo detiene si excede el tiempo límite del entorno elegido
20. Cuando hay resultados, el Operator Engine inicia **pod-publishing**
21. Pod-publishing sube resultados, logs y admin logs al volumen de output (S3 o IPFS)
22. Notifica al Operator Engine que la subida fue exitosa

#### Fase 5: Limpieza

23. El Operator Engine **elimina los volúmenes K8s**
24. K8s borra todos los volúmenes usados
25. El Operator Engine finaliza el job y notifica al Operator Service

#### Fase 6: Recuperación de Resultados

26. El consumidor llama a `getJobDetails(jobID)` al Provider
27. El Provider consulta al Operator Service
28. Con los detalles, el consumidor puede descargar los resultados del job ejecutado
29. Los resultados se sirven desde el volumen de output (S3/IPFS) vía el Provider

### Componentes Internos en Profundidad

#### Operator Service

Responsabilidades principales:
- Exponer API HTTP para endpoints de acceso y compute
- Interactuar con la infraestructura (cloud/on-premise) usando credenciales del Publisher
- Iniciar/detener/ejecutar instancias de compute con los algoritmos de usuarios
- Recuperar logs de ejecuciones
- Registrar nuevos compute jobs en K8s
- Listar jobs actuales y obtener resultados detallados por job
- Detener un job en ejecución

> **No almacena estado:** Todo se guarda directamente en el cluster K8s.

Puede integrarse desde el Ocean Provider o llamarse independientemente.

#### Operator Engine

Responsabilidades:
- Orquestar el flujo de ejecución completo
- Iniciar el pod de configuración (descarga de dependencias)
- Iniciar el pod del algoritmo
- Iniciar el pod de publicación (nuevos assets al network)
- Monitorizar tiempos de ejecución

**Variables de configuración del Operator Engine:**

| Variable | Descripción |
|----------|-------------|
| `OPERATOR_PRIVATE_KEY` | Clave privada única del operador (futuro: cuenta para recibir fees) |
| `IPFS_OUTPUT` | Gateway IPFS para subir datos de output |
| `IPFS_OUTPUT_PREFIX` | Prefijo para URLs de IPFS |
| `IPFS_ADMINLOGS` | Gateway para admin logs |
| `AWS_ACCESS_KEY_ID` | Credenciales S3 para buckets de logs y output |
| `AWS_SECRET_ACCESS_KEY` | Credenciales S3 |
| `BUCKET_OUTPUT` | Bucket S3 para output del algoritmo |
| `BUCKET_ADMINLOGS` | Bucket S3 para admin logs |
| `STORAGE_CLASS` | Clase de almacenamiento K8s a usar |
| `NOTIFY_START_URL` | URL callback al iniciar un job |
| `NOTIFY_STOP_URL` | URL callback al terminar un job |
| `MAX_JOB_DURATION` | Duración máxima en horas. `0` = sin expiración |
| `SERVICE_ACCOUNT` | Cuenta K8s para correr pods (default: `default`) |
| `IPFS_TYPE` | `CLUSTER` o `CLIENT` (default: CLIENT) |

#### Pod-Configuration

Script Node.js que al iniciarse:
1. **Descarga datasets** → `/data/inputs/{DID}/{index}`
2. **Descarga algoritmo** → `/data/transformations/algorithm`
3. **Descarga DDOs** → `/data/ddos/`
4. **Gestión de errores**: Actualiza estado en PostgreSQL si falla
5. **Señal de finalización**: Notifica al Operator Engine para iniciar el algorithm pod

#### Pod-Publishing

Tres áreas funcionales:
1. **Interacción con Operator Service**: Sube outputs a S3 o IPFS, logea pasos, actualiza PostgreSQL
2. **Rol en el Publishing Pod**: Publica nuevos assets creados en la red Ocean Protocol
3. **Gestión de Outputs**: Almacena resultados según configuración (IPFS o AWS S3)

> No proporciona almacenamiento propio; todo el estado vive en K8s o en la solución de datos elegida.

---

## PARTE 5: Datasets y Algoritmos — Clasificación y Permisos

### Tipos de Algoritmos

Los algoritmos en C2D se clasifican por su accesibilidad configurando `attributes.main.type` en el DDO:

| Tipo | Significado |
|------|-------------|
| `"access"` | **Público.** Se puede descargar con el datatoken apropiado |
| `"compute"` | **Privado.** Solo disponible para ejecutar como parte de un job C2D, sin posibilidad de descarga. Debe publicarse en el mismo Ocean Provider que el dataset objetivo |

### Niveles de Permisos para Datasets

Por **defecto, todos los datasets se publican como privados** (ningún algoritmo permitido). Esto previene fuga de datos por algoritmos maliciosos. El publicador puede configurar:

| Configuración | Comportamiento |
|---------------|----------------|
| **Permitir algoritmos específicos** | Solo los algoritmos referenciados por DID pueden ejecutarse |
| **Permitir todos los publicados** | Cualquier algoritmo publicado en la red puede ejecutarse (usando wildcard `*`) |
| **Permitir algoritmos raw** | Código raw puede ejecutarse (mayor riesgo de escape de datos) |
| **Permitir por publisher** | Solo algoritmos de publishers específicos (por address) |

### Configuración de Permisos en el DDO (Compute Options)

Un asset de tipo `compute` incluye un objeto `compute` adicional en su servicio:

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

### Atributos del Objeto Compute

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `allowRawAlgorithm`* | boolean | Si `true`, se acepta texto raw. Útil para drag & drop pero riesgo de escape. **Default: `false`** |
| `allowNetworkAccess`* | boolean | Si `true`, el job tendrá acceso a red |
| `publisherTrustedAlgorithmPublishers`* | string[] | Addresses de publishers de confianza. Si contiene `*`, todos permitidos. Si vacío o no definido, acceso restringido |
| `publisherTrustedAlgorithms`* | object[] | Array de algoritmos de confianza. Si contiene `*`, todos los algoritmos publicados permitidos. Si vacío o no definido, **ninguno permitido** |

### Trusted Algorithms: Verificación de Integridad

Cada entrada en `publisherTrustedAlgorithms` incluye:

| Campo | Descripción |
|-------|-------------|
| `did` | DID del algoritmo de confianza |
| `filesChecksum` | Hash de los archivos del algoritmo. Se obtiene llamando al Provider FileInfoEndpoint con `withChecksum=True`. Si hay múltiples archivos, es la concatenación de checksums |
| `containerSectionChecksum` | Hash calculado como: `sha256(entrypoint + checksum_de_la_imagen_docker)` |

Esto garantiza que el algoritmo no ha sido modificado después de ser autorizado.

---

## PARTE 6: Escribir Algoritmos para C2D

### Componentes de un Algoritmo

Todo algoritmo C2D tiene tres partes:

1. **Código del algoritmo** — Tu lógica (Python, Node.js, R, Julia, etc.)
2. **Imagen Docker** — Entorno de ejecución (imagen base + tag)
3. **Entry Point** — Comando que inicia la ejecución

### Objeto Environment en los Metadatos

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

- `$ALGO` es una **macro** que se reemplaza automáticamente con la ruta donde se descargó tu código dentro del pod.
- `image` + `tag` definen el contenedor Docker.
- `checksum` es el digest SHA256 de la imagen Docker.
- `entrypoint` define tu entry point. Si tienes múltiples versiones de Python, especifica la correcta: `python3.6 $ALGO`.

### Metadatos Completos del Algoritmo (DDO)

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

### Imágenes Docker Disponibles

Imágenes estándar de Ocean: https://github.com/oceanprotocol/algo_dockers

| Entorno | image | tag | entrypoint |
|---------|-------|-----|------------|
| Python 3.9 | `python` | `3.9.4-alpine3.13` | `python3.9 $ALGO` |
| Node.js 14 | `node` | `14` | `node $ALGO` |
| Node.js 12 | `node` | `12` | `node $ALGO` |
| Python + SQL | `oceanprotocol/algo_dockers` | `python-sql` | `python3.6 $ALGO` |

**¿Necesitas dependencias custom?** Crea tu propia imagen Docker:

```dockerfile
FROM python:3.9.4-alpine3.13
RUN pip install pandas numpy scikit-learn matplotlib
# La imagen debe soportar "pip" o el gestor de paquetes de tu lenguaje
```

Publícala en DockerHub y referencia la imagen/tag en tus metadatos.

### Almacenamiento de Datos en el Pod (Volúmenes)

| Ruta | Permisos | Contenido |
|------|----------|-----------|
| `/data/inputs` | Lectura | Datasets de entrada. Estructura: `/data/inputs/{did}/{service_id}`. Archivos nombrados por índice (0, 1, 2...) |
| `/data/ddos` | Lectura | Archivos JSON con la estructura DDO completa de cada asset (dataset + algoritmo) |
| `/data/outputs` | Lectura/Escritura | **Aquí escribes tus resultados.** Se suben a S3/IPFS y se devuelven al consumidor |
| `/data/logs/` | Lectura/Escritura | Todo output del algoritmo (print, console.log, etc.) se guarda aquí y se envía al consumidor |
| `/data/transformations/` | Lectura | Donde se almacena el código del algoritmo descargado |
| `/data/inputs/algoCustomData.json` | Lectura | Parámetros custom del consumidor (si se definieron `consumerParameters`) |

> **Nota importante:** Cuando usas Providers o Metadata Caches locales, los DDOs pueden no transferirse correctamente a C2D, pero los inputs sí están disponibles. Si tu algoritmo depende del contenido del DDO JSON, asegúrate de usar un Provider y Metadata Cache públicos.

### Variables de Entorno Disponibles en el Pod

| Variable | Contenido |
|----------|-----------|
| `DIDS` | Array JSON con los DIDs de los datasets de entrada |
| `TRANSFORMATION_DID` | DID del algoritmo que se está ejecutando |

### Consumer Parameters (Parámetros del Consumidor)

Permiten que el publicador del dataset o algoritmo defina **inputs que el comprador debe rellenar** antes de ejecutar el job.

**Tipos de parámetros soportados:**

| Tipo | Descripción |
|------|-------------|
| `text` | Campo de texto libre |
| `number` | Campo numérico |
| `boolean` | Checkbox true/false |
| `select` | Lista desplegable con opciones predefinidas |

**Estructura de cada parámetro:**

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `name` | string | Sí | Nombre del parámetro (clave en el JSON) |
| `type` | string | Sí | text, number, boolean, select |
| `label` | string | Sí | Etiqueta visible al usuario |
| `required` | boolean | Sí | Si es obligatorio |
| `description` | string | Sí | Descripción del campo |
| `default` | string/number/boolean | Sí | Valor por defecto. Para select: string key de la opción |
| `options` | object[] | Solo para select | Lista de opciones `{clave: valor}` |

**Ejemplo completo de definición:**

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

**Archivo JSON resultante en el pod** (`/data/inputs/algoCustomData.json`):

```json
{
  "hometown": "São Paulo",
  "age": 10,
  "developer": true,
  "languagePreference": "nodejs"
}
```

**Caso de uso para datasets:** Si el publisher necesita saber el intervalo de muestreo, define un parámetro `sampling`. El valor se añade como query parameter a la URL del dataset: `https://example.com/mydata?sampling=10`.

**Caso de uso para algoritmos:** Un algoritmo que necesita saber el número de iteraciones define un campo `iterations`. El comprador introduce el valor, que se almacena en `algoCustomData.json` para que el algoritmo lo lea.

### Ejemplo Completo: Algoritmo Python con Job Details

```python
import pandas as pd
import numpy as np
import os
import json

def get_job_details():
    """Lee metadatos de los assets usados por el algoritmo"""
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
    """Ejecuta el conteo de líneas basado en inputs"""
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

### Ejemplo Completo: Algoritmo Node.js (Scan de Inputs)

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

> Este ejemplo no usa variables de entorno — escanea directamente `/data/inputs`. Genera `/data/outputs/output.log` y `/data/logs/algo.log`.

---

## PARTE 7: Flujo C2D con ocean.py (Desarrollo Práctico)

### Publicar Dataset con Servicio Compute

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

> Para personalizar privacidad y accesibilidad, añade `compute_values` a `create_url_asset` según las DDO specs.

### Publicar Algoritmo

Para reemplazar el algoritmo de ejemplo:
1. Usa una de las imágenes estándar de `algo_dockers` o publica una imagen Docker propia
2. Usa el nombre de imagen y tag en la parte `container` de los metadatos del algoritmo
3. La imagen debe soportar instalación de dependencias (ej: `pip` para Python)
4. Puedes usar cualquier lenguaje

### Pagar y Ejecutar

```python
# pay_for_compute_service() automatiza:
# - Inicio de órdenes
# - Reutilización de órdenes previas (si transfer_tx_id existe)
# - Si provider fees expiraron pero la orden es válida → reutiliza on-chain
# - Si no hay transfer_tx_id o la orden expiró → crea nueva orden

# Para mejorar recursos de compute, usa un entorno C2D de pago:
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

## PARTE 8: Desplegar un Entorno C2D Propio

### Requisitos de Hardware

| Recurso | Recomendado |
|---------|-------------|
| CPUs | 8 |
| RAM | 16 GB |
| Almacenamiento | 100 GB SSD |
| Red | Conexión rápida a Internet |

### Pasos de Despliegue

#### 1. Instalar Minikube (si no tienes K8s)

```bash
wget -q --show-progress https://github.com/kubernetes/minikube/releases/download/v1.22.0/minikube_1.22.0-0_amd64.deb
sudo dpkg -i minikube_1.22.0-0_amd64.deb
minikube config set kubernetes-version v1.16.0
minikube start --cni=calico --driver=docker --container-runtime=docker
```

#### 2. Instalar kubectl

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

#### 3. Clonar Repositorios

```bash
mkdir computeToData && cd computeToData
git clone https://github.com/oceanprotocol/operator-service
git clone https://github.com/oceanprotocol/operator-engine
```

#### 4. Configurar PostgreSQL y almacenamiento (IPFS o S3)

#### 5. Desplegar Operator Service

```bash
kubectl config set-context --current --namespace ocean-operator
kubectl apply -f operator-service/kubernetes/deployment.yaml
```

#### 6. Inicializar y crear entorno de compute

```bash
curl -X POST "https://compute.example.com/api/v1/operator/pgsqlinit" \
  -H "accept: application/json" -H "Admin: myAdminPass"
```

> **Script automatizado:** https://github.com/oceanprotocol/c2d_barge

---

## PARTE 9: Herramientas de Desarrollo

| Herramienta | Uso | URL |
|-------------|-----|-----|
| **Ocean.py** | Librería Python para publicar, consumir y ejecutar C2D | https://github.com/oceanprotocol/ocean.py |
| **Ocean.js** | Librería JavaScript/TypeScript equivalente | https://github.com/oceanprotocol/ocean.js |
| **Ocean CLI** | Herramienta CLI para publish, consume, C2D | https://docs.oceanprotocol.com/developers/ocean-cli |
| **Barge** | Entorno local completo para desarrollo y testing | https://docs.oceanprotocol.com/developers/barge |
| **c2d-examples** | Ejemplos de algoritmos y datasets para C2D | https://github.com/oceanprotocol/c2d-examples |
| **algo_dockers** | Imágenes Docker pre-configuradas | https://github.com/oceanprotocol/algo_dockers |

---

## PARTE 10: Checklists Rápidos

### Para Montar un Ocean Node

- [ ] Servidor con 1 vCPU, 2 GB RAM, 4 GB disco mínimo
- [ ] Docker + Docker Compose instalados
- [ ] IP pública disponible
- [ ] Ejecutar `ocean-node-quickstart.sh`
- [ ] Abrir puertos 8000, 9000-9003
- [ ] Verificar en https://nodes.oceanprotocol.com/

### Para Desarrollar un Algoritmo C2D

- [ ] Elegir lenguaje e imagen Docker (o crear propia)
- [ ] Leer datos desde `/data/inputs/{did}/{index}`
- [ ] Opcionalmente leer DDOs desde `/data/ddos/{did}`
- [ ] Opcionalmente leer consumer params desde `/data/inputs/algoCustomData.json`
- [ ] Escribir resultados en `/data/outputs/`
- [ ] Definir metadatos: `container.entrypoint`, `container.image`, `container.tag`, `container.checksum`
- [ ] Publicar como asset de tipo `algorithm`
- [ ] Verificar que el dataset permite tu algoritmo (trusted algorithms)

### Para Desplegar un Entorno C2D

- [ ] Servidor potente (8 CPU, 16 GB RAM, 100 GB SSD)
- [ ] Kubernetes o Minikube instalado
- [ ] PostgreSQL desplegado en K8s
- [ ] IPFS o AWS S3 configurado para outputs
- [ ] Operator Service desplegado e inicializado
- [ ] Operator Engine configurado con PRIVATE_KEY única
- [ ] StorageClass en la misma zona que los pods
- [ ] Provider (Ocean Node) accesible y conectado

---

## PARTE 11: Integración Programática vía API — Conectar un Programa Externo al Ocean Node

Esta sección detalla cómo conectar **tu propio programa Python** directamente a la API HTTP del Ocean Node para ejecutar jobs C2D sin usar el marketplace. Se cubren dos enfoques: la API HTTP directa del nodo y la librería `ocean.py` como wrapper de alto nivel.

### Diagrama del Flujo Completo

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────┐
│ Tu programa  │────→│  Ocean Node  │────→│  Operator    │────→│   K8s    │
│   Python     │←────│  (Provider)  │←────│  Service     │←────│  Pod C2D │
│              │     │  HTTP API    │     │              │     │          │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────┘
       │                    │
       │  1. GET environments │
       │  2. Pagar on-chain   │
       │  3. POST /compute    │
       │  4. GET /compute     │ (polling status)
       │  5. GET /computeResult│
       ▼                    ▼
```

---

### 11.1 API HTTP del Ocean Node — Endpoints de Compute

El Ocean Node expone los mismos endpoints que el antiguo Provider, ahora integrados en un solo servicio. Todos los endpoints de compute están bajo `/api/services/`.

#### Listar Entornos de Compute Disponibles

```
GET /api/services/computeEnvironments?chainId={chainId}
```

**Parámetros:**
- `chainId` (int, obligatorio) — ID de la cadena (ej: 1 para Mainnet, 137 para Polygon, 8996 para desarrollo)

**Respuesta:**

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

#### Iniciar un Job de Compute

```
POST /api/services/compute
```

**Body (JSON):**

```json
{
  "signature": "0x...",
  "consumerAddress": "0xTuWalletAddress",
  "nonce": 1,
  "environment": "ocean-compute",
  "dataset": {
    "documentId": "did:op:DATASET_DID",
    "serviceId": "compute",
    "transferTxId": "0xTxHashDeLaOrdenOnChain",
    "userdata": {}
  },
  "algorithm": {
    "documentId": "did:op:ALGORITHM_DID",
    "serviceId": "compute",
    "transferTxId": "0xTxHashDeLaOrdenDelAlgoritmo",
    "algocustomdata": {
      "iterations": 100,
      "learning_rate": 0.01
    }
  },
  "additionalDatasets": []
}
```

**Campos clave:**

| Campo | Descripción |
|-------|-------------|
| `signature` | Firma del mensaje por el consumidor (autenticación) |
| `consumerAddress` | Dirección Ethereum del consumidor |
| `nonce` | Nonce para evitar replay attacks |
| `environment` | ID del entorno de compute (obtenido del endpoint anterior) |
| `dataset.documentId` | DID del dataset |
| `dataset.serviceId` | ID del servicio de compute en el DDO |
| `dataset.transferTxId` | Hash de la transacción on-chain de aprobación de datatokens |
| `dataset.userdata` | Parámetros del consumidor para el dataset (opcional) |
| `algorithm.documentId` | DID del algoritmo (una de `documentId` o `meta` es requerida) |
| `algorithm.meta` | Alternativa: metadatos raw del algoritmo (si no se usa DID) |
| `algorithm.transferTxId` | Hash de la transacción on-chain para el algoritmo |
| `algorithm.algocustomdata` | **Consumer Parameters** — el JSON con los parámetros que tu algoritmo leerá desde `/data/inputs/algoCustomData.json` |
| `additionalDatasets` | Array de objetos dataset adicionales (opcional) |

**Respuesta:**

```json
[
  {
    "jobId": "0x1111:001",
    "status": 1,
    "statusText": "Job started"
  }
]
```

#### Consultar Estado del Job

```
GET /api/services/compute?signature={sig}&consumerAddress={addr}&jobId={jobId}&documentId={did}
```

Al menos uno de `documentId`, `jobId` es requerido.

**Respuesta:**

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

**Códigos de estado:**

| Status | Texto | Significado |
|--------|-------|-------------|
| 1 | Warming up | Iniciando |
| 10 | Job started | Job comenzado |
| 20 | Configuring volumes | Configurando volúmenes K8s |
| 30 | Provisioning success | Datos descargados correctamente |
| 31 | Data provisioning failed | **Error:** fallo al descargar datos |
| 32 | Algorithm provisioning failed | **Error:** fallo al descargar algoritmo |
| 40 | Running algorithm | Algoritmo ejecutándose |
| 50 | Filtering results | Filtrando resultados |
| 60 | Publishing results | Publicando resultados |
| 70 | Job completed | **Completado** |

#### Descargar Resultados

```
GET /api/services/computeResult?jobId={jobId}&index={index}&consumerAddress={addr}&nonce={nonce}&signature={sig}
```

**Parámetros:**
- `jobId` — ID del job
- `index` — Índice del resultado a descargar (0 para primer output)
- `consumerAddress`, `nonce`, `signature` — Autenticación

**Respuesta:** Bytes del resultado.

#### Detener un Job

```
PUT /api/services/compute?signature={sig}&documentId={did}&jobId={jobId}
```

#### Eliminar un Job

```
DELETE /api/services/compute?signature={sig}&documentId={did}&jobId={jobId}&consumerAddress={addr}
```

---

### 11.2 Integración Completa con ocean.py (Método Recomendado)

`ocean.py` abstrae toda la complejidad de firmas, transacciones on-chain y llamadas HTTP. Este es el método recomendado para un programa externo.

#### Instalación

```bash
pip install ocean-lib
```

#### Configuración Inicial

```python
import os
from ocean_lib.ocean.ocean import Ocean
from ocean_lib.web3_internal.wallet import Wallet
from ocean_lib.example_config import get_config_dict

# Configuración — apuntando a tu Ocean Node
config = get_config_dict("polygon")  # o "mainnet", "sepolia", etc.

# Sobreescribir el Provider URL con tu propio Ocean Node
config["PROVIDER_URL"] = "http://TU_OCEAN_NODE_IP:8000"

ocean = Ocean(config)

# Tu wallet (consumidor)
consumer_wallet = Wallet(
    ocean.web3,
    private_key=os.getenv("CONSUMER_PRIVATE_KEY"),  # 0x...
)
print(f"Consumer address: {consumer_wallet.address}")
```

#### Paso 1: Resolver Dataset y Algoritmo

```python
# Obtener DDOs por DID
DATA_ddo = ocean.assets.resolve("did:op:TU_DATASET_DID")
ALGO_ddo = ocean.assets.resolve("did:op:TU_ALGORITHM_DID")

# Obtener el servicio de compute del dataset
compute_service = DATA_ddo.services[0]  # o buscar por type="compute"
assert compute_service.type == "compute", "El servicio no es de tipo compute"

# Obtener el servicio del algoritmo
algo_service = ALGO_ddo.services[0]

print(f"Dataset: {DATA_ddo.did}")
print(f"Algorithm: {ALGO_ddo.did}")
print(f"Provider endpoint: {compute_service.service_endpoint}")
```

#### Paso 2: Seleccionar Entorno de Compute

```python
# Listar todos los entornos C2D disponibles
environments = ocean.compute.get_c2d_environments(
    compute_service.service_endpoint,
    DATA_ddo.chain_id
)

print("Entornos disponibles:")
for env in environments:
    print(f"  ID: {env['id']}, CPU: {env['nCPU']}, RAM: {env['ramGB']}GB, "
          f"GPU: {env['nGPU']}, Precio mín: {env['priceMin']}")

# Elegir entorno (ej: el primero disponible, o el gratuito)
compute_env = environments[0]["id"]

# O para un entorno gratuito:
# free_env = ocean.compute.get_free_c2d_environment(
#     compute_service.service_endpoint, DATA_ddo.chain_id
# )
# compute_env = free_env["id"]
```

#### Paso 3: Pagar por el Servicio de Compute (On-Chain)

```python
from ocean_lib.models.compute_input import ComputeInput

# Crear objetos ComputeInput
dataset_compute = ComputeInput(DATA_ddo, compute_service)
algo_compute = ComputeInput(ALGO_ddo, algo_service)

# Obtener preview de fees del provider
datasets = [dataset_compute]
algorithm_data = algo_compute

# Pagar — esto maneja automáticamente:
# - Aprobación de datatokens para dataset
# - Aprobación de datatokens para algoritmo
# - Provider fees
# - Reutilización de órdenes previas si aún son válidas
datasets, algorithm_data = ocean.assets.pay_for_compute_service(
    datasets=datasets,
    algorithm_data=algorithm_data,
    consumer_address=consumer_wallet.address,
    compute_environment=compute_env,
    valid_until=0,  # 0 = usar duración por defecto del entorno
    consume_market_order_fee_address=consumer_wallet.address,
    consume_market_order_fee_token=DATA_ddo.datatokens[0]["address"],
    consume_market_order_fee_amount=0,
    wallet=consumer_wallet,
)
```

#### Paso 4: Iniciar el Job C2D con Consumer Parameters

```python
# Definir tus consumer parameters (algocustomdata)
# Estos llegarán al algoritmo en /data/inputs/algoCustomData.json
my_algo_params = {
    "iterations": 100,
    "learning_rate": 0.01,
    "model_type": "random_forest",
    "output_format": "json"
}

# Iniciar el job de compute
job_id = ocean.compute.start(
    consumer_wallet=consumer_wallet,
    dataset=dataset_compute,
    compute_environment=compute_env,
    algorithm=algo_compute,
    algorithm_algocustomdata=my_algo_params,  # ← tus consumer parameters
    additional_datasets=[],  # datasets adicionales si los hay
)

print(f"Job iniciado! ID: {job_id}")
```

#### Paso 5: Monitorizar el Estado (Polling)

```python
import time

# Polling del estado hasta que el job termine
while True:
    status = ocean.compute.status(
        ddo=DATA_ddo,
        service=compute_service,
        job_id=job_id,
        wallet=consumer_wallet
    )
    
    print(f"Estado: {status['statusText']} (código: {status['status']})")
    
    # Job completado
    if status["status"] == 70:
        print("¡Job completado exitosamente!")
        break
    
    # Errores
    if status["status"] in (31, 32):
        print(f"ERROR: {status['statusText']}")
        break
    
    time.sleep(15)  # Esperar 15 segundos antes de la siguiente consulta
```

#### Paso 6: Descargar Resultados

```python
# Obtener resultado del job (índice 0 = primer output)
result = ocean.compute.result(
    ddo=DATA_ddo,
    service=compute_service,
    job_id=job_id,
    index=0,
    wallet=consumer_wallet
)

print(f"Resultado DID: {result.get('did', 'N/A')}")
print(f"URLs de resultados: {result.get('urls', [])}")
print(f"URLs de logs: {result.get('logs', [])}")

# Obtener logs del algoritmo
logs = ocean.compute.compute_job_result_logs(
    ddo=DATA_ddo,
    service=compute_service,
    job_id=job_id,
    wallet=consumer_wallet,
    log_type="output"  # "output" o "algorithmLog"
)
print(f"Logs: {logs}")
```

#### Paso 7 (Opcional): Detener un Job en Ejecución

```python
stop_result = ocean.compute.stop(
    ddo=DATA_ddo,
    service=compute_service,
    job_id=job_id,
    wallet=consumer_wallet
)
print(f"Job detenido: {stop_result['statusText']}")
```

---

### 11.3 Ejemplo End-to-End: Script Completo

```python
#!/usr/bin/env python3
"""
Ejemplo completo: Conectar programa externo a Ocean Node C2D
Sin marketplace — todo vía API programática.
"""

import os
import time
from ocean_lib.ocean.ocean import Ocean
from ocean_lib.web3_internal.wallet import Wallet
from ocean_lib.example_config import get_config_dict
from ocean_lib.models.compute_input import ComputeInput

# ============================================================
# CONFIGURACIÓN
# ============================================================
NETWORK = "polygon"                           # Red blockchain
OCEAN_NODE_URL = "http://TU_NODE_IP:8000"     # Tu Ocean Node
DATASET_DID = "did:op:TU_DATASET_DID"         # DID del dataset
ALGO_DID = "did:op:TU_ALGORITHM_DID"          # DID del algoritmo
PRIVATE_KEY = os.getenv("CONSUMER_PRIVATE_KEY")

# Parámetros custom para el algoritmo
ALGO_PARAMS = {
    "iterations": 500,
    "learning_rate": 0.001,
    "batch_size": 32
}

# ============================================================
# INICIALIZACIÓN
# ============================================================
config = get_config_dict(NETWORK)
config["PROVIDER_URL"] = OCEAN_NODE_URL
ocean = Ocean(config)
wallet = Wallet(ocean.web3, private_key=PRIVATE_KEY)
print(f"[INIT] Consumer: {wallet.address}")

# ============================================================
# RESOLVER ASSETS
# ============================================================
data_ddo = ocean.assets.resolve(DATASET_DID)
algo_ddo = ocean.assets.resolve(ALGO_DID)
compute_svc = data_ddo.services[0]
algo_svc = algo_ddo.services[0]
print(f"[OK] Dataset resuelto: {data_ddo.did}")
print(f"[OK] Algoritmo resuelto: {algo_ddo.did}")

# ============================================================
# SELECCIONAR ENTORNO
# ============================================================
envs = ocean.compute.get_c2d_environments(
    compute_svc.service_endpoint, data_ddo.chain_id
)
env_id = envs[0]["id"]
print(f"[OK] Entorno seleccionado: {env_id} "
      f"(CPU:{envs[0]['nCPU']}, RAM:{envs[0]['ramGB']}GB)")

# ============================================================
# PAGAR ON-CHAIN
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
print("[OK] Pago realizado")

# ============================================================
# INICIAR JOB C2D CON CONSUMER PARAMETERS
# ============================================================
job_id = ocean.compute.start(
    consumer_wallet=wallet,
    dataset=dataset_input,
    compute_environment=env_id,
    algorithm=algo_input,
    algorithm_algocustomdata=ALGO_PARAMS,
)
print(f"[OK] Job iniciado: {job_id}")

# ============================================================
# POLLING DE ESTADO
# ============================================================
TERMINAL_STATES = {70, 31, 32}
while True:
    status = ocean.compute.status(data_ddo, compute_svc, job_id, wallet)
    code = status["status"]
    text = status["statusText"]
    print(f"[...] Estado: {text} ({code})")
    
    if code in TERMINAL_STATES:
        break
    time.sleep(15)

# ============================================================
# RECOGER RESULTADOS
# ============================================================
if code == 70:
    result = ocean.compute.result(data_ddo, compute_svc, job_id, 0, wallet)
    print(f"\n[RESULTADO] URLs: {result.get('urls', [])}")
    print(f"[RESULTADO] DID: {result.get('did', 'N/A')}")
    
    logs = ocean.compute.compute_job_result_logs(
        data_ddo, compute_svc, job_id, wallet
    )
    print(f"[LOGS] {logs}")
else:
    print(f"\n[ERROR] Job falló con estado: {text}")
```

---

### 11.4 Integración vía HTTP Directo (Sin ocean.py)

Si prefieres no usar `ocean.py` y hacer llamadas HTTP directas (por ejemplo, desde otro lenguaje o un microservicio), necesitas manejar manualmente la firma y las transacciones on-chain.

```python
"""
Ejemplo de llamadas HTTP directas al Ocean Node.
Requiere: requests, web3, eth_account
"""

import requests
import json
import time
from web3 import Web3
from eth_account.messages import encode_defunct

OCEAN_NODE = "http://TU_NODE_IP:8000"
PRIVATE_KEY = "0x..."
CHAIN_ID = 137  # Polygon

w3 = Web3()
account = w3.eth.account.from_key(PRIVATE_KEY)

def sign_message(message: str) -> str:
    """Firma un mensaje con la clave privada del consumidor."""
    msg = encode_defunct(text=message)
    signed = w3.eth.account.sign_message(msg, private_key=PRIVATE_KEY)
    return signed.signature.hex()


# --- 1. LISTAR ENTORNOS ---
def get_environments(chain_id: int):
    resp = requests.get(
        f"{OCEAN_NODE}/api/services/computeEnvironments",
        params={"chainId": chain_id}
    )
    return resp.json()


# --- 2. INICIAR JOB ---
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


# --- 3. CONSULTAR ESTADO ---
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


# --- 4. DESCARGAR RESULTADO ---
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
    return resp.content  # Bytes del resultado


# --- USO ---
if __name__ == "__main__":
    # Listar entornos
    envs = get_environments(CHAIN_ID)
    print(f"Entornos: {json.dumps(envs, indent=2)}")
    
    # NOTA: dataset_tx_id y algo_tx_id son los hashes de las
    # transacciones on-chain donde aprobaste los datatokens.
    # Esto requiere interacción previa con los smart contracts.
    
    # Iniciar job con consumer parameters
    result = start_compute_job(
        dataset_did="did:op:DATASET_DID",
        algo_did="did:op:ALGO_DID",
        environment_id=envs[0]["id"],
        dataset_tx_id="0x...",     # De la transacción on-chain
        algo_tx_id="0x...",        # De la transacción on-chain
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
        print(f"Estado: {status[0]['statusText']}")
        if status[0]["status"] in (70, 31, 32):
            break
        time.sleep(15)
    
    # Descargar resultado
    if status[0]["status"] == 70:
        output = get_result(job_id, 0)
        with open("resultado_c2d.bin", "wb") as f:
            f.write(output)
        print(f"Resultado guardado ({len(output)} bytes)")
```

---

### 11.5 Cómo Fluyen los Consumer Parameters

```
Tu programa Python                    Ocean Node                K8s Pod
       │                                  │                        │
       │ algocustomdata: {                │                        │
       │   "iterations": 100,             │                        │
       │   "learning_rate": 0.01          │                        │
       │ }                                │                        │
       │──── POST /api/services/compute──→│                        │
       │                                  │── Crea Job ──────────→│
       │                                  │                        │
       │                                  │   Pod-Configuration    │
       │                                  │   escribe el JSON en:  │
       │                                  │   /data/inputs/        │
       │                                  │     algoCustomData.json│
       │                                  │                        │
       │                                  │   Tu algoritmo lee:    │
       │                                  │   json.load(open(      │
       │                                  │     "/data/inputs/     │
       │                                  │     algoCustomData.json│
       │                                  │   ))                   │
       │                                  │                        │
       │                                  │   → {"iterations":100, │
       │                                  │      "learning_rate":  │
       │                                  │       0.01}            │
       │                                  │                        │
       │                                  │   Algoritmo escribe:   │
       │                                  │   /data/outputs/result │
       │                                  │                        │
       │←── GET /computeResult ───────────│←── S3/IPFS ──────────│
       │    (bytes del resultado)          │                        │
```

**Dentro del algoritmo, lees los parámetros así:**

```python
import json

# Leer consumer parameters enviados por tu programa externo
with open("/data/inputs/algoCustomData.json") as f:
    params = json.load(f)

iterations = params.get("iterations", 10)
learning_rate = params.get("learning_rate", 0.001)

print(f"Ejecutando con {iterations} iteraciones, lr={learning_rate}")
```

---

### 11.6 Notas Importantes para la Integración

**Sobre la autenticación (firmas):**
- Cada llamada a la API requiere una firma (`signature`) del consumidor
- La firma se genera firmando un mensaje con la clave privada del consumidor
- `ocean.py` maneja esto automáticamente; con HTTP directo, debes firmar con `eth_account`

**Sobre el pago on-chain (transferTxId):**
- Antes de iniciar un job C2D, debes haber **aprobado y transferido datatokens** on-chain tanto para el dataset como para el algoritmo
- `ocean.py` automatiza esto con `pay_for_compute_service()`
- Con HTTP directo, debes interactuar con los smart contracts ERC20 de datatokens usando `web3.py`

**Sobre `algorithm.meta` vs `algorithm.documentId`:**
- Si el algoritmo está **publicado como asset**, usa `algorithm.documentId` (el DID)
- Si quieres enviar código **raw**, usa `algorithm.meta` con los metadatos del contenedor
- `algorithm.meta` toma precedencia sobre `documentId` si ambos están presentes
- El dataset debe tener `allowRawAlgorithm: true` para aceptar código raw

**Sobre los consumer parameters:**
- Se envían en `algorithm.algocustomdata` en la API HTTP
- Se pasan como `algorithm_algocustomdata` en `ocean.compute.start()`
- Llegan al pod en `/data/inputs/algoCustomData.json`
- Tu algoritmo los lee con `json.load()`

**Sobre la reutilización de órdenes:**
- `pay_for_compute_service()` reutiliza automáticamente órdenes previas válidas
- Si los provider fees expiraron pero la orden sigue activa, se reutiliza on-chain
- Si todo expiró, crea una nueva orden (nuevo gasto)

---

## Enlaces Clave

| Recurso | URL |
|---------|-----|
| Repo principal Ocean Node | https://github.com/oceanprotocol/ocean-node |
| Dashboard de nodos | https://nodes.oceanprotocol.com/ |
| Variables de entorno | https://github.com/oceanprotocol/ocean-node/blob/main/docs/env.md |
| API del nodo | https://github.com/oceanprotocol/ocean-node/blob/develop/API.md |
| C2D V2 docs | https://github.com/oceanprotocol/ocean-node/blob/develop/docs/C2DV2.md |
| Imágenes Docker algoritmos | https://github.com/oceanprotocol/algo_dockers |
| Ejemplos C2D | https://github.com/oceanprotocol/c2d-examples |
| Docs oficiales C2D | https://docs.oceanprotocol.com/developers/compute-to-data |
| Arquitectura C2D | https://docs.oceanprotocol.com/developers/compute-to-data/compute-to-data-architecture |
| Datasets & Algoritmos | https://docs.oceanprotocol.com/developers/compute-to-data/compute-to-data-datasets-algorithms |
| Workflow C2D | https://docs.oceanprotocol.com/developers/compute-to-data/compute-workflow |
| Writing Algorithms | https://docs.oceanprotocol.com/developers/compute-to-data/compute-to-data-algorithms |
| Compute Options | https://docs.oceanprotocol.com/developers/compute-to-data/compute-options |
| Despliegue C2D Minikube | https://docs.oceanprotocol.com/infrastructure/compute-to-data-minikube |
| Ocean.py C2D flow | https://github.com/oceanprotocol/ocean.py/blob/main/READMEs/c2d-flow.md |
| Operator Engine | https://github.com/oceanprotocol/operator-engine |
| Operator Service | https://github.com/oceanprotocol/operator-service |
