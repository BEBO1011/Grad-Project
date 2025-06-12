import random
from sqlalchemy import extract
import string
import datetime
from database import (
    get_session, User, Vehicle, MaintenanceCenter, Service, 
    MaintenanceAppointment, MaintenanceRecord, SavedLocation,
    VehicleHealthData, ChatSession, ChatMessage
)
from sqlalchemy import func

def get_user_by_email(email):
    """Get a user by their email address"""
    session = get_session()
    try:
        user = session.query(User).filter(User.email == email).first()
        return user
    finally:
        session.close()

def get_user_by_id(user_id):
    """Get a user by their ID"""
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        return user
    finally:
        session.close()
        
def update_user_profile(user_id, name=None, phone=None, preferred_language=None, profile_picture=None):
    """Update a user's profile information"""
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return None, "User not found"
            
        # Update fields if provided
        if name:
            user.name = name
        if phone:
            user.phone = phone
        if preferred_language:
            user.preferred_language = preferred_language
        if profile_picture:
            user.profile_picture = profile_picture
            
        user.updated_at = datetime.datetime.utcnow()
        session.commit()
        return user, None
    except Exception as e:
        session.rollback()
        return None, str(e)
    finally:
        session.close()

def create_user(name, email, password, phone=None, language="en"):
    """Create a new user"""
    session = get_session()
    print('CREATE')
    try:
        # Check if user already exists
        existing_user = session.query(User).filter(User.email == email).first()
        if existing_user:
            return None, "User with this email already exists"
        
        # Create new user
        user = User(
            name=name,
            email=email,
            phone=phone,
            preferred_language=language,
            is_active=True,
            last_login=datetime.datetime.utcnow()
        )
        user.set_password(password)
        session.add(user)
        session.flush()
        session.commit()
        print("User ID after creation:", user.id)
        return user, None
    except Exception as e:
        print(e)
        session.rollback()
        return None, str(e)
    finally:
        session.close()

def authenticate_user(email, password):
    """Authenticate a user with email and password"""
    session = get_session()
    try:
        user = session.query(User).filter(User.email == email).first()
        if not user or not user.check_password(password):
            return None, "Invalid email or password"
        
        # Update last login time
        user.last_login = datetime.datetime.utcnow()
        session.commit()
        
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }, None
    except Exception as e:
        return None, str(e)
    finally:
        session.close()

def add_vehicle(user_id, brand, model, year, vin=None, license_plate=None, color=None, mileage=None, fuel_type=None, transmission=None):
    """Add a vehicle for a user"""
    session = get_session()
    try:
        # Check if user exists
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return None, "User not found"
        
        # Create vehicle
        vehicle = Vehicle(
            user_id=user_id,
            brand=brand,
            model=model,
            year=year,
            vin=vin,
            license_plate=license_plate,
            color=color,
            mileage=mileage,
            fuel_type=fuel_type,
            transmission=transmission
        )
        
        session.add(vehicle)
        session.commit()
        return vehicle, None
    except Exception as e:
        session.rollback()
        return None, str(e)
    finally:
        session.close()

def get_user_vehicles(user_id):
    """Get all vehicles for a user"""
    session = get_session()
    try:
        vehicles = session.query(Vehicle).filter(Vehicle.user_id == user_id).all()
        return vehicles
    finally:
        session.close()
        
def get_vehicle_by_id(vehicle_id):
    """Get a vehicle by ID"""
    session = get_session()
    try:
        vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        return vehicle
    finally:
        session.close()

def get_maintenance_centers(limit=None, offset=0):
    """Get maintenance centers with optional pagination"""
    session = get_session()
    try:
        query = session.query(MaintenanceCenter).order_by(MaintenanceCenter.rating.desc())
        
        if limit:
            query = query.limit(limit).offset(offset)
            
        centers = query.all()
        return centers
    finally:
        session.close()

def get_center_by_id(center_id):
    """Get a maintenance center by ID"""
    session = get_session()
    try:
        center = session.query(MaintenanceCenter).filter(MaintenanceCenter.id == center_id).first()
        return center
    finally:
        session.close()

def get_center_services(center_id):
    """Get services offered by a specific maintenance center"""
    session = get_session()
    try:
        services = session.query(Service).filter(Service.center_id == center_id).all()
        return services
    finally:
        session.close()

