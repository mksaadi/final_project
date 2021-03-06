from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.post_list_view, name='post_view'),
    path('job_list_view/', views.job_list_view, name='job_list_view'),
    path('workspaces/', views.workspaces, name='workspaces'),
    path('find_jobs/', views.find_jobs, name='find_jobs'),
    path('approve_job_request/', views.approve_job_request, name='approve_job_request'),
    path('like_unlike', views.like_unlike_view, name='like_unlike'),
    path('<pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    path('<pk>/update/', views.PostUpdateView.as_view(), name='post-update'),
    path('send_job_request/', views.send_job_request, name='send_job_request'),
    path('job/<int:job_id>/', views.job_detail_view, name='job_detail_view'),
    path('employee_list/', views.employee_list, name='employee_list'),





]