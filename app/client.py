import asyncio
import logging
from pathlib import Path

import grpc
from app.service_pb2 import GenerateRequest, HealthRequest
from app.service_pb2_grpc import StableDiffusionServiceStub

async def run_client(prompt: str, output_path: str = "output.png") -> None:
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = StableDiffusionServiceStub(channel)
        
        # Health check
        health_response = await stub.HealthCheck(HealthRequest())
        logging.info(f"Health status: {health_response.status}")
        
        if health_response.status != "SERVING":
            logging.error("Service is not healthy")
            return
        
        # Generate image
        response = await stub.GenerateImage(
            GenerateRequest(
                prompt=prompt,
                height=512,
                width=512,
                num_inference_steps=50,
                guidance_scale=7.5,
            )
        )
        
        if response.HasField("success"):
            with open(output_path, "wb") as f:
                f.write(response.success.image_data)
            logging.info(f"Image saved to {output_path}")
        else:
            logging.error(f"Error: {response.error.message} (code {response.error.code})")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    prompt = "a beautiful sunset over mountains, digital art"
    asyncio.run(run_client(prompt))