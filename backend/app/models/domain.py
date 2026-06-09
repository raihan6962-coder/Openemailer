import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class Domain(Base, TimestampMixin):
    __tablename__ = "domains"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid, index=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    spf_status: Mapped[str] = mapped_column(String(50), default="pending")
    dkim_status: Mapped[str] = mapped_column(String(50), default="pending")
    dmarc_status: Mapped[str] = mapped_column(String(50), default="pending")
    mx_status: Mapped[str] = mapped_column(String(50), default="pending")
    deliverability_score: Mapped[int] = mapped_column(Integer, default=0)
    reputation_score: Mapped[int] = mapped_column(Integer, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_checked: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    dns_records = relationship("DNSRecord", back_populates="domain", cascade="all, delete-orphan")
    health_records = relationship("DomainHealth", back_populates="domain", cascade="all, delete-orphan")


class DNSRecord(Base):
    __tablename__ = "dns_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    domain_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("domains.id"), nullable=False, index=True)
    record_type: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    ttl: Mapped[int] = mapped_column(Integer, default=3600)
    priority: Mapped[int] = mapped_column(Integer, nullable=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=False)
    last_checked: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    domain = relationship("Domain", back_populates="dns_records")


class DomainHealth(Base):
    __tablename__ = "domain_health"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    domain_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("domains.id"), nullable=False, index=True)
    spf_valid: Mapped[bool] = mapped_column(Boolean, default=False)
    dkim_valid: Mapped[bool] = mapped_column(Boolean, default=False)
    dmarc_valid: Mapped[bool] = mapped_column(Boolean, default=False)
    mx_valid: Mapped[bool] = mapped_column(Boolean, default=False)
    spf_record: Mapped[str] = mapped_column(Text, nullable=True)
    dkim_record: Mapped[str] = mapped_column(Text, nullable=True)
    dmarc_record: Mapped[str] = mapped_column(Text, nullable=True)
    mx_records: Mapped[str] = mapped_column(Text, nullable=True)
    health_score: Mapped[int] = mapped_column(Integer, default=0)
    issues: Mapped[str] = mapped_column(Text, nullable=True)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    domain = relationship("Domain", back_populates="health_records")
