from django.http import HttpResponse, request
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from .models import SearchHistory, Tag
import json
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
def article(request,article_url):
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path='chromedriver',chrome_options=chrome_options)
    driver.get(article_url)
    driver.close()

@csrf_protect
@login_required
def tags_query(request,tag,page):
    tag = tag.lower()
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path='chromedriver',chrome_options=chrome_options)
    url = 'https://medium.com/tag/'+tag
    Tag.objects.get_or_create(keyword=tag)
    driver.get(url)
    time.sleep(1)
    content_list = []
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    elements = driver.find_elements_by_css_selector('.streamItem.streamItem--postPreview.js-streamItem')
    similar_tags = driver.find_element_by_css_selector('.tags.tags--postTags.tags--light').find_elements_by_tag_name('li')
    sim_tags=[]
    for tag in similar_tags:
        sim_tags.append(tag.find_element_by_tag_name('a').get_attribute('text'))
    for element in elements:
        blog_details = dict()
        main_element = element.find_element_by_tag_name('div').find_element_by_tag_name('div')
        blog_details['url'] = main_element.find_element_by_css_selector('.postArticle-readMore').find_element_by_tag_name('a').get_attribute('href')
        blog_details['author_name'] = main_element.find_element_by_css_selector('.u-clearfix.u-marginBottom15.u-paddingTop5').find_element_by_tag_name('div').find_element_by_tag_name('div').find_element_by_css_selector('.postMetaInline.postMetaInline-authorLockup.ui-captionStrong.u-flex1.u-noWrapWithEllipsis').find_element_by_css_selector('.ds-link.ds-link--styleSubtle.link.link--darken.link--accent.u-accentColor--textNormal.u-accentColor--textDarken').text
        blog_details['heading'] = main_element.find_element_by_tag_name('h3').text
        blog_details['sub_head'] = main_element.find_element_by_tag_name('h4').text
        content_list.append(blog_details)

    driver.close()
    data = {'sim_tags':sim_tags,'blog_list':content_list}
    data = json.dumps(data)
    return HttpResponse(data, content_type='application/json')

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