def book_appointment(user_id, vehicle_id, center_id, service_id, appointment_date, notes=None):
    """Book a maintenance appointment"""
    session = get_session()
    try:
        # Validate all references exist
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return None, "User not found"
            
        vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id, Vehicle.user_id == user_id).first()
        if not vehicle:
            return None, "Vehicle not found or does not belong to user"
            
        center = session.query(MaintenanceCenter).filter(MaintenanceCenter.id == center_id).first()
        if not center:
            return None, "Maintenance center not found"
            
        service = None
        if service_id:
            service = session.query(Service).filter(Service.id == service_id, Service.center_id == center_id).first()
            if not service:
                return None, "Service not found or not offered by the center"
        
        # Create appointment
        appointment = MaintenanceAppointment(
            user_id=user_id,
            vehicle_id=vehicle_id,
            center_id=center_id,
            service_id=service_id,
            appointment_date=appointment_date,
            status="scheduled",
            notes=notes
        )
        
        session.add(appointment)
        session.commit()
        return {
            "id": appointment.id,
            "user_id": appointment.user_id,
            "vehicle_id": appointment.vehicle_id,
            "center_id": appointment.center_id,
            "service_id": appointment.service_id,
            "appointment_date": appointment.appointment_date.isoformat(),
            "status": appointment.status,
            "notes": appointment.notes
        }, None
    except Exception as e:
        session.rollback()
        return None, str(e)
    finally:
        session.close()

def get_user_appointments(user_id, status=None):
    """Get appointments for a user with optional status filter"""
    session = get_session()
    try:
        query = session.query(MaintenanceAppointment).filter(MaintenanceAppointment.user_id == user_id)
        
        if status:
            query = query.filter(MaintenanceAppointment.status == status)
            
        appointments = query.order_by(MaintenanceAppointment.appointment_date).all()
        return appointments
    finally:
        session.close()

def save_user_location(user_id, name, latitude, longitude, address=None, is_favorite=False):
    """Save a location for a user"""
    session = get_session()
    try:
        # Check if user exists
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return None, "User not found"
        
        # Create saved location
        location = SavedLocation(
            user_id=user_id,
            name=name,
            address=address,
            latitude=latitude,
            longitude=longitude,
            is_favorite=is_favorite
        )
        
        session.add(location)
        session.commit()
        # Convert to dict BEFORE session is closed
        location_dict = {
            'id': location.id,
            'user_id': location.user_id,
            'name': location.name,
            'address': location.address,
            'latitude': location.latitude,
            'longitude': location.longitude,
            'is_favorite': location.is_favorite
        }
        
        return location_dict, None
    except Exception as e:
        session.rollback()
        return None, str(e)
    finally:
        session.close()

def get_user_saved_locations(user_id):
    """Get all saved locations for a user"""
    session = get_session()
    try:
        locations = session.query(SavedLocation).filter(SavedLocation.user_id == user_id).all()
        return locations
    finally:
        session.close()

def save_vehicle_health_data(vehicle_id, data):
    """Save health data for a vehicle"""
    session = get_session()
    try:
        # Check if vehicle exists
        vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            return None, "Vehicle not found"
        
        # Create health data record
        health_data = VehicleHealthData(
            vehicle_id=vehicle_id,
            **data
        )
        
        session.add(health_data)
        session.commit()
        return health_data, None
    except Exception as e:
        session.rollback()
        return None, str(e)
    finally:
        session.close()

def get_vehicle_health_history(vehicle_id, limit=10):
    """Get health history for a vehicle with limit"""
    session = get_session()
    try:
        health_data = session.query(VehicleHealthData)\
            .filter(VehicleHealthData.vehicle_id == vehicle_id)\
            .order_by(VehicleHealthData.timestamp.desc())\
            .limit(limit)\
            .all()
        return health_data
    finally:
        session.close()

def create_chat_session(user_id=None, vehicle_id=None):
    """Create a new chat session"""
    session = get_session()
    try:
        # Generate a unique session key
        session_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
        
        chat_session = ChatSession(
            user_id=user_id,
            vehicle_id=vehicle_id,
            session_key=session_key,
            start_time=datetime.datetime.utcnow(),
            is_active=True
        )
        
        session.add(chat_session)
        session.commit()
        return chat_session
    except Exception as e:
        session.rollback()
        return None
    finally:
        session.close()

