
-- tohle mazat z ostreho dumpu pred vysosanim dat

-- pozor na id 2347 (slug misa je tam triplicita)
update core_author a, core_author b set a.slug = concat(a.slug, '_') where a.slug = b.slug and a.id < b.id;
update core_author a, core_author b set a.slug = concat(a.slug, '_') where a.slug = b.slug and a.id < b.id;

-- uz neni
drop table core_dependency;

-- pk je neco jineho
alter table core_hitcount drop column id;

-- nepouzivame
drop table ellaadmin_categoryuserrole;
drop table ellaadmin_siteuserrole;

-- nepouzivame
drop table encoder_formattedfile;
drop table encoder_format;
drop table uploader_upload;

-- asi stara tabulka
drop table media_format;

-- nepouzivame
drop table menu_menuitem;
drop table menu_menu;


-- tohle delal honza, neni pro to model
drop table discussions_question;
-- tahle appka se nepouziva - haha! chyba lavky ;)
drop table `discussions_bannedstring`;
drop table `discussions_banneduser`;
drop table `discussions_postviewed`;
drop table `discussions_topicthread`;
drop table `discussions_topic`;


-- zase duplicity
-- select id from polls_contestant group by contest_id, email having count(*) > 1;
-- pry by sla pouzit promenna, neco ve smyslu:
-- set @xx = (select group_concat(x) from (select target_ct_id as x from comments_comment group by target_id having count(*) > 1) as a);
update polls_contestant set email = concat('_', email) where id in (2004, 23045,62003, 72669, 78587, 75993, 78391, 67271);

-- nektere galerie nemaji kategorie
-- select id from galleries_gallery where category_id is null;
-- select id, slug from core_category where slug like '%archiv%';
update galleries_gallery set category_id = 38 where category_id is null;

-- nektere listingy maji referenci na neexistujici objekt
-- pro upravu je treba pridat kaskadni mazani kvuli konstrejnam na listingu a hitkauntech
-- alter table core_listing drop foreign key placement_id_refs_id_7c52840e;
alter table core_listing add CONSTRAINT placement_id_refs_id_7c52840e FOREIGN KEY (`placement_id`) REFERENCES `core_placement` (`id`) on delete cascade on update cascade;
-- alter table core_hitcount drop foreign key placement_id_refs_id_7d42d973;
alter table core_hitcount add constraint `placement_id_refs_id_7d42d973` FOREIGN KEY (`placement_id`) REFERENCES `core_placement` (`id`) on delete cascade on update cascade;

-- nalezeni a odstraneni spatnych placementu
-- articles:
-- select p.id, p.target_id from core_placement p where p.target_ct_id = 16 and not exists (select id from articles_article where id = p.target_id);
delete from core_placement where target_id in (750519, 750521) and target_ct_id = 16;
-- quizes:
-- select p.id, p.target_id from core_placement p where p.target_ct_id = 32 and not exists (select id from polls_quiz where id = p.target_id);
delete from core_placement where target_id in (7974) and target_ct_id = 32;
-- interviews:
-- select p.id, p.target_id from core_placement p where p.target_ct_id = 55 and not exists (select id from interviews_interview where id = p.target_id);
delete from core_placement where target_id in (68) and target_ct_id = 55;
-- fotky
-- select photo_id from articles_article where photo_id not in (select id from photos_photo);
update articles_article set photo_id = null where id in (485283);


-- a pak uz jenom
-- $ mysqldump -t -c jmeno_databaze
-- coz udela dump pouze dat a v definovanem poradi

