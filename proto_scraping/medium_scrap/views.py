from django.http import HttpResponse, request
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import SearchHistory, Tag
import json
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import ElementClickInterceptedException
import time

def home(request):
    if not request.user.is_authenticated:
        context = {}
    else:
        user = User.objects.get(username=request.user)
        history = SearchHistory.objects.filter(user=user)
        context = {'history':history}
    return render(request,'medium_scrap/home.html',context)

@login_required
def tags_query(request,tag,page):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(executable_path='chromedriver',chrome_options=chrome_options)
    url = 'https://medium.com/tag/'+tag
    driver.get(url)
    time.sleep(3)
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    elements = driver.find_elements_by_css_selector('.streamItem.streamItem--postPreview.js-streamItem')
    print(elements)
    # for element in elements:
    #     main_element = element.find_element_by_tag_name('div').find_element_by_tag_name('div')
    #     author_name = main_element.find_element_by_css_selector('u-clearfix.u-marginBottom15.u-paddingTop5').find_element_by_tag_name('div').find_element_by_tag_name('div').find_element_by_css_selector('postMetaInline.postMetaInline-authorLockup.ui-captionStrong.u-flex1.u-noWrapWithEllipsis').find_element_by_css_selector('ds-link.ds-link--styleSubtle.link.link--darken link--accent.u-accentColor--textNormal.u-accentColor--textDarken')
    #     print(author_name)
    # json_object = json.dumps(elements)
    json_object = json.dumps(dict())
    return HttpResponse(json_object, content_type='application/json')

def signup_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        print("post")
        form = UserCreationForm(request.POST)
        if form.is_valid():
            print("Valid")
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(request, username=username, password=password)
            login(request,user)
            return redirect('home')
    return render(request, 'medium_scrap/signup.html')

def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST" :
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return redirect('login')
    else:
       return render(request, 'medium_scrap/login.html',{})

def logout_user(request):
    logout(request)
    return redirect('home')