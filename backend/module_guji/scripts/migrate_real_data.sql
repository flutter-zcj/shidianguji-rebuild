-- 识典古籍：把既有古籍库（gj_*）的真实数据迁移到 module_guji 的 guji_* 表
--
-- 前置：目标表已由 python -m module_guji.scripts.migrate_real_data 建好
-- 源表：gj_category(5) / gj_book(244) / gj_chapter(4339)
--
-- 约定：
-- 1. 主键沿用源表 id，保证 book/chapter 对应关系可直接 JOIN；迁移完成后会 setval 修正序列
-- 2. 四部分类由「经部/史部/子部/集部」归一化为「经/史/子/集」
-- 3. 章节正文按换行切分为段落，空行丢弃

BEGIN;

-- ------------------------------ 清理（幂等重跑） ------------------------------
DELETE FROM guji_paragraph;
DELETE FROM guji_chapter;
DELETE FROM guji_volume;
DELETE FROM guji_quotation;
DELETE FROM guji_book;
DELETE FROM guji_category;
DELETE FROM guji_recommend;
DELETE FROM guji_homepage_banner;

-- ------------------------------ 1. 分类 ------------------------------
INSERT INTO guji_category
    (cate_id, parent_id, cate_name, cate_type, cate_level, order_num, description, status, del_flag, create_time, update_time)
SELECT
    c.id,
    0,
    CASE c.name
        WHEN '经部' THEN '经'
        WHEN '史部' THEN '史'
        WHEN '子部' THEN '子'
        WHEN '集部' THEN '集'
        ELSE '其他'
    END,
    'traditional',
    1,
    c.sort_order,
    coalesce(c.description, ''),
    '0',
    '0',
    now(),
    now()
FROM gj_category c;

-- ------------------------------ 2. 书籍 ------------------------------
INSERT INTO guji_book
    (book_id, book_name, authors, dynasty_name, traditional_category, abstract, introduction,
     edition, library, importance_level, popularity, book_status, has_main_content,
     version, meta_version, pin_yin_version, audio_version, status, del_flag, create_time, update_time)
SELECT
    b.id,
    b.title,
    coalesce(b.author, ''),
    coalesce(b.dynasty, ''),
    CASE c.name
        WHEN '经部' THEN '经'
        WHEN '史部' THEN '史'
        WHEN '子部' THEN '子'
        WHEN '集部' THEN '集'
        ELSE '其他'
    END,
    left(coalesce(b.summary, ''), 500),
    coalesce(b.summary, ''),
    coalesce(b.source, 'public'),
    coalesce(b.source, 'public'),
    5,
    b.char_count,
    'published',
    CASE WHEN b.chapter_count > 0 THEN 1 ELSE 0 END,
    1, 1, 1, 1,
    '0',
    '0',
    now(),
    now()
FROM gj_book b
LEFT JOIN gj_category c ON c.id = b.category_id;

-- ------------------------------ 3. 卷（一书一卷） ------------------------------
INSERT INTO guji_volume
    (volume_id, book_id, volume_name, volume_order, has_main_content, editors, del_flag, create_time, update_time)
SELECT b.id, b.id, '全文', 1, 1, '识典古籍整理组', '0', now(), now()
FROM gj_book b;

-- ------------------------------ 4. 章节（目录） ------------------------------
INSERT INTO guji_chapter
    (chapter_id, book_id, volume_id, chapter_name, str_chapter_name, chapter_level, chapter_order,
     has_main_content, del_flag, create_time, update_time)
SELECT c.id, c.book_id, c.book_id, c.title, c.title, 1, c.idx, 1, '0', now(), now()
FROM gj_chapter c
JOIN gj_book b ON b.id = c.book_id;

-- ------------------------------ 5. 段落（正文，按换行切分） ------------------------------
INSERT INTO guji_paragraph
    (book_id, volume_id, chapter_id, chapter_name, para_index, content_type, para_source_type,
     content, book_version, del_flag, create_time, update_time)
SELECT
    c.book_id,
    c.book_id,
    c.id,
    c.title,
    row_number() OVER (PARTITION BY c.id ORDER BY p.ord),
    'NORMAL',
    'origin',
    btrim(p.part),
    1,
    '0',
    now(),
    now()
FROM gj_chapter c
JOIN gj_book b ON b.id = c.book_id
CROSS JOIN LATERAL regexp_split_to_table(c.content, '\n') WITH ORDINALITY AS p(part, ord)
WHERE length(btrim(p.part)) > 0;

COMMIT;

