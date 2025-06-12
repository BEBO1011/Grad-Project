import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
import json

DATABASE_URL = os.environ.get('mysql+pymysql://root@localhost:3306/car_service')
engine = create_engine('mysql+pymysql://root@localhost:3306/car_service')

# engine = create_engine('mysql+mysqlconnector://root:@127.0.0.1:3306/car_service')
Base = declarative_base()
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20))
    profile_picture = Column(String(255))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    preferred_language = Column(String(10), default='en')  # For multi-language support
    
    # Relationships
    vehicles = relationship("Vehicle", back_populates="owner", cascade="all, delete-orphan")
    maintenance_appointments = relationship("MaintenanceAppointment", back_populates="user")
    saved_locations = relationship("SavedLocation", back_populates="user")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'preferred_language': self.preferred_language
        }

class Vehicle(Base):
    __tablename__ = 'vehicles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    brand = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    vin = Column(String(17))
    license_plate = Column(String(20))
    color = Column(String(30))
    mileage = Column(Float)
    fuel_type = Column(String(20))
    transmission = Column(String(20))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="vehicles")
    maintenance_records = relationship("MaintenanceRecord", back_populates="vehicle", cascade="all, delete-orphan")
    health_data = relationship("VehicleHealthData", back_populates="vehicle", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'brand': self.brand,
            'model': self.model,
            'year': self.year,
            'vin': self.vin,
            'license_plate': self.license_plate,
            'color': self.color,
            'mileage': self.mileage,
            'fuel_type': self.fuel_type,
            'transmission': self.transmission
        }

class MaintenanceCenter(Base):
    __tablename__ = 'maintenance_centers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(50), nullable=False)
    state = Column(String(50))
    country = Column(String(50), nullable=False)
    postal_code = Column(String(20))
    phone = Column(String(20))
    email = Column(String(120))
    website = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    rating = Column(Float)
    specialties = Column(String(255))  # JSON string of specialties
    hours_of_operation = Column(String(255))  # JSON string of hours
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    appointments = relationship("MaintenanceAppointment", back_populates="center")
    services = relationship("Service", back_populates="center")
    
    def get_specialties(self):
        if self.specialties:
            return json.loads(self.specialties)
        return []
    
    def get_hours(self):
        if self.hours_of_operation:
            return json.loads(self.hours_of_operation)
        return {}
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'rating': self.rating,
            'specialties': self.get_specialties(),
            'hours_of_operation': self.get_hours()
        }

class Service(Base):
    __tablename__ = 'services'
    
    id = Column(Integer, primary_key=True)
    center_id = Column(Integer, ForeignKey('maintenance_centers.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float)
    duration_minutes = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    center = relationship("MaintenanceCenter", back_populates="services")
    maintenance_records = relationship("MaintenanceRecord", back_populates="service")
    
    def to_dict(self):
        return {
            'id': self.id,
            'center_id': self.center_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'duration_minutes': self.duration_minutes
        }

class MaintenanceAppointment(Base):
    __tablename__ = 'maintenance_appointments'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    center_id = Column(Integer, ForeignKey('maintenance_centers.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'))
    appointment_date = Column(DateTime, nullable=False)
    status = Column(String(20), default='scheduled')  # scheduled, confirmed, completed, cancelled
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="maintenance_appointments")
    vehicle = relationship("Vehicle")
    center = relationship("MaintenanceCenter", back_populates="appointments")
    service = relationship("Service")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'vehicle_id': self.vehicle_id,
            'center_id': self.center_id,
            'service_id': self.service_id,
            'appointment_date': self.appointment_date.isoformat(),
            'status': self.status,
            'notes': self.notes
        }

class MaintenanceRecord(Base):
    __tablename__ = 'maintenance_records'
    
    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'))
    service_date = Column(Date, nullable=False)
    mileage = Column(Float)
    description = Column(Text)
    cost = Column(Float)
    performed_by = Column(String(100))
    parts_replaced = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="maintenance_records")
    service = relationship("Service", back_populates="maintenance_records")
    
    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'service_id': self.service_id,
            'service_date': self.service_date.isoformat(),
            'mileage': self.mileage,
            'description': self.description,
            'cost': self.cost,
            'performed_by': self.performed_by,
            'parts_replaced': self.parts_replaced
        }

class SavedLocation(Base):
    __tablename__ = 'saved_locations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    address = Column(String(255))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="saved_locations")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'is_favorite': self.is_favorite
        }

class VehicleHealthData(Base):
    __tablename__ = 'vehicle_health_data'
    
    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    engine_status = Column(String(20))
    oil_level = Column(Float)
    coolant_level = Column(Float)
    brake_fluid_level = Column(Float)
    tire_pressure_front_left = Column(Float)
    tire_pressure_front_right = Column(Float)
    tire_pressure_rear_left = Column(Float)
    tire_pressure_rear_right = Column(Float)
    battery_health = Column(Float)
    fuel_level = Column(Float)
    mileage = Column(Float)
    engine_temperature = Column(Float)
    check_engine_light = Column(Boolean, default=False)
    diagnostic_codes = Column(String(255))  # JSON string of codes
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="health_data")
    
    def get_diagnostic_codes(self):
        if self.diagnostic_codes:
            return json.loads(self.diagnostic_codes)
        return []
    
    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'timestamp': self.timestamp.isoformat(),
            'engine_status': self.engine_status,
            'oil_level': self.oil_level,
            'coolant_level': self.coolant_level,
            'brake_fluid_level': self.brake_fluid_level,
            'tire_pressure_front_left': self.tire_pressure_front_left,
            'tire_pressure_front_right': self.tire_pressure_front_right,
            'tire_pressure_rear_left': self.tire_pressure_rear_left,
            'tire_pressure_rear_right': self.tire_pressure_rear_right,
            'battery_health': self.battery_health,
            'fuel_level': self.fuel_level,
            'mileage': self.mileage,
            'engine_temperature': self.engine_temperature,
            'check_engine_light': self.check_engine_light,
            'diagnostic_codes': self.get_diagnostic_codes()
        }

class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    session_key = Column(String(50), nullable=False, unique=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User")
    vehicle = relationship("Vehicle")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_key': self.session_key,
            'vehicle_id': self.vehicle_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_active': self.is_active
        }

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('chat_sessions.id'), nullable=False)
    is_bot = Column(Boolean, default=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    language = Column(String(10))  # Language the message was sent in
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'is_bot': self.is_bot,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'language': self.language
        }

def init_db():
    """Initialize the database by creating all tables"""
    Base.metadata.create_all(engine)

def get_session():
    """Get a new database session"""
    return Session()