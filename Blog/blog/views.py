#coding=utf-8
from django.shortcuts import render,redirect
import logging
from django.conf import settings
from models import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.db import connection
from django.db.models import Count
from forms import *
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.hashers import make_password



logger = logging.getLogger('blog.views')
# Create your views here.
def global_setting(request):
    SITE_URL = settings.SITE_URL
    SITE_NAME = settings.SITE_NAME
    SITE_DESC = settings.SITE_DESC

    #ad_imgurl_list = Ad.objects.all().values('image_url')
    ad_imgurl_list=Ad.objects.filter(status=True)

    category_list = Category.objects.all()

    article_click_list = Article.objects.all().order_by('-click_count')[:6]

    comment_count_list = Comment.objects.values('article').annotate(comment_count=Count('article')).order_by('-comment_count')
    article_comment_list = [Article.objects.get(pk=comment['article']) for comment in comment_count_list][:6]

    article_recommend_list = Article.objects.all().order_by('is_recommend')[:6]

    tag_list = Tag.objects.all()

    archive_list = Article.objects.distinct_date() #归档文章 重写了objects工具包

    links_list = Links.objects.all()
    return locals()

def getpage(request, article_list):
    paginator = Paginator(article_list, 4) #把上面的文章结果集进行分页来显示（每页2条数据） ###分页对象paginator
    try:
        page = int(request.GET.get('page', 1)) #获取当前页的页码数page对象（用户什么都没传值 默认页码为1）
        article_list=paginator.page(page)#返回当前页码的 数据
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        article_list = paginator.page(1)#异常:错误传值或者不传值（网页第一次打开时）时 获取第1页数据展示
    return article_list

def index(request):
    try:
        article_list=Article.objects.all()
        article_list = getpage(request, article_list)
    except Exception as e:
        logger.error(e)
    return render(request,'index.html',locals())

def archive(request):
    try:
        year = request.GET.get('year', None)
        month = request.GET.get('month', None)
        article_list = Article.objects.filter(date_publish__icontains=year + '-' + month)
        article_list = getpage(request, article_list)
    except Exception as e:
        logger.error(e)
    return  render(request,'archive.html',locals())

def tag(request):##当前标签的文章s 归档页面处理函数
    try:
        id = request.GET.get( "id", None)
        tag=Tag.objects.get(pk=id)
        tagarticle_list = tag.article_set.all()
        article_list=getpage(request,tagarticle_list)
    except Exception as e:
        logger.error(e)
    return render(request, 'tag_archive.html', locals())

def article(request): #当前文章详情对象
    try:
        # 获取文章id
        id = request.GET.get('id', None) #获取用户访问article--url时携带的ID值
        try:
            # 获取文章信息对象
            article = Article.objects.get(pk=id) #从数据库查询:用户传过来的ID作为文章ID进行获得文章的查询
            article.click_count+=1
            article.save() #保存浏览的次数
        except Article.DoesNotExist: #若用户传过来的ID在数据库中没有对应这个文章ID号 触发异常下面提示没有此ID号的文章
            return render(request, 'failure.html', {'reason': '没有找到对应的文章'})

        # 评论表单对象
        comment_form = CommentForm({'author': request.user.username, #初始化 表单对象的值
                                    'email': request.user.email,
                                    'url': request.user.url,
                                    'article': id} if request.user.is_authenticated() else{'article': id})#判断登录显示与非登录显示-文章的id
        # 获取（读取）评论信息
		##########做评论的子父层级的划分############
        commentsnum = len(Comment.objects.filter(article=article).order_by('id')) #取出id为"id"的文章的评论总数

        comments = Comment.objects.filter(article=article).order_by('id')#一次性取出 文章的所有评论 集合（按评论的id进行集合的排序,只取有评论的文章）
        comment_list = [] #定义评论容器列表对象 用于存放评论（模板里会用到的评论列表）
        for comment in comments: #循环文章的所有评论(父,子等评论所有评论)
            for item in comment_list: #item当前评论
                if not hasattr(item, 'children_comment'): #判断当前评论列表里是否有子评论
                    setattr(item, 'children_comment', []) #添加子评论到当前（相对子为父了）评论列表里
                if comment.pid == item: #判断文章评论是否有comment.pid父级评论 有的话再判断文章 父评论 是否是 当前评论 （文章评论的父级评论==当前评论的话 则为当前评论为该文章评论的父评论（父 子 评论关系））
                    item.children_comment.append(comment) #添加 当前评论（相对子为父了）的子评论（coment）到当前评论的 子评论列表 里
                    break
            if comment.pid is None: #如果该文章评论的pid为空 则这个评论不是其他评论的子评论(理解为 没有被回复的评论)
                comment_list.append(comment) # 没有子评论的评论直接添加到评论列表里（评论list）
    except Exception as e:
        logger.error(e)
    return render(request, 'article.html', locals())

