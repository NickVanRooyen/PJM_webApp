class SigmaAdMan(admin.ModelAdmin):
exclude = ('category',)

def save_model(self, request, obj, form, change):
    obj.category = 2
    obj.save()