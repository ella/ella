from django.db import models, connection
from django.contrib.contenttypes.models import ContentType
from ella.oldcomments.models import Comment


class TopicThreadManager(models.Manager):

    def get_most_filled(self):
        ct_thread = ContentType.objects.get_for_model(self.model)
        subquery="""
        (
        SELECT
            COUNT(*) AS comment_count,
            target_id
        FROM
            comments_comment
        WHERE
            target_ct_id = %d
        GROUP BY
        target_id
        ) AS _rate""" % ct_thread._get_pk_val()
        cond = 'discussions_topicthread.id = _rate.target_id'
        return self.model.objects.extra(
            select={'cnt': '_rate.comment_count'},
            tables=[subquery],
            where=[cond]
        ).order_by('-cnt')

    def get_most_viewed(self):
        """ returns queryset of most viewed TopicThread instances. """
        return self.model.objects.order_by('-hit_counts')

    def get_with_newest_posts(self):
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
        ) AS _rslt
        """ % ct_thread._get_pk_val()
        cond = 'discussions_topicthread.id = _rslt.target_id'
        return self.model.objects.extra(
            tables=[subquery],
            where=[cond]
        )

    def get_unread_posts(self, user):
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

    def get_unread_topicthreads(self, user):
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

    def get_unread_topics(self, user):
        pass
