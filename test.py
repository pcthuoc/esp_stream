import socket
import opuslib
from collections import deque

class OpusStreamServer:
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port
        self.buffer_size = 4096
        self.decoder = opuslib.Decoder(48000, 2)  # 48kHz, stereo
        self.buffer = bytearray()
        
    def decode_opus_chunk(self, opus_data):
        try:
            # Decode opus frame to PCM
            pcm_data = self.decoder.decode(bytes(opus_data), 480 * 2)
            return pcm_data
        except Exception as e:
            print(f"Decoding error: {e}")
            return None

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(1)
        print(f"Server listening on {self.host}:{self.port}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connected to {addr}")
            
            try:
                while True:
                    # Receive data
                    data = client_socket.recv(1024*4)
                    if not data:
                        break
                    
                    # Add to buffer
                    self.buffer.extend(data)
                    if len(self.buffer) >= 4096:
                        print(f"Received {len(data)} bytes from {addr}, Buffer size: {len(self.buffer)} bytes")
                        print(self.buffer)
                        return
                    # Process when buffer reaches 4096 bytes
                    # while len(self.buffer) >= 4096:
                    #     # # Take first 4096 bytes
                    #     # chunk = self.buffer[:4096]
                    #     # self.buffer = self.buffer[4096:]
                        
                    #     # # Decode chunk
                    #     # pcm_data = self.decode_opus_chunk(chunk)
                    #     # if pcm_data:
                    #     #     # Save or process PCM data
                    #     #     with open("output.pcm", "ab") as f:
                    #     #         f.write(pcm_data)
                        
            except Exception as e:
                print(f"Error: {e}")
            finally:
                client_socket.close()
                print(f"Disconnected from {addr}")

if __name__ == "__main__":
    server = OpusStreamServer()
    server.start_server()