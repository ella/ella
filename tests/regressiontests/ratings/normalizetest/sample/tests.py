test_normalize = r'''
>>> from decimal import Decimal
>>> from ella.ratings.models import *
>>>
>>> from sample.models import SampleModel
>>>
>>> for i in range(-5, 11):
...
...     s = SampleModel(r=i)
...     s.save()
>>>
>>> TotalRate.objects.get_normalized_rating(SampleModel.objects.get(r=10), 2, Decimal("0.5"))
Decimal("0.0")
>>>
>>> for i in range(-5, 11):
...     s = SampleModel.objects.get(r=i)
...     r = TotalRate(target=s, amount=i)
...     r.save()
>>>
>>> TotalRate.objects.get_normalized_rating(SampleModel.objects.get(r=-5), 2, Decimal("0.5"))
Decimal("-2.0")
>>> TotalRate.objects.get_normalized_rating(SampleModel.objects.get(r=0), 2, Decimal("0.5"))
Decimal("0.0")
>>> TotalRate.objects.get_normalized_rating(SampleModel.objects.get(r=5), 2, Decimal("0.5"))
Decimal("1.0")
>>> TotalRate.objects.get_normalized_rating(SampleModel.objects.get(r=7), 2, Decimal("0.5"))
Decimal("1.5")
>>> TotalRate.objects.get_normalized_rating(SampleModel.objects.get(r=9), 2, Decimal("0.5"))
Decimal("2.0")
>>> TotalRate.objects.get_normalized_rating(SampleModel.objects.get(r=10), 2, Decimal("0.5"))
Decimal("2.0")
'''


__test__ = {
    'test_normalize': test_normalize,
}



if __name__ == '__main__':
    import doctest
    doctest.testmod()

