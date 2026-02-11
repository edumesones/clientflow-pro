#!/usr/bin/env python3
"""
Script para cargar datos de ejemplo/demo en ClientFlow Pro
"""
import sys
import os
from datetime import datetime, date, time, timedelta

# Agregar el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.models import (
    User, UserRole,
    Professional,
    AvailabilitySlot,
    Appointment, AppointmentStatus,
    Lead, LeadStatus,
    ClientNote
)

def seed_data():
    print("🌱 Cargando datos de ejemplo...")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Verificar si ya hay datos
        if db.query(User).first():
            print("⚠️  La base de datos ya contiene datos.")
            response = input("¿Deseas borrar todo y recargar? (s/N): ")
            if response.lower() != 's':
                print("Cancelado.")
                return
            
            # Borrar datos existentes
            db.query(ClientNote).delete()
            db.query(Appointment).delete()
            db.query(Lead).delete()
            db.query(AvailabilitySlot).delete()
            db.query(Professional).delete()
            db.query(User).delete()
            db.commit()
            print("🗑️  Datos anteriores eliminados.")
        
        # 1. Crear usuario admin
        print("\n👤 Creando usuario admin...")
        admin = User(
            email="admin@clientflow.pro",
            hashed_password=get_password_hash("admin123"),
            full_name="Administrador",
            phone="+1234567890",
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        db.commit()
        print(f"   ✓ Admin: {admin.email} / admin123")
        
        # 2. Crear usuario profesional de demo
        print("\n👨‍⚕️ Creando profesional de demo...")
        prof_user = User(
            email="demo@clientflow.pro",
            hashed_password=get_password_hash("demo123"),
            full_name="Dr. Ana García",
            phone="+5215512345678",
            role=UserRole.PROFESSIONAL,
            is_active=True
        )
        db.add(prof_user)
        db.commit()
        
        professional = Professional(
            user_id=prof_user.id,
            slug="dr-ana-garcia",
            bio="Especialista en atención personalizada con más de 10 años de experiencia.",
            specialty="Consultoría Profesional",
            timezone="America/Mexico_City",
            appointment_duration=60,
            buffer_time=15,
            advance_booking_days=30,
            is_accepting_appointments=True
        )
        db.add(professional)
        db.commit()
        print(f"   ✓ Profesional: {prof_user.email} / demo123")
        print(f"   ✓ URL pública: /book/{professional.slug}")
        
        # 3. Crear disponibilidad (Lunes a Viernes, 9:00 - 18:00)
        print("\n📅 Configurando disponibilidad...")
        for day in range(5):  # 0=Lunes, 4=Viernes
            slot = AvailabilitySlot(
                professional_id=professional.id,
                day_of_week=day,
                start_time=time(9, 0),
                end_time=time(18, 0),
                is_active=True
            )
            db.add(slot)
        db.commit()
        print("   ✓ Horario: Lunes a Viernes, 9:00 - 18:00")
        
        # 4. Crear clientes de ejemplo
        print("\n👥 Creando clientes de ejemplo...")
        clients = [
            ("María López", "maria@ejemplo.com", "+5215511111111"),
            ("Juan Pérez", "juan@ejemplo.com", "+5215522222222"),
            ("Carlos Ruiz", "carlos@ejemplo.com", "+5215533333333"),
        ]
        
        created_clients = []
        for name, email, phone in clients:
            client = User(
                email=email,
                hashed_password=get_password_hash("password123"),
                full_name=name,
                phone=phone,
                role=UserRole.CLIENT,
                is_active=True
            )
            db.add(client)
            db.commit()
            created_clients.append(client)
            print(f"   ✓ {name}")
        
        # 5. Crear citas de ejemplo
        print("\n📆 Creando citas de ejemplo...")
        today = date.today()
        
        appointments_data = [
            (today + timedelta(days=1), time(10, 0), created_clients[0], "Consulta inicial", 100.0, AppointmentStatus.CONFIRMED),
            (today + timedelta(days=2), time(14, 0), created_clients[1], "Seguimiento", 80.0, AppointmentStatus.CONFIRMED),
            (today - timedelta(days=2), time(11, 0), created_clients[2], "Revisión", 120.0, AppointmentStatus.COMPLETED),
            (today - timedelta(days=5), time(16, 0), None, "Consulta", 100.0, AppointmentStatus.NO_SHOW),
        ]
        
        for appt_date, appt_time, client, service, price, status in appointments_data:
            appointment = Appointment(
                professional_id=professional.id,
                client_id=client.id if client else None,
                lead_name="Pedro Sánchez" if not client else None,
                lead_email="pedro@ejemplo.com" if not client else None,
                lead_phone="+5215544444444" if not client else None,
                appointment_date=appt_date,
                start_time=appt_time,
                end_time=time(appt_time.hour + 1, appt_time.minute),
                service_type=service,
                price=price,
                status=status,
                notes="Cita de ejemplo"
            )
            db.add(appointment)
        db.commit()
        print(f"   ✓ {len(appointments_data)} citas creadas")
        
        # 6. Crear leads de ejemplo
        print("\n🎯 Creando leads de ejemplo...")
        leads_data = [
            ("Laura Martínez", "laura@ejemplo.com", "+5215555555555", LeadStatus.NEW, today - timedelta(days=1)),
            ("Roberto Díaz", "roberto@ejemplo.com", "+5215566666666", LeadStatus.CONTACTED, today - timedelta(days=4)),
            ("Sofia Hernández", "sofia@ejemplo.com", "+5215577777777", LeadStatus.CONVERTED, today - timedelta(days=10)),
            ("Miguel Torres", "miguel@ejemplo.com", "+5215588888888", LeadStatus.FOLLOWED_UP, today - timedelta(days=6)),
        ]
        
        for name, email, phone, status, created in leads_data:
            lead = Lead(
                professional_id=professional.id,
                name=name,
                email=email,
                phone=phone,
                source="web",
                status=status,
                created_at=datetime.combine(created, datetime.min.time()),
                first_contact_date=datetime.combine(created, datetime.min.time())
            )
            db.add(lead)
        db.commit()
        print(f"   ✓ {len(leads_data)} leads creados")
        
        # 7. Crear notas de cliente
        print("\n📝 Creando notas de ejemplo...")
        note = ClientNote(
            professional_id=professional.id,
            client_id=created_clients[0].id,
            content="Cliente interesado en servicio premium. Buena comunicación.",
            next_steps="Enviar propuesta detallada",
            follow_up_date=today + timedelta(days=3)
        )
        db.add(note)
        db.commit()
        print("   ✓ Notas creadas")
        
        print("\n" + "=" * 50)
        print("🎉 Datos de ejemplo cargados exitosamente!")
        print("\nCredenciales de acceso:")
        print("  👤 Admin:    admin@clientflow.pro / admin123")
        print("  👨‍⚕️ Profesional: demo@clientflow.pro / demo123")
        print("\nURLs importantes:")
        print("  📊 Dashboard: http://localhost:3000/admin")
        print(f"  📅 Reserva pública: http://localhost:3000/book/{professional.slug}")
        print("  📚 API Docs: http://localhost:8000/docs")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
