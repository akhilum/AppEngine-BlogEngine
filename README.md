AppEngine-BlogEngine
====================

A simple blog engine to set up blogs on Google App Engine.

====================

This simple script allows you to host blogs on your Google App Engine website. Just add the blog details to the config section and provide the html page for your blog for this engine to render onto. You are good to go.

USAGE:-<br/>
<em> Its as easy as 1,2,3 </em>

1. Create an <a href="https://developers.google.com/appengine/docs/python/gettingstartedpython27/introduction">App Engine App</a>. place blog.py into your main folder and into your app.yaml file add the following entry

<pre>
handlers:
- url: /blogs.*
  script: blog.application
</pre>

2. Goto blog.py file. Search for "CONFIGS" at the top of the file.
     in the blog_config array make an entry for each of the blog you wanna make.

3. make a directory called templates/ add blog_<Your_blog_id>.html file there which is used to render the blog.
     so if your blog_id is called 'abcd' add blog_abcd.html there.



<div class="container">
<p>
Its a very simple script that handles different aspects like :-
</p>
<ul>
<li>Multiple users</li>
<li>URL safe blog ids</li> 
<li>Admin access to blogs</li>
<li>Commenting System</li>
<li>Ability to save as drafts</li>
</ul>
</p>
</div>

This script returns a dictionary with the following values to Junja template engine
<pre>
template_values = {     'articles' : articles ,
                        'num_articles' : len(articles),
                        'limit' : limit,
                        'offset' : offset,
                        'unique_id' : unique_id,
                        'comments' : comments,
                        'num_comments' : len(comments),
                        'login_url' : url,
                        'login_url_text' : url_linktext,
                        'blog_id' : blog_id,
                        'blog_name' = self.app.config.get(blog_id)['name'],
                        'blog_desc' = self.app.config.get(blog_id)['desc']
                  }
</pre>                  
Here article is a blog post

Which will be instasiated as per the following rules:-

1. articles will be an array with the articles you want to display. If you are viewing/editing one article it will have only one article with unique id stored in unique_id
2. num_articles will have length of articles array
3. limit and offset will give the range of articles that are being displayed.
      If you have 50 blog posts. And you show 5 blog posts in a page. If You are displaying blog posts numbered (12-16). Then limit will be 5 & offset will be 11
4. unique_id will be the unique id of the blog post if you are viewing a single blog post in detail.
5. comments will be the array having the comments.
6. num_comments will be the length of comments array
7. login_url and login_url_text will be the url and text to log in a user to make a comment (optional). You can have to user comment as anonymous.
8. blog_id, blog_name and blog_desc apply if you have hosted multiple blogs on the same site. Then the config parameters that you give to the application will be used to control this parameters.



