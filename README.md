# Gender Classification API — Stage 1

A FastAPI service that accepts a name, calls three external APIs (Genderize, Agify, Nationalize), and stores the result in a MySQL database.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/profiles` | Create a new profile |
| GET | `/api/profiles` | Get all profiles (with optional filters) |
| GET | `/api/profiles/{id}` | Get a single profile by ID |
| DELETE | `/api/profiles/{id}` | Delete a profile |

## Filters for GET /api/profiles

| Parameter | Example |
|-----------|---------|
| `gender` | `?gender=male` |
| `country_id` | `?country_id=NG` |
| `age_group` | `?age_group=adult` |

## Example Request

```bash