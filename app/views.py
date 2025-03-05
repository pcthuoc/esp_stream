# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
from audiofile.models import Audio
from django.views.generic.list import ListView
from django.http import FileResponse, Http404
from django.conf import settings
import os
from django.http import JsonResponse, Http404

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import sys
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@login_required(login_url="/login/")
def home(request):
    audios = Audio.objects.all().order_by('-date_created')[:5]
    context = {
        'segment': 'dashboard',
        'audios': audios,
        'MEDIA_URL' : settings.MEDIA_URL
    }

    html_template = loader.get_template('dashboard.html')
    return HttpResponse(html_template.render(context, request))

class AudioListView(LoginRequiredMixin, ListView):
    model = Audio
    paginate_by = 5  # Hiển thị 10 file mỗi trang
    template_name = 'list_file.html'
    context_object_name = 'audios'
    login_url = "/login/"

    def get_queryset(self):
        queryset = Audio.objects.all().order_by('-date_created')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['segment'] = 'listfile'  
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context



def download_audio(request, filename):
    if not filename.endswith(".mp3"):
        filename += ".mp3"
    file_path = os.path.join(settings.MEDIA_ROOT, 'audio', filename)
    
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), as_attachment=True)
        return response
    else:
        raise Http404("File không tồn tại")


def delete_audio(request, filename):
    """Xóa bản ghi trong database trước, sau đó xóa file trong hệ thống"""
    if request.method == "POST":
        try:
            # Tìm và xóa bản ghi trong database trước
            audio_record = Audio.objects.get(name_file=filename)
            audio_record.delete()  # Xóa bản ghi trong database

            # Định nghĩa đường dẫn file (thêm .mp3 vào filename)
            file_path = os.path.join(settings.MEDIA_ROOT, "audio", f"{filename}.mp3")

            # Thử xóa file nếu nó tồn tại (không quan trọng nếu không tồn tại)
            if os.path.exists(file_path):
                os.remove(file_path)  # Xóa file âm thanh

            return JsonResponse({"success": True, "message": "Bản ghi đã xóa thành công!"}, status=200)

        except Audio.DoesNotExist:
            return JsonResponse({"success": False, "message": "Bản ghi không tồn tại trong database!"}, status=404)

    return JsonResponse({"success": False, "message": "Yêu cầu không hợp lệ!"}, status=400)


@csrf_exempt
def upload_audio(request):
    if request.method == 'POST':
        chunk = request.body  # Lấy dữ liệu âm thanh nhị phân

        if not chunk:
            return JsonResponse({"message": "No audio data received"}, status=400)
        
        print(type(chunk))  # In kiểu dữ liệu của chunk để debug
        # Gửi dữ liệu âm thanh đến WebSocket Group
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "audio_stream",  # Tên nhóm (có thể tùy chỉnh theo yêu cầu ứng dụng)
            {
                "type": "send_audio", 
                "chunk": chunk
            }
        )
        
        return JsonResponse({"message": "Chunk received"}, status=200)
    
    return JsonResponse({"message": "Invalid request"}, status=400)


def stream_audio(request):
    return render(request, "stream.html")





@csrf_exempt
def receive_audio(request):
    """ Nhận dữ liệu audio và in ra console thay vì lưu file """
    if request.method == "POST":
        if request.headers.get('Transfer-Encoding', '').lower() != 'chunked':
            return JsonResponse({"error": "Chunked transfer encoding required"}, status=400)

        total_bytes = 0
        data = []

        try:
            while True:
                chunk_size_data = request.body[:2]  # Đọc 2 byte đầu tiên
                if len(chunk_size_data) < 2:
                    break  # Hết dữ liệu

                chunk_size = int(chunk_size_data.hex(), 16)
                if chunk_size == 0:
                    break  # Chunk kết thúc

                chunk_data = request.body[2:2+chunk_size]
                total_bytes += len(chunk_data)
                data.append(chunk_data)

                # Xóa phần đã đọc khỏi request.body
                request.body = request.body[2+chunk_size+2:]

            print(f"Received Audio Data: {total_bytes} bytes")

            return JsonResponse({"message": f"Received {total_bytes} bytes"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Invalid request method"}, status=400)
