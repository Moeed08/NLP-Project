# main.py in project root
from app.server import serve
from frontend.ui import create_interface
import asyncio
import threading

def run_grpc():
    asyncio.run(serve())

def run_gradio():
    demo = create_interface()
    demo.launch()

if __name__ == "__main__":
    grpc_thread = threading.Thread(target=run_grpc)
    grpc_thread.start()
    
    run_gradio()