# Senda AI - Dialogflow CX Agent

This directory contains the Dialogflow CX agent configuration for the Senda AI salon receptionist.

## Agent Structure

### Flows
- **Default Start Flow**: Initial greeting and intent routing
- **Appointment Booking Flow**: Handles new appointment bookings
- **Appointment Management Flow**: Handles cancellations and modifications
- **Information Flow**: Provides service information, hours, pricing

### Intents
- `greeting`: Welcome message
- `book_appointment`: Book new appointment
- `check_availability`: Check available time slots
- `cancel_appointment`: Cancel existing appointment
- `modify_appointment`: Change appointment details
- `service_inquiry`: Ask about services
- `hours_inquiry`: Ask about business hours
- `pricing_inquiry`: Ask about service pricing
- `confirm_yes`: Affirmative response
- `confirm_no`: Negative response

### Entities
- `@service`: Salon services (haircut, coloring, manicure, etc.)
- `@date`: Appointment dates
- `@time`: Appointment times
- `@customer_name`: Customer names
- `@phone_number`: Phone numbers

## Deployment

### Prerequisites
1. Google Cloud Project with Dialogflow CX API enabled
2. Service account with Dialogflow CX permissions
3. Webhook URL configured (your FastAPI endpoint)

### Creating the Agent

You can create the agent using:
1. **Google Cloud Console** (recommended for first-time setup)
2. **Dialogflow CX API** (using the configuration files in this directory)
3. **Terraform** (for infrastructure as code)

### Using the Configuration Files

The JSON files in this directory can be imported into Dialogflow CX:

```bash
# Set your project ID
export PROJECT_ID="your-google-project-id"
export LOCATION="us-central1"

# Create the agent using gcloud CLI
gcloud dialogflow cx agents create \
  --display-name="Senda AI Receptionist" \
  --default-language-code="en" \
  --time-zone="America/New_York" \
  --project=$PROJECT_ID \
  --location=$LOCATION
```

### Webhook Configuration

The agent is configured to call webhooks at:
- `https://your-api-domain.com/webhooks/dialogflow`

Make sure to update the webhook URL in the agent settings after deployment.

## Testing

### Phone Integration
1. Set up Dialogflow Phone Gateway for testing
2. Configure Telnyx integration for production number

### Text Testing
Use the Dialogflow CX simulator in Google Cloud Console

## Voice Settings

Recommended voice settings for natural conversation:
- **Voice**: en-US-Neural2-F (female) or en-US-Neural2-D (male)
- **Speaking Rate**: 1.0
- **Pitch**: 0
- **Volume Gain**: 0

## Session Parameters

Key session parameters tracked during conversation:
- `customer_name`: Customer's name
- `customer_phone`: Customer's phone number
- `selected_service`: Chosen service
- `appointment_date`: Selected date
- `appointment_time`: Selected time
- `confirmation_number`: Booking confirmation
- `available_times`: Available time slots from Phorest
