"""Phorest API client for salon management operations."""

import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, date, time
import logging
from app.config import settings
import base64

logger = logging.getLogger(__name__)


class PhorestService:
    """Service for interacting with Phorest salon management API."""

    def __init__(self):
        """Initialize Phorest API client."""
        self.base_url = "https://api.phorest.com/third-party-api-server/api/business"
        self.branch_id = settings.PHOREST_BRANCH_ID
        self.client_id = settings.PHOREST_CLIENT_ID
        self.client_secret = settings.PHOREST_CLIENT_SECRET

        # Create Basic Auth credentials
        credentials = f"{self.client_id}:{self.client_secret}"
        self.auth_header = base64.b64encode(credentials.encode()).decode()

        self.headers = {
            "Authorization": f"Basic {self.auth_header}",
            "Content-Type": "application/json"
        }

    async def get_services(self) -> List[Dict[str, Any]]:
        """
        Get list of available services from Phorest.

        Returns:
            List of services with details
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{self.branch_id}/service",
                    headers=self.headers,
                    timeout=10.0
                )

                response.raise_for_status()
                data = response.json()

                services = []
                for service in data.get("_embedded", {}).get("services", []):
                    services.append({
                        "id": service.get("serviceId"),
                        "name": service.get("serviceName"),
                        "duration": service.get("serviceDuration"),
                        "price": service.get("servicePrice"),
                        "category": service.get("serviceCategory")
                    })

                logger.info(f"Retrieved {len(services)} services from Phorest")
                return services

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching services: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error fetching services: {str(e)}")
            raise

    async def get_staff(self) -> List[Dict[str, Any]]:
        """
        Get list of staff members.

        Returns:
            List of staff with their details
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{self.branch_id}/staff",
                    headers=self.headers,
                    timeout=10.0
                )

                response.raise_for_status()
                data = response.json()

                staff = []
                for member in data.get("_embedded", {}).get("staff", []):
                    staff.append({
                        "id": member.get("staffId"),
                        "name": member.get("staffName"),
                        "email": member.get("staffEmail"),
                        "active": member.get("isActive", True)
                    })

                logger.info(f"Retrieved {len(staff)} staff members from Phorest")
                return staff

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching staff: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error fetching staff: {str(e)}")
            raise

    async def check_availability(
        self,
        service_id: str,
        requested_date: date,
        staff_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Check available appointment slots.

        Args:
            service_id: ID of the service
            requested_date: Date to check availability
            staff_id: Optional specific staff member

        Returns:
            List of available time slots
        """
        try:
            params = {
                "serviceId": service_id,
                "date": requested_date.isoformat()
            }

            if staff_id:
                params["staffId"] = staff_id

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{self.branch_id}/appointment/availability",
                    headers=self.headers,
                    params=params,
                    timeout=10.0
                )

                response.raise_for_status()
                data = response.json()

                # Parse available slots
                available_slots = []
                for slot in data.get("availableSlots", []):
                    available_slots.append({
                        "time": slot.get("time"),
                        "staff_id": slot.get("staffId"),
                        "staff_name": slot.get("staffName")
                    })

                logger.info(f"Found {len(available_slots)} available slots for {requested_date}")
                return available_slots

        except httpx.HTTPError as e:
            logger.error(f"HTTP error checking availability: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error checking availability: {str(e)}")
            raise

    async def create_appointment(
        self,
        client_id: str,
        service_id: str,
        staff_id: str,
        appointment_date: datetime,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new appointment.

        Args:
            client_id: Client's ID in Phorest
            service_id: Service ID
            staff_id: Staff member ID
            appointment_date: Date and time of appointment
            notes: Optional appointment notes

        Returns:
            Created appointment details
        """
        try:
            payload = {
                "clientId": client_id,
                "serviceId": service_id,
                "staffId": staff_id,
                "startDateTime": appointment_date.isoformat(),
                "notes": notes or ""
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/{self.branch_id}/appointment",
                    headers=self.headers,
                    json=payload,
                    timeout=10.0
                )

                response.raise_for_status()
                data = response.json()

                appointment = {
                    "appointment_id": data.get("appointmentId"),
                    "confirmation_number": data.get("confirmationNumber"),
                    "client_id": client_id,
                    "service_id": service_id,
                    "staff_id": staff_id,
                    "start_time": appointment_date.isoformat(),
                    "status": data.get("status", "confirmed")
                }

                logger.info(f"Created appointment: {appointment['appointment_id']}")
                return appointment

        except httpx.HTTPError as e:
            logger.error(f"HTTP error creating appointment: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating appointment: {str(e)}")
            raise

    async def find_or_create_client(
        self,
        phone: str,
        name: str,
        email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Find existing client by phone or create new one.

        Args:
            phone: Client's phone number
            name: Client's name
            email: Client's email (optional)

        Returns:
            Client details with ID
        """
        try:
            # First, search for existing client by phone
            async with httpx.AsyncClient() as client:
                search_response = await client.get(
                    f"{self.base_url}/{self.branch_id}/client",
                    headers=self.headers,
                    params={"phone": phone},
                    timeout=10.0
                )

                if search_response.status_code == 200:
                    data = search_response.json()
                    clients = data.get("_embedded", {}).get("clients", [])

                    if clients:
                        # Client found
                        existing_client = clients[0]
                        logger.info(f"Found existing client: {existing_client.get('clientId')}")
                        return {
                            "client_id": existing_client.get("clientId"),
                            "name": existing_client.get("clientName"),
                            "phone": existing_client.get("clientPhone"),
                            "email": existing_client.get("clientEmail"),
                            "is_new": False
                        }

                # Client not found, create new one
                create_payload = {
                    "firstName": name.split()[0] if name else "Customer",
                    "lastName": " ".join(name.split()[1:]) if len(name.split()) > 1 else "",
                    "mobile": phone,
                    "email": email or ""
                }

                create_response = await client.post(
                    f"{self.base_url}/{self.branch_id}/client",
                    headers=self.headers,
                    json=create_payload,
                    timeout=10.0
                )

                create_response.raise_for_status()
                new_client = create_response.json()

                logger.info(f"Created new client: {new_client.get('clientId')}")
                return {
                    "client_id": new_client.get("clientId"),
                    "name": f"{create_payload['firstName']} {create_payload['lastName']}".strip(),
                    "phone": phone,
                    "email": email,
                    "is_new": True
                }

        except httpx.HTTPError as e:
            logger.error(f"HTTP error with client operations: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error finding/creating client: {str(e)}")
            raise

    async def cancel_appointment(
        self,
        appointment_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cancel an existing appointment.

        Args:
            appointment_id: ID of appointment to cancel
            reason: Optional cancellation reason

        Returns:
            Cancellation confirmation
        """
        try:
            payload = {
                "status": "cancelled",
                "cancellationReason": reason or "Customer requested cancellation"
            }

            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/{self.branch_id}/appointment/{appointment_id}",
                    headers=self.headers,
                    json=payload,
                    timeout=10.0
                )

                response.raise_for_status()

                logger.info(f"Cancelled appointment: {appointment_id}")
                return {
                    "status": "cancelled",
                    "appointment_id": appointment_id,
                    "reason": reason
                }

        except httpx.HTTPError as e:
            logger.error(f"HTTP error cancelling appointment: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error cancelling appointment: {str(e)}")
            raise

    async def get_appointment(self, appointment_id: str) -> Dict[str, Any]:
        """
        Get appointment details.

        Args:
            appointment_id: ID of the appointment

        Returns:
            Appointment details
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{self.branch_id}/appointment/{appointment_id}",
                    headers=self.headers,
                    timeout=10.0
                )

                response.raise_for_status()
                data = response.json()

                return {
                    "appointment_id": data.get("appointmentId"),
                    "client_name": data.get("clientName"),
                    "service_name": data.get("serviceName"),
                    "staff_name": data.get("staffName"),
                    "start_time": data.get("startDateTime"),
                    "status": data.get("status"),
                    "notes": data.get("notes")
                }

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching appointment: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error fetching appointment: {str(e)}")
            raise
