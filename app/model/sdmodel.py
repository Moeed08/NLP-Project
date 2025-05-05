# Ensure you have the necessary libraries installed:
# pip install diffusers transformers torch accelerate
# accelerate is often helpful even for CPU for certain optimizations

from diffusers import StableDiffusionPipeline
import torch

# Define the model ID
model_id = "runwayml/stable-diffusion-v1-5" # Using the v1.5 legacy model as specified

# Load the pipeline
# We remove torch_dtype=torch.float16 to use the default float32, which is better for CPU
print(f"Loading model {model_id}...")
pipe = StableDiffusionPipeline.from_pretrained(model_id)
print("Model loaded.")

# Move the pipeline to the CPU
print("Moving model to CPU...")
pipe = pipe.to("cpu")
print("Model moved to CPU.")

# Define the prompt
prompt = "a photo of an astronaut riding a horse on mars"

# Generate the image
# Note: This will be SIGNIFICANTLY slower on a CPU compared to a GPU.
# Generation could take several minutes or even longer depending on your CPU.
print(f"Generating image for prompt: '{prompt}'...")
print("This step might take a very long time on CPU, please be patient.")
image = pipe(prompt).images[0]
print("Image generation complete.")

# Save the image
output_filename = "astronaut_rides_horse_cpu.png"
image.save(output_filename)
print(f"Image saved as {output_filename}")