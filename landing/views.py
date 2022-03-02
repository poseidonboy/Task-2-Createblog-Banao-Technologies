from django.shortcuts import render
from .forms import signup_form, login_form, post_form
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.contrib import messages
from .models import Newuser, post
from json import dumps



# Create your views here.
def onlanding(request):
    if request.method == "POST":
        fm=login_form(request=request, data=request.POST)
        if fm.is_valid():
            uname=fm.cleaned_data['username']
            pword=fm.cleaned_data['password']
            usr= authenticate(username=uname, password=pword)
            if usr is not None:
                login(request, usr)
                group = None
                if usr.groups.exists():
                    group = usr.groups.all()[0].name
                    if group == 'Doctor':
                        return HttpResponseRedirect('/dashdoctor/')
                    if group == 'Patient':
                        return HttpResponseRedirect('/dashpatient/')
        else:
            messages.error(request, "Invalid Credentials!!!")
            return HttpResponseRedirect('/')
    else:
        fm= login_form()
    return render(request, 'login.html', {'form': fm})
   


def signup(request):
    if request.method == "POST":
        fm=signup_form(request.POST, request.FILES)
        print(fm)
        if fm.is_valid():
            user = fm.save()
            group = Group.objects.get(name=request.POST.get('groups'))
            user.groups.add(group)
            messages.success(request, "Account created successfully!!!")
            return HttpResponseRedirect('/')
    else:
        fm= signup_form()
    return render(request, 'signup.html', {'form':fm})

    
def dashboard_doctor(request):
    if request.method == "POST":
        form = post_form(request.POST, request.FILES)
        if form.is_valid():
            pt= form.save()
            data={
                "id":pt.id,
                "title":pt.title,
                "postimg":pt.postimg.url,
                "categories":pt.categories,
                "summary":pt.summary,
                "content":pt.content,
                "is_draft":pt.is_draft,
            }
            return JsonResponse({"postdata":data})
        else:
            return JsonResponse({"msg":"Invalid data"})
    else:
        fm=post_form()
        postMH=post.objects.filter(categories='MENTAL HEALTH')
        postHD=post.objects.filter(categories='HEART DISEASE')
        postC19=post.objects.filter(categories='COVID19')
        postIZ=post.objects.filter(categories='IMMUNIZATION')
        context={
           'form':fm,
           'postMH':postMH,
           'postHD':postHD,
           'postC19':postC19,
           'postIZ':postIZ,
           'author':request.user.username,

        }
        return render(request, 'dashdoctor.html', context)

@csrf_exempt
def dashboard_patient(request):
    if request.method=="POST":
        pstobj=post.objects.all()
        blog_data=[]
        for pst in pstobj:
            item={
                "id":pst.id,
                "title":pst.title,
                "postimg":pst.postimg.url,
                "categories":pst.categories,
                "summary":pst.summary,
                "content":pst.content,
                "is_draft":pst.is_draft,
            }
            blog_data.append(item)

        return JsonResponse({"postdata": blog_data})
    else:
        defaultdata=post.objects.filter(categories="MENTAL HEALTH", is_draft=False)
    return render(request, 'dashpatient.html', {'dt':defaultdata})

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

def postview(request, pk):
    postobj=post.objects.get(id=pk)
    return render(request, 'viewpost.html', {'pt':postobj})


