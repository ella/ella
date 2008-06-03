from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from ella.comments.models import Comment


class MostFilledManager(models.Manager):

    def get_query_set(self):
        ct_thread = ContentType.objects.get_for_model(self.model)
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
        return self.model.objects.extra(
            select={'cnt': '_rate.comment_count'},
            tables=[subquery],
            where=[cond]
).order_by('-cnt')


class MostViewedManager(models.Manager):

    def get_query_set(self):
        ct_thread = ContentType.objects.get_for_model(self.model)
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
        return self.model.objects.extra(
            select={'cnt': '_hitcount.hits'},
            tables=[subquery],
            where=[cond]
).order_by('-cnt')

class WithNewestPostsManager(models.Manager):

    def get_query_set(self):
        ct_thread = ContentType.objects.get_for_model(self.model)
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
        return self.model.objects.extra(
            tables=[subquery],
            where=[cond]
)

class UnreadItemsManager(models.Manager):

    def get_posts(self, user):
        CT = ContentType.objects.get_for_model(self.model)
        qset = Comment.objects.filter(target_ct=CT).extra(
            tables=[ '''
                comments_comment AS cmt
                LEFT JOIN
                    (
                        SELECT
                            id, target_id, user_id
                        FROM
                            discussions_postviewed
                        WHERE
                            user_id = %d
) AS dpv
                ON
                    dpv.target_id = cmt.id
            ''' % user._get_pk_val() ],
            where=['dpv.id IS NULL', 'comments_comment.id = cmt.id']
)
        return qset

    def get_topicthreads(self, user):
        CT = ContentType.objects.get_for_model(self.model)
        cur = connection.cursor()
        sql = '''
            SELECT
                comments_comment.target_id,
                COUNT(comments_comment.target_id)
            FROM
                comments_comment
              LEFT JOIN
                (
                    SELECT
                        id, target_id, user_id
                    FROM
                        discussions_postviewed
                    WHERE
                        user_id = %d
) AS pw
              ON
                pw.target_id = comments_comment.id
            WHERE
                pw.id IS NULL
                AND
                comments_comment.target_ct_id = %d
            GROUP BY
                comments_comment.target_id
            ''' % (user._get_pk_val(), CT._get_pk_val())
        cur.execute(sql)
        data = cur.fetchall()
        if not data:
            return []
        thread_ids = map(lambda x: x[0], data)
        unread_count = map(lambda x: x[1], data)
        out = self.model.objects.filter(pk__in=thread_ids)
        for i, item in enumerate(out):
            setattr(item, 'unread_post_count', unread_count[i])
        return out

    def get_topics(self, user):
        pass
