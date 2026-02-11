#!/usr/bin/env python3
"""
Script de inicialización de base de datos para ClientFlow Pro
Crea todas las tablas necesarias
"""
import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import engine, Base
from app.models.models import (
    User, UserRole,
    Professional,
    AvailabilitySlot,
    Appointment, AppointmentStatus,
    Lead, LeadStatus,
    Reminder, ReminderStatus,
    ClientNote,
    StatsDaily
)

def init_database():
    print("🚀 Inicializando base de datos de ClientFlow Pro...")
    print("=" * 50)
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    print("✅ Tablas creadas exitosamente:")
    print("  - users")
    print("  - professionals")
    print("  - availability_slots")
    print("  - appointments")
    print("  - leads")
    print("  - reminders")
    print("  - client_notes")
    print("  - stats_daily")
    
    print("\n" + "=" * 50)
    print("🎉 Base de datos lista!")
    print("\nAhora ejecuta: python scripts/seed_data.py")
    print("para cargar datos de ejemplo.")

if __name__ == "__main__":
    init_database()
