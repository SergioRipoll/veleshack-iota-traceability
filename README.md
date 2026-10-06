# VelesHack 2026 - Tangle Traceability & Observability System

Sistema completo de ingesta, trazabilidad, persistencia y observabilidad en tiempo real sobre una red privada DLT IOTA (Hornet).

## 🚀 Arquitectura del Proyecto

El sistema se divide en cuatro componentes principales:
1. **Nodo Privado IOTA Hornet (Docker & INX Dashboard):** Red local sobre el puerto `14265` (REST API) y explorador gráfico en el puerto `31011`.
2. **Messages API (Ingesta - Puerto 5555):** Gateway en Flask que empaqueta cargas útiles JSON en formato hexadecimal y las sube a la Tangle mediante la API REST de Hornet.
3. **Traceability API (Backend - Puerto 5050):** Backend Flask + SQLite (`traceability.db`) que intercepta los `blockId`, verifica la solidez (*solidity*) y validez del bloque consultando al nodo Hornet y persiste la información enriquecida.
4. **Observability Dashboard (Frontend Web - Puerto 5050):** Panel de control interactivo integrado que consume `/messages` y renderiza el estado de los bloques en tiempo real.

---

## 🛠️ Requisitos e Instalación

### Requisitos Previos
- Docker & Docker Compose
- Python 3.10+
- WSL Ubuntu

### Instalar Dependencias
```bash
# Dependencias de la Messages API
pip install -r iota-messages-api/requirements.txt --break-system-packages

# Dependencias de la Traceability API
pip install -r traceability-app/requirements.txt --break-system-packages
