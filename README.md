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
# Interactive GraphQL Query Builder (GraphiQL) at http://localhost:8000/graphql
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
    width: 1024
    height: 1024
    style: PHOTOREALISTIC
    image_format: PNG
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
├── main.py             # FastAPI app setup
├── schema.py           # GraphQL Schema - Dynamically loaded from resolvers
├── types/              # Type files used across resolvers
│   ├── enums.py        # Enum definitions
│   ├── inputs.py       # Input types
│   ├── responses.py    # Response types
│   └── scalars.py      # Custom scalars
├── resolvers/
│   ├── queries/        # Query resolvers
│   │   └── example-query/
│   │       └── example-query.py
│   └── mutations/    # Mutation resolvers
│       └── example-mutation/
│           └── example-mutation.py
└── services/
    ├── auth.py
    └── image_generator.py
```

## Generated SDKs

SDKs are automatically generated for:
- Python
- TypeScript
- Go
- Java
- More coming soon!

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


## Contributing

We welcome contributions! To add a new model, follow these steps:

1. **Fork the repository** and clone it to your local machine.
2. **Create a new branch** for your feature:
    ```bash
    git checkout -b feature/add-new-model
    ```
3. **Add your model**:
    - Add a model repository from huggingface in [**enums.py**](./app/types/enums.py):
    ```python
    @strawberry.enum
    class ModelType(Enum):
        ...
        FLUX_1_SCHNELL = "black-forest-labs/FLUX.1-schnell"

        # Add your model
        YOUR_NEW_MODEL = "your-company/URMoDL.1"
    ```
    - Register your model pipeline in [**model_pipeline_registry.py**](./app/services/model_pipeline_registry.py):
    ```python
    cls.register(
        ModelType.STABLE_V1_4,
        PipelineConfig(
            pipeline_class=StableDiffusionPipeline,
            default_params={"safety_checker": None},
            inference_params={"num_inference_steps": 50},
        ),
    )
    ```
    - Update `app/schema.py` to include your model in the GraphQL schema.
    - Create necessary resolvers in `app/resolvers/` to handle queries and mutations for your model.
4. **Write tests** for your model in the `tests/` directory.
5. **Commit your changes** and push your branch to GitHub:
    ```bash
    git add .
    git commit -m "Add new model"
    git push origin add-new-model
    ```
6. **Create a Pull Request** on GitHub:
  - Go to your forked repository on GitHub.
  - Click on the "New pull request" button.
  - Ensure the base repository is set to the original repository and the base branch is `master`.
  - Provide a specific and concise description of your changes.
  - Submit the pull request for review.

Thank you for contributing!