from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from core.models import Profile
from django.http import HttpResponse
from .models import Chat
import json
from django.http import JsonResponse
from uuid import UUID
# Create your views here.



class UUIDEncoder(json.JSONEncoder):
    def default(self, obj) :
        try:
            if isinstance(obj, UUID):
                return obj.hex
            return json.JSONEncoder.default(self.obj)
        except:
            return    

@login_required(login_url='/login')
def support_user(request):
    context= {
        "page_title" : "Support | Luua"
    }
    return render(request, 'chat/support.html', context)


@staff_member_required(login_url='/manage')
@login_required(login_url='/manage/login')
def manage_chat_group(request):
    show = 0
    if 'show' in request.GET and int(request.GET['show']) > 0:
        show =  int(request.GET['show'])*10
    try:        
        chats = Chat.last_chat_group() # .distinct('profile')
    except Exception as err:
        print(err)
        return JsonResponse(json.dumps({
            "status_code" : 500,
            "error" : str(err),
        }), safe=False)
    return JsonResponse(json.dumps({
        "status_code" : 200,
        "show" : show,
        "chats" : chats
    }, cls=UUIDEncoder), safe=False)

@staff_member_required(login_url='/manage')
@login_required(login_url='/manage/login')
def support_chat(request, profile_id):
    if Profile.objects.filter(uid=profile_id).exists():
        context = {
            "profile_id" :  profile_id
        }
        return render(request, 'chat/chat.html', context)   
    return HttpResponse('<h1>Invalid user_id</h1>')    


@staff_member_required(login_url='/manage')
@login_required(login_url='/manage/login')
def all_latest_chat_only(request):
    return render(request, 'chat/m-group-chat.html')   

@login_required(login_url='/login')
def older_message(request):
    if 'chat_id' not in request.GET or not Profile.objects.filter(uid=request.GET['chat_id']).exists():
        return JsonResponse({"status_code" : 400, "error" : "chat_id_invalid"})
    chat_id = str(request.GET['chat_id']).replace('-', '')    
    return JsonResponse(json.dumps({
        "status_code" : 200,
        "type" : "old-chats",
        "chats" : list(Chat.objects.filter(profile=Profile.objects.get(uid=chat_id)).values())
    }, cls=UUIDEncoder), safe=False)