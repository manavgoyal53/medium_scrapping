from django.http import HttpResponse, request
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from .models import SearchHistory, Tag, Article
import json
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
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
    obj = Article.objects.get(url=article_url)
    driver = webdriver.Chrome(executable_path='chromedriver',chrome_options=chrome_options)
    driver.get(article_url)
    links = driver.find_elements_by_tag_name('a')
    similar_tags = []
    for link in links:
        url = link.get_attribute('href')
        check1 = url.find('/tag/')
        check2 = url.find('/tagged/')
        if check1 !=-1 or check2!=-1:
            tag,cretaed = Tag.objects.get_or_create(keyword=link.get_attribute('text').lower())
            obj.tags.add(tag)
            similar_tags.append(tag)
    driver.close()
    context = {'article':obj,'similar_tags':similar_tags}
    return render(request,'medium_scrap/article.html',context)
    

@csrf_protect
@login_required
def tags_query(request,tag,page):
    tag = tag.lower()
    chrome_options = Options()
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path='chromedriver',chrome_options=chrome_options)
    url = 'https://medium.com/tag/'+tag
    user = User.objects.get(username=request.user)
    object, created= Tag.objects.get_or_create(keyword=tag)
    SearchHistory.objects.get_or_create(user=user,tag=object)
    driver.set_window_size(1920, 1080)
    driver.get(url)
    time.sleep(5)
    content_list = []
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(9)
    elements = driver.find_elements_by_css_selector('.streamItem.streamItem--postPreview.js-streamItem')[page*10:(page+1)*10]
    similar_tags = driver.find_element_by_css_selector('.tags.tags--postTags.tags--light').find_elements_by_tag_name('li')
    sim_tags=[]
    for tag in similar_tags:
        sim_tags.append(tag.find_element_by_tag_name('a').get_attribute('text'))
    print(elements)
    for element in elements:
        blog_details = dict()
        main_element = element.find_element_by_tag_name('div').find_element_by_tag_name('div')
        # url = main_element.find_element_by_class_name('postArticle-readMore').find_element_by_tag_name('a').get_attribute('href')
        url = ''
        url = blog_details['url'] = url.split('?')[0]
        article_obj,created = Article.objects.get_or_create(url=url)
        if created:
            blog_details['author_name'] = main_element.find_element_by_css_selector('.u-clearfix.u-marginBottom15.u-paddingTop5').find_element_by_tag_name('div').find_element_by_tag_name('div').find_element_by_css_selector('.postMetaInline.postMetaInline-authorLockup.ui-captionStrong.u-flex1.u-noWrapWithEllipsis').find_element_by_css_selector('.ds-link.ds-link--styleSubtle.link.link--darken.link--accent.u-accentColor--textNormal.u-accentColor--textDarken').text
            blog_details['heading'] = main_element.find_element_by_tag_name('h3').text
            article_obj.author = blog_details['author_name']
            article_obj.title = blog_details['heading']
            claps_resp = main_element.find_element_by_css_selector('.u-clearfix.u-paddingTop10')
            try:
                claps = claps_resp.find_element_by_class_name('.u-floatLeft').find_element_by_tag_name('div').find_element_by_tag_name('span').find_element_by_tag_name('button').get_attribute('innerHTML')
            except NoSuchElementException:
                claps = str(0)
            try:
                resp = claps_resp.find_element_by_css_selector('.buttonSet.u-floatRight').find_element_by_tag_name('a').get_attribute('text')
            except NoSuchElementException:
                resp = str(0)
            try:
                blog_details['sub_head'] = main_element.find_element_by_tag_name('h4').text
            except NoSuchElementException:
                blog_details['sub_head'] = ''
            article_obj.sub_title = blog_details['sub_head']
            article_obj.claps = claps
            article_obj.responses = resp
            article_obj.save()
        else:
            blog_details['author_name'] = article_obj.author
            blog_details['sub_head'] = article_obj.sub_title
            blog_details['heading'] = article_obj.title

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