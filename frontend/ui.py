import gradio as gr
import grpc
import asyncio
from pathlib import Path
import tempfile
import os
from PIL import Image
import io
import sys
# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))
# Import generated gRPC code
from app.service_pb2 import GenerateRequest
from app.service_pb2_grpc import StableDiffusionServiceStub

# gRPC client setup
async def generate_image_grpc(prompt, height, width, steps, guidance_scale, seed):
    # Create a channel and stub
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = StableDiffusionServiceStub(channel)
        
        # Prepare the request
        request = GenerateRequest(
            prompt=prompt,
            height=int(height),
            width=int(width),
            num_inference_steps=int(steps),
            guidance_scale=float(guidance_scale),
            seed=int(seed) if seed else None,
        )
        
        # Call the gRPC service
        try:
            response = await stub.GenerateImage(request)
            
            if response.HasField("success"):
                # Convert bytes to image
                image = Image.open(io.BytesIO(response.success.image_data))
                return image, f"Generation successful! Seed used: {response.success.seed}"
            else:
                error_msg = f"Error {response.error.code}: {response.error.message}"
                return None, error_msg
                
        except grpc.RpcError as e:
            return None, f"gRPC Error: {e.code()}: {e.details()}"
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"

# Gradio interface
def create_interface():
    with gr.Blocks(title="Stable Diffusion Image Generator") as demo:
        gr.Markdown("# 🎨 Stable Diffusion Image Generator")
        gr.Markdown("Enter a prompt and generate images using Stable Diffusion via gRPC")
        
        with gr.Row():
            with gr.Column():
                prompt = gr.Textbox(
                    label="Prompt",
                    placeholder="Enter your prompt here...",
                    lines=3,
                )
                
                with gr.Accordion("Advanced Settings", open=False):
                    height = gr.Slider(
                        label="Height",
                        minimum=256,
                        maximum=1024,
                        step=64,
                        value=512,
                    )
                    width = gr.Slider(
                        label="Width",
                        minimum=256,
                        maximum=1024,
                        step=64,
                        value=512,
                    )
                    steps = gr.Slider(
                        label="Inference Steps",
                        minimum=10,
                        maximum=100,
                        step=5,
                        value=50,
                    )
                    guidance_scale = gr.Slider(
                        label="Guidance Scale",
                        minimum=1.0,
                        maximum=20.0,
                        step=0.5,
                        value=7.5,
                    )
                    seed = gr.Number(
                        label="Seed (leave empty for random)",
                        value=None,
                        precision=0,
                    )
                
                submit_btn = gr.Button("Generate Image", variant="primary")
            
            with gr.Column():
                output_image = gr.Image(
                    label="Generated Image",
                    type="pil",
                    interactive=False,
                )
                status = gr.Textbox(
                    label="Status",
                    interactive=False,
                )
        
        # Examples
        examples = gr.Examples(
            examples=[
                ["A beautiful sunset over mountains, digital art"],
                ["A futuristic cityscape at night, cyberpunk style"],
                ["A cute corgi puppy wearing a crown, portrait"],
            ],
            inputs=[prompt],
        )
        
        # Event handlers
        submit_btn.click(
            fn=generate_image_grpc,
            inputs=[prompt, height, width, steps, guidance_scale, seed],
            outputs=[output_image, status],
        )
        
        # Quick generate on prompt enter
        prompt.submit(
            fn=generate_image_grpc,
            inputs=[prompt, height, width, steps, guidance_scale, seed],
            outputs=[output_image, status],
        )
    
    return demo

if __name__ == "__main__":
    # Create and launch the Gradio interface
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
    )