-- ------------------------------ 6. 回填统计 ------------------------------
UPDATE guji_chapter ch
SET paragraph_count = coalesce(t.cnt, 0)
FROM (SELECT chapter_id, count(*) cnt FROM guji_paragraph GROUP BY chapter_id) t
WHERE t.chapter_id = ch.chapter_id;

UPDATE guji_book bk
SET paragraph_number = coalesce(t.cnt, 0),
    paragraph_size = CASE WHEN t.cnt > 0 THEN t.chars / t.cnt ELSE 0 END
FROM (
    SELECT p.book_id, count(*) cnt, sum(length(p.content)) chars
    FROM guji_paragraph p GROUP BY p.book_id
) t
WHERE t.book_id = bk.book_id;

UPDATE guji_category c
SET book_count = coalesce(t.cnt, 0)
FROM (SELECT traditional_category, count(*) cnt FROM guji_book GROUP BY traditional_category) t
WHERE t.traditional_category = c.cate_name;

-- ------------------------------ 7. 序列对齐（前面用了显式主键） ------------------------------
SELECT setval(pg_get_serial_sequence('guji_category', 'cate_id'), GREATEST((SELECT max(cate_id) FROM guji_category), 1));
SELECT setval(pg_get_serial_sequence('guji_book', 'book_id'), GREATEST((SELECT max(book_id) FROM guji_book), 1));
SELECT setval(pg_get_serial_sequence('guji_volume', 'volume_id'), GREATEST((SELECT max(volume_id) FROM guji_volume), 1));
SELECT setval(pg_get_serial_sequence('guji_chapter', 'chapter_id'), GREATEST((SELECT max(chapter_id) FROM guji_chapter), 1));
SELECT setval(pg_get_serial_sequence('guji_paragraph', 'paragraph_id'), GREATEST((SELECT max(paragraph_id) FROM guji_paragraph), 1));

-- ------------------------------ 8. 首页：横幅 + 推荐位 ------------------------------
INSERT INTO guji_homepage_banner
    (title, images, schema_url, order_num, status, del_flag, create_time, update_time)
VALUES
    ('识典古籍 · 免费阅读', '{"800": "https://lf3-static.bytednsdoc.com/obj/eden-cn/banner.webp"}', 'guji://book/1', 1, '0', '0', now(), now()),
    ('经史子集 · 全文在线', '{"800": "https://lf3-static.bytednsdoc.com/obj/eden-cn/banner2.webp"}', 'guji://category', 2, '0', '0', now(), now());

INSERT INTO guji_recommend
    (module_key, module_title, biz_type, biz_id, title, sub_title, schema_url, order_num, status, del_flag, create_time, update_time)
SELECT
    'recommend',
    '今日推荐',
    'book',
    b.book_id::text,
    b.book_name,
    b.authors || ' · ' || coalesce(b.dynasty_name, ''),
    'guji://book/' || b.book_id::text,
    row_number() OVER (ORDER BY b.popularity DESC, b.book_id),
    '0',
    '0',
    now(),
    now()
FROM guji_book b
WHERE b.has_main_content = 1
ORDER BY b.popularity DESC, b.book_id
LIMIT 12;

-- ------------------------------ 9. 名句：从热门书籍正文中抽取 ------------------------------
-- 规则：取每本书前若干段的首个「8~28 字且含句号/反问」的句子，按书籍热度取前 60 条
WITH candidate AS (
    SELECT
        p.book_id,
        p.chapter_id,
        p.paragraph_id,
        p.chapter_name,
        (regexp_match(p.content, '[^。！？；]*[。！？]'))[1] AS sentence
    FROM guji_paragraph p
    JOIN guji_book b ON b.book_id = p.book_id
    WHERE p.content LIKE '%。%' OR p.content LIKE '%！%' OR p.content LIKE '%？%'
)
INSERT INTO guji_quotation
    (book_id, book_name, book_version, chapter_id, chapter_name, paragraph_id, famous_quote,
     cate_name, author, dynasty_category, favorites_num, status, del_flag, create_time, update_time)
SELECT
    c.book_id,
    b.book_name,
    1,
    c.chapter_id,
    c.chapter_name,
    c.paragraph_id,
    replace(c.sentence, '　', ''),
    coalesce(b.traditional_category, '其他'),
    b.authors,
    coalesce(b.dynasty_name, ''),
    0,
    'published',
    '0',
    now(),
    now()
FROM candidate c
JOIN guji_book b ON b.book_id = c.book_id
WHERE length(c.sentence) BETWEEN 8 AND 28
  AND c.sentence NOT LIKE '%本章%'
ORDER BY b.popularity DESC, c.paragraph_id
LIMIT 60;
