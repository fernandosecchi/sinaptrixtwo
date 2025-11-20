#!/usr/bin/env python3
"""Script to seed sample iSeries servers for testing."""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.database import AsyncSessionLocal
from src.services.infrastructure.servidor_service import ServidorService
from src.models.infrastructure.servidor import ProcessorTier, EstadoRegistro, TipoStorage


async def seed_servers():
    """Create sample servers for testing."""
    print("🚀 Starting server seeding...")

    async with AsyncSessionLocal() as session:
        service = ServidorService(session)

        # Check if servers already exist
        existing = await service.list_servidores()
        if existing:
            print(f"⚠️  Database already has {len(existing)} servers. Skipping seed.")
            return

        # Sample servers data
        servers_data = [
            {
                "modelo": "9009-42A",
                "processor_feature_code": "EP30",
                "processor_tier": ProcessorTier.P30,
                "nombre_servidor": "PROD-iSeries-01",
                "descripcion": "Servidor principal de producción",
                "ubicacion": "Data Center Principal - Rack A1",
                "es_virtualizado": False,
                "estado_registro": EstadoRegistro.CONFIRMADO,
                "numero_serie": "65-A1B2C",
                "machine_type": "9009",
                "frame_id": "FRAME-01",
                "firmware_version": "FW950.30",
                "cantidad_procesadores_fisicos": 8,
                "memoria_total_mb": 262144,  # 256 GB
                "tipo_storage": TipoStorage.SAN,
                "os_version": "V7R4M0",
                "ip_principal": "192.168.100.10",
                "activo": True,
                "notas": "Servidor principal con alta disponibilidad"
            },
            {
                "modelo": "9009-42A",
                "processor_feature_code": "EP20",
                "processor_tier": ProcessorTier.P20,
                "nombre_servidor": "PROD-iSeries-02",
                "descripcion": "Servidor de respaldo",
                "ubicacion": "Data Center Principal - Rack A2",
                "es_virtualizado": False,
                "estado_registro": EstadoRegistro.CONFIRMADO,
                "numero_serie": "65-A1B2D",
                "machine_type": "9009",
                "frame_id": "FRAME-02",
                "firmware_version": "FW950.30",
                "cantidad_procesadores_fisicos": 6,
                "memoria_total_mb": 196608,  # 192 GB
                "tipo_storage": TipoStorage.SAN,
                "os_version": "V7R4M0",
                "ip_principal": "192.168.100.11",
                "activo": True,
                "notas": "Servidor de respaldo con replicación en tiempo real"
            },
            {
                "modelo": "8203-E4A",
                "processor_feature_code": "EPX5",
                "processor_tier": ProcessorTier.P10,
                "nombre_servidor": "DEV-iSeries-01",
                "descripcion": "Servidor de desarrollo",
                "ubicacion": "Data Center Secundario",
                "es_virtualizado": True,
                "estado_registro": EstadoRegistro.CONFIRMADO,
                "numero_serie": "65-D1E2F",
                "machine_type": "8203",
                "firmware_version": "FW860.20",
                "cantidad_procesadores_fisicos": 4,
                "memoria_total_mb": 131072,  # 128 GB
                "tipo_storage": TipoStorage.INTERNO,
                "os_version": "V7R3M0",
                "ip_principal": "192.168.200.10",
                "activo": True,
                "notas": "Servidor para desarrollo y testing"
            },
            {
                "modelo": "9105-22A",
                "processor_feature_code": "EP50",
                "processor_tier": ProcessorTier.P50,
                "nombre_servidor": "POWER10-TEST",
                "descripcion": "Servidor Power10 para evaluación",
                "ubicacion": "Laboratorio",
                "es_virtualizado": False,
                "estado_registro": EstadoRegistro.PRELIMINAR,
                "numero_serie": "65-P10A1",
                "machine_type": "9105",
                "frame_id": "FRAME-P10",
                "firmware_version": "FW1030.10",
                "cantidad_procesadores_fisicos": 16,
                "memoria_total_mb": 524288,  # 512 GB
                "tipo_storage": TipoStorage.VSAN,
                "os_version": "V7R5M0",
                "ip_principal": "10.0.0.10",
                "activo": True,
                "notas": "Servidor Power10 en fase de evaluación"
            },
            {
                "modelo": "9009-41A",
                "processor_feature_code": "EP10",
                "processor_tier": ProcessorTier.P05,
                "nombre_servidor": "TEST-iSeries-01",
                "descripcion": "Servidor de pruebas",
                "ubicacion": "Data Center Principal - Rack B1",
                "es_virtualizado": True,
                "estado_registro": EstadoRegistro.CONFIRMADO,
                "numero_serie": "65-T1A2B",
                "machine_type": "9009",
                "firmware_version": "FW950.20",
                "cantidad_procesadores_fisicos": 2,
                "memoria_total_mb": 65536,  # 64 GB
                "tipo_storage": TipoStorage.MIXTO,
                "os_version": "V7R4M0",
                "ip_principal": "192.168.100.50",
                "activo": True,
                "notas": "Servidor para pruebas de aplicaciones"
            },
            {
                "modelo": "8286-42A",
                "processor_feature_code": "EP25",
                "processor_tier": ProcessorTier.P20,
                "nombre_servidor": None,  # Sin nombre asignado
                "descripcion": "Servidor pendiente de configuración",
                "ubicacion": "Almacén",
                "es_virtualizado": False,
                "estado_registro": EstadoRegistro.PRELIMINAR,
                "numero_serie": None,  # Sin serie aún
                "machine_type": "8286",
                "firmware_version": None,
                "cantidad_procesadores_fisicos": None,
                "memoria_total_mb": None,
                "tipo_storage": None,
                "os_version": None,
                "ip_principal": None,
                "activo": False,
                "notas": "Servidor recién adquirido, pendiente de instalación"
            },
            {
                "modelo": "9009-42A",
                "processor_feature_code": "EP15",
                "processor_tier": ProcessorTier.P10,
                "nombre_servidor": "OBSOLETE-01",
                "descripcion": "Servidor fuera de servicio",
                "ubicacion": "Almacén",
                "es_virtualizado": False,
                "estado_registro": EstadoRegistro.OBSOLETO,
                "numero_serie": "65-OLD01",
                "machine_type": "9009",
                "firmware_version": "FW940.10",
                "cantidad_procesadores_fisicos": 4,
                "memoria_total_mb": 98304,  # 96 GB
                "tipo_storage": TipoStorage.INTERNO,
                "os_version": "V7R2M0",
                "ip_principal": "192.168.100.99",
                "activo": False,
                "notas": "Servidor retirado del servicio activo"
            },
            {
                "modelo": "9080-M9S",
                "processor_feature_code": "EP40",
                "processor_tier": ProcessorTier.P40,
                "nombre_servidor": "HMC-Manager",
                "descripcion": "Hardware Management Console",
                "ubicacion": "Data Center Principal - Rack Admin",
                "es_virtualizado": False,
                "estado_registro": EstadoRegistro.CONFIRMADO,
                "numero_serie": "65-HMC01",
                "machine_type": "9080",
                "firmware_version": "V9R1M910",
                "cantidad_procesadores_fisicos": 12,
                "memoria_total_mb": 393216,  # 384 GB
                "tipo_storage": TipoStorage.SAN,
                "os_version": "HMC V9R1",
                "ip_principal": "192.168.100.5",
                "activo": True,
                "notas": "Consola de gestión para todos los servidores Power"
            }
        ]

        # Create servers
        print(f"📦 Creating {len(servers_data)} sample servers...")
        for i, data in enumerate(servers_data, 1):
            try:
                server = await service.create_servidor(**data)
                print(f"  ✅ Created server {i}: {server.display_name}")
            except Exception as e:
                print(f"  ❌ Error creating server {i}: {str(e)}")

        # Commit all changes
        await session.commit()

    # Display statistics
    async with AsyncSessionLocal() as session:
        service = ServidorService(session)
        stats = await service.get_statistics()

        print("\n📊 Server Statistics:")
        print(f"  Total servers: {stats['total_servers']}")
        print(f"  Active servers: {stats['active_servers']}")
        print(f"  Virtualized: {stats['virtualized_servers']}")
        print(f"  Physical: {stats['physical_servers']}")
        print(f"\n  By Processor Tier:")
        for tier, count in stats['servers_by_tier'].items():
            print(f"    {tier}: {count}")
        print(f"\n  By Status:")
        for status, count in stats['servers_by_status'].items():
            print(f"    {status}: {count}")

    print("\n✨ Server seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_servers())