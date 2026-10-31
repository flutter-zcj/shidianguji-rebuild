-- 识典古籍：名句重建（可重复执行）
--
-- 策略：
-- 1. 先用「经典名句白名单」在正文中做包含匹配，命中才入库 —— 保证句子真实存在于对应书籍
-- 2. 白名单未覆盖的热门书，按严格规则（8~30 字、无冒号解释、无说书人口吻）补足，每本最多 2 条

DELETE FROM guji_quotation;

-- ------------------------------ 1. 白名单名句 ------------------------------
WITH whitelist(book_name, quote_text, needle) AS (
    VALUES
    ('论语', '学而时习之，不亦说乎？', '学而时习之'),
    ('论语', '有朋自远方来，不亦乐乎？', '有朋自远方来'),
    ('论语', '三人行，必有我师焉。', '三人行'),
    ('论语', '温故而知新，可以为师矣。', '温故而知新'),
    ('论语', '知之者不如好之者，好之者不如乐之者。', '知之者不如好之者'),
    ('论语', '逝者如斯夫，不舍昼夜。', '逝者如斯夫'),
    ('论语', '吾日三省吾身。', '吾日三省吾身'),
    ('论语', '君子坦荡荡，小人长戚戚。', '君子坦荡荡'),
    ('论语', '己所不欲，勿施于人。', '己所不欲'),
    ('道德经', '道可道，非常道；名可名，非常名。', '道可道'),
    ('道德经', '上善若水，水善利万物而不争。', '上善若水'),
    ('道德经', '千里之行，始于足下。', '千里之行'),
    ('道德经', '知人者智，自知者明。', '知人者智'),
    ('道德经', '祸兮福之所倚，福兮祸之所伏。', '祸兮福之所倚'),
    ('道德经', '治大国若烹小鲜。', '治大国若烹小鲜'),
    ('易经', '天行健，君子以自强不息。', '天行健'),
    ('易经', '地势坤，君子以厚德载物。', '地势坤'),
    ('易经', '穷则变，变则通，通则久。', '穷则变'),
    ('孟子', '生于忧患，而死于安乐也。', '生于忧患'),
    ('孟子', '富贵不能淫，贫贱不能移，威武不能屈。', '富贵不能淫'),
    ('孟子', '鱼，我所欲也；熊掌，亦我所欲也。', '我所欲也'),
    ('孟子', '天时不如地利，地利不如人和。', '天时不如地利'),
    ('诗经', '关关雎鸠，在河之洲。', '关关雎鸠'),
    ('诗经', '蒹葭苍苍，白露为霜。', '蒹葭苍苍'),
    ('诗经', '桃之夭夭，灼灼其华。', '桃之夭夭'),
    ('诗经', '执子之手，与子偕老。', '执子之手'),
    ('孙子兵法', '知己知彼，百战不殆。', '知己知彼'),
    ('孙子兵法', '兵者，诡道也。', '兵者'),
    ('孙子兵法', '攻其无备，出其不意。', '攻其无备'),
    ('红楼梦', '满纸荒唐言，一把辛酸泪。', '满纸荒唐言'),
    ('三国志演义', '话说天下大势，分久必合，合久必分。', '分久必合'),
    ('西游记', '心生，种种魔生；心灭，种种魔灭。', '种种魔生'),
    ('水浒传', '路见不平，拔刀相助。', '拔刀相助'),
    ('菜根谭', '宠辱不惊，闲看庭前花开花落。', '宠辱不惊'),
    ('围炉夜话', '教子弟于幼时，便当有正大光明气象。', '正大光明'),
    ('颜氏家训', '积财千万，不如薄伎在身。', '积财千万'),
    ('世说新语', '小时了了，大未必佳。', '小时了了')
)
INSERT INTO guji_quotation
    (book_id, book_name, book_version, chapter_id, chapter_name, paragraph_id, famous_quote,
     cate_name, author, dynasty_category, favorites_num, status, del_flag, create_time, update_time)
SELECT DISTINCT ON (w.quote_text)
    b.book_id,
    b.book_name,
    1,
    p.chapter_id,
    p.chapter_name,
    p.paragraph_id,
    w.quote_text,
    coalesce(b.traditional_category, '其他'),
    b.authors,
    coalesce(b.dynasty_name, ''),
    0,
    'published',
    '0',
    now(),
    now()
FROM whitelist w
JOIN guji_book b ON b.book_name = w.book_name
JOIN guji_paragraph p ON p.book_id = b.book_id AND p.content LIKE '%' || w.needle || '%'
ORDER BY w.quote_text, p.paragraph_id;

-- ------------------------------ 2. 严格规则补足（每本最多 2 条） ------------------------------
INSERT INTO guji_quotation
    (book_id, book_name, book_version, chapter_id, chapter_name, paragraph_id, famous_quote,
     cate_name, author, dynasty_category, favorites_num, status, del_flag, create_time, update_time)
SELECT
    b.book_id,
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
FROM (
    SELECT
        p.book_id, p.chapter_id, p.paragraph_id, p.chapter_name,
        (regexp_match(p.content, '[^。！？；]*[。！？]'))[1] AS sentence,
        row_number() OVER (PARTITION BY p.book_id ORDER BY p.paragraph_id) AS rn
    FROM guji_paragraph p
    WHERE length(p.content) > 40
      AND p.content NOT LIKE '%：%'
      AND p.content NOT LIKE '%看官%'
      AND p.content NOT LIKE '%你道%'
      AND p.content NOT LIKE '%说话%'
) c
JOIN guji_book b ON b.book_id = c.book_id
WHERE c.rn <= 2
  AND length(c.sentence) BETWEEN 10 AND 30
  AND b.traditional_category IN ('经', '子')
  AND NOT EXISTS (
      SELECT 1 FROM guji_quotation q WHERE q.book_id = b.book_id
  )
ORDER BY b.popularity DESC, c.paragraph_id
LIMIT 30;

-- ------------------------------ 3. 系统通知 ------------------------------
INSERT INTO guji_notice (title, content, notice_type, publish_time, status, del_flag)
SELECT * FROM (VALUES
    ('《论语》新增全本注疏', '《论语》已完成全本注疏整理，可在阅读器中开启注疏显示查看。', 'system', to_char(now(), 'YYYY-MM-DD HH24:MI'), '0', '0'),
    ('阅读打卡活动上线', '连续打卡 7 天可解锁「笃学」等级权益，记得每天来读一读。', 'system', to_char(now(), 'YYYY-MM-DD HH24:MI'), '0', '0'),
    ('听书功能更新', '多部经典已生成朗读音频，可在听书页试听。', 'system', to_char(now(), 'YYYY-MM-DD HH24:MI'), '0', '0')
) v(title, content, notice_type, publish_time, status, del_flag);

SELECT '名句' AS 项, count(*) AS 行数 FROM guji_quotation
UNION ALL SELECT '通知', count(*) FROM guji_notice;
