from flask import Flask, jsonify
import time
import random
from enum import Enum
from typing import Dict, Any

class JobStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    ERROR = "error"

class TranslationServer:
    def __init__(self, completion_time: float = 10.0, error_probability: float = 0.1):
        # Initialize the server
        self.start_time = time.time()
        self.completion_time = completion_time
        # Error probability
        self.error_probability = error_probability
        # Make sure the error is only determined once
        self.error_determined = False
        # Flag to determine if an error is going to occur
        self.will_error = False
    
    def get_status(self) -> Dict[str, Any]:
        if not self.error_determined:
            self.will_error = random.random() < self.error_probability
            self.error_determined = True
        
        elapsed_time = time.time() - self.start_time
        
        if self.will_error and elapsed_time >= self.completion_time:
            return {"result": JobStatus.ERROR}
        elif elapsed_time >= self.completion_time:
            return {"result": JobStatus.COMPLETED}
        else:
            progress = min(elapsed_time / self.completion_time * 100, 99)
            return {
                "result": JobStatus.PENDING,
                "progress": round(progress, 1)
            }

def create_app(completion_time: float = 10.0, error_prob: float = 0.1):
    app = Flask(__name__)
    app.translation_server = TranslationServer(completion_time, error_prob)

    @app.route('/status')
    def get_status():
        return jsonify(app.translation_server.get_status())

    return app

def start_server(host: str = "127.0.0.1", port: int = 8000, 
                completion_time: float = 10.0, error_prob: float = 0.1):
    app = create_app(completion_time, error_prob)
    app.run(host=host, port=port)

if __name__ == "__main__":
    start_server()