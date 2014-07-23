import cgi
import os
import sys
import urllib
import datetime
import time

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import mail

#from webapp2_extras.routes import Route
from webapp2_extras.routes import PathPrefixRoute

import webapp2
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

##################################################################################
# CONFIGS ( Make Changes Here) :-
FETCH_THEM_ALL = 1000000
DEFAULT_BLOG_NAME = "DEFAULT_BLOG"# Give name for your DEFAULT_BLOG
blog_config = { 
             'main' : {'name' : 'BlogName', 'desc' : 'A blog about things i wanna write' , 'id' : 'main'},
           'motors' : {'name' : 'List Of My Fav Cars and Bikes', 'desc' : 'I Approve this list', 'id' : 'motors'}
}# Make an entry to the map above in the following format.
#  'blog_id ' : {'name' : 'blog title to be shown', 'desc' : 'description of the blog', 'id' : 'blog_name_id to your blog(for DB Key)'}
##################################################################################

def common_between_admin_and_guest(lim, off, unique_id, url, url_linktext, blog_id, blog_key, is_admin=False):
    limit  = -1
    offset = -1
    if lim=="no" and off=="":
        limit = FETCH_THEM_ALL
        offset = 0
    elif lim=="" and off=="":
        limit  = 5
        offset = 0
    elif lim!="" and off=="":
        if lim.isdigit():
            limit  = int(lim)
            offset = 0
        else:
            limit  = 5
            offset = 0
    elif lim=="" and off!="":
        if off.isdigit():
            limit  = 5
            offset = int(off)
        else:
            limit  = 5
            offset = 0
    elif lim!="" and off!="":
        if lim.isdigit() and off.isdigit():
            limit  = int(lim)
            offset = int(off)
        else:
            limit  = 5
            offset = 0
    else:
        limit  = 5
        offset = 0

    if unique_id == "":
        #blog_key = get_blog_key(self.app.config.get(blog_id)['id'])
        if is_admin:
            q = Article.query(ancestor=blog_key)
        else:
            q = Article.query(Article.draft==False,ancestor=blog_key)
        q.order(-Article.updated_date)
        articles = q.fetch(limit, offset=offset)
        comments = []
    else:
        article_key = ndb.Key(urlsafe=unique_id)
        articles     = [article_key.get()]
        comments_query = Comments.query(ancestor=comments_blog_key(unique_id)).order(-Comments.date)
        comments = comments_query.fetch()

    template_values = { 'articles' : articles ,
                        'num_articles' : len(articles),
                        'limit' : limit, 
                        'offset' : offset,
                        'unique_id' : unique_id,
                        'comments' : comments,
                        'num_comments' : len(comments),
                        'login_url' : url,
                        'login_url_text' : url_linktext,
                        'blog_id' : blog_id }

    return template_values

##################################################################################
def chunks(l, n):
    """Returns a list of small lists each of size n if given a list l"""
    if n < 1:
        n = 1
    return [l[i:i + n] for i in range(0, len(l), n)]
##################################################################################

##################################################################################

def get_blog_key(blog_name=DEFAULT_BLOG_NAME):
    """We make this key so as to allow multiple blogs to run on the same site"""
    if blog_name == None or blog_name == "":
        blog_name = DEFAULT_BLOG_NAME
    return ndb.Key('Article', blog_name)

class Article(ndb.Model):
    """Models individual Blog entries."""
    unique_id      = ndb.StringProperty(indexed=True)
    published_date = ndb.DateTimeProperty()
    updated_date   = ndb.DateTimeProperty(auto_now=True)
    author         = ndb.UserProperty()
    tags           = ndb.StringProperty(indexed=True)
    blog_title     = ndb.StringProperty(indexed=False)
    blog_head      = ndb.StringProperty(indexed=False)
    blog_body      = ndb.StringProperty(indexed=False)
    draft          = ndb.BooleanProperty(indexed=True,required=True, default=True)

    def str(self):
        "published_date:" + str(published_date) + ";updated_date:" + str(updated_date) + ";author:" + str(author) + ";tags:" + str(tags) + ";blog_title:" + str(blog_title) + ";blog_head:" + str(blog_head) + ";blog_body:" + str(blog_body) + ";draft:" + str(draft)

##################################################################################

def comments_blog_key(unique_id):
    """Constructs a Datastore key to identify which Article the comments are for."""
    return ndb.Key('Comments', unique_id)

class Comments(ndb.Model):
    """Models Comments"""
    author = ndb.UserProperty()
    comment = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

##################################################################################

class BlogPage(webapp2.RequestHandler):
    def get(self, blog_id):
        if not blog_id in self.app.config.keys():
            self.redirect('/')
            return
        unique_id = self.request.get('unique_id')
        lim = self.request.get('lim')
        off = self.request.get('off')
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = users.get_current_user().nickname()
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        blog_key = ""
        if unique_id == "":
            blog_key = get_blog_key(self.app.config.get(blog_id)['id'])

        template_values = common_between_admin_and_guest(lim, off, unique_id, url, url_linktext, blog_id, blog_key, is_admin=False)
        template_values['blog_name'] = self.app.config.get(blog_id)['name']
        template_values['blog_desc'] = self.app.config.get(blog_id)['desc']

        template = JINJA_ENVIRONMENT.get_template('templates/blog_'+self.app.config.get(blog_id)['id']+'.html')
        self.response.write(template.render(template_values))

