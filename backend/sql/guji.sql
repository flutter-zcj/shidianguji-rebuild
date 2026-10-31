-- ----------------------------------------------------------------------------
-- 识典古籍重建 - 古籍阅读平台业务表（guji_*）
-- 数据库：ruoyi-fastapi（与 RuoYi 系统表同库）
-- 说明：示例数据取自公版古典文献（论语/道德经/三字经/千字文/诗经/孟子）
-- ----------------------------------------------------------------------------

-- 1、古籍书目表
drop table if exists guji_book;
create table guji_book (
  book_id           bigint(20)      not null auto_increment    comment '书目ID',
  book_name         varchar(100)    not null                   comment '书名',
  author            varchar(50)     default ''                 comment '作者',
  dynasty           varchar(20)     default ''                 comment '朝代',
  category          varchar(20)     default ''                 comment '分类（经/史/子/集/蒙学）',
  intro             varchar(1000)   default ''                 comment '内容简介',
  cover             varchar(255)    default ''                 comment '封面图URL',
  chapter_count     int(11)         default 0                  comment '章节数',
  status            char(1)         default '0'                comment '状态（0上架 1下架）',
  del_flag          char(1)         default '0'                comment '删除标志（0代表存在 2代表删除）',
  create_by         varchar(64)     default ''                 comment '创建者',
  create_time       datetime(3)                                comment '创建时间',
  update_by         varchar(64)     default ''                 comment '更新者',
  update_time       datetime(3)                                comment '更新时间',
  primary key (book_id),
  key idx_book_category (category),
  key idx_book_dynasty (dynasty)
) engine=innodb auto_increment=100 comment = '古籍书目表';

-- 2、章节表
drop table if exists guji_chapter;
create table guji_chapter (
  chapter_id        bigint(20)      not null auto_increment    comment '章节ID',
  book_id           bigint(20)      not null                   comment '所属书目ID',
  chapter_no        int(11)         default 0                  comment '章节序号',
  chapter_name      varchar(100)    default ''                 comment '章节标题',
  paragraph_count   int(11)         default 0                  comment '段落数',
  create_time       datetime(3)                                comment '创建时间',
  update_time       datetime(3)                                comment '更新时间',
  primary key (chapter_id),
  key idx_chapter_book (book_id)
) engine=innodb auto_increment=1000 comment = '古籍章节表';

-- 3、段落表
drop table if exists guji_paragraph;
create table guji_paragraph (
  paragraph_id      bigint(20)      not null auto_increment    comment '段落ID',
  chapter_id        bigint(20)      not null                   comment '所属章节ID',
  book_id           bigint(20)      not null                   comment '所属书目ID',
  para_seq          int(11)         default 0                  comment '段落序号',
  para_text         text                                      comment '段落文本',
  primary key (paragraph_id),
  key idx_para_chapter (chapter_id),
  key idx_para_book (book_id)
) engine=innodb auto_increment=100000 comment = '古籍段落表';

-- 4、书架表
drop table if exists guji_bookshelf;
create table guji_bookshelf (
  shelf_id          bigint(20)      not null auto_increment    comment '书架ID',
  user_id           bigint(20)      not null                   comment '用户ID',
  book_id           bigint(20)      not null                   comment '书目ID',
  last_chapter_id   bigint(20)      default 0                  comment '最后阅读章节ID',
  last_paragraph_id bigint(20)      default 0                  comment '最后阅读段落ID',
  create_time       datetime(3)                                comment '收藏时间',
  update_time       datetime(3)                                comment '更新时间',
  primary key (shelf_id),
  unique key uk_shelf_user_book (user_id, book_id),
  key idx_shelf_user (user_id)
) engine=innodb auto_increment=10000 comment = '古籍书架表';

-- 5、阅读历史表
drop table if exists guji_read_history;
create table guji_read_history (
  history_id        bigint(20)      not null auto_increment    comment '历史ID',
  user_id           bigint(20)      not null                   comment '用户ID',
  book_id           bigint(20)      not null                   comment '书目ID',
  chapter_id        bigint(20)      default 0                  comment '章节ID',
  paragraph_id      bigint(20)      default 0                  comment '段落ID',
  read_time         datetime(3)                                comment '阅读时间',
  primary key (history_id),
  key idx_history_user (user_id),
  key idx_history_user_time (user_id, read_time)
) engine=innodb auto_increment=100000 comment = '古籍阅读历史表';

