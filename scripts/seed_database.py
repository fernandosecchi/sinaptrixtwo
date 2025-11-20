#!/usr/bin/env python3
"""
Script to seed the database with example data for testing purposes.
Run with: docker-compose exec app python scripts/seed_database.py
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
import random

# Add the parent directory to the path to import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from src.database import AsyncSessionLocal
from src.services.users.user_service import UserService
from src.services.leads.lead_service import LeadService
from src.models.enums import LeadStatus, LeadSource
from src.schemas.leads.lead import LeadCreate


# Sample data for users
SAMPLE_USERS = [
    {
        "first_name": "Carlos",
        "last_name": "García",
        "email": "carlos.garcia@example.com"
    },
    {
        "first_name": "María",
        "last_name": "López",
        "email": "maria.lopez@example.com"
    },
    {
        "first_name": "Juan",
        "last_name": "Martínez",
        "email": "juan.martinez@example.com"
    },
    {
        "first_name": "Ana",
        "last_name": "Rodríguez",
        "email": "ana.rodriguez@example.com"
    },
    {
        "first_name": "Pedro",
        "last_name": "Fernández",
        "email": "pedro.fernandez@example.com"
    },
    {
        "first_name": "Laura",
        "last_name": "Sánchez",
        "email": "laura.sanchez@example.com"
    },
    {
        "first_name": "Diego",
        "last_name": "Torres",
        "email": "diego.torres@example.com"
    },
    {
        "first_name": "Sofía",
        "last_name": "Ramírez",
        "email": "sofia.ramirez@example.com"
    },
    {
        "first_name": "Miguel",
        "last_name": "Vega",
        "email": "miguel.vega@example.com"
    },
    {
        "first_name": "Carmen",
        "last_name": "Morales",
        "email": "carmen.morales@example.com"
    }
]

# Sample data for leads
SAMPLE_LEADS = [
    {
        "first_name": "Roberto",
        "last_name": "Jiménez",
        "email": "roberto.jimenez@techcorp.com",
        "phone": "+54 11 4567-8901",
        "company": "TechCorp Solutions",
        "position": "CTO",
        "status": LeadStatus.CLIENT.value,
        "source": LeadSource.WEBSITE.value,
        "notes": "Interesado en soluciones de automatización. Ya es cliente desde hace 6 meses."
    },
    {
        "first_name": "Patricia",
        "last_name": "Mendoza",
        "email": "patricia.mendoza@innovate.io",
        "phone": "+54 11 3456-7890",
        "company": "Innovate Labs",
        "position": "Product Manager",
        "status": LeadStatus.PROSPECT.value,
        "source": LeadSource.REFERRAL.value,
        "notes": "Referido por Carlos García. Reunión programada para la próxima semana."
    },
    {
        "first_name": "Fernando",
        "last_name": "Silva",
        "email": "fernando.silva@startup.com",
        "phone": "+54 11 2345-6789",
        "company": "StartupXYZ",
        "position": "CEO",
        "status": LeadStatus.LEAD.value,
        "source": LeadSource.EVENT.value,
        "notes": "Conocido en el evento TechConf 2024. Solicito demo del producto."
    },
    {
        "first_name": "Luciana",
        "last_name": "Castro",
        "email": "luciana.castro@marketing.agency",
        "phone": "+54 11 5678-9012",
        "company": "Marketing Agency Pro",
        "position": "Marketing Director",
        "status": LeadStatus.PROSPECT.value,
        "source": LeadSource.SOCIAL_MEDIA.value,
        "notes": "Contacto por LinkedIn. Interesada en herramientas de análisis."
    },
    {
        "first_name": "Alejandro",
        "last_name": "Paz",
        "email": "alejandro.paz@consulting.com",
        "company": "Consulting Group",
        "position": "Senior Consultant",
        "status": LeadStatus.LOST.value,
        "source": LeadSource.EMAIL.value,
        "notes": "No hubo match con sus necesidades actuales. Revisar en Q2 2025."
    },
    {
        "first_name": "Valentina",
        "last_name": "Ruiz",
        "email": "valentina.ruiz@ecommerce.shop",
        "phone": "+54 11 6789-0123",
        "company": "E-Shop Express",
        "position": "Operations Manager",
        "status": LeadStatus.CLIENT.value,
        "source": LeadSource.WEBSITE.value,
        "notes": "Cliente activo. Plan Enterprise. Muy satisfecha con el servicio."
    },
    {
        "first_name": "Martín",
        "last_name": "Herrera",
        "email": "martin.herrera@fintech.bank",
        "phone": "+54 11 7890-1234",
        "company": "FinTech Bank",
        "position": "IT Manager",
        "status": LeadStatus.PROSPECT.value,
        "source": LeadSource.PHONE.value,
        "notes": "Llamada inbound. Evaluando propuesta técnica."
    },
    {
        "first_name": "Gabriela",
        "last_name": "Díaz",
        "email": "gabriela.diaz@health.clinic",
        "phone": "+54 11 8901-2345",
        "company": "Health Clinic Plus",
        "position": "Administrator",
        "status": LeadStatus.LEAD.value,
        "source": LeadSource.REFERRAL.value,
        "notes": "Referido por cliente existente. Primer contacto pendiente."
    },
    {
        "first_name": "Nicolás",
        "last_name": "Álvarez",
        "email": "nicolas.alvarez@logistics.co",
        "company": "Logistics International",
        "position": "COO",
        "status": LeadStatus.CLIENT.value,
        "source": LeadSource.EVENT.value,
        "notes": "Cliente desde 2023. Renovación de contrato en proceso."
    },
    {
        "first_name": "Camila",
        "last_name": "Vargas",
        "email": "camila.vargas@design.studio",
        "phone": "+54 11 9012-3456",
        "company": "Creative Design Studio",
        "position": "Creative Director",
        "status": LeadStatus.LEAD.value,
        "source": LeadSource.SOCIAL_MEDIA.value,
        "notes": "Interacción en Instagram. Solicitó información sobre precios."
    },
    {
        "first_name": "Sebastián",
        "last_name": "Luna",
        "email": "sebastian.luna@realestate.com",
        "phone": "+54 11 1234-5678",
        "company": "RealEstate Pro",
        "position": "Sales Manager",
        "status": LeadStatus.PROSPECT.value,
        "source": LeadSource.WEBSITE.value,
        "notes": "Descargó whitepaper. En proceso de nurturing."
    },
    {
        "first_name": "Florencia",
        "last_name": "Ortiz",
        "email": "florencia.ortiz@education.org",
        "company": "Education Foundation",
        "position": "Program Director",
        "status": LeadStatus.LOST.value,
        "source": LeadSource.EMAIL.value,
        "notes": "Presupuesto no aprobado. Contactar nuevamente en próximo ciclo fiscal."
    },
    {
        "first_name": "Andrés",
        "last_name": "Gutiérrez",
        "email": "andres.gutierrez@transport.net",
        "phone": "+54 11 2468-1357",
        "company": "Transport Network",
        "position": "Fleet Manager",
        "status": LeadStatus.CLIENT.value,
        "source": LeadSource.PHONE.value,
        "notes": "Cliente con plan básico. Oportunidad de upsell identificada."
    },
    {
        "first_name": "Julieta",
        "last_name": "Medina",
        "email": "julieta.medina@fashion.brand",
        "phone": "+54 11 3579-2468",
        "company": "Fashion Brand Co",
        "position": "Brand Manager",
        "status": LeadStatus.LEAD.value,
        "source": LeadSource.OTHER.value,
        "notes": "Contacto por recomendación de socio estratégico."
    },
    {
        "first_name": "Gonzalo",
        "last_name": "Pereira",
        "email": "gonzalo.pereira@software.dev",
        "company": "Software Development Inc",
        "position": "Tech Lead",
        "status": LeadStatus.PROSPECT.value,
        "source": LeadSource.WEBSITE.value,
        "notes": "Completó trial de 14 días. Evaluación técnica positiva."
    }
]


async def clear_existing_data():
    """Clear existing data from users and leads tables."""
    async with AsyncSessionLocal() as session:
        try:
            # Clear leads first (in case there are foreign key constraints in the future)
            await session.execute(text("DELETE FROM leads"))
            await session.execute(text("DELETE FROM users"))
            await session.commit()
            print("✓ Existing data cleared")
        except Exception as e:
            await session.rollback()
            print(f"✗ Error clearing data: {e}")
            raise


async def seed_users():
    """Seed the database with sample users."""
    async with AsyncSessionLocal() as session:
        user_service = UserService(session)
        created_users = []

        for user_data in SAMPLE_USERS:
            try:
                user = await user_service.create_user(**user_data)
                created_users.append(user)
                print(f"  ✓ Created user: {user.full_name} ({user.email})")
            except Exception as e:
                print(f"  ✗ Error creating user {user_data['email']}: {e}")

        # Soft delete some users for testing
        if len(created_users) >= 2:
            # Soft delete the last 2 users
            for user in created_users[-2:]:
                await user_service.delete_user(user.id)
                print(f"  ✓ Soft deleted user: {user.full_name}")

        return len(created_users)


async def seed_leads():
    """Seed the database with sample leads."""
    async with AsyncSessionLocal() as session:
        lead_service = LeadService(session)
        created_leads = []

        for i, lead_data in enumerate(SAMPLE_LEADS):
            try:
                # Convert source string to LeadSource enum
                source_value = lead_data.get("source")
                if source_value:
                    # Get the enum member by its value
                    source_enum = LeadSource(source_value)
                else:
                    source_enum = None

                # Convert status string to LeadStatus enum
                status_value = lead_data.get("status", LeadStatus.LEAD.value)
                status_enum = LeadStatus(status_value)

                # Create LeadCreate schema object
                lead_create_data = LeadCreate(
                    first_name=lead_data["first_name"],
                    last_name=lead_data["last_name"],
                    email=lead_data["email"],
                    phone=lead_data.get("phone"),
                    company=lead_data.get("company"),
                    position=lead_data.get("position"),
                    notes=lead_data.get("notes"),
                    source=source_enum,
                    status=status_enum
                )

                # Create the lead using the service
                lead = await lead_service.create_lead(lead_create_data)

                # Update timestamps for clients and prospects after creation
                if lead.status == LeadStatus.CLIENT.value:
                    # Update the lead directly in the repository
                    lead.converted_to_client_at = datetime.utcnow() - timedelta(days=random.randint(10, 180))
                    lead.converted_to_prospect_at = datetime.utcnow() - timedelta(days=random.randint(181, 365))
                    await session.commit()
                elif lead.status == LeadStatus.PROSPECT.value:
                    lead.converted_to_prospect_at = datetime.utcnow() - timedelta(days=random.randint(1, 90))
                    await session.commit()

                created_leads.append(lead)
                print(f"  ✓ Created lead: {lead.full_name} - {lead.company} ({lead.status})")
            except Exception as e:
                print(f"  ✗ Error creating lead {lead_data['email']}: {e}")

        return len(created_leads)


async def main():
    """Main function to run the seed script."""
    print("\n" + "="*60)
    print("🌱 Database Seeding Script")
    print("="*60 + "\n")

    try:
        # Clear existing data
        print("📦 Clearing existing data...")
        await clear_existing_data()

        # Seed users
        print("\n👥 Seeding Users...")
        users_count = await seed_users()
        print(f"  → Created {users_count} users (including {min(2, users_count)} soft-deleted)")

        # Seed leads
        print("\n📋 Seeding Leads...")
        leads_count = await seed_leads()
        print(f"  → Created {leads_count} leads")

        # Summary
        print("\n" + "="*60)
        print("✅ Seeding completed successfully!")
        print(f"   • {users_count} users created")
        print(f"   • {leads_count} leads created")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ Seeding failed: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())