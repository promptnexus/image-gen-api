# AI Image Generation API

A GraphQL API service for generating AI images with custom styles, sizes, and formats. Built with FastAPI, Strawberry GraphQL, and Poetry.

## Features

- 🖼️ Generate AI images with customizable:
  - Sizes (256x256, 512x512, 1024x1024)
  - Formats (PNG, JPEG, WEBP)
  - Styles (Photorealistic, Artistic, Cartoon, Abstract)
- 🔒 API Key authentication
- 📚 Auto-generated documentation
- ✨ Type-safe GraphQL schema
- 🔄 SDK generation for multiple languages

## Quick Start

```bash
# Install dependencies
poetry install

# Start the server
poetry run python app/main.py

# Server runs at http://localhost:8000
# Documentation at http://localhost:8000/docs
```

## API Usage

### Authentication

Include your API key in requests:
```bash
curl -H "X-API-Key: sk_your_key" http://localhost:8000/
```

### Example Query

```graphql
mutation GenerateImages($input: ImageGenerationInput!) {
  generateImages(input: {
    prompt: "a beautiful sunset"
    size: LARGE
    style: PHOTOREALISTIC
    format: PNG
    numImages: 1
  }) {
    success
    results {
      id
      url
    }
  }
}
```

## Development

```bash
# Run with auto-reload
poetry run uvicorn app.main:app --reload

# Generate SDKs
graphql-codegen

# Run tests (once implemented)
poetry run pytest
```

## Project Structure

```
app/
├── __init__.py
├── main.py              # FastAPI app setup
├── schema.py            # GraphQL schema
├── types/              
│   ├── enums.py        # Enum definitions
│   ├── inputs.py       # Input types
│   ├── responses.py    # Response types
│   └── scalars.py      # Custom scalars
├── resolvers/
│   ├── queries.py      # Query resolvers
│   └── mutations.py    # Mutation resolvers
└── services/
    ├── auth.py         # Auth logic
    └── image.py        # Image generation
```

## Generated SDKs

SDKs are automatically generated for:
- Python
- TypeScript
- Go
- Java

## Environment Variables

```bash
# Required
API_KEY_SECRET=your_secret_key

# Optional
PORT=8000
HOST=0.0.0.0
```

## License

MIT