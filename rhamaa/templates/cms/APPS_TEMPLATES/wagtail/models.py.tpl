from django.db import models
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.search import index

from utils.models import BasePage


# Create your models here.

class ExamplePage(BasePage):
    """Example page model for demonstration."""

    introduction = models.TextField(
        help_text='Text to describe the page',
        blank=True
    )

    body = RichTextField(
        verbose_name="Page body",
        blank=True
    )

    content_panels = BasePage.content_panels + [
        FieldPanel('introduction'),
        FieldPanel('body'),
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField('introduction'),
        index.SearchField('body'),
    ]

    class Meta:
        verbose_name = "Example Page"
        verbose_name_plural = "Example Pages"
