from django import template

register = template.Library()


@register.filter()
def censor(text, bad_words=None):
    if not isinstance(text, str):
        raise TypeError("Фильтр 'censor' применяется только к строкам")

    if bad_words is None:
        bad_words = {'редиска', 'негодяй', 'мерзавец', 'подлец', 'мошенник'}

    for word in bad_words:
        text = text.replace(word, word[0] + '*' * (len(word) - 1))
        text = text.replace(word.title(), word[0].upper() + '*' * (len(word) - 1))

    return text