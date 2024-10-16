
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API Routes
    path("create", views.create_post, name="create_post"),
    path("posts/<int:post_id>", views.edit_post, name="edit_post"),
    path("profile/<str:username>/<int:page_number>", views.profile, name="profile"),
    path("following/<int:page_number>", views.following, name="following"),
    path("page/<int:page_number>", views.get_posts, name="get_posts")
]
