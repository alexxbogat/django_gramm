def set_email_verified(strategy, details, user=None, backend=None, *args, **kwargs):
    """Marks the user's email as verified and activates the user account."""
    if user and not user.email_verified:
        user.email_verified = True
        user.is_active = True
        user.save()
