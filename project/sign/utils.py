def request_object(model, **kwargs):
    current_group, created = model.objects.get_or_create(**kwargs)
    return current_group