-- 6、听书音频表
drop table if exists guji_audio;
create table guji_audio (
  audio_id          bigint(20)      not null auto_increment    comment '音频ID',
  book_id           bigint(20)      not null                   comment '书目ID',
  chapter_id        bigint(20)      default 0                  comment '章节ID（0为全书音频）',
  audio_name        varchar(100)    default ''                 comment '音频名称',
  audio_url         varchar(255)    default ''                 comment '音频地址',
  duration_sec      int(11)         default 0                  comment '时长（秒）',
  create_time       datetime(3)                                comment '创建时间',
  primary key (audio_id),
  key idx_audio_book (book_id)
) engine=innodb auto_increment=1000 comment = '古籍听书音频表';

-- ----------------------------------------------------------------------------
-- 初始化数据
-- ----------------------------------------------------------------------------
insert into guji_book(book_id, book_name, author, dynasty, category, intro, chapter_count, status, del_flag, create_by, create_time)
values
(100, '论语', '孔子及弟子', '春秋', '经', '儒家经典，记载孔子及其弟子言行，共二十篇，是儒家思想的核心典籍。', 2, '0', '0', 'admin', sysdate()),
(101, '道德经', '老子', '春秋', '子', '道家开山之作，又称《老子》，全书五千余言，分上下两篇共八十一章，讲道与德的哲学体系。', 10, '0', '0', 'admin', sysdate()),
(102, '三字经', '王应麟', '宋', '蒙学', '中国传统蒙学三大读物之一，三字一句朗朗上口，涵盖历史、伦理、常识等启蒙内容。', 2, '0', '0', 'admin', sysdate()),
(103, '千字文', '周兴嗣', '南北朝', '蒙学', '由一千个不重复汉字组成的四言韵文，历代用于儿童识字启蒙的经典教材。', 2, '0', '0', 'admin', sysdate()),
(104, '诗经', '佚名（孔子删定）', '先秦', '经', '中国第一部诗歌总集，收录西周初年至春秋中叶诗歌三百零五篇，分风、雅、颂三部分。', 2, '0', '0', 'admin', sysdate()),
(105, '孟子', '孟轲', '战国', '经', '儒家经典之一，记录孟子及其弟子言行的语录体著作，共七篇，主张性善论与仁政。', 1, '0', '0', 'admin', sysdate());

-- 论语章节
insert into guji_chapter(chapter_id, book_id, chapter_no, chapter_name, paragraph_count, create_time)
values
(1000, 100, 1, '学而篇', 6, sysdate()),
(1001, 100, 2, '为政篇', 4, sysdate());

-- 论语段落
insert into guji_paragraph(paragraph_id, chapter_id, book_id, para_seq, para_text)
values
(100000, 1000, 100, 1, '子曰：“学而时习之，不亦说乎？有朋自远方来，不亦乐乎？人不知而不愠，不亦君子乎？”'),
(100001, 1000, 100, 2, '有子曰：“其为人也孝弟，而好犯上者，鲜矣；不好犯上，而好作乱者，未之有也。君子务本，本立而道生。孝弟也者，其为仁之本与！”'),
(100002, 1000, 100, 3, '子曰：“巧言令色，鲜矣仁！”'),
(100003, 1000, 100, 4, '曾子曰：“吾日三省吾身：为人谋而不忠乎？与朋友交而不信乎？传不习乎？”'),
(100004, 1000, 100, 5, '子曰：“道千乘之国，敬事而信，节用而爱人，使民以时。”'),
(100005, 1000, 100, 6, '子曰：“弟子入则孝，出则弟，谨而信，泛爱众，而亲仁。行有余力，则以学文。”'),
(100006, 1001, 100, 1, '子曰：“为政以德，譬如北辰，居其所而众星共之。”'),
(100007, 1001, 100, 2, '子曰：“《诗》三百，一言以蔽之，曰：‘思无邪。’”'),
(100008, 1001, 100, 3, '子曰：“道之以政，齐之以刑，民免而无耻；道之以德，齐之以礼，有耻且格。”'),
(100009, 1001, 100, 4, '子曰：“吾十有五而志于学，三十而立，四十而不惑，五十而知天命，六十而耳顺，七十而从心所欲，不逾矩。”');

