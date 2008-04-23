from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


class TopicThreadManager(models.Manager):
    def get_most_filled(self):
        from ella.discussions.models import TopicThread
        ct_thread = ContentType.objects.get_for_model(TopicThread)
        subquery="""
        (
        SELECT
            COUNT(id) AS comment_count,
            target_id
        FROM
            comments_comment
        WHERE
            target_ct_id = %d
        GROUP BY
            target_id
) AS _rate
        """ % ct_thread._get_pk_val()
        cond = 'discussions_topicthread.id = _rate.target_id'
        return TopicThread.objects.all().extra(
            select={'cnt': '_rate.comment_count'},
            tables=[subquery],
            where=[cond]
).order_by('-cnt')


    def get_most_viewed(self):
        from ella.discussions.models import TopicThread
        ct_thread = ContentType.objects.get_for_model(TopicThread)
        subquery="""
        (
        SELECT
            hits,
            target_id
        FROM
            core_hitcount
        WHERE
            target_ct_id = %d
) AS _hitcount
        """ % ct_thread._get_pk_val()
        cond = 'discussions_topicthread.id = _hitcount.target_id'
        return TopicThread.objects.all().extra(
            select={'cnt': '_hitcount.hits'},
            tables=[subquery],
            where=[cond]
).order_by('-cnt')


    def get_with_newest_posts(self):
        from ella.discussions.models import TopicThread
        ct_thread = ContentType.objects.get_for_model(TopicThread)
        subquery="""
        (
        SELECT
            target_id
        FROM
            comments_comment
        WHERE
            target_ct_id = %d
        GROUP BY
            target_id
        ORDER BY
            submit_date DESC
) AS _res
        """ % ct_thread._get_pk_val()
        cond = 'discussions_topicthread.id = _res.target_id'
        return TopicThread.objects.all().extra(
            tables=[subquery],
            where=[cond]
)
