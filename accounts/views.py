from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, FormView, ListView

from accounts.forms import (
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
        queryset = User.objects.all().order_by("-date_joined")
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


class UserDetailView(AdminRequiredMixin, DetailView):
    model = User
    template_name = "accounts/user_detail.html"
    context_object_name = "account"


class UserToggleActiveView(AdminRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.pk == request.user.pk:
            messages.error(request, "Bạn không thể tự khóa tài khoản của chính mình.")
        else:
            user.is_active = not user.is_active
            user.save(update_fields=["is_active"])
            if user.is_active:
                messages.success(request, f"Đã mở khóa tài khoản {user.username}.")
            else:
                messages.warning(request, f"Đã khóa tài khoản {user.username}.")

        next_url = request.POST.get("next")
        if next_url:
            return redirect(next_url)
        return redirect("accounts:user-list")
