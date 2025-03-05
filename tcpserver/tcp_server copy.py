import socket
import select
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from opuslib import Decoder
import socket
import select
import time
# Cấu hình giải mã
SAMPLE_RATE = 16000  # Tốc độ mẫu
CHANNELS = 2  # Stereo
FRAME_SIZE = 960  # Kích thước frame chuẩn của Opus 16kHz
def start_tcp_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"🔹 Listening on {host}:{port}")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"✅ Accepted connection from {addr}")

            # Đặt tên file theo thời gian
            decoder = Decoder(SAMPLE_RATE, CHANNELS)

            
            try:
                with client_socket, open(filename, "wb") as f:
                    while True:
                        ready = select.select([client_socket], [], [], 5)
                        if ready[0]:  # Nếu có dữ liệu đến từ socket
                            part = client_socket.recv(16384)  # Nhận tối đa 16KB/lần
                            if not part:
                                print("❌ Client disconnected.")
                                break
                            pcm_data = decoder.decode(opus_data, FRAME_SIZE)
                            print(f"🔄 Decoded {len(opus_data)} bytes Opus → {len(pcm_data)} bytes PCM")
                                print("Data received, transmitting...")
                                # When bytes_data is received, send it to the audio_stream group
                            channel_layer = get_channel_layer()
                                async_to_sync(channel_layer.group_send)(
                                    "audio_stream",  # Group name
                                    {
                                        "type": "send_audio",
                                        "chunk": part
                                    }
                                )
                        else:
                            print("⏳ Timeout or no more data.")
                            break

                print(f"✅ File saved: {filename} ({total_size} bytes)")
                print(f"🔄 You can now decode it with: `opusdec {filename} output.wav`")

            except Exception as e:
                print(f"⚠️ Error handling client {addr}: {e}")

    except KeyboardInterrupt:
        print("🔴 Server stopping...")
    finally:
        server_socket.close()
        print("🔴 Server stopped.")
