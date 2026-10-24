-- Old schema.sql checked constraint names across all schemas. Repair only missing
-- circular foreign keys in the current schema, retaining every existing row.
DO $fk$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_submissions_latest_report' AND conrelid = 'submissions'::regclass
    ) THEN
        ALTER TABLE submissions ADD CONSTRAINT fk_submissions_latest_report
            FOREIGN KEY (latest_report_id) REFERENCES ai_reports(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_submissions_ai_job' AND conrelid = 'submissions'::regclass
    ) THEN
        ALTER TABLE submissions ADD CONSTRAINT fk_submissions_ai_job
            FOREIGN KEY (ai_job_id) REFERENCES jobs(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_materials_current_version' AND conrelid = 'materials'::regclass
    ) THEN
        ALTER TABLE materials ADD CONSTRAINT fk_materials_current_version
            FOREIGN KEY (current_version_id) REFERENCES material_versions(id) ON DELETE SET NULL;
    END IF;
END
$fk$;
