import socket
import opuslib
import signal
import sys
import time  # Add this import

class OpusStreamServer:
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port
        self.buffer_size = 4096
        self.running = True
        
        # Opus parameters
        self.SAMPLE_RATE = 48000
        self.CHANNELS = 2
        self.OPUS_FRAME_SIZE = 1024  # Size of each Opus frame
        self.decoder = opuslib.Decoder(self.SAMPLE_RATE, self.CHANNELS)
    
    def recv_exact(self, sock, size):
        """Receive exactly 'size' bytes from socket, buffering incomplete receives"""
        data = bytearray()
        sock.setblocking(0)  # Non-blocking mode
        
        while len(data) < size:
            try:
                chunk = sock.recv(size - len(data))
                if not chunk:
                    if len(data) > 0:
                        print(f"Incomplete chunk received: {len(data)} bytes, needed {size}")
                    return None
                data.extend(chunk)
                
                if len(data) < size:
                    print(f"Partial receive: {len(data)}/{size} bytes")
                
            except BlockingIOError:
                time.sleep(0.01)  # Small delay to prevent CPU spinning
                continue
            except socket.error as e:
                print(f"Socket error: {e}")
                return None
                
        sock.setblocking(1)  # Reset to blocking mode
        return bytes(data)

    def decode_opus_to_raw_pcm(self, opus_data):
        pcm_data = bytearray()
        for i in range(0, len(opus_data), self.OPUS_FRAME_SIZE):
            try:
                frame = opus_data[i:i + self.OPUS_FRAME_SIZE]
                if len(frame) == self.OPUS_FRAME_SIZE:
                    decoded = self.decoder.decode(frame, 960)  # 20ms at 48kHz
                    if decoded:
                        pcm_data.extend(decoded)
            except Exception as e:
                print(f"Decoding error at frame {i//self.OPUS_FRAME_SIZE}: {e}")
                continue
        return bytes(pcm_data)
    
    def start_server(self):
        signal.signal(signal.SIGINT, lambda s, f: self.signal_handler(s, f))
        
        with open("output.pcm", "wb") as pcm_file:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            
            print(f"Server listening on {self.host}:{self.port}")
            print("Press Ctrl+C to stop server and save file")
            
            receive_buffer = bytearray()

            while self.running:
                client_socket, addr = self.server_socket.accept()
                print(f"Connected to {addr}")
                
                try:
                    while self.running:
                        # Use recv_exact to ensure complete chunks
                        data = self.recv_exact(client_socket, 4096)
                        if not data:
                            break
                        
                        receive_buffer.extend(data)
                        print(f"Buffer size: {len(receive_buffer)} bytes")
                        
                        # Process complete chunks
                        while len(receive_buffer) >= self.buffer_size:
                            chunk = receive_buffer[:self.buffer_size]
                            receive_buffer = receive_buffer[self.buffer_size:]
                            
                            pcm_data = self.decode_opus_to_raw_pcm(chunk)
                            if pcm_data:
                                pcm_file.write(pcm_data)
                                pcm_file.flush()
                                print(f"Decoded {len(pcm_data)} bytes of PCM data")
                                
                except ConnectionResetError:
                    print(f"Connection reset by {addr}")
                except Exception as e:
                    print(f"Error handling {addr}: {e}")
                finally:
                    client_socket.close()
                    print(f"Disconnected from {addr}")
                    print(f"Remaining buffer: {len(receive_buffer)} bytes")

    def signal_handler(self, sig, frame):
        print("\nClosing server...")
        self.running = False
        if hasattr(self, 'server_socket'):
            self.server_socket.close()
        sys.exit(0)

if __name__ == "__main__":
    server = OpusStreamServer()
    server.start_server()