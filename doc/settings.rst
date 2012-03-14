.. _settings:

List of configuration settings
##############################

Core settings
*************

**CACHE_TIMEOUT**
    Timeout used for cache persistence for most of cached function Ella uses.
    
    Default: ``600``
    
**CACHE_TIMEOUT_LONG**
    Chache persistence timeout for rarely-changing results.
    
    Default: ``3600``
    
**CATEGORY_LISTINGS_PAGINATE_BY**
    Number of **objects per page** when browsing the **category listing**.
    
    Default: ``20``
    
**RSS_NUM_IN_FEED**
    Number of **items** in automated category RSS/Atom feeds.
    
    Default: ``10``
    
**RSS_ENCLOSURE_PHOTO_FORMAT**
    Photo format to use when providing photo link in RSS/Atom feed ``<enclosure>``
    element.
    
    Default: ``None``
    
**DOUBLE_RENDER**
    Boolean that switches the **Double render function**, for more details on Double
    rendering, see :ref:`features-double-render`.
    
    Default: ``False``
    
**DOUBLE_RENDER_EXCLUDE_URLS**
    URLs to be excluded from double rendering. For details, see
    :ref:`features-double-render`.        
    
    Default: ``None``                                       

**RELATED_FINDERS**
    List of named related finders. For instructions how to use it, see
    :ref:`features-related`.
    
    Default::
    
        RELATED_FINDERS = {
            'default': (
                'ella.core.related_finders.directly_related',
                'ella.core.related_finders.related_by_category',
            ),
            'directly': (
                'ella.core.related_finders.directly_related',
            )
        }
        
Photos settings
***************
**PHOTOS_FORMAT_QUALITY_DEFAULT**
    Sampling quality choices to use in administration when defining
    :func:`photo formats <ella.photos.models.Format>`.
    
    Default::
    
        PHOTOS_FORMAT_QUALITY = (
            (45, _('Low')),
            (65, _('Medium')),
            (75, _('Good')),
            (85, _('Better')),
            (95, _('High')),
        )
        
**PHOTOS_CUSTOM_SUBDIR**
    Custom subdirectory in ``photos`` directory where to place the photos.
    
    Default: ``''``
    
**PHOTOS_UPLOAD_TO**
    Completely override where the photos are uploaded to. Symbols ``%Y``,
    ``%m`` and ``%d`` are replaced by integer value of year, month and day
    respectively.
    
    Default: ``'photos/%Y/%m/%d'``
        