-- 道德经章节（前十章）
insert into guji_chapter(chapter_id, book_id, chapter_no, chapter_name, paragraph_count, create_time)
values
(1010, 101, 1, '第一章', 1, sysdate()), (1011, 101, 2, '第二章', 1, sysdate()),
(1012, 101, 3, '第三章', 1, sysdate()), (1013, 101, 4, '第四章', 1, sysdate()),
(1014, 101, 5, '第五章', 1, sysdate()), (1015, 101, 6, '第六章', 1, sysdate()),
(1016, 101, 7, '第七章', 1, sysdate()), (1017, 101, 8, '第八章', 1, sysdate()),
(1018, 101, 9, '第九章', 1, sysdate()), (1019, 101, 10, '第十章', 1, sysdate());

insert into guji_paragraph(paragraph_id, chapter_id, book_id, para_seq, para_text)
values
(100010, 1010, 101, 1, '道可道，非常道；名可名，非常名。无名，天地之始；有名，万物之母。故常无欲，以观其妙；常有欲，以观其徼。此两者同出而异名，同谓之玄。玄之又玄，众妙之门。'),
(100011, 1011, 101, 1, '天下皆知美之为美，斯恶已；皆知善之为善，斯不善已。故有无相生，难易相成，长短相较，高下相倾，音声相和，前后相随。是以圣人处无为之事，行不言之教，万物作焉而不辞，生而不有，为而不恃，功成而弗居。夫唯弗居，是以不去。'),
(100012, 1012, 101, 1, '不尚贤，使民不争；不贵难得之货，使民不为盗；不见可欲，使民心不乱。是以圣人之治，虚其心，实其腹，弱其志，强其骨，常使民无知无欲。使夫智者不敢为也。为无为，则无不治。'),
(100013, 1013, 101, 1, '道冲，而用之或不盈。渊兮，似万物之宗。挫其锐，解其纷，和其光，同其尘。湛兮，似或存。吾不知谁之子，象帝之先。'),
(100014, 1014, 101, 1, '天地不仁，以万物为刍狗；圣人不仁，以百姓为刍狗。天地之间，其犹橐籥乎？虚而不屈，动而愈出。多言数穷，不如守中。'),
(100015, 1015, 101, 1, '谷神不死，是谓玄牝。玄牝之门，是谓天地根。绵绵若存，用之不勤。'),
(100016, 1016, 101, 1, '天长地久。天地所以能长且久者，以其不自生，故能长生。是以圣人后其身而身先，外其身而身存。非以其无私邪？故能成其私。'),
(100017, 1017, 101, 1, '上善若水。水善利万物而不争，处众人之所恶，故几于道。居善地，心善渊，与善仁，言善信，政善治，事善能，动善时。夫唯不争，故无尤。'),
(100018, 1018, 101, 1, '持而盈之，不如其已；揣而锐之，不可长保。金玉满堂，莫之能守；富贵而骄，自遗其咎。功遂身退，天之道也。'),
(100019, 1019, 101, 1, '载营魄抱一，能无离乎？专气致柔，能如婴儿乎？涤除玄览，能无疵乎？爱民治国，能无为乎？天门开阖，能为雌乎？明白四达，能无知乎？生之畜之，生而不有，为而不恃，长而不宰，是谓玄德。');

-- 三字经章节
insert into guji_chapter(chapter_id, book_id, chapter_no, chapter_name, paragraph_count, create_time)
values
(1020, 102, 1, '开篇·教之道', 4, sysdate()),
(1021, 102, 2, '勤学篇', 2, sysdate());

insert into guji_paragraph(paragraph_id, chapter_id, book_id, para_seq, para_text)
values
(100020, 1020, 102, 1, '人之初，性本善。性相近，习相远。苟不教，性乃迁。教之道，贵以专。'),
(100021, 1020, 102, 2, '昔孟母，择邻处。子不学，断机杼。窦燕山，有义方。教五子，名俱扬。'),
(100022, 1020, 102, 3, '养不教，父之过。教不严，师之惰。子不学，非所宜。幼不学，老何为。'),
(100023, 1020, 102, 4, '玉不琢，不成器。人不学，不知义。为人子，方少时。亲师友，习礼仪。'),
(100024, 1021, 102, 1, '香九龄，能温席。孝于亲，所当执。融四岁，能让梨。弟于长，宜先知。'),
(100025, 1021, 102, 2, '首孝弟，次见闻。知某数，识某文。一而十，十而百。百而千，千而万。');