def comment_post(request):
    try:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid(): #表单提交信息进行服务端的验证
            #获取表单信息
            comment = Comment.objects.create(username=comment_form.cleaned_data["author"], #验证通过 创建评论对象 初始化
                                             email=comment_form.cleaned_data["email"],
                                             url=comment_form.cleaned_data["url"],
                                             content=comment_form.cleaned_data["comment"],
                                             article_id=comment_form.cleaned_data["article"],
                                             user=request.user if request.user.is_authenticated() else None)
            comment.save()#评论保存到数据库
        else:
            return render(request, 'failure.html', {'reason': comment_form.errors}) #没通过验证 把错误信息保存在errors对象里返回到模板
    except Exception as e:
        logger.error(e)
    return redirect(request.META['HTTP_REFERER'])


# 注销
def do_logout(request):
    try:
        logout(request) #调用django自带的注销方法 进行注销 （主要对session进行清除）
    except Exception as e:
        print e
        logger.error(e)
    return redirect(request.META['HTTP_REFERER'])

# 注册
def do_reg(request):
    try:
        if request.method == 'POST': #post表单提交
            reg_form = RegForm(request.POST)#向表单提交相关注册信息 赋值 给注册表单对象（RegForm对象来源于froms.py）
            if reg_form.is_valid():#表单对象服务端验证 验证通过后
                # 注册
                user = User.objects.create(username=reg_form.cleaned_data["username"],#通过cleaned_data把模板的表单初始数值传进来
                                    email=reg_form.cleaned_data["email"],
                                    url=reg_form.cleaned_data["url"],
                                    password=make_password(reg_form.cleaned_data["password"]),) #make_password 自带密码加密方式（可以自定义eg:手机+邮箱等方式）
                user.save() #保存user到数据库 完成注册

                # 登录
                user.backend = 'django.contrib.auth.backends.ModelBackend' # 指定默认的登录验证方式（默认用户名+密码组合登录）
                login(request, user) #调用login django自带登录方法 进行 登录 通过user对象
                return redirect(request.POST.get('source_url')) #调用redirect方法进行地址跳转到页面来源地址（注册之前的那个页面）
            else:
                return render(request, 'failure.html', {'reason': reg_form.errors})
        else:
            reg_form = RegForm()#get提交表单---》直接到注册页面:--初始化表单对象reg_form 然后在下面将该对象传到reg.html模板
    except Exception as e:
        logger.error(e)

    return render(request, 'reg.html', locals())

# 登录
def do_login(request):
    try:
        if request.method == 'POST':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                # 登录
                username = login_form.cleaned_data["username"] #得到用户提交的用户名
                password = login_form.cleaned_data["password"]#得到用户提交的密码
                user = authenticate(username=username, password=password) #调用authenticate（也可以自定义验证方式eg：手机+邮箱+密码等方式）方法进行用户名,密码 进行验证
                if user is not None:
                    user.backend = 'django.contrib.auth.backends.ModelBackend' # 指定默认的登录验证方式
                    login(request, user)
                else:
                    return render(request, 'failure.html', {'reason': '登录验证失败'})
                return redirect(request.POST.get('source_url')) #登录成功跳转到页面来源地址
            else:
                return render(request, 'failure.html', {'reason': login_form.errors})
        else:
            login_form = LoginForm()
    except Exception as e:
        logger.error(e)
    return render(request, 'login.html', locals())

def category(request):
    try:
        # 先获取客户端提交的信息
        cid = request.GET.get('id', None)
        try:
            category = Category.objects.get(pk=cid)
        except Category.DoesNotExist:
            return render(request, 'failure.html', {'reason': '此分类暂无文章,待续....'})
        article_list = category.article_set.all()
        article_list = getpage(request, article_list)
    except Exception as e:
        logger.error(e)
    return render(request, 'category.html', locals())