from django.contrib.auth.models import User, AnonymousUser, Permission, Group
from django.core.management import call_command
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

from djangosanetesting  import cases

from ella.newman.models import CategoryUserRole, DenormalizedCategoryUserRole, has_model_list_permission
from ella.newman.models import has_category_permission, has_object_permission, cat_children, compute_applicable_categories
from ella.newman.models import applicable_categories, permission_filtered_model_qs, is_category_fk, model_category_fk_value
from ella.newman.models import model_category_fk
from ella.core.models import Category


class TestGetPage(cases.DatabaseTestCase):
    def setUp(self):
        super(TestGetPage, self).setUp()
        #call_command('syncroles', verbosity=0, notransaction=True)

    def test__applicable_categories__for_user(self):
        user = User.objects.get(username='newman')
        ap_cat = compute_applicable_categories(user)
        ap_cat.sort()
        cats = [317, 25, 339, 329, 341, 327, 321, 325, 331, 323, 451, 455, 449, 450, 459, 
            453, 448, 456, 457, 454, 452, 458, 347, 346, 351, 352, 353, 345, 344, 349, 350, 348,
            391, 394, 395, 389, 439, 396, 393, 388, 387, 390, 392, 373, 376, 379, 377, 369, 368, 
            374, 375, 385, 386, 383, 382, 378, 384, 380, 442, 371, 370, 372, 443, 381, 422, 424, 
            423, 427, 426, 425, 419, 421, 420, 444, 429, 428, 430, 431, 432, 433, 447, 436, 440, 
            435, 437, 434, 446, 445, 365, 441, 363, 366, 364, 367, 362, 361, 359, 356, 358, 438, 
            355, 360, 354, 357, 401, 405, 402, 406, 407, 403, 404, 409, 414, 410, 415, 416, 412, 
            417, 411, 413, 418, 408, 400, 397, 399, 38, 99, 91, 333, 153, 34, 89, 183, 100, 39, 
            37, 102, 101, 48, 29, 103, 72, 31, 143, 144, 167, 90, 175, 106, 147, 104, 161, 105, 
            107, 171, 142, 165, 163, 117, 113, 110, 112, 111, 114, 179, 118, 149, 119, 120, 121, 
            122, 148, 123, 170, 191, 193, 195, 197]
        cats.sort()
        self.assert_equals( ap_cat , cats )

    def test__applicable_categories__for_user_permission(self):
        user = User.objects.get(username='newman')
        ap_cat = compute_applicable_categories(user, 'articles.view_article')
        ap_cat.sort()
        cats = [317, 25, 339, 329, 341, 327, 321, 325, 331, 323, 451, 455, 449, 450, 459, 
            453, 448, 456, 457, 454, 452, 458, 347, 346, 351, 352, 353, 345, 344, 349, 350, 348,
            391, 394, 395, 389, 439, 396, 393, 388, 387, 390, 392, 373, 376, 379, 377, 369, 368, 
            374, 375, 385, 386, 383, 382, 378, 384, 380, 442, 371, 370, 372, 443, 381, 422, 424, 
            423, 427, 426, 425, 419, 421, 420, 444, 429, 428, 430, 431, 432, 433, 447, 436, 440, 
            435, 437, 434, 446, 445, 365, 441, 363, 366, 364, 367, 362, 361, 359, 356, 358, 438, 
            355, 360, 354, 357, 401, 405, 402, 406, 407, 403, 404, 409, 414, 410, 415, 416, 412, 
            417, 411, 413, 418, 408, 400, 397, 399, 38, 99, 91, 333, 153, 34, 89, 183, 100, 39, 
            37, 102, 101, 48, 29, 103, 72, 31, 143, 144, 167, 90, 175, 106, 147, 104, 161, 105, 
            107, 171, 142, 165, 163, 117, 113, 110, 112, 111, 114, 179, 118, 149, 119, 120, 121, 
            122, 148, 123, 170, 191, 193, 195, 197]
        cats.sort()
        self.assert_equals( ap_cat , cats )
