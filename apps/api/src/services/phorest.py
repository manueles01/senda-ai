"""
Phorest API Service
Handles all interactions with Phorest salon management system
"""

import httpx
import base64
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from zoneinfo import ZoneInfo


class PhorestService:
    """Service for interacting with Phorest API"""

    def __init__(self):
        self.base_url = os.getenv("PHOREST_BASE_URL")
        self.business_id = os.getenv("PHOREST_BUSINESS_ID")
        self.branch_id = os.getenv("PHOREST_BRANCH_ID")
        self.timezone = os.getenv("SALON_TIMEZONE", "America/New_York")
        username = os.getenv("PHOREST_USERNAME")
        password = os.getenv("PHOREST_PASSWORD")

        # Create basic auth header with 'global/' prefix (required by Phorest API)
        auth_string = base64.b64encode(f"global/{username}:{password}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {auth_string}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def find_client_by_phone(
        self, phone_number: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find a client in Phorest by phone number

        Args:
            phone_number: Customer's phone number

        Returns:
            Client data if found, None otherwise
        """
        print(f"\n🔍 find_client_by_phone() called")
        print(f"  Phone number: {phone_number}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Note: Client endpoint does NOT include branch ID (per Phorest API docs)
            url = f"{self.base_url}/third-party-api-server/api/business/{self.business_id}/client"

            try:
                # Search by phone
                params = {"mobile": phone_number, "size": 50, "page": 0}
                print(f"  URL: {url}")
                print(f"  Params: {params}")

                response = await client.get(
                    url, headers=self.headers, params=params
                )

                print(f"  Response Status: {response.status_code}")
                response.raise_for_status()

                data = response.json()
                clients = data.get("_embedded", {}).get("clients", [])

                print(f"  Found {len(clients)} client(s)")
                if clients:
                    print(f"  ✅ Match: {clients[0].get('firstName')} {clients[0].get('lastName')} - {clients[0].get('mobile')}")
                    return clients[0]  # Return first match
                else:
                    print(f"  ℹ️  No clients found with mobile: {phone_number}")
                    return None

            except Exception as e:
                print(f"❌ Error finding client: {e}")
                print(f"  URL: {url}")
                return None

    async def create_client(
        self, first_name: str, last_name: str, phone_number: str, email: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new client in Phorest

        Args:
            first_name: Client's first name
            last_name: Client's last name
            phone_number: Client's phone number
            email: Client's email (optional)

        Returns:
            Created client data if successful, None otherwise
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Note: Client endpoint does NOT include branch ID (per Phorest API docs)
            url = f"{self.base_url}/third-party-api-server/api/business/{self.business_id}/client"

            payload = {
                "firstName": first_name,
                "lastName": last_name,
                "mobile": phone_number,
            }

            if email:
                payload["email"] = email

            try:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"❌ Error creating client: {e}")
                return None

    async def get_services(self) -> List[Dict[str, Any]]:
        """Get all available services"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.base_url}/third-party-api-server/api/business/{self.business_id}/branch/{self.branch_id}/service"

            try:
                response = await client.get(
                    url, headers=self.headers, params={"size": 500}
                )
                response.raise_for_status()
                data = response.json()
                services = data.get("_embedded", {}).get("services", [])
                if not services:
                    print(f"⚠️  No services in response. Response keys: {list(data.keys())}")
                return services
            except Exception as e:
                print(f"❌ Error fetching services: {e}")
                print(f"  URL: {url}")
                return []

    async def get_staff(self) -> List[Dict[str, Any]]:
        """Get all staff members"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.base_url}/third-party-api-server/api/business/{self.business_id}/branch/{self.branch_id}/staff"

            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                staff = data.get("_embedded", {}).get("staffs", [])
                if not staff:
                    print(f"⚠️  No staff in response. Response keys: {list(data.keys())}")
                return staff
            except Exception as e:
                print(f"❌ Error fetching staff: {e}")
                print(f"  URL: {url}")
                return []

    async def check_availability(
        self,
        service_name: str,
        staff_name: Optional[str] = None,
        days_ahead: int = 7,
    ) -> Dict[str, Any]:
        """
        Check availability for a service with optional staff preference

        Args:
            service_name: Name of the service
            staff_name: Optional staff member name
            days_ahead: Number of days to check ahead

        Returns:
            Dictionary with service, staff, and available time slots
        """
        print(f"\n🔵 check_availability() called")
        print(f"  Requested service: '{service_name}'")
        print(f"  Requested staff: '{staff_name}'")
        print(f"  Days ahead: {days_ahead}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get services and find match
            print(f"\n  📋 Fetching services list...")
            services = await self.get_services()
            print(f"  ✅ Got {len(services)} services")

            service = None
            for svc in services:
                if service_name.lower() in svc["name"].lower():
                    service = svc
                    break
            if not service and services:
                service = services[0]  # Default to first service

            if service:
                print(f"  ✅ Matched service: {service.get('name')}")
            else:
                print(f"  ❌ No service matched!")

            # Get staff and find match
            print(f"\n  👥 Fetching staff list...")
            staff_list = await self.get_staff()
            print(f"  ✅ Got {len(staff_list)} staff members")

            staff = None
            if staff_name:
                for s in staff_list:
                    if staff_name.lower() in s["firstName"].lower():
                        staff = s
                        break
            if not staff and staff_list:
                staff = staff_list[0]  # Default to first staff

            if staff:
                print(f"  ✅ Matched staff: {staff.get('firstName')} {staff.get('lastName')}")
            else:
                print(f"  ❌ No staff matched!")

            if not service or not staff:
                print(f"  ❌ Missing service or staff - returning empty")
                return {"service": None, "staff": None, "slots": []}

            # Check availability
            now = datetime.now()
            later = now + timedelta(days=days_ahead)

            avail_url = f"{self.base_url}/third-party-api-server/api/business/{self.business_id}/branch/{self.branch_id}/appointments/availability"
            payload = {
                "startTime": now.isoformat() + "Z",
                "endTime": later.isoformat() + "Z",
                "clientServiceSelections": [
                    {
                        "serviceSelections": [{"serviceId": service["serviceId"]}],
                        "staffId": staff["staffId"],
                    }
                ],
            }

            print(f"\n🔍 DEBUG: Checking availability")
            print(f"  Service: {service.get('name')} (ID: {service.get('serviceId')})")
            print(f"  Staff: {staff.get('firstName')} {staff.get('lastName')} (ID: {staff.get('staffId')})")
            print(f"  URL: {avail_url}")
            print(f"  Payload: {payload}")

            try:
                response = await client.post(
                    avail_url, headers=self.headers, json=payload
                )

                print(f"  Response Status: {response.status_code}")
                print(f"  Response Headers: {dict(response.headers)}")

                response.raise_for_status()
                result = response.json()

                print(f"  Response Body: {result}")
                print(f"  Data field exists: {'data' in result}")
                if result.get("data"):
                    print(f"  Number of slots: {len(result['data'])}")

                slots = []
                if result.get("data"):
                    for slot_data in result["data"][:3]:  # Get first 3 slots
                        schedule = slot_data["clientSchedules"][0]["serviceSchedules"][
                            0
                        ]
                        # Parse UTC time from Phorest
                        dt_utc = datetime.fromisoformat(
                            schedule["startTime"].replace("Z", "+00:00")
                        )

                        # Convert to salon's local timezone
                        dt_local = dt_utc.astimezone(ZoneInfo(self.timezone))

                        # Format for natural speech
                        # Example: "Monday, November 18th at 2:30 PM"
                        day = dt_local.strftime("%A")
                        month = dt_local.strftime("%B")
                        day_num = dt_local.day
                        # Add ordinal suffix (1st, 2nd, 3rd, etc.)
                        if 10 <= day_num % 100 <= 20:
                            suffix = "th"
                        else:
                            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day_num % 10, "th")
                        time_str = dt_local.strftime("%I:%M %p").lstrip("0")

                        formatted_time = f"{day}, {month} {day_num}{suffix} at {time_str}"

                        slots.append(
                            {
                                "time": formatted_time,
                                "raw": schedule["startTime"],
                            }
                        )

                return {
                    "service": service["name"],
                    "service_id": service["serviceId"],
                    "staff": f"{staff['firstName']} {staff['lastName']}",
                    "staff_id": staff["staffId"],
                    "slots": slots,
                }

            except httpx.HTTPStatusError as e:
                print(f"\n❌ HTTP Error checking availability:")
                print(f"  Status Code: {e.response.status_code}")
                print(f"  Response Body: {e.response.text}")
                print(f"  Request URL: {e.request.url}")
                print(f"  Request Body: {payload}")
                return {"service": None, "staff": None, "slots": []}
            except Exception as e:
                print(f"\n❌ Error checking availability: {type(e).__name__}")
                print(f"  Error: {str(e)}")
                import traceback
                print(f"  Traceback: {traceback.format_exc()}")
                return {"service": None, "staff": None, "slots": []}

    async def create_appointment(
        self,
        client_id: str,
        service_id: str,
        staff_id: str,
        start_time: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new appointment

        Args:
            client_id: Phorest client ID
            service_id: Service ID
            staff_id: Staff member ID
            start_time: ISO format start time

        Returns:
            Created appointment data if successful, None otherwise
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.base_url}/third-party-api-server/api/business/{self.business_id}/branch/{self.branch_id}/appointment"

            payload = {
                "clientId": client_id,
                "startTime": start_time,
                "services": [{"serviceId": service_id, "staffId": staff_id}],
            }

            try:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"❌ Error creating appointment: {e}")
                return None

    async def get_client_appointments(
        self, client_id: str
    ) -> List[Dict[str, Any]]:
        """Get all appointments for a client"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.base_url}/third-party-api-server/api/business/{self.business_id}/branch/{self.branch_id}/appointment"

            try:
                response = await client.get(
                    url, headers=self.headers, params={"clientId": client_id}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("_embedded", {}).get("appointments", [])
            except Exception as e:
                print(f"❌ Error fetching appointments: {e}")
                return []

    async def cancel_appointment(self, appointment_id: str) -> bool:
        """Cancel an appointment"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.base_url}/third-party-api-server/api/business/{self.business_id}/branch/{self.branch_id}/appointment/{appointment_id}/cancel"

            try:
                response = await client.post(url, headers=self.headers, json={})
                response.raise_for_status()
                return True
            except Exception as e:
                print(f"❌ Error canceling appointment: {e}")
                return False


# Create singleton instance
phorest_service = PhorestService()
