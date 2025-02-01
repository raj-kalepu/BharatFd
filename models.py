from django.db import models
from ckeditor.fields import RichTextField
from django.core.cache import cache
from googletrans import Translator

translator = Translator()

class FAQ(models.Model):
    question = models.TextField()
    answer = RichTextField()
    # Auto-translated fields (extend as needed)
    question_hi = models.TextField(blank=True, null=True)
    question_bn = models.TextField(blank=True, null=True)
    answer_hi = RichTextField(blank=True, null=True)
    answer_bn = RichTextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Auto-translate missing fields using googletrans with fallback to English.
        for lang, field in (('hi', 'question_hi'), ('bn', 'question_bn')):
            if not getattr(self, field):
                try:
                    setattr(self, field, translator.translate(self.question, dest=lang).text)
                except Exception:
                    setattr(self, field, self.question)
        for lang, field in (('hi', 'answer_hi'), ('bn', 'answer_bn')):
            if not getattr(self, field):
                try:
                    setattr(self, field, translator.translate(self.answer, dest=lang).text)
                except Exception:
                    setattr(self, field, self.answer)
        super().save(*args, **kwargs)

    def get_translation(self, field, lang='en'):
        cache_key = f"faq_{self.id}_{field}_{lang}"
        translation = cache.get(cache_key)
        if translation:
            return translation
        if lang == 'en':
            translation = getattr(self, field)
        else:
            translation = getattr(self, f"{field}_{lang}", None) or getattr(self, field)
        cache.set(cache_key, translation, timeout=3600)
        return translation

    def __str__(self):
        return self.question