def get_chat_session(session_key):
    """Get a chat session by its key"""
    session = get_session()
    try:
        chat_session = session.query(ChatSession).filter(ChatSession.session_key == session_key).first()
        return chat_session
    finally:
        session.close()

def save_chat_message(session_id, message, is_bot=False, language="en"):
    """Save a chat message"""
    session = get_session()
    try:
        chat_message = ChatMessage(
            session_id=session_id,
            message=message,
            is_bot=is_bot,
            timestamp=datetime.datetime.utcnow(),
            language=language
        )
        
        session.add(chat_message)
        session.commit()
        return chat_message
    except Exception as e:
        session.rollback()
        return None
    finally:
        session.close()

def get_chat_messages(session_id):
    """Get all messages for a chat session"""
    session = get_session()
    try:
        messages = session.query(ChatMessage)\
            .filter(ChatMessage.session_id == session_id)\
            .order_by(ChatMessage.timestamp)\
            .all()
        return messages
    finally:
        session.close()

def end_chat_session(session_key):
    """End a chat session"""
    session = get_session()
    try:
        chat_session = session.query(ChatSession).filter(ChatSession.session_key == session_key).first()
        if chat_session:
            chat_session.is_active = False
            chat_session.end_time = datetime.datetime.utcnow()
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()

def get_total_users():
    """Get total number of users."""
    session = get_session()
    try:
        return session.query(User).count()
    finally:
        session.close()

def get_active_appointments():
    """Get number of active appointments."""
    session = get_session()
    try:
        return session.query(MaintenanceAppointment).filter(
            MaintenanceAppointment.status.in_(['pending', 'confirmed'])
        ).count()
    finally:
        session.close()

def get_monthly_revenue():
    """Get total revenue for current month."""
    session = get_session()
    try:
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        return session.query(func.sum(MaintenanceAppointment.cost)).filter(
            extract('month', MaintenanceAppointment.created_at) == current_month,
            extract('year', MaintenanceAppointment.created_at) == current_year
        ).scalar() or 0
    finally:
        session.close()

def get_total_centers():
    """Get total number of service centers."""
    session = get_session()
    try:
        return session.query(MaintenanceCenter).count()
    finally:
        session.close()

def get_recent_appointments(limit=10):
    """Get recent appointments with user and vehicle details."""
    session = get_session()
    try:
        return session.query(MaintenanceAppointment).join(User).join(Vehicle).order_by(
            MaintenanceAppointment.created_at.desc()
        ).limit(limit).all()
    finally:
        session.close()

def get_recent_user_activity(limit=10):
    """Get recent user activities."""
    session = get_session()
    try:
        return session.query(MaintenanceRecord).order_by(
            MaintenanceRecord.created_at.desc()
        ).limit(limit).all()
    finally:
        session.close()

def get_monthly_statistics():
    """Get monthly statistics for users, appointments, and revenue."""
    session = get_session()
    try:
        current_year = datetime.now().year
        
        # Get monthly user registrations
        user_stats = session.query(
            extract('month', User.created_at).label('month'),
            func.count(User.id).label('count')
        ).filter(
            extract('year', User.created_at) == current_year
        ).group_by('month').all()
        
        # Get monthly appointments
        appointment_stats = session.query(
            extract('month', MaintenanceAppointment.created_at).label('month'),
            func.count(MaintenanceAppointment.id).label('count')
        ).filter(
            extract('year', MaintenanceAppointment.created_at) == current_year
        ).group_by('month').all()
        
        # Get monthly revenue
        revenue_stats = session.query(
            extract('month', MaintenanceAppointment.created_at).label('month'),
            func.sum(MaintenanceAppointment.cost).label('total')
        ).filter(
            extract('year', MaintenanceAppointment.created_at) == current_year
        ).group_by('month').all()
        
        # Format the data
        months = range(1, 13)
        return {
            'users': [next((stat.count for stat in user_stats if stat.month == month), 0) for month in months],
            'appointments': [next((stat.count for stat in appointment_stats if stat.month == month), 0) for month in months],
            'revenue': [next((stat.total for stat in revenue_stats if stat.month == month), 0) for month in months]
        }
    finally:
        session.close()