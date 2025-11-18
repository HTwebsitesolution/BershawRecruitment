"""
Calendar Integration Service

Handles calendar integrations for automated interview scheduling.
Supports multiple providers: Google Calendar, Calendly, Outlook.
"""

from __future__ import annotations
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from uuid import UUID
import json

logger = logging.getLogger(__name__)

# Calendar provider types
CalendarProvider = str  # "google", "calendly", "outlook", "manual"


class CalendarService:
    """
    Calendar integration service for interview scheduling.
    
    Supports multiple calendar providers:
    - Google Calendar (via API)
    - Calendly (via API)
    - Outlook Calendar (via Microsoft Graph API)
    - Manual booking links (Calendly-style)
    """
    
    def __init__(self):
        # Load API keys from settings
        from app.settings import settings
        self.google_calendar_enabled = bool(settings.google_calendar_api_key)
        self.calendly_enabled = bool(settings.calendly_api_key)
        self.outlook_enabled = bool(settings.microsoft_graph_client_id)
        
        # Store settings for use in methods
        self.settings = settings
    
    def create_booking_link(
        self,
        profile_id: UUID,
        candidate_email: str,
        candidate_name: str,
        duration_minutes: int = 30,
        provider: CalendarProvider = "calendly",
        preferred_times: Optional[List[datetime]] = None,
        timezone: str = "Europe/London"
    ) -> Dict[str, Any]:
        """
        Create a booking link for interview scheduling.
        
        Args:
            profile_id: Candidate profile ID
            candidate_email: Candidate email
            candidate_name: Candidate name
            duration_minutes: Interview duration
            provider: Calendar provider ("google", "calendly", "outlook", "manual")
            preferred_times: List of preferred time slots
            timezone: Timezone for scheduling
        
        Returns:
            Dict with booking_link, booking_id, and metadata
        """
        if provider == "calendly":
            return self._create_calendly_link(
                profile_id, candidate_email, candidate_name, duration_minutes, preferred_times, timezone
            )
        elif provider == "google":
            return self._create_google_calendar_link(
                profile_id, candidate_email, candidate_name, duration_minutes, preferred_times, timezone
            )
        elif provider == "outlook":
            return self._create_outlook_calendar_link(
                profile_id, candidate_email, candidate_name, duration_minutes, preferred_times, timezone
            )
        elif provider == "manual":
            return self._create_manual_booking_link(
                profile_id, candidate_email, candidate_name, duration_minutes
            )
        else:
            raise ValueError(f"Unsupported calendar provider: {provider}")
    
    def _create_calendly_link(
        self,
        profile_id: UUID,
        candidate_email: str,
        candidate_name: str,
        duration_minutes: int,
        preferred_times: Optional[List[datetime]],
        timezone: str
    ) -> Dict[str, Any]:
        """
        Create a Calendly booking link.
        
        Requires:
        - CALENDLY_API_KEY in environment
        - CALENDLY_EVENT_TYPE_URI (your Calendly event type)
        """
        # Placeholder implementation
        # In production, integrate with Calendly API:
        # https://developer.calendly.com/api-docs
        
        booking_id = f"calendly_{profile_id}_{datetime.utcnow().timestamp()}"
        
        # Generate Calendly-style booking link
        # Format: https://calendly.com/{username}/{event-type}?name={name}&email={email}
        calendly_username = self.settings.calendly_username
        event_type = self.settings.calendly_event_type
        
        booking_link = (
            f"https://calendly.com/{calendly_username}/{event_type}"
            f"?name={candidate_name.replace(' ', '%20')}"
            f"&email={candidate_email}"
            f"&duration={duration_minutes}"
        )
        
        logger.info(f"Created Calendly booking link for profile {profile_id}")
        
        return {
            "booking_link": booking_link,
            "booking_id": booking_id,
            "provider": "calendly",
            "duration_minutes": duration_minutes,
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "metadata": {
                "candidate_email": candidate_email,
                "candidate_name": candidate_name,
                "timezone": timezone
            }
        }
    
    def _create_google_calendar_link(
        self,
        profile_id: UUID,
        candidate_email: str,
        candidate_name: str,
        duration_minutes: int,
        preferred_times: Optional[List[datetime]],
        timezone: str
    ) -> Dict[str, Any]:
        """
        Create a Google Calendar booking link.
        
        Requires:
        - GOOGLE_CALENDAR_API_KEY in environment
        - GOOGLE_CALENDAR_ID in environment
        """
        # Placeholder implementation
        # In production, integrate with Google Calendar API:
        # https://developers.google.com/calendar/api
        
        booking_id = f"google_{profile_id}_{datetime.utcnow().timestamp()}"
        
        # Generate Google Calendar link
        # Format: https://calendar.google.com/calendar/u/0/r/eventedit?dates={start}/{end}&text={title}&details={details}
        
        # For now, return a manual booking link
        # In production, create event via API and return event link
        booking_link = f"https://calendar.google.com/calendar/u/0/r/eventedit?dates=TBD&text=Interview with {candidate_name}"
        
        logger.info(f"Created Google Calendar booking link for profile {profile_id}")
        
        return {
            "booking_link": booking_link,
            "booking_id": booking_id,
            "provider": "google",
            "duration_minutes": duration_minutes,
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "metadata": {
                "candidate_email": candidate_email,
                "candidate_name": candidate_name,
                "timezone": timezone,
                "preferred_times": [t.isoformat() for t in (preferred_times or [])]
            }
        }
    
    def _create_outlook_calendar_link(
        self,
        profile_id: UUID,
        candidate_email: str,
        candidate_name: str,
        duration_minutes: int,
        preferred_times: Optional[List[datetime]],
        timezone: str
    ) -> Dict[str, Any]:
        """
        Create an Outlook Calendar booking link.
        
        Requires:
        - MICROSOFT_GRAPH_CLIENT_ID in environment
        - MICROSOFT_GRAPH_CLIENT_SECRET in environment
        """
        # Placeholder implementation
        # In production, integrate with Microsoft Graph API:
        # https://docs.microsoft.com/en-us/graph/api/resources/calendar
        
        booking_id = f"outlook_{profile_id}_{datetime.utcnow().timestamp()}"
        
        # Generate Outlook Calendar link
        booking_link = f"https://outlook.live.com/calendar/0/deeplink/compose?subject=Interview with {candidate_name}"
        
        logger.info(f"Created Outlook Calendar booking link for profile {profile_id}")
        
        return {
            "booking_link": booking_link,
            "booking_id": booking_id,
            "provider": "outlook",
            "duration_minutes": duration_minutes,
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "metadata": {
                "candidate_email": candidate_email,
                "candidate_name": candidate_name,
                "timezone": timezone
            }
        }
    
    def _create_manual_booking_link(
        self,
        profile_id: UUID,
        candidate_email: str,
        candidate_name: str,
        duration_minutes: int
    ) -> Dict[str, Any]:
        """
        Create a manual booking link (for custom scheduling systems).
        """
        booking_id = f"manual_{profile_id}_{datetime.utcnow().timestamp()}"
        
        # Generate a generic booking link
        # In production, integrate with your custom scheduling system
        base_url = "https://bershaw-recruitment.com/schedule"  # Should come from settings
        booking_link = f"{base_url}?profile_id={profile_id}&email={candidate_email}"
        
        logger.info(f"Created manual booking link for profile {profile_id}")
        
        return {
            "booking_link": booking_link,
            "booking_id": booking_id,
            "provider": "manual",
            "duration_minutes": duration_minutes,
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "metadata": {
                "candidate_email": candidate_email,
                "candidate_name": candidate_name
            }
        }
    
    def cancel_booking(
        self,
        booking_id: str,
        provider: CalendarProvider
    ) -> bool:
        """
        Cancel a scheduled interview booking.
        
        Args:
            booking_id: Booking ID from create_booking_link
            provider: Calendar provider
        
        Returns:
            True if cancelled successfully
        """
        logger.info(f"Cancelling booking {booking_id} on {provider}")
        
        # In production, call provider API to cancel booking
        # For now, just log the cancellation
        
        return True
    
    def get_booking_status(
        self,
        booking_id: str,
        provider: CalendarProvider
    ) -> Dict[str, Any]:
        """
        Get the status of a booking.
        
        Args:
            booking_id: Booking ID
            provider: Calendar provider
        
        Returns:
            Dict with booking status and details
        """
        # Placeholder implementation
        # In production, query provider API for booking status
        
        return {
            "booking_id": booking_id,
            "status": "pending",  # pending, confirmed, cancelled, completed
            "provider": provider,
            "booked_time": None,
            "timezone": "Europe/London"
        }


# Initialize calendar service
calendar_service = CalendarService()

