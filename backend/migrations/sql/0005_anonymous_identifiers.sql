-- Replace identifiers derived from student numbers without touching original materials.
UPDATE archives
SET anon_code = 'A' || replace(gen_random_uuid()::text, '-', '')
WHERE student_no <> '' AND position(student_no in coalesce(anon_code, '')) > 0;

-- Only repair unsafe/missing anonymous identifiers, preserving the notice body.
UPDATE notices n
SET content = jsonb_set(n.content, '{student,anon_code}', to_jsonb(a.anon_code), true)
FROM archives a
WHERE n.archive_id = a.id AND jsonb_typeof(n.content->'student') = 'object'
AND (coalesce(n.content#>>'{student,anon_code}', '') = ''
     OR (coalesce(n.content#>>'{student,student_no}', '') <> ''
         AND position(n.content#>>'{student,student_no}' in n.content#>>'{student,anon_code}') > 0)
     OR (a.student_no <> '' AND position(a.student_no in n.content#>>'{student,anon_code}') > 0));

-- Previously generated spreadsheets cannot be repaired by rewriting database rows.
-- Expire their authenticated download links; administrators can regenerate them.
UPDATE export_files SET expires_at = LEAST(coalesce(expires_at, now()), now())
WHERE export_type = 'DESENSITIZED_DATA';
