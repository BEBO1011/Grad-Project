import os
import json
import datetime
from database import init_db, get_session, User, Vehicle, MaintenanceCenter, Service

def seed_maintenance_centers(session):
    """Add sample maintenance centers to the database"""
    
    centers = [
        {
            "name": "CService Premium Auto Care",
            "address": "123 Luxury Lane",
            "city": "Dubai",
            "state": "Dubai",
            "country": "UAE",
            "postal_code": "12345",
            "phone": "+971 4 123 4567",
            "email": "info@cservice-premium.com",
            "website": "https://cservice-premium.com",
            "latitude": 25.2048,
            "longitude": 55.2708,
            "rating": 4.9,
            "specialties": json.dumps(["BMW", "Mercedes", "Audi", "Porsche"]),
            "hours_of_operation": json.dumps({
                "Monday": "8:00 AM - 8:00 PM",
                "Tuesday": "8:00 AM - 8:00 PM",
                "Wednesday": "8:00 AM - 8:00 PM",
                "Thursday": "8:00 AM - 8:00 PM",
                "Friday": "8:00 AM - 6:00 PM",
                "Saturday": "9:00 AM - 5:00 PM",
                "Sunday": "Closed"
            })
        },
        {
            "name": "Luxury Motors Service Center",
            "address": "456 Elite Boulevard",
            "city": "Abu Dhabi",
            "state": "Abu Dhabi",
            "country": "UAE",
            "postal_code": "54321",
            "phone": "+971 2 987 6543",
            "email": "service@luxurymotors.com",
            "website": "https://luxurymotors.com",
            "latitude": 24.4539,
            "longitude": 54.3773,
            "rating": 4.8,
            "specialties": json.dumps(["Bentley", "Rolls Royce", "Ferrari", "Lamborghini"]),
            "hours_of_operation": json.dumps({
                "Monday": "9:00 AM - 7:00 PM",
                "Tuesday": "9:00 AM - 7:00 PM",
                "Wednesday": "9:00 AM - 7:00 PM",
                "Thursday": "9:00 AM - 7:00 PM",
                "Friday": "9:00 AM - 5:00 PM",
                "Saturday": "10:00 AM - 4:00 PM",
                "Sunday": "Closed"
            })
        },
        {
            "name": "Executive Auto Clinic",
            "address": "789 Premium Plaza",
            "city": "Sharjah",
            "state": "Sharjah",
            "country": "UAE",
            "postal_code": "67890",
            "phone": "+971 6 345 6789",
            "email": "appointments@executiveautoclinic.com",
            "website": "https://executiveautoclinic.com",
            "latitude": 25.3463,
            "longitude": 55.4209,
            "rating": 4.7,
            "specialties": json.dumps(["Jaguar", "Land Rover", "Lexus", "Infiniti"]),
            "hours_of_operation": json.dumps({
                "Monday": "8:30 AM - 7:30 PM",
                "Tuesday": "8:30 AM - 7:30 PM",
                "Wednesday": "8:30 AM - 7:30 PM",
                "Thursday": "8:30 AM - 7:30 PM",
                "Friday": "8:30 AM - 5:30 PM",
                "Saturday": "9:30 AM - 3:30 PM",
                "Sunday": "Closed"
            })
        }
    ]
    
    for center_data in centers:
        center = MaintenanceCenter(**center_data)
        session.add(center)
    
    session.commit()
    return len(centers)

def seed_services(session):
    """Add sample services to the database"""
    
    # Get all centers
    centers = session.query(MaintenanceCenter).all()
    if not centers:
        return 0
    
    services_count = 0
    
    # Common services for all centers
    common_services = [
        {
            "name": "Premium Oil Change",
            "description": "Full synthetic oil change with premium filter and multi-point inspection",
            "price": 199.99,
            "duration_minutes": 60
        },
        {
            "name": "Brake System Service",
            "description": "Complete brake pad replacement, rotor inspection, and brake fluid flush",
            "price": 499.99,
            "duration_minutes": 120
        },
        {
            "name": "Comprehensive Vehicle Inspection",
            "description": "150-point inspection of all vehicle systems with detailed report",
            "price": 299.99,
            "duration_minutes": 90
        },
        {
            "name": "Engine Diagnostic",
            "description": "Advanced computerized diagnostics with AI-powered analysis",
            "price": 249.99,
            "duration_minutes": 75
        },
        {
            "name": "Luxury Detail Package",
            "description": "Complete interior and exterior detailing with premium products",
            "price": 349.99,
            "duration_minutes": 180
        }
    ]
    
    # Add common services to all centers
    for center in centers:
        for service_data in common_services:
            service = Service(center_id=center.id, **service_data)
            session.add(service)
            services_count += 1
    
    # Specialized services per center
    specialized_services = {
        1: [  # First center (index 0)
            {
                "name": "European Vehicle Computer Programming",
                "description": "Advanced ECU reprogramming for European luxury vehicles",
                "price": 599.99,
                "duration_minutes": 120
            },
            {
                "name": "German Sport Suspension Tuning",
                "description": "Performance-focused suspension adjustment for German sport sedans",
                "price": 799.99,
                "duration_minutes": 240
            }
        ],
        2: [  # Second center (index 1)
            {
                "name": "Exotic Vehicle Maintenance",
                "description": "Specialized maintenance for exotic sports cars",
                "price": 1299.99,
                "duration_minutes": 180
            },
            {
                "name": "Custom Interior Upholstery",
                "description": "Premium leather upholstery restoration and customization",
                "price": 2499.99,
                "duration_minutes": 480
            }
        ],
        3: [  # Third center (index 2)
            {
                "name": "British and Japanese Diagnostics",
                "description": "Specialized diagnostics for British and Japanese luxury vehicles",
                "price": 449.99,
                "duration_minutes": 120
            },
            {
                "name": "Off-Road Performance Package",
                "description": "Comprehensive service and adjustment for luxury off-road vehicles",
                "price": 899.99,
                "duration_minutes": 300
            }
        ]
    }
    
    # Add specialized services to respective centers
    for center_id, services in specialized_services.items():
        for service_data in services:
            service = Service(center_id=center_id, **service_data)
            session.add(service)
            services_count += 1
    
    session.commit()
    return services_count

def create_admin_user(session):
    """Create an admin user for testing"""
    admin = User(
        name="Admin User",
        email="admin@cservice.com",
        phone="+1 123-456-7890",
        profile_picture="/static/images/user-profile.jpg",
        preferred_language="en",
        is_active=True,
        last_login=datetime.datetime.utcnow()
    )
    admin.set_password("Admin123!")
    
    # Add a vehicle for the admin
    admin_vehicle = Vehicle(
        brand="BMW",
        model="7 Series",
        year=2023,
        vin="WBAYF8C54DDX12345",
        license_plate="ADMIN1",
        color="Black",
        mileage=5000.0,
        fuel_type="Gasoline",
        transmission="Automatic"
    )
    
    admin.vehicles.append(admin_vehicle)
    session.add(admin)
    session.commit()
    
    return admin.id

def main():
    """Initialize and seed the database"""
    print("Initializing database...")
    init_db()
    
    session = get_session()
    try:
        print("Seeding maintenance centers...")
        centers_count = seed_maintenance_centers(session)
        print(f"Added {centers_count} maintenance centers.")
        
        print("Seeding services...")
        services_count = seed_services(session)
        print(f"Added {services_count} services.")
        
        print("Creating admin user...")
        admin_id = create_admin_user(session)
        print(f"Created admin user with ID: {admin_id}")
        
        print("Database initialization complete.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main()