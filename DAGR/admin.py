from django.contrib import admin


from DAGR.models import *
# Register your models here.

admin.site.register(DAGR)
admin.site.register(Relationship)
admin.site.register(Webpage)
admin.site.register(Word_Document)
admin.site.register(Keyword)
admin.site.register(Image)
admin.site.register(Audio)
admin.site.register(Video)
admin.site.register(Tweet)