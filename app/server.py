import asyncio
import logging
from concurrent import futures
from typing import Optional

import grpc
from PIL import Image
import io
import json
from pathlib import Path
import sys
# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.service_pb2 import (
    GenerateRequest,
    GenerateResponse,
    Success,
    Error,
    HealthResponse,
)
from app.service_pb2_grpc import (
    StableDiffusionServiceServicer,
    add_StableDiffusionServiceServicer_to_server,
)

# Stable Diffusion imports
import torch
from diffusers import StableDiffusionPipeline

class StableDiffusionServicer(StableDiffusionServiceServicer):
    def __init__(self):
        self.logger = logging.getLogger("StableDiffusionServicer")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.logger.info(f"Using device: {self.device}")
        
        # Initialize the model
        try:
            self.pipe = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            ).to(self.device)
            self.logger.info("Stable Diffusion model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load model: {str(e)}")
            raise

    async def GenerateImage(
        self, request: GenerateRequest, context: grpc.aio.ServicerContext
    ) -> GenerateResponse:
        try:
            # Validate input
            if not request.prompt or len(request.prompt.strip()) == 0:
                return GenerateResponse(
                    error=Error(message="Prompt cannot be empty", code=400)
                )

            height = request.height if request.height and request.height > 0 else 512
            width = request.width if request.width and request.width > 0 else 512
            num_inference_steps = (
                request.num_inference_steps
                if request.num_inference_steps and request.num_inference_steps > 0
                else 50
            )
            guidance_scale = (
                request.guidance_scale
                if request.guidance_scale and request.guidance_scale > 0
                else 7.5
            )
            seed = request.seed if request.seed else torch.randint(0, 2**32 - 1, (1,)).item()

            generator = torch.Generator(device=self.device).manual_seed(seed)

            # Generate image
            
             # Generate image (properly awaited)
            result = await asyncio.to_thread(
                self.pipe,
                prompt=request.prompt,
                height=height,
                width=width,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator,
        )
            image = result.images[0]  # Now we access images on the actual result
        
        # Convert to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format="PNG")
            img_bytes = img_byte_arr.getvalue()

            return GenerateResponse(
                success=Success(
                    image_data=img_bytes,
                    mime_type="image/png",
                    seed=seed,
                )
        )

        except torch.cuda.OutOfMemoryError:
            return GenerateResponse(
                error=Error(
                    message="CUDA out of memory - try reducing image size or steps",
                    code=507,
                )
            )
        except Exception as e:
            self.logger.error(f"Error generating image: {str(e)}")
            return GenerateResponse(
                error=Error(
                    message=f"Internal server error: {str(e)}",
                    code=500,
                )
            )

    async def HealthCheck(self, request, context):
        try:
            # Simple health check - verify model is loaded
            if hasattr(self, "pipe") and self.pipe is not None:
                return HealthResponse(status="SERVING")
            return HealthResponse(status="NOT_SERVING")
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return HealthResponse(status="NOT_SERVING")

async def serve() -> None:
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ("grpc.max_send_message_length", 100 * 1024 * 1024),
            ("grpc.max_receive_message_length", 100 * 1024 * 1024),
        ],
    )
    add_StableDiffusionServiceServicer_to_server(
        StableDiffusionServicer(), server
    )
    server.add_insecure_port("[::]:50051")
    await server.start()
    logging.info("Server started on port 50051")
    await server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())