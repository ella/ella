
# tohle mazat z ostreho dumpu pred vysosanim dat

# pozor na id 2347 (slug misa je tam triplicita)
update core_author a, core_author b set a.slug = concat(a.slug, '_') where a.slug = b.slug and a.id < b.id;
update core_author a, core_author b set a.slug = concat(a.slug, '_') where a.slug = b.slug and a.id < b.id;

# uz neni
drop table core_dependency;

# pk je neco jineho
alter table core_hitcount drop column id;

# tohle delal honza, neni pro to model
drop table discussions_question;

# tahle appka se nepouziva
drop table `discussions_bannedstring`;
drop table `discussions_banneduser`;
drop table `discussions_postviewed`;
drop table `discussions_topicthread`;
drop table `discussions_topic`;

# nepouzivame
drop table ellaadmin_categoryuserrole;
drop table ellaadmin_siteuserrole;

# nepouzivame
drop table encoder_formattedfile;
drop table encoder_format;

# neni
drop table media_format;
drop table menu_menu;
drop table menu_menuitem;

drop table uploader_upload;

# zase duplicity
# select id from polls_contestant group by contest_id, email having count(*) > 1;
update polls_contestant set email = concat('_', email) where id in (2004, 23045,62003, 72669, 78587, 75993, 78391, 67271);

