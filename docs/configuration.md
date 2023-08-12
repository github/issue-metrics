# Application Configuration
The application follows the standard 12 factor app approach to configuration values. It will read from a `.env` file
or an environment variable. Below are a list of all the configuration requirements.

```dotenv
###
# Application
###
ENVIRONMENT="local"

###
# Database
###
CQLENG_ALLOW_SCHEMA_MANAGEMENT="1"

### AWS or Azure OR GCP
# AWS - The keys should not be required when the company moves to 100% role based access
### billing account
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_ROLE_ARN=""
```
