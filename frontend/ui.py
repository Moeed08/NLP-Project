import grpc
import gradio as gr
from PIL import Image
from io import BytesIO
import base64
import service_pb2, service_pb2_grpc

def generate(prompt):
    channel = grpc.insecure_channel("localhost:50051")
    stub = service_pb2_grpc.DiffusionServiceStub(channel)
    resp = stub.GenerateImage(service_pb2.PromptRequest(prompt=prompt))
    image = Image.open(BytesIO(base64.b64decode(resp.image_base64)))
    return image

gr.Interface(fn=generate, inputs="text", outputs="image", title="SD Image Generator").launch()