##################################################################################

class AdminBlogPage(webapp2.RequestHandler):
    def get(self, blog_id):
        if not blog_id in self.app.config.keys():
            self.redirect('/')
            return
        unique_id = self.request.get('unique_id')
        lim = self.request.get('lim')
        off = self.request.get('off')
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = users.get_current_user().nickname()
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        blog_key = ""
        if unique_id == "":
            blog_key = get_blog_key(self.app.config.get(blog_id)['id'])
        template_values = common_between_admin_and_guest(lim, off, unique_id, url, url_linktext, blog_id, blog_key, is_admin=True)
        template_values['blog_name'] = self.app.config.get(blog_id)['name']
        template_values['blog_desc'] = self.app.config.get(blog_id)['desc']
        template = JINJA_ENVIRONMENT.get_template('templates/blog_admin.html')
        self.response.write(template.render(template_values))

##################################################################################

class CommentOnBlog(webapp2.RequestHandler):
    def post(self, blog_id):
        unique_id = self.request.get('unique_id')
        comment = Comments(parent=comments_blog_key(unique_id))
        if users.get_current_user():
            comment.author = users.get_current_user()
        comment.comment = self.request.get('comment')
        comment.put()
        self.redirect('/blogs/'+blog_id+'/blog?unique_id='+unique_id)
                
##################################################################################

class SaveBlog(webapp2.RequestHandler):
    '''
    1. New Blog Publish=No So Draft
    2. New Blog Publish=Yes
    3. Old Blog Publish always Yes
    '''
    def post(self, blog_id):
        if not blog_id in self.app.config.keys():
            self.redirect('/')
            return
        user_name = users.get_current_user()
        is_draft = True
        if (self.request.get('publish') == "Yes"):
            is_draft = False
        unique_id = self.request.get('unique_id')
        current_datetime = datetime.datetime.now()
        
        if unique_id == "":
            # New article .. published_date will be None for new drafts
            article  = Article(parent=get_blog_key(self.app.config.get(blog_id)['id']),
                               author = user_name,
                               tags   = self.request.get('tags'),
                               blog_title= self.request.get('blog_title'),
                               blog_head = self.request.get('blog_head'),
                               blog_body = self.request.get('blog_body'),
                               draft     = is_draft
                              )
            if not is_draft:
                article.published_date = current_datetime
        else:
            # Update Existing Article
            article_key = ndb.Key(urlsafe=unique_id)
            article     = article_key.get()
            article.tags       = self.request.get('tags')
            article.blog_title = self.request.get('blog_title')
            article.blog_head  = self.request.get('blog_head')
            article.blog_body  = self.request.get('blog_body')
            article.draft      = is_draft
            if article.draft:# Article was a draft Previously
                if not is_draft:# It has to be published now:
                    article.published_date = current_datetime

        article_key = article.put()
        article.unique_id = article_key.urlsafe()
        article.put()
        time.sleep(1) # Required so prevent read before index commit refer https://developers.google.com/appengine/articles/transaction_isolation
        self.redirect('/blogs/'+blog_id+'/blog')

##################################################################################

class EditBlog(webapp2.RequestHandler):
    def get(self, blog_id):
        unique_id = self.request.get('unique_id')
        template_values = {}
        if unique_id == "":
           template_values = { 'author' : users.get_current_user()}
        else:
            article_key = ndb.Key(urlsafe=unique_id)
            article     = article_key.get()
            template_values = { 'author' : users.get_current_user(), 'article' : article }
            
        template = JINJA_ENVIRONMENT.get_template('templates/blog_edit.html')
        self.response.write(template.render(template_values))

##################################################################################

class DeleteBlog(webapp2.RequestHandler):
    def get(self, blog_id):
        unique_id = self.request.get('unique_id')
        if unique_id == "":
            self.redirect('/blogs'+blog_id+'/blog')
            return

        #q = ndb.gql("SELECT * FROM Article WHERE unique_id = \'" + unique_id + "\'")
        q = Article.query(Article.unique_id==unique_id, ancestor=get_blog_key(self.app.config.get(blog_id)['id']))
        template_values = {}
        articles = q.fetch()
        for article in articles:
            article.key.delete()

        self.redirect('/blogs/'+blog_id+'/blog') 

##################################################################################

application = webapp2.WSGIApplication([
    (r'/blogs/(.*)/blog', BlogPage),
    (r'/blogs/(.*)/blog/comment', CommentOnBlog),
    (r'/blogsadmin/(.*)/blog', AdminBlogPage),
    (r'/blogsadmin/(.*)/blog/save', SaveBlog),
    (r'/blogsadmin/(.*)/blog/delete', DeleteBlog),
], config=blog_config, debug=True)

##################################################################################

