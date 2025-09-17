from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model

User = get_user_model()


def send_verification_email(request, user: User) -> None:
    """Sends a verification email to a user.

    Args:
        request: The HTTP request object.
        user: The user to send verification email to.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    link = request.build_absolute_uri(reverse('activate', args=[uid, token]))

    send_mail(
        subject='Verify your email',
        message=f'Click the link to verify: {link}',
        from_email=None,
        recipient_list=[user.email],
        fail_silently=False
    )
