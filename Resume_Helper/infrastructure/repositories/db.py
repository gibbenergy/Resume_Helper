"""
SQLAlchemy Database Models for Job Applications

This module defines the database schema using SQLAlchemy ORM.
Replaces JSON file storage with proper relational database.
"""

from sqlalchemy import (
    create_engine, Column, String, Integer, Text, DateTime, JSON, 
    ForeignKey, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class Application(Base):
    """Main application table - stores job application data."""
    
    __tablename__ = 'applications'
    
    # Primary key (hash of job_url)
    id = Column(String(16), primary_key=True)
    
    # Required fields
    job_url = Column(String(500), nullable=False, unique=True, index=True)
    company = Column(String(100), nullable=False, index=True)
    position = Column(String(100), nullable=False, index=True)
    
    # Optional core fields
    location = Column(String(500))
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    date_applied = Column(String(20), index=True)  # ISO format: YYYY-MM-DD
    application_source = Column(String(50), index=True)
    priority = Column(String(20), default='Medium', index=True)
    status = Column(String(50), default='Applied', index=True)
    
    # Text fields
    description = Column(Text)
    notes = Column(Text)
    
    # Metadata fields
    match_score = Column(Integer)
    
    # Contact information
    hr_contact = Column(String(100))
    hiring_manager = Column(String(100))
    recruiter = Column(String(100))
    referral = Column(String(100))
    
    # JSON fields for complex data
    requirements = Column(JSON, default=list)
    analysis_data = Column(JSON, default=dict)  # AI analysis results
    interview_pipeline = Column(JSON, default=dict)  # Interview rounds
    timeline = Column(JSON, default=list)
    next_actions = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    
    # Timestamps
    created_date = Column(DateTime, default=datetime.now, nullable=False)
    last_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relationships
    documents = relationship("Document", back_populates="application", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_company_status', 'company', 'status'),
        Index('idx_status_priority', 'status', 'priority'),
        Index('idx_date_applied', 'date_applied'),
    )
    
    def to_dict(self):
        """Convert to dictionary format."""
        return {
            'id': self.id,
            'job_url': self.job_url,
            'company': self.company,
            'position': self.position,
            'location': self.location,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'date_applied': self.date_applied,
            'application_source': self.application_source,
            'priority': self.priority,
            'status': self.status,
            'description': self.description,
            'notes': self.notes,
            'match_score': self.match_score,
            'hr_contact': self.hr_contact,
            'hiring_manager': self.hiring_manager,
            'recruiter': self.recruiter,
            'referral': self.referral,
            'requirements': self.requirements or [],
            'analysis_data': self.analysis_data or {},
            'interview_pipeline': self.interview_pipeline or {},
            'timeline': self.timeline or [],
            'next_actions': self.next_actions or [],
            'tags': self.tags or [],
            'documents': [doc.to_dict() for doc in self.documents],
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


class Document(Base):
    """Document table - stores uploaded documents for applications."""
    
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String(16), ForeignKey('applications.id'), nullable=False, index=True)
    
    name = Column(String(100), nullable=False)
    type = Column(String(50))  # resume, cover_letter, etc.
    path = Column(String(500), nullable=False)
    upload_date = Column(DateTime, default=datetime.now, nullable=False)
    size = Column(Integer, default=0)
    
    # Relationship
    application = relationship("Application", back_populates="documents")
    
    def to_dict(self):
        """Convert to dictionary format."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'path': self.path,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'size': self.size
        }


class Settings(Base):
    """Settings table - stores application settings."""
    
    __tablename__ = 'settings'
    
    key = Column(String(100), primary_key=True)
    value = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


def init_database(db_path: str = None):
    """
    Initialize database and create all tables.
    
    Args:
        db_path: Path to SQLite database file. Defaults to data/applications.db
        
    Returns:
        tuple: (engine, SessionLocal) for database operations
    """
    if db_path is None:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(project_root, 'data')
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, 'applications.db')
    
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    
    return engine, SessionLocal


def get_default_settings():
    """Get default settings for the application."""
    return {
        'default_interview_rounds': [
            'phone_screen', 'technical', 'panel',
            'manager', 'culture_fit', 'final_round'
        ],
        'application_sources': [
            'LinkedIn', 'Company Website', 'Indeed',
            'Glassdoor', 'Referral', 'Recruiter', 'AI Analysis', 'Other'
        ],
        'priority_levels': ['High', 'Medium', 'Low'],
        'status_options': [
            'Applied', 'Offer', 'Rejected', 'Withdrawn'
        ],
        'interview_statuses': [
            'not_started', 'scheduled', 'completed',
            'passed', 'failed', 'cancelled'
        ]
    }

