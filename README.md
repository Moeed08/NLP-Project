# Text-to-Image Generator using gRPC and Gradio

This project implements a text-to-image generation service using a gRPC backend and a Gradio frontend. The backend forwards prompts to a Hugging Face Space hosting a Stable Diffusion model, and the frontend provides a simple web interface for users to enter prompts and view the generated images.

## Project Structure

```
NLP-Project/
├── .github/
│   └── workflows/
│       └── main.yml        # GitHub Actions CI/CD workflow
├── app/
│   ├── __init__.py
│   ├── server.py           # gRPC server implementation
│   ├── service.proto       # Protocol Buffers definition for gRPC
│   ├── client.py           # (Empty) Potential gRPC client test script
│   ├── service_pb2.py      # Generated gRPC code (ignored by git)
│   └── service_pb2_grpc.py # Generated gRPC code (ignored by git)
├── frontend/
│   └── ui.py               # Gradio frontend application
├── tests/
│   └── postman/
│       └── collection.json # (Empty) Postman collection for API testing
├── .dockerignore           # Specifies files to ignore in Docker build
├── .gitignore              # Specifies intentionally untracked files
├── Dockerfile              # Docker configuration for the application
├── README.md               # This file
└── requirements.txt        # Python dependencies
```

## Components

1. **gRPC Server (`app/server.py`)**:
   - Listens for incoming gRPC requests on port 50051.
   - Receives a text prompt via the `GenerateImage` RPC method.
   - Makes a POST request to a specified Hugging Face Space API endpoint (`HUGGINGFACE_API`) with the prompt.
   - Receives the generated image (base64 encoded) from the Hugging Face Space.
   - Returns the base64 image string in the gRPC response.
   - **Note:** You need to replace `"https://your-space-url.hf.space/generate"` in `app/server.py` with the actual URL of your Hugging Face Space API endpoint.

2. **Gradio Frontend (`frontend/ui.py`)**:
   - Provides a web interface using Gradio.
   - Takes a text prompt as input.
   - Connects to the gRPC server running on `localhost:50051`.
   - Calls the `GenerateImage` RPC method with the user's prompt.
   - Receives the base64 image string, decodes it, and displays the image in the UI.

3. **gRPC Definition (`app/service.proto`)**:
   - Defines the `DiffusionService` with the `GenerateImage` RPC method.
   - Specifies the `PromptRequest` (containing the text prompt) and `ImageReply` (containing the base64 image string) message types.

4. **Dockerfile**:
   - Defines the steps to build a Docker image for the application.
   - Uses a Python 3.10 base image.
   - Installs dependencies from `requirements.txt`.
   - Copies the application code.
   - Sets the default command to run the Gradio frontend (`frontend/ui.py`).

5. **CI/CD (`.github/workflows/main.yml`)**:
   - A GitHub Actions workflow triggered on pushes to the `main` branch.
   - Sets up Python 3.10.
   - Installs dependencies.
   - Runs `flake8` for linting.
   - Compiles the `.proto` file using `grpc_tools`.
   - Includes an optional step to run `pytest` (currently no tests are defined).

## Setup and Usage

### Prerequisites

- Python 3.10 or later
- pip
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd NLP-Project
   ```
2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   # source venv/bin/activate # On macOS/Linux
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Generate gRPC code:**
   ```bash
   python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. app/service.proto
   ```

### Running the Application

1. **Start the gRPC server:**
   Open a terminal, activate the virtual environment, and run:
   ```bash
   python app/server.py
   ```
   *(Remember to update the `HUGGINGFACE_API` URL in `app/server.py` first)*

2. **Start the Gradio frontend:**
   Open *another* terminal, activate the virtual environment, and run:
   ```bash
   python frontend/ui.py
   ```
   Navigate to the local URL provided by Gradio (usually `http://127.0.0.1:7860`) in your web browser. Enter a prompt and click submit to generate an image.

## Docker

You can build and run the application using Docker.

1. **Build the Docker image:**
   ```bash
   docker build -t nlp-project .
   ```
2. **Run the container:**
   ```bash
   docker run -p 7860:7860 nlp-project
   ```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
check.