-- 千字文章节
insert into guji_chapter(chapter_id, book_id, chapter_no, chapter_name, paragraph_count, create_time)
values
(1030, 103, 1, '天文地理', 2, sysdate()),
(1031, 103, 2, '人文历史', 2, sysdate());

insert into guji_paragraph(paragraph_id, chapter_id, book_id, para_seq, para_text)
values
(100030, 1030, 103, 1, '天地玄黄，宇宙洪荒。日月盈昃，辰宿列张。寒来暑往，秋收冬藏。闰余成岁，律吕调阳。'),
(100031, 1030, 103, 2, '云腾致雨，露结为霜。金生丽水，玉出昆冈。剑号巨阙，珠称夜光。果珍李柰，菜重芥姜。海咸河淡，鳞潜羽翔。龙师火帝，鸟官人皇。'),
(100032, 1031, 103, 1, '始制文字，乃服衣裳。推位让国，有虞陶唐。吊民伐罪，周发殷汤。坐朝问道，垂拱平章。'),
(100033, 1031, 103, 2, '爱育黎首，臣伏戎羌。遐迩一体，率宾归王。鸣凤在竹，白驹食场。化被草木，赖及万方。');

-- 诗经章节
insert into guji_chapter(chapter_id, book_id, chapter_no, chapter_name, paragraph_count, create_time)
values
(1040, 104, 1, '周南·关雎', 3, sysdate()),
(1041, 104, 2, '秦风·蒹葭', 3, sysdate());

insert into guji_paragraph(paragraph_id, chapter_id, book_id, para_seq, para_text)
values
(100040, 1040, 104, 1, '关关雎鸠，在河之洲。窈窕淑女，君子好逑。'),
(100041, 1040, 104, 2, '参差荇菜，左右流之。窈窕淑女，寤寐求之。求之不得，寤寐思服。悠哉悠哉，辗转反侧。'),
(100042, 1040, 104, 3, '参差荇菜，左右采之。窈窕淑女，琴瑟友之。参差荇菜，左右芼之。窈窕淑女，钟鼓乐之。'),
(100043, 1041, 104, 1, '蒹葭苍苍，白露为霜。所谓伊人，在水一方。溯洄从之，道阻且长。溯游从之，宛在水中央。'),
(100044, 1041, 104, 2, '蒹葭萋萋，白露未晞。所谓伊人，在水之湄。溯洄从之，道阻且跻。溯游从之，宛在水中坻。'),
(100045, 1041, 104, 3, '蒹葭采采，白露未已。所谓伊人，在水之涘。溯洄从之，道阻且右。溯游从之，宛在水中沚。');

-- 孟子章节
insert into guji_chapter(chapter_id, book_id, chapter_no, chapter_name, paragraph_count, create_time)
values
(1050, 105, 1, '梁惠王章句上', 2, sysdate());

insert into guji_paragraph(paragraph_id, chapter_id, book_id, para_seq, para_text)
values
(100050, 1050, 105, 1, '孟子见梁惠王。王曰：“叟！不远千里而来，亦将有以利吾国乎？”孟子对曰：“王何必曰利？亦有仁义而已矣。王曰‘何以利吾国’，大夫曰‘何以利吾家’，士庶人曰‘何以利吾身’，上下交征利而国危矣。”'),
(100051, 1050, 105, 2, '“未有仁而遗其亲者也，未有义而后其君者也。王亦曰仁义而已矣，何必曰利？”');

-- 听书音频示例数据
insert into guji_audio(audio_id, book_id, chapter_id, audio_name, audio_url, duration_sec, create_time)
values
(1000, 100, 1000, '学而篇 有声书', 'https://example.com/audio/lunyu_xueer.mp3', 360, sysdate()),
(1001, 100, 1001, '为政篇 有声书', 'https://example.com/audio/lunyu_weizheng.mp3', 300, sysdate()),
(1002, 101, 1010, '道德经 第一章', 'https://example.com/audio/daodejing_01.mp3', 90, sysdate()),
(1003, 101, 1011, '道德经 第二章', 'https://example.com/audio/daodejing_02.mp3', 120, sysdate()),
(1004, 104, 1040, '关雎 诵读', 'https://example.com/audio/shijing_guanju.mp3', 180, sysdate());
