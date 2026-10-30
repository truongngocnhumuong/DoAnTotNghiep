from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView

from accounts.forms import (
    AdminUserCreateForm,
    AdminUserUpdateForm,
    CandidateRegistrationForm,
    RoleBasedAuthenticationForm,
)
from accounts.mixins import AdminRequiredMixin
from accounts.models import User
from accounts.utils import get_role_redirect_url


class CandidateRegistrationView(FormView):
    template_name = "accounts/register.html"
    form_class = CandidateRegistrationForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(get_role_redirect_url(request.user))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "Đăng ký thành công. Vui lòng đăng nhập bằng tài khoản vừa tạo.",
        )
        return redirect("accounts:login")


class RoleBasedLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = RoleBasedAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        redirect_to = self.get_redirect_url()
        if redirect_to:
            return redirect_to
        return get_role_redirect_url(self.request.user)


class RoleBasedLogoutView(LogoutView):
    http_method_names = ["post", "options"]
    next_page = reverse_lazy("jobs:home")


class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        queryset = User.objects.all()
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query)
                | Q(email__icontains=query)
                | Q(full_name__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "").strip()
        return context


class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = AdminUserCreateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user-list")

    def form_valid(self, form):
        messages.success(self.request, "Đã tạo tài khoản thành công.")
        return super().form_valid(form)


class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = AdminUserUpdateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user-list")

    def form_valid(self, form):
        messages.success(self.request, "Đã cập nhật tài khoản thành công.")
        return super().form_valid(form)


class UserDetailView(AdminRequiredMixin, DetailView):
    model = User
    template_name = "accounts/user_detail.html"
    context_object_name = "account"
