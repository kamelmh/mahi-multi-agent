from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Index, String, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_users_email', 'email'),
    )

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(String(100), nullable=False)
    type = Column(Enum('expense', 'income', name='category_type'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_categories_user_id', 'user_id'),
        Index('idx_categories_user_id_name', 'user_id', 'name'),
    )

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id', ondelete='RESTRICT'), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    date = Column(Date, nullable=False, index=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_transactions_user_id_date', 'user_id', 'date'),
        Index('idx_transactions_category_id', 'category_id'),
    )

class Budget(Base):
    __tablename__ = 'budgets'
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id', ondelete='RESTRICT'), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    period = Column(Enum('monthly', 'weekly', name='budget_period'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    __table_args__ = (
        Index('idx_budgets_user_id', 'user_id'),
        Index('idx_budgets_category_id', 'category_id'),
        Index('idx_budgets_user_id_period', 'user_id', 'period'),
        Index('idx_buddates_date_range', 'start_date', 'end_date'),
    )