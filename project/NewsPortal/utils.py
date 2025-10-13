def create_or_update(context, request_path):
    if "create" in request_path:
        title = "Добавление "
    else:
        title = "Редактирование "

    if "news" in request_path:
        title += "новости"
    else:
        title += "статьи"

    context['create_or_update'] = title
    return context