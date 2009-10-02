from ella import newman
from ella.ratings.models import Rating, TotalRate, ModelWeight

class RatingOptions(newman.NewmanModelAdmin):
    list_filter = ('time', 'target_ct',)
    list_display = ('__unicode__', 'time', 'amount', 'user',)

class TotalRateOptions(newman.NewmanModelAdmin):
    list_filter = ('target_ct',)
    list_display = ('__unicode__', 'amount')

class ModelWeightOptions(newman.NewmanModelAdmin):
    list_filter = ('content_type',)
    list_display = ('content_type', 'weight', 'owner_field',)

newman.site.register(Rating, RatingOptions)
newman.site.register(TotalRate, TotalRateOptions)
newman.site.register(ModelWeight, ModelWeightOptions)


