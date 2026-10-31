-- 数据打磨 v2：为「整书只一个章节」的书重建章节目录，并清理英文元数据简介
--
-- 与 v1 的区别：段落重挂载改用「临时索引 + 区间连接」，避免逐行关联子查询（v1 跑 10 分钟未完成）

BEGIN;

-- ------------------------------ 1. 识别候选标题 ------------------------------
CREATE TEMP TABLE single_book AS
SELECT c.book_id, max(c.chapter_order) AS max_order
FROM guji_chapter c
GROUP BY c.book_id
HAVING count(*) = 1;

CREATE TEMP TABLE heading AS
SELECT
    p.book_id,
    p.para_index,
    p.content,
    row_number() OVER (PARTITION BY p.book_id ORDER BY p.para_index) AS hidx
FROM guji_paragraph p
JOIN single_book s ON s.book_id = p.book_id
WHERE length(p.content) BETWEEN 2 AND 24
  AND translate(p.content, '。，、；：！？「」“”"0123456789', '') = p.content;

CREATE TEMP TABLE target AS
SELECT book_id, min(para_index) AS first_index
FROM heading
GROUP BY book_id
HAVING count(*) >= 2;

CREATE TEMP TABLE new_chapter AS
SELECT row_number() OVER (ORDER BY h.book_id, h.hidx) AS rn, h.*, s.max_order
FROM heading h
JOIN target t ON t.book_id = h.book_id
JOIN single_book s ON s.book_id = h.book_id;

-- ------------------------------ 2. 写入新章节，并取回 id ↔ 起始段序号 ------------------------------
CREATE TEMP TABLE chapter_map AS
WITH ins AS (
    INSERT INTO guji_chapter
        (book_id, volume_id, chapter_name, str_chapter_name, chapter_level, chapter_order,
         has_main_content, del_flag, create_time, update_time)
    SELECT n.book_id, n.book_id, n.content, n.content, 1, n.max_order + n.hidx, 1, '0', now(), now()
    FROM new_chapter n
    RETURNING chapter_id, book_id, chapter_name, chapter_order
)
SELECT
    i.chapter_id,
    i.book_id,
    i.chapter_name,
    n.para_index
FROM ins i
JOIN new_chapter n
  ON n.book_id = i.book_id
 AND i.chapter_order = n.max_order + n.hidx;

CREATE INDEX idx_chapter_map ON chapter_map (book_id, para_index);

-- 段落表临时索引：让区间连接走索引扫描
CREATE INDEX tmp_idx_gp ON guji_paragraph (book_id, para_index);

-- ------------------------------ 3. 区间挂载：标题之后的段落归入该章节 ------------------------------
CREATE TEMP TABLE bound AS
SELECT
    book_id,
    chapter_id,
    chapter_name,
    para_index AS lo,
    coalesce(lead(para_index) OVER (PARTITION BY book_id ORDER BY para_index), 2147483647) AS hi
FROM chapter_map;

UPDATE guji_paragraph p
SET chapter_id = b.chapter_id,
    chapter_name = b.chapter_name
FROM bound b
JOIN target t ON t.book_id = b.book_id
WHERE p.book_id = b.book_id
  AND p.para_index >= b.lo
  AND p.para_index < b.hi;

-- ------------------------------ 4. 首个标题之前的内容归入第一章 ------------------------------
UPDATE guji_paragraph p
SET chapter_id = f.chapter_id,
    chapter_name = f.chapter_name
FROM (
    SELECT DISTINCT ON (c.book_id) c.book_id, c.chapter_id, c.chapter_name
    FROM chapter_map c
    ORDER BY c.book_id, c.para_index
) f
JOIN target t ON t.book_id = f.book_id
WHERE p.book_id = f.book_id
  AND p.chapter_id IN (SELECT chapter_id FROM guji_chapter pc WHERE pc.book_id = p.book_id AND pc.chapter_order = (SELECT max_order FROM single_book s WHERE s.book_id = p.book_id));

-- ------------------------------ 5. 清理无段落的旧“全篇”章节 ------------------------------
DELETE FROM guji_chapter c
USING target x
WHERE x.book_id = c.book_id
  AND NOT EXISTS (SELECT 1 FROM guji_paragraph p WHERE p.chapter_id = c.chapter_id);

DROP INDEX tmp_idx_gp;

COMMIT;

-- ------------------------------ 6. 统计与清档 ------------------------------
UPDATE guji_chapter ch
SET paragraph_count = coalesce(t.cnt, 0)
FROM (SELECT chapter_id, count(*) cnt FROM guji_paragraph GROUP BY chapter_id) t
WHERE t.chapter_id = ch.chapter_id;

UPDATE guji_book b
SET abstract = CASE
        WHEN coalesce(b.dynasty_name, '') = '' THEN CONCAT('《', b.book_name, '》', coalesce(b.authors, ''), '撰。全书共 ', coalesce(b.paragraph_number, 0), ' 段。')
        ELSE CONCAT('《', b.book_name, '》', b.dynasty_name, '·', coalesce(b.authors, ''), '撰。全书共 ', coalesce(b.paragraph_number, 0), ' 段。')
    END,
    introduction = CASE
        WHEN coalesce(b.dynasty_name, '') = '' THEN CONCAT('《', b.book_name, '》为', coalesce(b.authors, ''), '所著，共收录 ', coalesce(b.paragraph_number, 0), ' 段正文。')
        ELSE CONCAT('《', b.book_name, '》为', b.dynasty_name, '时期', coalesce(b.authors, ''), '所著，共收录 ', coalesce(b.paragraph_number, 0), ' 段正文。')
    END
WHERE coalesce(b.abstract, '') <> ''
  AND b.abstract !~ '[一-龥]';

SELECT '书籍' AS 项, count(*) AS 行数 FROM guji_book
UNION ALL SELECT '章节', count(*) FROM guji_chapter
UNION ALL SELECT '段落', count(*) FROM guji_paragraph
UNION ALL SELECT '仍为单章的书', count(*) FROM (SELECT book_id FROM guji_chapter GROUP BY book_id HAVING count(*) = 1) v
UNION ALL SELECT '纯英文简介已改写', count(*) FROM guji_book WHERE abstract LIKE '《%';
