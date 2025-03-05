import socket
import opuslib  # Thư viện Opus để giải mã
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync




def decode_opus_to_raw_pcm(opus_data):
    # Opus decoding parameters
    SAMPLE_RATE = 48000
    CHANNELS = 2
    FRAME_SIZE = 480  # For 48kHz
    
    # Initialize Opus decoder
    decoder = opuslib.Decoder(SAMPLE_RATE, CHANNELS)
    
    # Container for PCM data
    pcm_data = bytearray()
    
    # Process opus data in chunks
    offset = 0
    while offset < len(opus_data):
        try:
            # Get frame
            frame = opus_data[offset:offset + FRAME_SIZE]
            if not frame:
                break
                
            # Decode to PCM
            decoded = decoder.decode(bytes(frame), FRAME_SIZE * CHANNELS)
            if decoded:
                pcm_data.extend(decoded)
            
            offset += FRAME_SIZE
            
        except Exception as e:
            print(f"Decoding error at offset {offset}: {e}")
            offset += 1
            continue
            
    return bytes(pcm_data)


def start_tcp_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP
    server_socket.bind((host, port))
    server_socket.listen(1)  # Chỉ xử lý một client tại một thời điểm
    print(f"🔵 TCP Server listening on {host}:{port}")

    try:
        while True:
            print("⏳ Waiting for a connection...")
            client_socket, addr = server_socket.accept()  # Chấp nhận kết nối
            print(f"🔵 Connected by {addr}")

            buffer = bytearray()  # Tạo buffer để gom dữ liệu

            try:
                while True:
                    data = client_socket.recv(1024 * 8)  # Nhận tối đa 8KB
                    if not data:
                        break  # Nếu client ngắt kết nối, thoát vòng lặp

                    buffer.extend(data)  # Gộp dữ liệu vào buffer
                    print(f"📩 Received {len(data)} bytes from {addr}, Buffer size: {len(buffer)} bytes")
                    if len(buffer) == 4096:
                        pcm_data=decode_opus_to_raw_pcm(buffer)
                        print(f"🚀 Sent {len(pcm_data)} bytes PCM to WebSocket")
                        return
                    # # Nếu buffer đạt hoặc vượt 4096 byte, giải mã và gửi đi
                    # while len(buffer) >= 4096:
                    #     opus_chunk = bytes(buffer[:4096])  # Chuyển thành bytes trước khi giải mã
                    #     print(opus_chunk)
                    #     buffer = buffer[4096:]  # Xóa phần đã xử lý

                    #     # Giải mã Opus → PCM
                    #     pcm_data = decode_opus_to_pcm(opus_chunk)
                    #     if pcm_data:
                    #         # Gửi PCM đến WebSocket thay vì Opus
                    #         channel_layer = get_channel_layer()
                    #         async_to_sync(channel_layer.group_send)(
                    #             "audio_stream",
                    #             {
                    #                 "type": "send_audio",
                    #                 "chunk": pcm_data  # Gửi PCM
                    #             }
                    #         )
                    #         print(f"🚀 Sent {len(pcm_data)} bytes PCM to WebSocket")
                    #     else:
                    #         print("⚠️ Skipped invalid Opus chunk")

                   

            except ConnectionResetError:
                print(f"⚠️ Connection lost with {addr}")
            finally:
                client_socket.close()
                print(f"✅ Connection closed with {addr}")
    except KeyboardInterrupt:
        print("🛑 Server stopping...")
    finally:
        server_socket.close()
        print("✅ Server stopped.")
