from django.contrib import admin

from ella.ratings.models import Rating, TotalRate, ModelWeight

class RatingOptions(admin.ModelAdmin):
    list_filter = ('time', 'target_ct',)
    list_display = ('__unicode__', 'time', 'amount', 'user',)

class TotalRateOptions(admin.ModelAdmin):
    list_filter = ('target_ct',)
    list_display = ('__unicode__', 'amount')

class ModelWeightOptions(admin.ModelAdmin):
    list_filter = ('content_type',)
    list_display = ('content_type', 'weight', 'owner_field',)

admin.site.register(Rating, RatingOptions)
admin.site.register(TotalRate, TotalRateOptions)
admin.site.register(ModelWeight, ModelWeightOptions)



