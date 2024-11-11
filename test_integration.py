import multiprocessing
import time
import logging
from video_translation_system.server import start_server
from video_translation_system.client import TranslationClient, ClientConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def status_callback(status):
    """Callback function to handle status updates"""
    if "progress" in status:
        logger.info(f"Status: {status['result']}, Progress: {status['progress']}%")
    else:
        logger.info(f"Status: {status['result']}")

def run_client_test():
    """Run the client test"""
    # Configure the client
    config = ClientConfig(
        initial_delay=1.0,
        max_delay=5.0,
        backoff_factor=1.2,
        max_retries=3,
        timeout=30.0,
        jitter=True
    )
    
    # Create and run client
    client = TranslationClient(
        "http://127.0.0.1:8000",
        config=config,
        status_callback=status_callback
    )
    
    try:
        logger.info("Starting translation status check...")
        result = client.wait_for_completion()
        logger.info(f"Final result: {result}")
    except Exception as e:
        logger.error(f"Error during translation: {str(e)}")

def main():
    # Start server in a separate process
    server_process = multiprocessing.Process(
        target=start_server,
        kwargs={
            "completion_time": 15,
            "error_prob": 0.2
        }
    )
    
    try:
        server_process.start()
        # Wait for server to start
        time.sleep(2)
        # Run client test
        run_client_test()
    finally:
        server_process.terminate()
        server_process.join()

if __name__ == "__main__":
    main()