"""Enumerations used across the application."""
import enum


class LeadStatus(str, enum.Enum):
    """Lead status enum for tracking pipeline stages."""
    LEAD = "lead"
    PROSPECT = "prospect"
    CLIENT = "client"
    LOST = "lost"


class LeadSource(str, enum.Enum):
    """Lead source enum for tracking origin."""
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    PHONE = "phone"
    EVENT = "event"
    OTHER = "other"