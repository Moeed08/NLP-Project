import grpc
from concurrent import futures
import service_pb2, service_pb2_grpc
import requests

HUGGINGFACE_API = "https://your-space-url.hf.space/generate"

class DiffusionServicer(service_pb2_grpc.DiffusionServiceServicer):
    def GenerateImage(self, request, context):
        resp = requests.post(HUGGINGFACE_API, json={"prompt": request.prompt})
        image_b64 = resp.json().get("image")
        return service_pb2.ImageReply(image_base64=image_b64)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_DiffusionServiceServicer_to_server(DiffusionServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()
