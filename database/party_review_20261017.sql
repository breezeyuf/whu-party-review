--
-- PostgreSQL database dump
--

\restrict d0phDmaZdf0gLSTcuYfKJMuMWmtLFAimPwHAkEpt2wybWERVbVFYkiOuntZ9Ons

-- Dumped from database version 16.15
-- Dumped by pg_dump version 16.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_org_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_roles DROP CONSTRAINT IF EXISTS user_roles_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_roles DROP CONSTRAINT IF EXISTS user_roles_org_id_fkey;
ALTER TABLE IF EXISTS ONLY public.time_rules DROP CONSTRAINT IF EXISTS time_rules_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY public.time_rules DROP CONSTRAINT IF EXISTS time_rules_suggestion_template_id_fkey;
ALTER TABLE IF EXISTS ONLY public.time_node_extractions DROP CONSTRAINT IF EXISTS time_node_extractions_material_version_id_fkey;
ALTER TABLE IF EXISTS ONLY public.time_node_extractions DROP CONSTRAINT IF EXISTS time_node_extractions_material_id_fkey;
ALTER TABLE IF EXISTS ONLY public.time_node_extractions DROP CONSTRAINT IF EXISTS time_node_extractions_archive_id_fkey;
ALTER TABLE IF EXISTS ONLY public.time_node_defs DROP CONSTRAINT IF EXISTS time_node_defs_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY public.time_node_defs DROP CONSTRAINT IF EXISTS time_node_defs_stage_code_fkey;
ALTER TABLE IF EXISTS ONLY public.time_node_defs DROP CONSTRAINT IF EXISTS time_node_defs_required_from_stage_fkey;
ALTER TABLE IF EXISTS ONLY public.system_settings DROP CONSTRAINT IF EXISTS system_settings_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY public.suggestion_templates DROP CONSTRAINT IF EXISTS suggestion_templates_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY public.submissions DROP CONSTRAINT IF EXISTS submissions_stage_code_fkey;
ALTER TABLE IF EXISTS ONLY public.submissions DROP CONSTRAINT IF EXISTS submissions_filed_by_fkey;
ALTER TABLE IF EXISTS ONLY public.submissions DROP CONSTRAINT IF EXISTS submissions_college_id_fkey;
ALTER TABLE IF EXISTS ONLY public.submissions DROP CONSTRAINT IF EXISTS submissions_branch_id_fkey;
ALTER TABLE IF EXISTS ONLY public.submissions DROP CONSTRAINT IF EXISTS submissions_batch_id_fkey;
ALTER TABLE IF EXISTS ONLY public.submissions DROP CONSTRAINT IF EXISTS submissions_archive_id_fkey;
ALTER TABLE IF EXISTS ONLY public.sensitive_phrases DROP CONSTRAINT IF EXISTS sensitive_phrases_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY public.rule_versions DROP CONSTRAINT IF EXISTS rule_versions_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.review_records DROP CONSTRAINT IF EXISTS review_records_submission_id_fkey;
ALTER TABLE IF EXISTS ONLY public.review_records DROP CONSTRAINT IF EXISTS review_records_reviewer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.review_records DROP CONSTRAINT IF EXISTS review_records_report_id_fkey;
ALTER TABLE IF EXISTS ONLY public.prompt_templates DROP CONSTRAINT IF EXISTS prompt_templates_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY public.political_terms DROP CONSTRAINT IF EXISTS political_terms_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY public.parse_results DROP CONSTRAINT IF EXISTS parse_results_version_id_fkey;
ALTER TABLE IF EXISTS ONLY public.parse_results DROP CONSTRAINT IF EXISTS parse_results_corrected_by_fkey;
ALTER TABLE IF EXISTS ONLY public.orgs DROP CONSTRAINT IF EXISTS orgs_parent_id_fkey;
ALTER TABLE IF EXISTS ONLY public.notices DROP CONSTRAINT IF EXISTS notices_submission_id_fkey;
ALTER TABLE IF EXISTS ONLY public.notices DROP CONSTRAINT IF EXISTS notices_student_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.notices DROP CONSTRAINT IF EXISTS notices_report_id_fkey;
ALTER TABLE IF EXISTS ONLY public.notices DROP CONSTRAINT IF EXISTS notices_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.notices DROP CONSTRAINT IF EXISTS notices_archive_id_fkey;
ALTER TABLE IF EXISTS ONLY public.messages DROP CONSTRAINT IF EXISTS messages_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.materials DROP CONSTRAINT IF EXISTS materials_uploaded_by_fkey;
ALTER TABLE IF EXISTS ONLY public.materials DROP CONSTRAINT IF EXISTS materials_type_id_fkey;
ALTER TABLE IF EXISTS ONLY public.materials DROP CONSTRAINT IF EXISTS materials_submission_id_fkey;
ALTER TABLE IF EXISTS ONLY public.materials DROP CONSTRAINT IF EXISTS materials_stage_code_fkey;
ALTER TABLE IF EXISTS ONLY public.materials DROP CONSTRAINT IF EXISTS materials_deleted_by_fkey;
ALTER TABLE IF EXISTS ONLY public.materials DROP CONSTRAINT IF EXISTS materials_declared_type_id_fkey;
ALTER TABLE IF EXISTS ONLY public.materials DROP CONSTRAINT IF EXISTS materials_archive_id_fkey;
ALTER TABLE IF EXISTS ONLY public.material_versions DROP CONSTRAINT IF EXISTS material_versions_uploaded_by_fkey;
ALTER TABLE IF EXISTS ONLY public.material_versions DROP CONSTRAINT IF EXISTS material_versions_material_id_fkey;
ALTER TABLE IF EXISTS ONLY public.material_types DROP CONSTRAINT IF EXISTS material_types_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY public.jobs DROP CONSTRAINT IF EXISTS jobs_parent_id_fkey;
ALTER TABLE IF EXISTS ONLY public.jobs DROP CONSTRAINT IF EXISTS jobs_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.issues DROP CONSTRAINT IF EXISTS issues_submission_id_fkey;
ALTER TABLE IF EXISTS ONLY public.issues DROP CONSTRAINT IF EXISTS issues_reviewed_by_fkey;
ALTER TABLE IF EXISTS ONLY public.issues DROP CONSTRAINT IF EXISTS issues_response_version_id_fkey;
ALTER TABLE IF EXISTS ONLY public.issues DROP CONSTRAINT IF EXISTS issues_resolved_by_report_id_fkey;
ALTER TABLE IF EXISTS ONLY public.issues DROP CONSTRAINT IF EXISTS issues_report_id_fkey;
ALTER TABLE IF EXISTS ONLY public.issues DROP CONSTRAINT IF EXISTS issues_prev_issue_id_fkey;
ALTER TABLE IF EXISTS ONLY public.issues DROP CONSTRAINT IF EXISTS issues_material_version_id_fkey;
ALTER TABLE IF EXISTS ONLY public.issues DROP CONSTRAINT IF EXISTS issues_material_id_fkey;
ALTER TABLE IF EXISTS ONLY public.issues DROP CONSTRAINT IF EXISTS issues_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.handover_records DROP CONSTRAINT IF EXISTS handover_records_submission_id_fkey;
ALTER TABLE IF EXISTS ONLY public.handover_records DROP CONSTRAINT IF EXISTS handover_records_report_id_fkey;
ALTER TABLE IF EXISTS ONLY public.handover_records DROP CONSTRAINT IF EXISTS handover_records_assignee_id_fkey;
ALTER TABLE IF EXISTS ONLY public.submissions DROP CONSTRAINT IF EXISTS fk_submissions_latest_report;
ALTER TABLE IF EXISTS ONLY public.submissions DROP CONSTRAINT IF EXISTS fk_submissions_ai_job;
ALTER TABLE IF EXISTS ONLY public.materials DROP CONSTRAINT IF EXISTS fk_materials_current_version;
ALTER TABLE IF EXISTS ONLY public.export_files DROP CONSTRAINT IF EXISTS export_files_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.cross_review_pairs DROP CONSTRAINT IF EXISTS cross_review_pairs_target_branch_id_fkey;
ALTER TABLE IF EXISTS ONLY public.cross_review_pairs DROP CONSTRAINT IF EXISTS cross_review_pairs_reviewer_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.cross_review_pairs DROP CONSTRAINT IF EXISTS cross_review_pairs_reviewer_branch_id_fkey;
ALTER TABLE IF EXISTS ONLY public.cross_review_pairs DROP CONSTRAINT IF EXISTS cross_review_pairs_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.cross_review_pairs DROP CONSTRAINT IF EXISTS cross_review_pairs_college_id_fkey;
ALTER TABLE IF EXISTS ONLY public.cross_review_pairs DROP CONSTRAINT IF EXISTS cross_review_pairs_batch_id_fkey;
ALTER TABLE IF EXISTS ONLY public.checklist_items DROP CONSTRAINT IF EXISTS checklist_items_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY public.checklist_items DROP CONSTRAINT IF EXISTS checklist_items_stage_code_fkey;
ALTER TABLE IF EXISTS ONLY public.checklist_items DROP CONSTRAINT IF EXISTS checklist_items_material_type_id_fkey;
ALTER TABLE IF EXISTS ONLY public.check_rules DROP CONSTRAINT IF EXISTS check_rules_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY public.check_rules DROP CONSTRAINT IF EXISTS check_rules_suggestion_template_id_fkey;
ALTER TABLE IF EXISTS ONLY public.batches DROP CONSTRAINT IF EXISTS batches_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.batch_upload_items DROP CONSTRAINT IF EXISTS batch_upload_items_material_type_id_fkey;
ALTER TABLE IF EXISTS ONLY public.batch_upload_items DROP CONSTRAINT IF EXISTS batch_upload_items_material_id_fkey;
ALTER TABLE IF EXISTS ONLY public.batch_upload_items DROP CONSTRAINT IF EXISTS batch_upload_items_matched_archive_id_fkey;
ALTER TABLE IF EXISTS ONLY public.batch_upload_items DROP CONSTRAINT IF EXISTS batch_upload_items_job_id_fkey;
ALTER TABLE IF EXISTS ONLY public.archives DROP CONSTRAINT IF EXISTS archives_student_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.archives DROP CONSTRAINT IF EXISTS archives_current_stage_fkey;
ALTER TABLE IF EXISTS ONLY public.archives DROP CONSTRAINT IF EXISTS archives_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.archives DROP CONSTRAINT IF EXISTS archives_college_id_fkey;
ALTER TABLE IF EXISTS ONLY public.archives DROP CONSTRAINT IF EXISTS archives_branch_id_fkey;
ALTER TABLE IF EXISTS ONLY public.archives DROP CONSTRAINT IF EXISTS archives_batch_id_fkey;
ALTER TABLE IF EXISTS ONLY public.archive_time_nodes DROP CONSTRAINT IF EXISTS archive_time_nodes_source_extraction_id_fkey;
ALTER TABLE IF EXISTS ONLY public.archive_time_nodes DROP CONSTRAINT IF EXISTS archive_time_nodes_locked_stage_fkey;
ALTER TABLE IF EXISTS ONLY public.archive_time_nodes DROP CONSTRAINT IF EXISTS archive_time_nodes_corrected_by_fkey;
ALTER TABLE IF EXISTS ONLY public.archive_time_nodes DROP CONSTRAINT IF EXISTS archive_time_nodes_archive_id_fkey;
ALTER TABLE IF EXISTS ONLY public.ai_reports DROP CONSTRAINT IF EXISTS ai_reports_triggered_by_fkey;
ALTER TABLE IF EXISTS ONLY public.ai_reports DROP CONSTRAINT IF EXISTS ai_reports_submission_id_fkey;
ALTER TABLE IF EXISTS ONLY public.ai_reports DROP CONSTRAINT IF EXISTS ai_reports_rule_version_id_fkey;
ALTER TABLE IF EXISTS ONLY public.ai_reports DROP CONSTRAINT IF EXISTS ai_reports_recheck_of_report_id_fkey;
ALTER TABLE IF EXISTS ONLY public.ai_reports DROP CONSTRAINT IF EXISTS ai_reports_job_id_fkey;
DROP TRIGGER IF EXISTS trg_users_updated_at ON public.users;
DROP TRIGGER IF EXISTS trg_time_rules_updated_at ON public.time_rules;
DROP TRIGGER IF EXISTS trg_time_node_defs_updated_at ON public.time_node_defs;
DROP TRIGGER IF EXISTS trg_system_settings_updated_at ON public.system_settings;
DROP TRIGGER IF EXISTS trg_suggestion_templates_updated_at ON public.suggestion_templates;
DROP TRIGGER IF EXISTS trg_submissions_updated_at ON public.submissions;
DROP TRIGGER IF EXISTS trg_submissions_filed_guard ON public.submissions;
DROP TRIGGER IF EXISTS trg_sensitive_phrases_updated_at ON public.sensitive_phrases;
DROP TRIGGER IF EXISTS trg_schema_meta_updated_at ON public.schema_meta;
DROP TRIGGER IF EXISTS trg_review_records_guard ON public.review_records;
DROP TRIGGER IF EXISTS trg_prompt_templates_updated_at ON public.prompt_templates;
DROP TRIGGER IF EXISTS trg_political_terms_updated_at ON public.political_terms;
DROP TRIGGER IF EXISTS trg_parse_results_updated_at ON public.parse_results;
DROP TRIGGER IF EXISTS trg_orgs_updated_at ON public.orgs;
DROP TRIGGER IF EXISTS trg_notices_updated_at ON public.notices;
DROP TRIGGER IF EXISTS trg_materials_updated_at ON public.materials;
DROP TRIGGER IF EXISTS trg_material_versions_guard ON public.material_versions;
DROP TRIGGER IF EXISTS trg_material_types_updated_at ON public.material_types;
DROP TRIGGER IF EXISTS trg_issues_updated_at ON public.issues;
DROP TRIGGER IF EXISTS trg_checklist_items_updated_at ON public.checklist_items;
DROP TRIGGER IF EXISTS trg_check_rules_updated_at ON public.check_rules;
DROP TRIGGER IF EXISTS trg_batches_updated_at ON public.batches;
DROP TRIGGER IF EXISTS trg_batch_upload_items_updated_at ON public.batch_upload_items;
DROP TRIGGER IF EXISTS trg_audit_logs_append_only ON public.audit_logs;
DROP TRIGGER IF EXISTS trg_archives_updated_at ON public.archives;
DROP TRIGGER IF EXISTS trg_archive_time_nodes_updated_at ON public.archive_time_nodes;
DROP INDEX IF EXISTS public.ix_users_org;
DROP INDEX IF EXISTS public.ix_user_roles_role_org;
DROP INDEX IF EXISTS public.ix_submissions_status;
DROP INDEX IF EXISTS public.ix_submissions_college;
DROP INDEX IF EXISTS public.ix_submissions_batch;
DROP INDEX IF EXISTS public.ix_revoked_tokens_exp;
DROP INDEX IF EXISTS public.ix_review_records_submission;
DROP INDEX IF EXISTS public.ix_review_records_reviewer;
DROP INDEX IF EXISTS public.ix_orgs_parent;
DROP INDEX IF EXISTS public.ix_notices_submission;
DROP INDEX IF EXISTS public.ix_notices_student;
DROP INDEX IF EXISTS public.ix_messages_user;
DROP INDEX IF EXISTS public.ix_materials_submission;
DROP INDEX IF EXISTS public.ix_materials_archive;
DROP INDEX IF EXISTS public.ix_material_versions_sha;
DROP INDEX IF EXISTS public.ix_jobs_target;
DROP INDEX IF EXISTS public.ix_jobs_queue;
DROP INDEX IF EXISTS public.ix_jobs_parent;
DROP INDEX IF EXISTS public.ix_issues_submission;
DROP INDEX IF EXISTS public.ix_issues_rule;
DROP INDEX IF EXISTS public.ix_issues_report;
DROP INDEX IF EXISTS public.ix_issues_fingerprint;
DROP INDEX IF EXISTS public.ix_handover_records_report;
DROP INDEX IF EXISTS public.ix_extractions_version;
DROP INDEX IF EXISTS public.ix_extractions_archive_node;
DROP INDEX IF EXISTS public.ix_cross_pairs_reviewer;
DROP INDEX IF EXISTS public.ix_batch_upload_items_job;
DROP INDEX IF EXISTS public.ix_audit_logs_user;
DROP INDEX IF EXISTS public.ix_audit_logs_time;
DROP INDEX IF EXISTS public.ix_audit_logs_action;
DROP INDEX IF EXISTS public.ix_archives_college;
DROP INDEX IF EXISTS public.ix_archives_branch;
DROP INDEX IF EXISTS public.ix_archives_batch;
DROP INDEX IF EXISTS public.ix_ai_reports_submission;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_username_key;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.user_roles DROP CONSTRAINT IF EXISTS user_roles_pkey;
ALTER TABLE IF EXISTS ONLY public.user_roles DROP CONSTRAINT IF EXISTS uq_user_roles;
ALTER TABLE IF EXISTS ONLY public.submissions DROP CONSTRAINT IF EXISTS uq_submissions_stage;
ALTER TABLE IF EXISTS ONLY public.sensitive_phrases DROP CONSTRAINT IF EXISTS uq_sensitive;
ALTER TABLE IF EXISTS ONLY public.material_versions DROP CONSTRAINT IF EXISTS uq_material_versions;
ALTER TABLE IF EXISTS ONLY public.cross_review_pairs DROP CONSTRAINT IF EXISTS uq_cross_pairs;
ALTER TABLE IF EXISTS ONLY public.checklist_items DROP CONSTRAINT IF EXISTS uq_checklist;
ALTER TABLE IF EXISTS ONLY public.archive_time_nodes DROP CONSTRAINT IF EXISTS uq_archive_time_nodes;
ALTER TABLE IF EXISTS ONLY public.ai_reports DROP CONSTRAINT IF EXISTS uq_ai_reports_no;
ALTER TABLE IF EXISTS ONLY public.time_rules DROP CONSTRAINT IF EXISTS time_rules_pkey;
ALTER TABLE IF EXISTS ONLY public.time_rules DROP CONSTRAINT IF EXISTS time_rules_code_key;
ALTER TABLE IF EXISTS ONLY public.time_node_extractions DROP CONSTRAINT IF EXISTS time_node_extractions_pkey;
ALTER TABLE IF EXISTS ONLY public.time_node_defs DROP CONSTRAINT IF EXISTS time_node_defs_pkey;
ALTER TABLE IF EXISTS ONLY public.time_node_defs DROP CONSTRAINT IF EXISTS time_node_defs_code_key;
ALTER TABLE IF EXISTS ONLY public.system_settings DROP CONSTRAINT IF EXISTS system_settings_pkey;
ALTER TABLE IF EXISTS ONLY public.suggestion_templates DROP CONSTRAINT IF EXISTS suggestion_templates_pkey;
ALTER TABLE IF EXISTS ONLY public.suggestion_templates DROP CONSTRAINT IF EXISTS suggestion_templates_code_key;
ALTER TABLE IF EXISTS ONLY public.submissions DROP CONSTRAINT IF EXISTS submissions_pkey;
ALTER TABLE IF EXISTS ONLY public.stages DROP CONSTRAINT IF EXISTS stages_stage_key_key;
ALTER TABLE IF EXISTS ONLY public.stages DROP CONSTRAINT IF EXISTS stages_pkey;
ALTER TABLE IF EXISTS ONLY public.sensitive_phrases DROP CONSTRAINT IF EXISTS sensitive_phrases_pkey;
ALTER TABLE IF EXISTS ONLY public.schema_meta DROP CONSTRAINT IF EXISTS schema_meta_pkey;
ALTER TABLE IF EXISTS ONLY public.rule_versions DROP CONSTRAINT IF EXISTS rule_versions_version_no_key;
ALTER TABLE IF EXISTS ONLY public.rule_versions DROP CONSTRAINT IF EXISTS rule_versions_pkey;
ALTER TABLE IF EXISTS ONLY public.revoked_tokens DROP CONSTRAINT IF EXISTS revoked_tokens_pkey;
ALTER TABLE IF EXISTS ONLY public.review_records DROP CONSTRAINT IF EXISTS review_records_pkey;
ALTER TABLE IF EXISTS ONLY public.prompt_templates DROP CONSTRAINT IF EXISTS prompt_templates_pkey;
ALTER TABLE IF EXISTS ONLY public.prompt_templates DROP CONSTRAINT IF EXISTS prompt_templates_code_key;
ALTER TABLE IF EXISTS ONLY public.political_terms DROP CONSTRAINT IF EXISTS political_terms_standard_text_key;
ALTER TABLE IF EXISTS ONLY public.political_terms DROP CONSTRAINT IF EXISTS political_terms_pkey;
ALTER TABLE IF EXISTS ONLY public.parse_results DROP CONSTRAINT IF EXISTS parse_results_version_id_key;
ALTER TABLE IF EXISTS ONLY public.parse_results DROP CONSTRAINT IF EXISTS parse_results_pkey;
ALTER TABLE IF EXISTS ONLY public.orgs DROP CONSTRAINT IF EXISTS orgs_pkey;
ALTER TABLE IF EXISTS ONLY public.orgs DROP CONSTRAINT IF EXISTS orgs_code_key;
ALTER TABLE IF EXISTS ONLY public.notices DROP CONSTRAINT IF EXISTS notices_pkey;
ALTER TABLE IF EXISTS ONLY public.messages DROP CONSTRAINT IF EXISTS messages_pkey;
ALTER TABLE IF EXISTS ONLY public.messages DROP CONSTRAINT IF EXISTS messages_dedup_key_key;
ALTER TABLE IF EXISTS ONLY public.materials DROP CONSTRAINT IF EXISTS materials_pkey;
ALTER TABLE IF EXISTS ONLY public.material_versions DROP CONSTRAINT IF EXISTS material_versions_stored_path_key;
ALTER TABLE IF EXISTS ONLY public.material_versions DROP CONSTRAINT IF EXISTS material_versions_pkey;
ALTER TABLE IF EXISTS ONLY public.material_types DROP CONSTRAINT IF EXISTS material_types_pkey;
ALTER TABLE IF EXISTS ONLY public.material_types DROP CONSTRAINT IF EXISTS material_types_code_key;
ALTER TABLE IF EXISTS ONLY public.jobs DROP CONSTRAINT IF EXISTS jobs_pkey;
ALTER TABLE IF EXISTS ONLY public.issues DROP CONSTRAINT IF EXISTS issues_pkey;
ALTER TABLE IF EXISTS ONLY public.handover_records DROP CONSTRAINT IF EXISTS handover_records_pkey;
ALTER TABLE IF EXISTS ONLY public.export_files DROP CONSTRAINT IF EXISTS export_files_pkey;
ALTER TABLE IF EXISTS ONLY public.cross_review_pairs DROP CONSTRAINT IF EXISTS cross_review_pairs_pkey;
ALTER TABLE IF EXISTS ONLY public.checklist_items DROP CONSTRAINT IF EXISTS checklist_items_pkey;
ALTER TABLE IF EXISTS ONLY public.check_rules DROP CONSTRAINT IF EXISTS check_rules_pkey;
ALTER TABLE IF EXISTS ONLY public.check_rules DROP CONSTRAINT IF EXISTS check_rules_code_key;
ALTER TABLE IF EXISTS ONLY public.batches DROP CONSTRAINT IF EXISTS batches_pkey;
ALTER TABLE IF EXISTS ONLY public.batches DROP CONSTRAINT IF EXISTS batches_name_key;
ALTER TABLE IF EXISTS ONLY public.batch_upload_items DROP CONSTRAINT IF EXISTS batch_upload_items_pkey;
ALTER TABLE IF EXISTS ONLY public.audit_logs DROP CONSTRAINT IF EXISTS audit_logs_pkey;
ALTER TABLE IF EXISTS ONLY public.archives DROP CONSTRAINT IF EXISTS archives_student_user_id_key;
ALTER TABLE IF EXISTS ONLY public.archives DROP CONSTRAINT IF EXISTS archives_student_no_key;
ALTER TABLE IF EXISTS ONLY public.archives DROP CONSTRAINT IF EXISTS archives_pkey;
ALTER TABLE IF EXISTS ONLY public.archives DROP CONSTRAINT IF EXISTS archives_anon_code_key;
ALTER TABLE IF EXISTS ONLY public.archive_time_nodes DROP CONSTRAINT IF EXISTS archive_time_nodes_pkey;
ALTER TABLE IF EXISTS ONLY public.ai_reports DROP CONSTRAINT IF EXISTS ai_reports_pkey;
DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.user_roles;
DROP TABLE IF EXISTS public.time_rules;
DROP TABLE IF EXISTS public.time_node_extractions;
DROP TABLE IF EXISTS public.time_node_defs;
DROP TABLE IF EXISTS public.system_settings;
DROP TABLE IF EXISTS public.suggestion_templates;
DROP TABLE IF EXISTS public.submissions;
DROP TABLE IF EXISTS public.stages;
DROP TABLE IF EXISTS public.sensitive_phrases;
DROP TABLE IF EXISTS public.schema_meta;
DROP TABLE IF EXISTS public.rule_versions;
DROP TABLE IF EXISTS public.revoked_tokens;
DROP TABLE IF EXISTS public.review_records;
DROP TABLE IF EXISTS public.prompt_templates;
DROP TABLE IF EXISTS public.political_terms;
DROP TABLE IF EXISTS public.parse_results;
DROP TABLE IF EXISTS public.orgs;
DROP TABLE IF EXISTS public.notices;
DROP TABLE IF EXISTS public.messages;
DROP TABLE IF EXISTS public.materials;
DROP TABLE IF EXISTS public.material_versions;
DROP TABLE IF EXISTS public.material_types;
DROP TABLE IF EXISTS public.jobs;
DROP TABLE IF EXISTS public.issues;
DROP TABLE IF EXISTS public.handover_records;
DROP TABLE IF EXISTS public.export_files;
DROP TABLE IF EXISTS public.cross_review_pairs;
DROP TABLE IF EXISTS public.checklist_items;
DROP TABLE IF EXISTS public.check_rules;
DROP TABLE IF EXISTS public.batches;
DROP TABLE IF EXISTS public.batch_upload_items;
DROP TABLE IF EXISTS public.audit_logs;
DROP TABLE IF EXISTS public.archives;
DROP TABLE IF EXISTS public.archive_time_nodes;
DROP TABLE IF EXISTS public.ai_reports;
DROP FUNCTION IF EXISTS public.set_updated_at();
DROP FUNCTION IF EXISTS public.guard_purge_only();
DROP FUNCTION IF EXISTS public.guard_filed_submission();
DROP FUNCTION IF EXISTS public.forbid_change();
--
-- Name: forbid_change(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.forbid_change() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    RAISE EXCEPTION '表 % 只允许追加，禁止 %', TG_TABLE_NAME, TG_OP USING ERRCODE = 'P0001';
END
$$;


--
-- Name: guard_filed_submission(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.guard_filed_submission() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF current_setting('app.allow_purge', true) = 'on' THEN
        IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
        RETURN NEW;
    END IF;
    IF OLD.status = 'FILED' AND (TG_OP = 'DELETE' OR NEW.status IS DISTINCT FROM 'FILED') THEN
        RAISE EXCEPTION '已备案提交包 % 为只读归档', OLD.id USING ERRCODE = 'P0001';
    END IF;
    IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
    RETURN NEW;
END
$$;


--
-- Name: guard_purge_only(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.guard_purge_only() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF TG_OP = 'DELETE' AND current_setting('app.allow_purge', true) = 'on' THEN
        RETURN OLD;
    END IF;
    RAISE EXCEPTION '表 % 的记录需留痕保存，禁止 %', TG_TABLE_NAME, TG_OP USING ERRCODE = 'P0001';
END
$$;


--
-- Name: set_updated_at(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.set_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: ai_reports; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ai_reports (
    id bigint NOT NULL,
    submission_id bigint NOT NULL,
    report_no integer NOT NULL,
    trigger_type text NOT NULL,
    triggered_by bigint,
    job_id bigint,
    rule_version_id bigint NOT NULL,
    mode text NOT NULL,
    llm_model text,
    ocr_engine text,
    degrade_reason text,
    status text DEFAULT 'RUNNING'::text NOT NULL,
    material_versions jsonb DEFAULT '[]'::jsonb NOT NULL,
    changed_materials jsonb DEFAULT '[]'::jsonb NOT NULL,
    classification jsonb DEFAULT '[]'::jsonb NOT NULL,
    completeness jsonb DEFAULT '{}'::jsonb NOT NULL,
    timeline_snapshot jsonb DEFAULT '{}'::jsonb NOT NULL,
    rule_results jsonb DEFAULT '[]'::jsonb NOT NULL,
    summary jsonb DEFAULT '{}'::jsonb NOT NULL,
    recommendation text,
    recheck_of_report_id bigint,
    recheck_summary jsonb,
    error text,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    finished_at timestamp with time zone,
    duration_ms integer,
    handover_status text,
    effective_recommendation text,
    handover_reasons jsonb DEFAULT '[]'::jsonb NOT NULL,
    CONSTRAINT ai_reports_effective_recommendation_check CHECK (((effective_recommendation IS NULL) OR (effective_recommendation = ANY (ARRAY['SUGGEST_PASS'::text, 'SUGGEST_RETURN'::text, 'NEEDS_REVIEW'::text])))),
    CONSTRAINT ai_reports_handover_status_check CHECK (((handover_status IS NULL) OR (handover_status = ANY (ARRAY['NOT_REQUIRED'::text, 'REQUIRED'::text, 'DONE'::text])))),
    CONSTRAINT ai_reports_mode_check CHECK ((mode = ANY (ARRAY['RULE_ONLY'::text, 'RULE_LLM'::text]))),
    CONSTRAINT ai_reports_recommendation_check CHECK ((recommendation = ANY (ARRAY['SUGGEST_PASS'::text, 'SUGGEST_RETURN'::text, 'NEEDS_REVIEW'::text]))),
    CONSTRAINT ai_reports_status_check CHECK ((status = ANY (ARRAY['RUNNING'::text, 'DONE'::text, 'FAILED'::text]))),
    CONSTRAINT ai_reports_trigger_type_check CHECK ((trigger_type = ANY (ARRAY['SELF_CHECK'::text, 'REVIEW'::text, 'BATCH'::text, 'RECHECK'::text])))
);


--
-- Name: ai_reports_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.ai_reports ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.ai_reports_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: archive_time_nodes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.archive_time_nodes (
    id bigint NOT NULL,
    archive_id bigint NOT NULL,
    node_code text NOT NULL,
    value_date date,
    value_end_date date,
    hours real,
    seq_count integer DEFAULT 0 NOT NULL,
    source_extraction_id bigint,
    source_count integer DEFAULT 0 NOT NULL,
    has_conflict boolean DEFAULT false NOT NULL,
    corrected_date date,
    corrected_end_date date,
    corrected_hours real,
    correction_reason text,
    corrected_by bigint,
    corrected_at timestamp with time zone,
    locked boolean DEFAULT false NOT NULL,
    locked_stage smallint,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: archive_time_nodes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.archive_time_nodes ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.archive_time_nodes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: archives; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.archives (
    id bigint NOT NULL,
    student_user_id bigint NOT NULL,
    student_no text NOT NULL,
    real_name text NOT NULL,
    gender text,
    ethnicity text,
    birth_date date,
    native_place text,
    id_card_enc text,
    id_card_masked text,
    major text,
    class_name text,
    college_id bigint NOT NULL,
    branch_id bigint NOT NULL,
    batch_id bigint,
    current_stage smallint DEFAULT 1 NOT NULL,
    status text DEFAULT 'ACTIVE'::text NOT NULL,
    profile_extra jsonb DEFAULT '{}'::jsonb NOT NULL,
    anon_code text NOT NULL,
    data_source text DEFAULT 'MANUAL'::text NOT NULL,
    is_demo boolean DEFAULT false NOT NULL,
    timeline_updated_at timestamp with time zone,
    created_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT archives_data_source_check CHECK ((data_source = ANY (ARRAY['DEMO'::text, 'IMPORT'::text, 'MANUAL'::text]))),
    CONSTRAINT archives_gender_check CHECK ((gender = ANY (ARRAY['男'::text, '女'::text]))),
    CONSTRAINT archives_status_check CHECK ((status = ANY (ARRAY['ACTIVE'::text, 'COMPLETED'::text, 'SUSPENDED'::text])))
);


--
-- Name: archives_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.archives ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.archives_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_logs (
    id bigint NOT NULL,
    user_id bigint,
    username text,
    role text,
    action text NOT NULL,
    object_type text,
    object_id text,
    detail jsonb DEFAULT '{}'::jsonb NOT NULL,
    ip text,
    user_agent text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.audit_logs ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.audit_logs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: batch_upload_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.batch_upload_items (
    id bigint NOT NULL,
    job_id bigint NOT NULL,
    entry_path text NOT NULL,
    temp_path text,
    file_size bigint,
    parsed_student_no text,
    parsed_type_hint text,
    matched_archive_id bigint,
    match_method text,
    material_type_id bigint,
    status text DEFAULT 'UNMATCHED'::text NOT NULL,
    material_id bigint,
    error text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT batch_upload_items_match_method_check CHECK ((match_method = ANY (ARRAY['FILENAME'::text, 'DIRECTORY'::text, 'MANUAL'::text]))),
    CONSTRAINT batch_upload_items_status_check CHECK ((status = ANY (ARRAY['MATCHED'::text, 'UNMATCHED'::text, 'IMPORTED'::text, 'SKIPPED'::text, 'FAILED'::text])))
);


--
-- Name: batch_upload_items_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.batch_upload_items ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.batch_upload_items_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: batches; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.batches (
    id bigint NOT NULL,
    name text NOT NULL,
    year smallint NOT NULL,
    term text DEFAULT 'FULL_YEAR'::text NOT NULL,
    stage_codes jsonb DEFAULT '[1, 2, 3, 4, 5]'::jsonb NOT NULL,
    description text,
    start_date date NOT NULL,
    end_date date NOT NULL,
    self_deadline date,
    branch_deadline date,
    cross_deadline date,
    college_deadline date,
    org_deadline date,
    status text DEFAULT 'ACTIVE'::text NOT NULL,
    is_demo boolean DEFAULT false NOT NULL,
    created_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT batches_status_check CHECK ((status = ANY (ARRAY['ACTIVE'::text, 'CLOSED'::text]))),
    CONSTRAINT batches_term_check CHECK ((term = ANY (ARRAY['SPRING'::text, 'AUTUMN'::text, 'FULL_YEAR'::text]))),
    CONSTRAINT ck_batches_range CHECK ((end_date >= start_date))
);


--
-- Name: batches_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.batches ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.batches_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: check_rules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.check_rules (
    id bigint NOT NULL,
    code text NOT NULL,
    category text NOT NULL,
    name text NOT NULL,
    engine text NOT NULL,
    applies_to jsonb DEFAULT '[]'::jsonb NOT NULL,
    params jsonb DEFAULT '{}'::jsonb NOT NULL,
    severity text NOT NULL,
    needs_human_judgement boolean DEFAULT false NOT NULL,
    basis text,
    message_template text NOT NULL,
    suggestion_template_id bigint,
    is_optional boolean DEFAULT false NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    sort_order integer DEFAULT 0 NOT NULL,
    updated_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT check_rules_category_check CHECK ((category = ANY (ARRAY['FORMAT'::text, 'CONTENT'::text]))),
    CONSTRAINT check_rules_engine_check CHECK ((engine = ANY (ARRAY['RULE'::text, 'LLM'::text, 'RULE_LLM'::text]))),
    CONSTRAINT check_rules_severity_check CHECK ((severity = ANY (ARRAY['BLOCK'::text, 'WARN'::text, 'INFO'::text])))
);


--
-- Name: check_rules_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.check_rules ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.check_rules_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: checklist_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.checklist_items (
    id bigint NOT NULL,
    stage_code smallint NOT NULL,
    material_type_id bigint NOT NULL,
    quantity_mode text DEFAULT 'FIXED'::text NOT NULL,
    fixed_count integer DEFAULT 1 NOT NULL,
    period_months integer,
    period_start_node text,
    period_end_node text,
    is_required boolean DEFAULT true NOT NULL,
    requirement_text text,
    sort_order integer DEFAULT 0 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    updated_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT checklist_items_fixed_count_check CHECK ((fixed_count >= 0)),
    CONSTRAINT checklist_items_period_months_check CHECK (((period_months IS NULL) OR (period_months > 0))),
    CONSTRAINT checklist_items_quantity_mode_check CHECK ((quantity_mode = ANY (ARRAY['FIXED'::text, 'PER_PERIOD'::text]))),
    CONSTRAINT ck_checklist_period CHECK (((quantity_mode = 'FIXED'::text) OR ((period_months IS NOT NULL) AND (period_start_node IS NOT NULL))))
);


--
-- Name: checklist_items_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.checklist_items ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.checklist_items_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: cross_review_pairs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cross_review_pairs (
    id bigint NOT NULL,
    batch_id bigint NOT NULL,
    college_id bigint NOT NULL,
    target_branch_id bigint NOT NULL,
    reviewer_branch_id bigint NOT NULL,
    reviewer_user_id bigint,
    created_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_cross_pairs_not_self CHECK ((target_branch_id <> reviewer_branch_id))
);


--
-- Name: cross_review_pairs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.cross_review_pairs ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.cross_review_pairs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: export_files; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.export_files (
    id bigint NOT NULL,
    export_type text NOT NULL,
    params jsonb DEFAULT '{}'::jsonb NOT NULL,
    file_name text NOT NULL,
    stored_path text NOT NULL,
    row_count integer DEFAULT 0 NOT NULL,
    created_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone DEFAULT (now() + '7 days'::interval) NOT NULL,
    CONSTRAINT export_files_export_type_check CHECK ((export_type = ANY (ARRAY['DESENSITIZED_DATA'::text, 'STATS_REPORT'::text, 'AI_QUALITY'::text, 'RULES'::text])))
);


--
-- Name: export_files_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.export_files ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.export_files_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: handover_records; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.handover_records (
    id bigint NOT NULL,
    report_id bigint NOT NULL,
    submission_id bigint NOT NULL,
    assignee_id bigint,
    assignee_name text NOT NULL,
    assignee_role text NOT NULL,
    reason_codes jsonb DEFAULT '[]'::jsonb NOT NULL,
    handover_reason text,
    ai_recommendation text,
    human_decision text NOT NULL,
    effective_recommendation text NOT NULL,
    issue_ids jsonb DEFAULT '[]'::jsonb NOT NULL,
    material_ids jsonb DEFAULT '[]'::jsonb NOT NULL,
    confidence_snapshot jsonb DEFAULT '{}'::jsonb NOT NULL,
    decided_at timestamp with time zone DEFAULT now() NOT NULL,
    ip text,
    CONSTRAINT handover_records_human_decision_check CHECK ((human_decision = ANY (ARRAY['CONFIRM'::text, 'OVERRIDE_PASS'::text, 'OVERRIDE_RETURN'::text])))
);


--
-- Name: handover_records_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.handover_records ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.handover_records_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: issues; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.issues (
    id bigint NOT NULL,
    submission_id bigint NOT NULL,
    report_id bigint,
    material_id bigint,
    material_version_id bigint,
    source text NOT NULL,
    category text NOT NULL,
    severity text NOT NULL,
    rule_code text,
    rule_basis text,
    title text NOT NULL,
    description text NOT NULL,
    location jsonb DEFAULT '{}'::jsonb NOT NULL,
    actual_value text,
    expected_value text,
    suggestion text,
    suggestion_example text,
    needs_human_judgement boolean DEFAULT false NOT NULL,
    confidence real,
    fingerprint text,
    is_active boolean DEFAULT true NOT NULL,
    review_status text DEFAULT 'PENDING'::text NOT NULL,
    review_level text,
    reviewed_by bigint,
    reviewed_at timestamp with time zone,
    review_note text,
    original_snapshot jsonb,
    created_by bigint,
    created_level text,
    response_type text,
    response_text text,
    response_version_id bigint,
    responded_at timestamp with time zone,
    resolution text DEFAULT 'OPEN'::text NOT NULL,
    resolved_by_report_id bigint,
    prev_issue_id bigint,
    is_new_in_recheck boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_issues_manual CHECK (((source = 'MANUAL'::text) = (report_id IS NULL))),
    CONSTRAINT issues_category_check CHECK ((category = ANY (ARRAY['COMPLETENESS'::text, 'TIME'::text, 'FORMAT'::text, 'CONTENT'::text]))),
    CONSTRAINT issues_created_level_check CHECK ((created_level = ANY (ARRAY['BRANCH'::text, 'CROSS'::text, 'COLLEGE'::text, 'ORG'::text]))),
    CONSTRAINT issues_resolution_check CHECK ((resolution = ANY (ARRAY['OPEN'::text, 'RESOLVED'::text, 'UNRESOLVED'::text, 'WAIVED'::text]))),
    CONSTRAINT issues_response_type_check CHECK ((response_type = ANY (ARRAY['MODIFIED'::text, 'EXPLAINED'::text]))),
    CONSTRAINT issues_review_level_check CHECK ((review_level = ANY (ARRAY['BRANCH'::text, 'CROSS'::text, 'COLLEGE'::text, 'ORG'::text]))),
    CONSTRAINT issues_review_status_check CHECK ((review_status = ANY (ARRAY['PENDING'::text, 'CONFIRMED'::text, 'REJECTED'::text, 'MODIFIED'::text]))),
    CONSTRAINT issues_severity_check CHECK ((severity = ANY (ARRAY['BLOCK'::text, 'WARN'::text, 'INFO'::text]))),
    CONSTRAINT issues_source_check CHECK ((source = ANY (ARRAY['AI_RULE'::text, 'AI_LLM'::text, 'MANUAL'::text])))
);


--
-- Name: issues_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.issues ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.issues_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.jobs (
    id bigint NOT NULL,
    job_type text NOT NULL,
    status text DEFAULT 'QUEUED'::text NOT NULL,
    parent_id bigint,
    target_type text,
    target_id bigint,
    params jsonb DEFAULT '{}'::jsonb NOT NULL,
    total integer DEFAULT 1 NOT NULL,
    done_count integer DEFAULT 0 NOT NULL,
    failed_count integer DEFAULT 0 NOT NULL,
    progress integer DEFAULT 0 NOT NULL,
    stage_text text,
    result jsonb,
    error text,
    attempts integer DEFAULT 0 NOT NULL,
    max_attempts integer DEFAULT 3 NOT NULL,
    created_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    started_at timestamp with time zone,
    heartbeat_at timestamp with time zone,
    finished_at timestamp with time zone,
    CONSTRAINT jobs_job_type_check CHECK ((job_type = ANY (ARRAY['PARSE'::text, 'AI_CHECK'::text, 'BATCH_AI_CHECK'::text, 'BATCH_UPLOAD'::text, 'NOTICE_BATCH'::text, 'EXPORT'::text]))),
    CONSTRAINT jobs_progress_check CHECK (((progress >= 0) AND (progress <= 100))),
    CONSTRAINT jobs_status_check CHECK ((status = ANY (ARRAY['QUEUED'::text, 'RUNNING'::text, 'SUCCEEDED'::text, 'PARTIAL'::text, 'FAILED'::text, 'CANCELLED'::text])))
);


--
-- Name: jobs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.jobs ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.jobs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: material_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.material_types (
    id bigint NOT NULL,
    code text NOT NULL,
    name text NOT NULL,
    stage_codes jsonb DEFAULT '[]'::jsonb NOT NULL,
    title_keywords jsonb DEFAULT '[]'::jsonb NOT NULL,
    exclude_keywords jsonb DEFAULT '[]'::jsonb NOT NULL,
    element_template jsonb DEFAULT '[]'::jsonb NOT NULL,
    format_requirements jsonb DEFAULT '{}'::jsonb NOT NULL,
    date_node_map jsonb DEFAULT '{}'::jsonb NOT NULL,
    description text,
    is_active boolean DEFAULT true NOT NULL,
    sort_order integer DEFAULT 0 NOT NULL,
    updated_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: material_types_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.material_types ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.material_types_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: material_versions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.material_versions (
    id bigint NOT NULL,
    material_id bigint NOT NULL,
    version_no integer NOT NULL,
    original_filename text NOT NULL,
    stored_path text NOT NULL,
    file_ext text NOT NULL,
    mime_type text NOT NULL,
    file_size bigint NOT NULL,
    sha256 text NOT NULL,
    page_count integer,
    change_note text,
    parse_status text DEFAULT 'PENDING'::text NOT NULL,
    parse_error text,
    parsed_at timestamp with time zone,
    is_frozen boolean DEFAULT false NOT NULL,
    uploaded_by bigint,
    uploaded_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT material_versions_file_ext_check CHECK ((file_ext = ANY (ARRAY['pdf'::text, 'jpg'::text, 'jpeg'::text, 'png'::text, 'docx'::text]))),
    CONSTRAINT material_versions_file_size_check CHECK ((file_size > 0)),
    CONSTRAINT material_versions_parse_status_check CHECK ((parse_status = ANY (ARRAY['PENDING'::text, 'RUNNING'::text, 'DONE'::text, 'FAILED'::text]))),
    CONSTRAINT material_versions_version_no_check CHECK ((version_no >= 1))
);


--
-- Name: material_versions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.material_versions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.material_versions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: materials; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.materials (
    id bigint NOT NULL,
    archive_id bigint NOT NULL,
    submission_id bigint NOT NULL,
    stage_code smallint NOT NULL,
    title text NOT NULL,
    declared_type_id bigint,
    type_id bigint,
    type_source text,
    type_confidence real,
    type_status text DEFAULT 'PENDING'::text NOT NULL,
    current_version_id bigint,
    version_count integer DEFAULT 0 NOT NULL,
    status text DEFAULT 'ACTIVE'::text NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by bigint,
    uploaded_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT materials_status_check CHECK ((status = ANY (ARRAY['ACTIVE'::text, 'DELETED'::text]))),
    CONSTRAINT materials_type_confidence_check CHECK (((type_confidence IS NULL) OR ((type_confidence >= (0)::double precision) AND (type_confidence <= (1)::double precision)))),
    CONSTRAINT materials_type_source_check CHECK ((type_source = ANY (ARRAY['DECLARED'::text, 'AI'::text, 'MANUAL'::text]))),
    CONSTRAINT materials_type_status_check CHECK ((type_status = ANY (ARRAY['PENDING'::text, 'AUTO'::text, 'NEEDS_CONFIRM'::text, 'CONFIRMED'::text])))
);


--
-- Name: materials_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.materials ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.materials_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: messages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.messages (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    msg_type text NOT NULL,
    title text NOT NULL,
    content text DEFAULT ''::text NOT NULL,
    link_type text,
    link_id bigint,
    is_read boolean DEFAULT false NOT NULL,
    read_at timestamp with time zone,
    dedup_key text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT messages_msg_type_check CHECK ((msg_type = ANY (ARRAY['RETURNED'::text, 'RECTIFICATION'::text, 'COMPLETION'::text, 'PASSED'::text, 'FILED'::text, 'DEADLINE'::text, 'TASK'::text, 'JOB_DONE'::text, 'SYSTEM'::text])))
);


--
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.messages ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.messages_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: notices; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notices (
    id bigint NOT NULL,
    notice_type text NOT NULL,
    submission_id bigint NOT NULL,
    archive_id bigint NOT NULL,
    student_user_id bigint NOT NULL,
    report_id bigint,
    round_no integer DEFAULT 1 NOT NULL,
    title text NOT NULL,
    content jsonb NOT NULL,
    deadline date,
    status text DEFAULT 'DRAFT'::text NOT NULL,
    sent_at timestamp with time zone,
    created_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT notices_notice_type_check CHECK ((notice_type = ANY (ARRAY['COMPLETION'::text, 'RECTIFICATION'::text]))),
    CONSTRAINT notices_status_check CHECK ((status = ANY (ARRAY['DRAFT'::text, 'SENT'::text])))
);


--
-- Name: notices_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.notices ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.notices_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: orgs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.orgs (
    id bigint NOT NULL,
    parent_id bigint,
    org_type text NOT NULL,
    name text NOT NULL,
    code text,
    sort_order integer DEFAULT 0 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    is_demo boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_orgs_root CHECK (((org_type = 'SCHOOL'::text) = (parent_id IS NULL))),
    CONSTRAINT orgs_org_type_check CHECK ((org_type = ANY (ARRAY['SCHOOL'::text, 'COLLEGE'::text, 'BRANCH'::text])))
);


--
-- Name: orgs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.orgs ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.orgs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: parse_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.parse_results (
    id bigint NOT NULL,
    version_id bigint NOT NULL,
    parser text NOT NULL,
    ocr_engine text,
    preview_pdf_path text,
    full_text text DEFAULT ''::text NOT NULL,
    char_count integer DEFAULT 0 NOT NULL,
    pages jsonb DEFAULT '[]'::jsonb NOT NULL,
    visual_marks jsonb DEFAULT '{}'::jsonb NOT NULL,
    extracted_fields jsonb DEFAULT '{}'::jsonb NOT NULL,
    format_features jsonb DEFAULT '{}'::jsonb NOT NULL,
    warnings jsonb DEFAULT '[]'::jsonb NOT NULL,
    corrected_text text,
    corrected_fields jsonb,
    corrected_by bigint,
    corrected_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT parse_results_parser_check CHECK ((parser = ANY (ARRAY['PDF_TEXT'::text, 'DOCX'::text, 'OCR'::text, 'MIXED'::text, 'NONE'::text])))
);


--
-- Name: parse_results_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.parse_results ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.parse_results_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: political_terms; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.political_terms (
    id bigint NOT NULL,
    term_type text DEFAULT 'VARIANT'::text NOT NULL,
    standard_text text NOT NULL,
    wrong_variants jsonb DEFAULT '[]'::jsonb NOT NULL,
    sequence_items jsonb DEFAULT '[]'::jsonb NOT NULL,
    category text,
    severity text DEFAULT 'WARN'::text NOT NULL,
    note text,
    is_active boolean DEFAULT true NOT NULL,
    updated_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT political_terms_severity_check CHECK ((severity = ANY (ARRAY['BLOCK'::text, 'WARN'::text, 'INFO'::text]))),
    CONSTRAINT political_terms_term_type_check CHECK ((term_type = ANY (ARRAY['VARIANT'::text, 'SEQUENCE'::text])))
);


--
-- Name: political_terms_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.political_terms ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.political_terms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: prompt_templates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.prompt_templates (
    id bigint NOT NULL,
    code text NOT NULL,
    name text NOT NULL,
    system_prompt text NOT NULL,
    user_prompt text NOT NULL,
    output_schema jsonb DEFAULT '{}'::jsonb NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    updated_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: prompt_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.prompt_templates ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.prompt_templates_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: review_records; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.review_records (
    id bigint NOT NULL,
    submission_id bigint NOT NULL,
    level text NOT NULL,
    action text NOT NULL,
    from_status text NOT NULL,
    to_status text NOT NULL,
    reviewer_id bigint,
    reviewer_name text NOT NULL,
    reviewer_role text NOT NULL,
    comment text,
    report_id bigint,
    issue_ids jsonb DEFAULT '[]'::jsonb NOT NULL,
    round_no integer NOT NULL,
    is_batch boolean DEFAULT false NOT NULL,
    ip text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT review_records_action_check CHECK ((action = ANY (ARRAY['SUBMIT'::text, 'RESUBMIT'::text, 'PASS'::text, 'RETURN'::text, 'FILE'::text]))),
    CONSTRAINT review_records_level_check CHECK ((level = ANY (ARRAY['SELF'::text, 'BRANCH'::text, 'CROSS'::text, 'COLLEGE'::text, 'ORG'::text])))
);


--
-- Name: review_records_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.review_records ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.review_records_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: revoked_tokens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.revoked_tokens (
    jti text NOT NULL,
    user_id bigint NOT NULL,
    token_type text NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    revoked_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT revoked_tokens_token_type_check CHECK ((token_type = ANY (ARRAY['access'::text, 'refresh'::text])))
);


--
-- Name: rule_versions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rule_versions (
    id bigint NOT NULL,
    version_no integer NOT NULL,
    change_kind text NOT NULL,
    change_action text NOT NULL,
    change_object_id bigint,
    change_summary text NOT NULL,
    snapshot jsonb NOT NULL,
    created_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT rule_versions_change_action_check CHECK ((change_action = ANY (ARRAY['INIT'::text, 'CREATE'::text, 'UPDATE'::text, 'DELETE'::text, 'IMPORT'::text])))
);


--
-- Name: rule_versions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.rule_versions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.rule_versions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: schema_meta; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schema_meta (
    key text NOT NULL,
    value text NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: sensitive_phrases; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sensitive_phrases (
    id bigint NOT NULL,
    phrase text NOT NULL,
    match_type text DEFAULT 'KEYWORD'::text NOT NULL,
    category text NOT NULL,
    risk_level text DEFAULT 'MEDIUM'::text NOT NULL,
    risk_note text,
    suggestion text,
    is_active boolean DEFAULT true NOT NULL,
    updated_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT sensitive_phrases_category_check CHECK ((category = ANY (ARRAY['IDEOLOGY'::text, 'MOTIVATION'::text, 'OTHER'::text]))),
    CONSTRAINT sensitive_phrases_match_type_check CHECK ((match_type = ANY (ARRAY['KEYWORD'::text, 'REGEX'::text]))),
    CONSTRAINT sensitive_phrases_risk_level_check CHECK ((risk_level = ANY (ARRAY['HIGH'::text, 'MEDIUM'::text, 'LOW'::text])))
);


--
-- Name: sensitive_phrases_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.sensitive_phrases ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.sensitive_phrases_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: stages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stages (
    code smallint NOT NULL,
    stage_key text NOT NULL,
    name text NOT NULL,
    sort_order smallint NOT NULL,
    CONSTRAINT stages_code_check CHECK (((code >= 1) AND (code <= 5)))
);


--
-- Name: submissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.submissions (
    id bigint NOT NULL,
    archive_id bigint NOT NULL,
    stage_code smallint NOT NULL,
    batch_id bigint,
    college_id bigint NOT NULL,
    branch_id bigint NOT NULL,
    status text DEFAULT 'DRAFT'::text NOT NULL,
    return_level text,
    round_no integer DEFAULT 1 NOT NULL,
    latest_report_id bigint,
    ai_status text DEFAULT 'NONE'::text NOT NULL,
    ai_job_id bigint,
    submitted_at timestamp with time zone,
    level_entered_at timestamp with time zone,
    filed_at timestamp with time zone,
    filed_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_submissions_return CHECK (((status = 'RETURNED'::text) = (return_level IS NOT NULL))),
    CONSTRAINT submissions_ai_status_check CHECK ((ai_status = ANY (ARRAY['NONE'::text, 'QUEUED'::text, 'RUNNING'::text, 'DONE'::text, 'FAILED'::text]))),
    CONSTRAINT submissions_return_level_check CHECK ((return_level = ANY (ARRAY['BRANCH'::text, 'CROSS'::text, 'COLLEGE'::text, 'ORG'::text]))),
    CONSTRAINT submissions_round_no_check CHECK ((round_no >= 1)),
    CONSTRAINT submissions_status_check CHECK ((status = ANY (ARRAY['DRAFT'::text, 'BRANCH_REVIEW'::text, 'CROSS_REVIEW'::text, 'COLLEGE_REVIEW'::text, 'ORG_FILING'::text, 'FILED'::text, 'RETURNED'::text])))
);


--
-- Name: submissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.submissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.submissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: suggestion_templates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.suggestion_templates (
    id bigint NOT NULL,
    code text NOT NULL,
    rule_code text,
    title text NOT NULL,
    template_text text NOT NULL,
    example_text text,
    is_active boolean DEFAULT true NOT NULL,
    updated_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: suggestion_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.suggestion_templates ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.suggestion_templates_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: system_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.system_settings (
    key text NOT NULL,
    value jsonb NOT NULL,
    description text,
    updated_by bigint,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: time_node_defs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.time_node_defs (
    id bigint NOT NULL,
    code text NOT NULL,
    name text NOT NULL,
    value_kind text NOT NULL,
    has_hours boolean DEFAULT false NOT NULL,
    stage_code smallint,
    required_from_stage smallint,
    source_material_codes jsonb DEFAULT '[]'::jsonb NOT NULL,
    extract_keywords jsonb DEFAULT '[]'::jsonb NOT NULL,
    derive_expr jsonb,
    sort_order integer DEFAULT 0 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    updated_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_node_derived CHECK (((value_kind = 'DERIVED'::text) = (derive_expr IS NOT NULL))),
    CONSTRAINT time_node_defs_value_kind_check CHECK ((value_kind = ANY (ARRAY['DATE'::text, 'DATE_RANGE'::text, 'DATE_SEQ'::text, 'DERIVED'::text])))
);


--
-- Name: time_node_defs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.time_node_defs ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.time_node_defs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: time_node_extractions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.time_node_extractions (
    id bigint NOT NULL,
    archive_id bigint NOT NULL,
    node_code text NOT NULL,
    material_id bigint,
    material_version_id bigint,
    seq_index integer DEFAULT 0 NOT NULL,
    value_date date,
    value_end_date date,
    hours real,
    raw_text text,
    invalid_reason text,
    page_no integer,
    bbox jsonb,
    confidence real,
    method text NOT NULL,
    is_current boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_extraction_source CHECK (((method = ANY (ARRAY['IMPORT'::text, 'MANUAL'::text])) OR (material_version_id IS NOT NULL))),
    CONSTRAINT time_node_extractions_method_check CHECK ((method = ANY (ARRAY['RULE'::text, 'LLM'::text, 'IMPORT'::text, 'MANUAL'::text])))
);


--
-- Name: time_node_extractions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.time_node_extractions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.time_node_extractions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: time_rules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.time_rules (
    id bigint NOT NULL,
    code text NOT NULL,
    name text NOT NULL,
    rule_type text NOT NULL,
    params jsonb DEFAULT '{"checks": []}'::jsonb NOT NULL,
    applies_stages jsonb DEFAULT '[]'::jsonb NOT NULL,
    severity text NOT NULL,
    basis text,
    message_template text NOT NULL,
    suggestion_template_id bigint,
    is_active boolean DEFAULT true NOT NULL,
    sort_order integer DEFAULT 0 NOT NULL,
    updated_by bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT time_rules_rule_type_check CHECK ((rule_type = ANY (ARRAY['AGE'::text, 'INTERVAL'::text, 'ORDER'::text, 'SEQ_GAP'::text, 'SEQ_COUNT'::text, 'DURATION'::text, 'DERIVED'::text, 'CONSISTENCY'::text, 'VALID_DATE'::text, 'REQUIRED_NODES'::text, 'IN_RANGE'::text, 'COMPOSITE'::text]))),
    CONSTRAINT time_rules_severity_check CHECK ((severity = ANY (ARRAY['BLOCK'::text, 'WARN'::text, 'INFO'::text, 'CALC'::text])))
);


--
-- Name: time_rules_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.time_rules ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.time_rules_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_roles (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    role text NOT NULL,
    org_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT user_roles_role_check CHECK ((role = ANY (ARRAY['STUDENT'::text, 'BRANCH_REVIEWER'::text, 'CROSS_REVIEWER'::text, 'COLLEGE_REVIEWER'::text, 'ORG_ADMIN'::text, 'SYS_ADMIN'::text])))
);


--
-- Name: user_roles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.user_roles ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.user_roles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    username text NOT NULL,
    password_hash text NOT NULL,
    real_name text NOT NULL,
    gender text,
    org_id bigint,
    email text,
    phone_enc text,
    phone_masked text,
    is_active boolean DEFAULT true NOT NULL,
    must_change_password boolean DEFAULT true NOT NULL,
    failed_login_count integer DEFAULT 0 NOT NULL,
    locked_until timestamp with time zone,
    token_version integer DEFAULT 0 NOT NULL,
    last_login_at timestamp with time zone,
    last_login_ip text,
    is_demo boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT users_gender_check CHECK ((gender = ANY (ARRAY['男'::text, '女'::text])))
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.users ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Data for Name: ai_reports; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ai_reports (id, submission_id, report_no, trigger_type, triggered_by, job_id, rule_version_id, mode, llm_model, ocr_engine, degrade_reason, status, material_versions, changed_materials, classification, completeness, timeline_snapshot, rule_results, summary, recommendation, recheck_of_report_id, recheck_summary, error, started_at, finished_at, duration_ms, handover_status, effective_recommendation, handover_reasons) FROM stdin;
1	3	1	REVIEW	1	7	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 1, "version_no": 1, "material_id": 1}, {"version_id": 2, "version_no": 1, "material_id": 2}, {"version_id": 3, "version_no": 1, "material_id": 3}, {"version_id": 4, "version_no": 1, "material_id": 4}, {"version_id": 5, "version_no": 1, "material_id": 5}, {"version_id": 6, "version_no": 1, "material_id": 6}]	[]	{"counts": [{"count": 1, "type_code": "APPLICATION_LETTER", "type_name": "入党申请书"}, {"count": 3, "type_code": "THOUGHT_REPORT", "type_name": "思想汇报"}, {"count": 1, "type_code": "CANDIDATE_MEETING_RECORD", "type_name": "支委会确定发展对象记录"}, {"count": 1, "type_code": "AUTOBIOGRAPHY", "type_name": "自传"}], "materials": [{"title": "入党申请书", "status": "AUTO", "type_code": "APPLICATION_LETTER", "confidence": 1.0, "material_id": 1, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 2, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 3, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 4, "type_source": "DECLARED"}, {"title": "支委会确定发展对象记录", "status": "AUTO", "type_code": "CANDIDATE_MEETING_RECORD", "confidence": 1.0, "material_id": 5, "type_source": "DECLARED"}, {"title": "自传", "status": "AUTO", "type_code": "AUTOBIOGRAPHY", "confidence": 1.0, "material_id": 6, "type_source": "DECLARED"}]}	{"extra": [{"title": "入党申请书", "reason": "不在本阶段清单", "material_id": 1}], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [6], "material_type": {"id": 9, "code": "AUTOBIOGRAPHY", "name": "自传"}, "quantity_mode": "FIXED", "requirement_text": "自传", "checklist_item_id": 9, "material_type_name": "自传"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [5], "material_type": {"id": 10, "code": "CANDIDATE_MEETING_RECORD", "name": "支委会确定发展对象记录"}, "quantity_mode": "FIXED", "requirement_text": "支委会确定发展对象记录", "checklist_item_id": 10, "material_type_name": "支委会确定发展对象记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 11, "code": "POLITICAL_REVIEW", "name": "政治审查材料"}, "quantity_mode": "FIXED", "requirement_text": "政治审查材料", "checklist_item_id": 11, "material_type_name": "政治审查材料"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 12, "code": "TRAINING_CERT", "name": "集中培训结业证书"}, "quantity_mode": "FIXED", "requirement_text": "集中培训结业证书", "checklist_item_id": 12, "material_type_name": "集中培训结业证书"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 13, "code": "RECORD_BOOK_CANDIDATE", "name": "写实簿·发展对象考察部分"}, "quantity_mode": "FIXED", "requirement_text": "写实簿发展对象考察部分", "checklist_item_id": 13, "material_type_name": "写实簿·发展对象考察部分"}, {"actual": 3, "missing": 2, "expected": 5, "required": true, "material_ids": [2, 3, 4], "material_type": {"id": 7, "code": "THOUGHT_REPORT", "name": "思想汇报"}, "quantity_mode": "PER_PERIOD", "requirement_text": "每季度至少一份思想汇报", "checklist_item_id": 14, "material_type_name": "思想汇报"}], "stage_code": 3, "is_complete": false, "unclassified": [], "missing_total": 5}	{"nodes": {"D01": null, "T01": "2003-05-12", "T02": "2023-03-15", "T03": "2023-03-20", "T04": "2024-09-10", "T05": null, "T06": "2003-05-12", "T07": null, "T08": "2025-08-30", "T09": null, "T10": null, "T11": null, "T12": null, "T13": null, "T14": null, "T15": null, "T16": null, "T17": null, "T18": null, "T19": null, "T20": null, "T21": null}, "derived": {}}	[{"result": "FAIL", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"result": "PASS", "rule_code": "R-T01"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T02"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T05"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T06"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T07"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T08"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T09"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T10"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T11"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T12"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T14"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T15"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T16"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T17"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T18"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T19"}, {"result": "PASS", "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "PASS", "rule_code": "R-T22"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "PASS", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "FAIL", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "FAIL", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "PASS", "rule_code": "R-C04"}, {"result": "FAIL", "rule_code": "R-C05"}, {"result": "FAIL", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 20, "rules_run": 39, "by_category": {"TIME": 5, "FORMAT": 6, "CONTENT": 5, "COMPLETENESS": 4}, "by_severity": {"WARN": 12, "BLOCK": 8}, "rules_failed": 11, "rules_skipped": 18, "needs_judgement": 0, "materials_checked": 6}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:36:16.171885+08	2026-10-17 18:36:16.251443+08	79	REQUIRED	\N	["LOW_CONFIDENCE", "KEY_STAGE"]
2	6	1	REVIEW	1	11	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 7, "version_no": 1, "material_id": 7}, {"version_id": 8, "version_no": 1, "material_id": 8}, {"version_id": 9, "version_no": 1, "material_id": 9}]	[]	{"counts": [{"count": 1, "type_code": "APPLICATION_LETTER", "type_name": "入党申请书"}, {"count": 1, "type_code": "AUTOBIOGRAPHY", "type_name": "自传"}, {"count": 1, "type_code": "THOUGHT_REPORT", "type_name": "思想汇报"}], "materials": [{"title": "入党申请书", "status": "AUTO", "type_code": "APPLICATION_LETTER", "confidence": 1.0, "material_id": 7, "type_source": "DECLARED"}, {"title": "自传", "status": "AUTO", "type_code": "AUTOBIOGRAPHY", "confidence": 1.0, "material_id": 8, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 9, "type_source": "DECLARED"}]}	{"extra": [{"title": "入党申请书", "reason": "不在本阶段清单", "material_id": 7}], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [8], "material_type": {"id": 9, "code": "AUTOBIOGRAPHY", "name": "自传"}, "quantity_mode": "FIXED", "requirement_text": "自传", "checklist_item_id": 9, "material_type_name": "自传"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 10, "code": "CANDIDATE_MEETING_RECORD", "name": "支委会确定发展对象记录"}, "quantity_mode": "FIXED", "requirement_text": "支委会确定发展对象记录", "checklist_item_id": 10, "material_type_name": "支委会确定发展对象记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 11, "code": "POLITICAL_REVIEW", "name": "政治审查材料"}, "quantity_mode": "FIXED", "requirement_text": "政治审查材料", "checklist_item_id": 11, "material_type_name": "政治审查材料"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 12, "code": "TRAINING_CERT", "name": "集中培训结业证书"}, "quantity_mode": "FIXED", "requirement_text": "集中培训结业证书", "checklist_item_id": 12, "material_type_name": "集中培训结业证书"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 13, "code": "RECORD_BOOK_CANDIDATE", "name": "写实簿·发展对象考察部分"}, "quantity_mode": "FIXED", "requirement_text": "写实簿发展对象考察部分", "checklist_item_id": 13, "material_type_name": "写实簿·发展对象考察部分"}, {"actual": 1, "missing": 4, "expected": 5, "required": true, "material_ids": [9], "material_type": {"id": 7, "code": "THOUGHT_REPORT", "name": "思想汇报"}, "quantity_mode": "PER_PERIOD", "requirement_text": "每季度至少一份思想汇报", "checklist_item_id": 14, "material_type_name": "思想汇报"}], "stage_code": 3, "is_complete": false, "unclassified": [], "missing_total": 8}	{"nodes": {"D01": null, "T01": "2003-05-12", "T02": "2023-03-15", "T03": null, "T04": "2024-09-10", "T05": null, "T06": "2004-01-01", "T07": null, "T08": "2025-08-30", "T09": null, "T10": null, "T11": null, "T12": null, "T13": null, "T14": null, "T15": null, "T16": null, "T17": null, "T18": null, "T19": null, "T20": null, "T21": null}, "derived": {}}	[{"result": "FAIL", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"result": "PASS", "rule_code": "R-T01"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T02"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T05"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T06"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T07"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T08"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T09"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T10"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T11"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T12"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T14"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T15"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T16"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T17"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T18"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T19"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "PASS", "rule_code": "R-T22"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "PASS", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "FAIL", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "FAIL", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "FAIL", "rule_code": "R-C04"}, {"result": "FAIL", "rule_code": "R-C05"}, {"result": "FAIL", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 21, "rules_run": 39, "by_category": {"TIME": 6, "FORMAT": 3, "CONTENT": 7, "COMPLETENESS": 5}, "by_severity": {"WARN": 10, "BLOCK": 11}, "rules_failed": 13, "rules_skipped": 18, "needs_judgement": 2, "materials_checked": 3}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:36:16.338466+08	2026-10-17 18:36:16.386749+08	48	REQUIRED	\N	["LOW_CONFIDENCE", "MATERIAL_CONFLICT", "NEEDS_JUDGEMENT", "KEY_STAGE"]
3	12	1	REVIEW	1	19	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 11, "version_no": 1, "material_id": 11}, {"version_id": 12, "version_no": 1, "material_id": 12}, {"version_id": 13, "version_no": 1, "material_id": 13}, {"version_id": 14, "version_no": 1, "material_id": 14}, {"version_id": 15, "version_no": 1, "material_id": 15}, {"version_id": 16, "version_no": 1, "material_id": 16}]	[]	{"counts": [{"count": 1, "type_code": "APPLICATION_FORM", "type_name": "入党志愿书"}, {"count": 1, "type_code": "ADMISSION_MEETING_RECORD", "type_name": "支部大会讨论接收记录"}, {"count": 1, "type_code": "POLITICAL_REVIEW", "type_name": "政治审查材料"}, {"count": 1, "type_code": "TRAINING_CERT", "type_name": "集中培训结业证书"}, {"count": 1, "type_code": "CANDIDATE_PUBLICITY", "type_name": "发展对象公示材料"}, {"count": 1, "type_code": "PRE_REVIEW_OPINION", "type_name": "上级党委预审意见"}], "materials": [{"title": "入党志愿书", "status": "AUTO", "type_code": "APPLICATION_FORM", "confidence": 1.0, "material_id": 11, "type_source": "DECLARED"}, {"title": "支部大会讨论接收记录", "status": "AUTO", "type_code": "ADMISSION_MEETING_RECORD", "confidence": 1.0, "material_id": 12, "type_source": "DECLARED"}, {"title": "政治审查材料", "status": "AUTO", "type_code": "POLITICAL_REVIEW", "confidence": 1.0, "material_id": 13, "type_source": "DECLARED"}, {"title": "集中培训结业证书", "status": "AUTO", "type_code": "TRAINING_CERT", "confidence": 1.0, "material_id": 14, "type_source": "DECLARED"}, {"title": "发展对象公示材料", "status": "AUTO", "type_code": "CANDIDATE_PUBLICITY", "confidence": 1.0, "material_id": 15, "type_source": "DECLARED"}, {"title": "上级党委预审意见", "status": "AUTO", "type_code": "PRE_REVIEW_OPINION", "confidence": 1.0, "material_id": 16, "type_source": "DECLARED"}]}	{"extra": [{"title": "政治审查材料", "reason": "不在本阶段清单", "material_id": 13}, {"title": "集中培训结业证书", "reason": "不在本阶段清单", "material_id": 14}], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [15], "material_type": {"id": 14, "code": "CANDIDATE_PUBLICITY", "name": "发展对象公示材料"}, "quantity_mode": "FIXED", "requirement_text": "发展对象公示材料", "checklist_item_id": 15, "material_type_name": "发展对象公示材料"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [16], "material_type": {"id": 15, "code": "PRE_REVIEW_OPINION", "name": "上级党委预审意见"}, "quantity_mode": "FIXED", "requirement_text": "上级党委预审意见", "checklist_item_id": 16, "material_type_name": "上级党委预审意见"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [11], "material_type": {"id": 16, "code": "APPLICATION_FORM", "name": "入党志愿书"}, "quantity_mode": "FIXED", "requirement_text": "入党志愿书", "checklist_item_id": 17, "material_type_name": "入党志愿书"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [12], "material_type": {"id": 17, "code": "ADMISSION_MEETING_RECORD", "name": "支部大会讨论接收记录"}, "quantity_mode": "FIXED", "requirement_text": "支部大会讨论接收预备党员记录", "checklist_item_id": 18, "material_type_name": "支部大会讨论接收记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 18, "code": "COMMITTEE_TALK_RECORD", "name": "上级党委派人谈话记录"}, "quantity_mode": "FIXED", "requirement_text": "上级党委派人谈话记录", "checklist_item_id": 19, "material_type_name": "上级党委派人谈话记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 19, "code": "ADMISSION_APPROVAL", "name": "上级党委审批意见"}, "quantity_mode": "FIXED", "requirement_text": "上级党委审批意见", "checklist_item_id": 20, "material_type_name": "上级党委审批意见"}], "stage_code": 4, "is_complete": false, "unclassified": [], "missing_total": 2}	{"nodes": {"D01": "2026-06-01", "T01": "2003-05-12", "T02": "2022-03-15", "T03": null, "T04": "2023-04-01", "T05": null, "T06": "2024-06-01", "T07": null, "T08": "2024-05-01", "T09": "2024-06-01", "T10": "2024-07-01", "T11": null, "T12": "2025-05-10", "T13": "2025-05-20", "T14": "2025-06-01", "T15": null, "T16": "2025-06-01", "T17": null, "T18": null, "T19": "2025-04-20", "T20": "2025-06-01", "T21": null}, "derived": {"D01": "2026-06-01"}}	[{"result": "FAIL", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"result": "PASS", "rule_code": "R-T01"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T02"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"result": "PASS", "rule_code": "R-T05"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T06"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T07"}, {"result": "PASS", "rule_code": "R-T08"}, {"result": "PASS", "rule_code": "R-T09"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T10"}, {"result": "PASS", "rule_code": "R-T11"}, {"result": "PASS", "rule_code": "R-T12"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T14"}, {"result": "PASS", "rule_code": "R-T15"}, {"result": "PASS", "derived": {"D01": "2026-06-01"}, "rule_code": "R-T16"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T17"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T18"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T19"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T22"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "FAIL", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "PASS", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "PASS", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "PASS", "rule_code": "R-C04"}, {"result": "PASS", "rule_code": "R-C05"}, {"result": "FAIL", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 13, "rules_run": 39, "by_category": {"TIME": 3, "FORMAT": 7, "CONTENT": 1, "COMPLETENESS": 2}, "by_severity": {"WARN": 6, "BLOCK": 7}, "rules_failed": 7, "rules_skipped": 15, "needs_judgement": 0, "materials_checked": 6}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:36:16.646203+08	2026-10-17 18:36:16.683266+08	37	REQUIRED	\N	["LOW_CONFIDENCE", "MATERIAL_CONFLICT", "KEY_STAGE"]
4	17	1	REVIEW	1	23	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 17, "version_no": 1, "material_id": 17}, {"version_id": 18, "version_no": 1, "material_id": 18}, {"version_id": 19, "version_no": 1, "material_id": 19}]	[]	{"counts": [{"count": 1, "type_code": "REGULARIZATION_LETTER", "type_name": "转正申请书"}, {"count": 1, "type_code": "REGULARIZATION_MEETING_RECORD", "type_name": "支部大会讨论转正记录"}, {"count": 1, "type_code": "REGULARIZATION_PUBLICITY", "type_name": "转正公示材料"}], "materials": [{"title": "转正申请书", "status": "AUTO", "type_code": "REGULARIZATION_LETTER", "confidence": 1.0, "material_id": 17, "type_source": "DECLARED"}, {"title": "支部大会讨论转正记录", "status": "AUTO", "type_code": "REGULARIZATION_MEETING_RECORD", "confidence": 1.0, "material_id": 18, "type_source": "DECLARED"}, {"title": "转正公示材料", "status": "AUTO", "type_code": "REGULARIZATION_PUBLICITY", "confidence": 1.0, "material_id": 19, "type_source": "DECLARED"}]}	{"extra": [], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [17], "material_type": {"id": 20, "code": "REGULARIZATION_LETTER", "name": "转正申请书"}, "quantity_mode": "FIXED", "requirement_text": "转正申请书", "checklist_item_id": 21, "material_type_name": "转正申请书"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 21, "code": "RECORD_BOOK_PROBATIONARY", "name": "写实簿·预备党员考察部分"}, "quantity_mode": "FIXED", "requirement_text": "写实簿预备党员考察部分", "checklist_item_id": 22, "material_type_name": "写实簿·预备党员考察部分"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [19], "material_type": {"id": 22, "code": "REGULARIZATION_PUBLICITY", "name": "转正公示材料"}, "quantity_mode": "FIXED", "requirement_text": "转正公示材料", "checklist_item_id": 23, "material_type_name": "转正公示材料"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [18], "material_type": {"id": 23, "code": "REGULARIZATION_MEETING_RECORD", "name": "支部大会讨论转正记录"}, "quantity_mode": "FIXED", "requirement_text": "支部大会讨论转正记录", "checklist_item_id": 24, "material_type_name": "支部大会讨论转正记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 24, "code": "REGULARIZATION_APPROVAL", "name": "上级党委审批转正意见"}, "quantity_mode": "FIXED", "requirement_text": "上级党委审批转正意见", "checklist_item_id": 25, "material_type_name": "上级党委审批转正意见"}, {"actual": 0, "missing": 4, "expected": 4, "required": true, "material_ids": [], "material_type": {"id": 7, "code": "THOUGHT_REPORT", "name": "思想汇报"}, "quantity_mode": "PER_PERIOD", "requirement_text": "预备期每季度至少一份思想汇报", "checklist_item_id": 26, "material_type_name": "思想汇报"}], "stage_code": 5, "is_complete": false, "unclassified": [], "missing_total": 6}	{"nodes": {"D01": "2025-10-01", "T01": null, "T02": null, "T03": null, "T04": null, "T05": null, "T06": "2025-09-20", "T07": null, "T08": null, "T09": null, "T10": null, "T11": "2025-09-25", "T12": null, "T13": null, "T14": "2024-10-01", "T15": null, "T16": "2024-10-20", "T17": null, "T18": "2025-09-20", "T19": null, "T20": "2025-10-08", "T21": null}, "derived": {"D01": "2025-10-01"}}	[{"result": "FAIL", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T01"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T02"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T05"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T06"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T07"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T08"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T09"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T10"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T11"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T12"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T14"}, {"result": "PASS", "rule_code": "R-T15"}, {"result": "PASS", "derived": {"D01": "2025-10-01"}, "rule_code": "R-T16"}, {"result": "PASS", "rule_code": "R-T17"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T18"}, {"result": "PASS", "rule_code": "R-T19"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T22"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "PASS", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "PASS", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "PASS", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "PASS", "rule_code": "R-C04"}, {"result": "FAIL", "rule_code": "R-C05"}, {"result": "PASS", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 10, "rules_run": 39, "by_category": {"TIME": 3, "FORMAT": 3, "CONTENT": 1, "COMPLETENESS": 3}, "by_severity": {"WARN": 4, "BLOCK": 6}, "rules_failed": 6, "rules_skipped": 19, "needs_judgement": 0, "materials_checked": 3}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:36:16.786994+08	2026-10-17 18:36:16.819121+08	32	REQUIRED	\N	["LOW_CONFIDENCE", "MATERIAL_CONFLICT", "KEY_STAGE"]
5	18	1	REVIEW	1	26	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 20, "version_no": 1, "material_id": 20}, {"version_id": 21, "version_no": 1, "material_id": 21}]	[]	{"counts": [{"count": 1, "type_code": "APPLICATION_LETTER", "type_name": "入党申请书"}, {"count": 1, "type_code": "PARTY_TALK_RECORD", "type_name": "党组织派人谈话记录"}], "materials": [{"title": "入党申请书", "status": "AUTO", "type_code": "APPLICATION_LETTER", "confidence": 1.0, "material_id": 20, "type_source": "DECLARED"}, {"title": "党组织派人谈话记录", "status": "AUTO", "type_code": "PARTY_TALK_RECORD", "confidence": 1.0, "material_id": 21, "type_source": "DECLARED"}]}	{"extra": [], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [20], "material_type": {"id": 1, "code": "APPLICATION_LETTER", "name": "入党申请书"}, "quantity_mode": "FIXED", "requirement_text": "本人亲笔或打印后签字的入党申请书", "checklist_item_id": 1, "material_type_name": "入党申请书"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [21], "material_type": {"id": 2, "code": "PARTY_TALK_RECORD", "name": "党组织派人谈话记录"}, "quantity_mode": "FIXED", "requirement_text": "党组织派人谈话记录", "checklist_item_id": 2, "material_type_name": "党组织派人谈话记录"}], "stage_code": 1, "is_complete": true, "unclassified": [], "missing_total": 0}	{"nodes": {"D01": null, "T01": "2003-05-12", "T02": "2023-03-15", "T03": "2023-03-28", "T04": null, "T05": null, "T06": "2023-03-15", "T07": null, "T08": null, "T09": null, "T10": null, "T11": null, "T12": null, "T13": null, "T14": null, "T15": "2023-03-28", "T16": null, "T17": null, "T18": null, "T19": null, "T20": null, "T21": null}, "derived": {}}	[{"result": "PASS", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"result": "PASS", "rule_code": "R-T01"}, {"result": "PASS", "rule_code": "R-T02"}, {"result": "PASS", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T05"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T06"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T07"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T08"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T09"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T10"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T11"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T12"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T14"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T15"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T16"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T17"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T18"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T19"}, {"result": "PASS", "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "PASS", "rule_code": "R-T22"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "FAIL", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "PASS", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "FAIL", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "PASS", "rule_code": "R-C04"}, {"result": "PASS", "rule_code": "R-C05"}, {"result": "FAIL", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 5, "rules_run": 39, "by_category": {"TIME": 1, "FORMAT": 2, "CONTENT": 2}, "by_severity": {"WARN": 2, "BLOCK": 3}, "rules_failed": 5, "rules_skipped": 20, "needs_judgement": 0, "materials_checked": 2}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:36:16.88347+08	2026-10-17 18:36:16.913592+08	30	REQUIRED	\N	["LOW_CONFIDENCE", "KEY_STAGE"]
15	54	1	REVIEW	1	78	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 62, "version_no": 1, "material_id": 62}, {"version_id": 63, "version_no": 1, "material_id": 63}]	[]	{"counts": [{"count": 1, "type_code": "APPLICATION_LETTER", "type_name": "入党申请书"}, {"count": 1, "type_code": "PARTY_TALK_RECORD", "type_name": "党组织派人谈话记录"}], "materials": [{"title": "入党申请书", "status": "AUTO", "type_code": "APPLICATION_LETTER", "confidence": 1.0, "material_id": 62, "type_source": "DECLARED"}, {"title": "党组织派人谈话记录", "status": "AUTO", "type_code": "PARTY_TALK_RECORD", "confidence": 1.0, "material_id": 63, "type_source": "DECLARED"}]}	{"extra": [], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [62], "material_type": {"id": 1, "code": "APPLICATION_LETTER", "name": "入党申请书"}, "quantity_mode": "FIXED", "requirement_text": "本人亲笔或打印后签字的入党申请书", "checklist_item_id": 1, "material_type_name": "入党申请书"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [63], "material_type": {"id": 2, "code": "PARTY_TALK_RECORD", "name": "党组织派人谈话记录"}, "quantity_mode": "FIXED", "requirement_text": "党组织派人谈话记录", "checklist_item_id": 2, "material_type_name": "党组织派人谈话记录"}], "stage_code": 1, "is_complete": true, "unclassified": [], "missing_total": 0}	{"nodes": {"D01": null, "T01": "2003-05-12", "T02": "2023-03-15", "T03": "2023-03-28", "T04": null, "T05": null, "T06": "2023-03-15", "T07": null, "T08": null, "T09": null, "T10": null, "T11": null, "T12": null, "T13": null, "T14": null, "T15": "2023-03-28", "T16": null, "T17": null, "T18": null, "T19": null, "T20": null, "T21": null}, "derived": {}}	[{"result": "PASS", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"result": "PASS", "rule_code": "R-T01"}, {"result": "PASS", "rule_code": "R-T02"}, {"result": "PASS", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T05"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T06"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T07"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T08"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T09"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T10"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T11"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T12"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T14"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T15"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T16"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T17"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T18"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T19"}, {"result": "PASS", "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "PASS", "rule_code": "R-T22"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "FAIL", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "PASS", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "FAIL", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "PASS", "rule_code": "R-C04"}, {"result": "PASS", "rule_code": "R-C05"}, {"result": "FAIL", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 5, "rules_run": 39, "by_category": {"TIME": 1, "FORMAT": 2, "CONTENT": 2}, "by_severity": {"WARN": 2, "BLOCK": 3}, "rules_failed": 5, "rules_skipped": 20, "needs_judgement": 0, "materials_checked": 2}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:36:18.84329+08	2026-10-17 18:36:18.876813+08	33	REQUIRED	\N	["LOW_CONFIDENCE", "KEY_STAGE"]
20	72	1	REVIEW	1	104	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 83, "version_no": 1, "material_id": 83}, {"version_id": 84, "version_no": 1, "material_id": 84}]	[]	{"counts": [{"count": 1, "type_code": "APPLICATION_LETTER", "type_name": "入党申请书"}, {"count": 1, "type_code": "PARTY_TALK_RECORD", "type_name": "党组织派人谈话记录"}], "materials": [{"title": "入党申请书", "status": "AUTO", "type_code": "APPLICATION_LETTER", "confidence": 1.0, "material_id": 83, "type_source": "DECLARED"}, {"title": "党组织派人谈话记录", "status": "AUTO", "type_code": "PARTY_TALK_RECORD", "confidence": 1.0, "material_id": 84, "type_source": "DECLARED"}]}	{"extra": [], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [83], "material_type": {"id": 1, "code": "APPLICATION_LETTER", "name": "入党申请书"}, "quantity_mode": "FIXED", "requirement_text": "本人亲笔或打印后签字的入党申请书", "checklist_item_id": 1, "material_type_name": "入党申请书"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [84], "material_type": {"id": 2, "code": "PARTY_TALK_RECORD", "name": "党组织派人谈话记录"}, "quantity_mode": "FIXED", "requirement_text": "党组织派人谈话记录", "checklist_item_id": 2, "material_type_name": "党组织派人谈话记录"}], "stage_code": 1, "is_complete": true, "unclassified": [], "missing_total": 0}	{"nodes": {"D01": null, "T01": "2003-05-12", "T02": "2023-03-15", "T03": "2023-03-28", "T04": null, "T05": null, "T06": "2023-03-15", "T07": null, "T08": null, "T09": null, "T10": null, "T11": null, "T12": null, "T13": null, "T14": null, "T15": "2023-03-28", "T16": null, "T17": null, "T18": null, "T19": null, "T20": null, "T21": null}, "derived": {}}	[{"result": "PASS", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"result": "PASS", "rule_code": "R-T01"}, {"result": "PASS", "rule_code": "R-T02"}, {"result": "PASS", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T05"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T06"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T07"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T08"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T09"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T10"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T11"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T12"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T14"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T15"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T16"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T17"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T18"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T19"}, {"result": "PASS", "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "PASS", "rule_code": "R-T22"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "FAIL", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "PASS", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "FAIL", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "PASS", "rule_code": "R-C04"}, {"result": "PASS", "rule_code": "R-C05"}, {"result": "FAIL", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 5, "rules_run": 39, "by_category": {"TIME": 1, "FORMAT": 2, "CONTENT": 2}, "by_severity": {"WARN": 2, "BLOCK": 3}, "rules_failed": 5, "rules_skipped": 20, "needs_judgement": 0, "materials_checked": 2}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:36:19.853836+08	2026-10-17 18:36:19.866477+08	12	REQUIRED	\N	["LOW_CONFIDENCE", "KEY_STAGE"]
6	21	1	REVIEW	1	33	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 22, "version_no": 1, "material_id": 22}, {"version_id": 23, "version_no": 1, "material_id": 23}, {"version_id": 24, "version_no": 1, "material_id": 24}, {"version_id": 25, "version_no": 1, "material_id": 25}, {"version_id": 26, "version_no": 1, "material_id": 26}, {"version_id": 27, "version_no": 1, "material_id": 27}]	[]	{"counts": [{"count": 1, "type_code": "APPLICATION_LETTER", "type_name": "入党申请书"}, {"count": 3, "type_code": "THOUGHT_REPORT", "type_name": "思想汇报"}, {"count": 1, "type_code": "CANDIDATE_MEETING_RECORD", "type_name": "支委会确定发展对象记录"}, {"count": 1, "type_code": "AUTOBIOGRAPHY", "type_name": "自传"}], "materials": [{"title": "入党申请书", "status": "AUTO", "type_code": "APPLICATION_LETTER", "confidence": 1.0, "material_id": 22, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 23, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 24, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 25, "type_source": "DECLARED"}, {"title": "支委会确定发展对象记录", "status": "AUTO", "type_code": "CANDIDATE_MEETING_RECORD", "confidence": 1.0, "material_id": 26, "type_source": "DECLARED"}, {"title": "自传", "status": "AUTO", "type_code": "AUTOBIOGRAPHY", "confidence": 1.0, "material_id": 27, "type_source": "DECLARED"}]}	{"extra": [{"title": "入党申请书", "reason": "不在本阶段清单", "material_id": 22}], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [27], "material_type": {"id": 9, "code": "AUTOBIOGRAPHY", "name": "自传"}, "quantity_mode": "FIXED", "requirement_text": "自传", "checklist_item_id": 9, "material_type_name": "自传"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [26], "material_type": {"id": 10, "code": "CANDIDATE_MEETING_RECORD", "name": "支委会确定发展对象记录"}, "quantity_mode": "FIXED", "requirement_text": "支委会确定发展对象记录", "checklist_item_id": 10, "material_type_name": "支委会确定发展对象记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 11, "code": "POLITICAL_REVIEW", "name": "政治审查材料"}, "quantity_mode": "FIXED", "requirement_text": "政治审查材料", "checklist_item_id": 11, "material_type_name": "政治审查材料"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 12, "code": "TRAINING_CERT", "name": "集中培训结业证书"}, "quantity_mode": "FIXED", "requirement_text": "集中培训结业证书", "checklist_item_id": 12, "material_type_name": "集中培训结业证书"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 13, "code": "RECORD_BOOK_CANDIDATE", "name": "写实簿·发展对象考察部分"}, "quantity_mode": "FIXED", "requirement_text": "写实簿发展对象考察部分", "checklist_item_id": 13, "material_type_name": "写实簿·发展对象考察部分"}, {"actual": 3, "missing": 2, "expected": 5, "required": true, "material_ids": [23, 24, 25], "material_type": {"id": 7, "code": "THOUGHT_REPORT", "name": "思想汇报"}, "quantity_mode": "PER_PERIOD", "requirement_text": "每季度至少一份思想汇报", "checklist_item_id": 14, "material_type_name": "思想汇报"}], "stage_code": 3, "is_complete": false, "unclassified": [], "missing_total": 5}	{"nodes": {"D01": null, "T01": "2003-05-12", "T02": "2023-03-15", "T03": "2023-03-20", "T04": "2024-09-10", "T05": null, "T06": "2003-05-12", "T07": null, "T08": "2025-08-30", "T09": null, "T10": null, "T11": null, "T12": null, "T13": null, "T14": null, "T15": null, "T16": null, "T17": null, "T18": null, "T19": null, "T20": null, "T21": null}, "derived": {}}	[{"result": "FAIL", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"result": "PASS", "rule_code": "R-T01"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T02"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T05"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T06"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T07"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T08"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T09"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T10"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T11"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T12"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T14"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T15"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T16"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T17"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T18"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T19"}, {"result": "PASS", "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "PASS", "rule_code": "R-T22"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "PASS", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "FAIL", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "FAIL", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "PASS", "rule_code": "R-C04"}, {"result": "FAIL", "rule_code": "R-C05"}, {"result": "FAIL", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 20, "rules_run": 39, "by_category": {"TIME": 5, "FORMAT": 6, "CONTENT": 5, "COMPLETENESS": 4}, "by_severity": {"WARN": 12, "BLOCK": 8}, "rules_failed": 11, "rules_skipped": 18, "needs_judgement": 0, "materials_checked": 6}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:36:17.141377+08	2026-10-17 18:36:17.180581+08	39	REQUIRED	\N	["LOW_CONFIDENCE", "KEY_STAGE"]
7	24	1	REVIEW	1	37	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 28, "version_no": 1, "material_id": 28}, {"version_id": 29, "version_no": 1, "material_id": 29}, {"version_id": 30, "version_no": 1, "material_id": 30}]	[]	{"counts": [{"count": 1, "type_code": "APPLICATION_LETTER", "type_name": "入党申请书"}, {"count": 1, "type_code": "AUTOBIOGRAPHY", "type_name": "自传"}, {"count": 1, "type_code": "THOUGHT_REPORT", "type_name": "思想汇报"}], "materials": [{"title": "入党申请书", "status": "AUTO", "type_code": "APPLICATION_LETTER", "confidence": 1.0, "material_id": 28, "type_source": "DECLARED"}, {"title": "自传", "status": "AUTO", "type_code": "AUTOBIOGRAPHY", "confidence": 1.0, "material_id": 29, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 30, "type_source": "DECLARED"}]}	{"extra": [{"title": "入党申请书", "reason": "不在本阶段清单", "material_id": 28}], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [29], "material_type": {"id": 9, "code": "AUTOBIOGRAPHY", "name": "自传"}, "quantity_mode": "FIXED", "requirement_text": "自传", "checklist_item_id": 9, "material_type_name": "自传"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 10, "code": "CANDIDATE_MEETING_RECORD", "name": "支委会确定发展对象记录"}, "quantity_mode": "FIXED", "requirement_text": "支委会确定发展对象记录", "checklist_item_id": 10, "material_type_name": "支委会确定发展对象记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 11, "code": "POLITICAL_REVIEW", "name": "政治审查材料"}, "quantity_mode": "FIXED", "requirement_text": "政治审查材料", "checklist_item_id": 11, "material_type_name": "政治审查材料"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 12, "code": "TRAINING_CERT", "name": "集中培训结业证书"}, "quantity_mode": "FIXED", "requirement_text": "集中培训结业证书", "checklist_item_id": 12, "material_type_name": "集中培训结业证书"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 13, "code": "RECORD_BOOK_CANDIDATE", "name": "写实簿·发展对象考察部分"}, "quantity_mode": "FIXED", "requirement_text": "写实簿发展对象考察部分", "checklist_item_id": 13, "material_type_name": "写实簿·发展对象考察部分"}, {"actual": 1, "missing": 4, "expected": 5, "required": true, "material_ids": [30], "material_type": {"id": 7, "code": "THOUGHT_REPORT", "name": "思想汇报"}, "quantity_mode": "PER_PERIOD", "requirement_text": "每季度至少一份思想汇报", "checklist_item_id": 14, "material_type_name": "思想汇报"}], "stage_code": 3, "is_complete": false, "unclassified": [], "missing_total": 8}	{"nodes": {"D01": null, "T01": "2003-05-12", "T02": "2023-03-15", "T03": null, "T04": "2024-09-10", "T05": null, "T06": "2004-01-01", "T07": null, "T08": "2025-08-30", "T09": null, "T10": null, "T11": null, "T12": null, "T13": null, "T14": null, "T15": null, "T16": null, "T17": null, "T18": null, "T19": null, "T20": null, "T21": null}, "derived": {}}	[{"result": "FAIL", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"result": "PASS", "rule_code": "R-T01"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T02"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T05"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T06"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T07"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T08"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T09"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T10"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T11"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T12"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T14"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T15"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T16"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T17"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T18"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T19"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "PASS", "rule_code": "R-T22"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "PASS", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "FAIL", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "FAIL", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "FAIL", "rule_code": "R-C04"}, {"result": "FAIL", "rule_code": "R-C05"}, {"result": "FAIL", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 21, "rules_run": 39, "by_category": {"TIME": 6, "FORMAT": 3, "CONTENT": 7, "COMPLETENESS": 5}, "by_severity": {"WARN": 10, "BLOCK": 11}, "rules_failed": 13, "rules_skipped": 18, "needs_judgement": 2, "materials_checked": 3}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:36:17.308078+08	2026-10-17 18:36:17.340937+08	32	REQUIRED	\N	["LOW_CONFIDENCE", "MATERIAL_CONFLICT", "NEEDS_JUDGEMENT", "KEY_STAGE"]
8	30	1	REVIEW	1	45	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 32, "version_no": 1, "material_id": 32}, {"version_id": 33, "version_no": 1, "material_id": 33}, {"version_id": 34, "version_no": 1, "material_id": 34}, {"version_id": 35, "version_no": 1, "material_id": 35}, {"version_id": 36, "version_no": 1, "material_id": 36}, {"version_id": 37, "version_no": 1, "material_id": 37}]	[]	{"counts": [{"count": 1, "type_code": "APPLICATION_FORM", "type_name": "入党志愿书"}, {"count": 1, "type_code": "ADMISSION_MEETING_RECORD", "type_name": "支部大会讨论接收记录"}, {"count": 1, "type_code": "POLITICAL_REVIEW", "type_name": "政治审查材料"}, {"count": 1, "type_code": "TRAINING_CERT", "type_name": "集中培训结业证书"}, {"count": 1, "type_code": "CANDIDATE_PUBLICITY", "type_name": "发展对象公示材料"}, {"count": 1, "type_code": "PRE_REVIEW_OPINION", "type_name": "上级党委预审意见"}], "materials": [{"title": "入党志愿书", "status": "AUTO", "type_code": "APPLICATION_FORM", "confidence": 1.0, "material_id": 32, "type_source": "DECLARED"}, {"title": "支部大会讨论接收记录", "status": "AUTO", "type_code": "ADMISSION_MEETING_RECORD", "confidence": 1.0, "material_id": 33, "type_source": "DECLARED"}, {"title": "政治审查材料", "status": "AUTO", "type_code": "POLITICAL_REVIEW", "confidence": 1.0, "material_id": 34, "type_source": "DECLARED"}, {"title": "集中培训结业证书", "status": "AUTO", "type_code": "TRAINING_CERT", "confidence": 1.0, "material_id": 35, "type_source": "DECLARED"}, {"title": "发展对象公示材料", "status": "AUTO", "type_code": "CANDIDATE_PUBLICITY", "confidence": 1.0, "material_id": 36, "type_source": "DECLARED"}, {"title": "上级党委预审意见", "status": "AUTO", "type_code": "PRE_REVIEW_OPINION", "confidence": 1.0, "material_id": 37, "type_source": "DECLARED"}]}	{"extra": [{"title": "政治审查材料", "reason": "不在本阶段清单", "material_id": 34}, {"title": "集中培训结业证书", "reason": "不在本阶段清单", "material_id": 35}], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [36], "material_type": {"id": 14, "code": "CANDIDATE_PUBLICITY", "name": "发展对象公示材料"}, "quantity_mode": "FIXED", "requirement_text": "发展对象公示材料", "checklist_item_id": 15, "material_type_name": "发展对象公示材料"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [37], "material_type": {"id": 15, "code": "PRE_REVIEW_OPINION", "name": "上级党委预审意见"}, "quantity_mode": "FIXED", "requirement_text": "上级党委预审意见", "checklist_item_id": 16, "material_type_name": "上级党委预审意见"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [32], "material_type": {"id": 16, "code": "APPLICATION_FORM", "name": "入党志愿书"}, "quantity_mode": "FIXED", "requirement_text": "入党志愿书", "checklist_item_id": 17, "material_type_name": "入党志愿书"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [33], "material_type": {"id": 17, "code": "ADMISSION_MEETING_RECORD", "name": "支部大会讨论接收记录"}, "quantity_mode": "FIXED", "requirement_text": "支部大会讨论接收预备党员记录", "checklist_item_id": 18, "material_type_name": "支部大会讨论接收记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 18, "code": "COMMITTEE_TALK_RECORD", "name": "上级党委派人谈话记录"}, "quantity_mode": "FIXED", "requirement_text": "上级党委派人谈话记录", "checklist_item_id": 19, "material_type_name": "上级党委派人谈话记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 19, "code": "ADMISSION_APPROVAL", "name": "上级党委审批意见"}, "quantity_mode": "FIXED", "requirement_text": "上级党委审批意见", "checklist_item_id": 20, "material_type_name": "上级党委审批意见"}], "stage_code": 4, "is_complete": false, "unclassified": [], "missing_total": 2}	{"nodes": {"D01": "2026-06-01", "T01": "2003-05-12", "T02": "2022-03-15", "T03": null, "T04": "2023-04-01", "T05": null, "T06": "2024-06-01", "T07": null, "T08": "2024-05-01", "T09": "2024-06-01", "T10": "2024-07-01", "T11": null, "T12": "2025-05-10", "T13": "2025-05-20", "T14": "2025-06-01", "T15": null, "T16": "2025-06-01", "T17": null, "T18": null, "T19": "2025-04-20", "T20": "2025-06-01", "T21": null}, "derived": {"D01": "2026-06-01"}}	[{"result": "FAIL", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"result": "PASS", "rule_code": "R-T01"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T02"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"result": "PASS", "rule_code": "R-T05"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T06"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T07"}, {"result": "PASS", "rule_code": "R-T08"}, {"result": "PASS", "rule_code": "R-T09"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T10"}, {"result": "PASS", "rule_code": "R-T11"}, {"result": "PASS", "rule_code": "R-T12"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T14"}, {"result": "PASS", "rule_code": "R-T15"}, {"result": "PASS", "derived": {"D01": "2026-06-01"}, "rule_code": "R-T16"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T17"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T18"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T19"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T22"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "FAIL", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "PASS", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "PASS", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "PASS", "rule_code": "R-C04"}, {"result": "PASS", "rule_code": "R-C05"}, {"result": "FAIL", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 13, "rules_run": 39, "by_category": {"TIME": 3, "FORMAT": 7, "CONTENT": 1, "COMPLETENESS": 2}, "by_severity": {"WARN": 6, "BLOCK": 7}, "rules_failed": 7, "rules_skipped": 15, "needs_judgement": 0, "materials_checked": 6}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:36:17.615095+08	2026-10-17 18:36:17.655773+08	40	REQUIRED	\N	["LOW_CONFIDENCE", "MATERIAL_CONFLICT", "KEY_STAGE"]
9	35	1	REVIEW	1	49	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 38, "version_no": 1, "material_id": 38}, {"version_id": 39, "version_no": 1, "material_id": 39}, {"version_id": 40, "version_no": 1, "material_id": 40}]	[]	{"counts": [{"count": 1, "type_code": "REGULARIZATION_LETTER", "type_name": "转正申请书"}, {"count": 1, "type_code": "REGULARIZATION_MEETING_RECORD", "type_name": "支部大会讨论转正记录"}, {"count": 1, "type_code": "REGULARIZATION_PUBLICITY", "type_name": "转正公示材料"}], "materials": [{"title": "转正申请书", "status": "AUTO", "type_code": "REGULARIZATION_LETTER", "confidence": 1.0, "material_id": 38, "type_source": "DECLARED"}, {"title": "支部大会讨论转正记录", "status": "AUTO", "type_code": "REGULARIZATION_MEETING_RECORD", "confidence": 1.0, "material_id": 39, "type_source": "DECLARED"}, {"title": "转正公示材料", "status": "AUTO", "type_code": "REGULARIZATION_PUBLICITY", "confidence": 1.0, "material_id": 40, "type_source": "DECLARED"}]}	{"extra": [], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [38], "material_type": {"id": 20, "code": "REGULARIZATION_LETTER", "name": "转正申请书"}, "quantity_mode": "FIXED", "requirement_text": "转正申请书", "checklist_item_id": 21, "material_type_name": "转正申请书"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 21, "code": "RECORD_BOOK_PROBATIONARY", "name": "写实簿·预备党员考察部分"}, "quantity_mode": "FIXED", "requirement_text": "写实簿预备党员考察部分", "checklist_item_id": 22, "material_type_name": "写实簿·预备党员考察部分"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [40], "material_type": {"id": 22, "code": "REGULARIZATION_PUBLICITY", "name": "转正公示材料"}, "quantity_mode": "FIXED", "requirement_text": "转正公示材料", "checklist_item_id": 23, "material_type_name": "转正公示材料"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [39], "material_type": {"id": 23, "code": "REGULARIZATION_MEETING_RECORD", "name": "支部大会讨论转正记录"}, "quantity_mode": "FIXED", "requirement_text": "支部大会讨论转正记录", "checklist_item_id": 24, "material_type_name": "支部大会讨论转正记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 24, "code": "REGULARIZATION_APPROVAL", "name": "上级党委审批转正意见"}, "quantity_mode": "FIXED", "requirement_text": "上级党委审批转正意见", "checklist_item_id": 25, "material_type_name": "上级党委审批转正意见"}, {"actual": 0, "missing": 4, "expected": 4, "required": true, "material_ids": [], "material_type": {"id": 7, "code": "THOUGHT_REPORT", "name": "思想汇报"}, "quantity_mode": "PER_PERIOD", "requirement_text": "预备期每季度至少一份思想汇报", "checklist_item_id": 26, "material_type_name": "思想汇报"}], "stage_code": 5, "is_complete": false, "unclassified": [], "missing_total": 6}	{"nodes": {"D01": "2025-10-01", "T01": null, "T02": null, "T03": null, "T04": null, "T05": null, "T06": "2025-09-20", "T07": null, "T08": null, "T09": null, "T10": null, "T11": "2025-09-25", "T12": null, "T13": null, "T14": "2024-10-01", "T15": null, "T16": "2024-10-20", "T17": null, "T18": "2025-09-20", "T19": null, "T20": "2025-10-08", "T21": null}, "derived": {"D01": "2025-10-01"}}	[{"result": "FAIL", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T01"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T02"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T05"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T06"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T07"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T08"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T09"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T10"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T11"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T12"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T14"}, {"result": "PASS", "rule_code": "R-T15"}, {"result": "PASS", "derived": {"D01": "2025-10-01"}, "rule_code": "R-T16"}, {"result": "PASS", "rule_code": "R-T17"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T18"}, {"result": "PASS", "rule_code": "R-T19"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T22"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "PASS", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "PASS", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "PASS", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "PASS", "rule_code": "R-C04"}, {"result": "FAIL", "rule_code": "R-C05"}, {"result": "PASS", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 10, "rules_run": 39, "by_category": {"TIME": 3, "FORMAT": 3, "CONTENT": 1, "COMPLETENESS": 3}, "by_severity": {"WARN": 4, "BLOCK": 6}, "rules_failed": 6, "rules_skipped": 19, "needs_judgement": 0, "materials_checked": 3}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:36:17.759115+08	2026-10-17 18:36:17.791941+08	32	REQUIRED	\N	["LOW_CONFIDENCE", "MATERIAL_CONFLICT", "KEY_STAGE"]
10	36	1	REVIEW	1	52	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 41, "version_no": 1, "material_id": 41}, {"version_id": 42, "version_no": 1, "material_id": 42}]	[]	{"counts": [{"count": 1, "type_code": "APPLICATION_LETTER", "type_name": "入党申请书"}, {"count": 1, "type_code": "PARTY_TALK_RECORD", "type_name": "党组织派人谈话记录"}], "materials": [{"title": "入党申请书", "status": "AUTO", "type_code": "APPLICATION_LETTER", "confidence": 1.0, "material_id": 41, "type_source": "DECLARED"}, {"title": "党组织派人谈话记录", "status": "AUTO", "type_code": "PARTY_TALK_RECORD", "confidence": 1.0, "material_id": 42, "type_source": "DECLARED"}]}	{"extra": [], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [41], "material_type": {"id": 1, "code": "APPLICATION_LETTER", "name": "入党申请书"}, "quantity_mode": "FIXED", "requirement_text": "本人亲笔或打印后签字的入党申请书", "checklist_item_id": 1, "material_type_name": "入党申请书"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [42], "material_type": {"id": 2, "code": "PARTY_TALK_RECORD", "name": "党组织派人谈话记录"}, "quantity_mode": "FIXED", "requirement_text": "党组织派人谈话记录", "checklist_item_id": 2, "material_type_name": "党组织派人谈话记录"}], "stage_code": 1, "is_complete": true, "unclassified": [], "missing_total": 0}	{"nodes": {"D01": null, "T01": "2003-05-12", "T02": "2023-03-15", "T03": "2023-03-28", "T04": null, "T05": null, "T06": "2023-03-15", "T07": null, "T08": null, "T09": null, "T10": null, "T11": null, "T12": null, "T13": null, "T14": null, "T15": "2023-03-28", "T16": null, "T17": null, "T18": null, "T19": null, "T20": null, "T21": null}, "derived": {}}	[{"result": "PASS", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"result": "PASS", "rule_code": "R-T01"}, {"result": "PASS", "rule_code": "R-T02"}, {"result": "PASS", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T05"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T06"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T07"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T08"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T09"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T10"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T11"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T12"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T14"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T15"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T16"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T17"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T18"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T19"}, {"result": "PASS", "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "PASS", "rule_code": "R-T22"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "FAIL", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "PASS", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "FAIL", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "PASS", "rule_code": "R-C04"}, {"result": "PASS", "rule_code": "R-C05"}, {"result": "FAIL", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 5, "rules_run": 39, "by_category": {"TIME": 1, "FORMAT": 2, "CONTENT": 2}, "by_severity": {"WARN": 2, "BLOCK": 3}, "rules_failed": 5, "rules_skipped": 20, "needs_judgement": 0, "materials_checked": 2}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:36:17.874273+08	2026-10-17 18:36:17.909162+08	34	REQUIRED	\N	["LOW_CONFIDENCE", "KEY_STAGE"]
11	39	1	REVIEW	1	59	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 43, "version_no": 1, "material_id": 43}, {"version_id": 44, "version_no": 1, "material_id": 44}, {"version_id": 45, "version_no": 1, "material_id": 45}, {"version_id": 46, "version_no": 1, "material_id": 46}, {"version_id": 47, "version_no": 1, "material_id": 47}, {"version_id": 48, "version_no": 1, "material_id": 48}]	[]	{"counts": [{"count": 1, "type_code": "APPLICATION_LETTER", "type_name": "入党申请书"}, {"count": 3, "type_code": "THOUGHT_REPORT", "type_name": "思想汇报"}, {"count": 1, "type_code": "CANDIDATE_MEETING_RECORD", "type_name": "支委会确定发展对象记录"}, {"count": 1, "type_code": "AUTOBIOGRAPHY", "type_name": "自传"}], "materials": [{"title": "入党申请书", "status": "AUTO", "type_code": "APPLICATION_LETTER", "confidence": 1.0, "material_id": 43, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 44, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 45, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 46, "type_source": "DECLARED"}, {"title": "支委会确定发展对象记录", "status": "AUTO", "type_code": "CANDIDATE_MEETING_RECORD", "confidence": 1.0, "material_id": 47, "type_source": "DECLARED"}, {"title": "自传", "status": "AUTO", "type_code": "AUTOBIOGRAPHY", "confidence": 1.0, "material_id": 48, "type_source": "DECLARED"}]}	{"extra": [{"title": "入党申请书", "reason": "不在本阶段清单", "material_id": 43}], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [48], "material_type": {"id": 9, "code": "AUTOBIOGRAPHY", "name": "自传"}, "quantity_mode": "FIXED", "requirement_text": "自传", "checklist_item_id": 9, "material_type_name": "自传"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [47], "material_type": {"id": 10, "code": "CANDIDATE_MEETING_RECORD", "name": "支委会确定发展对象记录"}, "quantity_mode": "FIXED", "requirement_text": "支委会确定发展对象记录", "checklist_item_id": 10, "material_type_name": "支委会确定发展对象记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 11, "code": "POLITICAL_REVIEW", "name": "政治审查材料"}, "quantity_mode": "FIXED", "requirement_text": "政治审查材料", "checklist_item_id": 11, "material_type_name": "政治审查材料"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 12, "code": "TRAINING_CERT", "name": "集中培训结业证书"}, "quantity_mode": "FIXED", "requirement_text": "集中培训结业证书", "checklist_item_id": 12, "material_type_name": "集中培训结业证书"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 13, "code": "RECORD_BOOK_CANDIDATE", "name": "写实簿·发展对象考察部分"}, "quantity_mode": "FIXED", "requirement_text": "写实簿发展对象考察部分", "checklist_item_id": 13, "material_type_name": "写实簿·发展对象考察部分"}, {"actual": 3, "missing": 2, "expected": 5, "required": true, "material_ids": [44, 45, 46], "material_type": {"id": 7, "code": "THOUGHT_REPORT", "name": "思想汇报"}, "quantity_mode": "PER_PERIOD", "requirement_text": "每季度至少一份思想汇报", "checklist_item_id": 14, "material_type_name": "思想汇报"}], "stage_code": 3, "is_complete": false, "unclassified": [], "missing_total": 5}	{"nodes": {"D01": null, "T01": "2003-05-12", "T02": "2023-03-15", "T03": "2023-03-20", "T04": "2024-09-10", "T05": null, "T06": "2003-05-12", "T07": null, "T08": "2025-08-30", "T09": null, "T10": null, "T11": null, "T12": null, "T13": null, "T14": null, "T15": null, "T16": null, "T17": null, "T18": null, "T19": null, "T20": null, "T21": null}, "derived": {}}	[{"result": "FAIL", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"result": "PASS", "rule_code": "R-T01"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T02"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T05"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T06"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T07"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T08"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T09"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T10"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T11"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T12"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T14"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T15"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T16"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T17"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T18"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T19"}, {"result": "PASS", "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "PASS", "rule_code": "R-T22"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "PASS", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "FAIL", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "FAIL", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "PASS", "rule_code": "R-C04"}, {"result": "FAIL", "rule_code": "R-C05"}, {"result": "FAIL", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 20, "rules_run": 39, "by_category": {"TIME": 5, "FORMAT": 6, "CONTENT": 5, "COMPLETENESS": 4}, "by_severity": {"WARN": 12, "BLOCK": 8}, "rules_failed": 11, "rules_skipped": 18, "needs_judgement": 0, "materials_checked": 6}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:36:18.137976+08	2026-10-17 18:36:18.184345+08	46	REQUIRED	\N	["LOW_CONFIDENCE", "KEY_STAGE"]
12	42	1	REVIEW	1	63	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 49, "version_no": 1, "material_id": 49}, {"version_id": 50, "version_no": 1, "material_id": 50}, {"version_id": 51, "version_no": 1, "material_id": 51}]	[]	{"counts": [{"count": 1, "type_code": "APPLICATION_LETTER", "type_name": "入党申请书"}, {"count": 1, "type_code": "AUTOBIOGRAPHY", "type_name": "自传"}, {"count": 1, "type_code": "THOUGHT_REPORT", "type_name": "思想汇报"}], "materials": [{"title": "入党申请书", "status": "AUTO", "type_code": "APPLICATION_LETTER", "confidence": 1.0, "material_id": 49, "type_source": "DECLARED"}, {"title": "自传", "status": "AUTO", "type_code": "AUTOBIOGRAPHY", "confidence": 1.0, "material_id": 50, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 51, "type_source": "DECLARED"}]}	{"extra": [{"title": "入党申请书", "reason": "不在本阶段清单", "material_id": 49}], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [50], "material_type": {"id": 9, "code": "AUTOBIOGRAPHY", "name": "自传"}, "quantity_mode": "FIXED", "requirement_text": "自传", "checklist_item_id": 9, "material_type_name": "自传"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 10, "code": "CANDIDATE_MEETING_RECORD", "name": "支委会确定发展对象记录"}, "quantity_mode": "FIXED", "requirement_text": "支委会确定发展对象记录", "checklist_item_id": 10, "material_type_name": "支委会确定发展对象记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 11, "code": "POLITICAL_REVIEW", "name": "政治审查材料"}, "quantity_mode": "FIXED", "requirement_text": "政治审查材料", "checklist_item_id": 11, "material_type_name": "政治审查材料"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 12, "code": "TRAINING_CERT", "name": "集中培训结业证书"}, "quantity_mode": "FIXED", "requirement_text": "集中培训结业证书", "checklist_item_id": 12, "material_type_name": "集中培训结业证书"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 13, "code": "RECORD_BOOK_CANDIDATE", "name": "写实簿·发展对象考察部分"}, "quantity_mode": "FIXED", "requirement_text": "写实簿发展对象考察部分", "checklist_item_id": 13, "material_type_name": "写实簿·发展对象考察部分"}, {"actual": 1, "missing": 4, "expected": 5, "required": true, "material_ids": [51], "material_type": {"id": 7, "code": "THOUGHT_REPORT", "name": "思想汇报"}, "quantity_mode": "PER_PERIOD", "requirement_text": "每季度至少一份思想汇报", "checklist_item_id": 14, "material_type_name": "思想汇报"}], "stage_code": 3, "is_complete": false, "unclassified": [], "missing_total": 8}	{"nodes": {"D01": null, "T01": "2003-05-12", "T02": "2023-03-15", "T03": null, "T04": "2024-09-10", "T05": null, "T06": "2004-01-01", "T07": null, "T08": "2025-08-30", "T09": null, "T10": null, "T11": null, "T12": null, "T13": null, "T14": null, "T15": null, "T16": null, "T17": null, "T18": null, "T19": null, "T20": null, "T21": null}, "derived": {}}	[{"result": "FAIL", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"result": "PASS", "rule_code": "R-T01"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T02"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T05"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T06"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T07"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T08"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T09"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T10"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T11"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T12"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T14"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T15"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T16"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T17"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T18"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T19"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "PASS", "rule_code": "R-T22"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "PASS", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "FAIL", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "FAIL", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "FAIL", "rule_code": "R-C04"}, {"result": "FAIL", "rule_code": "R-C05"}, {"result": "FAIL", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 21, "rules_run": 39, "by_category": {"TIME": 6, "FORMAT": 3, "CONTENT": 7, "COMPLETENESS": 5}, "by_severity": {"WARN": 10, "BLOCK": 11}, "rules_failed": 13, "rules_skipped": 18, "needs_judgement": 2, "materials_checked": 3}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:36:18.285204+08	2026-10-17 18:36:18.316117+08	30	REQUIRED	\N	["LOW_CONFIDENCE", "MATERIAL_CONFLICT", "NEEDS_JUDGEMENT", "KEY_STAGE"]
13	48	1	REVIEW	1	71	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 53, "version_no": 1, "material_id": 53}, {"version_id": 54, "version_no": 1, "material_id": 54}, {"version_id": 55, "version_no": 1, "material_id": 55}, {"version_id": 56, "version_no": 1, "material_id": 56}, {"version_id": 57, "version_no": 1, "material_id": 57}, {"version_id": 58, "version_no": 1, "material_id": 58}]	[]	{"counts": [{"count": 1, "type_code": "APPLICATION_FORM", "type_name": "入党志愿书"}, {"count": 1, "type_code": "ADMISSION_MEETING_RECORD", "type_name": "支部大会讨论接收记录"}, {"count": 1, "type_code": "POLITICAL_REVIEW", "type_name": "政治审查材料"}, {"count": 1, "type_code": "TRAINING_CERT", "type_name": "集中培训结业证书"}, {"count": 1, "type_code": "CANDIDATE_PUBLICITY", "type_name": "发展对象公示材料"}, {"count": 1, "type_code": "PRE_REVIEW_OPINION", "type_name": "上级党委预审意见"}], "materials": [{"title": "入党志愿书", "status": "AUTO", "type_code": "APPLICATION_FORM", "confidence": 1.0, "material_id": 53, "type_source": "DECLARED"}, {"title": "支部大会讨论接收记录", "status": "AUTO", "type_code": "ADMISSION_MEETING_RECORD", "confidence": 1.0, "material_id": 54, "type_source": "DECLARED"}, {"title": "政治审查材料", "status": "AUTO", "type_code": "POLITICAL_REVIEW", "confidence": 1.0, "material_id": 55, "type_source": "DECLARED"}, {"title": "集中培训结业证书", "status": "AUTO", "type_code": "TRAINING_CERT", "confidence": 1.0, "material_id": 56, "type_source": "DECLARED"}, {"title": "发展对象公示材料", "status": "AUTO", "type_code": "CANDIDATE_PUBLICITY", "confidence": 1.0, "material_id": 57, "type_source": "DECLARED"}, {"title": "上级党委预审意见", "status": "AUTO", "type_code": "PRE_REVIEW_OPINION", "confidence": 1.0, "material_id": 58, "type_source": "DECLARED"}]}	{"extra": [{"title": "政治审查材料", "reason": "不在本阶段清单", "material_id": 55}, {"title": "集中培训结业证书", "reason": "不在本阶段清单", "material_id": 56}], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [57], "material_type": {"id": 14, "code": "CANDIDATE_PUBLICITY", "name": "发展对象公示材料"}, "quantity_mode": "FIXED", "requirement_text": "发展对象公示材料", "checklist_item_id": 15, "material_type_name": "发展对象公示材料"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [58], "material_type": {"id": 15, "code": "PRE_REVIEW_OPINION", "name": "上级党委预审意见"}, "quantity_mode": "FIXED", "requirement_text": "上级党委预审意见", "checklist_item_id": 16, "material_type_name": "上级党委预审意见"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [53], "material_type": {"id": 16, "code": "APPLICATION_FORM", "name": "入党志愿书"}, "quantity_mode": "FIXED", "requirement_text": "入党志愿书", "checklist_item_id": 17, "material_type_name": "入党志愿书"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [54], "material_type": {"id": 17, "code": "ADMISSION_MEETING_RECORD", "name": "支部大会讨论接收记录"}, "quantity_mode": "FIXED", "requirement_text": "支部大会讨论接收预备党员记录", "checklist_item_id": 18, "material_type_name": "支部大会讨论接收记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 18, "code": "COMMITTEE_TALK_RECORD", "name": "上级党委派人谈话记录"}, "quantity_mode": "FIXED", "requirement_text": "上级党委派人谈话记录", "checklist_item_id": 19, "material_type_name": "上级党委派人谈话记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 19, "code": "ADMISSION_APPROVAL", "name": "上级党委审批意见"}, "quantity_mode": "FIXED", "requirement_text": "上级党委审批意见", "checklist_item_id": 20, "material_type_name": "上级党委审批意见"}], "stage_code": 4, "is_complete": false, "unclassified": [], "missing_total": 2}	{"nodes": {"D01": "2026-06-01", "T01": "2003-05-12", "T02": "2022-03-15", "T03": null, "T04": "2023-04-01", "T05": null, "T06": "2024-06-01", "T07": null, "T08": "2024-05-01", "T09": "2024-06-01", "T10": "2024-07-01", "T11": null, "T12": "2025-05-10", "T13": "2025-05-20", "T14": "2025-06-01", "T15": null, "T16": "2025-06-01", "T17": null, "T18": null, "T19": "2025-04-20", "T20": "2025-06-01", "T21": null}, "derived": {"D01": "2026-06-01"}}	[{"result": "FAIL", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"result": "PASS", "rule_code": "R-T01"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T02"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"result": "PASS", "rule_code": "R-T05"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T06"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T07"}, {"result": "PASS", "rule_code": "R-T08"}, {"result": "PASS", "rule_code": "R-T09"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T10"}, {"result": "PASS", "rule_code": "R-T11"}, {"result": "PASS", "rule_code": "R-T12"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T14"}, {"result": "PASS", "rule_code": "R-T15"}, {"result": "PASS", "derived": {"D01": "2026-06-01"}, "rule_code": "R-T16"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T17"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T18"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T19"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T22"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "FAIL", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "PASS", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "PASS", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "PASS", "rule_code": "R-C04"}, {"result": "PASS", "rule_code": "R-C05"}, {"result": "FAIL", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 13, "rules_run": 39, "by_category": {"TIME": 3, "FORMAT": 7, "CONTENT": 1, "COMPLETENESS": 2}, "by_severity": {"WARN": 6, "BLOCK": 7}, "rules_failed": 7, "rules_skipped": 15, "needs_judgement": 0, "materials_checked": 6}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:36:18.602938+08	2026-10-17 18:36:18.636822+08	33	REQUIRED	\N	["LOW_CONFIDENCE", "MATERIAL_CONFLICT", "KEY_STAGE"]
14	53	1	REVIEW	1	75	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 59, "version_no": 1, "material_id": 59}, {"version_id": 60, "version_no": 1, "material_id": 60}, {"version_id": 61, "version_no": 1, "material_id": 61}]	[]	{"counts": [{"count": 1, "type_code": "REGULARIZATION_LETTER", "type_name": "转正申请书"}, {"count": 1, "type_code": "REGULARIZATION_MEETING_RECORD", "type_name": "支部大会讨论转正记录"}, {"count": 1, "type_code": "REGULARIZATION_PUBLICITY", "type_name": "转正公示材料"}], "materials": [{"title": "转正申请书", "status": "AUTO", "type_code": "REGULARIZATION_LETTER", "confidence": 1.0, "material_id": 59, "type_source": "DECLARED"}, {"title": "支部大会讨论转正记录", "status": "AUTO", "type_code": "REGULARIZATION_MEETING_RECORD", "confidence": 1.0, "material_id": 60, "type_source": "DECLARED"}, {"title": "转正公示材料", "status": "AUTO", "type_code": "REGULARIZATION_PUBLICITY", "confidence": 1.0, "material_id": 61, "type_source": "DECLARED"}]}	{"extra": [], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [59], "material_type": {"id": 20, "code": "REGULARIZATION_LETTER", "name": "转正申请书"}, "quantity_mode": "FIXED", "requirement_text": "转正申请书", "checklist_item_id": 21, "material_type_name": "转正申请书"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 21, "code": "RECORD_BOOK_PROBATIONARY", "name": "写实簿·预备党员考察部分"}, "quantity_mode": "FIXED", "requirement_text": "写实簿预备党员考察部分", "checklist_item_id": 22, "material_type_name": "写实簿·预备党员考察部分"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [61], "material_type": {"id": 22, "code": "REGULARIZATION_PUBLICITY", "name": "转正公示材料"}, "quantity_mode": "FIXED", "requirement_text": "转正公示材料", "checklist_item_id": 23, "material_type_name": "转正公示材料"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [60], "material_type": {"id": 23, "code": "REGULARIZATION_MEETING_RECORD", "name": "支部大会讨论转正记录"}, "quantity_mode": "FIXED", "requirement_text": "支部大会讨论转正记录", "checklist_item_id": 24, "material_type_name": "支部大会讨论转正记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 24, "code": "REGULARIZATION_APPROVAL", "name": "上级党委审批转正意见"}, "quantity_mode": "FIXED", "requirement_text": "上级党委审批转正意见", "checklist_item_id": 25, "material_type_name": "上级党委审批转正意见"}, {"actual": 0, "missing": 4, "expected": 4, "required": true, "material_ids": [], "material_type": {"id": 7, "code": "THOUGHT_REPORT", "name": "思想汇报"}, "quantity_mode": "PER_PERIOD", "requirement_text": "预备期每季度至少一份思想汇报", "checklist_item_id": 26, "material_type_name": "思想汇报"}], "stage_code": 5, "is_complete": false, "unclassified": [], "missing_total": 6}	{"nodes": {"D01": "2025-10-01", "T01": null, "T02": null, "T03": null, "T04": null, "T05": null, "T06": "2025-09-20", "T07": null, "T08": null, "T09": null, "T10": null, "T11": "2025-09-25", "T12": null, "T13": null, "T14": "2024-10-01", "T15": null, "T16": "2024-10-20", "T17": null, "T18": "2025-09-20", "T19": null, "T20": "2025-10-08", "T21": null}, "derived": {"D01": "2025-10-01"}}	[{"result": "FAIL", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T01"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T02"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T05"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T06"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T07"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T08"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T09"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T10"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T11"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T12"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T14"}, {"result": "PASS", "rule_code": "R-T15"}, {"result": "PASS", "derived": {"D01": "2025-10-01"}, "rule_code": "R-T16"}, {"result": "PASS", "rule_code": "R-T17"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T18"}, {"result": "PASS", "rule_code": "R-T19"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T22"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "PASS", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "PASS", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "PASS", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "PASS", "rule_code": "R-C04"}, {"result": "FAIL", "rule_code": "R-C05"}, {"result": "PASS", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 10, "rules_run": 39, "by_category": {"TIME": 3, "FORMAT": 3, "CONTENT": 1, "COMPLETENESS": 3}, "by_severity": {"WARN": 4, "BLOCK": 6}, "rules_failed": 6, "rules_skipped": 19, "needs_judgement": 0, "materials_checked": 3}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:36:18.744342+08	2026-10-17 18:36:18.776118+08	31	REQUIRED	\N	["LOW_CONFIDENCE", "MATERIAL_CONFLICT", "KEY_STAGE"]
16	57	1	REVIEW	1	85	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 64, "version_no": 1, "material_id": 64}, {"version_id": 65, "version_no": 1, "material_id": 65}, {"version_id": 66, "version_no": 1, "material_id": 66}, {"version_id": 67, "version_no": 1, "material_id": 67}, {"version_id": 68, "version_no": 1, "material_id": 68}, {"version_id": 69, "version_no": 1, "material_id": 69}]	[]	{"counts": [{"count": 1, "type_code": "APPLICATION_LETTER", "type_name": "入党申请书"}, {"count": 3, "type_code": "THOUGHT_REPORT", "type_name": "思想汇报"}, {"count": 1, "type_code": "CANDIDATE_MEETING_RECORD", "type_name": "支委会确定发展对象记录"}, {"count": 1, "type_code": "AUTOBIOGRAPHY", "type_name": "自传"}], "materials": [{"title": "入党申请书", "status": "AUTO", "type_code": "APPLICATION_LETTER", "confidence": 1.0, "material_id": 64, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 65, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 66, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 67, "type_source": "DECLARED"}, {"title": "支委会确定发展对象记录", "status": "AUTO", "type_code": "CANDIDATE_MEETING_RECORD", "confidence": 1.0, "material_id": 68, "type_source": "DECLARED"}, {"title": "自传", "status": "AUTO", "type_code": "AUTOBIOGRAPHY", "confidence": 1.0, "material_id": 69, "type_source": "DECLARED"}]}	{"extra": [{"title": "入党申请书", "reason": "不在本阶段清单", "material_id": 64}], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [69], "material_type": {"id": 9, "code": "AUTOBIOGRAPHY", "name": "自传"}, "quantity_mode": "FIXED", "requirement_text": "自传", "checklist_item_id": 9, "material_type_name": "自传"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [68], "material_type": {"id": 10, "code": "CANDIDATE_MEETING_RECORD", "name": "支委会确定发展对象记录"}, "quantity_mode": "FIXED", "requirement_text": "支委会确定发展对象记录", "checklist_item_id": 10, "material_type_name": "支委会确定发展对象记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 11, "code": "POLITICAL_REVIEW", "name": "政治审查材料"}, "quantity_mode": "FIXED", "requirement_text": "政治审查材料", "checklist_item_id": 11, "material_type_name": "政治审查材料"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 12, "code": "TRAINING_CERT", "name": "集中培训结业证书"}, "quantity_mode": "FIXED", "requirement_text": "集中培训结业证书", "checklist_item_id": 12, "material_type_name": "集中培训结业证书"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 13, "code": "RECORD_BOOK_CANDIDATE", "name": "写实簿·发展对象考察部分"}, "quantity_mode": "FIXED", "requirement_text": "写实簿发展对象考察部分", "checklist_item_id": 13, "material_type_name": "写实簿·发展对象考察部分"}, {"actual": 3, "missing": 2, "expected": 5, "required": true, "material_ids": [65, 66, 67], "material_type": {"id": 7, "code": "THOUGHT_REPORT", "name": "思想汇报"}, "quantity_mode": "PER_PERIOD", "requirement_text": "每季度至少一份思想汇报", "checklist_item_id": 14, "material_type_name": "思想汇报"}], "stage_code": 3, "is_complete": false, "unclassified": [], "missing_total": 5}	{"nodes": {"D01": null, "T01": "2003-05-12", "T02": "2023-03-15", "T03": "2023-03-20", "T04": "2024-09-10", "T05": null, "T06": "2003-05-12", "T07": null, "T08": "2025-08-30", "T09": null, "T10": null, "T11": null, "T12": null, "T13": null, "T14": null, "T15": null, "T16": null, "T17": null, "T18": null, "T19": null, "T20": null, "T21": null}, "derived": {}}	[{"result": "FAIL", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"result": "PASS", "rule_code": "R-T01"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T02"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T05"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T06"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T07"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T08"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T09"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T10"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T11"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T12"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T14"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T15"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T16"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T17"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T18"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T19"}, {"result": "PASS", "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "PASS", "rule_code": "R-T22"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "PASS", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "FAIL", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "FAIL", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "PASS", "rule_code": "R-C04"}, {"result": "FAIL", "rule_code": "R-C05"}, {"result": "FAIL", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 20, "rules_run": 39, "by_category": {"TIME": 5, "FORMAT": 6, "CONTENT": 5, "COMPLETENESS": 4}, "by_severity": {"WARN": 12, "BLOCK": 8}, "rules_failed": 11, "rules_skipped": 18, "needs_judgement": 0, "materials_checked": 6}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:36:19.116604+08	2026-10-17 18:36:19.157799+08	41	REQUIRED	\N	["LOW_CONFIDENCE", "KEY_STAGE"]
17	60	1	REVIEW	1	89	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 70, "version_no": 1, "material_id": 70}, {"version_id": 71, "version_no": 1, "material_id": 71}, {"version_id": 72, "version_no": 1, "material_id": 72}]	[]	{"counts": [{"count": 1, "type_code": "APPLICATION_LETTER", "type_name": "入党申请书"}, {"count": 1, "type_code": "AUTOBIOGRAPHY", "type_name": "自传"}, {"count": 1, "type_code": "THOUGHT_REPORT", "type_name": "思想汇报"}], "materials": [{"title": "入党申请书", "status": "AUTO", "type_code": "APPLICATION_LETTER", "confidence": 1.0, "material_id": 70, "type_source": "DECLARED"}, {"title": "自传", "status": "AUTO", "type_code": "AUTOBIOGRAPHY", "confidence": 1.0, "material_id": 71, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 72, "type_source": "DECLARED"}]}	{"extra": [{"title": "入党申请书", "reason": "不在本阶段清单", "material_id": 70}], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [71], "material_type": {"id": 9, "code": "AUTOBIOGRAPHY", "name": "自传"}, "quantity_mode": "FIXED", "requirement_text": "自传", "checklist_item_id": 9, "material_type_name": "自传"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 10, "code": "CANDIDATE_MEETING_RECORD", "name": "支委会确定发展对象记录"}, "quantity_mode": "FIXED", "requirement_text": "支委会确定发展对象记录", "checklist_item_id": 10, "material_type_name": "支委会确定发展对象记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 11, "code": "POLITICAL_REVIEW", "name": "政治审查材料"}, "quantity_mode": "FIXED", "requirement_text": "政治审查材料", "checklist_item_id": 11, "material_type_name": "政治审查材料"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 12, "code": "TRAINING_CERT", "name": "集中培训结业证书"}, "quantity_mode": "FIXED", "requirement_text": "集中培训结业证书", "checklist_item_id": 12, "material_type_name": "集中培训结业证书"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 13, "code": "RECORD_BOOK_CANDIDATE", "name": "写实簿·发展对象考察部分"}, "quantity_mode": "FIXED", "requirement_text": "写实簿发展对象考察部分", "checklist_item_id": 13, "material_type_name": "写实簿·发展对象考察部分"}, {"actual": 1, "missing": 4, "expected": 5, "required": true, "material_ids": [72], "material_type": {"id": 7, "code": "THOUGHT_REPORT", "name": "思想汇报"}, "quantity_mode": "PER_PERIOD", "requirement_text": "每季度至少一份思想汇报", "checklist_item_id": 14, "material_type_name": "思想汇报"}], "stage_code": 3, "is_complete": false, "unclassified": [], "missing_total": 8}	{"nodes": {"D01": null, "T01": "2003-05-12", "T02": "2023-03-15", "T03": null, "T04": "2024-09-10", "T05": null, "T06": "2004-01-01", "T07": null, "T08": "2025-08-30", "T09": null, "T10": null, "T11": null, "T12": null, "T13": null, "T14": null, "T15": null, "T16": null, "T17": null, "T18": null, "T19": null, "T20": null, "T21": null}, "derived": {}}	[{"result": "FAIL", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"result": "PASS", "rule_code": "R-T01"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T02"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T05"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T06"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T07"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T08"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T09"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T10"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T11"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T12"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T14"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T15"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T16"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T17"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T18"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T19"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "PASS", "rule_code": "R-T22"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "PASS", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "FAIL", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "FAIL", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "FAIL", "rule_code": "R-C04"}, {"result": "FAIL", "rule_code": "R-C05"}, {"result": "FAIL", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 21, "rules_run": 39, "by_category": {"TIME": 6, "FORMAT": 3, "CONTENT": 7, "COMPLETENESS": 5}, "by_severity": {"WARN": 10, "BLOCK": 11}, "rules_failed": 13, "rules_skipped": 18, "needs_judgement": 2, "materials_checked": 3}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:36:19.266225+08	2026-10-17 18:36:19.299982+08	33	REQUIRED	\N	["LOW_CONFIDENCE", "MATERIAL_CONFLICT", "NEEDS_JUDGEMENT", "KEY_STAGE"]
18	66	1	REVIEW	1	97	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 74, "version_no": 1, "material_id": 74}, {"version_id": 75, "version_no": 1, "material_id": 75}, {"version_id": 76, "version_no": 1, "material_id": 76}, {"version_id": 77, "version_no": 1, "material_id": 77}, {"version_id": 78, "version_no": 1, "material_id": 78}, {"version_id": 79, "version_no": 1, "material_id": 79}]	[]	{"counts": [{"count": 1, "type_code": "APPLICATION_FORM", "type_name": "入党志愿书"}, {"count": 1, "type_code": "ADMISSION_MEETING_RECORD", "type_name": "支部大会讨论接收记录"}, {"count": 1, "type_code": "POLITICAL_REVIEW", "type_name": "政治审查材料"}, {"count": 1, "type_code": "TRAINING_CERT", "type_name": "集中培训结业证书"}, {"count": 1, "type_code": "CANDIDATE_PUBLICITY", "type_name": "发展对象公示材料"}, {"count": 1, "type_code": "PRE_REVIEW_OPINION", "type_name": "上级党委预审意见"}], "materials": [{"title": "入党志愿书", "status": "AUTO", "type_code": "APPLICATION_FORM", "confidence": 1.0, "material_id": 74, "type_source": "DECLARED"}, {"title": "支部大会讨论接收记录", "status": "AUTO", "type_code": "ADMISSION_MEETING_RECORD", "confidence": 1.0, "material_id": 75, "type_source": "DECLARED"}, {"title": "政治审查材料", "status": "AUTO", "type_code": "POLITICAL_REVIEW", "confidence": 1.0, "material_id": 76, "type_source": "DECLARED"}, {"title": "集中培训结业证书", "status": "AUTO", "type_code": "TRAINING_CERT", "confidence": 1.0, "material_id": 77, "type_source": "DECLARED"}, {"title": "发展对象公示材料", "status": "AUTO", "type_code": "CANDIDATE_PUBLICITY", "confidence": 1.0, "material_id": 78, "type_source": "DECLARED"}, {"title": "上级党委预审意见", "status": "AUTO", "type_code": "PRE_REVIEW_OPINION", "confidence": 1.0, "material_id": 79, "type_source": "DECLARED"}]}	{"extra": [{"title": "政治审查材料", "reason": "不在本阶段清单", "material_id": 76}, {"title": "集中培训结业证书", "reason": "不在本阶段清单", "material_id": 77}], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [78], "material_type": {"id": 14, "code": "CANDIDATE_PUBLICITY", "name": "发展对象公示材料"}, "quantity_mode": "FIXED", "requirement_text": "发展对象公示材料", "checklist_item_id": 15, "material_type_name": "发展对象公示材料"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [79], "material_type": {"id": 15, "code": "PRE_REVIEW_OPINION", "name": "上级党委预审意见"}, "quantity_mode": "FIXED", "requirement_text": "上级党委预审意见", "checklist_item_id": 16, "material_type_name": "上级党委预审意见"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [74], "material_type": {"id": 16, "code": "APPLICATION_FORM", "name": "入党志愿书"}, "quantity_mode": "FIXED", "requirement_text": "入党志愿书", "checklist_item_id": 17, "material_type_name": "入党志愿书"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [75], "material_type": {"id": 17, "code": "ADMISSION_MEETING_RECORD", "name": "支部大会讨论接收记录"}, "quantity_mode": "FIXED", "requirement_text": "支部大会讨论接收预备党员记录", "checklist_item_id": 18, "material_type_name": "支部大会讨论接收记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 18, "code": "COMMITTEE_TALK_RECORD", "name": "上级党委派人谈话记录"}, "quantity_mode": "FIXED", "requirement_text": "上级党委派人谈话记录", "checklist_item_id": 19, "material_type_name": "上级党委派人谈话记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 19, "code": "ADMISSION_APPROVAL", "name": "上级党委审批意见"}, "quantity_mode": "FIXED", "requirement_text": "上级党委审批意见", "checklist_item_id": 20, "material_type_name": "上级党委审批意见"}], "stage_code": 4, "is_complete": false, "unclassified": [], "missing_total": 2}	{"nodes": {"D01": "2026-06-01", "T01": "2003-05-12", "T02": "2022-03-15", "T03": null, "T04": "2023-04-01", "T05": null, "T06": "2024-06-01", "T07": null, "T08": "2024-05-01", "T09": "2024-06-01", "T10": "2024-07-01", "T11": null, "T12": "2025-05-10", "T13": "2025-05-20", "T14": "2025-06-01", "T15": null, "T16": "2025-06-01", "T17": null, "T18": null, "T19": "2025-04-20", "T20": "2025-06-01", "T21": null}, "derived": {"D01": "2026-06-01"}}	[{"result": "FAIL", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"result": "PASS", "rule_code": "R-T01"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T02"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"result": "PASS", "rule_code": "R-T05"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T06"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T07"}, {"result": "PASS", "rule_code": "R-T08"}, {"result": "PASS", "rule_code": "R-T09"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T10"}, {"result": "PASS", "rule_code": "R-T11"}, {"result": "PASS", "rule_code": "R-T12"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T14"}, {"result": "PASS", "rule_code": "R-T15"}, {"result": "PASS", "derived": {"D01": "2026-06-01"}, "rule_code": "R-T16"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T17"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T18"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T19"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T22"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "FAIL", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "PASS", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "PASS", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "PASS", "rule_code": "R-C04"}, {"result": "PASS", "rule_code": "R-C05"}, {"result": "FAIL", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 13, "rules_run": 39, "by_category": {"TIME": 3, "FORMAT": 7, "CONTENT": 1, "COMPLETENESS": 2}, "by_severity": {"WARN": 6, "BLOCK": 7}, "rules_failed": 7, "rules_skipped": 15, "needs_judgement": 0, "materials_checked": 6}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:36:19.594958+08	2026-10-17 18:36:19.633751+08	38	REQUIRED	\N	["LOW_CONFIDENCE", "MATERIAL_CONFLICT", "KEY_STAGE"]
19	71	1	REVIEW	1	101	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 80, "version_no": 1, "material_id": 80}, {"version_id": 81, "version_no": 1, "material_id": 81}, {"version_id": 82, "version_no": 1, "material_id": 82}]	[]	{"counts": [{"count": 1, "type_code": "REGULARIZATION_LETTER", "type_name": "转正申请书"}, {"count": 1, "type_code": "REGULARIZATION_MEETING_RECORD", "type_name": "支部大会讨论转正记录"}, {"count": 1, "type_code": "REGULARIZATION_PUBLICITY", "type_name": "转正公示材料"}], "materials": [{"title": "转正申请书", "status": "AUTO", "type_code": "REGULARIZATION_LETTER", "confidence": 1.0, "material_id": 80, "type_source": "DECLARED"}, {"title": "支部大会讨论转正记录", "status": "AUTO", "type_code": "REGULARIZATION_MEETING_RECORD", "confidence": 1.0, "material_id": 81, "type_source": "DECLARED"}, {"title": "转正公示材料", "status": "AUTO", "type_code": "REGULARIZATION_PUBLICITY", "confidence": 1.0, "material_id": 82, "type_source": "DECLARED"}]}	{"extra": [], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [80], "material_type": {"id": 20, "code": "REGULARIZATION_LETTER", "name": "转正申请书"}, "quantity_mode": "FIXED", "requirement_text": "转正申请书", "checklist_item_id": 21, "material_type_name": "转正申请书"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 21, "code": "RECORD_BOOK_PROBATIONARY", "name": "写实簿·预备党员考察部分"}, "quantity_mode": "FIXED", "requirement_text": "写实簿预备党员考察部分", "checklist_item_id": 22, "material_type_name": "写实簿·预备党员考察部分"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [82], "material_type": {"id": 22, "code": "REGULARIZATION_PUBLICITY", "name": "转正公示材料"}, "quantity_mode": "FIXED", "requirement_text": "转正公示材料", "checklist_item_id": 23, "material_type_name": "转正公示材料"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [81], "material_type": {"id": 23, "code": "REGULARIZATION_MEETING_RECORD", "name": "支部大会讨论转正记录"}, "quantity_mode": "FIXED", "requirement_text": "支部大会讨论转正记录", "checklist_item_id": 24, "material_type_name": "支部大会讨论转正记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 24, "code": "REGULARIZATION_APPROVAL", "name": "上级党委审批转正意见"}, "quantity_mode": "FIXED", "requirement_text": "上级党委审批转正意见", "checklist_item_id": 25, "material_type_name": "上级党委审批转正意见"}, {"actual": 0, "missing": 4, "expected": 4, "required": true, "material_ids": [], "material_type": {"id": 7, "code": "THOUGHT_REPORT", "name": "思想汇报"}, "quantity_mode": "PER_PERIOD", "requirement_text": "预备期每季度至少一份思想汇报", "checklist_item_id": 26, "material_type_name": "思想汇报"}], "stage_code": 5, "is_complete": false, "unclassified": [], "missing_total": 6}	{"nodes": {"D01": "2025-10-01", "T01": null, "T02": null, "T03": null, "T04": null, "T05": null, "T06": "2025-09-20", "T07": null, "T08": null, "T09": null, "T10": null, "T11": "2025-09-25", "T12": null, "T13": null, "T14": "2024-10-01", "T15": null, "T16": "2024-10-20", "T17": null, "T18": "2025-09-20", "T19": null, "T20": "2025-10-08", "T21": null}, "derived": {"D01": "2025-10-01"}}	[{"result": "FAIL", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T01"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T02"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T05"}, {"result": "PASS", "rule_code": "R-T06"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T07"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T08"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T09"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T10"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T11"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T12"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T14"}, {"result": "PASS", "rule_code": "R-T15"}, {"result": "PASS", "derived": {"D01": "2025-10-01"}, "rule_code": "R-T16"}, {"result": "PASS", "rule_code": "R-T17"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T18"}, {"result": "PASS", "rule_code": "R-T19"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T22"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "PASS", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "PASS", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "PASS", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "PASS", "rule_code": "R-C04"}, {"result": "FAIL", "rule_code": "R-C05"}, {"result": "PASS", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 10, "rules_run": 39, "by_category": {"TIME": 3, "FORMAT": 3, "CONTENT": 1, "COMPLETENESS": 3}, "by_severity": {"WARN": 4, "BLOCK": 6}, "rules_failed": 6, "rules_skipped": 18, "needs_judgement": 0, "materials_checked": 3}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:36:19.755102+08	2026-10-17 18:36:19.783658+08	28	REQUIRED	\N	["LOW_CONFIDENCE", "MATERIAL_CONFLICT", "KEY_STAGE"]
21	8	1	REVIEW	5	105	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 10, "version_no": 1, "material_id": 10}]	[]	{"counts": [{"count": 1, "type_code": "APPLICATION_LETTER", "type_name": "入党申请书"}], "materials": [{"title": "入党申请书", "status": "AUTO", "type_code": "APPLICATION_LETTER", "confidence": 1.0, "material_id": 10, "type_source": "DECLARED"}]}	{"extra": [{"title": "入党申请书", "reason": "不在本阶段清单", "material_id": 10}], "items": [{"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 3, "code": "RECOMMENDATION", "name": "推荐/推优材料"}, "quantity_mode": "FIXED", "requirement_text": "党员推荐或团组织推优材料", "checklist_item_id": 3, "material_type_name": "推荐/推优材料"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 4, "code": "ACTIVIST_MEETING_RECORD", "name": "支委会研究确定积极分子记录"}, "quantity_mode": "FIXED", "requirement_text": "支委会（支部大会）研究确定积极分子记录", "checklist_item_id": 4, "material_type_name": "支委会研究确定积极分子记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 5, "code": "ACTIVIST_FILING", "name": "积极分子备案材料"}, "quantity_mode": "FIXED", "requirement_text": "积极分子备案材料", "checklist_item_id": 5, "material_type_name": "积极分子备案材料"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 6, "code": "RECORD_BOOK_ACTIVIST", "name": "写实簿·积极分子培养考察部分"}, "quantity_mode": "FIXED", "requirement_text": "写实簿积极分子培养考察部分", "checklist_item_id": 6, "material_type_name": "写实簿·积极分子培养考察部分"}, {"actual": 0, "missing": 9, "expected": 9, "required": true, "material_ids": [], "material_type": {"id": 7, "code": "THOUGHT_REPORT", "name": "思想汇报"}, "quantity_mode": "PER_PERIOD", "requirement_text": "每季度至少一份思想汇报", "checklist_item_id": 7, "material_type_name": "思想汇报"}, {"actual": 0, "missing": 1, "expected": 1, "required": false, "material_ids": [], "material_type": {"id": 8, "code": "ACTIVIST_TRAINING_CERT", "name": "积极分子培训结业证明"}, "quantity_mode": "FIXED", "requirement_text": "积极分子培训结业证明（可选）", "checklist_item_id": 8, "material_type_name": "积极分子培训结业证明"}], "stage_code": 2, "is_complete": false, "unclassified": [], "missing_total": 13}	{"nodes": {"D01": null, "T01": null, "T02": "2023-03-15", "T03": null, "T04": "2024-09-10", "T05": null, "T06": "2023-03-15", "T07": null, "T08": null, "T09": null, "T10": null, "T11": null, "T12": null, "T13": null, "T14": null, "T15": null, "T16": null, "T17": null, "T18": null, "T19": null, "T20": null, "T21": null}, "derived": {}}	[{"result": "FAIL", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T01"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T02"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T03"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T04"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T05"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T06"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T07"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T08"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T09"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T10"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T11"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T12"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T14"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T15"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T16"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T17"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T18"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T19"}, {"result": "PASS", "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T22"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T23"}, {"result": "PASS", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "PASS", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "PASS", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "FAIL", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "PASS", "rule_code": "R-C04"}, {"result": "PASS", "rule_code": "R-C05"}, {"result": "FAIL", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 13, "rules_run": 39, "by_category": {"TIME": 5, "CONTENT": 2, "COMPLETENESS": 6}, "by_severity": {"INFO": 1, "WARN": 4, "BLOCK": 8}, "rules_failed": 8, "rules_skipped": 20, "needs_judgement": 0, "materials_checked": 1}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:53:08.565885+08	2026-10-17 18:53:08.597171+08	31	REQUIRED	\N	["LOW_CONFIDENCE", "KEY_STAGE"]
22	3	2	BATCH	5	107	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 1, "version_no": 1, "material_id": 1}, {"version_id": 2, "version_no": 1, "material_id": 2}, {"version_id": 3, "version_no": 1, "material_id": 3}, {"version_id": 4, "version_no": 1, "material_id": 4}, {"version_id": 5, "version_no": 1, "material_id": 5}, {"version_id": 6, "version_no": 1, "material_id": 6}]	[]	{"counts": [{"count": 1, "type_code": "APPLICATION_LETTER", "type_name": "入党申请书"}, {"count": 3, "type_code": "THOUGHT_REPORT", "type_name": "思想汇报"}, {"count": 1, "type_code": "CANDIDATE_MEETING_RECORD", "type_name": "支委会确定发展对象记录"}, {"count": 1, "type_code": "AUTOBIOGRAPHY", "type_name": "自传"}], "materials": [{"title": "入党申请书", "status": "AUTO", "type_code": "APPLICATION_LETTER", "confidence": 1.0, "material_id": 1, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 2, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 3, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 4, "type_source": "DECLARED"}, {"title": "支委会确定发展对象记录", "status": "AUTO", "type_code": "CANDIDATE_MEETING_RECORD", "confidence": 1.0, "material_id": 5, "type_source": "DECLARED"}, {"title": "自传", "status": "AUTO", "type_code": "AUTOBIOGRAPHY", "confidence": 1.0, "material_id": 6, "type_source": "DECLARED"}]}	{"extra": [{"title": "入党申请书", "reason": "不在本阶段清单", "material_id": 1}], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [6], "material_type": {"id": 9, "code": "AUTOBIOGRAPHY", "name": "自传"}, "quantity_mode": "FIXED", "requirement_text": "自传", "checklist_item_id": 9, "material_type_name": "自传"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [5], "material_type": {"id": 10, "code": "CANDIDATE_MEETING_RECORD", "name": "支委会确定发展对象记录"}, "quantity_mode": "FIXED", "requirement_text": "支委会确定发展对象记录", "checklist_item_id": 10, "material_type_name": "支委会确定发展对象记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 11, "code": "POLITICAL_REVIEW", "name": "政治审查材料"}, "quantity_mode": "FIXED", "requirement_text": "政治审查材料", "checklist_item_id": 11, "material_type_name": "政治审查材料"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 12, "code": "TRAINING_CERT", "name": "集中培训结业证书"}, "quantity_mode": "FIXED", "requirement_text": "集中培训结业证书", "checklist_item_id": 12, "material_type_name": "集中培训结业证书"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 13, "code": "RECORD_BOOK_CANDIDATE", "name": "写实簿·发展对象考察部分"}, "quantity_mode": "FIXED", "requirement_text": "写实簿发展对象考察部分", "checklist_item_id": 13, "material_type_name": "写实簿·发展对象考察部分"}, {"actual": 3, "missing": 2, "expected": 5, "required": true, "material_ids": [2, 3, 4], "material_type": {"id": 7, "code": "THOUGHT_REPORT", "name": "思想汇报"}, "quantity_mode": "PER_PERIOD", "requirement_text": "每季度至少一份思想汇报", "checklist_item_id": 14, "material_type_name": "思想汇报"}], "stage_code": 3, "is_complete": false, "unclassified": [], "missing_total": 5}	{"nodes": {"D01": null, "T01": "2003-05-12", "T02": "2023-03-15", "T03": "2023-03-20", "T04": "2024-09-10", "T05": null, "T06": "2003-05-12", "T07": null, "T08": "2025-08-30", "T09": null, "T10": null, "T11": null, "T12": null, "T13": null, "T14": null, "T15": null, "T16": null, "T17": null, "T18": null, "T19": null, "T20": null, "T21": null}, "derived": {}}	[{"result": "FAIL", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"result": "PASS", "rule_code": "R-T01"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T02"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T05"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T06"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T07"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T08"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T09"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T10"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T11"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T12"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T14"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T15"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T16"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T17"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T18"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T19"}, {"result": "PASS", "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "PASS", "rule_code": "R-T22"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "PASS", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "FAIL", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "FAIL", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "PASS", "rule_code": "R-C04"}, {"result": "FAIL", "rule_code": "R-C05"}, {"result": "FAIL", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 20, "rules_run": 39, "by_category": {"TIME": 5, "FORMAT": 6, "CONTENT": 5, "COMPLETENESS": 4}, "by_severity": {"WARN": 12, "BLOCK": 8}, "rules_failed": 11, "rules_skipped": 18, "needs_judgement": 0, "materials_checked": 6}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 18:53:30.638627+08	2026-10-17 18:53:30.677608+08	38	REQUIRED	\N	["LOW_CONFIDENCE", "KEY_STAGE"]
23	3	3	REVIEW	5	108	1	RULE_ONLY	\N	\N	未配置大模型	DONE	[{"version_id": 1, "version_no": 1, "material_id": 1}, {"version_id": 2, "version_no": 1, "material_id": 2}, {"version_id": 3, "version_no": 1, "material_id": 3}, {"version_id": 4, "version_no": 1, "material_id": 4}, {"version_id": 5, "version_no": 1, "material_id": 5}, {"version_id": 6, "version_no": 1, "material_id": 6}]	[]	{"counts": [{"count": 1, "type_code": "APPLICATION_LETTER", "type_name": "入党申请书"}, {"count": 3, "type_code": "THOUGHT_REPORT", "type_name": "思想汇报"}, {"count": 1, "type_code": "CANDIDATE_MEETING_RECORD", "type_name": "支委会确定发展对象记录"}, {"count": 1, "type_code": "AUTOBIOGRAPHY", "type_name": "自传"}], "materials": [{"title": "入党申请书", "status": "AUTO", "type_code": "APPLICATION_LETTER", "confidence": 1.0, "material_id": 1, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 2, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 3, "type_source": "DECLARED"}, {"title": "思想汇报", "status": "AUTO", "type_code": "THOUGHT_REPORT", "confidence": 1.0, "material_id": 4, "type_source": "DECLARED"}, {"title": "支委会确定发展对象记录", "status": "AUTO", "type_code": "CANDIDATE_MEETING_RECORD", "confidence": 1.0, "material_id": 5, "type_source": "DECLARED"}, {"title": "自传", "status": "AUTO", "type_code": "AUTOBIOGRAPHY", "confidence": 1.0, "material_id": 6, "type_source": "DECLARED"}]}	{"extra": [{"title": "入党申请书", "reason": "不在本阶段清单", "material_id": 1}], "items": [{"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [6], "material_type": {"id": 9, "code": "AUTOBIOGRAPHY", "name": "自传"}, "quantity_mode": "FIXED", "requirement_text": "自传", "checklist_item_id": 9, "material_type_name": "自传"}, {"actual": 1, "missing": 0, "expected": 1, "required": true, "material_ids": [5], "material_type": {"id": 10, "code": "CANDIDATE_MEETING_RECORD", "name": "支委会确定发展对象记录"}, "quantity_mode": "FIXED", "requirement_text": "支委会确定发展对象记录", "checklist_item_id": 10, "material_type_name": "支委会确定发展对象记录"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 11, "code": "POLITICAL_REVIEW", "name": "政治审查材料"}, "quantity_mode": "FIXED", "requirement_text": "政治审查材料", "checklist_item_id": 11, "material_type_name": "政治审查材料"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 12, "code": "TRAINING_CERT", "name": "集中培训结业证书"}, "quantity_mode": "FIXED", "requirement_text": "集中培训结业证书", "checklist_item_id": 12, "material_type_name": "集中培训结业证书"}, {"actual": 0, "missing": 1, "expected": 1, "required": true, "material_ids": [], "material_type": {"id": 13, "code": "RECORD_BOOK_CANDIDATE", "name": "写实簿·发展对象考察部分"}, "quantity_mode": "FIXED", "requirement_text": "写实簿发展对象考察部分", "checklist_item_id": 13, "material_type_name": "写实簿·发展对象考察部分"}, {"actual": 3, "missing": 2, "expected": 5, "required": true, "material_ids": [2, 3, 4], "material_type": {"id": 7, "code": "THOUGHT_REPORT", "name": "思想汇报"}, "quantity_mode": "PER_PERIOD", "requirement_text": "每季度至少一份思想汇报", "checklist_item_id": 14, "material_type_name": "思想汇报"}], "stage_code": 3, "is_complete": false, "unclassified": [], "missing_total": 5}	{"nodes": {"D01": null, "T01": "2003-05-12", "T02": "2023-03-15", "T03": "2023-03-20", "T04": "2024-09-10", "T05": null, "T06": "2003-05-12", "T07": null, "T08": "2025-08-30", "T09": null, "T10": null, "T11": null, "T12": null, "T13": null, "T14": null, "T15": null, "T16": null, "T17": null, "T18": null, "T19": null, "T20": null, "T21": null}, "derived": {}}	[{"result": "FAIL", "issue_ids": [], "rule_code": "COMPLETENESS"}, {"result": "PASS", "rule_code": "R-T01"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T02"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T03"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T04"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T05"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T06"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T07"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T08"}, {"reason": "节点缺失", "result": "SKIPPED", "rule_code": "R-T09"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T10"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T11"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T12"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T13"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T14"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T15"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T16"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T17"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T18"}, {"reason": "不适用当前阶段", "result": "SKIPPED", "rule_code": "R-T19"}, {"result": "PASS", "rule_code": "R-T20"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T21"}, {"result": "PASS", "rule_code": "R-T22"}, {"result": "FAIL", "issue_ids": [], "rule_code": "R-T23"}, {"result": "FAIL", "rule_code": "R-F01"}, {"result": "PASS", "rule_code": "R-F02"}, {"result": "PASS", "rule_code": "R-F03"}, {"result": "PASS", "rule_code": "R-F04"}, {"result": "PASS", "rule_code": "R-F05"}, {"result": "FAIL", "rule_code": "R-F06"}, {"result": "PASS", "rule_code": "R-F07"}, {"result": "FAIL", "rule_code": "R-C01"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C02"}, {"result": "PASS", "rule_code": "R-C03"}, {"result": "PASS", "rule_code": "R-C04"}, {"result": "FAIL", "rule_code": "R-C05"}, {"result": "FAIL", "rule_code": "R-C06"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C07"}, {"reason": "需大模型，当前为仅规则模式", "result": "SKIPPED", "rule_code": "R-C08"}]	{"total": 20, "rules_run": 39, "by_category": {"TIME": 5, "FORMAT": 6, "CONTENT": 5, "COMPLETENESS": 4}, "by_severity": {"WARN": 12, "BLOCK": 8}, "rules_failed": 11, "rules_skipped": 18, "needs_judgement": 0, "materials_checked": 6}	SUGGEST_RETURN	\N	\N	\N	2026-10-17 19:17:49.718654+08	2026-10-17 19:17:49.7605+08	41	REQUIRED	\N	["LOW_CONFIDENCE", "KEY_STAGE"]
\.


--
-- Data for Name: archive_time_nodes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.archive_time_nodes (id, archive_id, node_code, value_date, value_end_date, hours, seq_count, source_extraction_id, source_count, has_conflict, corrected_date, corrected_end_date, corrected_hours, correction_reason, corrected_by, corrected_at, locked, locked_stage, updated_at) FROM stdin;
23	2	T01	2003-05-12	\N	\N	2	6	3	t	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
24	2	T02	2023-03-15	\N	\N	2	7	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
25	2	T03	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
26	2	T04	2024-09-10	\N	\N	1	8	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
27	2	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
28	2	T06	2004-01-01	2025-08-01	\N	3	104	3	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
29	2	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
30	2	T08	2025-08-30	\N	\N	1	9	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
31	2	T09	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
32	2	T10	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
33	2	T11	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
34	2	T12	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
35	2	T13	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
36	2	T14	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
37	2	T15	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
38	2	T16	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
39	2	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
40	2	T18	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
41	2	T19	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
42	2	T20	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
45	3	T01	\N	\N	\N	0	106	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
46	3	T02	2023-03-15	\N	\N	2	10	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
47	3	T03	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
48	3	T04	2024-09-10	\N	\N	1	11	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
49	3	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
50	3	T06	2023-03-15	2023-03-15	\N	1	107	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
51	3	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
52	3	T08	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
53	3	T09	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
54	3	T10	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
55	3	T11	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
56	3	T12	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
57	3	T13	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
58	3	T14	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
59	3	T15	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
60	3	T16	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
61	3	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
62	3	T18	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
63	3	T19	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
64	3	T20	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
89	5	T01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
90	5	T02	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
91	5	T03	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
92	5	T04	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
93	5	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
94	5	T06	2025-09-20	2025-10-08	\N	3	130	3	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
95	5	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
96	5	T08	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
97	5	T09	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
98	5	T10	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
99	5	T11	2025-09-25	\N	\N	2	134	2	t	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
100	5	T12	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
101	5	T13	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
102	5	T14	2024-10-01	\N	\N	2	16	2	t	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
103	5	T15	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
104	5	T16	2024-10-20	\N	\N	1	17	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
105	5	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
106	5	T18	2025-09-20	\N	\N	2	18	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
67	4	T01	2003-05-12	\N	\N	1	109	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
68	4	T02	2022-03-15	\N	\N	1	12	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
69	4	T03	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
70	4	T04	2023-04-01	\N	\N	1	13	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
71	4	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
72	4	T06	2024-06-01	2025-06-01	\N	6	110	6	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
73	4	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
74	4	T08	2024-05-01	\N	\N	1	14	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
75	4	T09	2024-06-01	\N	\N	1	115	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
76	4	T10	2024-07-01	2024-07-05	\N	2	117	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
77	4	T11	\N	\N	\N	0	120	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
78	4	T12	2025-05-10	\N	\N	1	124	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
79	4	T13	2025-05-20	\N	\N	1	108	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
80	4	T14	2025-06-01	\N	\N	2	15	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
81	4	T15	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
82	4	T16	2025-06-01	\N	\N	1	113	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
83	4	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
84	4	T18	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
155	8	T01	2003-05-12	\N	\N	2	28	3	t	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
156	8	T02	2023-03-15	\N	\N	2	29	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
111	6	T01	2003-05-12	\N	\N	1	20	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
112	6	T02	2023-03-15	\N	\N	2	21	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
157	8	T03	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
158	8	T04	2024-09-10	\N	\N	1	30	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
159	8	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
160	8	T06	2004-01-01	2025-08-01	\N	3	158	3	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
161	8	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
162	8	T08	2025-08-30	\N	\N	1	31	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
163	8	T09	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
164	8	T10	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
165	8	T11	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
166	8	T12	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
167	8	T13	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
168	8	T14	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
169	8	T15	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
170	8	T16	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
171	8	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
172	8	T18	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
173	8	T19	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
174	8	T20	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
133	7	T01	2003-05-12	\N	\N	2	23	3	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
134	7	T02	2023-03-15	\N	\N	2	24	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
135	7	T03	2023-03-20	\N	\N	1	25	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
136	7	T04	2024-09-10	\N	\N	1	26	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
137	7	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
138	7	T06	2003-05-12	2025-08-30	\N	6	146	6	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
139	7	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
140	7	T08	2025-08-30	\N	\N	2	27	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
141	7	T09	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
142	7	T10	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
143	7	T11	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
144	7	T12	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
145	7	T13	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
146	7	T14	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
147	7	T15	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
148	7	T16	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
149	7	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
150	7	T18	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
151	7	T19	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
152	7	T20	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
177	9	T01	\N	\N	\N	0	161	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
178	9	T02	2023-03-15	\N	\N	2	32	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
179	9	T03	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
180	9	T04	2024-09-10	\N	\N	1	33	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
181	9	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
182	9	T06	2023-03-15	2023-03-15	\N	1	162	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
183	9	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
184	9	T08	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
185	9	T09	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
186	9	T10	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
187	9	T11	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
188	9	T12	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
189	9	T13	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
190	9	T14	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
191	9	T15	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
192	9	T16	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
193	9	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
194	9	T18	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
195	9	T19	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
196	9	T20	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
199	10	T01	2003-05-12	\N	\N	1	164	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
200	10	T02	2022-03-15	\N	\N	1	34	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
201	10	T03	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
202	10	T04	2023-04-01	\N	\N	1	35	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
203	10	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
204	10	T06	2024-06-01	2025-06-01	\N	6	165	6	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
205	10	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
206	10	T08	2024-05-01	\N	\N	1	36	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
207	10	T09	2024-06-01	\N	\N	1	170	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
208	10	T10	2024-07-01	2024-07-05	\N	2	172	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
209	10	T11	\N	\N	\N	0	175	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
210	10	T12	2025-05-10	\N	\N	1	179	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
211	10	T13	2025-05-20	\N	\N	1	163	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
212	10	T14	2025-06-01	\N	\N	2	37	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
213	10	T15	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
227	11	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
287	14	T01	2003-05-12	\N	\N	2	50	3	t	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
288	14	T02	2023-03-15	\N	\N	2	51	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
289	14	T03	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
290	14	T04	2024-09-10	\N	\N	1	52	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
291	14	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
292	14	T06	2004-01-01	2025-08-01	\N	3	211	3	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
293	14	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
294	14	T08	2025-08-30	\N	\N	1	53	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
295	14	T09	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
296	14	T10	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
297	14	T11	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
221	11	T01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
222	11	T02	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
223	11	T03	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
224	11	T04	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
225	11	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
298	14	T12	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
299	14	T13	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
300	14	T14	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
301	14	T15	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
302	14	T16	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
303	14	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
304	14	T18	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
305	14	T19	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
306	14	T20	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
243	12	T01	2003-05-12	\N	\N	1	42	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
244	12	T02	2023-03-15	\N	\N	2	43	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
245	12	T03	2023-03-28	\N	\N	2	44	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
246	12	T04	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
247	12	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
248	12	T06	2023-03-15	2023-03-28	\N	2	197	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
249	12	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
250	12	T08	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
251	12	T09	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
252	12	T10	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
253	12	T11	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
254	12	T12	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
255	12	T13	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
256	12	T14	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
257	12	T15	2023-03-28	\N	\N	1	198	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
258	12	T16	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
259	12	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
260	12	T18	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
261	12	T19	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
265	13	T01	2003-05-12	\N	\N	2	45	3	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
266	13	T02	2023-03-15	\N	\N	2	46	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
267	13	T03	2023-03-20	\N	\N	1	47	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
268	13	T04	2024-09-10	\N	\N	1	48	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
269	13	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
270	13	T06	2003-05-12	2025-08-30	\N	6	203	6	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
271	13	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
272	13	T08	2025-08-30	\N	\N	2	49	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
273	13	T09	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
274	13	T10	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
275	13	T11	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
276	13	T12	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
277	13	T13	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
278	13	T14	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
279	13	T15	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
280	13	T16	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
281	13	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
282	13	T18	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
283	13	T19	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
284	13	T20	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
309	15	T01	\N	\N	\N	0	216	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
310	15	T02	2023-03-15	\N	\N	2	54	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
311	15	T03	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
312	15	T04	2024-09-10	\N	\N	1	55	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
313	15	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
314	15	T06	2023-03-15	2023-03-15	\N	1	217	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
315	15	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
316	15	T08	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
317	15	T09	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
318	15	T10	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
319	15	T11	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
320	15	T12	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
321	15	T13	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
353	17	T01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
354	17	T02	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
355	17	T03	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
356	17	T04	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
357	17	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
358	17	T06	2025-09-20	2025-10-08	\N	3	240	3	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
332	16	T02	2022-03-15	\N	\N	1	56	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
333	16	T03	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
334	16	T04	2023-04-01	\N	\N	1	57	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
335	16	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
336	16	T06	2024-06-01	2025-06-01	\N	6	220	6	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
337	16	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
339	16	T09	2024-06-01	\N	\N	1	225	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
359	17	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
360	17	T08	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
361	17	T09	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
331	16	T01	2003-05-12	\N	\N	1	219	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
362	17	T10	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
363	17	T11	2025-09-25	\N	\N	2	244	2	t	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
364	17	T12	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
365	17	T13	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
366	17	T14	2024-10-01	\N	\N	2	60	2	t	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
367	17	T15	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
368	17	T16	2024-10-20	\N	\N	1	61	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
369	17	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
370	17	T18	2025-09-20	\N	\N	2	62	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
371	17	T19	\N	\N	\N	0	242	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
419	20	T01	2003-05-12	\N	\N	2	72	3	t	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
420	20	T02	2023-03-15	\N	\N	2	73	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
421	20	T03	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
422	20	T04	2024-09-10	\N	\N	1	74	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
423	20	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
424	20	T06	2004-01-01	2025-08-01	\N	3	268	3	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
425	20	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
426	20	T08	2025-08-30	\N	\N	1	75	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
427	20	T09	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
428	20	T10	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
397	19	T01	2003-05-12	\N	\N	2	67	3	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
375	18	T01	2003-05-12	\N	\N	1	64	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
376	18	T02	2023-03-15	\N	\N	2	65	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
377	18	T03	2023-03-28	\N	\N	2	66	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
378	18	T04	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
379	18	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
380	18	T06	2023-03-15	2023-03-28	\N	2	252	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
381	18	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
382	18	T08	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
383	18	T09	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
384	18	T10	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
385	18	T11	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
386	18	T12	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
387	18	T13	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
388	18	T14	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
389	18	T15	2023-03-28	\N	\N	1	253	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
390	18	T16	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
391	18	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
392	18	T18	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
393	18	T19	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
394	18	T20	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
398	19	T02	2023-03-15	\N	\N	2	68	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
399	19	T03	2023-03-20	\N	\N	1	69	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
400	19	T04	2024-09-10	\N	\N	1	70	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
401	19	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
402	19	T06	2003-05-12	2025-08-30	\N	6	256	6	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
403	19	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
404	19	T08	2025-08-30	\N	\N	2	71	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
405	19	T09	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
406	19	T10	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
407	19	T11	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
408	19	T12	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
409	19	T13	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
410	19	T14	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
411	19	T15	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
412	19	T16	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
413	19	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
414	19	T18	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
415	19	T19	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
429	20	T11	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
430	20	T12	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
431	20	T13	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
432	20	T14	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
433	20	T15	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
434	20	T16	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
435	20	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
441	21	T01	\N	\N	\N	0	271	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
442	21	T02	2023-03-15	\N	\N	2	76	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
443	21	T03	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
444	21	T04	2024-09-10	\N	\N	1	77	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
445	21	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
446	21	T06	2023-03-15	2023-03-15	\N	1	272	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
447	21	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
448	21	T08	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
449	21	T09	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
450	21	T10	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
485	23	T01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
486	23	T02	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
487	23	T03	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
488	23	T04	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
489	23	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
490	23	T06	2025-09-20	2025-10-08	\N	3	292	3	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
491	23	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
492	23	T08	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
493	23	T09	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
494	23	T10	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
495	23	T11	2025-09-25	\N	\N	2	299	2	t	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
496	23	T12	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
497	23	T13	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
498	23	T14	2024-10-01	\N	\N	2	82	2	t	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
499	23	T15	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
500	23	T16	2024-10-20	\N	\N	1	83	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
501	23	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
502	23	T18	2025-09-20	\N	\N	2	84	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
463	22	T01	2003-05-12	\N	\N	1	274	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
464	22	T02	2022-03-15	\N	\N	1	78	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
465	22	T03	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
466	22	T04	2023-04-01	\N	\N	1	79	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
467	22	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
468	22	T06	2024-06-01	2025-06-01	\N	6	275	6	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
469	22	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
470	22	T08	2024-05-01	\N	\N	1	80	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
471	22	T09	2024-06-01	\N	\N	1	280	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
472	22	T10	2024-07-01	2024-07-05	\N	2	282	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
473	22	T11	\N	\N	\N	0	285	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
474	22	T12	2025-05-10	\N	\N	1	289	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
475	22	T13	2025-05-20	\N	\N	1	273	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
476	22	T14	2025-06-01	\N	\N	2	81	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
477	22	T15	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
478	22	T16	2025-06-01	\N	\N	1	278	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
479	22	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
480	22	T18	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
503	23	T19	\N	\N	\N	0	297	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
505	23	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
507	24	T01	2003-05-12	\N	\N	1	86	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
508	24	T02	2023-03-15	\N	\N	2	87	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
509	24	T03	2023-03-28	\N	\N	2	88	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
510	24	T04	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
511	24	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
512	24	T06	2023-03-15	2023-03-28	\N	2	305	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
513	24	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
514	24	T08	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
515	24	T09	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
516	24	T10	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
517	24	T11	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
518	24	T12	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
519	24	T13	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
520	24	T14	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
521	24	T15	2023-03-28	\N	\N	1	308	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
522	24	T16	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
523	24	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
524	24	T18	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
525	24	T19	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
526	24	T20	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
86	4	T20	2025-06-01	\N	\N	1	114	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
87	4	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
88	4	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
262	12	T20	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
107	5	T19	\N	\N	\N	0	132	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
108	5	T20	2025-10-08	\N	\N	5	19	5	t	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
1	1	T01	2003-05-12	\N	\N	2	1	3	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
2	1	T02	2023-03-15	\N	\N	2	2	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
3	1	T03	2023-03-20	\N	\N	1	3	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
4	1	T04	2024-09-10	\N	\N	1	4	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
5	1	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
6	1	T06	2003-05-12	2025-08-30	\N	6	91	6	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
7	1	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
8	1	T08	2025-08-30	\N	\N	2	5	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
9	1	T09	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
10	1	T10	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
11	1	T11	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
12	1	T12	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
13	1	T13	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
14	1	T14	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
15	1	T15	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
16	1	T16	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
17	1	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
18	1	T18	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
19	1	T19	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
20	1	T20	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
21	1	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
22	1	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.070146+08
109	5	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
110	5	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.701623+08
113	6	T03	2023-03-28	\N	\N	2	22	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
114	6	T04	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
115	6	T05	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
116	6	T06	2023-03-15	2023-03-28	\N	2	142	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
117	6	T07	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
118	6	T08	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
119	6	T09	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
120	6	T10	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
121	6	T11	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
122	6	T12	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
123	6	T13	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
124	6	T14	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
43	2	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
44	2	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.283133+08
65	3	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
66	3	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.335665+08
125	6	T15	2023-03-28	\N	\N	1	143	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
126	6	T16	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
127	6	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
128	6	T18	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
129	6	T19	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
130	6	T20	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
131	6	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
132	6	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.83434+08
153	7	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
154	7	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.058438+08
85	4	T19	2025-04-20	\N	\N	2	122	2	t	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:16.56473+08
285	13	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
286	13	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.048617+08
322	15	T14	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
175	8	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
176	8	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.198706+08
197	9	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
198	9	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.308864+08
323	15	T15	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
214	10	T16	2025-06-01	\N	\N	1	168	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
215	10	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
216	10	T18	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
217	10	T19	2025-04-20	\N	\N	2	177	2	t	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
218	10	T20	2025-06-01	\N	\N	1	169	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
307	14	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
308	14	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.200117+08
324	15	T16	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
325	15	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
326	15	T18	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
226	11	T06	2025-09-20	2025-10-08	\N	3	185	3	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
228	11	T08	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
229	11	T09	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
230	11	T10	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
219	10	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
220	10	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.530324+08
231	11	T11	2025-09-25	\N	\N	2	189	2	t	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
232	11	T12	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
233	11	T13	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
234	11	T14	2024-10-01	\N	\N	2	38	2	t	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
235	11	T15	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
236	11	T16	2024-10-20	\N	\N	1	39	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
237	11	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
238	11	T18	2025-09-20	\N	\N	2	40	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
239	11	T19	\N	\N	\N	0	187	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
240	11	T20	2025-10-08	\N	\N	5	41	5	t	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
327	15	T19	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
328	15	T20	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
329	15	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
330	15	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.286026+08
241	11	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
242	11	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.678206+08
263	12	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
264	12	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:17.807089+08
481	22	T19	2025-04-20	\N	\N	2	287	2	t	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
483	22	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
484	22	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
504	23	T20	2025-10-08	\N	\N	5	85	5	t	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
342	16	T12	2025-05-10	\N	\N	1	234	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
343	16	T13	2025-05-20	\N	\N	1	218	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
344	16	T14	2025-06-01	\N	\N	2	59	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
345	16	T15	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
346	16	T16	2025-06-01	\N	\N	1	223	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
347	16	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
348	16	T18	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
349	16	T19	2025-04-20	\N	\N	2	232	2	t	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
350	16	T20	2025-06-01	\N	\N	1	224	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
351	16	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
352	16	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
416	19	T20	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
417	19	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
418	19	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.043316+08
338	16	T08	2024-05-01	\N	\N	1	58	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
340	16	T10	2024-07-01	2024-07-05	\N	2	227	2	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
341	16	T11	\N	\N	\N	0	230	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.519366+08
372	17	T20	2025-10-08	\N	\N	5	63	5	t	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
373	17	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
374	17	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.659499+08
395	18	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
396	18	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:18.792186+08
436	20	T18	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
437	20	T19	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
438	20	T20	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
439	20	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
440	20	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.179992+08
451	21	T11	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
452	21	T12	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
453	21	T13	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
454	21	T14	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
455	21	T15	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
456	21	T16	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
457	21	T17	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
458	21	T18	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
459	21	T19	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
460	21	T20	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
461	21	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
462	21	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.267079+08
482	22	T20	2025-06-01	\N	\N	1	279	1	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.505521+08
506	23	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.655451+08
527	24	T21	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
528	24	D01	\N	\N	\N	0	\N	0	f	\N	\N	\N	\N	\N	\N	f	\N	2026-10-17 18:36:19.803078+08
\.


--
-- Data for Name: archives; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.archives (id, student_user_id, student_no, real_name, gender, ethnicity, birth_date, native_place, id_card_enc, id_card_masked, major, class_name, college_id, branch_id, batch_id, current_stage, status, profile_extra, anon_code, data_source, is_demo, timeline_updated_at, created_by, created_at, updated_at) FROM stdin;
6	16	D2023006	演示学生06	男	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2302	2	4	1	1	ACTIVE	{}	ANON0006	DEMO	t	2026-10-17 18:36:16.87833+08	1	2026-10-17 18:36:00.992376+08	2026-10-17 18:36:16.83434+08
7	17	D2023007	演示学生07	女	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2303	2	4	1	3	ACTIVE	{}	ANON0007	DEMO	t	2026-10-17 18:36:17.136965+08	1	2026-10-17 18:36:01.157964+08	2026-10-17 18:36:17.058438+08
8	18	D2023008	演示学生08	男	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2304	2	4	1	3	ACTIVE	{}	ANON0008	DEMO	t	2026-10-17 18:36:17.301852+08	1	2026-10-17 18:36:01.321823+08	2026-10-17 18:36:17.198706+08
9	19	D2023009	演示学生09	女	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2301	2	5	1	2	ACTIVE	{}	ANON0009	DEMO	t	2026-10-17 18:36:17.376447+08	1	2026-10-17 18:36:01.48673+08	2026-10-17 18:36:17.308864+08
1	11	D2023001	演示学生01	女	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2301	2	3	1	3	ACTIVE	{}	ANON0001	DEMO	t	2026-10-17 18:36:16.158895+08	1	2026-10-17 18:36:00.157448+08	2026-10-17 18:36:16.070146+08
2	12	D2023002	演示学生02	男	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2302	2	3	1	3	ACTIVE	{}	ANON0002	DEMO	t	2026-10-17 18:36:16.33053+08	1	2026-10-17 18:36:00.324111+08	2026-10-17 18:36:16.283133+08
3	13	D2023003	演示学生03	女	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2303	2	3	1	2	ACTIVE	{}	ANON0003	DEMO	t	2026-10-17 18:36:16.38317+08	1	2026-10-17 18:36:00.491616+08	2026-10-17 18:36:16.335665+08
10	20	D2023010	演示学生10	男	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2302	2	5	1	4	ACTIVE	{}	ANON0010	DEMO	t	2026-10-17 18:36:17.609582+08	1	2026-10-17 18:36:01.651523+08	2026-10-17 18:36:17.530324+08
4	14	D2023004	演示学生04	男	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2304	2	3	1	4	ACTIVE	{}	ANON0004	DEMO	t	2026-10-17 18:36:16.641885+08	1	2026-10-17 18:36:00.660358+08	2026-10-17 18:36:16.56473+08
11	21	D2023011	演示学生11	女	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2303	2	5	1	5	ACTIVE	{}	ANON0011	DEMO	t	2026-10-17 18:36:17.754785+08	1	2026-10-17 18:36:01.823284+08	2026-10-17 18:36:17.678206+08
5	15	D2023005	演示学生05	女	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2301	2	4	1	5	ACTIVE	{}	ANON0005	DEMO	t	2026-10-17 18:36:16.78147+08	1	2026-10-17 18:36:00.824726+08	2026-10-17 18:36:16.701623+08
22	32	D2023022	演示学生22	男	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2302	6	9	1	4	ACTIVE	{}	ANON0022	DEMO	t	2026-10-17 18:36:19.590451+08	1	2026-10-17 18:36:03.669635+08	2026-10-17 18:36:19.505521+08
12	22	D2023012	演示学生12	男	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2304	2	5	1	1	ACTIVE	{}	ANON0012	DEMO	t	2026-10-17 18:36:17.853176+08	1	2026-10-17 18:36:01.990047+08	2026-10-17 18:36:17.807089+08
17	27	D2023017	演示学生17	女	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2301	6	8	1	5	ACTIVE	{}	ANON0017	DEMO	t	2026-10-17 18:36:18.739348+08	1	2026-10-17 18:36:02.831342+08	2026-10-17 18:36:18.659499+08
18	28	D2023018	演示学生18	男	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2302	6	8	1	1	ACTIVE	{}	ANON0018	DEMO	t	2026-10-17 18:36:18.838654+08	1	2026-10-17 18:36:03.000731+08	2026-10-17 18:36:18.792186+08
23	33	D2023023	演示学生23	女	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2303	6	9	1	5	ACTIVE	{}	ANON0023	DEMO	t	2026-10-17 18:36:19.750648+08	1	2026-10-17 18:36:03.837492+08	2026-10-17 18:36:19.655451+08
13	23	D2023013	演示学生13	女	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2301	6	7	1	3	ACTIVE	{}	ANON0013	DEMO	t	2026-10-17 18:36:18.132653+08	1	2026-10-17 18:36:02.154702+08	2026-10-17 18:36:18.048617+08
24	34	D2023024	演示学生24	男	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2304	6	9	1	1	ACTIVE	{}	ANON0024	DEMO	t	2026-10-17 18:36:19.849544+08	1	2026-10-17 18:36:04.035246+08	2026-10-17 18:36:19.803078+08
14	24	D2023014	演示学生14	男	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2302	6	7	1	3	ACTIVE	{}	ANON0014	DEMO	t	2026-10-17 18:36:18.280709+08	1	2026-10-17 18:36:02.325139+08	2026-10-17 18:36:18.200117+08
15	25	D2023015	演示学生15	女	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2303	6	7	1	2	ACTIVE	{}	ANON0015	DEMO	t	2026-10-17 18:36:18.350891+08	1	2026-10-17 18:36:02.493692+08	2026-10-17 18:36:18.286026+08
19	29	D2023019	演示学生19	女	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2303	6	8	1	3	ACTIVE	{}	ANON0019	DEMO	t	2026-10-17 18:36:19.112044+08	1	2026-10-17 18:36:03.170063+08	2026-10-17 18:36:19.043316+08
20	30	D2023020	演示学生20	男	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2304	6	8	1	3	ACTIVE	{}	ANON0020	DEMO	t	2026-10-17 18:36:19.261079+08	1	2026-10-17 18:36:03.34086+08	2026-10-17 18:36:19.179992+08
16	26	D2023016	演示学生16	男	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2304	6	7	1	4	ACTIVE	{}	ANON0016	DEMO	t	2026-10-17 18:36:18.59878+08	1	2026-10-17 18:36:02.66173+08	2026-10-17 18:36:18.519366+08
21	31	D2023021	演示学生21	女	汉族	2003-05-12	湖北武汉	\N	\N	计算机科学与技术	计科 2301	6	9	1	2	ACTIVE	{}	ANON0021	DEMO	t	2026-10-17 18:36:19.324434+08	1	2026-10-17 18:36:03.506738+08	2026-10-17 18:36:19.267079+08
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.audit_logs (id, user_id, username, role, action, object_type, object_id, detail, ip, user_agent, created_at) FROM stdin;
1	1	admin	\N	LOGIN	user	1	{}	127.0.0.1	curl/8.21.0	2026-10-17 18:30:37.283556+08
2	1	admin	\N	LOGIN	user	1	{}	127.0.0.1	curl/8.21.0	2026-10-17 18:31:09.298582+08
3	1	admin	\N	LOGIN	user	1	{}	127.0.0.1	curl/8.21.0	2026-10-17 18:35:58.346789+08
4	1	admin	SYS_ADMIN	SEED_DEMO	demo	\N	{"reset": false}	127.0.0.1	curl/8.21.0	2026-10-17 18:36:15.162963+08
5	\N	\N	\N	LOGIN_FAILED	user	1	{"remain": 4, "username": "admin"}	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36 Edg/155.0.0.0	2026-10-17 18:37:16.435135+08
6	\N	\N	\N	LOGIN_FAILED	user	1	{"remain": 3, "username": "admin"}	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36 Edg/155.0.0.0	2026-10-17 18:42:59.176854+08
7	11	demo_stu01	\N	LOGIN	user	11	{}	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/155.0.0.0 Safari/537.36	2026-10-17 18:44:31.168303+08
8	5	demo_branch1	\N	LOGIN	user	5	{}	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/155.0.0.0 Safari/537.36	2026-10-17 18:44:54.056796+08
9	1	admin	\N	LOGIN	user	1	{}	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/155.0.0.0 Safari/537.36	2026-10-17 18:45:12.412257+08
10	1	admin	\N	LOGIN	user	1	{}	127.0.0.1	curl/8.21.0	2026-10-17 18:45:53.628568+08
11	11	demo_stu01	\N	LOGIN	user	11	{}	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/155.0.0.0 Safari/537.36	2026-10-17 18:47:18.431647+08
12	5	demo_branch1	\N	LOGIN	user	5	{}	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/155.0.0.0 Safari/537.36	2026-10-17 18:47:40.892043+08
13	11	demo_stu01	\N	LOGIN	user	11	{}	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/155.0.0.0 Safari/537.36	2026-10-17 18:48:32.279462+08
40	5	demo_branch1	\N	LOGIN	user	5	{}	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36 Edg/155.0.0.0	2026-10-17 18:52:50.018668+08
41	5	demo_branch1	BRANCH_REVIEWER	AI_CHECK	submission	8	{}	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36 Edg/155.0.0.0	2026-10-17 18:53:07.90141+08
42	11	demo_stu01	\N	LOGIN	user	11	{}	127.0.0.1	curl/8.21.0	2026-10-17 18:53:42.501493+08
43	1	admin	\N	LOGIN	user	1	{}	127.0.0.1	curl/8.21.0	2026-10-17 18:55:44.6426+08
44	1	admin	\N	LOGIN	user	1	{}	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/155.0.0.0 Safari/537.36	2026-10-17 18:56:40.488338+08
45	2	demo_org	\N	LOGIN	user	2	{}	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/155.0.0.0 Safari/537.36	2026-10-17 18:57:11.430175+08
46	11	demo_stu01	\N	LOGIN	user	11	{}	127.0.0.1	curl/8.21.0	2026-10-17 19:11:25.933084+08
47	5	demo_branch1	BRANCH_REVIEWER	AI_CHECK	submission	3	{}	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36 Edg/155.0.0.0	2026-10-17 19:17:49.104141+08
48	2	demo_org	\N	LOGIN	user	2	{}	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/155.0.0.0 Safari/537.36	2026-10-17 19:18:09.854721+08
49	1	admin	\N	LOGIN	user	1	{}	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/155.0.0.0 Safari/537.36	2026-10-17 19:18:42.04957+08
50	5	demo_branch1	\N	LOGIN	user	5	{}	127.0.0.1	curl/8.21.0	2026-10-17 19:19:06.547659+08
59	2	demo_org	\N	LOGIN	user	2	{}	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/155.0.0.0 Safari/537.36	2026-10-17 19:30:26.920253+08
\.


--
-- Data for Name: batch_upload_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.batch_upload_items (id, job_id, entry_path, temp_path, file_size, parsed_student_no, parsed_type_hint, matched_archive_id, match_method, material_type_id, status, material_id, error, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: batches; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.batches (id, name, year, term, stage_codes, description, start_date, end_date, self_deadline, branch_deadline, cross_deadline, college_deadline, org_deadline, status, is_demo, created_by, created_at, updated_at) FROM stdin;
1	2026 年度发展批次（演示）	2026	FULL_YEAR	[1, 2, 3, 4, 5]	\N	2026-01-01	2026-12-31	2026-10-18	2026-10-21	2026-10-25	2026-10-28	2026-11-05	ACTIVE	t	1	2026-10-17 18:35:59.981283+08	2026-10-17 18:35:59.981283+08
\.


--
-- Data for Name: check_rules; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.check_rules (id, code, category, name, engine, applies_to, params, severity, needs_human_judgement, basis, message_template, suggestion_template_id, is_optional, is_active, sort_order, updated_by, created_at, updated_at) FROM stdin;
1	R-F01	FORMAT	文书结构完整	RULE	[]	{"elements": ["title", "salutation", "body", "closing", "signature", "date"]}	WARN	f	学校党员发展材料规范	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	t	1	\N	2026-10-17 18:29:29.452615+08	2026-10-17 18:29:29.452617+08
2	R-F02	FORMAT	落款日期格式	RULE	[]	{}	WARN	f	学校党员发展材料规范	落款日期未按“××××年××月××日”书写	\N	f	t	2	\N	2026-10-17 18:29:29.452671+08	2026-10-17 18:29:29.452671+08
3	R-F03	FORMAT	签名齐全	RULE	[]	{}	BLOCK	f	学校党员发展材料规范	规定签名位未检测到签名	\N	f	t	3	\N	2026-10-17 18:29:29.452692+08	2026-10-17 18:29:29.452692+08
4	R-F04	FORMAT	印章齐全	RULE	[]	{}	BLOCK	f	学校党员发展材料规范	规定盖章位未检测到党组织印章	\N	f	t	4	\N	2026-10-17 18:29:29.45271+08	2026-10-17 18:29:29.45271+08
5	R-F05	FORMAT	手写材料可辨识	RULE	["RECORD_BOOK_ACTIVIST", "RECORD_BOOK_CANDIDATE", "RECORD_BOOK_PROBATIONARY"]	{}	WARN	f	学校党员发展材料规范	写实簿等手写材料清晰度不足或文本过少	\N	f	t	5	\N	2026-10-17 18:29:29.452725+08	2026-10-17 18:29:29.452725+08
6	R-F06	FORMAT	篇幅下限	RULE	["AUTOBIOGRAPHY"]	{"min_chars": {"AUTOBIOGRAPHY": 3000}}	WARN	f	学校党员发展材料规范	材料正文字数不足规定篇幅	\N	f	t	6	\N	2026-10-17 18:29:29.45274+08	2026-10-17 18:29:29.452741+08
7	R-F07	FORMAT	扫描件清晰度	RULE	[]	{"min_dpi": 150, "blur_threshold": 60}	WARN	f	学校党员发展材料规范	扫描件分辨率不足或页面模糊	\N	f	t	7	\N	2026-10-17 18:29:29.452756+08	2026-10-17 18:29:29.452756+08
8	R-F08	FORMAT	版式规范	RULE	[]	{"docx_layout": {"font": "宋体", "size_pt": 12, "margin_cm": 2.54, "line_spacing": 1.5}}	INFO	f	学校党员发展材料规范	DOCX 字体、字号、行距或页边距与学校模板不一致	\N	t	f	8	\N	2026-10-17 18:29:29.452771+08	2026-10-17 18:29:29.452771+08
9	R-F09	FORMAT	页面方向与装订	RULE	[]	{}	INFO	f	学校党员发展材料规范	页面方向或装订边距不符合归档要求	\N	t	f	9	\N	2026-10-17 18:29:29.452786+08	2026-10-17 18:29:29.452786+08
10	R-C01	CONTENT	政治术语规范	RULE	[]	{}	WARN	f	党章及发展党员工作细则；学校审核标准	出现不规范政治术语或并列顺序错误	\N	f	t	10	\N	2026-10-17 18:29:29.452804+08	2026-10-17 18:29:29.452804+08
11	R-C02	CONTENT	政治表述准确性	LLM	[]	{}	WARN	t	党章及发展党员工作细则；学校审核标准	政治理论表述疑似不准确，请审核员研判	\N	f	t	11	\N	2026-10-17 18:29:29.45282+08	2026-10-17 18:29:29.452821+08
12	R-C03	CONTENT	意识形态表述	RULE_LLM	[]	{}	BLOCK	t	党章及发展党员工作细则；学校审核标准	疑似存在需研判的意识形态表述	\N	f	t	12	\N	2026-10-17 18:29:29.452836+08	2026-10-17 18:29:29.452836+08
13	R-C04	CONTENT	入党动机表述	RULE_LLM	["APPLICATION_LETTER", "THOUGHT_REPORT", "REGULARIZATION_LETTER"]	{}	WARN	t	党章及发展党员工作细则；学校审核标准	入党动机表述疑似功利化或要素不足	\N	f	t	13	\N	2026-10-17 18:29:29.452851+08	2026-10-17 18:29:29.452851+08
14	R-C05	CONTENT	内容要素完整	RULE	[]	{}	WARN	f	党章及发展党员工作细则；学校审核标准	材料缺少模板规定的内容要素	\N	f	t	14	\N	2026-10-17 18:29:29.452866+08	2026-10-17 18:29:29.452866+08
15	R-C06	CONTENT	基本信息一致	RULE	[]	{}	BLOCK	f	党章及发展党员工作细则；学校审核标准	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	t	15	\N	2026-10-17 18:29:29.452881+08	2026-10-17 18:29:29.452881+08
16	R-C07	CONTENT	经历与时间线吻合	LLM	["AUTOBIOGRAPHY", "APPLICATION_LETTER"]	{}	WARN	t	党章及发展党员工作细则；学校审核标准	自传或申请书经历与时间节点疑似矛盾	\N	f	t	16	\N	2026-10-17 18:29:29.452896+08	2026-10-17 18:29:29.452896+08
17	R-C08	CONTENT	思想认识深度	LLM	["THOUGHT_REPORT", "AUTOBIOGRAPHY"]	{}	INFO	t	党章及发展党员工作细则；学校审核标准	思想认识表述较空泛，建议结合学习与实践写实	\N	f	t	17	\N	2026-10-17 18:29:29.452911+08	2026-10-17 18:29:29.452911+08
18	R-C09	CONTENT	引用原文核对	RULE	[]	{}	INFO	f	党章及发展党员工作细则；学校审核标准	疑似错误引用党章或重要文献原文	\N	t	f	18	\N	2026-10-17 18:29:29.452928+08	2026-10-17 18:29:29.452928+08
19	R-C10	CONTENT	同批次文本高度相似	RULE	["THOUGHT_REPORT", "AUTOBIOGRAPHY", "APPLICATION_LETTER"]	{"threshold": 0.8}	WARN	f	党章及发展党员工作细则；学校审核标准	与同批次其他学生材料文本高度相似	\N	t	f	19	\N	2026-10-17 18:29:29.452943+08	2026-10-17 18:29:29.452943+08
\.


--
-- Data for Name: checklist_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.checklist_items (id, stage_code, material_type_id, quantity_mode, fixed_count, period_months, period_start_node, period_end_node, is_required, requirement_text, sort_order, is_active, updated_by, created_at, updated_at) FROM stdin;
1	1	1	FIXED	1	\N	\N	\N	t	本人亲笔或打印后签字的入党申请书	1	t	\N	2026-10-17 18:29:29.422241+08	2026-10-17 18:29:29.422242+08
2	1	2	FIXED	1	\N	\N	\N	t	党组织派人谈话记录	2	t	\N	2026-10-17 18:29:29.422955+08	2026-10-17 18:29:29.422955+08
3	2	3	FIXED	1	\N	\N	\N	t	党员推荐或团组织推优材料	3	t	\N	2026-10-17 18:29:29.423417+08	2026-10-17 18:29:29.423417+08
4	2	4	FIXED	1	\N	\N	\N	t	支委会（支部大会）研究确定积极分子记录	4	t	\N	2026-10-17 18:29:29.423816+08	2026-10-17 18:29:29.423817+08
5	2	5	FIXED	1	\N	\N	\N	t	积极分子备案材料	5	t	\N	2026-10-17 18:29:29.424189+08	2026-10-17 18:29:29.424189+08
6	2	6	FIXED	1	\N	\N	\N	t	写实簿积极分子培养考察部分	6	t	\N	2026-10-17 18:29:29.424639+08	2026-10-17 18:29:29.424639+08
7	2	7	PER_PERIOD	0	3	T04	T08	t	每季度至少一份思想汇报	7	t	\N	2026-10-17 18:29:29.424988+08	2026-10-17 18:29:29.424989+08
8	2	8	FIXED	1	\N	\N	\N	f	积极分子培训结业证明（可选）	8	t	\N	2026-10-17 18:29:29.425322+08	2026-10-17 18:29:29.425323+08
9	3	9	FIXED	1	\N	\N	\N	t	自传	9	t	\N	2026-10-17 18:29:29.425652+08	2026-10-17 18:29:29.425653+08
10	3	10	FIXED	1	\N	\N	\N	t	支委会确定发展对象记录	10	t	\N	2026-10-17 18:29:29.426091+08	2026-10-17 18:29:29.426092+08
11	3	11	FIXED	1	\N	\N	\N	t	政治审查材料	11	t	\N	2026-10-17 18:29:29.426534+08	2026-10-17 18:29:29.426535+08
12	3	12	FIXED	1	\N	\N	\N	t	集中培训结业证书	12	t	\N	2026-10-17 18:29:29.426944+08	2026-10-17 18:29:29.426945+08
13	3	13	FIXED	1	\N	\N	\N	t	写实簿发展对象考察部分	13	t	\N	2026-10-17 18:29:29.427307+08	2026-10-17 18:29:29.427308+08
14	3	7	PER_PERIOD	0	3	T08	T14	t	每季度至少一份思想汇报	14	t	\N	2026-10-17 18:29:29.427635+08	2026-10-17 18:29:29.427636+08
15	4	14	FIXED	1	\N	\N	\N	t	发展对象公示材料	15	t	\N	2026-10-17 18:29:29.427946+08	2026-10-17 18:29:29.427947+08
16	4	15	FIXED	1	\N	\N	\N	t	上级党委预审意见	16	t	\N	2026-10-17 18:29:29.428243+08	2026-10-17 18:29:29.428243+08
17	4	16	FIXED	1	\N	\N	\N	t	入党志愿书	17	t	\N	2026-10-17 18:29:29.428537+08	2026-10-17 18:29:29.428538+08
18	4	17	FIXED	1	\N	\N	\N	t	支部大会讨论接收预备党员记录	18	t	\N	2026-10-17 18:29:29.428826+08	2026-10-17 18:29:29.428826+08
19	4	18	FIXED	1	\N	\N	\N	t	上级党委派人谈话记录	19	t	\N	2026-10-17 18:29:29.429116+08	2026-10-17 18:29:29.429117+08
20	4	19	FIXED	1	\N	\N	\N	t	上级党委审批意见	20	t	\N	2026-10-17 18:29:29.4294+08	2026-10-17 18:29:29.429401+08
21	5	20	FIXED	1	\N	\N	\N	t	转正申请书	21	t	\N	2026-10-17 18:29:29.429683+08	2026-10-17 18:29:29.429683+08
22	5	21	FIXED	1	\N	\N	\N	t	写实簿预备党员考察部分	22	t	\N	2026-10-17 18:29:29.430001+08	2026-10-17 18:29:29.430002+08
23	5	22	FIXED	1	\N	\N	\N	t	转正公示材料	23	t	\N	2026-10-17 18:29:29.430438+08	2026-10-17 18:29:29.430439+08
24	5	23	FIXED	1	\N	\N	\N	t	支部大会讨论转正记录	24	t	\N	2026-10-17 18:29:29.430952+08	2026-10-17 18:29:29.430953+08
25	5	24	FIXED	1	\N	\N	\N	t	上级党委审批转正意见	25	t	\N	2026-10-17 18:29:29.43132+08	2026-10-17 18:29:29.431321+08
26	5	7	PER_PERIOD	0	3	T14	T20	t	预备期每季度至少一份思想汇报	26	t	\N	2026-10-17 18:29:29.431644+08	2026-10-17 18:29:29.431644+08
\.


--
-- Data for Name: cross_review_pairs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.cross_review_pairs (id, batch_id, college_id, target_branch_id, reviewer_branch_id, reviewer_user_id, created_by, created_at) FROM stdin;
1	1	2	3	4	\N	1	2026-10-17 18:35:59.985696+08
2	1	2	4	5	\N	1	2026-10-17 18:35:59.985777+08
3	1	2	5	3	\N	1	2026-10-17 18:35:59.985803+08
4	1	6	7	8	\N	1	2026-10-17 18:35:59.985827+08
5	1	6	8	9	\N	1	2026-10-17 18:35:59.985846+08
6	1	6	9	7	\N	1	2026-10-17 18:35:59.985864+08
\.


--
-- Data for Name: export_files; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.export_files (id, export_type, params, file_name, stored_path, row_count, created_by, created_at, expires_at) FROM stdin;
\.


--
-- Data for Name: handover_records; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.handover_records (id, report_id, submission_id, assignee_id, assignee_name, assignee_role, reason_codes, handover_reason, ai_recommendation, human_decision, effective_recommendation, issue_ids, material_ids, confidence_snapshot, decided_at, ip) FROM stdin;
\.


--
-- Data for Name: issues; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.issues (id, submission_id, report_id, material_id, material_version_id, source, category, severity, rule_code, rule_basis, title, description, location, actual_value, expected_value, suggestion, suggestion_example, needs_human_judgement, confidence, fingerprint, is_active, review_status, review_level, reviewed_by, reviewed_at, review_note, original_snapshot, created_by, created_level, response_type, response_text, response_version_id, responded_at, resolution, resolved_by_report_id, prev_issue_id, is_new_in_recheck, created_at, updated_at) FROM stdin;
21	6	2	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《支委会确定发展对象记录》	应交 1 份，已交 0 份，缺少 1 份。支委会确定发展对象记录	{"checklist_item_id": 10}	0	1	缺少《支委会确定发展对象记录》1 份（应交 1 份，已交 0 份）。请按要求补交：支委会确定发展对象记录。	\N	f	0.9	a14816de9623777c76f088d00e203aacbffdcf09	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.38952+08	2026-10-17 18:36:16.389522+08
22	6	2	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《政治审查材料》	应交 1 份，已交 0 份，缺少 1 份。政治审查材料	{"checklist_item_id": 11}	0	1	缺少《政治审查材料》1 份（应交 1 份，已交 0 份）。请按要求补交：政治审查材料。	\N	f	0.9	d54d125051786d628b7f668fff5b64c9c77fe60c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.389615+08	2026-10-17 18:36:16.389615+08
23	6	2	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《集中培训结业证书》	应交 1 份，已交 0 份，缺少 1 份。集中培训结业证书	{"checklist_item_id": 12}	0	1	缺少《集中培训结业证书》1 份（应交 1 份，已交 0 份）。请按要求补交：集中培训结业证书。	\N	f	0.9	ffaca8c9d99a22a690909577b59c36cfe00ded4e	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.38967+08	2026-10-17 18:36:16.38967+08
24	6	2	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《写实簿·发展对象考察部分》	应交 1 份，已交 0 份，缺少 1 份。写实簿发展对象考察部分	{"checklist_item_id": 13}	0	1	缺少《写实簿·发展对象考察部分》1 份（应交 1 份，已交 0 份）。请按要求补交：写实簿发展对象考察部分。	\N	f	0.9	f3ce00a714e76e4da498f001d62fdeb73595ba39	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.389717+08	2026-10-17 18:36:16.389718+08
25	6	2	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《思想汇报》	应交 5 份，已交 1 份，缺少 4 份。每季度至少一份思想汇报	{"checklist_item_id": 14}	1	5	缺少《思想汇报》4 份（应交 5 份，已交 1 份）。请按要求补交：每季度至少一份思想汇报。	\N	f	0.9	3ecf2968464ecbacc34ba93a0b7fa3bee2237bdc	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.389763+08	2026-10-17 18:36:16.389763+08
26	6	2	\N	\N	AI_RULE	TIME	BLOCK	R-T05	中国共产党发展党员工作细则	积极分子培养满一年	间隔 11 个月 20 天，不足 1 YEAR	{"node_code": "T08"}	11 个月 20 天	≥ 1 YEAR	《》中T08为 11 个月 20 天，不符合“积极分子培养满一年”要求（≥ 1 YEAR）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	88b2a22720c273901ff055f427fad5d6a9b9ab4c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.389812+08	2026-10-17 18:36:16.389812+08
27	6	2	\N	\N	AI_RULE	TIME	WARN	R-T06	中国共产党发展党员工作细则	思想汇报相邻间隔	相邻间隔超过 3 MONTH	{}	1 处超间隔	相邻 ≤ 3 MONTH	《》中为 1 处超间隔，不符合“思想汇报相邻间隔”要求（相邻 ≤ 3 MONTH）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	d573fe8a048c5e4f4037f87661fbd9447c785a91	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.389852+08	2026-10-17 18:36:16.389852+08
28	6	2	\N	\N	AI_RULE	TIME	BLOCK	R-T07	中国共产党发展党员工作细则	思想汇报按期提交	3 个周期不足	{}	实交 3 份 / 4 个周期	每周期至少 1 份	《》中为 实交 3 份 / 4 个周期，不符合“思想汇报按期提交”要求（每周期至少 1 份）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	5f5774cdf6e704e82bae15f7d10922feae6d3de0	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.389883+08	2026-10-17 18:36:16.389883+08
29	6	2	\N	\N	AI_RULE	TIME	BLOCK	R-T20	中国共产党发展党员工作细则	同一节点多来源一致	节点冲突：T01	{}	T01	多来源一致	《》中为 T01，不符合“同一节点多来源一致”要求（多来源一致）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	be362baf116f03e83999efb6666f72a067822107	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.389912+08	2026-10-17 18:36:16.389912+08
30	6	2	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T01	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	7b0433541f34e6ff13d738aa67e14f7f453f0ee1	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.38994+08	2026-10-17 18:36:16.38994+08
31	6	2	\N	\N	AI_RULE	TIME	WARN	R-T23	中国共产党发展党员工作细则	序列日期落在培养区间	思想汇报日期未落在对应培养考察区间内	{}	2 份越界	2024-09-10 ~ 2025-08-30	《》中为 2 份越界，不符合“序列日期落在培养区间”要求（2024-09-10 ~ 2025-08-30）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	229988362a2e86e0ed843510b7e013efd428dd09	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.389968+08	2026-10-17 18:36:16.389968+08
32	6	2	8	8	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 8}	body	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	ace939ef4c5cd4b444f86193b4edc0a0b09fc9b6	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.389997+08	2026-10-17 18:36:16.389997+08
33	6	2	9	9	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 9}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	30225b4304ca463c45686fb039c4ed1606489f48	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.390024+08	2026-10-17 18:36:16.390025+08
34	6	2	8	8	AI_RULE	FORMAT	WARN	R-F06	学校党员发展材料规范	篇幅下限	正文字数 39，不足 3000	{"material_id": 8}	39	3000	材料正文字数不足规定篇幅	\N	f	0.9	bcbc1b66f584d12c84a5154f9adf4c5eee71a702	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.390053+08	2026-10-17 18:36:16.390054+08
35	6	2	7	7	AI_RULE	CONTENT	WARN	R-C01	党章及发展党员工作细则；学校审核标准	政治术语规范	指导思想并列表述有缺项	{"snippet": "马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想", "material_id": 7}	马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想	马克思列宁主义、毛泽东思想、邓小平理论、“三个代表”重要思想、科学发展观、习近平新时代中国特色社会主义思想	出现不规范政治术语或并列顺序错误	\N	f	0.9	4b59b3f3f5edde97ae5d9f5c1078b39e9d76e57a	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.390082+08	2026-10-17 18:36:16.390082+08
36	6	2	7	7	AI_RULE	CONTENT	WARN	R-C04	党章及发展党员工作细则；学校审核标准	入党动机表述	入党动机表述需关注：“入党可以评优评奖”	{"snippet": "入党可以评优评奖", "material_id": 7}	入党可以评优评奖	理想信念导向	请从理想信念、服务师生、发挥作用等角度重写入党动机。	\N	t	0.9	5f8a461de358a398a99b035776dd6edebe82e45a	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.390109+08	2026-10-17 18:36:16.390109+08
37	6	2	7	7	AI_RULE	CONTENT	WARN	R-C04	党章及发展党员工作细则；学校审核标准	入党动机表述	入党动机表述需关注：“为了好找工作”	{"snippet": "为了好找工作", "material_id": 7}	为了好找工作	理想信念导向	请结合对党的认识和自身成长经历写明入党动机。	\N	t	0.9	854bb9225953c4ff2612970f44efbb6b701e3ddf	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.390138+08	2026-10-17 18:36:16.390138+08
38	6	2	8	8	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：家庭主要成员、成长经历、思想演变	{"snippet": "缺", "material_id": 8}	缺	应包含 家庭主要成员、成长经历、思想演变	材料缺少模板规定的内容要素	\N	f	0.9	36df3f4561fd4e7842db50a2ce67f460a452beff	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.390166+08	2026-10-17 18:36:16.390166+08
39	6	2	9	9	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 9}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	ce95af6af9230c67785a89a7185832479db48e49	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.390194+08	2026-10-17 18:36:16.390194+08
40	6	2	7	7	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	姓名与档案不一致	{"snippet": "演示学生", "material_id": 7}	演示学生	演示学生02	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	4c3efe7bae9a263353388ab0b2dae8a2fd42218b	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.390223+08	2026-10-17 18:36:16.390223+08
41	6	2	8	8	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	出生日期与档案不一致	{"snippet": "2004-01-01", "material_id": 8}	2004-01-01	2003-05-12	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	0fde0190baadb8c46b3c6dff2f1bb2d359140572	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.390251+08	2026-10-17 18:36:16.390251+08
65	18	5	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T01	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	7b0433541f34e6ff13d738aa67e14f7f453f0ee1	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.919657+08	2026-10-17 18:36:16.919659+08
66	18	5	21	21	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 21}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	ee7935495a639bc0f923104676f4f27497fb5fd3	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.919738+08	2026-10-17 18:36:16.919738+08
67	18	5	21	21	AI_RULE	FORMAT	BLOCK	R-F03	学校党员发展材料规范	签名齐全	谈话人签名未检测到签名	{"material_id": 21}	无	应有签名	《党组织派人谈话记录》谈话人签名 未检测到签名，请本人（或相关负责人）补签。	\N	f	0.9	a5ad7e5de7fa1ce7df0fb1e3dfb36c596d5f8661	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.919777+08	2026-10-17 18:36:16.919777+08
68	18	5	20	20	AI_RULE	CONTENT	WARN	R-C01	党章及发展党员工作细则；学校审核标准	政治术语规范	指导思想并列表述有缺项	{"snippet": "马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想", "material_id": 20}	马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想	马克思列宁主义、毛泽东思想、邓小平理论、“三个代表”重要思想、科学发展观、习近平新时代中国特色社会主义思想	出现不规范政治术语或并列顺序错误	\N	f	0.9	fa5503200bf93908e499ba1af5f011b52536b23b	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.919811+08	2026-10-17 18:36:16.919811+08
69	18	5	20	20	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	姓名与档案不一致	{"snippet": "演示学生", "material_id": 20}	演示学生	演示学生06	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	a8be12fafbad29890f119b570c36c8a237596426	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.919843+08	2026-10-17 18:36:16.919843+08
203	54	15	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T01	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	7b0433541f34e6ff13d738aa67e14f7f453f0ee1	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.87892+08	2026-10-17 18:36:18.878922+08
204	54	15	63	63	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 63}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	d0e6fb735f2b5a1b066660327116bed27818bf35	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.879022+08	2026-10-17 18:36:18.879023+08
42	12	3	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《上级党委派人谈话记录》	应交 1 份，已交 0 份，缺少 1 份。上级党委派人谈话记录	{"checklist_item_id": 19}	0	1	缺少《上级党委派人谈话记录》1 份（应交 1 份，已交 0 份）。请按要求补交：上级党委派人谈话记录。	\N	f	0.9	02d406caffdb054371475cf98f5799d29b9dd144	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.686523+08	2026-10-17 18:36:16.686524+08
43	12	3	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《上级党委审批意见》	应交 1 份，已交 0 份，缺少 1 份。上级党委审批意见	{"checklist_item_id": 20}	0	1	缺少《上级党委审批意见》1 份（应交 1 份，已交 0 份）。请按要求补交：上级党委审批意见。	\N	f	0.9	282669a4c1ba1b5b0d57fec9e5fcfde3cc06e34f	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.686584+08	2026-10-17 18:36:16.686584+08
44	12	3	\N	\N	AI_RULE	TIME	BLOCK	R-T20	中国共产党发展党员工作细则	同一节点多来源一致	节点冲突：T19	{}	T19	多来源一致	《》中为 T19，不符合“同一节点多来源一致”要求（多来源一致）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	5569b826211e6f99a5beeadf047c070b83b0239c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.686621+08	2026-10-17 18:36:16.686622+08
45	12	3	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T10,T11	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	ff456394583aaa985c3c3be83c6d0088cf66efdb	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.686655+08	2026-10-17 18:36:16.686655+08
46	12	3	\N	\N	AI_RULE	TIME	BLOCK	R-T22	中国共产党发展党员工作细则	阶段必填节点与单调递增	当前阶段关键时间节点缺失或顺序颠倒	{}	T14->T20	关键节点严格递增	《》中为 T14->T20，不符合“阶段必填节点与单调递增”要求（关键节点严格递增）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	8581edbb854d94dd754e7838561e8778816c7989	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.686686+08	2026-10-17 18:36:16.686687+08
47	12	3	11	11	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 11}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	d5a0ffe2459b8992de403ea1590cbe7a01b45272	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.68672+08	2026-10-17 18:36:16.68672+08
48	12	3	12	12	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 12}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	5330b24d2d6269d79566753969b6a807f916846d	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.686751+08	2026-10-17 18:36:16.686751+08
49	12	3	13	13	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 13}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	2ece0f54985610b4a9ce0b8122d0f78a113b0926	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.68678+08	2026-10-17 18:36:16.686781+08
50	12	3	14	14	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 14}	body	应包含 title,body	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	96ab715d56d0ca5aec8aee62b4f2e5bec551d217	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.686809+08	2026-10-17 18:36:16.686809+08
51	12	3	15	15	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 15}	body	应包含 title,body,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	a6fcfca595b5c5bcd2807b8e0c9314e7a9b477a5	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.686836+08	2026-10-17 18:36:16.686837+08
52	12	3	16	16	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 16}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	1001a52118ad598f05159fc6dac4e87d322d5bff	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.686864+08	2026-10-17 18:36:16.686865+08
53	12	3	11	11	AI_RULE	FORMAT	BLOCK	R-F03	学校党员发展材料规范	签名齐全	本人签名未检测到签名	{"material_id": 11}	无	应有签名	《入党志愿书》本人签名 未检测到签名，请本人（或相关负责人）补签。	\N	f	0.9	87330d496239795587118d9455e27cf23ac03d39	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.686894+08	2026-10-17 18:36:16.686894+08
54	12	3	11	11	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	姓名与档案不一致	{"snippet": "演示学生", "material_id": 11}	演示学生	演示学生04	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	2aa333047ebfaf78fdffc3a2552687c756c01209	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.686923+08	2026-10-17 18:36:16.686924+08
55	17	4	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《写实簿·预备党员考察部分》	应交 1 份，已交 0 份，缺少 1 份。写实簿预备党员考察部分	{"checklist_item_id": 22}	0	1	缺少《写实簿·预备党员考察部分》1 份（应交 1 份，已交 0 份）。请按要求补交：写实簿预备党员考察部分。	\N	f	0.9	ea3a5912f136481d35cb4311956f6fb72c3865f7	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.82361+08	2026-10-17 18:36:16.823612+08
56	17	4	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《上级党委审批转正意见》	应交 1 份，已交 0 份，缺少 1 份。上级党委审批转正意见	{"checklist_item_id": 25}	0	1	缺少《上级党委审批转正意见》1 份（应交 1 份，已交 0 份）。请按要求补交：上级党委审批转正意见。	\N	f	0.9	44dbf57023407049a3c375af371b7cfb4f11e42e	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.823709+08	2026-10-17 18:36:16.823709+08
57	17	4	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《思想汇报》	应交 4 份，已交 0 份，缺少 4 份。预备期每季度至少一份思想汇报	{"checklist_item_id": 26}	0	4	缺少《思想汇报》4 份（应交 4 份，已交 0 份）。请按要求补交：预备期每季度至少一份思想汇报。	\N	f	0.9	b822922008621d745f152aa9e61ca03ab1183034	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.823747+08	2026-10-17 18:36:16.823748+08
58	17	4	\N	\N	AI_RULE	TIME	BLOCK	R-T20	中国共产党发展党员工作细则	同一节点多来源一致	节点冲突：T11,T14,T20	{}	T11,T14,T20	多来源一致	《》中为 T11,T14,T20，不符合“同一节点多来源一致”要求（多来源一致）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	83a664d89fc5fb5ea098cc8d406840517c5f33d5	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.823781+08	2026-10-17 18:36:16.823782+08
59	17	4	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T19	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	e417b5496dd18a3d3d4f41bb1a69e6952f54df99	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.823814+08	2026-10-17 18:36:16.823814+08
60	17	4	\N	\N	AI_RULE	TIME	BLOCK	R-T22	中国共产党发展党员工作细则	阶段必填节点与单调递增	缺少 T19	{}	缺失 T19	阶段必填节点齐全	《》中为 缺失 T19，不符合“阶段必填节点与单调递增”要求（阶段必填节点齐全）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	49d5fb696e42d5a0a4af8b96fceab32f60404425	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.823847+08	2026-10-17 18:36:16.823848+08
61	17	4	17	17	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 17}	body,signature	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	c628623f8b8901074f737cc1ae820affc91c0480	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.82388+08	2026-10-17 18:36:16.82388+08
62	17	4	18	18	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 18}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	33d62af5a1d32c8563f3e7cf18d7c3b2d86d1fcb	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.823911+08	2026-10-17 18:36:16.823912+08
63	17	4	19	19	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 19}	body	应包含 title,body,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	4e4be22f13f55d6a4f4c296e5ee52c3ede89357f	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.823941+08	2026-10-17 18:36:16.823941+08
64	17	4	17	17	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 17}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	bd6946affe2ead822e971f5b04e599dde697c64a	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.823971+08	2026-10-17 18:36:16.823971+08
70	21	6	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《政治审查材料》	应交 1 份，已交 0 份，缺少 1 份。政治审查材料	{"checklist_item_id": 11}	0	1	缺少《政治审查材料》1 份（应交 1 份，已交 0 份）。请按要求补交：政治审查材料。	\N	f	0.9	d54d125051786d628b7f668fff5b64c9c77fe60c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.188537+08	2026-10-17 18:36:17.188538+08
71	21	6	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《集中培训结业证书》	应交 1 份，已交 0 份，缺少 1 份。集中培训结业证书	{"checklist_item_id": 12}	0	1	缺少《集中培训结业证书》1 份（应交 1 份，已交 0 份）。请按要求补交：集中培训结业证书。	\N	f	0.9	ffaca8c9d99a22a690909577b59c36cfe00ded4e	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.188605+08	2026-10-17 18:36:17.188606+08
72	21	6	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《写实簿·发展对象考察部分》	应交 1 份，已交 0 份，缺少 1 份。写实簿发展对象考察部分	{"checklist_item_id": 13}	0	1	缺少《写实簿·发展对象考察部分》1 份（应交 1 份，已交 0 份）。请按要求补交：写实簿发展对象考察部分。	\N	f	0.9	f3ce00a714e76e4da498f001d62fdeb73595ba39	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.188643+08	2026-10-17 18:36:17.188644+08
73	21	6	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《思想汇报》	应交 5 份，已交 3 份，缺少 2 份。每季度至少一份思想汇报	{"checklist_item_id": 14}	3	5	缺少《思想汇报》2 份（应交 5 份，已交 3 份）。请按要求补交：每季度至少一份思想汇报。	\N	f	0.9	3ecf2968464ecbacc34ba93a0b7fa3bee2237bdc	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.188678+08	2026-10-17 18:36:17.188678+08
74	21	6	\N	\N	AI_RULE	TIME	BLOCK	R-T05	中国共产党发展党员工作细则	积极分子培养满一年	间隔 11 个月 20 天，不足 1 YEAR	{"node_code": "T08"}	11 个月 20 天	≥ 1 YEAR	《》中T08为 11 个月 20 天，不符合“积极分子培养满一年”要求（≥ 1 YEAR）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	88b2a22720c273901ff055f427fad5d6a9b9ab4c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.188711+08	2026-10-17 18:36:17.188711+08
75	21	6	\N	\N	AI_RULE	TIME	WARN	R-T06	中国共产党发展党员工作细则	思想汇报相邻间隔	相邻间隔超过 3 MONTH	{}	3 处超间隔	相邻 ≤ 3 MONTH	《》中为 3 处超间隔，不符合“思想汇报相邻间隔”要求（相邻 ≤ 3 MONTH）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	cf6df7d5c267fd795ee57f39d46aef9aa22ed8d7	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.188743+08	2026-10-17 18:36:17.188744+08
76	21	6	\N	\N	AI_RULE	TIME	BLOCK	R-T07	中国共产党发展党员工作细则	思想汇报按期提交	1 个周期不足	{}	实交 6 份 / 4 个周期	每周期至少 1 份	《》中为 实交 6 份 / 4 个周期，不符合“思想汇报按期提交”要求（每周期至少 1 份）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	651be8191e11ebb30a0eee826d1afc7067384fd5	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.188775+08	2026-10-17 18:36:17.188776+08
77	21	6	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T01	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	7b0433541f34e6ff13d738aa67e14f7f453f0ee1	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.188806+08	2026-10-17 18:36:17.188806+08
78	21	6	\N	\N	AI_RULE	TIME	WARN	R-T23	中国共产党发展党员工作细则	序列日期落在培养区间	思想汇报日期未落在对应培养考察区间内	{}	2 份越界	2024-09-10 ~ 2025-08-30	《》中为 2 份越界，不符合“序列日期落在培养区间”要求（2024-09-10 ~ 2025-08-30）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	229988362a2e86e0ed843510b7e013efd428dd09	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.188837+08	2026-10-17 18:36:17.188838+08
79	21	6	23	23	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 23}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	ed6849e8f2374f8c294b93204f7ea54edb2eea1f	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.188868+08	2026-10-17 18:36:17.188868+08
80	21	6	24	24	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 24}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	30827ed3e3401364b7ba3623b47789b9d72ffc66	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.188897+08	2026-10-17 18:36:17.188897+08
81	21	6	25	25	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 25}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	ce46135103667a4907a7ed93a60e91bb0b423cda	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.188926+08	2026-10-17 18:36:17.188926+08
82	21	6	26	26	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 26}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	c8d6a0f7525be101cfe4397ea42b42614a829495	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.188956+08	2026-10-17 18:36:17.188956+08
83	21	6	27	27	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：signature	{"material_id": 27}	signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	ba82f59a2efced47f319da68758758217a189400	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.188984+08	2026-10-17 18:36:17.188984+08
84	21	6	27	27	AI_RULE	FORMAT	WARN	R-F06	学校党员发展材料规范	篇幅下限	正文字数 516，不足 3000	{"material_id": 27}	516	3000	材料正文字数不足规定篇幅	\N	f	0.9	496f50fe9aa63365d37f22ab535cf38158eee51c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.189013+08	2026-10-17 18:36:17.189013+08
85	21	6	22	22	AI_RULE	CONTENT	WARN	R-C01	党章及发展党员工作细则；学校审核标准	政治术语规范	指导思想并列表述有缺项	{"snippet": "马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想", "material_id": 22}	马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想	马克思列宁主义、毛泽东思想、邓小平理论、“三个代表”重要思想、科学发展观、习近平新时代中国特色社会主义思想	出现不规范政治术语或并列顺序错误	\N	f	0.9	42404403f8d444e992be50343155b1b3168c040b	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.189042+08	2026-10-17 18:36:17.189042+08
86	21	6	23	23	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 23}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	fc7850e061ea69625f26b4c908a87a9a94b6e581	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.18907+08	2026-10-17 18:36:17.18907+08
87	21	6	24	24	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 24}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	1acb92daf959af0c8a387c11e8db02fa6b40dc03	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.189098+08	2026-10-17 18:36:17.189098+08
88	21	6	25	25	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 25}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	a92ab554c3fb136a941aa2836244746f5f22c022	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.189125+08	2026-10-17 18:36:17.189126+08
89	21	6	22	22	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	姓名与档案不一致	{"snippet": "演示学生", "material_id": 22}	演示学生	演示学生07	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	3fde1ebc4d07bdc1e96c06b65a219a3a557d722d	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.189153+08	2026-10-17 18:36:17.189153+08
90	24	7	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《支委会确定发展对象记录》	应交 1 份，已交 0 份，缺少 1 份。支委会确定发展对象记录	{"checklist_item_id": 10}	0	1	缺少《支委会确定发展对象记录》1 份（应交 1 份，已交 0 份）。请按要求补交：支委会确定发展对象记录。	\N	f	0.9	a14816de9623777c76f088d00e203aacbffdcf09	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.345376+08	2026-10-17 18:36:17.345377+08
91	24	7	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《政治审查材料》	应交 1 份，已交 0 份，缺少 1 份。政治审查材料	{"checklist_item_id": 11}	0	1	缺少《政治审查材料》1 份（应交 1 份，已交 0 份）。请按要求补交：政治审查材料。	\N	f	0.9	d54d125051786d628b7f668fff5b64c9c77fe60c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.345455+08	2026-10-17 18:36:17.345455+08
92	24	7	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《集中培训结业证书》	应交 1 份，已交 0 份，缺少 1 份。集中培训结业证书	{"checklist_item_id": 12}	0	1	缺少《集中培训结业证书》1 份（应交 1 份，已交 0 份）。请按要求补交：集中培训结业证书。	\N	f	0.9	ffaca8c9d99a22a690909577b59c36cfe00ded4e	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.345494+08	2026-10-17 18:36:17.345494+08
93	24	7	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《写实簿·发展对象考察部分》	应交 1 份，已交 0 份，缺少 1 份。写实簿发展对象考察部分	{"checklist_item_id": 13}	0	1	缺少《写实簿·发展对象考察部分》1 份（应交 1 份，已交 0 份）。请按要求补交：写实簿发展对象考察部分。	\N	f	0.9	f3ce00a714e76e4da498f001d62fdeb73595ba39	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.345528+08	2026-10-17 18:36:17.345528+08
94	24	7	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《思想汇报》	应交 5 份，已交 1 份，缺少 4 份。每季度至少一份思想汇报	{"checklist_item_id": 14}	1	5	缺少《思想汇报》4 份（应交 5 份，已交 1 份）。请按要求补交：每季度至少一份思想汇报。	\N	f	0.9	3ecf2968464ecbacc34ba93a0b7fa3bee2237bdc	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.345563+08	2026-10-17 18:36:17.345563+08
95	24	7	\N	\N	AI_RULE	TIME	BLOCK	R-T05	中国共产党发展党员工作细则	积极分子培养满一年	间隔 11 个月 20 天，不足 1 YEAR	{"node_code": "T08"}	11 个月 20 天	≥ 1 YEAR	《》中T08为 11 个月 20 天，不符合“积极分子培养满一年”要求（≥ 1 YEAR）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	88b2a22720c273901ff055f427fad5d6a9b9ab4c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.345599+08	2026-10-17 18:36:17.3456+08
96	24	7	\N	\N	AI_RULE	TIME	WARN	R-T06	中国共产党发展党员工作细则	思想汇报相邻间隔	相邻间隔超过 3 MONTH	{}	1 处超间隔	相邻 ≤ 3 MONTH	《》中为 1 处超间隔，不符合“思想汇报相邻间隔”要求（相邻 ≤ 3 MONTH）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	d573fe8a048c5e4f4037f87661fbd9447c785a91	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.34563+08	2026-10-17 18:36:17.345631+08
97	24	7	\N	\N	AI_RULE	TIME	BLOCK	R-T07	中国共产党发展党员工作细则	思想汇报按期提交	3 个周期不足	{}	实交 3 份 / 4 个周期	每周期至少 1 份	《》中为 实交 3 份 / 4 个周期，不符合“思想汇报按期提交”要求（每周期至少 1 份）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	5f5774cdf6e704e82bae15f7d10922feae6d3de0	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.345661+08	2026-10-17 18:36:17.345662+08
98	24	7	\N	\N	AI_RULE	TIME	BLOCK	R-T20	中国共产党发展党员工作细则	同一节点多来源一致	节点冲突：T01	{}	T01	多来源一致	《》中为 T01，不符合“同一节点多来源一致”要求（多来源一致）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	be362baf116f03e83999efb6666f72a067822107	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.345691+08	2026-10-17 18:36:17.345691+08
99	24	7	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T01	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	7b0433541f34e6ff13d738aa67e14f7f453f0ee1	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.345724+08	2026-10-17 18:36:17.345724+08
100	24	7	\N	\N	AI_RULE	TIME	WARN	R-T23	中国共产党发展党员工作细则	序列日期落在培养区间	思想汇报日期未落在对应培养考察区间内	{}	2 份越界	2024-09-10 ~ 2025-08-30	《》中为 2 份越界，不符合“序列日期落在培养区间”要求（2024-09-10 ~ 2025-08-30）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	229988362a2e86e0ed843510b7e013efd428dd09	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.345754+08	2026-10-17 18:36:17.345754+08
101	24	7	29	29	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 29}	body	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	b115adf19b8e15b8a7bfa062c10d78b863230816	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.345784+08	2026-10-17 18:36:17.345785+08
102	24	7	30	30	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 30}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	6f0a826c2d22a16ee6e99e0c39f028e29778b148	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.345813+08	2026-10-17 18:36:17.345813+08
103	24	7	29	29	AI_RULE	FORMAT	WARN	R-F06	学校党员发展材料规范	篇幅下限	正文字数 39，不足 3000	{"material_id": 29}	39	3000	材料正文字数不足规定篇幅	\N	f	0.9	dc5896c508db92dc9bd4dcb6ed34bf6f0a8e71c2	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.345841+08	2026-10-17 18:36:17.345841+08
104	24	7	28	28	AI_RULE	CONTENT	WARN	R-C01	党章及发展党员工作细则；学校审核标准	政治术语规范	指导思想并列表述有缺项	{"snippet": "马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想", "material_id": 28}	马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想	马克思列宁主义、毛泽东思想、邓小平理论、“三个代表”重要思想、科学发展观、习近平新时代中国特色社会主义思想	出现不规范政治术语或并列顺序错误	\N	f	0.9	1879389e47865334bf31ca8161fdc89a5b4f1ba5	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.345869+08	2026-10-17 18:36:17.345869+08
105	24	7	28	28	AI_RULE	CONTENT	WARN	R-C04	党章及发展党员工作细则；学校审核标准	入党动机表述	入党动机表述需关注：“入党可以评优评奖”	{"snippet": "入党可以评优评奖", "material_id": 28}	入党可以评优评奖	理想信念导向	请从理想信念、服务师生、发挥作用等角度重写入党动机。	\N	t	0.9	b98050aca9334391810f9b185c1635687213f94d	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.345897+08	2026-10-17 18:36:17.345897+08
106	24	7	28	28	AI_RULE	CONTENT	WARN	R-C04	党章及发展党员工作细则；学校审核标准	入党动机表述	入党动机表述需关注：“为了好找工作”	{"snippet": "为了好找工作", "material_id": 28}	为了好找工作	理想信念导向	请结合对党的认识和自身成长经历写明入党动机。	\N	t	0.9	50a12f53764972dd38f5ba98295c879ba788205e	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.345924+08	2026-10-17 18:36:17.345925+08
107	24	7	29	29	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：家庭主要成员、成长经历、思想演变	{"snippet": "缺", "material_id": 29}	缺	应包含 家庭主要成员、成长经历、思想演变	材料缺少模板规定的内容要素	\N	f	0.9	beb09a4cc5222877505cc1983f845032dd3c35fd	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.345953+08	2026-10-17 18:36:17.345954+08
108	24	7	30	30	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 30}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	10b12d9a4cf0ccc4592c5cb5b2f9667a37bb4beb	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.345982+08	2026-10-17 18:36:17.345983+08
109	24	7	28	28	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	姓名与档案不一致	{"snippet": "演示学生", "material_id": 28}	演示学生	演示学生08	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	e7cb093d7307be3378462deae9dc8360d5f3a28f	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.346011+08	2026-10-17 18:36:17.346011+08
110	24	7	29	29	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	出生日期与档案不一致	{"snippet": "2004-01-01", "material_id": 29}	2004-01-01	2003-05-12	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	913f95a061b6b1c1ddf417bf1037d6fdbb5754c7	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.346039+08	2026-10-17 18:36:17.346039+08
111	30	8	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《上级党委派人谈话记录》	应交 1 份，已交 0 份，缺少 1 份。上级党委派人谈话记录	{"checklist_item_id": 19}	0	1	缺少《上级党委派人谈话记录》1 份（应交 1 份，已交 0 份）。请按要求补交：上级党委派人谈话记录。	\N	f	0.9	02d406caffdb054371475cf98f5799d29b9dd144	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.660169+08	2026-10-17 18:36:17.66017+08
112	30	8	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《上级党委审批意见》	应交 1 份，已交 0 份，缺少 1 份。上级党委审批意见	{"checklist_item_id": 20}	0	1	缺少《上级党委审批意见》1 份（应交 1 份，已交 0 份）。请按要求补交：上级党委审批意见。	\N	f	0.9	282669a4c1ba1b5b0d57fec9e5fcfde3cc06e34f	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.660231+08	2026-10-17 18:36:17.660231+08
113	30	8	\N	\N	AI_RULE	TIME	BLOCK	R-T20	中国共产党发展党员工作细则	同一节点多来源一致	节点冲突：T19	{}	T19	多来源一致	《》中为 T19，不符合“同一节点多来源一致”要求（多来源一致）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	5569b826211e6f99a5beeadf047c070b83b0239c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.660269+08	2026-10-17 18:36:17.660269+08
114	30	8	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T10,T11	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	ff456394583aaa985c3c3be83c6d0088cf66efdb	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.660303+08	2026-10-17 18:36:17.660303+08
115	30	8	\N	\N	AI_RULE	TIME	BLOCK	R-T22	中国共产党发展党员工作细则	阶段必填节点与单调递增	当前阶段关键时间节点缺失或顺序颠倒	{}	T14->T20	关键节点严格递增	《》中为 T14->T20，不符合“阶段必填节点与单调递增”要求（关键节点严格递增）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	8581edbb854d94dd754e7838561e8778816c7989	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.660337+08	2026-10-17 18:36:17.660337+08
116	30	8	32	32	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 32}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	5d30b114c2fd29932a34fe884368446c37564e7e	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.660371+08	2026-10-17 18:36:17.660371+08
117	30	8	33	33	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 33}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	3ba0ba906d4ba0e17a68256549de94826ec34882	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.660402+08	2026-10-17 18:36:17.660402+08
118	30	8	34	34	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 34}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	1844371ad17d1f783a2835a38b5b1fdef92c6060	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.660431+08	2026-10-17 18:36:17.660432+08
119	30	8	35	35	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 35}	body	应包含 title,body	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	83d0bb10d90cdfb7895394b9d5c2f85772fd35f1	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.660461+08	2026-10-17 18:36:17.660461+08
120	30	8	36	36	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 36}	body	应包含 title,body,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	4df76edaca1795e9d0cb05568b12e78efaf149e1	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.660491+08	2026-10-17 18:36:17.660491+08
121	30	8	37	37	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 37}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	7511c4e8c23e2bf2dc9a937259845ade56d8e097	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.660521+08	2026-10-17 18:36:17.660521+08
122	30	8	32	32	AI_RULE	FORMAT	BLOCK	R-F03	学校党员发展材料规范	签名齐全	本人签名未检测到签名	{"material_id": 32}	无	应有签名	《入党志愿书》本人签名 未检测到签名，请本人（或相关负责人）补签。	\N	f	0.9	b46f182a5bf3d02be869b2e8a1d205e544103c20	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.660551+08	2026-10-17 18:36:17.660551+08
123	30	8	32	32	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	姓名与档案不一致	{"snippet": "演示学生", "material_id": 32}	演示学生	演示学生10	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	8b25b2155f82bb55b48b2b985d29a8deeb61e9f1	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.66058+08	2026-10-17 18:36:17.66058+08
124	35	9	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《写实簿·预备党员考察部分》	应交 1 份，已交 0 份，缺少 1 份。写实簿预备党员考察部分	{"checklist_item_id": 22}	0	1	缺少《写实簿·预备党员考察部分》1 份（应交 1 份，已交 0 份）。请按要求补交：写实簿预备党员考察部分。	\N	f	0.9	ea3a5912f136481d35cb4311956f6fb72c3865f7	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.794483+08	2026-10-17 18:36:17.794485+08
125	35	9	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《上级党委审批转正意见》	应交 1 份，已交 0 份，缺少 1 份。上级党委审批转正意见	{"checklist_item_id": 25}	0	1	缺少《上级党委审批转正意见》1 份（应交 1 份，已交 0 份）。请按要求补交：上级党委审批转正意见。	\N	f	0.9	44dbf57023407049a3c375af371b7cfb4f11e42e	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.794579+08	2026-10-17 18:36:17.79458+08
126	35	9	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《思想汇报》	应交 4 份，已交 0 份，缺少 4 份。预备期每季度至少一份思想汇报	{"checklist_item_id": 26}	0	4	缺少《思想汇报》4 份（应交 4 份，已交 0 份）。请按要求补交：预备期每季度至少一份思想汇报。	\N	f	0.9	b822922008621d745f152aa9e61ca03ab1183034	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.79462+08	2026-10-17 18:36:17.79462+08
127	35	9	\N	\N	AI_RULE	TIME	BLOCK	R-T20	中国共产党发展党员工作细则	同一节点多来源一致	节点冲突：T11,T14,T20	{}	T11,T14,T20	多来源一致	《》中为 T11,T14,T20，不符合“同一节点多来源一致”要求（多来源一致）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	83a664d89fc5fb5ea098cc8d406840517c5f33d5	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.794654+08	2026-10-17 18:36:17.794654+08
128	35	9	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T19	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	e417b5496dd18a3d3d4f41bb1a69e6952f54df99	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.794687+08	2026-10-17 18:36:17.794687+08
129	35	9	\N	\N	AI_RULE	TIME	BLOCK	R-T22	中国共产党发展党员工作细则	阶段必填节点与单调递增	缺少 T19	{}	缺失 T19	阶段必填节点齐全	《》中为 缺失 T19，不符合“阶段必填节点与单调递增”要求（阶段必填节点齐全）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	49d5fb696e42d5a0a4af8b96fceab32f60404425	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.794721+08	2026-10-17 18:36:17.794721+08
130	35	9	38	38	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 38}	body,signature	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	ddfc6b8e2579f8ffca3cd5439840a20f54eef6b6	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.794752+08	2026-10-17 18:36:17.794752+08
131	35	9	39	39	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 39}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	60919fbf92980460d3e5d95faa3bceb0c73e5c28	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.794784+08	2026-10-17 18:36:17.794784+08
132	35	9	40	40	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 40}	body	应包含 title,body,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	217e1f67a55f19a1fabee95336f2c0fa14791438	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.794815+08	2026-10-17 18:36:17.794815+08
133	35	9	38	38	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 38}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	2ef405d33d454ed0a571e376cb1ebae3eb28773b	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.794847+08	2026-10-17 18:36:17.794847+08
134	36	10	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T01	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	7b0433541f34e6ff13d738aa67e14f7f453f0ee1	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.934616+08	2026-10-17 18:36:17.93462+08
135	36	10	42	42	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 42}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	2f4e0b6231dca8438b10fef30f69a2b266a1e376	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.934731+08	2026-10-17 18:36:17.934732+08
136	36	10	42	42	AI_RULE	FORMAT	BLOCK	R-F03	学校党员发展材料规范	签名齐全	谈话人签名未检测到签名	{"material_id": 42}	无	应有签名	《党组织派人谈话记录》谈话人签名 未检测到签名，请本人（或相关负责人）补签。	\N	f	0.9	22aa59e37b889e7e44508525d30e2403df0960de	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.934781+08	2026-10-17 18:36:17.934781+08
137	36	10	41	41	AI_RULE	CONTENT	WARN	R-C01	党章及发展党员工作细则；学校审核标准	政治术语规范	指导思想并列表述有缺项	{"snippet": "马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想", "material_id": 41}	马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想	马克思列宁主义、毛泽东思想、邓小平理论、“三个代表”重要思想、科学发展观、习近平新时代中国特色社会主义思想	出现不规范政治术语或并列顺序错误	\N	f	0.9	180af8fca78e99a060b0d2067e8c27be7f690514	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.934826+08	2026-10-17 18:36:17.934826+08
138	36	10	41	41	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	姓名与档案不一致	{"snippet": "演示学生", "material_id": 41}	演示学生	演示学生12	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	f3113030203c368f098231137f92230102ca6017	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:17.934871+08	2026-10-17 18:36:17.934872+08
139	39	11	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《政治审查材料》	应交 1 份，已交 0 份，缺少 1 份。政治审查材料	{"checklist_item_id": 11}	0	1	缺少《政治审查材料》1 份（应交 1 份，已交 0 份）。请按要求补交：政治审查材料。	\N	f	0.9	d54d125051786d628b7f668fff5b64c9c77fe60c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.186929+08	2026-10-17 18:36:18.186931+08
140	39	11	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《集中培训结业证书》	应交 1 份，已交 0 份，缺少 1 份。集中培训结业证书	{"checklist_item_id": 12}	0	1	缺少《集中培训结业证书》1 份（应交 1 份，已交 0 份）。请按要求补交：集中培训结业证书。	\N	f	0.9	ffaca8c9d99a22a690909577b59c36cfe00ded4e	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.186999+08	2026-10-17 18:36:18.186999+08
141	39	11	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《写实簿·发展对象考察部分》	应交 1 份，已交 0 份，缺少 1 份。写实簿发展对象考察部分	{"checklist_item_id": 13}	0	1	缺少《写实簿·发展对象考察部分》1 份（应交 1 份，已交 0 份）。请按要求补交：写实簿发展对象考察部分。	\N	f	0.9	f3ce00a714e76e4da498f001d62fdeb73595ba39	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.187038+08	2026-10-17 18:36:18.187038+08
142	39	11	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《思想汇报》	应交 5 份，已交 3 份，缺少 2 份。每季度至少一份思想汇报	{"checklist_item_id": 14}	3	5	缺少《思想汇报》2 份（应交 5 份，已交 3 份）。请按要求补交：每季度至少一份思想汇报。	\N	f	0.9	3ecf2968464ecbacc34ba93a0b7fa3bee2237bdc	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.187072+08	2026-10-17 18:36:18.187073+08
143	39	11	\N	\N	AI_RULE	TIME	BLOCK	R-T05	中国共产党发展党员工作细则	积极分子培养满一年	间隔 11 个月 20 天，不足 1 YEAR	{"node_code": "T08"}	11 个月 20 天	≥ 1 YEAR	《》中T08为 11 个月 20 天，不符合“积极分子培养满一年”要求（≥ 1 YEAR）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	88b2a22720c273901ff055f427fad5d6a9b9ab4c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.187107+08	2026-10-17 18:36:18.187107+08
144	39	11	\N	\N	AI_RULE	TIME	WARN	R-T06	中国共产党发展党员工作细则	思想汇报相邻间隔	相邻间隔超过 3 MONTH	{}	3 处超间隔	相邻 ≤ 3 MONTH	《》中为 3 处超间隔，不符合“思想汇报相邻间隔”要求（相邻 ≤ 3 MONTH）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	cf6df7d5c267fd795ee57f39d46aef9aa22ed8d7	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.18714+08	2026-10-17 18:36:18.18714+08
145	39	11	\N	\N	AI_RULE	TIME	BLOCK	R-T07	中国共产党发展党员工作细则	思想汇报按期提交	1 个周期不足	{}	实交 6 份 / 4 个周期	每周期至少 1 份	《》中为 实交 6 份 / 4 个周期，不符合“思想汇报按期提交”要求（每周期至少 1 份）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	651be8191e11ebb30a0eee826d1afc7067384fd5	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.187171+08	2026-10-17 18:36:18.187172+08
146	39	11	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T01	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	7b0433541f34e6ff13d738aa67e14f7f453f0ee1	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.187201+08	2026-10-17 18:36:18.187201+08
147	39	11	\N	\N	AI_RULE	TIME	WARN	R-T23	中国共产党发展党员工作细则	序列日期落在培养区间	思想汇报日期未落在对应培养考察区间内	{}	2 份越界	2024-09-10 ~ 2025-08-30	《》中为 2 份越界，不符合“序列日期落在培养区间”要求（2024-09-10 ~ 2025-08-30）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	229988362a2e86e0ed843510b7e013efd428dd09	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.187231+08	2026-10-17 18:36:18.187231+08
148	39	11	44	44	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 44}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	c67dbf4cb827ffc693b1757a7948269799633ef2	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.187262+08	2026-10-17 18:36:18.187262+08
149	39	11	45	45	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 45}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	cfbe82206d4f9db1426041d375ecd79fd37e8b12	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.187291+08	2026-10-17 18:36:18.187292+08
150	39	11	46	46	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 46}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	2dad47f7b33b1c4b290f138b39f64e867dbb0781	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.187322+08	2026-10-17 18:36:18.187322+08
151	39	11	47	47	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 47}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	2df6be258e6f81fb323373c8f8e9a016f0d7fe58	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.187355+08	2026-10-17 18:36:18.187355+08
152	39	11	48	48	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：signature	{"material_id": 48}	signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	7396b8ecffdda7d1cdce84a97d1e5f618107f7a9	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.187385+08	2026-10-17 18:36:18.187385+08
153	39	11	48	48	AI_RULE	FORMAT	WARN	R-F06	学校党员发展材料规范	篇幅下限	正文字数 516，不足 3000	{"material_id": 48}	516	3000	材料正文字数不足规定篇幅	\N	f	0.9	25b20daf5d37f72ab41b83ab88f4199eb7816dc9	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.187414+08	2026-10-17 18:36:18.187414+08
154	39	11	43	43	AI_RULE	CONTENT	WARN	R-C01	党章及发展党员工作细则；学校审核标准	政治术语规范	指导思想并列表述有缺项	{"snippet": "马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想", "material_id": 43}	马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想	马克思列宁主义、毛泽东思想、邓小平理论、“三个代表”重要思想、科学发展观、习近平新时代中国特色社会主义思想	出现不规范政治术语或并列顺序错误	\N	f	0.9	10310834d4d9d8167bbac9b86bc9979223025d2a	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.187443+08	2026-10-17 18:36:18.187443+08
155	39	11	44	44	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 44}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	a893ddfc86bef794bbe592b3b86edbcec6e55745	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.187473+08	2026-10-17 18:36:18.187473+08
156	39	11	45	45	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 45}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	120ad4b677821af3ef17dac3f43d1582db1429b1	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.187501+08	2026-10-17 18:36:18.187501+08
157	39	11	46	46	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 46}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	b8f843a37d649a261ea77e489a9a80a7234459ed	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.187532+08	2026-10-17 18:36:18.187532+08
158	39	11	43	43	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	姓名与档案不一致	{"snippet": "演示学生", "material_id": 43}	演示学生	演示学生13	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	7d5254235254e7b24958e145644ac383488e013b	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.187561+08	2026-10-17 18:36:18.187561+08
159	42	12	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《支委会确定发展对象记录》	应交 1 份，已交 0 份，缺少 1 份。支委会确定发展对象记录	{"checklist_item_id": 10}	0	1	缺少《支委会确定发展对象记录》1 份（应交 1 份，已交 0 份）。请按要求补交：支委会确定发展对象记录。	\N	f	0.9	a14816de9623777c76f088d00e203aacbffdcf09	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.317978+08	2026-10-17 18:36:18.317979+08
160	42	12	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《政治审查材料》	应交 1 份，已交 0 份，缺少 1 份。政治审查材料	{"checklist_item_id": 11}	0	1	缺少《政治审查材料》1 份（应交 1 份，已交 0 份）。请按要求补交：政治审查材料。	\N	f	0.9	d54d125051786d628b7f668fff5b64c9c77fe60c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.318053+08	2026-10-17 18:36:18.318053+08
161	42	12	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《集中培训结业证书》	应交 1 份，已交 0 份，缺少 1 份。集中培训结业证书	{"checklist_item_id": 12}	0	1	缺少《集中培训结业证书》1 份（应交 1 份，已交 0 份）。请按要求补交：集中培训结业证书。	\N	f	0.9	ffaca8c9d99a22a690909577b59c36cfe00ded4e	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.318089+08	2026-10-17 18:36:18.318089+08
162	42	12	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《写实簿·发展对象考察部分》	应交 1 份，已交 0 份，缺少 1 份。写实簿发展对象考察部分	{"checklist_item_id": 13}	0	1	缺少《写实簿·发展对象考察部分》1 份（应交 1 份，已交 0 份）。请按要求补交：写实簿发展对象考察部分。	\N	f	0.9	f3ce00a714e76e4da498f001d62fdeb73595ba39	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.318121+08	2026-10-17 18:36:18.318121+08
163	42	12	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《思想汇报》	应交 5 份，已交 1 份，缺少 4 份。每季度至少一份思想汇报	{"checklist_item_id": 14}	1	5	缺少《思想汇报》4 份（应交 5 份，已交 1 份）。请按要求补交：每季度至少一份思想汇报。	\N	f	0.9	3ecf2968464ecbacc34ba93a0b7fa3bee2237bdc	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.318151+08	2026-10-17 18:36:18.318152+08
164	42	12	\N	\N	AI_RULE	TIME	BLOCK	R-T05	中国共产党发展党员工作细则	积极分子培养满一年	间隔 11 个月 20 天，不足 1 YEAR	{"node_code": "T08"}	11 个月 20 天	≥ 1 YEAR	《》中T08为 11 个月 20 天，不符合“积极分子培养满一年”要求（≥ 1 YEAR）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	88b2a22720c273901ff055f427fad5d6a9b9ab4c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.318184+08	2026-10-17 18:36:18.318184+08
165	42	12	\N	\N	AI_RULE	TIME	WARN	R-T06	中国共产党发展党员工作细则	思想汇报相邻间隔	相邻间隔超过 3 MONTH	{}	1 处超间隔	相邻 ≤ 3 MONTH	《》中为 1 处超间隔，不符合“思想汇报相邻间隔”要求（相邻 ≤ 3 MONTH）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	d573fe8a048c5e4f4037f87661fbd9447c785a91	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.318215+08	2026-10-17 18:36:18.318215+08
166	42	12	\N	\N	AI_RULE	TIME	BLOCK	R-T07	中国共产党发展党员工作细则	思想汇报按期提交	3 个周期不足	{}	实交 3 份 / 4 个周期	每周期至少 1 份	《》中为 实交 3 份 / 4 个周期，不符合“思想汇报按期提交”要求（每周期至少 1 份）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	5f5774cdf6e704e82bae15f7d10922feae6d3de0	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.318246+08	2026-10-17 18:36:18.318246+08
167	42	12	\N	\N	AI_RULE	TIME	BLOCK	R-T20	中国共产党发展党员工作细则	同一节点多来源一致	节点冲突：T01	{}	T01	多来源一致	《》中为 T01，不符合“同一节点多来源一致”要求（多来源一致）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	be362baf116f03e83999efb6666f72a067822107	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.318284+08	2026-10-17 18:36:18.318285+08
168	42	12	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T01	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	7b0433541f34e6ff13d738aa67e14f7f453f0ee1	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.318334+08	2026-10-17 18:36:18.318334+08
169	42	12	\N	\N	AI_RULE	TIME	WARN	R-T23	中国共产党发展党员工作细则	序列日期落在培养区间	思想汇报日期未落在对应培养考察区间内	{}	2 份越界	2024-09-10 ~ 2025-08-30	《》中为 2 份越界，不符合“序列日期落在培养区间”要求（2024-09-10 ~ 2025-08-30）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	229988362a2e86e0ed843510b7e013efd428dd09	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.318388+08	2026-10-17 18:36:18.318389+08
170	42	12	50	50	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 50}	body	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	34af97a10ee60d501b57be1de902add5046cee8a	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.318445+08	2026-10-17 18:36:18.318446+08
171	42	12	51	51	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 51}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	5d576ebf9482bf3082a595ea539737c2163848a8	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.318496+08	2026-10-17 18:36:18.318497+08
172	42	12	50	50	AI_RULE	FORMAT	WARN	R-F06	学校党员发展材料规范	篇幅下限	正文字数 39，不足 3000	{"material_id": 50}	39	3000	材料正文字数不足规定篇幅	\N	f	0.9	e76484a5ce94836a7499b5f8940409907207dda7	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.318549+08	2026-10-17 18:36:18.31855+08
173	42	12	49	49	AI_RULE	CONTENT	WARN	R-C01	党章及发展党员工作细则；学校审核标准	政治术语规范	指导思想并列表述有缺项	{"snippet": "马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想", "material_id": 49}	马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想	马克思列宁主义、毛泽东思想、邓小平理论、“三个代表”重要思想、科学发展观、习近平新时代中国特色社会主义思想	出现不规范政治术语或并列顺序错误	\N	f	0.9	9b50fe6f8c561004eb7742ba274c543d67b3d838	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.318621+08	2026-10-17 18:36:18.318621+08
191	48	13	53	53	AI_RULE	FORMAT	BLOCK	R-F03	学校党员发展材料规范	签名齐全	本人签名未检测到签名	{"material_id": 53}	无	应有签名	《入党志愿书》本人签名 未检测到签名，请本人（或相关负责人）补签。	\N	f	0.9	3492e0d93a5febe78db21e6a9292b6dad3a07c7b	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.6415+08	2026-10-17 18:36:18.6415+08
174	42	12	49	49	AI_RULE	CONTENT	WARN	R-C04	党章及发展党员工作细则；学校审核标准	入党动机表述	入党动机表述需关注：“入党可以评优评奖”	{"snippet": "入党可以评优评奖", "material_id": 49}	入党可以评优评奖	理想信念导向	请从理想信念、服务师生、发挥作用等角度重写入党动机。	\N	t	0.9	4b73298e80ea20ab903a81304d76e21bbf21ae5c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.318661+08	2026-10-17 18:36:18.318661+08
175	42	12	49	49	AI_RULE	CONTENT	WARN	R-C04	党章及发展党员工作细则；学校审核标准	入党动机表述	入党动机表述需关注：“为了好找工作”	{"snippet": "为了好找工作", "material_id": 49}	为了好找工作	理想信念导向	请结合对党的认识和自身成长经历写明入党动机。	\N	t	0.9	00159c08930903f72add7d962dd29ee64703b046	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.31869+08	2026-10-17 18:36:18.31869+08
176	42	12	50	50	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：家庭主要成员、成长经历、思想演变	{"snippet": "缺", "material_id": 50}	缺	应包含 家庭主要成员、成长经历、思想演变	材料缺少模板规定的内容要素	\N	f	0.9	3adee87807b8b31050ef114399e1b1a3a31c016c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.318727+08	2026-10-17 18:36:18.318728+08
177	42	12	51	51	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 51}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	e2eeb5f760392640cdd696ebe86434e10acdfed8	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.318761+08	2026-10-17 18:36:18.318761+08
178	42	12	49	49	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	姓名与档案不一致	{"snippet": "演示学生", "material_id": 49}	演示学生	演示学生14	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	69a40f3ae7c04ae439174eab03d292066ab63183	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.318789+08	2026-10-17 18:36:18.318789+08
179	42	12	50	50	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	出生日期与档案不一致	{"snippet": "2004-01-01", "material_id": 50}	2004-01-01	2003-05-12	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	4a1a44672577535842ef5ff3bbd9f1b746093c26	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.318817+08	2026-10-17 18:36:18.318818+08
180	48	13	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《上级党委派人谈话记录》	应交 1 份，已交 0 份，缺少 1 份。上级党委派人谈话记录	{"checklist_item_id": 19}	0	1	缺少《上级党委派人谈话记录》1 份（应交 1 份，已交 0 份）。请按要求补交：上级党委派人谈话记录。	\N	f	0.9	02d406caffdb054371475cf98f5799d29b9dd144	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.641106+08	2026-10-17 18:36:18.641108+08
181	48	13	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《上级党委审批意见》	应交 1 份，已交 0 份，缺少 1 份。上级党委审批意见	{"checklist_item_id": 20}	0	1	缺少《上级党委审批意见》1 份（应交 1 份，已交 0 份）。请按要求补交：上级党委审批意见。	\N	f	0.9	282669a4c1ba1b5b0d57fec9e5fcfde3cc06e34f	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.641183+08	2026-10-17 18:36:18.641183+08
182	48	13	\N	\N	AI_RULE	TIME	BLOCK	R-T20	中国共产党发展党员工作细则	同一节点多来源一致	节点冲突：T19	{}	T19	多来源一致	《》中为 T19，不符合“同一节点多来源一致”要求（多来源一致）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	5569b826211e6f99a5beeadf047c070b83b0239c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.64122+08	2026-10-17 18:36:18.641221+08
183	48	13	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T10,T11	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	ff456394583aaa985c3c3be83c6d0088cf66efdb	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.641252+08	2026-10-17 18:36:18.641253+08
184	48	13	\N	\N	AI_RULE	TIME	BLOCK	R-T22	中国共产党发展党员工作细则	阶段必填节点与单调递增	当前阶段关键时间节点缺失或顺序颠倒	{}	T14->T20	关键节点严格递增	《》中为 T14->T20，不符合“阶段必填节点与单调递增”要求（关键节点严格递增）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	8581edbb854d94dd754e7838561e8778816c7989	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.641282+08	2026-10-17 18:36:18.641283+08
185	48	13	53	53	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 53}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	8be3b125ddd2e1f0dd16a1b2c80255caca333f0d	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.641315+08	2026-10-17 18:36:18.641315+08
186	48	13	54	54	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 54}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	56b857fa6019f5cc6354ed57bd5669aff43a03f6	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.641346+08	2026-10-17 18:36:18.641346+08
187	48	13	55	55	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 55}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	61e2814682d3423ee6a92a24f12cfec8b6398fae	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.641376+08	2026-10-17 18:36:18.641376+08
188	48	13	56	56	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 56}	body	应包含 title,body	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	d2fd5338212192a38f5d35d1279f47bd22ddd747	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.641404+08	2026-10-17 18:36:18.641404+08
189	48	13	57	57	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 57}	body	应包含 title,body,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	79f7534d4986442b083d9145e9a90882a56bc8c7	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.641432+08	2026-10-17 18:36:18.641433+08
190	48	13	58	58	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 58}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	e55c159a04d3e387528d1f309ebe9628c764d6be	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.641462+08	2026-10-17 18:36:18.641462+08
192	48	13	53	53	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	姓名与档案不一致	{"snippet": "演示学生", "material_id": 53}	演示学生	演示学生16	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	4d8557c765ca523954163d1e70a9bbf59ffe4563	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.641529+08	2026-10-17 18:36:18.641529+08
193	53	14	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《写实簿·预备党员考察部分》	应交 1 份，已交 0 份，缺少 1 份。写实簿预备党员考察部分	{"checklist_item_id": 22}	0	1	缺少《写实簿·预备党员考察部分》1 份（应交 1 份，已交 0 份）。请按要求补交：写实簿预备党员考察部分。	\N	f	0.9	ea3a5912f136481d35cb4311956f6fb72c3865f7	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.778509+08	2026-10-17 18:36:18.778511+08
194	53	14	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《上级党委审批转正意见》	应交 1 份，已交 0 份，缺少 1 份。上级党委审批转正意见	{"checklist_item_id": 25}	0	1	缺少《上级党委审批转正意见》1 份（应交 1 份，已交 0 份）。请按要求补交：上级党委审批转正意见。	\N	f	0.9	44dbf57023407049a3c375af371b7cfb4f11e42e	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.778687+08	2026-10-17 18:36:18.778688+08
195	53	14	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《思想汇报》	应交 4 份，已交 0 份，缺少 4 份。预备期每季度至少一份思想汇报	{"checklist_item_id": 26}	0	4	缺少《思想汇报》4 份（应交 4 份，已交 0 份）。请按要求补交：预备期每季度至少一份思想汇报。	\N	f	0.9	b822922008621d745f152aa9e61ca03ab1183034	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.778765+08	2026-10-17 18:36:18.778766+08
196	53	14	\N	\N	AI_RULE	TIME	BLOCK	R-T20	中国共产党发展党员工作细则	同一节点多来源一致	节点冲突：T11,T14,T20	{}	T11,T14,T20	多来源一致	《》中为 T11,T14,T20，不符合“同一节点多来源一致”要求（多来源一致）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	83a664d89fc5fb5ea098cc8d406840517c5f33d5	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.778837+08	2026-10-17 18:36:18.778838+08
197	53	14	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T19	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	e417b5496dd18a3d3d4f41bb1a69e6952f54df99	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.778903+08	2026-10-17 18:36:18.778903+08
198	53	14	\N	\N	AI_RULE	TIME	BLOCK	R-T22	中国共产党发展党员工作细则	阶段必填节点与单调递增	缺少 T19	{}	缺失 T19	阶段必填节点齐全	《》中为 缺失 T19，不符合“阶段必填节点与单调递增”要求（阶段必填节点齐全）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	49d5fb696e42d5a0a4af8b96fceab32f60404425	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.778972+08	2026-10-17 18:36:18.778972+08
199	53	14	59	59	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 59}	body,signature	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	0a36db11b5365dafd249353962eb159bdf9a2093	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.779033+08	2026-10-17 18:36:18.779034+08
200	53	14	60	60	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 60}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	547fe36a373c5166ad4c35761340865ab32790ec	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.779093+08	2026-10-17 18:36:18.779094+08
201	53	14	61	61	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 61}	body	应包含 title,body,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	550a3a6fef65d6de5035b8c93da5200a2d5bbbb4	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.779152+08	2026-10-17 18:36:18.779153+08
202	53	14	59	59	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 59}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	93976525a202bd59c58153c33665961d08c5ec65	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.779211+08	2026-10-17 18:36:18.779212+08
208	57	16	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《政治审查材料》	应交 1 份，已交 0 份，缺少 1 份。政治审查材料	{"checklist_item_id": 11}	0	1	缺少《政治审查材料》1 份（应交 1 份，已交 0 份）。请按要求补交：政治审查材料。	\N	f	0.9	d54d125051786d628b7f668fff5b64c9c77fe60c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.16073+08	2026-10-17 18:36:19.160731+08
209	57	16	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《集中培训结业证书》	应交 1 份，已交 0 份，缺少 1 份。集中培训结业证书	{"checklist_item_id": 12}	0	1	缺少《集中培训结业证书》1 份（应交 1 份，已交 0 份）。请按要求补交：集中培训结业证书。	\N	f	0.9	ffaca8c9d99a22a690909577b59c36cfe00ded4e	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.160821+08	2026-10-17 18:36:19.160822+08
210	57	16	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《写实簿·发展对象考察部分》	应交 1 份，已交 0 份，缺少 1 份。写实簿发展对象考察部分	{"checklist_item_id": 13}	0	1	缺少《写实簿·发展对象考察部分》1 份（应交 1 份，已交 0 份）。请按要求补交：写实簿发展对象考察部分。	\N	f	0.9	f3ce00a714e76e4da498f001d62fdeb73595ba39	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.160877+08	2026-10-17 18:36:19.160877+08
211	57	16	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《思想汇报》	应交 5 份，已交 3 份，缺少 2 份。每季度至少一份思想汇报	{"checklist_item_id": 14}	3	5	缺少《思想汇报》2 份（应交 5 份，已交 3 份）。请按要求补交：每季度至少一份思想汇报。	\N	f	0.9	3ecf2968464ecbacc34ba93a0b7fa3bee2237bdc	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.160925+08	2026-10-17 18:36:19.160926+08
212	57	16	\N	\N	AI_RULE	TIME	BLOCK	R-T05	中国共产党发展党员工作细则	积极分子培养满一年	间隔 11 个月 20 天，不足 1 YEAR	{"node_code": "T08"}	11 个月 20 天	≥ 1 YEAR	《》中T08为 11 个月 20 天，不符合“积极分子培养满一年”要求（≥ 1 YEAR）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	88b2a22720c273901ff055f427fad5d6a9b9ab4c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.160974+08	2026-10-17 18:36:19.160974+08
205	54	15	63	63	AI_RULE	FORMAT	BLOCK	R-F03	学校党员发展材料规范	签名齐全	谈话人签名未检测到签名	{"material_id": 63}	无	应有签名	《党组织派人谈话记录》谈话人签名 未检测到签名，请本人（或相关负责人）补签。	\N	f	0.9	b580e5f55a58f9e52dfddfa5099e3c56fc14fa0f	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.879063+08	2026-10-17 18:36:18.879063+08
206	54	15	62	62	AI_RULE	CONTENT	WARN	R-C01	党章及发展党员工作细则；学校审核标准	政治术语规范	指导思想并列表述有缺项	{"snippet": "马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想", "material_id": 62}	马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想	马克思列宁主义、毛泽东思想、邓小平理论、“三个代表”重要思想、科学发展观、习近平新时代中国特色社会主义思想	出现不规范政治术语或并列顺序错误	\N	f	0.9	4f33328cf8c37e941d40f28d6f94feb1bac0e3e4	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.879096+08	2026-10-17 18:36:18.879097+08
207	54	15	62	62	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	姓名与档案不一致	{"snippet": "演示学生", "material_id": 62}	演示学生	演示学生18	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	50f285f7c1ba545205e6b7ab06431757cabdb652	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:18.879128+08	2026-10-17 18:36:18.879129+08
272	72	20	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T01	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	7b0433541f34e6ff13d738aa67e14f7f453f0ee1	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.868478+08	2026-10-17 18:36:19.86848+08
273	72	20	84	84	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 84}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	ee54c18af76ae13fbe591c46e5fe801be00b5fef	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.868568+08	2026-10-17 18:36:19.868569+08
274	72	20	84	84	AI_RULE	FORMAT	BLOCK	R-F03	学校党员发展材料规范	签名齐全	谈话人签名未检测到签名	{"material_id": 84}	无	应有签名	《党组织派人谈话记录》谈话人签名 未检测到签名，请本人（或相关负责人）补签。	\N	f	0.9	9a65a8cea10ce33fd21a39514216408501d820d0	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.868619+08	2026-10-17 18:36:19.86862+08
275	72	20	83	83	AI_RULE	CONTENT	WARN	R-C01	党章及发展党员工作细则；学校审核标准	政治术语规范	指导思想并列表述有缺项	{"snippet": "马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想", "material_id": 83}	马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想	马克思列宁主义、毛泽东思想、邓小平理论、“三个代表”重要思想、科学发展观、习近平新时代中国特色社会主义思想	出现不规范政治术语或并列顺序错误	\N	f	0.9	aec52f4f8b6cb1d30fc1a4136631a21e3f9d09ee	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.868662+08	2026-10-17 18:36:19.868662+08
276	72	20	83	83	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	姓名与档案不一致	{"snippet": "演示学生", "material_id": 83}	演示学生	演示学生24	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	9fe71420391efd73ca5e7c24d069b69435a22f8b	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.8687+08	2026-10-17 18:36:19.868701+08
213	57	16	\N	\N	AI_RULE	TIME	WARN	R-T06	中国共产党发展党员工作细则	思想汇报相邻间隔	相邻间隔超过 3 MONTH	{}	3 处超间隔	相邻 ≤ 3 MONTH	《》中为 3 处超间隔，不符合“思想汇报相邻间隔”要求（相邻 ≤ 3 MONTH）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	cf6df7d5c267fd795ee57f39d46aef9aa22ed8d7	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.161019+08	2026-10-17 18:36:19.16102+08
214	57	16	\N	\N	AI_RULE	TIME	BLOCK	R-T07	中国共产党发展党员工作细则	思想汇报按期提交	1 个周期不足	{}	实交 6 份 / 4 个周期	每周期至少 1 份	《》中为 实交 6 份 / 4 个周期，不符合“思想汇报按期提交”要求（每周期至少 1 份）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	651be8191e11ebb30a0eee826d1afc7067384fd5	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.161066+08	2026-10-17 18:36:19.161066+08
215	57	16	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T01	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	7b0433541f34e6ff13d738aa67e14f7f453f0ee1	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.161109+08	2026-10-17 18:36:19.16111+08
216	57	16	\N	\N	AI_RULE	TIME	WARN	R-T23	中国共产党发展党员工作细则	序列日期落在培养区间	思想汇报日期未落在对应培养考察区间内	{}	2 份越界	2024-09-10 ~ 2025-08-30	《》中为 2 份越界，不符合“序列日期落在培养区间”要求（2024-09-10 ~ 2025-08-30）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	229988362a2e86e0ed843510b7e013efd428dd09	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.161151+08	2026-10-17 18:36:19.161151+08
217	57	16	65	65	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 65}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	3f0ed4c05dd458cd5183707a8deddcbad154adcb	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.161193+08	2026-10-17 18:36:19.161193+08
218	57	16	66	66	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 66}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	43de69680096fe000df23687d6a94fb1fbb60c34	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.161233+08	2026-10-17 18:36:19.161233+08
219	57	16	67	67	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 67}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	7b15a760ecb8d06344520a4de542b9a5110846ad	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.161261+08	2026-10-17 18:36:19.161261+08
220	57	16	68	68	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 68}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	cbeb6a69e9d548da9d08eb2c76173f2ad7c34edb	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.161289+08	2026-10-17 18:36:19.161289+08
221	57	16	69	69	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：signature	{"material_id": 69}	signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	65430ca55a7289374977631620691745c44d6b38	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.161316+08	2026-10-17 18:36:19.161317+08
222	57	16	69	69	AI_RULE	FORMAT	WARN	R-F06	学校党员发展材料规范	篇幅下限	正文字数 516，不足 3000	{"material_id": 69}	516	3000	材料正文字数不足规定篇幅	\N	f	0.9	3799152ee44bdf03ded4a84963e33696661bc283	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.161344+08	2026-10-17 18:36:19.161345+08
223	57	16	64	64	AI_RULE	CONTENT	WARN	R-C01	党章及发展党员工作细则；学校审核标准	政治术语规范	指导思想并列表述有缺项	{"snippet": "马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想", "material_id": 64}	马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想	马克思列宁主义、毛泽东思想、邓小平理论、“三个代表”重要思想、科学发展观、习近平新时代中国特色社会主义思想	出现不规范政治术语或并列顺序错误	\N	f	0.9	7abd37cf318082b866c38febeff6ea916ec67d8e	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.161372+08	2026-10-17 18:36:19.161372+08
224	57	16	65	65	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 65}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	7f515494146f708b6dcdaa2d37e0020866bcdc44	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.161402+08	2026-10-17 18:36:19.161402+08
225	57	16	66	66	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 66}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	822763a65656a79eb7f29c80a85383d038a14e54	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.16143+08	2026-10-17 18:36:19.16143+08
226	57	16	67	67	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 67}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	aac0401b12b1d542cce020deb319458b634e982a	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.161458+08	2026-10-17 18:36:19.161458+08
227	57	16	64	64	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	姓名与档案不一致	{"snippet": "演示学生", "material_id": 64}	演示学生	演示学生19	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	c454eee74dd878efba4237f54a889790779f3cde	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.161486+08	2026-10-17 18:36:19.161486+08
228	60	17	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《支委会确定发展对象记录》	应交 1 份，已交 0 份，缺少 1 份。支委会确定发展对象记录	{"checklist_item_id": 10}	0	1	缺少《支委会确定发展对象记录》1 份（应交 1 份，已交 0 份）。请按要求补交：支委会确定发展对象记录。	\N	f	0.9	a14816de9623777c76f088d00e203aacbffdcf09	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.302071+08	2026-10-17 18:36:19.302074+08
229	60	17	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《政治审查材料》	应交 1 份，已交 0 份，缺少 1 份。政治审查材料	{"checklist_item_id": 11}	0	1	缺少《政治审查材料》1 份（应交 1 份，已交 0 份）。请按要求补交：政治审查材料。	\N	f	0.9	d54d125051786d628b7f668fff5b64c9c77fe60c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.30221+08	2026-10-17 18:36:19.302211+08
230	60	17	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《集中培训结业证书》	应交 1 份，已交 0 份，缺少 1 份。集中培训结业证书	{"checklist_item_id": 12}	0	1	缺少《集中培训结业证书》1 份（应交 1 份，已交 0 份）。请按要求补交：集中培训结业证书。	\N	f	0.9	ffaca8c9d99a22a690909577b59c36cfe00ded4e	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.302269+08	2026-10-17 18:36:19.302269+08
231	60	17	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《写实簿·发展对象考察部分》	应交 1 份，已交 0 份，缺少 1 份。写实簿发展对象考察部分	{"checklist_item_id": 13}	0	1	缺少《写实簿·发展对象考察部分》1 份（应交 1 份，已交 0 份）。请按要求补交：写实簿发展对象考察部分。	\N	f	0.9	f3ce00a714e76e4da498f001d62fdeb73595ba39	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.302315+08	2026-10-17 18:36:19.302315+08
232	60	17	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《思想汇报》	应交 5 份，已交 1 份，缺少 4 份。每季度至少一份思想汇报	{"checklist_item_id": 14}	1	5	缺少《思想汇报》4 份（应交 5 份，已交 1 份）。请按要求补交：每季度至少一份思想汇报。	\N	f	0.9	3ecf2968464ecbacc34ba93a0b7fa3bee2237bdc	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.302363+08	2026-10-17 18:36:19.302363+08
233	60	17	\N	\N	AI_RULE	TIME	BLOCK	R-T05	中国共产党发展党员工作细则	积极分子培养满一年	间隔 11 个月 20 天，不足 1 YEAR	{"node_code": "T08"}	11 个月 20 天	≥ 1 YEAR	《》中T08为 11 个月 20 天，不符合“积极分子培养满一年”要求（≥ 1 YEAR）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	88b2a22720c273901ff055f427fad5d6a9b9ab4c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.302412+08	2026-10-17 18:36:19.302412+08
234	60	17	\N	\N	AI_RULE	TIME	WARN	R-T06	中国共产党发展党员工作细则	思想汇报相邻间隔	相邻间隔超过 3 MONTH	{}	1 处超间隔	相邻 ≤ 3 MONTH	《》中为 1 处超间隔，不符合“思想汇报相邻间隔”要求（相邻 ≤ 3 MONTH）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	d573fe8a048c5e4f4037f87661fbd9447c785a91	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.302458+08	2026-10-17 18:36:19.302459+08
235	60	17	\N	\N	AI_RULE	TIME	BLOCK	R-T07	中国共产党发展党员工作细则	思想汇报按期提交	3 个周期不足	{}	实交 3 份 / 4 个周期	每周期至少 1 份	《》中为 实交 3 份 / 4 个周期，不符合“思想汇报按期提交”要求（每周期至少 1 份）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	5f5774cdf6e704e82bae15f7d10922feae6d3de0	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.302504+08	2026-10-17 18:36:19.302504+08
236	60	17	\N	\N	AI_RULE	TIME	BLOCK	R-T20	中国共产党发展党员工作细则	同一节点多来源一致	节点冲突：T01	{}	T01	多来源一致	《》中为 T01，不符合“同一节点多来源一致”要求（多来源一致）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	be362baf116f03e83999efb6666f72a067822107	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.302535+08	2026-10-17 18:36:19.302535+08
237	60	17	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T01	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	7b0433541f34e6ff13d738aa67e14f7f453f0ee1	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.302566+08	2026-10-17 18:36:19.302566+08
238	60	17	\N	\N	AI_RULE	TIME	WARN	R-T23	中国共产党发展党员工作细则	序列日期落在培养区间	思想汇报日期未落在对应培养考察区间内	{}	2 份越界	2024-09-10 ~ 2025-08-30	《》中为 2 份越界，不符合“序列日期落在培养区间”要求（2024-09-10 ~ 2025-08-30）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	229988362a2e86e0ed843510b7e013efd428dd09	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.302597+08	2026-10-17 18:36:19.302597+08
239	60	17	71	71	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 71}	body	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	d2a6ca69cdccefe9cdac3bddd8bee27b857b3719	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.30263+08	2026-10-17 18:36:19.30263+08
240	60	17	72	72	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 72}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	ee329bdce35d606f7a323a04bf5f3c80c8b43fc2	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.302661+08	2026-10-17 18:36:19.302661+08
241	60	17	71	71	AI_RULE	FORMAT	WARN	R-F06	学校党员发展材料规范	篇幅下限	正文字数 39，不足 3000	{"material_id": 71}	39	3000	材料正文字数不足规定篇幅	\N	f	0.9	075c08b05c5a2438775d0f5c339a9410e8c567ec	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.302693+08	2026-10-17 18:36:19.302693+08
242	60	17	70	70	AI_RULE	CONTENT	WARN	R-C01	党章及发展党员工作细则；学校审核标准	政治术语规范	指导思想并列表述有缺项	{"snippet": "马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想", "material_id": 70}	马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想	马克思列宁主义、毛泽东思想、邓小平理论、“三个代表”重要思想、科学发展观、习近平新时代中国特色社会主义思想	出现不规范政治术语或并列顺序错误	\N	f	0.9	ffebc21f6a3b201913eab7502498f9ae9561071c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.302723+08	2026-10-17 18:36:19.302723+08
243	60	17	70	70	AI_RULE	CONTENT	WARN	R-C04	党章及发展党员工作细则；学校审核标准	入党动机表述	入党动机表述需关注：“入党可以评优评奖”	{"snippet": "入党可以评优评奖", "material_id": 70}	入党可以评优评奖	理想信念导向	请从理想信念、服务师生、发挥作用等角度重写入党动机。	\N	t	0.9	7992daa298da6c60060fa5b876156a9c50f154de	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.302754+08	2026-10-17 18:36:19.302754+08
261	66	18	74	74	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	姓名与档案不一致	{"snippet": "演示学生", "material_id": 74}	演示学生	演示学生22	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	7f8972fdb0f93fc98b6aca913ed21ec88d0a906e	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.636905+08	2026-10-17 18:36:19.636905+08
244	60	17	70	70	AI_RULE	CONTENT	WARN	R-C04	党章及发展党员工作细则；学校审核标准	入党动机表述	入党动机表述需关注：“为了好找工作”	{"snippet": "为了好找工作", "material_id": 70}	为了好找工作	理想信念导向	请结合对党的认识和自身成长经历写明入党动机。	\N	t	0.9	c5e4329092949ae41ebe9f7d8ea4da51016ebcca	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.302783+08	2026-10-17 18:36:19.302783+08
245	60	17	71	71	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：家庭主要成员、成长经历、思想演变	{"snippet": "缺", "material_id": 71}	缺	应包含 家庭主要成员、成长经历、思想演变	材料缺少模板规定的内容要素	\N	f	0.9	7c6b5eee97edb53d11e8e3b3439a80b3fce4aa60	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.302814+08	2026-10-17 18:36:19.302814+08
246	60	17	72	72	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 72}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	3913f7c3120363a218f26b5b8257b35ad7e59dc8	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.302845+08	2026-10-17 18:36:19.302845+08
247	60	17	70	70	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	姓名与档案不一致	{"snippet": "演示学生", "material_id": 70}	演示学生	演示学生20	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	f1134bf8d7ea44907218fd1ae2587d827b11b45a	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.302875+08	2026-10-17 18:36:19.302876+08
248	60	17	71	71	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	出生日期与档案不一致	{"snippet": "2004-01-01", "material_id": 71}	2004-01-01	2003-05-12	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	1bf5a6465de19a689a7720131e1990883c6b24b2	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.302907+08	2026-10-17 18:36:19.302907+08
249	66	18	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《上级党委派人谈话记录》	应交 1 份，已交 0 份，缺少 1 份。上级党委派人谈话记录	{"checklist_item_id": 19}	0	1	缺少《上级党委派人谈话记录》1 份（应交 1 份，已交 0 份）。请按要求补交：上级党委派人谈话记录。	\N	f	0.9	02d406caffdb054371475cf98f5799d29b9dd144	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.636492+08	2026-10-17 18:36:19.636493+08
250	66	18	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《上级党委审批意见》	应交 1 份，已交 0 份，缺少 1 份。上级党委审批意见	{"checklist_item_id": 20}	0	1	缺少《上级党委审批意见》1 份（应交 1 份，已交 0 份）。请按要求补交：上级党委审批意见。	\N	f	0.9	282669a4c1ba1b5b0d57fec9e5fcfde3cc06e34f	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.636571+08	2026-10-17 18:36:19.636572+08
251	66	18	\N	\N	AI_RULE	TIME	BLOCK	R-T20	中国共产党发展党员工作细则	同一节点多来源一致	节点冲突：T19	{}	T19	多来源一致	《》中为 T19，不符合“同一节点多来源一致”要求（多来源一致）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	5569b826211e6f99a5beeadf047c070b83b0239c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.63661+08	2026-10-17 18:36:19.63661+08
252	66	18	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T10,T11	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	ff456394583aaa985c3c3be83c6d0088cf66efdb	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.636642+08	2026-10-17 18:36:19.636642+08
253	66	18	\N	\N	AI_RULE	TIME	BLOCK	R-T22	中国共产党发展党员工作细则	阶段必填节点与单调递增	当前阶段关键时间节点缺失或顺序颠倒	{}	T14->T20	关键节点严格递增	《》中为 T14->T20，不符合“阶段必填节点与单调递增”要求（关键节点严格递增）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	8581edbb854d94dd754e7838561e8778816c7989	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.636673+08	2026-10-17 18:36:19.636673+08
254	66	18	74	74	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 74}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	11ac3500801261e74a8e0d07b6a5d992863b1cb4	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.636704+08	2026-10-17 18:36:19.636704+08
255	66	18	75	75	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 75}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	7a24cd0419c51b338c41b8682f3784a1d0010e2d	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.636734+08	2026-10-17 18:36:19.636734+08
256	66	18	76	76	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 76}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	94f27a6f90692b6c1928f3f9d2ac1548c8dc3950	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.636763+08	2026-10-17 18:36:19.636763+08
257	66	18	77	77	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 77}	body	应包含 title,body	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	bf9e191ea18541c1f114c97b102204d0e141459d	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.636791+08	2026-10-17 18:36:19.636791+08
258	66	18	78	78	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 78}	body	应包含 title,body,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	be18338bdb07c07cf47da3484782312dfdb63ff6	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.636819+08	2026-10-17 18:36:19.63682+08
259	66	18	79	79	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 79}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	2a5ad6017bff2d4100e50287d238cd6e6fda9a07	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.636848+08	2026-10-17 18:36:19.636849+08
260	66	18	74	74	AI_RULE	FORMAT	BLOCK	R-F03	学校党员发展材料规范	签名齐全	本人签名未检测到签名	{"material_id": 74}	无	应有签名	《入党志愿书》本人签名 未检测到签名，请本人（或相关负责人）补签。	\N	f	0.9	2d915e0d70f4d30822789c7e9156a97e4ef3853e	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.636877+08	2026-10-17 18:36:19.636877+08
262	71	19	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《写实簿·预备党员考察部分》	应交 1 份，已交 0 份，缺少 1 份。写实簿预备党员考察部分	{"checklist_item_id": 22}	0	1	缺少《写实簿·预备党员考察部分》1 份（应交 1 份，已交 0 份）。请按要求补交：写实簿预备党员考察部分。	\N	f	0.9	ea3a5912f136481d35cb4311956f6fb72c3865f7	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.788572+08	2026-10-17 18:36:19.788575+08
263	71	19	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《上级党委审批转正意见》	应交 1 份，已交 0 份，缺少 1 份。上级党委审批转正意见	{"checklist_item_id": 25}	0	1	缺少《上级党委审批转正意见》1 份（应交 1 份，已交 0 份）。请按要求补交：上级党委审批转正意见。	\N	f	0.9	44dbf57023407049a3c375af371b7cfb4f11e42e	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.788652+08	2026-10-17 18:36:19.788653+08
264	71	19	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《思想汇报》	应交 4 份，已交 0 份，缺少 4 份。预备期每季度至少一份思想汇报	{"checklist_item_id": 26}	0	4	缺少《思想汇报》4 份（应交 4 份，已交 0 份）。请按要求补交：预备期每季度至少一份思想汇报。	\N	f	0.9	b822922008621d745f152aa9e61ca03ab1183034	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.78869+08	2026-10-17 18:36:19.78869+08
265	71	19	\N	\N	AI_RULE	TIME	BLOCK	R-T20	中国共产党发展党员工作细则	同一节点多来源一致	节点冲突：T11,T14,T20	{}	T11,T14,T20	多来源一致	《》中为 T11,T14,T20，不符合“同一节点多来源一致”要求（多来源一致）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	83a664d89fc5fb5ea098cc8d406840517c5f33d5	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.788722+08	2026-10-17 18:36:19.788722+08
266	71	19	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T19	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	e417b5496dd18a3d3d4f41bb1a69e6952f54df99	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.788754+08	2026-10-17 18:36:19.788755+08
267	71	19	\N	\N	AI_RULE	TIME	BLOCK	R-T22	中国共产党发展党员工作细则	阶段必填节点与单调递增	缺少 T19	{}	缺失 T19	阶段必填节点齐全	《》中为 缺失 T19，不符合“阶段必填节点与单调递增”要求（阶段必填节点齐全）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	49d5fb696e42d5a0a4af8b96fceab32f60404425	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.788786+08	2026-10-17 18:36:19.788786+08
268	71	19	80	80	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 80}	body,signature	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	3c2fb41a483c67e3b743706d4a331f440670a708	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.788817+08	2026-10-17 18:36:19.788817+08
269	71	19	81	81	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 81}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	d6bdad69c9c1a91e1de29a09fcf6c1ac48035bd9	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.788846+08	2026-10-17 18:36:19.788846+08
270	71	19	82	82	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 82}	body	应包含 title,body,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	4a029c38b8ff706d1fc76613b853c3ee257d665e	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.788875+08	2026-10-17 18:36:19.788875+08
271	71	19	80	80	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 80}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	70061b19b635d9ae0565559f6e016f7fba9d32af	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:19.788904+08	2026-10-17 18:36:19.788904+08
277	8	21	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《推荐/推优材料》	应交 1 份，已交 0 份，缺少 1 份。党员推荐或团组织推优材料	{"checklist_item_id": 3}	0	1	缺少《推荐/推优材料》1 份（应交 1 份，已交 0 份）。请按要求补交：党员推荐或团组织推优材料。	\N	f	0.9	fb193a570b68bbfd50bc15ceb13a5fad0589ee47	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:08.602896+08	2026-10-17 18:53:08.602899+08
278	8	21	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《支委会研究确定积极分子记录》	应交 1 份，已交 0 份，缺少 1 份。支委会（支部大会）研究确定积极分子记录	{"checklist_item_id": 4}	0	1	缺少《支委会研究确定积极分子记录》1 份（应交 1 份，已交 0 份）。请按要求补交：支委会（支部大会）研究确定积极分子记录。	\N	f	0.9	e455627724cb21970aab6943eb292dcc2e16e827	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:08.60301+08	2026-10-17 18:53:08.603011+08
279	8	21	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《积极分子备案材料》	应交 1 份，已交 0 份，缺少 1 份。积极分子备案材料	{"checklist_item_id": 5}	0	1	缺少《积极分子备案材料》1 份（应交 1 份，已交 0 份）。请按要求补交：积极分子备案材料。	\N	f	0.9	3fd3a4bd20f0e5464d3ded1a53c3c993c6de88ca	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:08.603053+08	2026-10-17 18:53:08.603053+08
280	8	21	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《写实簿·积极分子培养考察部分》	应交 1 份，已交 0 份，缺少 1 份。写实簿积极分子培养考察部分	{"checklist_item_id": 6}	0	1	缺少《写实簿·积极分子培养考察部分》1 份（应交 1 份，已交 0 份）。请按要求补交：写实簿积极分子培养考察部分。	\N	f	0.9	b5563b403a91136d79cf8eca16f4324988ea3a45	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:08.603087+08	2026-10-17 18:53:08.603087+08
281	8	21	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《思想汇报》	应交 9 份，已交 0 份，缺少 9 份。每季度至少一份思想汇报	{"checklist_item_id": 7}	0	9	缺少《思想汇报》9 份（应交 9 份，已交 0 份）。请按要求补交：每季度至少一份思想汇报。	\N	f	0.9	b646980d2aecbfeb247d94fd4620bb8e1ee281cc	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:08.60312+08	2026-10-17 18:53:08.60312+08
282	8	21	\N	\N	AI_RULE	COMPLETENESS	INFO	COMPLETENESS	\N	可选项《积极分子培训结业证明》未交齐	可选项应交 1 份，已交 0 份。	{"checklist_item_id": 8}	0	1	缺少《》 份（应交  份，已交  份）。请按要求补交：。截止日期：。	请补交思想汇报 1 份，写明近期学习与实践收获。	f	0.9	9ee3370bd0bc839399b86a732d396dceb3997de3	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:08.60315+08	2026-10-17 18:53:08.603151+08
283	8	21	\N	\N	AI_RULE	TIME	WARN	R-T04	中国共产党发展党员工作细则	确定积极分子距申请不过久	间隔 1 年 5 个月 26 天 超过 30 DAY	{}	1 年 5 个月 26 天	≤ 30 DAY	《》中为 1 年 5 个月 26 天，不符合“确定积极分子距申请不过久”要求（≤ 30 DAY）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	5fde87d1fbb8cec2703933c49330eb41b855f36f	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:08.603183+08	2026-10-17 18:53:08.603183+08
284	8	21	\N	\N	AI_RULE	TIME	WARN	R-T06	中国共产党发展党员工作细则	思想汇报相邻间隔	相邻间隔超过 3 MONTH	{}	1 处超间隔	相邻 ≤ 3 MONTH	《》中为 1 处超间隔，不符合“思想汇报相邻间隔”要求（相邻 ≤ 3 MONTH）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	d573fe8a048c5e4f4037f87661fbd9447c785a91	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:08.603215+08	2026-10-17 18:53:08.603215+08
285	8	21	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T01	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	7b0433541f34e6ff13d738aa67e14f7f453f0ee1	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:08.603254+08	2026-10-17 18:53:08.603255+08
286	8	21	\N	\N	AI_RULE	TIME	BLOCK	R-T22	中国共产党发展党员工作细则	阶段必填节点与单调递增	缺少 T03	{}	缺失 T03	阶段必填节点齐全	《》中为 缺失 T03，不符合“阶段必填节点与单调递增”要求（阶段必填节点齐全）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	be70f07ef638b917e086dcdff24f0abe9a1cf5d0	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:08.603286+08	2026-10-17 18:53:08.603286+08
287	8	21	\N	\N	AI_RULE	TIME	WARN	R-T23	中国共产党发展党员工作细则	序列日期落在培养区间	思想汇报日期未落在对应培养考察区间内	{}	1 份越界	2024-09-10 ~ 2026-10-17	《》中为 1 份越界，不符合“序列日期落在培养区间”要求（2024-09-10 ~ 2026-10-17）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	6c1a2a2b74e1ddf2ba659f17cc21de06e5414f85	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:08.603316+08	2026-10-17 18:53:08.603316+08
288	8	21	10	10	AI_RULE	CONTENT	WARN	R-C01	党章及发展党员工作细则；学校审核标准	政治术语规范	指导思想并列表述有缺项	{"snippet": "马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想", "material_id": 10}	马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想	马克思列宁主义、毛泽东思想、邓小平理论、“三个代表”重要思想、科学发展观、习近平新时代中国特色社会主义思想	出现不规范政治术语或并列顺序错误	\N	f	0.9	5bf612fecea46a596e083d259cf0cf69a813d59f	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:08.603347+08	2026-10-17 18:53:08.603348+08
289	8	21	10	10	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	姓名与档案不一致	{"snippet": "演示学生", "material_id": 10}	演示学生	演示学生03	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	b8826bb9dcdf513a7eb3ff41a7fdebf83a6cb38c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:08.603377+08	2026-10-17 18:53:08.603377+08
1	3	1	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《政治审查材料》	应交 1 份，已交 0 份，缺少 1 份。政治审查材料	{"checklist_item_id": 11}	0	1	缺少《政治审查材料》1 份（应交 1 份，已交 0 份）。请按要求补交：政治审查材料。	\N	f	0.9	d54d125051786d628b7f668fff5b64c9c77fe60c	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.263372+08	2026-10-17 18:53:30.627902+08
2	3	1	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《集中培训结业证书》	应交 1 份，已交 0 份，缺少 1 份。集中培训结业证书	{"checklist_item_id": 12}	0	1	缺少《集中培训结业证书》1 份（应交 1 份，已交 0 份）。请按要求补交：集中培训结业证书。	\N	f	0.9	ffaca8c9d99a22a690909577b59c36cfe00ded4e	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.263499+08	2026-10-17 18:53:30.627902+08
3	3	1	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《写实簿·发展对象考察部分》	应交 1 份，已交 0 份，缺少 1 份。写实簿发展对象考察部分	{"checklist_item_id": 13}	0	1	缺少《写实簿·发展对象考察部分》1 份（应交 1 份，已交 0 份）。请按要求补交：写实簿发展对象考察部分。	\N	f	0.9	f3ce00a714e76e4da498f001d62fdeb73595ba39	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.263541+08	2026-10-17 18:53:30.627902+08
4	3	1	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《思想汇报》	应交 5 份，已交 3 份，缺少 2 份。每季度至少一份思想汇报	{"checklist_item_id": 14}	3	5	缺少《思想汇报》2 份（应交 5 份，已交 3 份）。请按要求补交：每季度至少一份思想汇报。	\N	f	0.9	3ecf2968464ecbacc34ba93a0b7fa3bee2237bdc	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.263575+08	2026-10-17 18:53:30.627902+08
5	3	1	\N	\N	AI_RULE	TIME	BLOCK	R-T05	中国共产党发展党员工作细则	积极分子培养满一年	间隔 11 个月 20 天，不足 1 YEAR	{"node_code": "T08"}	11 个月 20 天	≥ 1 YEAR	《》中T08为 11 个月 20 天，不符合“积极分子培养满一年”要求（≥ 1 YEAR）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	88b2a22720c273901ff055f427fad5d6a9b9ab4c	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.26361+08	2026-10-17 18:53:30.627902+08
6	3	1	\N	\N	AI_RULE	TIME	WARN	R-T06	中国共产党发展党员工作细则	思想汇报相邻间隔	相邻间隔超过 3 MONTH	{}	3 处超间隔	相邻 ≤ 3 MONTH	《》中为 3 处超间隔，不符合“思想汇报相邻间隔”要求（相邻 ≤ 3 MONTH）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	cf6df7d5c267fd795ee57f39d46aef9aa22ed8d7	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.263642+08	2026-10-17 18:53:30.627902+08
7	3	1	\N	\N	AI_RULE	TIME	BLOCK	R-T07	中国共产党发展党员工作细则	思想汇报按期提交	1 个周期不足	{}	实交 6 份 / 4 个周期	每周期至少 1 份	《》中为 实交 6 份 / 4 个周期，不符合“思想汇报按期提交”要求（每周期至少 1 份）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	651be8191e11ebb30a0eee826d1afc7067384fd5	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.263673+08	2026-10-17 18:53:30.627902+08
8	3	1	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T01	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	7b0433541f34e6ff13d738aa67e14f7f453f0ee1	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.263706+08	2026-10-17 18:53:30.627902+08
9	3	1	\N	\N	AI_RULE	TIME	WARN	R-T23	中国共产党发展党员工作细则	序列日期落在培养区间	思想汇报日期未落在对应培养考察区间内	{}	2 份越界	2024-09-10 ~ 2025-08-30	《》中为 2 份越界，不符合“序列日期落在培养区间”要求（2024-09-10 ~ 2025-08-30）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	229988362a2e86e0ed843510b7e013efd428dd09	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.263736+08	2026-10-17 18:53:30.627902+08
10	3	1	2	2	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 2}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	e4ec39b1b9a4131f399fbef4bb5492f0888d2f12	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.263765+08	2026-10-17 18:53:30.627902+08
11	3	1	3	3	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 3}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	5c9b767521e0e4b67105509b18f73123542b23f7	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.263795+08	2026-10-17 18:53:30.627902+08
12	3	1	4	4	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 4}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	df2eea41b16457c18b63a8b50ce17696b3bc6518	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.263824+08	2026-10-17 18:53:30.627902+08
13	3	1	5	5	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 5}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	bbd2df754334145fb619297b6d5b231719e42aa1	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.263853+08	2026-10-17 18:53:30.627902+08
14	3	1	6	6	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：signature	{"material_id": 6}	signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	d3905e87ac997f075b17913c69ca86777645b158	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.263882+08	2026-10-17 18:53:30.627902+08
15	3	1	6	6	AI_RULE	FORMAT	WARN	R-F06	学校党员发展材料规范	篇幅下限	正文字数 516，不足 3000	{"material_id": 6}	516	3000	材料正文字数不足规定篇幅	\N	f	0.9	2a9581b3a81ce3a10006cce035b86443f4e6fc84	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.263911+08	2026-10-17 18:53:30.627902+08
16	3	1	1	1	AI_RULE	CONTENT	WARN	R-C01	党章及发展党员工作细则；学校审核标准	政治术语规范	指导思想并列表述有缺项	{"snippet": "马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想", "material_id": 1}	马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想	马克思列宁主义、毛泽东思想、邓小平理论、“三个代表”重要思想、科学发展观、习近平新时代中国特色社会主义思想	出现不规范政治术语或并列顺序错误	\N	f	0.9	70743d07176a598d80a5c291671239057f23f417	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.263939+08	2026-10-17 18:53:30.627902+08
17	3	1	2	2	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 2}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	c1cb6603c23ecd6764547783bfd709cd086dacba	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.263968+08	2026-10-17 18:53:30.627902+08
18	3	1	3	3	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 3}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	319d9ebfbd4ee4d764d26c2609d56f365df2ad38	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.263996+08	2026-10-17 18:53:30.627902+08
19	3	1	4	4	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 4}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	e63209cccce963a14b2fe71f0bbab8cb5e72a618	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.264024+08	2026-10-17 18:53:30.627902+08
20	3	1	1	1	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	姓名与档案不一致	{"snippet": "演示学生", "material_id": 1}	演示学生	演示学生01	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	767ec91e45268fd815e8eaa2cd58bebeb1753283	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:36:16.264052+08	2026-10-17 18:53:30.627902+08
290	3	22	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《政治审查材料》	应交 1 份，已交 0 份，缺少 1 份。政治审查材料	{"checklist_item_id": 11}	0	1	缺少《政治审查材料》1 份（应交 1 份，已交 0 份）。请按要求补交：政治审查材料。	\N	f	0.9	d54d125051786d628b7f668fff5b64c9c77fe60c	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:30.683371+08	2026-10-17 19:17:49.701354+08
304	3	22	6	6	AI_RULE	FORMAT	WARN	R-F06	学校党员发展材料规范	篇幅下限	正文字数 516，不足 3000	{"material_id": 6}	516	3000	材料正文字数不足规定篇幅	\N	f	0.9	2a9581b3a81ce3a10006cce035b86443f4e6fc84	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:30.684026+08	2026-10-17 19:17:49.701354+08
291	3	22	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《集中培训结业证书》	应交 1 份，已交 0 份，缺少 1 份。集中培训结业证书	{"checklist_item_id": 12}	0	1	缺少《集中培训结业证书》1 份（应交 1 份，已交 0 份）。请按要求补交：集中培训结业证书。	\N	f	0.9	ffaca8c9d99a22a690909577b59c36cfe00ded4e	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:30.683463+08	2026-10-17 19:17:49.701354+08
292	3	22	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《写实簿·发展对象考察部分》	应交 1 份，已交 0 份，缺少 1 份。写实簿发展对象考察部分	{"checklist_item_id": 13}	0	1	缺少《写实簿·发展对象考察部分》1 份（应交 1 份，已交 0 份）。请按要求补交：写实簿发展对象考察部分。	\N	f	0.9	f3ce00a714e76e4da498f001d62fdeb73595ba39	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:30.683502+08	2026-10-17 19:17:49.701354+08
293	3	22	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《思想汇报》	应交 5 份，已交 3 份，缺少 2 份。每季度至少一份思想汇报	{"checklist_item_id": 14}	3	5	缺少《思想汇报》2 份（应交 5 份，已交 3 份）。请按要求补交：每季度至少一份思想汇报。	\N	f	0.9	3ecf2968464ecbacc34ba93a0b7fa3bee2237bdc	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:30.683541+08	2026-10-17 19:17:49.701354+08
294	3	22	\N	\N	AI_RULE	TIME	BLOCK	R-T05	中国共产党发展党员工作细则	积极分子培养满一年	间隔 11 个月 20 天，不足 1 YEAR	{"node_code": "T08"}	11 个月 20 天	≥ 1 YEAR	《》中T08为 11 个月 20 天，不符合“积极分子培养满一年”要求（≥ 1 YEAR）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	88b2a22720c273901ff055f427fad5d6a9b9ab4c	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:30.683587+08	2026-10-17 19:17:49.701354+08
295	3	22	\N	\N	AI_RULE	TIME	WARN	R-T06	中国共产党发展党员工作细则	思想汇报相邻间隔	相邻间隔超过 3 MONTH	{}	3 处超间隔	相邻 ≤ 3 MONTH	《》中为 3 处超间隔，不符合“思想汇报相邻间隔”要求（相邻 ≤ 3 MONTH）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	cf6df7d5c267fd795ee57f39d46aef9aa22ed8d7	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:30.683652+08	2026-10-17 19:17:49.701354+08
296	3	22	\N	\N	AI_RULE	TIME	BLOCK	R-T07	中国共产党发展党员工作细则	思想汇报按期提交	1 个周期不足	{}	实交 6 份 / 4 个周期	每周期至少 1 份	《》中为 实交 6 份 / 4 个周期，不符合“思想汇报按期提交”要求（每周期至少 1 份）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	651be8191e11ebb30a0eee826d1afc7067384fd5	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:30.683687+08	2026-10-17 19:17:49.701354+08
297	3	22	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T01	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	7b0433541f34e6ff13d738aa67e14f7f453f0ee1	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:30.683717+08	2026-10-17 19:17:49.701354+08
298	3	22	\N	\N	AI_RULE	TIME	WARN	R-T23	中国共产党发展党员工作细则	序列日期落在培养区间	思想汇报日期未落在对应培养考察区间内	{}	2 份越界	2024-09-10 ~ 2025-08-30	《》中为 2 份越界，不符合“序列日期落在培养区间”要求（2024-09-10 ~ 2025-08-30）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	229988362a2e86e0ed843510b7e013efd428dd09	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:30.683753+08	2026-10-17 19:17:49.701354+08
299	3	22	2	2	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 2}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	e4ec39b1b9a4131f399fbef4bb5492f0888d2f12	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:30.683812+08	2026-10-17 19:17:49.701354+08
300	3	22	3	3	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 3}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	5c9b767521e0e4b67105509b18f73123542b23f7	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:30.683857+08	2026-10-17 19:17:49.701354+08
301	3	22	4	4	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 4}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	df2eea41b16457c18b63a8b50ce17696b3bc6518	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:30.683889+08	2026-10-17 19:17:49.701354+08
302	3	22	5	5	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 5}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	bbd2df754334145fb619297b6d5b231719e42aa1	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:30.683918+08	2026-10-17 19:17:49.701354+08
303	3	22	6	6	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：signature	{"material_id": 6}	signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	d3905e87ac997f075b17913c69ca86777645b158	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:30.683957+08	2026-10-17 19:17:49.701354+08
305	3	22	1	1	AI_RULE	CONTENT	WARN	R-C01	党章及发展党员工作细则；学校审核标准	政治术语规范	指导思想并列表述有缺项	{"snippet": "马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想", "material_id": 1}	马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想	马克思列宁主义、毛泽东思想、邓小平理论、“三个代表”重要思想、科学发展观、习近平新时代中国特色社会主义思想	出现不规范政治术语或并列顺序错误	\N	f	0.9	70743d07176a598d80a5c291671239057f23f417	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:30.684082+08	2026-10-17 19:17:49.701354+08
306	3	22	2	2	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 2}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	c1cb6603c23ecd6764547783bfd709cd086dacba	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:30.684151+08	2026-10-17 19:17:49.701354+08
307	3	22	3	3	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 3}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	319d9ebfbd4ee4d764d26c2609d56f365df2ad38	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:30.68421+08	2026-10-17 19:17:49.701354+08
308	3	22	4	4	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 4}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	e63209cccce963a14b2fe71f0bbab8cb5e72a618	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:30.684268+08	2026-10-17 19:17:49.701354+08
309	3	22	1	1	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	姓名与档案不一致	{"snippet": "演示学生", "material_id": 1}	演示学生	演示学生01	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	767ec91e45268fd815e8eaa2cd58bebeb1753283	f	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 18:53:30.684318+08	2026-10-17 19:17:49.701354+08
310	3	23	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《政治审查材料》	应交 1 份，已交 0 份，缺少 1 份。政治审查材料	{"checklist_item_id": 11}	0	1	缺少《政治审查材料》1 份（应交 1 份，已交 0 份）。请按要求补交：政治审查材料。	\N	f	0.9	d54d125051786d628b7f668fff5b64c9c77fe60c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 19:17:49.764242+08	2026-10-17 19:17:49.764243+08
311	3	23	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《集中培训结业证书》	应交 1 份，已交 0 份，缺少 1 份。集中培训结业证书	{"checklist_item_id": 12}	0	1	缺少《集中培训结业证书》1 份（应交 1 份，已交 0 份）。请按要求补交：集中培训结业证书。	\N	f	0.9	ffaca8c9d99a22a690909577b59c36cfe00ded4e	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 19:17:49.764333+08	2026-10-17 19:17:49.764334+08
312	3	23	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《写实簿·发展对象考察部分》	应交 1 份，已交 0 份，缺少 1 份。写实簿发展对象考察部分	{"checklist_item_id": 13}	0	1	缺少《写实簿·发展对象考察部分》1 份（应交 1 份，已交 0 份）。请按要求补交：写实簿发展对象考察部分。	\N	f	0.9	f3ce00a714e76e4da498f001d62fdeb73595ba39	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 19:17:49.764374+08	2026-10-17 19:17:49.764375+08
313	3	23	\N	\N	AI_RULE	COMPLETENESS	BLOCK	COMPLETENESS	党员发展各阶段材料清单	缺少《思想汇报》	应交 5 份，已交 3 份，缺少 2 份。每季度至少一份思想汇报	{"checklist_item_id": 14}	3	5	缺少《思想汇报》2 份（应交 5 份，已交 3 份）。请按要求补交：每季度至少一份思想汇报。	\N	f	0.9	3ecf2968464ecbacc34ba93a0b7fa3bee2237bdc	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 19:17:49.764409+08	2026-10-17 19:17:49.76441+08
314	3	23	\N	\N	AI_RULE	TIME	BLOCK	R-T05	中国共产党发展党员工作细则	积极分子培养满一年	间隔 11 个月 20 天，不足 1 YEAR	{"node_code": "T08"}	11 个月 20 天	≥ 1 YEAR	《》中T08为 11 个月 20 天，不符合“积极分子培养满一年”要求（≥ 1 YEAR）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	88b2a22720c273901ff055f427fad5d6a9b9ab4c	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 19:17:49.764444+08	2026-10-17 19:17:49.764444+08
315	3	23	\N	\N	AI_RULE	TIME	WARN	R-T06	中国共产党发展党员工作细则	思想汇报相邻间隔	相邻间隔超过 3 MONTH	{}	3 处超间隔	相邻 ≤ 3 MONTH	《》中为 3 处超间隔，不符合“思想汇报相邻间隔”要求（相邻 ≤ 3 MONTH）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	cf6df7d5c267fd795ee57f39d46aef9aa22ed8d7	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 19:17:49.764476+08	2026-10-17 19:17:49.764476+08
316	3	23	\N	\N	AI_RULE	TIME	BLOCK	R-T07	中国共产党发展党员工作细则	思想汇报按期提交	1 个周期不足	{}	实交 6 份 / 4 个周期	每周期至少 1 份	《》中为 实交 6 份 / 4 个周期，不符合“思想汇报按期提交”要求（每周期至少 1 份）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	651be8191e11ebb30a0eee826d1afc7067384fd5	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 19:17:49.764508+08	2026-10-17 19:17:49.764508+08
317	3	23	\N	\N	AI_RULE	TIME	BLOCK	R-T21	中国共产党发展党员工作细则	日期合法且不晚于上传日	抽取日期不完整、不合法或晚于材料上传日	{}	T01	日期合法且不晚于上传日	《》第  页日期“”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	f	0.9	7b0433541f34e6ff13d738aa67e14f7f453f0ee1	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 19:17:49.764537+08	2026-10-17 19:17:49.764538+08
318	3	23	\N	\N	AI_RULE	TIME	WARN	R-T23	中国共产党发展党员工作细则	序列日期落在培养区间	思想汇报日期未落在对应培养考察区间内	{}	2 份越界	2024-09-10 ~ 2025-08-30	《》中为 2 份越界，不符合“序列日期落在培养区间”要求（2024-09-10 ~ 2025-08-30）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	f	0.9	229988362a2e86e0ed843510b7e013efd428dd09	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 19:17:49.764567+08	2026-10-17 19:17:49.764567+08
319	3	23	2	2	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 2}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	e4ec39b1b9a4131f399fbef4bb5492f0888d2f12	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 19:17:49.764599+08	2026-10-17 19:17:49.764599+08
320	3	23	3	3	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 3}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	5c9b767521e0e4b67105509b18f73123542b23f7	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 19:17:49.764628+08	2026-10-17 19:17:49.764628+08
321	3	23	4	4	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body	{"material_id": 4}	body	应包含 title,salutation,body,closing,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	df2eea41b16457c18b63a8b50ce17696b3bc6518	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 19:17:49.764658+08	2026-10-17 19:17:49.764658+08
322	3	23	5	5	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：body,signature	{"material_id": 5}	body,signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	bbd2df754334145fb619297b6d5b231719e42aa1	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 19:17:49.764689+08	2026-10-17 19:17:49.764689+08
323	3	23	6	6	AI_RULE	FORMAT	WARN	R-F01	学校党员发展材料规范	文书结构完整	缺少文书要素：signature	{"material_id": 6}	signature	应包含 title,body,signature,date	材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素	\N	f	0.9	d3905e87ac997f075b17913c69ca86777645b158	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 19:17:49.764718+08	2026-10-17 19:17:49.764718+08
324	3	23	6	6	AI_RULE	FORMAT	WARN	R-F06	学校党员发展材料规范	篇幅下限	正文字数 516，不足 3000	{"material_id": 6}	516	3000	材料正文字数不足规定篇幅	\N	f	0.9	2a9581b3a81ce3a10006cce035b86443f4e6fc84	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 19:17:49.764746+08	2026-10-17 19:17:49.764747+08
325	3	23	1	1	AI_RULE	CONTENT	WARN	R-C01	党章及发展党员工作细则；学校审核标准	政治术语规范	指导思想并列表述有缺项	{"snippet": "马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想", "material_id": 1}	马克思列宁主义、毛泽东思想、邓小平理论、科学发展观、习近平新时代中国特色社会主义思想	马克思列宁主义、毛泽东思想、邓小平理论、“三个代表”重要思想、科学发展观、习近平新时代中国特色社会主义思想	出现不规范政治术语或并列顺序错误	\N	f	0.9	70743d07176a598d80a5c291671239057f23f417	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 19:17:49.764775+08	2026-10-17 19:17:49.764775+08
326	3	23	2	2	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 2}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	c1cb6603c23ecd6764547783bfd709cd086dacba	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 19:17:49.764807+08	2026-10-17 19:17:49.764807+08
327	3	23	3	3	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 3}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	319d9ebfbd4ee4d764d26c2609d56f365df2ad38	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 19:17:49.764835+08	2026-10-17 19:17:49.764836+08
328	3	23	4	4	AI_RULE	CONTENT	WARN	R-C05	党章及发展党员工作细则；学校审核标准	内容要素完整	缺少内容要素：入党动机、理论认识	{"snippet": "缺", "material_id": 4}	缺	应包含 入党动机、理论认识	材料缺少模板规定的内容要素	\N	f	0.9	e63209cccce963a14b2fe71f0bbab8cb5e72a618	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 19:17:49.764866+08	2026-10-17 19:17:49.764867+08
329	3	23	1	1	AI_RULE	CONTENT	BLOCK	R-C06	党章及发展党员工作细则；学校审核标准	基本信息一致	姓名与档案不一致	{"snippet": "演示学生", "material_id": 1}	演示学生	演示学生01	姓名、学号、出生日期等基本信息与档案或其他材料不一致	\N	f	0.9	767ec91e45268fd815e8eaa2cd58bebeb1753283	t	PENDING	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	OPEN	\N	\N	f	2026-10-17 19:17:49.764895+08	2026-10-17 19:17:49.764895+08
\.


--
-- Data for Name: jobs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.jobs (id, job_type, status, parent_id, target_type, target_id, params, total, done_count, failed_count, progress, stage_text, result, error, attempts, max_attempts, created_by, created_at, started_at, heartbeat_at, finished_at) FROM stdin;
105	AI_CHECK	SUCCEEDED	\N	submission	8	{"use_llm": true, "trigger_type": "REVIEW", "submission_id": 8}	1	0	0	100	执行中	{"report_id": 21, "report_no": 1}	\N	1	3	5	2026-10-17 18:53:07.894018+08	2026-10-17 18:53:08.546225+08	2026-10-17 18:53:08.548756+08	2026-10-17 18:53:08.614158+08
6	PARSE	SUCCEEDED	\N	material_version	6	{"version_id": 6}	1	0	0	100	执行中	{"version_id": 6}	\N	1	3	1	2026-10-17 18:36:06.458647+08	2026-10-17 18:36:16.069188+08	2026-10-17 18:36:16.069878+08	2026-10-17 18:36:16.159083+08
10	PARSE	SUCCEEDED	\N	material_version	9	{"version_id": 9}	1	0	0	100	执行中	{"version_id": 9}	\N	1	3	1	2026-10-17 18:36:06.702596+08	2026-10-17 18:36:16.280745+08	2026-10-17 18:36:16.282748+08	2026-10-17 18:36:16.330676+08
12	PARSE	SUCCEEDED	\N	material_version	10	{"version_id": 10}	1	0	0	100	执行中	{"version_id": 10}	\N	1	3	1	2026-10-17 18:36:06.788181+08	2026-10-17 18:36:16.334058+08	2026-10-17 18:36:16.335284+08	2026-10-17 18:36:16.38332+08
13	PARSE	SUCCEEDED	\N	material_version	11	{"version_id": 11}	1	0	0	100	执行中	{"version_id": 11}	\N	1	3	1	2026-10-17 18:36:06.907012+08	2026-10-17 18:36:16.387164+08	2026-10-17 18:36:16.387844+08	2026-10-17 18:36:16.435241+08
14	PARSE	SUCCEEDED	\N	material_version	12	{"version_id": 12}	1	0	0	100	执行中	{"version_id": 12}	\N	1	3	1	2026-10-17 18:36:07.00956+08	2026-10-17 18:36:16.424328+08	2026-10-17 18:36:16.425286+08	2026-10-17 18:36:16.478726+08
15	PARSE	SUCCEEDED	\N	material_version	13	{"version_id": 13}	1	0	0	100	执行中	{"version_id": 13}	\N	1	3	1	2026-10-17 18:36:07.124541+08	2026-10-17 18:36:16.438496+08	2026-10-17 18:36:16.43932+08	2026-10-17 18:36:16.519416+08
16	PARSE	SUCCEEDED	\N	material_version	14	{"version_id": 14}	1	0	0	100	执行中	{"version_id": 14}	\N	1	3	1	2026-10-17 18:36:07.241084+08	2026-10-17 18:36:16.482436+08	2026-10-17 18:36:16.483103+08	2026-10-17 18:36:16.560199+08
17	PARSE	SUCCEEDED	\N	material_version	15	{"version_id": 15}	1	0	0	100	执行中	{"version_id": 15}	\N	1	3	1	2026-10-17 18:36:07.345972+08	2026-10-17 18:36:16.522678+08	2026-10-17 18:36:16.523437+08	2026-10-17 18:36:16.602019+08
18	PARSE	SUCCEEDED	\N	material_version	16	{"version_id": 16}	1	0	0	100	执行中	{"version_id": 16}	\N	1	3	1	2026-10-17 18:36:07.446685+08	2026-10-17 18:36:16.563775+08	2026-10-17 18:36:16.564399+08	2026-10-17 18:36:16.642033+08
20	PARSE	SUCCEEDED	\N	material_version	17	{"version_id": 17}	1	0	0	100	执行中	{"version_id": 17}	\N	1	3	1	2026-10-17 18:36:07.529756+08	2026-10-17 18:36:16.645613+08	2026-10-17 18:36:16.646586+08	2026-10-17 18:36:16.697353+08
21	PARSE	SUCCEEDED	\N	material_version	18	{"version_id": 18}	1	0	0	100	执行中	{"version_id": 18}	\N	1	3	1	2026-10-17 18:36:07.65085+08	2026-10-17 18:36:16.695513+08	2026-10-17 18:36:16.696149+08	2026-10-17 18:36:16.738549+08
23	AI_CHECK	SUCCEEDED	\N	submission	17	{"trigger_type": "REVIEW", "submission_id": 17}	1	0	0	100	执行中	{"report_id": 4, "report_no": 1}	\N	1	3	1	2026-10-17 18:36:07.759985+08	2026-10-17 18:36:16.742559+08	2026-10-17 18:36:16.74321+08	2026-10-17 18:36:16.828962+08
24	PARSE	SUCCEEDED	\N	material_version	20	{"version_id": 20}	1	0	0	100	执行中	{"version_id": 20}	\N	1	3	1	2026-10-17 18:36:07.852946+08	2026-10-17 18:36:16.786377+08	2026-10-17 18:36:16.787293+08	2026-10-17 18:36:16.836903+08
26	AI_CHECK	SUCCEEDED	\N	submission	18	{"trigger_type": "REVIEW", "submission_id": 18}	1	0	0	100	执行中	{"report_id": 5, "report_no": 1}	\N	1	3	1	2026-10-17 18:36:07.963292+08	2026-10-17 18:36:16.840018+08	2026-10-17 18:36:16.840666+08	2026-10-17 18:36:16.924483+08
27	PARSE	SUCCEEDED	\N	material_version	22	{"version_id": 22}	1	0	0	100	执行中	{"version_id": 22}	\N	1	3	1	2026-10-17 18:36:08.057851+08	2026-10-17 18:36:16.881955+08	2026-10-17 18:36:16.883273+08	2026-10-17 18:36:16.932335+08
29	PARSE	SUCCEEDED	\N	material_version	24	{"version_id": 24}	1	0	0	100	执行中	{"version_id": 24}	\N	1	3	1	2026-10-17 18:36:08.21383+08	2026-10-17 18:36:16.93582+08	2026-10-17 18:36:16.936488+08	2026-10-17 18:36:17.013899+08
30	PARSE	SUCCEEDED	\N	material_version	25	{"version_id": 25}	1	0	0	100	执行中	{"version_id": 25}	\N	1	3	1	2026-10-17 18:36:08.288046+08	2026-10-17 18:36:16.977297+08	2026-10-17 18:36:16.978226+08	2026-10-17 18:36:17.054314+08
32	PARSE	SUCCEEDED	\N	material_version	27	{"version_id": 27}	1	0	0	100	执行中	{"version_id": 27}	\N	1	3	1	2026-10-17 18:36:08.471704+08	2026-10-17 18:36:17.057532+08	2026-10-17 18:36:17.05818+08	2026-10-17 18:36:17.137118+08
34	PARSE	SUCCEEDED	\N	material_version	28	{"version_id": 28}	1	0	0	100	执行中	{"version_id": 28}	\N	1	3	1	2026-10-17 18:36:08.555713+08	2026-10-17 18:36:17.140751+08	2026-10-17 18:36:17.14168+08	2026-10-17 18:36:17.19439+08
35	PARSE	SUCCEEDED	\N	material_version	29	{"version_id": 29}	1	0	0	100	执行中	{"version_id": 29}	\N	1	3	1	2026-10-17 18:36:08.628033+08	2026-10-17 18:36:17.197295+08	2026-10-17 18:36:17.198125+08	2026-10-17 18:36:17.23805+08
36	PARSE	SUCCEEDED	\N	material_version	30	{"version_id": 30}	1	0	0	100	执行中	{"version_id": 30}	\N	1	3	1	2026-10-17 18:36:08.701293+08	2026-10-17 18:36:17.197542+08	2026-10-17 18:36:17.198255+08	2026-10-17 18:36:17.302045+08
38	PARSE	SUCCEEDED	\N	material_version	31	{"version_id": 31}	1	0	0	100	执行中	{"version_id": 31}	\N	1	3	1	2026-10-17 18:36:08.794959+08	2026-10-17 18:36:17.307329+08	2026-10-17 18:36:17.308379+08	2026-10-17 18:36:17.376636+08
39	PARSE	SUCCEEDED	\N	material_version	32	{"version_id": 32}	1	0	0	100	执行中	{"version_id": 32}	\N	1	3	1	2026-10-17 18:36:08.914841+08	2026-10-17 18:36:17.355372+08	2026-10-17 18:36:17.356036+08	2026-10-17 18:36:17.398988+08
40	PARSE	SUCCEEDED	\N	material_version	33	{"version_id": 33}	1	0	0	100	执行中	{"version_id": 33}	\N	1	3	1	2026-10-17 18:36:09.049922+08	2026-10-17 18:36:17.384246+08	2026-10-17 18:36:17.385053+08	2026-10-17 18:36:17.442424+08
42	PARSE	SUCCEEDED	\N	material_version	35	{"version_id": 35}	1	0	0	100	执行中	{"version_id": 35}	\N	1	3	1	2026-10-17 18:36:09.259921+08	2026-10-17 18:36:17.446324+08	2026-10-17 18:36:17.459344+08	2026-10-17 18:36:17.525833+08
43	PARSE	SUCCEEDED	\N	material_version	36	{"version_id": 36}	1	0	0	100	执行中	{"version_id": 36}	\N	1	3	1	2026-10-17 18:36:09.361095+08	2026-10-17 18:36:17.487052+08	2026-10-17 18:36:17.487808+08	2026-10-17 18:36:17.566377+08
45	AI_CHECK	SUCCEEDED	\N	submission	30	{"trigger_type": "REVIEW", "submission_id": 30}	1	0	0	100	执行中	{"report_id": 8, "report_no": 1}	\N	1	3	1	2026-10-17 18:36:09.471437+08	2026-10-17 18:36:17.569428+08	2026-10-17 18:36:17.570035+08	2026-10-17 18:36:17.666452+08
48	PARSE	SUCCEEDED	\N	material_version	40	{"version_id": 40}	1	0	0	100	执行中	{"version_id": 40}	\N	1	3	1	2026-10-17 18:36:09.753573+08	2026-10-17 18:36:17.677108+08	2026-10-17 18:36:17.677905+08	2026-10-17 18:36:17.754923+08
47	PARSE	SUCCEEDED	\N	material_version	39	{"version_id": 39}	1	0	0	100	执行中	{"version_id": 39}	\N	1	3	1	2026-10-17 18:36:09.653239+08	2026-10-17 18:36:17.66965+08	2026-10-17 18:36:17.671194+08	2026-10-17 18:36:17.714018+08
107	AI_CHECK	SUCCEEDED	106	submission	3	{"use_llm": true, "trigger_type": "BATCH", "submission_id": 3}	1	0	0	100	执行中	{"report_id": 22, "report_no": 2}	\N	1	3	5	2026-10-17 18:53:30.619322+08	2026-10-17 18:53:30.62514+08	2026-10-17 18:53:30.627305+08	2026-10-17 18:53:30.693824+08
106	BATCH_AI_CHECK	SUCCEEDED	\N	batch	\N	{"submission_ids": [3]}	1	1	0	100	已拆分子任务	{"total": 1, "failed": 0}	\N	1	3	5	2026-10-17 18:53:30.523004+08	2026-10-17 18:53:30.61721+08	2026-10-17 18:53:30.698603+08	2026-10-17 18:53:30.69861+08
55	PARSE	SUCCEEDED	\N	material_version	45	{"version_id": 45}	1	0	0	100	执行中	{"version_id": 45}	\N	1	3	1	2026-10-17 18:36:10.21612+08	2026-10-17 18:36:17.948686+08	2026-10-17 18:36:17.9501+08	2026-10-17 18:36:17.998393+08
56	PARSE	SUCCEEDED	\N	material_version	46	{"version_id": 46}	1	0	0	100	执行中	{"version_id": 46}	\N	1	3	1	2026-10-17 18:36:10.321227+08	2026-10-17 18:36:17.957466+08	2026-10-17 18:36:17.958078+08	2026-10-17 18:36:18.044008+08
57	PARSE	SUCCEEDED	\N	material_version	47	{"version_id": 47}	1	0	0	100	执行中	{"version_id": 47}	\N	1	3	1	2026-10-17 18:36:10.477438+08	2026-10-17 18:36:18.003662+08	2026-10-17 18:36:18.004542+08	2026-10-17 18:36:18.087675+08
60	PARSE	SUCCEEDED	\N	material_version	49	{"version_id": 49}	1	0	0	100	执行中	{"version_id": 49}	\N	1	3	1	2026-10-17 18:36:10.675936+08	2026-10-17 18:36:18.137221+08	2026-10-17 18:36:18.138294+08	2026-10-17 18:36:18.195963+08
59	AI_CHECK	SUCCEEDED	\N	submission	39	{"trigger_type": "REVIEW", "submission_id": 39}	1	0	0	100	执行中	{"report_id": 11, "report_no": 1}	\N	1	3	1	2026-10-17 18:36:10.573537+08	2026-10-17 18:36:18.092571+08	2026-10-17 18:36:18.106094+08	2026-10-17 18:36:18.194193+08
61	PARSE	SUCCEEDED	\N	material_version	50	{"version_id": 50}	1	0	0	100	执行中	{"version_id": 50}	\N	1	3	1	2026-10-17 18:36:10.773991+08	2026-10-17 18:36:18.197374+08	2026-10-17 18:36:18.198025+08	2026-10-17 18:36:18.239889+08
64	PARSE	SUCCEEDED	\N	material_version	52	{"version_id": 52}	1	0	0	100	执行中	{"version_id": 52}	\N	1	3	1	2026-10-17 18:36:11.006875+08	2026-10-17 18:36:18.284517+08	2026-10-17 18:36:18.285554+08	2026-10-17 18:36:18.351064+08
65	PARSE	SUCCEEDED	\N	material_version	53	{"version_id": 53}	1	0	0	100	执行中	{"version_id": 53}	\N	1	3	1	2026-10-17 18:36:11.184535+08	2026-10-17 18:36:18.330836+08	2026-10-17 18:36:18.331628+08	2026-10-17 18:36:18.376585+08
66	PARSE	SUCCEEDED	\N	material_version	54	{"version_id": 54}	1	0	0	100	执行中	{"version_id": 54}	\N	1	3	1	2026-10-17 18:36:11.368809+08	2026-10-17 18:36:18.353791+08	2026-10-17 18:36:18.354429+08	2026-10-17 18:36:18.423536+08
67	PARSE	SUCCEEDED	\N	material_version	55	{"version_id": 55}	1	0	0	100	执行中	{"version_id": 55}	\N	1	3	1	2026-10-17 18:36:11.524828+08	2026-10-17 18:36:18.381004+08	2026-10-17 18:36:18.381752+08	2026-10-17 18:36:18.465548+08
69	PARSE	SUCCEEDED	\N	material_version	57	{"version_id": 57}	1	0	0	100	执行中	{"version_id": 57}	\N	1	3	1	2026-10-17 18:36:11.859351+08	2026-10-17 18:36:18.470666+08	2026-10-17 18:36:18.471367+08	2026-10-17 18:36:18.556689+08
71	AI_CHECK	SUCCEEDED	\N	submission	48	{"trigger_type": "REVIEW", "submission_id": 48}	1	0	0	100	执行中	{"report_id": 13, "report_no": 1}	\N	1	3	1	2026-10-17 18:36:12.015236+08	2026-10-17 18:36:18.561449+08	2026-10-17 18:36:18.562172+08	2026-10-17 18:36:18.646718+08
72	PARSE	SUCCEEDED	\N	material_version	59	{"version_id": 59}	1	0	0	100	执行中	{"version_id": 59}	\N	1	3	1	2026-10-17 18:36:12.121944+08	2026-10-17 18:36:18.602258+08	2026-10-17 18:36:18.60329+08	2026-10-17 18:36:18.654971+08
74	PARSE	SUCCEEDED	\N	material_version	61	{"version_id": 61}	1	0	0	100	执行中	{"version_id": 61}	\N	1	3	1	2026-10-17 18:36:12.418543+08	2026-10-17 18:36:18.658486+08	2026-10-17 18:36:18.659201+08	2026-10-17 18:36:18.739552+08
76	PARSE	SUCCEEDED	\N	material_version	62	{"version_id": 62}	1	0	0	100	执行中	{"version_id": 62}	\N	1	3	1	2026-10-17 18:36:12.525379+08	2026-10-17 18:36:18.743519+08	2026-10-17 18:36:18.744828+08	2026-10-17 18:36:18.796054+08
77	PARSE	SUCCEEDED	\N	material_version	63	{"version_id": 63}	1	0	0	100	执行中	{"version_id": 63}	\N	1	3	1	2026-10-17 18:36:12.670989+08	2026-10-17 18:36:18.790468+08	2026-10-17 18:36:18.791505+08	2026-10-17 18:36:18.838862+08
79	PARSE	SUCCEEDED	\N	material_version	64	{"version_id": 64}	1	0	0	100	执行中	{"version_id": 64}	\N	1	3	1	2026-10-17 18:36:12.780359+08	2026-10-17 18:36:18.842665+08	2026-10-17 18:36:18.84361+08	2026-10-17 18:36:18.896034+08
80	PARSE	SUCCEEDED	\N	material_version	65	{"version_id": 65}	1	0	0	100	执行中	{"version_id": 65}	\N	1	3	1	2026-10-17 18:36:12.884188+08	2026-10-17 18:36:18.889712+08	2026-10-17 18:36:18.890804+08	2026-10-17 18:36:18.939235+08
81	PARSE	SUCCEEDED	\N	material_version	66	{"version_id": 66}	1	0	0	100	执行中	{"version_id": 66}	\N	1	3	1	2026-10-17 18:36:12.971909+08	2026-10-17 18:36:18.899509+08	2026-10-17 18:36:18.900276+08	2026-10-17 18:36:18.981615+08
82	PARSE	SUCCEEDED	\N	material_version	67	{"version_id": 67}	1	0	0	100	执行中	{"version_id": 67}	\N	1	3	1	2026-10-17 18:36:13.066543+08	2026-10-17 18:36:18.942781+08	2026-10-17 18:36:18.955798+08	2026-10-17 18:36:19.025151+08
84	PARSE	SUCCEEDED	\N	material_version	69	{"version_id": 69}	1	0	0	100	执行中	{"version_id": 69}	\N	1	3	1	2026-10-17 18:36:13.307831+08	2026-10-17 18:36:19.029543+08	2026-10-17 18:36:19.042759+08	2026-10-17 18:36:19.11224+08
86	PARSE	SUCCEEDED	\N	material_version	70	{"version_id": 70}	1	0	0	100	执行中	{"version_id": 70}	\N	1	3	1	2026-10-17 18:36:13.420186+08	2026-10-17 18:36:19.115927+08	2026-10-17 18:36:19.116903+08	2026-10-17 18:36:19.175166+08
87	PARSE	SUCCEEDED	\N	material_version	71	{"version_id": 71}	1	0	0	100	执行中	{"version_id": 71}	\N	1	3	1	2026-10-17 18:36:13.5358+08	2026-10-17 18:36:19.171818+08	2026-10-17 18:36:19.172557+08	2026-10-17 18:36:19.218489+08
89	AI_CHECK	SUCCEEDED	\N	submission	60	{"trigger_type": "REVIEW", "submission_id": 60}	1	0	0	100	执行中	{"report_id": 17, "report_no": 1}	\N	1	3	1	2026-10-17 18:36:13.653079+08	2026-10-17 18:36:19.222501+08	2026-10-17 18:36:19.223269+08	2026-10-17 18:36:19.311847+08
90	PARSE	SUCCEEDED	\N	material_version	73	{"version_id": 73}	1	0	0	100	执行中	{"version_id": 73}	\N	1	3	1	2026-10-17 18:36:13.766705+08	2026-10-17 18:36:19.265384+08	2026-10-17 18:36:19.266584+08	2026-10-17 18:36:19.324628+08
92	PARSE	SUCCEEDED	\N	material_version	75	{"version_id": 75}	1	0	0	100	执行中	{"version_id": 75}	\N	1	3	1	2026-10-17 18:36:14.083723+08	2026-10-17 18:36:19.341124+08	2026-10-17 18:36:19.341978+08	2026-10-17 18:36:19.412889+08
93	PARSE	SUCCEEDED	\N	material_version	76	{"version_id": 76}	1	0	0	100	执行中	{"version_id": 76}	\N	1	3	1	2026-10-17 18:36:14.242941+08	2026-10-17 18:36:19.373411+08	2026-10-17 18:36:19.374229+08	2026-10-17 18:36:19.455725+08
96	PARSE	SUCCEEDED	\N	material_version	79	{"version_id": 79}	1	0	0	100	执行中	{"version_id": 79}	\N	1	3	1	2026-10-17 18:36:14.654025+08	2026-10-17 18:36:19.504536+08	2026-10-17 18:36:19.505236+08	2026-10-17 18:36:19.590659+08
95	PARSE	SUCCEEDED	\N	material_version	78	{"version_id": 78}	1	0	0	100	执行中	{"version_id": 78}	\N	1	3	1	2026-10-17 18:36:14.548311+08	2026-10-17 18:36:19.460831+08	2026-10-17 18:36:19.474484+08	2026-10-17 18:36:19.545347+08
108	AI_CHECK	SUCCEEDED	\N	submission	3	{"use_llm": true, "trigger_type": "REVIEW", "submission_id": 3}	1	0	0	100	执行中	{"report_id": 23, "report_no": 3}	\N	1	3	5	2026-10-17 19:17:49.099473+08	2026-10-17 19:17:49.698685+08	2026-10-17 19:17:49.700928+08	2026-10-17 19:17:49.774329+08
51	PARSE	SUCCEEDED	\N	material_version	42	{"version_id": 42}	1	0	0	100	执行中	{"version_id": 42}	\N	1	3	1	2026-10-17 18:36:09.946483+08	2026-10-17 18:36:17.805276+08	2026-10-17 18:36:17.806415+08	2026-10-17 18:36:17.853331+08
1	PARSE	SUCCEEDED	\N	material_version	1	{"version_id": 1}	1	0	0	100	执行中	{"version_id": 1}	\N	1	3	1	2026-10-17 18:36:05.969411+08	2026-10-17 18:36:15.54252+08	2026-10-17 18:36:15.551621+08	2026-10-17 18:36:15.907383+08
2	PARSE	SUCCEEDED	\N	material_version	2	{"version_id": 2}	1	0	0	100	执行中	{"version_id": 2}	\N	1	3	1	2026-10-17 18:36:06.045206+08	2026-10-17 18:36:15.543379+08	2026-10-17 18:36:15.544286+08	2026-10-17 18:36:15.974753+08
3	PARSE	SUCCEEDED	\N	material_version	3	{"version_id": 3}	1	0	0	100	执行中	{"version_id": 3}	\N	1	3	1	2026-10-17 18:36:06.123664+08	2026-10-17 18:36:15.914345+08	2026-10-17 18:36:15.915093+08	2026-10-17 18:36:16.018843+08
4	PARSE	SUCCEEDED	\N	material_version	4	{"version_id": 4}	1	0	0	100	执行中	{"version_id": 4}	\N	1	3	1	2026-10-17 18:36:06.28075+08	2026-10-17 18:36:15.979106+08	2026-10-17 18:36:15.98002+08	2026-10-17 18:36:16.06574+08
5	PARSE	SUCCEEDED	\N	material_version	5	{"version_id": 5}	1	0	0	100	执行中	{"version_id": 5}	\N	1	3	1	2026-10-17 18:36:06.383289+08	2026-10-17 18:36:16.022062+08	2026-10-17 18:36:16.022766+08	2026-10-17 18:36:16.110348+08
8	PARSE	SUCCEEDED	\N	material_version	7	{"version_id": 7}	1	0	0	100	执行中	{"version_id": 7}	\N	1	3	1	2026-10-17 18:36:06.55754+08	2026-10-17 18:36:16.164047+08	2026-10-17 18:36:16.165022+08	2026-10-17 18:36:16.224451+08
7	AI_CHECK	SUCCEEDED	\N	submission	3	{"trigger_type": "REVIEW", "submission_id": 3}	1	0	0	100	执行中	{"report_id": 1, "report_no": 1}	\N	1	3	1	2026-10-17 18:36:06.480381+08	2026-10-17 18:36:16.11484+08	2026-10-17 18:36:16.115901+08	2026-10-17 18:36:16.276529+08
9	PARSE	SUCCEEDED	\N	material_version	8	{"version_id": 8}	1	0	0	100	执行中	{"version_id": 8}	\N	1	3	1	2026-10-17 18:36:06.629545+08	2026-10-17 18:36:16.229377+08	2026-10-17 18:36:16.231577+08	2026-10-17 18:36:16.283992+08
11	AI_CHECK	SUCCEEDED	\N	submission	6	{"trigger_type": "REVIEW", "submission_id": 6}	1	0	0	100	执行中	{"report_id": 2, "report_no": 1}	\N	1	3	1	2026-10-17 18:36:06.711221+08	2026-10-17 18:36:16.287756+08	2026-10-17 18:36:16.288369+08	2026-10-17 18:36:16.416582+08
19	AI_CHECK	SUCCEEDED	\N	submission	12	{"trigger_type": "REVIEW", "submission_id": 12}	1	0	0	100	执行中	{"report_id": 3, "report_no": 1}	\N	1	3	1	2026-10-17 18:36:07.4548+08	2026-10-17 18:36:16.605262+08	2026-10-17 18:36:16.60587+08	2026-10-17 18:36:16.692674+08
22	PARSE	SUCCEEDED	\N	material_version	19	{"version_id": 19}	1	0	0	100	执行中	{"version_id": 19}	\N	1	3	1	2026-10-17 18:36:07.750654+08	2026-10-17 18:36:16.700795+08	2026-10-17 18:36:16.70138+08	2026-10-17 18:36:16.781646+08
25	PARSE	SUCCEEDED	\N	material_version	21	{"version_id": 21}	1	0	0	100	执行中	{"version_id": 21}	\N	1	3	1	2026-10-17 18:36:07.955028+08	2026-10-17 18:36:16.832672+08	2026-10-17 18:36:16.834018+08	2026-10-17 18:36:16.878474+08
28	PARSE	SUCCEEDED	\N	material_version	23	{"version_id": 23}	1	0	0	100	执行中	{"version_id": 23}	\N	1	3	1	2026-10-17 18:36:08.135986+08	2026-10-17 18:36:16.928608+08	2026-10-17 18:36:16.931091+08	2026-10-17 18:36:16.973254+08
31	PARSE	SUCCEEDED	\N	material_version	26	{"version_id": 26}	1	0	0	100	执行中	{"version_id": 26}	\N	1	3	1	2026-10-17 18:36:08.394625+08	2026-10-17 18:36:17.017296+08	2026-10-17 18:36:17.01792+08	2026-10-17 18:36:17.095376+08
33	AI_CHECK	SUCCEEDED	\N	submission	21	{"trigger_type": "REVIEW", "submission_id": 21}	1	0	0	100	执行中	{"report_id": 6, "report_no": 1}	\N	1	3	1	2026-10-17 18:36:08.479492+08	2026-10-17 18:36:17.099007+08	2026-10-17 18:36:17.099713+08	2026-10-17 18:36:17.195213+08
37	AI_CHECK	SUCCEEDED	\N	submission	24	{"trigger_type": "REVIEW", "submission_id": 24}	1	0	0	100	执行中	{"report_id": 7, "report_no": 1}	\N	1	3	1	2026-10-17 18:36:08.709813+08	2026-10-17 18:36:17.241509+08	2026-10-17 18:36:17.242198+08	2026-10-17 18:36:17.353084+08
41	PARSE	SUCCEEDED	\N	material_version	34	{"version_id": 34}	1	0	0	100	执行中	{"version_id": 34}	\N	1	3	1	2026-10-17 18:36:09.160833+08	2026-10-17 18:36:17.402021+08	2026-10-17 18:36:17.403182+08	2026-10-17 18:36:17.484006+08
44	PARSE	SUCCEEDED	\N	material_version	37	{"version_id": 37}	1	0	0	100	执行中	{"version_id": 37}	\N	1	3	1	2026-10-17 18:36:09.46423+08	2026-10-17 18:36:17.529348+08	2026-10-17 18:36:17.530019+08	2026-10-17 18:36:17.609746+08
46	PARSE	SUCCEEDED	\N	material_version	38	{"version_id": 38}	1	0	0	100	执行中	{"version_id": 38}	\N	1	3	1	2026-10-17 18:36:09.553034+08	2026-10-17 18:36:17.614233+08	2026-10-17 18:36:17.615404+08	2026-10-17 18:36:17.673466+08
49	AI_CHECK	SUCCEEDED	\N	submission	35	{"trigger_type": "REVIEW", "submission_id": 35}	1	0	0	100	执行中	{"report_id": 9, "report_no": 1}	\N	1	3	1	2026-10-17 18:36:09.76214+08	2026-10-17 18:36:17.717067+08	2026-10-17 18:36:17.717771+08	2026-10-17 18:36:17.801074+08
50	PARSE	SUCCEEDED	\N	material_version	41	{"version_id": 41}	1	0	0	100	执行中	{"version_id": 41}	\N	1	3	1	2026-10-17 18:36:09.84104+08	2026-10-17 18:36:17.757669+08	2026-10-17 18:36:17.758926+08	2026-10-17 18:36:17.812154+08
53	PARSE	SUCCEEDED	\N	material_version	43	{"version_id": 43}	1	0	0	100	执行中	{"version_id": 43}	\N	1	3	1	2026-10-17 18:36:10.035436+08	2026-10-17 18:36:17.856292+08	2026-10-17 18:36:17.856937+08	2026-10-17 18:36:17.907438+08
52	AI_CHECK	SUCCEEDED	\N	submission	36	{"trigger_type": "REVIEW", "submission_id": 36}	1	0	0	100	执行中	{"report_id": 10, "report_no": 1}	\N	1	3	1	2026-10-17 18:36:09.952989+08	2026-10-17 18:36:17.8155+08	2026-10-17 18:36:17.816179+08	2026-10-17 18:36:17.944998+08
54	PARSE	SUCCEEDED	\N	material_version	44	{"version_id": 44}	1	0	0	100	执行中	{"version_id": 44}	\N	1	3	1	2026-10-17 18:36:10.116072+08	2026-10-17 18:36:17.910466+08	2026-10-17 18:36:17.91119+08	2026-10-17 18:36:17.9544+08
58	PARSE	SUCCEEDED	\N	material_version	48	{"version_id": 48}	1	0	0	100	执行中	{"version_id": 48}	\N	1	3	1	2026-10-17 18:36:10.564915+08	2026-10-17 18:36:18.047338+08	2026-10-17 18:36:18.048153+08	2026-10-17 18:36:18.132853+08
101	AI_CHECK	SUCCEEDED	\N	submission	71	{"trigger_type": "REVIEW", "submission_id": 71}	1	0	0	100	执行中	{"report_id": 19, "report_no": 1}	\N	1	3	1	2026-10-17 18:36:14.955546+08	2026-10-17 18:36:19.711893+08	2026-10-17 18:36:19.71263+08	2026-10-17 18:36:19.793708+08
104	AI_CHECK	SUCCEEDED	\N	submission	72	{"trigger_type": "REVIEW", "submission_id": 72}	1	0	0	100	执行中	{"report_id": 20, "report_no": 1}	\N	1	3	1	2026-10-17 18:36:15.154858+08	2026-10-17 18:36:19.811583+08	2026-10-17 18:36:19.81257+08	2026-10-17 18:36:19.871982+08
102	PARSE	SUCCEEDED	\N	material_version	83	{"version_id": 83}	1	0	0	100	执行中	{"version_id": 83}	\N	1	3	1	2026-10-17 18:36:15.035306+08	2026-10-17 18:36:19.754427+08	2026-10-17 18:36:19.755415+08	2026-10-17 18:36:19.808047+08
62	PARSE	SUCCEEDED	\N	material_version	51	{"version_id": 51}	1	0	0	100	执行中	{"version_id": 51}	\N	1	3	1	2026-10-17 18:36:10.884106+08	2026-10-17 18:36:18.19882+08	2026-10-17 18:36:18.199624+08	2026-10-17 18:36:18.280878+08
68	PARSE	SUCCEEDED	\N	material_version	56	{"version_id": 56}	1	0	0	100	执行中	{"version_id": 56}	\N	1	3	1	2026-10-17 18:36:11.713208+08	2026-10-17 18:36:18.427011+08	2026-10-17 18:36:18.427833+08	2026-10-17 18:36:18.508517+08
70	PARSE	SUCCEEDED	\N	material_version	58	{"version_id": 58}	1	0	0	100	执行中	{"version_id": 58}	\N	1	3	1	2026-10-17 18:36:12.006861+08	2026-10-17 18:36:18.518192+08	2026-10-17 18:36:18.518856+08	2026-10-17 18:36:18.598941+08
78	AI_CHECK	SUCCEEDED	\N	submission	54	{"trigger_type": "REVIEW", "submission_id": 54}	1	0	0	100	执行中	{"report_id": 15, "report_no": 1}	\N	1	3	1	2026-10-17 18:36:12.678789+08	2026-10-17 18:36:18.799568+08	2026-10-17 18:36:18.800225+08	2026-10-17 18:36:18.885435+08
88	PARSE	SUCCEEDED	\N	material_version	72	{"version_id": 72}	1	0	0	100	执行中	{"version_id": 72}	\N	1	3	1	2026-10-17 18:36:13.644399+08	2026-10-17 18:36:19.179039+08	2026-10-17 18:36:19.179707+08	2026-10-17 18:36:19.261324+08
94	PARSE	SUCCEEDED	\N	material_version	77	{"version_id": 77}	1	0	0	100	执行中	{"version_id": 77}	\N	1	3	1	2026-10-17 18:36:14.408444+08	2026-10-17 18:36:19.417088+08	2026-10-17 18:36:19.417773+08	2026-10-17 18:36:19.500449+08
98	PARSE	SUCCEEDED	\N	material_version	80	{"version_id": 80}	1	0	0	100	执行中	{"version_id": 80}	\N	1	3	1	2026-10-17 18:36:14.74282+08	2026-10-17 18:36:19.5943+08	2026-10-17 18:36:19.595266+08	2026-10-17 18:36:19.650415+08
100	PARSE	SUCCEEDED	\N	material_version	82	{"version_id": 82}	1	0	0	100	执行中	{"version_id": 82}	\N	1	3	1	2026-10-17 18:36:14.948902+08	2026-10-17 18:36:19.654206+08	2026-10-17 18:36:19.65509+08	2026-10-17 18:36:19.750868+08
63	AI_CHECK	SUCCEEDED	\N	submission	42	{"trigger_type": "REVIEW", "submission_id": 42}	1	0	0	100	执行中	{"report_id": 12, "report_no": 1}	\N	1	3	1	2026-10-17 18:36:10.892974+08	2026-10-17 18:36:18.24358+08	2026-10-17 18:36:18.244432+08	2026-10-17 18:36:18.326795+08
73	PARSE	SUCCEEDED	\N	material_version	60	{"version_id": 60}	1	0	0	100	执行中	{"version_id": 60}	\N	1	3	1	2026-10-17 18:36:12.267454+08	2026-10-17 18:36:18.650671+08	2026-10-17 18:36:18.651426+08	2026-10-17 18:36:18.696569+08
75	AI_CHECK	SUCCEEDED	\N	submission	53	{"trigger_type": "REVIEW", "submission_id": 53}	1	0	0	100	执行中	{"report_id": 14, "report_no": 1}	\N	1	3	1	2026-10-17 18:36:12.427063+08	2026-10-17 18:36:18.700052+08	2026-10-17 18:36:18.700713+08	2026-10-17 18:36:18.786346+08
83	PARSE	SUCCEEDED	\N	material_version	68	{"version_id": 68}	1	0	0	100	执行中	{"version_id": 68}	\N	1	3	1	2026-10-17 18:36:13.209878+08	2026-10-17 18:36:18.985798+08	2026-10-17 18:36:18.986505+08	2026-10-17 18:36:19.067955+08
85	AI_CHECK	SUCCEEDED	\N	submission	57	{"trigger_type": "REVIEW", "submission_id": 57}	1	0	0	100	执行中	{"report_id": 16, "report_no": 1}	\N	1	3	1	2026-10-17 18:36:13.316889+08	2026-10-17 18:36:19.07187+08	2026-10-17 18:36:19.072567+08	2026-10-17 18:36:19.16847+08
91	PARSE	SUCCEEDED	\N	material_version	74	{"version_id": 74}	1	0	0	100	执行中	{"version_id": 74}	\N	1	3	1	2026-10-17 18:36:13.937822+08	2026-10-17 18:36:19.316524+08	2026-10-17 18:36:19.317521+08	2026-10-17 18:36:19.369213+08
97	AI_CHECK	SUCCEEDED	\N	submission	66	{"trigger_type": "REVIEW", "submission_id": 66}	1	0	0	100	执行中	{"report_id": 18, "report_no": 1}	\N	1	3	1	2026-10-17 18:36:14.66031+08	2026-10-17 18:36:19.549091+08	2026-10-17 18:36:19.549921+08	2026-10-17 18:36:19.641758+08
99	PARSE	SUCCEEDED	\N	material_version	81	{"version_id": 81}	1	0	0	100	执行中	{"version_id": 81}	\N	1	3	1	2026-10-17 18:36:14.846811+08	2026-10-17 18:36:19.646361+08	2026-10-17 18:36:19.647179+08	2026-10-17 18:36:19.707846+08
103	PARSE	SUCCEEDED	\N	material_version	84	{"version_id": 84}	1	0	0	100	执行中	{"version_id": 84}	\N	1	3	1	2026-10-17 18:36:15.148417+08	2026-10-17 18:36:19.800851+08	2026-10-17 18:36:19.802587+08	2026-10-17 18:36:19.849719+08
\.


--
-- Data for Name: material_types; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.material_types (id, code, name, stage_codes, title_keywords, exclude_keywords, element_template, format_requirements, date_node_map, description, is_active, sort_order, updated_by, created_at, updated_at) FROM stdin;
1	APPLICATION_LETTER	入党申请书	[1]	["入党申请书"]	[]	[{"key": "motive", "name": "入党动机", "keywords": ["入党动机", "为什么要入党"], "required": true}, {"key": "theory", "name": "理论认识", "keywords": ["党的性质", "指导思想", "宗旨"], "required": true}]	{"seal_slots": [], "doc_elements": ["title", "salutation", "body", "closing", "signature", "date"], "required_fields": ["姓名"], "signature_slots": [{"slot": "本人签名", "keywords": ["签名", "申请人"]}], "handwriting_required": false}	{"signature_date": "T02", "field:出生日期": "T01"}	\N	t	1	\N	2026-10-17 18:29:29.414319+08	2026-10-17 18:29:29.41432+08
2	PARTY_TALK_RECORD	党组织派人谈话记录	[1]	["谈话记录", "派人谈话"]	[]	[]	{"seal_slots": [{"slot": "党组织印章", "keywords": ["盖章", "党支部"]}], "doc_elements": ["title", "body", "signature", "date"], "required_fields": [], "signature_slots": [{"slot": "谈话人签名", "keywords": ["谈话人", "签名"]}]}	{"signature_date": "T03"}	\N	t	2	\N	2026-10-17 18:29:29.41438+08	2026-10-17 18:29:29.41438+08
3	RECOMMENDATION	推荐/推优材料	[2]	["推荐", "推优", "团组织推优"]	[]	[]	{"seal_slots": [{"slot": "团组织印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "signature", "date"], "signature_slots": [{"slot": "推荐组织签名", "keywords": ["签名"]}]}	{}	\N	t	3	\N	2026-10-17 18:29:29.4144+08	2026-10-17 18:29:29.4144+08
4	ACTIVIST_MEETING_RECORD	支委会研究确定积极分子记录	[2]	["确定入党积极分子", "支委会"]	[]	[]	{"seal_slots": [{"slot": "党支部印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "signature", "date"], "signature_slots": [{"slot": "书记签名", "keywords": ["书记", "签名"]}]}	{"signature_date": "T04"}	\N	t	4	\N	2026-10-17 18:29:29.414418+08	2026-10-17 18:29:29.414418+08
5	ACTIVIST_FILING	积极分子备案材料	[2]	["积极分子", "备案"]	[]	[]	{"seal_slots": [{"slot": "党委印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "date"]}	{"signature_date": "T04"}	\N	t	5	\N	2026-10-17 18:29:29.414434+08	2026-10-17 18:29:29.414434+08
6	RECORD_BOOK_ACTIVIST	写实簿·积极分子培养考察部分	[2]	["培养教育考察写实簿", "积极分子"]	[]	[]	{"doc_elements": ["title", "body", "signature"], "handwriting_required": true}	{"field:确定积极分子": "T04"}	\N	t	6	\N	2026-10-17 18:29:29.414448+08	2026-10-17 18:29:29.414448+08
7	THOUGHT_REPORT	思想汇报	[2, 3, 5]	["思想汇报"]	[]	[{"key": "motive", "name": "入党动机", "keywords": ["入党动机", "为什么要入党"], "required": true}, {"key": "theory", "name": "理论认识", "keywords": ["党的性质", "指导思想", "宗旨"], "required": true}]	{"doc_elements": ["title", "salutation", "body", "closing", "signature", "date"], "signature_slots": [{"slot": "本人签名", "keywords": ["汇报人", "签名"]}]}	{"signature_date": "T06"}	\N	t	7	\N	2026-10-17 18:29:29.414462+08	2026-10-17 18:29:29.414462+08
8	ACTIVIST_TRAINING_CERT	积极分子培训结业证明	[2]	["积极分子培训", "结业"]	[]	[]	{"seal_slots": [{"slot": "培训单位印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body"]}	{}	\N	t	8	\N	2026-10-17 18:29:29.414479+08	2026-10-17 18:29:29.41448+08
9	AUTOBIOGRAPHY	自传	[3]	["自传"]	[]	[{"key": "family", "name": "家庭主要成员", "keywords": ["家庭主要成员", "家庭成员"], "required": true}, {"key": "growth", "name": "成长经历", "keywords": ["成长", "学习经历"], "required": true}, {"key": "thought", "name": "思想演变", "keywords": ["思想", "认识"], "required": true}]	{"min_chars": 3000, "doc_elements": ["title", "body", "signature", "date"], "required_fields": ["姓名", "出生日期", "家庭主要成员"]}	{"field:出生日期": "T01"}	\N	t	9	\N	2026-10-17 18:29:29.414494+08	2026-10-17 18:29:29.414494+08
10	CANDIDATE_MEETING_RECORD	支委会确定发展对象记录	[3]	["确定为发展对象"]	[]	[]	{"seal_slots": [{"slot": "党支部印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "signature", "date"]}	{"signature_date": "T08"}	\N	t	10	\N	2026-10-17 18:29:29.414508+08	2026-10-17 18:29:29.414508+08
11	POLITICAL_REVIEW	政治审查材料	[3]	["政治审查", "政审", "函调"]	[]	[]	{"seal_slots": [{"slot": "审查单位印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "signature", "date"]}	{"signature_date": "T09"}	\N	t	11	\N	2026-10-17 18:29:29.414523+08	2026-10-17 18:29:29.414523+08
12	TRAINING_CERT	集中培训结业证书	[3]	["集中培训", "结业证书"]	[]	[]	{"seal_slots": [{"slot": "党校印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body"]}	{"field:学时": "T10", "field:培训起": "T10"}	\N	t	12	\N	2026-10-17 18:29:29.414538+08	2026-10-17 18:29:29.414538+08
13	RECORD_BOOK_CANDIDATE	写实簿·发展对象考察部分	[3]	["写实簿", "发展对象"]	[]	[]	{"doc_elements": ["title", "body"], "handwriting_required": true}	{}	\N	t	13	\N	2026-10-17 18:29:29.414553+08	2026-10-17 18:29:29.414553+08
14	CANDIDATE_PUBLICITY	发展对象公示材料	[4]	["公示", "发展对象"]	[]	[]	{"seal_slots": [{"slot": "党支部印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "date"]}	{"field:公示起": "T11"}	\N	t	14	\N	2026-10-17 18:29:29.414567+08	2026-10-17 18:29:29.414567+08
15	PRE_REVIEW_OPINION	上级党委预审意见	[4]	["预审"]	[]	[]	{"seal_slots": [{"slot": "党委印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "signature", "date"]}	{"signature_date": "T12"}	\N	t	15	\N	2026-10-17 18:29:29.414581+08	2026-10-17 18:29:29.414581+08
16	APPLICATION_FORM	入党志愿书	[4]	["入党志愿书"]	[]	[]	{"seal_slots": [{"slot": "党组织印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "signature", "date"], "signature_slots": [{"slot": "本人签名", "keywords": ["志愿人", "签名"]}]}	{"signature_date": "T13", "field:出生日期": "T01"}	\N	t	16	\N	2026-10-17 18:29:29.414595+08	2026-10-17 18:29:29.414595+08
17	ADMISSION_MEETING_RECORD	支部大会讨论接收记录	[4]	["支部大会", "接收预备党员"]	[]	[]	{"seal_slots": [{"slot": "党支部印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "signature", "date"]}	{"signature_date": "T14"}	\N	t	17	\N	2026-10-17 18:29:29.414608+08	2026-10-17 18:29:29.414609+08
18	COMMITTEE_TALK_RECORD	上级党委派人谈话记录	[4]	["上级党委", "谈话"]	[]	[]	{"doc_elements": ["title", "body", "signature", "date"]}	{"signature_date": "T15"}	\N	t	18	\N	2026-10-17 18:29:29.414622+08	2026-10-17 18:29:29.414622+08
19	ADMISSION_APPROVAL	上级党委审批意见	[4]	["审批", "接收为预备党员"]	[]	[]	{"seal_slots": [{"slot": "党委印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "signature", "date"]}	{"signature_date": "T16"}	\N	t	19	\N	2026-10-17 18:29:29.414637+08	2026-10-17 18:29:29.414637+08
20	REGULARIZATION_LETTER	转正申请书	[5]	["转正申请"]	[]	[{"key": "motive", "name": "入党动机", "keywords": ["入党动机", "为什么要入党"], "required": true}, {"key": "theory", "name": "理论认识", "keywords": ["党的性质", "指导思想", "宗旨"], "required": true}]	{"doc_elements": ["title", "salutation", "body", "closing", "signature", "date"]}	{"signature_date": "T18"}	\N	t	20	\N	2026-10-17 18:29:29.414652+08	2026-10-17 18:29:29.414653+08
21	RECORD_BOOK_PROBATIONARY	写实簿·预备党员考察部分	[5]	["写实簿", "预备党员"]	[]	[]	{"doc_elements": ["title", "body"], "handwriting_required": true}	{}	\N	t	21	\N	2026-10-17 18:29:29.414667+08	2026-10-17 18:29:29.414667+08
22	REGULARIZATION_PUBLICITY	转正公示材料	[5]	["转正", "公示"]	[]	[]	{"seal_slots": [{"slot": "党支部印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "date"]}	{"field:公示起": "T19"}	\N	t	22	\N	2026-10-17 18:29:29.41468+08	2026-10-17 18:29:29.414681+08
23	REGULARIZATION_MEETING_RECORD	支部大会讨论转正记录	[5]	["支部大会", "转正"]	[]	[]	{"doc_elements": ["title", "body", "signature", "date"]}	{"signature_date": "T20"}	\N	t	23	\N	2026-10-17 18:29:29.414694+08	2026-10-17 18:29:29.414694+08
24	REGULARIZATION_APPROVAL	上级党委审批转正意见	[5]	["审批", "转为正式党员"]	[]	[]	{"seal_slots": [{"slot": "党委印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "signature", "date"]}	{"signature_date": "T21"}	\N	t	24	\N	2026-10-17 18:29:29.414708+08	2026-10-17 18:29:29.414708+08
\.


--
-- Data for Name: material_versions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.material_versions (id, material_id, version_no, original_filename, stored_path, file_ext, mime_type, file_size, sha256, page_count, change_note, parse_status, parse_error, parsed_at, is_frozen, uploaded_by, uploaded_at) FROM stdin;
11	11	1	入党志愿书.pdf	materials/4/0048c3b8b3134e6e805adcccd82e3a53.pdf	pdf	application/pdf	3641319	2450dab664e971f23e6a5c19ab7fe5986681983dc2fa679fd03c753be5d6db0f	1	\N	DONE	\N	2026-10-17 18:36:16.42762+08	f	1	2026-10-17 18:36:06.906071+08
3	3	1	思想汇报.pdf	materials/1/0d92adfe4c124af7aae27c2571babfce.pdf	pdf	application/pdf	3640931	409f4622b6859d710225a3c30e6ec81f2fee27846680fa27647d2ad8e106c489	1	\N	DONE	\N	2026-10-17 18:36:16.01155+08	f	1	2026-10-17 18:36:06.122571+08
5	5	1	支委会确定发展对象记录.pdf	materials/1/d848156376ee427fa89eab80f8e1abe1.pdf	pdf	application/pdf	3641255	e05686145cb6b938e462f2503532386af54b3630809efb6a1377e85b20def964	1	\N	DONE	\N	2026-10-17 18:36:16.102868+08	f	1	2026-10-17 18:36:06.38227+08
6	6	1	自传.pdf	materials/1/212346cc243d484aa98cb6619785edff.pdf	pdf	application/pdf	3641065	46346ac9ad3f8c1f3028faba340d495197f18bd3b6a55d490945101df63fb1d9	1	\N	DONE	\N	2026-10-17 18:36:16.150369+08	f	1	2026-10-17 18:36:06.457566+08
7	7	1	入党申请书.pdf	materials/2/2b2951e975eb44c78e6552a41361b813.pdf	pdf	application/pdf	3641209	36510147e48580c9805bd9584105b04bef755ded014e3101b11e3ddc7f22a8d9	1	\N	DONE	\N	2026-10-17 18:36:16.212841+08	f	1	2026-10-17 18:36:06.556598+08
9	9	1	思想汇报.pdf	materials/2/120b8cb7a07346d39e766f5f53625ca1.pdf	pdf	application/pdf	3640930	a0d771cc0acd729e33ac5075cdf9038201d217910223fa9f665151c231ea1fb2	1	\N	DONE	\N	2026-10-17 18:36:16.319278+08	f	1	2026-10-17 18:36:06.701667+08
10	10	1	入党申请书.pdf	materials/3/634209f1cd9346ff9792f1783c7f62c5.pdf	pdf	application/pdf	3641194	aa87d6a37a112f25cf50745b9635460a779ea173b4a39e411841a2a2f42a802e	1	\N	DONE	\N	2026-10-17 18:36:16.374711+08	f	1	2026-10-17 18:36:06.787233+08
12	12	1	支部大会讨论接收记录.pdf	materials/4/7fc09c3349b7406abba2d2fbe67f9edc.pdf	pdf	application/pdf	3641222	acd1a2e741d7cba39f99df3123a95fa3445aca9dbbbc70d195b194a1f1c51c4b	1	\N	DONE	\N	2026-10-17 18:36:16.471176+08	f	1	2026-10-17 18:36:07.008666+08
13	13	1	政治审查材料.pdf	materials/4/e61e6ab1874a42d886518c0f5c775027.pdf	pdf	application/pdf	3641223	0668f0fb3bf12cb36e6ef2df71843f6bc959640c8a255152bf7daebf8f16e4d0	1	\N	DONE	\N	2026-10-17 18:36:16.513407+08	f	1	2026-10-17 18:36:07.12357+08
14	14	1	集中培训结业证书.pdf	materials/4/acedd1af240549899b0e3fe82c1c1cf4.pdf	pdf	application/pdf	3641296	ea63759edcb1303dca4c17f0f3afdea16985211a84ecd49a8c1000df6cff43cf	1	\N	DONE	\N	2026-10-17 18:36:16.553909+08	f	1	2026-10-17 18:36:07.240117+08
15	15	1	发展对象公示材料.pdf	materials/4/f96f3a7533f148b89f4e738f5984d69e.pdf	pdf	application/pdf	3641274	6232156627f7716c2d81fe6f1c66bcae0d0a2d2fdc1379438d4b15f916cb649c	1	\N	DONE	\N	2026-10-17 18:36:16.595338+08	f	1	2026-10-17 18:36:07.34509+08
16	16	1	上级党委预审意见.pdf	materials/4/22527387ee874083bfd40fc2716cf540.pdf	pdf	application/pdf	3641225	850d4f6ab880c2c7e5c012d7679d6a07b99297f3b02c40f464c9c8e07c4a0825	1	\N	DONE	\N	2026-10-17 18:36:16.635237+08	f	1	2026-10-17 18:36:07.445801+08
17	17	1	转正申请书.pdf	materials/5/0c5ba3674b0149f7806ce6c2b486e0ea.pdf	pdf	application/pdf	3640877	2cf91b3cd5946eab67885a6a7a93194a389c58cc743164093719e6419d4a5146	1	\N	DONE	\N	2026-10-17 18:36:16.685777+08	f	1	2026-10-17 18:36:07.528876+08
18	18	1	支部大会讨论转正记录.pdf	materials/5/eb939421540242e1940390be6ef20503.pdf	pdf	application/pdf	3641215	bd9c31490c5e4f66c1cde5858afc84006fd2b1cddeb0dca60cb3a1e97443dc18	1	\N	DONE	\N	2026-10-17 18:36:16.732079+08	f	1	2026-10-17 18:36:07.649955+08
19	19	1	转正公示材料.pdf	materials/5/1746aa17608443d79ed534ddcd7557e0.pdf	pdf	application/pdf	3641270	924326d64edde6184b3266efaaeb88cb434ed708903cbaf6b94eae6722d309c6	1	\N	DONE	\N	2026-10-17 18:36:16.774065+08	f	1	2026-10-17 18:36:07.749763+08
20	20	1	入党申请书.pdf	materials/6/2e49fdc9433d403f91f44011a19691f9.pdf	pdf	application/pdf	3641194	d1f3ccfe62c6ef17a6e1034dc12de6a6b1fcb78a62ffe940218adbb2bc8d0882	1	\N	DONE	\N	2026-10-17 18:36:16.829858+08	f	1	2026-10-17 18:36:07.852042+08
21	21	1	党组织派人谈话记录.pdf	materials/6/8a96b32d3ef94553a404e074785bf4e9.pdf	pdf	application/pdf	3641232	e23e0225e8462494adcbbd41076511b290b1ea11494345849c19ae675ee6164d	1	\N	DONE	\N	2026-10-17 18:36:16.871792+08	f	1	2026-10-17 18:36:07.954089+08
22	22	1	入党申请书.pdf	materials/7/95980ca969a6460ab8499f5d26574bf6.pdf	pdf	application/pdf	3641194	6d11ea1db8bde4d9026a9dabcea464e86b63e77d4f9c145d7763225b63e43040	1	\N	DONE	\N	2026-10-17 18:36:16.925369+08	f	1	2026-10-17 18:36:08.056916+08
23	23	1	思想汇报.pdf	materials/7/c6fb658f8d0b4f6da777c4b35817f0a7.pdf	pdf	application/pdf	3640931	1d86d02a649cffb945b62e18651bed7dc0bbb74f75b2798a9daed649d8ff9489	1	\N	DONE	\N	2026-10-17 18:36:16.966885+08	f	1	2026-10-17 18:36:08.135024+08
24	24	1	思想汇报.pdf	materials/7/5d7caa8950e9442b82b36d72c845b6e9.pdf	pdf	application/pdf	3640931	1705bfae67cc09d916cf0ddb64497e679164c75ff1813686717f45f511f1e19a	1	\N	DONE	\N	2026-10-17 18:36:17.008564+08	f	1	2026-10-17 18:36:08.212977+08
25	25	1	思想汇报.pdf	materials/7/728da1b36ae34f05b98049836b82d628.pdf	pdf	application/pdf	3640930	57cef5eeb5b6b3732e15847bec66768f114815529b054bf594d1f5c5d11324b4	1	\N	DONE	\N	2026-10-17 18:36:17.048631+08	f	1	2026-10-17 18:36:08.287124+08
26	26	1	支委会确定发展对象记录.pdf	materials/7/68395a349efb4054aab10559f30ffe94.pdf	pdf	application/pdf	3641255	07871d5a48566ab136606e1927e3a49040485e9cdb8dd7bf345d876a92f30e82	1	\N	DONE	\N	2026-10-17 18:36:17.089137+08	f	1	2026-10-17 18:36:08.393706+08
27	27	1	自传.pdf	materials/7/ccc55420b74346e0a733e235a2bbc87c.pdf	pdf	application/pdf	3641065	01cb3d85a40a6914ee984f8f24083ff1cea2ebf48ee3650970f946a87d423bb7	1	\N	DONE	\N	2026-10-17 18:36:17.130942+08	f	1	2026-10-17 18:36:08.4708+08
28	28	1	入党申请书.pdf	materials/8/6f98d682f24e4a75aef322c35dffe2cd.pdf	pdf	application/pdf	3641209	de8562c3b2f3d2aa0c2e1f580d9184198d1175928c5e9e84e5d460ba8151b3f1	1	\N	DONE	\N	2026-10-17 18:36:17.183213+08	f	1	2026-10-17 18:36:08.554853+08
29	29	1	自传.pdf	materials/8/b8cd588681904cf1b0cb7a8e9d34b4b1.pdf	pdf	application/pdf	3640858	09ab2847a8edf0689f0ff48701be47908b60a7987a8042ad0b87170df9e6d627	1	\N	DONE	\N	2026-10-17 18:36:17.231982+08	f	1	2026-10-17 18:36:08.627051+08
31	31	1	入党申请书.pdf	materials/9/bb28b994a56e45f8a9e093904fe1dc20.pdf	pdf	application/pdf	3641194	30cf6fab53600e1a7463b8106ced45e3768a4fa0cc40df1794bcc348ecc32aed	1	\N	DONE	\N	2026-10-17 18:36:17.352311+08	f	1	2026-10-17 18:36:08.79377+08
35	35	1	集中培训结业证书.pdf	materials/10/92baeb9266794689aa569038b33da789.pdf	pdf	application/pdf	3641296	b4f7154ce50afcc7046050f9c1cf2e97758d6930566499e43794dca0fde80a3b	1	\N	DONE	\N	2026-10-17 18:36:17.518802+08	f	1	2026-10-17 18:36:09.25904+08
36	36	1	发展对象公示材料.pdf	materials/10/f7504ed38cff4444815af0ece4446fcf.pdf	pdf	application/pdf	3641274	a5ab5873c2350089bbffd16764cd659e322b44a2dfcbcefd1ba2d50222b1fd4e	1	\N	DONE	\N	2026-10-17 18:36:17.559306+08	f	1	2026-10-17 18:36:09.360219+08
37	37	1	上级党委预审意见.pdf	materials/10/b788609d8ffc40e5a82466d2da277ec2.pdf	pdf	application/pdf	3641225	d8077fa821ec256f37ae0c11624fa64d22307cab752c5ef44f085afc4a8fbad2	1	\N	DONE	\N	2026-10-17 18:36:17.602436+08	f	1	2026-10-17 18:36:09.463319+08
38	38	1	转正申请书.pdf	materials/11/63b589a614754f57979b3573a412514c.pdf	pdf	application/pdf	3640877	d9342913a11215f3b09c495c3fc05662e965c43fee948ed3692d46c0b060ebed	1	\N	DONE	\N	2026-10-17 18:36:17.659579+08	f	1	2026-10-17 18:36:09.552213+08
39	39	1	支部大会讨论转正记录.pdf	materials/11/1d4491f30f0742c68f8e8325b820e344.pdf	pdf	application/pdf	3641215	c9aeca8defbffb77656d32a3555386b0ec09be94d21d95b5cfde3ed4e45425fb	1	\N	DONE	\N	2026-10-17 18:36:17.707505+08	f	1	2026-10-17 18:36:09.652379+08
40	40	1	转正公示材料.pdf	materials/11/f18e554521a94309a4b9456eead5e7e7.pdf	pdf	application/pdf	3641270	c87289653f23e61b2ab29f796d686a50dc8e64a531395d8f0c4ba2bcf35b00ca	1	\N	DONE	\N	2026-10-17 18:36:17.747444+08	f	1	2026-10-17 18:36:09.752562+08
41	41	1	入党申请书.pdf	materials/12/ad96906669af433e8932265d866b0b3e.pdf	pdf	application/pdf	3641194	c8632d2fae11a636048affc93bebbbbcf4bce0ed83353965db42ea553546a860	1	\N	DONE	\N	2026-10-17 18:36:17.804045+08	f	1	2026-10-17 18:36:09.839996+08
42	42	1	党组织派人谈话记录.pdf	materials/12/879a68725e6440c5adaee93a567fd714.pdf	pdf	application/pdf	3641232	c00d684c6e87c79d6f7800534ee4126727d7cb0623bb2448e0478e980806249e	1	\N	DONE	\N	2026-10-17 18:36:17.846617+08	f	1	2026-10-17 18:36:09.94561+08
43	43	1	入党申请书.pdf	materials/13/3b444d247e0d42f1b6bcc815df6f4287.pdf	pdf	application/pdf	3641194	1f11a89391e85260c698580e1c4bd9a36d8fc0227002ab597275f15c270ea7b0	1	\N	DONE	\N	2026-10-17 18:36:17.894473+08	f	1	2026-10-17 18:36:10.034498+08
45	45	1	思想汇报.pdf	materials/13/f09b1b68bde44a258127558c2278b7d6.pdf	pdf	application/pdf	3640931	3c59e05362d7b0d5a04800800b2f8885ba0c14742e544a65bdba27181fe3a1f2	1	\N	DONE	\N	2026-10-17 18:36:17.992308+08	f	1	2026-10-17 18:36:10.214918+08
46	46	1	思想汇报.pdf	materials/13/fb8e39d361da452484161e8eae46cb9d.pdf	pdf	application/pdf	3640930	c32e972334029c7c8211b9b76823207d3b7710848f1c74a4c389df6f4f3afefc	1	\N	DONE	\N	2026-10-17 18:36:18.038005+08	f	1	2026-10-17 18:36:10.320298+08
47	47	1	支委会确定发展对象记录.pdf	materials/13/2bc8bbe39a54403893e48a567821fc40.pdf	pdf	application/pdf	3641255	68c72fd5109f277c4c4bd15c10dcfdc08e4f8aa12537794f352888321c303c6a	1	\N	DONE	\N	2026-10-17 18:36:18.080431+08	f	1	2026-10-17 18:36:10.476564+08
48	48	1	自传.pdf	materials/13/4e9020ee7d0b412bb2744e635353a8c0.pdf	pdf	application/pdf	3641065	6c9fdf685764fb9a707a1f7dc8df085387b7e0f165dba698fe6f3a5c0d2669b7	1	\N	DONE	\N	2026-10-17 18:36:18.126108+08	f	1	2026-10-17 18:36:10.564276+08
49	49	1	入党申请书.pdf	materials/14/58bd8219b2734a1cad24de7929fbec5c.pdf	pdf	application/pdf	3641209	caacb896294a91515683b318f846e5a3def75ddd32fce27df0ee972db1cc6d04	1	\N	DONE	\N	2026-10-17 18:36:18.183165+08	f	1	2026-10-17 18:36:10.675188+08
50	50	1	自传.pdf	materials/14/d1cb6c02c545474ba3ef8185dddffa3e.pdf	pdf	application/pdf	3640858	d82b66cf50e08251a1885190ea2e1fa72e6c27b1e5411ab2f62415c474249438	1	\N	DONE	\N	2026-10-17 18:36:18.233049+08	f	1	2026-10-17 18:36:10.77308+08
51	51	1	思想汇报.pdf	materials/14/a8de1cd74b614422ba3b369885090f16.pdf	pdf	application/pdf	3640930	62759e18e0f82b83e3d42a4be316a5722c5bc07911de99449f847c0a11d411d3	1	\N	DONE	\N	2026-10-17 18:36:18.27518+08	f	1	2026-10-17 18:36:10.883326+08
52	52	1	入党申请书.pdf	materials/15/699e59e87b1040a08c0354a195c0baf3.pdf	pdf	application/pdf	3641194	ead9b030edabd5bbe29e664fb2a39d66911c378834dcf3842b8ffad56b5804eb	1	\N	DONE	\N	2026-10-17 18:36:18.329587+08	f	1	2026-10-17 18:36:11.005779+08
54	54	1	支部大会讨论接收记录.pdf	materials/16/a305e2df98664b97997b38c1c831d205.pdf	pdf	application/pdf	3641222	187e3a367775360152128219e50edc8103907eb07c635e4f2beb875827d9573d	1	\N	DONE	\N	2026-10-17 18:36:18.415721+08	f	1	2026-10-17 18:36:11.367881+08
55	55	1	政治审查材料.pdf	materials/16/fc182e9d95294bdbaf17b5da80b03041.pdf	pdf	application/pdf	3641223	d5853b55141400ac350b32e2fefdeb65d531162a5494bcac4bd6ba1d9a3dd866	1	\N	DONE	\N	2026-10-17 18:36:18.459171+08	f	1	2026-10-17 18:36:11.52386+08
56	56	1	集中培训结业证书.pdf	materials/16/aed8693f44934aeaa9d1f20c27a840fc.pdf	pdf	application/pdf	3641296	4007b4a3f209d53febd22d612814d033547d9db183d21b34b1f975870847bc96	1	\N	DONE	\N	2026-10-17 18:36:18.502595+08	f	1	2026-10-17 18:36:11.712354+08
57	57	1	发展对象公示材料.pdf	materials/16/02a2d2236cd64edd9b2f00565e70617f.pdf	pdf	application/pdf	3641274	df2f03fadab278b3041695cbc269cbd4bb6be21a999513c3b735c875f47f2e95	1	\N	DONE	\N	2026-10-17 18:36:18.549535+08	f	1	2026-10-17 18:36:11.858225+08
58	58	1	上级党委预审意见.pdf	materials/16/bfa4cda2c4a14580b4ea75a26b0783bf.pdf	pdf	application/pdf	3641225	0cdec63b8adf6fb1cf784459d7fb1c83d7089734710de52516536195408f8c3b	1	\N	DONE	\N	2026-10-17 18:36:18.592731+08	f	1	2026-10-17 18:36:12.006053+08
59	59	1	转正申请书.pdf	materials/17/c753de1145c2475dbb620f7d54fe8550.pdf	pdf	application/pdf	3640877	941bf32513758f993e0fc4f21732873e1d4b4f6cef7526f1b07bb7bdd934b1e8	1	\N	DONE	\N	2026-10-17 18:36:18.645992+08	f	1	2026-10-17 18:36:12.120937+08
60	60	1	支部大会讨论转正记录.pdf	materials/17/3fbecdc0d7f64d2f86f6578eaac409d7.pdf	pdf	application/pdf	3641215	a0a4f34fd61fd23e94d0b88daaa656b0f37bf2b2e0a7d70ba8b4e8dff50e6198	1	\N	DONE	\N	2026-10-17 18:36:18.689736+08	f	1	2026-10-17 18:36:12.266444+08
61	61	1	转正公示材料.pdf	materials/17/2ccb8111e616434c899f16d425c42af6.pdf	pdf	application/pdf	3641270	ecc953eb1a39d0db9e22bbde21e4f0cdadd137f6ca676aa84a7b729e538a7c82	1	\N	DONE	\N	2026-10-17 18:36:18.731903+08	f	1	2026-10-17 18:36:12.417661+08
62	62	1	入党申请书.pdf	materials/18/c460a5667b75489baf9d70c74e227c14.pdf	pdf	application/pdf	3641194	d83d314286965ebacf521a09a6bf98e378edbeadc6dd7b9941851c860d33c360	1	\N	DONE	\N	2026-10-17 18:36:18.789091+08	f	1	2026-10-17 18:36:12.524696+08
63	63	1	党组织派人谈话记录.pdf	materials/18/e3db237c1154444b935798e9a4ea727d.pdf	pdf	application/pdf	3641232	e228db1653c5ac243bd58af73b99412bad807658279df0674cc33cef136dcf98	1	\N	DONE	\N	2026-10-17 18:36:18.831388+08	f	1	2026-10-17 18:36:12.669961+08
1	1	1	入党申请书.pdf	materials/1/5d2c2a9ad9c64b7ebe8e347eeafc5955.pdf	pdf	application/pdf	3641194	5771b627d73d741123a2066e61f024c432535dae614e0b4b6d3b46fbbd5d9e9e	1	\N	DONE	\N	2026-10-17 18:36:15.895432+08	f	1	2026-10-17 18:36:05.963763+08
2	2	1	思想汇报.pdf	materials/1/aa3adeeb527e4175865c74f32bee2d83.pdf	pdf	application/pdf	3640931	d4c4c0eb7165f7790543cbf62dc2b7b43c2bf8d817c974337ca7daf10df5de4c	1	\N	DONE	\N	2026-10-17 18:36:15.954768+08	f	1	2026-10-17 18:36:06.044124+08
4	4	1	思想汇报.pdf	materials/1/26e902bc648e42fdbcf9c66532b3ca26.pdf	pdf	application/pdf	3640930	63e0df08817fcff07813971cf0b34b536b1fd1dae3a827dbc3e173051cd951c8	1	\N	DONE	\N	2026-10-17 18:36:16.053533+08	f	1	2026-10-17 18:36:06.279702+08
8	8	1	自传.pdf	materials/2/2eea6d60dbe94766964664baf835a981.pdf	pdf	application/pdf	3640858	bbb66ac0c1952b6201a516a7c63120fa8598f638604ee6a22b50f1be965443d2	1	\N	DONE	\N	2026-10-17 18:36:16.275788+08	f	1	2026-10-17 18:36:06.628592+08
30	30	1	思想汇报.pdf	materials/8/236f3bfed5f94c5693d233edcdb18dfc.pdf	pdf	application/pdf	3640930	c9e428b73aa704d74cd835a518c2e399b43855d399f6a495ac7e2e2acbadd9cd	1	\N	DONE	\N	2026-10-17 18:36:17.283517+08	f	1	2026-10-17 18:36:08.700322+08
32	32	1	入党志愿书.pdf	materials/10/65c7aba26f1c45019dcea04bfb4ee71c.pdf	pdf	application/pdf	3641319	607767e9f137136b80fa86656b8e140837ebdce54bddcb3836e258178b5bf112	1	\N	DONE	\N	2026-10-17 18:36:17.392246+08	f	1	2026-10-17 18:36:08.9139+08
33	33	1	支部大会讨论接收记录.pdf	materials/10/0f6e970c0f834e1881a6a965b507776e.pdf	pdf	application/pdf	3641222	2d9edf530b3a0a2b820dc5c89a9d96870a5b9014a82d3757b37f64410ffe100e	1	\N	DONE	\N	2026-10-17 18:36:17.433899+08	f	1	2026-10-17 18:36:09.047666+08
34	34	1	政治审查材料.pdf	materials/10/1971e5bb9e084d93b22a9fe508ba83e9.pdf	pdf	application/pdf	3641223	d847695863d0d5060e401d92b771d20a9f1e9acd2a15a077196462ecc18bb328	1	\N	DONE	\N	2026-10-17 18:36:17.47782+08	f	1	2026-10-17 18:36:09.159833+08
44	44	1	思想汇报.pdf	materials/13/2f3a0e8d5b1a49ccb68fa5111a3e9ce5.pdf	pdf	application/pdf	3640931	217c7f07a09f936e20a33ee0aa65dea9ddba8b347ed5c0bbc188e546e1b46cb8	1	\N	DONE	\N	2026-10-17 18:36:17.94686+08	f	1	2026-10-17 18:36:10.115194+08
65	65	1	思想汇报.pdf	materials/19/64a1f15b70f6482a8dbc361d879f08db.pdf	pdf	application/pdf	3640931	634ba48a5dc0acab5d4cd247a086a1f299067373c69e18b410305ee40af3eef8	1	\N	DONE	\N	2026-10-17 18:36:18.933795+08	f	1	2026-10-17 18:36:12.883139+08
66	66	1	思想汇报.pdf	materials/19/628837057a1a4956a1cb6160782c285e.pdf	pdf	application/pdf	3640931	bfa7dc79d381ffd799b7f5c310ff56ebf8eafb715d00058ed64bcf75abe10032	1	\N	DONE	\N	2026-10-17 18:36:18.975099+08	f	1	2026-10-17 18:36:12.971108+08
67	67	1	思想汇报.pdf	materials/19/57bb9e1e4890461ebec4c18a6fd51457.pdf	pdf	application/pdf	3640930	415bb38be84d29e5d52732bd13a311a50a3855d9b7501de3591950bf0ef2d6b5	1	\N	DONE	\N	2026-10-17 18:36:19.019228+08	f	1	2026-10-17 18:36:13.065693+08
69	69	1	自传.pdf	materials/19/d0244d767d554219a944dcc13b68e865.pdf	pdf	application/pdf	3641065	b3b22c8621d6a7df6237697b7a168c8d11338ac758f1d1ff7a986cf753cd525f	1	\N	DONE	\N	2026-10-17 18:36:19.105507+08	f	1	2026-10-17 18:36:13.307042+08
70	70	1	入党申请书.pdf	materials/20/a4d0f9bd45334fc9a2a2f50202304019.pdf	pdf	application/pdf	3641209	6cf4544ffe22556dc07506394073dbb8c10dec88be97092856c1893c8625aded	1	\N	DONE	\N	2026-10-17 18:36:19.164184+08	f	1	2026-10-17 18:36:13.419177+08
71	71	1	自传.pdf	materials/20/84ed58e5dff843d29eaa62a21c53fb2e.pdf	pdf	application/pdf	3640858	34486ad1cd332ed00e483012df1aa6adfdead923f0a8f9e2b166dd18bd3b7ad7	1	\N	DONE	\N	2026-10-17 18:36:19.211314+08	f	1	2026-10-17 18:36:13.534641+08
72	72	1	思想汇报.pdf	materials/20/c185a52a216240d8aa44adf5f80b649a.pdf	pdf	application/pdf	3640930	604117d631d43e30ee7b25d3bd84714bdde2ceeba329932b561d86ed849f5d9f	1	\N	DONE	\N	2026-10-17 18:36:19.254683+08	f	1	2026-10-17 18:36:13.643116+08
73	73	1	入党申请书.pdf	materials/21/90e0e307bf854b87b377bef2afe4d79c.pdf	pdf	application/pdf	3641194	fcfabe9b651914122b8b1fc81bf8f466feae8341f432aadd9b9ea6ac0adbe438	1	\N	DONE	\N	2026-10-17 18:36:19.314998+08	f	1	2026-10-17 18:36:13.765586+08
75	75	1	支部大会讨论接收记录.pdf	materials/22/fc63945d3f2940539915cc334215910a.pdf	pdf	application/pdf	3641222	f955d0ef1da307c74c77ca1459e232499340f67e5054883b821437d8e409168e	1	\N	DONE	\N	2026-10-17 18:36:19.405131+08	f	1	2026-10-17 18:36:14.082909+08
76	76	1	政治审查材料.pdf	materials/22/369c3727e59449ccb2f6ccbb429f2e18.pdf	pdf	application/pdf	3641223	c08b17699c0bb216a69f935f4d362902993d3440f599186f40aa64ded40ab0e3	1	\N	DONE	\N	2026-10-17 18:36:19.448863+08	f	1	2026-10-17 18:36:14.241941+08
77	77	1	集中培训结业证书.pdf	materials/22/2f98f718719d48a4ac56dcd7a41599cc.pdf	pdf	application/pdf	3641295	0b6d108550f2431e1e7b90a4ab964d7907c583d570e6103361ac1e9814eb81b7	1	\N	DONE	\N	2026-10-17 18:36:19.493882+08	f	1	2026-10-17 18:36:14.407402+08
78	78	1	发展对象公示材料.pdf	materials/22/e47f1c04745b419c867f8db3193d4aa3.pdf	pdf	application/pdf	3641274	e9f0fc3d7d8d3a51e3b77b82a5d4c28f54b3b64c117796b10311ed2c280568ff	1	\N	DONE	\N	2026-10-17 18:36:19.537974+08	f	1	2026-10-17 18:36:14.547014+08
79	79	1	上级党委预审意见.pdf	materials/22/259f40b20e02444db4adb38d6c5f8424.pdf	pdf	application/pdf	3641225	b81cf2b55e08efe58bb62d45a422e0a180744a6be8ce5ccca927fe0dfff0c106	1	\N	DONE	\N	2026-10-17 18:36:19.583283+08	f	1	2026-10-17 18:36:14.653145+08
80	80	1	转正申请书.pdf	materials/23/e2208f5e972b4ea198726f4842c32a02.pdf	pdf	application/pdf	3640877	1e4f506735c26fb04fcff05b79577d5824310b8004e75f60b9aa0e7c8cbf1d52	1	\N	DONE	\N	2026-10-17 18:36:19.639483+08	f	1	2026-10-17 18:36:14.741922+08
81	81	1	支部大会讨论转正记录.pdf	materials/23/18928f4ca46441e1a1cd2087c6c33188.pdf	pdf	application/pdf	3641215	6ad95051898feffbfa13c4fefac4d49a468dd84476c09780d2fc82cbe229f816	1	\N	DONE	\N	2026-10-17 18:36:19.687265+08	f	1	2026-10-17 18:36:14.845944+08
82	82	1	转正公示材料.pdf	materials/23/077de8e9b07e4c708accbae522f9d892.pdf	pdf	application/pdf	3641270	1fde604855bda3253bfa25cdf7989cdcd57a951787be54c9d9bdd34ee4cfb1eb	1	\N	DONE	\N	2026-10-17 18:36:19.742996+08	f	1	2026-10-17 18:36:14.947965+08
83	83	1	入党申请书.pdf	materials/24/acbc63e4b465414f8d3794ae299d98c5.pdf	pdf	application/pdf	3641194	ba5df00db1dd76ca98000dac3ba41ea4f5a4419b41cb2a829b45b5100f4c4c62	1	\N	DONE	\N	2026-10-17 18:36:19.801191+08	f	1	2026-10-17 18:36:15.034348+08
84	84	1	党组织派人谈话记录.pdf	materials/24/4b927d9c793f4e528d97fafe0a7f001c.pdf	pdf	application/pdf	3641232	24d815390abfbadd778de0dea43193f39a0e7b5e57288ae0ec6b1ca685f7e539	1	\N	DONE	\N	2026-10-17 18:36:19.842771+08	f	1	2026-10-17 18:36:15.147411+08
53	53	1	入党志愿书.pdf	materials/16/d7879387a99a4e2e98b2693d16c95bd6.pdf	pdf	application/pdf	3641319	7702de14d3f8f7d12f84513ec3f2db07fec8510e0ca54b22b5853f4344dcf876	1	\N	DONE	\N	2026-10-17 18:36:18.369032+08	f	1	2026-10-17 18:36:11.183509+08
64	64	1	入党申请书.pdf	materials/19/2e4a786c61e841578163e4ca3014f934.pdf	pdf	application/pdf	3641194	f9ee8e4aa94bf3437cf9b1356cec126a3723ba42e4b33dd160715f31c543788a	1	\N	DONE	\N	2026-10-17 18:36:18.888289+08	f	1	2026-10-17 18:36:12.779231+08
68	68	1	支委会确定发展对象记录.pdf	materials/19/d69170641663457b9487a68f87d52244.pdf	pdf	application/pdf	3641255	81545c9155f5107bee3604d71af70aebe8e6931a23cd163ed2633fb6a2b3c6dd	1	\N	DONE	\N	2026-10-17 18:36:19.061508+08	f	1	2026-10-17 18:36:13.208913+08
74	74	1	入党志愿书.pdf	materials/22/af9660e438cb431dacfebac6812b0e2d.pdf	pdf	application/pdf	3641319	86c59544500bb03858ce6aad05492306fdd527059cd54ab7f7d7c2837bd38c13	1	\N	DONE	\N	2026-10-17 18:36:19.359601+08	f	1	2026-10-17 18:36:13.936754+08
\.


--
-- Data for Name: materials; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.materials (id, archive_id, submission_id, stage_code, title, declared_type_id, type_id, type_source, type_confidence, type_status, current_version_id, version_count, status, deleted_at, deleted_by, uploaded_by, created_at, updated_at) FROM stdin;
1	1	3	3	入党申请书	1	1	DECLARED	1	AUTO	1	1	ACTIVE	\N	\N	1	2026-10-17 18:36:05.946455+08	2026-10-17 18:35:58.467057+08
2	1	3	3	思想汇报	7	7	DECLARED	1	AUTO	2	1	ACTIVE	\N	\N	1	2026-10-17 18:36:06.031706+08	2026-10-17 18:35:58.467057+08
3	1	3	3	思想汇报	7	7	DECLARED	1	AUTO	3	1	ACTIVE	\N	\N	1	2026-10-17 18:36:06.109093+08	2026-10-17 18:35:58.467057+08
4	1	3	3	思想汇报	7	7	DECLARED	1	AUTO	4	1	ACTIVE	\N	\N	1	2026-10-17 18:36:06.267149+08	2026-10-17 18:35:58.467057+08
5	1	3	3	支委会确定发展对象记录	10	10	DECLARED	1	AUTO	5	1	ACTIVE	\N	\N	1	2026-10-17 18:36:06.368761+08	2026-10-17 18:35:58.467057+08
6	1	3	3	自传	9	9	DECLARED	1	AUTO	6	1	ACTIVE	\N	\N	1	2026-10-17 18:36:06.444139+08	2026-10-17 18:35:58.467057+08
7	2	6	3	入党申请书	1	1	DECLARED	1	AUTO	7	1	ACTIVE	\N	\N	1	2026-10-17 18:36:06.544623+08	2026-10-17 18:35:58.467057+08
8	2	6	3	自传	9	9	DECLARED	1	AUTO	8	1	ACTIVE	\N	\N	1	2026-10-17 18:36:06.616649+08	2026-10-17 18:35:58.467057+08
9	2	6	3	思想汇报	7	7	DECLARED	1	AUTO	9	1	ACTIVE	\N	\N	1	2026-10-17 18:36:06.688411+08	2026-10-17 18:35:58.467057+08
10	3	8	2	入党申请书	1	1	DECLARED	1	AUTO	10	1	ACTIVE	\N	\N	1	2026-10-17 18:36:06.773413+08	2026-10-17 18:35:58.467057+08
11	4	12	4	入党志愿书	16	16	DECLARED	1	AUTO	11	1	ACTIVE	\N	\N	1	2026-10-17 18:36:06.892649+08	2026-10-17 18:35:58.467057+08
12	4	12	4	支部大会讨论接收记录	17	17	DECLARED	1	AUTO	12	1	ACTIVE	\N	\N	1	2026-10-17 18:36:06.995081+08	2026-10-17 18:35:58.467057+08
13	4	12	4	政治审查材料	11	11	DECLARED	1	AUTO	13	1	ACTIVE	\N	\N	1	2026-10-17 18:36:07.109293+08	2026-10-17 18:35:58.467057+08
14	4	12	4	集中培训结业证书	12	12	DECLARED	1	AUTO	14	1	ACTIVE	\N	\N	1	2026-10-17 18:36:07.225734+08	2026-10-17 18:35:58.467057+08
15	4	12	4	发展对象公示材料	14	14	DECLARED	1	AUTO	15	1	ACTIVE	\N	\N	1	2026-10-17 18:36:07.331633+08	2026-10-17 18:35:58.467057+08
16	4	12	4	上级党委预审意见	15	15	DECLARED	1	AUTO	16	1	ACTIVE	\N	\N	1	2026-10-17 18:36:07.433216+08	2026-10-17 18:35:58.467057+08
17	5	17	5	转正申请书	20	20	DECLARED	1	AUTO	17	1	ACTIVE	\N	\N	1	2026-10-17 18:36:07.516772+08	2026-10-17 18:35:58.467057+08
18	5	17	5	支部大会讨论转正记录	23	23	DECLARED	1	AUTO	18	1	ACTIVE	\N	\N	1	2026-10-17 18:36:07.637038+08	2026-10-17 18:35:58.467057+08
19	5	17	5	转正公示材料	22	22	DECLARED	1	AUTO	19	1	ACTIVE	\N	\N	1	2026-10-17 18:36:07.7371+08	2026-10-17 18:35:58.467057+08
20	6	18	1	入党申请书	1	1	DECLARED	1	AUTO	20	1	ACTIVE	\N	\N	1	2026-10-17 18:36:07.838553+08	2026-10-17 18:35:58.467057+08
21	6	18	1	党组织派人谈话记录	2	2	DECLARED	1	AUTO	21	1	ACTIVE	\N	\N	1	2026-10-17 18:36:07.939688+08	2026-10-17 18:35:58.467057+08
22	7	21	3	入党申请书	1	1	DECLARED	1	AUTO	22	1	ACTIVE	\N	\N	1	2026-10-17 18:36:08.044452+08	2026-10-17 18:35:58.467057+08
23	7	21	3	思想汇报	7	7	DECLARED	1	AUTO	23	1	ACTIVE	\N	\N	1	2026-10-17 18:36:08.121674+08	2026-10-17 18:35:58.467057+08
24	7	21	3	思想汇报	7	7	DECLARED	1	AUTO	24	1	ACTIVE	\N	\N	1	2026-10-17 18:36:08.201044+08	2026-10-17 18:35:58.467057+08
25	7	21	3	思想汇报	7	7	DECLARED	1	AUTO	25	1	ACTIVE	\N	\N	1	2026-10-17 18:36:08.273786+08	2026-10-17 18:35:58.467057+08
26	7	21	3	支委会确定发展对象记录	10	10	DECLARED	1	AUTO	26	1	ACTIVE	\N	\N	1	2026-10-17 18:36:08.380956+08	2026-10-17 18:35:58.467057+08
27	7	21	3	自传	9	9	DECLARED	1	AUTO	27	1	ACTIVE	\N	\N	1	2026-10-17 18:36:08.458253+08	2026-10-17 18:35:58.467057+08
28	8	24	3	入党申请书	1	1	DECLARED	1	AUTO	28	1	ACTIVE	\N	\N	1	2026-10-17 18:36:08.54156+08	2026-10-17 18:35:58.467057+08
29	8	24	3	自传	9	9	DECLARED	1	AUTO	29	1	ACTIVE	\N	\N	1	2026-10-17 18:36:08.614877+08	2026-10-17 18:35:58.467057+08
30	8	24	3	思想汇报	7	7	DECLARED	1	AUTO	30	1	ACTIVE	\N	\N	1	2026-10-17 18:36:08.687021+08	2026-10-17 18:35:58.467057+08
31	9	26	2	入党申请书	1	1	DECLARED	1	AUTO	31	1	ACTIVE	\N	\N	1	2026-10-17 18:36:08.7796+08	2026-10-17 18:35:58.467057+08
32	10	30	4	入党志愿书	16	16	DECLARED	1	AUTO	32	1	ACTIVE	\N	\N	1	2026-10-17 18:36:08.900394+08	2026-10-17 18:35:58.467057+08
33	10	30	4	支部大会讨论接收记录	17	17	DECLARED	1	AUTO	33	1	ACTIVE	\N	\N	1	2026-10-17 18:36:09.033401+08	2026-10-17 18:35:58.467057+08
34	10	30	4	政治审查材料	11	11	DECLARED	1	AUTO	34	1	ACTIVE	\N	\N	1	2026-10-17 18:36:09.145612+08	2026-10-17 18:35:58.467057+08
35	10	30	4	集中培训结业证书	12	12	DECLARED	1	AUTO	35	1	ACTIVE	\N	\N	1	2026-10-17 18:36:09.247133+08	2026-10-17 18:35:58.467057+08
36	10	30	4	发展对象公示材料	14	14	DECLARED	1	AUTO	36	1	ACTIVE	\N	\N	1	2026-10-17 18:36:09.347598+08	2026-10-17 18:35:58.467057+08
37	10	30	4	上级党委预审意见	15	15	DECLARED	1	AUTO	37	1	ACTIVE	\N	\N	1	2026-10-17 18:36:09.44956+08	2026-10-17 18:35:58.467057+08
38	11	35	5	转正申请书	20	20	DECLARED	1	AUTO	38	1	ACTIVE	\N	\N	1	2026-10-17 18:36:09.538878+08	2026-10-17 18:35:58.467057+08
39	11	35	5	支部大会讨论转正记录	23	23	DECLARED	1	AUTO	39	1	ACTIVE	\N	\N	1	2026-10-17 18:36:09.639822+08	2026-10-17 18:35:58.467057+08
40	11	35	5	转正公示材料	22	22	DECLARED	1	AUTO	40	1	ACTIVE	\N	\N	1	2026-10-17 18:36:09.739315+08	2026-10-17 18:35:58.467057+08
41	12	36	1	入党申请书	1	1	DECLARED	1	AUTO	41	1	ACTIVE	\N	\N	1	2026-10-17 18:36:09.82796+08	2026-10-17 18:35:58.467057+08
42	12	36	1	党组织派人谈话记录	2	2	DECLARED	1	AUTO	42	1	ACTIVE	\N	\N	1	2026-10-17 18:36:09.93229+08	2026-10-17 18:35:58.467057+08
43	13	39	3	入党申请书	1	1	DECLARED	1	AUTO	43	1	ACTIVE	\N	\N	1	2026-10-17 18:36:10.022567+08	2026-10-17 18:35:58.467057+08
44	13	39	3	思想汇报	7	7	DECLARED	1	AUTO	44	1	ACTIVE	\N	\N	1	2026-10-17 18:36:10.102545+08	2026-10-17 18:35:58.467057+08
45	13	39	3	思想汇报	7	7	DECLARED	1	AUTO	45	1	ACTIVE	\N	\N	1	2026-10-17 18:36:10.202071+08	2026-10-17 18:35:58.467057+08
46	13	39	3	思想汇报	7	7	DECLARED	1	AUTO	46	1	ACTIVE	\N	\N	1	2026-10-17 18:36:10.306267+08	2026-10-17 18:35:58.467057+08
47	13	39	3	支委会确定发展对象记录	10	10	DECLARED	1	AUTO	47	1	ACTIVE	\N	\N	1	2026-10-17 18:36:10.463537+08	2026-10-17 18:35:58.467057+08
48	13	39	3	自传	9	9	DECLARED	1	AUTO	48	1	ACTIVE	\N	\N	1	2026-10-17 18:36:10.550877+08	2026-10-17 18:35:58.467057+08
49	14	42	3	入党申请书	1	1	DECLARED	1	AUTO	49	1	ACTIVE	\N	\N	1	2026-10-17 18:36:10.663962+08	2026-10-17 18:35:58.467057+08
50	14	42	3	自传	9	9	DECLARED	1	AUTO	50	1	ACTIVE	\N	\N	1	2026-10-17 18:36:10.759436+08	2026-10-17 18:35:58.467057+08
51	14	42	3	思想汇报	7	7	DECLARED	1	AUTO	51	1	ACTIVE	\N	\N	1	2026-10-17 18:36:10.867502+08	2026-10-17 18:35:58.467057+08
52	15	44	2	入党申请书	1	1	DECLARED	1	AUTO	52	1	ACTIVE	\N	\N	1	2026-10-17 18:36:10.99267+08	2026-10-17 18:35:58.467057+08
53	16	48	4	入党志愿书	16	16	DECLARED	1	AUTO	53	1	ACTIVE	\N	\N	1	2026-10-17 18:36:11.170328+08	2026-10-17 18:35:58.467057+08
54	16	48	4	支部大会讨论接收记录	17	17	DECLARED	1	AUTO	54	1	ACTIVE	\N	\N	1	2026-10-17 18:36:11.353995+08	2026-10-17 18:35:58.467057+08
55	16	48	4	政治审查材料	11	11	DECLARED	1	AUTO	55	1	ACTIVE	\N	\N	1	2026-10-17 18:36:11.509224+08	2026-10-17 18:35:58.467057+08
56	16	48	4	集中培训结业证书	12	12	DECLARED	1	AUTO	56	1	ACTIVE	\N	\N	1	2026-10-17 18:36:11.698376+08	2026-10-17 18:35:58.467057+08
57	16	48	4	发展对象公示材料	14	14	DECLARED	1	AUTO	57	1	ACTIVE	\N	\N	1	2026-10-17 18:36:11.844386+08	2026-10-17 18:35:58.467057+08
58	16	48	4	上级党委预审意见	15	15	DECLARED	1	AUTO	58	1	ACTIVE	\N	\N	1	2026-10-17 18:36:11.99266+08	2026-10-17 18:35:58.467057+08
59	17	53	5	转正申请书	20	20	DECLARED	1	AUTO	59	1	ACTIVE	\N	\N	1	2026-10-17 18:36:12.106993+08	2026-10-17 18:35:58.467057+08
60	17	53	5	支部大会讨论转正记录	23	23	DECLARED	1	AUTO	60	1	ACTIVE	\N	\N	1	2026-10-17 18:36:12.25406+08	2026-10-17 18:35:58.467057+08
61	17	53	5	转正公示材料	22	22	DECLARED	1	AUTO	61	1	ACTIVE	\N	\N	1	2026-10-17 18:36:12.404313+08	2026-10-17 18:35:58.467057+08
62	18	54	1	入党申请书	1	1	DECLARED	1	AUTO	62	1	ACTIVE	\N	\N	1	2026-10-17 18:36:12.512132+08	2026-10-17 18:35:58.467057+08
63	18	54	1	党组织派人谈话记录	2	2	DECLARED	1	AUTO	63	1	ACTIVE	\N	\N	1	2026-10-17 18:36:12.656064+08	2026-10-17 18:35:58.467057+08
64	19	57	3	入党申请书	1	1	DECLARED	1	AUTO	64	1	ACTIVE	\N	\N	1	2026-10-17 18:36:12.766821+08	2026-10-17 18:35:58.467057+08
65	19	57	3	思想汇报	7	7	DECLARED	1	AUTO	65	1	ACTIVE	\N	\N	1	2026-10-17 18:36:12.869079+08	2026-10-17 18:35:58.467057+08
66	19	57	3	思想汇报	7	7	DECLARED	1	AUTO	66	1	ACTIVE	\N	\N	1	2026-10-17 18:36:12.959015+08	2026-10-17 18:35:58.467057+08
67	19	57	3	思想汇报	7	7	DECLARED	1	AUTO	67	1	ACTIVE	\N	\N	1	2026-10-17 18:36:13.054252+08	2026-10-17 18:35:58.467057+08
68	19	57	3	支委会确定发展对象记录	10	10	DECLARED	1	AUTO	68	1	ACTIVE	\N	\N	1	2026-10-17 18:36:13.195815+08	2026-10-17 18:35:58.467057+08
69	19	57	3	自传	9	9	DECLARED	1	AUTO	69	1	ACTIVE	\N	\N	1	2026-10-17 18:36:13.293975+08	2026-10-17 18:35:58.467057+08
70	20	60	3	入党申请书	1	1	DECLARED	1	AUTO	70	1	ACTIVE	\N	\N	1	2026-10-17 18:36:13.405929+08	2026-10-17 18:35:58.467057+08
71	20	60	3	自传	9	9	DECLARED	1	AUTO	71	1	ACTIVE	\N	\N	1	2026-10-17 18:36:13.517265+08	2026-10-17 18:35:58.467057+08
72	20	60	3	思想汇报	7	7	DECLARED	1	AUTO	72	1	ACTIVE	\N	\N	1	2026-10-17 18:36:13.630865+08	2026-10-17 18:35:58.467057+08
73	21	62	2	入党申请书	1	1	DECLARED	1	AUTO	73	1	ACTIVE	\N	\N	1	2026-10-17 18:36:13.753208+08	2026-10-17 18:35:58.467057+08
74	22	66	4	入党志愿书	16	16	DECLARED	1	AUTO	74	1	ACTIVE	\N	\N	1	2026-10-17 18:36:13.921787+08	2026-10-17 18:35:58.467057+08
75	22	66	4	支部大会讨论接收记录	17	17	DECLARED	1	AUTO	75	1	ACTIVE	\N	\N	1	2026-10-17 18:36:14.068995+08	2026-10-17 18:35:58.467057+08
76	22	66	4	政治审查材料	11	11	DECLARED	1	AUTO	76	1	ACTIVE	\N	\N	1	2026-10-17 18:36:14.228384+08	2026-10-17 18:35:58.467057+08
77	22	66	4	集中培训结业证书	12	12	DECLARED	1	AUTO	77	1	ACTIVE	\N	\N	1	2026-10-17 18:36:14.392822+08	2026-10-17 18:35:58.467057+08
78	22	66	4	发展对象公示材料	14	14	DECLARED	1	AUTO	78	1	ACTIVE	\N	\N	1	2026-10-17 18:36:14.532678+08	2026-10-17 18:35:58.467057+08
79	22	66	4	上级党委预审意见	15	15	DECLARED	1	AUTO	79	1	ACTIVE	\N	\N	1	2026-10-17 18:36:14.639867+08	2026-10-17 18:35:58.467057+08
80	23	71	5	转正申请书	20	20	DECLARED	1	AUTO	80	1	ACTIVE	\N	\N	1	2026-10-17 18:36:14.729585+08	2026-10-17 18:35:58.467057+08
81	23	71	5	支部大会讨论转正记录	23	23	DECLARED	1	AUTO	81	1	ACTIVE	\N	\N	1	2026-10-17 18:36:14.832825+08	2026-10-17 18:35:58.467057+08
82	23	71	5	转正公示材料	22	22	DECLARED	1	AUTO	82	1	ACTIVE	\N	\N	1	2026-10-17 18:36:14.934652+08	2026-10-17 18:35:58.467057+08
83	24	72	1	入党申请书	1	1	DECLARED	1	AUTO	83	1	ACTIVE	\N	\N	1	2026-10-17 18:36:15.022101+08	2026-10-17 18:35:58.467057+08
84	24	72	1	党组织派人谈话记录	2	2	DECLARED	1	AUTO	84	1	ACTIVE	\N	\N	1	2026-10-17 18:36:15.133756+08	2026-10-17 18:35:58.467057+08
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.messages (id, user_id, msg_type, title, content, link_type, link_id, is_read, read_at, dedup_key, created_at) FROM stdin;
108	5	JOB_DONE	任务 AI 校验 #108 已完成		job	108	t	2026-10-17 20:19:23.479844+08	\N	2026-10-17 19:17:49.775009+08
67	1	JOB_DONE	任务 材料解析 #67 已完成		job	67	f	\N	\N	2026-10-17 18:36:18.466283+08
69	1	JOB_DONE	任务 材料解析 #69 已完成		job	69	f	\N	\N	2026-10-17 18:36:18.557472+08
71	1	JOB_DONE	任务 AI 校验 #71 已完成		job	71	f	\N	\N	2026-10-17 18:36:18.647189+08
73	1	JOB_DONE	任务 材料解析 #73 已完成		job	73	f	\N	\N	2026-10-17 18:36:18.697289+08
75	1	JOB_DONE	任务 AI 校验 #75 已完成		job	75	f	\N	\N	2026-10-17 18:36:18.786931+08
77	1	JOB_DONE	任务 材料解析 #77 已完成		job	77	f	\N	\N	2026-10-17 18:36:18.839776+08
79	1	JOB_DONE	任务 材料解析 #79 已完成		job	79	f	\N	\N	2026-10-17 18:36:18.8968+08
81	1	JOB_DONE	任务 材料解析 #81 已完成		job	81	f	\N	\N	2026-10-17 18:36:18.982421+08
83	1	JOB_DONE	任务 材料解析 #83 已完成		job	83	f	\N	\N	2026-10-17 18:36:19.068674+08
85	1	JOB_DONE	任务 AI 校验 #85 已完成		job	85	f	\N	\N	2026-10-17 18:36:19.169138+08
87	1	JOB_DONE	任务 材料解析 #87 已完成		job	87	f	\N	\N	2026-10-17 18:36:19.219492+08
89	1	JOB_DONE	任务 AI 校验 #89 已完成		job	89	f	\N	\N	2026-10-17 18:36:19.312519+08
91	1	JOB_DONE	任务 材料解析 #91 已完成		job	91	f	\N	\N	2026-10-17 18:36:19.370234+08
93	1	JOB_DONE	任务 材料解析 #93 已完成		job	93	f	\N	\N	2026-10-17 18:36:19.456753+08
95	1	JOB_DONE	任务 材料解析 #95 已完成		job	95	f	\N	\N	2026-10-17 18:36:19.546104+08
97	1	JOB_DONE	任务 AI 校验 #97 已完成		job	97	f	\N	\N	2026-10-17 18:36:19.642359+08
99	1	JOB_DONE	任务 材料解析 #99 已完成		job	99	f	\N	\N	2026-10-17 18:36:19.708854+08
101	1	JOB_DONE	任务 AI 校验 #101 已完成		job	101	f	\N	\N	2026-10-17 18:36:19.796416+08
103	1	JOB_DONE	任务 材料解析 #103 已完成		job	103	f	\N	\N	2026-10-17 18:36:19.850498+08
1	1	JOB_DONE	任务 材料解析 #1 已完成		job	1	f	\N	\N	2026-10-17 18:36:15.908374+08
2	1	JOB_DONE	任务 材料解析 #2 已完成		job	2	f	\N	\N	2026-10-17 18:36:15.976179+08
3	1	JOB_DONE	任务 材料解析 #3 已完成		job	3	f	\N	\N	2026-10-17 18:36:16.019655+08
4	1	JOB_DONE	任务 材料解析 #4 已完成		job	4	f	\N	\N	2026-10-17 18:36:16.066621+08
5	1	JOB_DONE	任务 材料解析 #5 已完成		job	5	f	\N	\N	2026-10-17 18:36:16.111243+08
6	1	JOB_DONE	任务 材料解析 #6 已完成		job	6	f	\N	\N	2026-10-17 18:36:16.160418+08
7	1	JOB_DONE	任务 材料解析 #8 已完成		job	8	f	\N	\N	2026-10-17 18:36:16.225385+08
8	1	JOB_DONE	任务 AI 校验 #7 已完成		job	7	f	\N	\N	2026-10-17 18:36:16.277081+08
9	1	JOB_DONE	任务 材料解析 #9 已完成		job	9	f	\N	\N	2026-10-17 18:36:16.285077+08
10	1	JOB_DONE	任务 材料解析 #10 已完成		job	10	f	\N	\N	2026-10-17 18:36:16.331661+08
11	1	JOB_DONE	任务 材料解析 #12 已完成		job	12	f	\N	\N	2026-10-17 18:36:16.384483+08
12	1	JOB_DONE	任务 AI 校验 #11 已完成		job	11	f	\N	\N	2026-10-17 18:36:16.41757+08
13	1	JOB_DONE	任务 材料解析 #13 已完成		job	13	f	\N	\N	2026-10-17 18:36:16.436085+08
14	1	JOB_DONE	任务 材料解析 #14 已完成		job	14	f	\N	\N	2026-10-17 18:36:16.479543+08
15	1	JOB_DONE	任务 材料解析 #15 已完成		job	15	f	\N	\N	2026-10-17 18:36:16.520244+08
16	1	JOB_DONE	任务 材料解析 #16 已完成		job	16	f	\N	\N	2026-10-17 18:36:16.561264+08
17	1	JOB_DONE	任务 材料解析 #17 已完成		job	17	f	\N	\N	2026-10-17 18:36:16.602836+08
18	1	JOB_DONE	任务 材料解析 #18 已完成		job	18	f	\N	\N	2026-10-17 18:36:16.642831+08
19	1	JOB_DONE	任务 AI 校验 #19 已完成		job	19	f	\N	\N	2026-10-17 18:36:16.693093+08
20	1	JOB_DONE	任务 材料解析 #20 已完成		job	20	f	\N	\N	2026-10-17 18:36:16.698461+08
21	1	JOB_DONE	任务 材料解析 #21 已完成		job	21	f	\N	\N	2026-10-17 18:36:16.739254+08
22	1	JOB_DONE	任务 材料解析 #22 已完成		job	22	f	\N	\N	2026-10-17 18:36:16.782504+08
23	1	JOB_DONE	任务 AI 校验 #23 已完成		job	23	f	\N	\N	2026-10-17 18:36:16.829558+08
24	1	JOB_DONE	任务 材料解析 #24 已完成		job	24	f	\N	\N	2026-10-17 18:36:16.837608+08
25	1	JOB_DONE	任务 材料解析 #25 已完成		job	25	f	\N	\N	2026-10-17 18:36:16.879164+08
26	1	JOB_DONE	任务 AI 校验 #26 已完成		job	26	f	\N	\N	2026-10-17 18:36:16.925079+08
27	1	JOB_DONE	任务 材料解析 #27 已完成		job	27	f	\N	\N	2026-10-17 18:36:16.933296+08
28	1	JOB_DONE	任务 材料解析 #28 已完成		job	28	f	\N	\N	2026-10-17 18:36:16.9743+08
29	1	JOB_DONE	任务 材料解析 #29 已完成		job	29	f	\N	\N	2026-10-17 18:36:17.014769+08
30	1	JOB_DONE	任务 材料解析 #30 已完成		job	30	f	\N	\N	2026-10-17 18:36:17.054989+08
31	1	JOB_DONE	任务 材料解析 #31 已完成		job	31	f	\N	\N	2026-10-17 18:36:17.096089+08
32	1	JOB_DONE	任务 材料解析 #32 已完成		job	32	f	\N	\N	2026-10-17 18:36:17.137842+08
33	1	JOB_DONE	任务 材料解析 #34 已完成		job	34	f	\N	\N	2026-10-17 18:36:17.195444+08
34	1	JOB_DONE	任务 AI 校验 #33 已完成		job	33	f	\N	\N	2026-10-17 18:36:17.195677+08
35	1	JOB_DONE	任务 材料解析 #35 已完成		job	35	f	\N	\N	2026-10-17 18:36:17.238722+08
36	1	JOB_DONE	任务 材料解析 #36 已完成		job	36	f	\N	\N	2026-10-17 18:36:17.303291+08
37	1	JOB_DONE	任务 AI 校验 #37 已完成		job	37	f	\N	\N	2026-10-17 18:36:17.353489+08
38	1	JOB_DONE	任务 材料解析 #38 已完成		job	38	f	\N	\N	2026-10-17 18:36:17.378226+08
39	1	JOB_DONE	任务 材料解析 #39 已完成		job	39	f	\N	\N	2026-10-17 18:36:17.399673+08
40	1	JOB_DONE	任务 材料解析 #40 已完成		job	40	f	\N	\N	2026-10-17 18:36:17.443499+08
41	1	JOB_DONE	任务 材料解析 #41 已完成		job	41	f	\N	\N	2026-10-17 18:36:17.484658+08
42	1	JOB_DONE	任务 材料解析 #42 已完成		job	42	f	\N	\N	2026-10-17 18:36:17.526812+08
43	1	JOB_DONE	任务 材料解析 #43 已完成		job	43	f	\N	\N	2026-10-17 18:36:17.567089+08
44	1	JOB_DONE	任务 材料解析 #44 已完成		job	44	f	\N	\N	2026-10-17 18:36:17.610676+08
45	1	JOB_DONE	任务 AI 校验 #45 已完成		job	45	f	\N	\N	2026-10-17 18:36:17.667392+08
46	1	JOB_DONE	任务 材料解析 #46 已完成		job	46	f	\N	\N	2026-10-17 18:36:17.674508+08
47	1	JOB_DONE	任务 材料解析 #47 已完成		job	47	f	\N	\N	2026-10-17 18:36:17.714695+08
48	1	JOB_DONE	任务 材料解析 #48 已完成		job	48	f	\N	\N	2026-10-17 18:36:17.755787+08
49	1	JOB_DONE	任务 AI 校验 #49 已完成		job	49	f	\N	\N	2026-10-17 18:36:17.801669+08
50	1	JOB_DONE	任务 材料解析 #50 已完成		job	50	f	\N	\N	2026-10-17 18:36:17.813007+08
51	1	JOB_DONE	任务 材料解析 #51 已完成		job	51	f	\N	\N	2026-10-17 18:36:17.854179+08
52	1	JOB_DONE	任务 材料解析 #53 已完成		job	53	f	\N	\N	2026-10-17 18:36:17.908269+08
53	1	JOB_DONE	任务 AI 校验 #52 已完成		job	52	f	\N	\N	2026-10-17 18:36:17.946037+08
54	1	JOB_DONE	任务 材料解析 #54 已完成		job	54	f	\N	\N	2026-10-17 18:36:17.955155+08
55	1	JOB_DONE	任务 材料解析 #55 已完成		job	55	f	\N	\N	2026-10-17 18:36:17.999364+08
56	1	JOB_DONE	任务 材料解析 #56 已完成		job	56	f	\N	\N	2026-10-17 18:36:18.044858+08
57	1	JOB_DONE	任务 材料解析 #57 已完成		job	57	f	\N	\N	2026-10-17 18:36:18.088575+08
58	1	JOB_DONE	任务 材料解析 #58 已完成		job	58	f	\N	\N	2026-10-17 18:36:18.133712+08
59	1	JOB_DONE	任务 AI 校验 #59 已完成		job	59	f	\N	\N	2026-10-17 18:36:18.19487+08
60	1	JOB_DONE	任务 材料解析 #60 已完成		job	60	f	\N	\N	2026-10-17 18:36:18.196664+08
61	1	JOB_DONE	任务 材料解析 #61 已完成		job	61	f	\N	\N	2026-10-17 18:36:18.240729+08
62	1	JOB_DONE	任务 材料解析 #62 已完成		job	62	f	\N	\N	2026-10-17 18:36:18.281908+08
63	1	JOB_DONE	任务 AI 校验 #63 已完成		job	63	f	\N	\N	2026-10-17 18:36:18.327325+08
64	1	JOB_DONE	任务 材料解析 #64 已完成		job	64	f	\N	\N	2026-10-17 18:36:18.351867+08
65	1	JOB_DONE	任务 材料解析 #65 已完成		job	65	f	\N	\N	2026-10-17 18:36:18.37741+08
66	1	JOB_DONE	任务 材料解析 #66 已完成		job	66	f	\N	\N	2026-10-17 18:36:18.424292+08
68	1	JOB_DONE	任务 材料解析 #68 已完成		job	68	f	\N	\N	2026-10-17 18:36:18.509285+08
70	1	JOB_DONE	任务 材料解析 #70 已完成		job	70	f	\N	\N	2026-10-17 18:36:18.59969+08
72	1	JOB_DONE	任务 材料解析 #72 已完成		job	72	f	\N	\N	2026-10-17 18:36:18.655641+08
74	1	JOB_DONE	任务 材料解析 #74 已完成		job	74	f	\N	\N	2026-10-17 18:36:18.740408+08
76	1	JOB_DONE	任务 材料解析 #76 已完成		job	76	f	\N	\N	2026-10-17 18:36:18.796796+08
78	1	JOB_DONE	任务 AI 校验 #78 已完成		job	78	f	\N	\N	2026-10-17 18:36:18.886045+08
80	1	JOB_DONE	任务 材料解析 #80 已完成		job	80	f	\N	\N	2026-10-17 18:36:18.940052+08
82	1	JOB_DONE	任务 材料解析 #82 已完成		job	82	f	\N	\N	2026-10-17 18:36:19.025903+08
84	1	JOB_DONE	任务 材料解析 #84 已完成		job	84	f	\N	\N	2026-10-17 18:36:19.113091+08
86	1	JOB_DONE	任务 材料解析 #86 已完成		job	86	f	\N	\N	2026-10-17 18:36:19.175966+08
88	1	JOB_DONE	任务 材料解析 #88 已完成		job	88	f	\N	\N	2026-10-17 18:36:19.262317+08
90	1	JOB_DONE	任务 材料解析 #90 已完成		job	90	f	\N	\N	2026-10-17 18:36:19.338567+08
92	1	JOB_DONE	任务 材料解析 #92 已完成		job	92	f	\N	\N	2026-10-17 18:36:19.413728+08
94	1	JOB_DONE	任务 材料解析 #94 已完成		job	94	f	\N	\N	2026-10-17 18:36:19.501228+08
96	1	JOB_DONE	任务 材料解析 #96 已完成		job	96	f	\N	\N	2026-10-17 18:36:19.591485+08
98	1	JOB_DONE	任务 材料解析 #98 已完成		job	98	f	\N	\N	2026-10-17 18:36:19.651223+08
100	1	JOB_DONE	任务 材料解析 #100 已完成		job	100	f	\N	\N	2026-10-17 18:36:19.751671+08
102	1	JOB_DONE	任务 材料解析 #102 已完成		job	102	f	\N	\N	2026-10-17 18:36:19.808851+08
104	1	JOB_DONE	任务 AI 校验 #104 已完成		job	104	f	\N	\N	2026-10-17 18:36:19.872423+08
105	5	JOB_DONE	任务 AI 校验 #105 已完成		job	105	t	2026-10-17 20:19:23.479844+08	\N	2026-10-17 18:53:08.614956+08
106	5	JOB_DONE	任务 AI 校验 #107 已完成		job	107	t	2026-10-17 20:19:23.479844+08	\N	2026-10-17 18:53:30.694633+08
107	5	JOB_DONE	任务 批量 AI 校验 #106 已完成		job	106	t	2026-10-17 20:19:23.479844+08	\N	2026-10-17 18:53:30.698624+08
\.


--
-- Data for Name: notices; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.notices (id, notice_type, submission_id, archive_id, student_user_id, report_id, round_no, title, content, deadline, status, sent_at, created_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: orgs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.orgs (id, parent_id, org_type, name, code, sort_order, is_active, is_demo, created_at, updated_at) FROM stdin;
1	\N	SCHOOL	武汉大学	WHU	0	t	f	2026-10-17 18:29:29.488426+08	2026-10-17 18:29:29.488427+08
2	1	COLLEGE	演示学院	DEMO_C1	1	t	t	2026-10-17 18:35:58.47389+08	2026-10-17 18:35:58.473892+08
3	2	BRANCH	演示学院第1党支部	DEMO_C1B1	1	t	t	2026-10-17 18:35:58.475527+08	2026-10-17 18:35:58.475529+08
4	2	BRANCH	演示学院第2党支部	DEMO_C1B2	2	t	t	2026-10-17 18:35:58.476159+08	2026-10-17 18:35:58.47616+08
5	2	BRANCH	演示学院第3党支部	DEMO_C1B3	3	t	t	2026-10-17 18:35:58.476852+08	2026-10-17 18:35:58.476853+08
6	1	COLLEGE	示例学院	DEMO_C2	2	t	t	2026-10-17 18:35:58.477648+08	2026-10-17 18:35:58.47765+08
7	6	BRANCH	示例学院第1党支部	DEMO_C2B1	1	t	t	2026-10-17 18:35:58.478382+08	2026-10-17 18:35:58.478383+08
8	6	BRANCH	示例学院第2党支部	DEMO_C2B2	2	t	t	2026-10-17 18:35:58.479063+08	2026-10-17 18:35:58.479064+08
9	6	BRANCH	示例学院第3党支部	DEMO_C2B3	3	t	t	2026-10-17 18:35:58.479509+08	2026-10-17 18:35:58.47951+08
\.


--
-- Data for Name: parse_results; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.parse_results (id, version_id, parser, ocr_engine, preview_pdf_path, full_text, char_count, pages, visual_marks, extracted_fields, format_features, warnings, corrected_text, corrected_fields, corrected_by, corrected_at, created_at, updated_at) FROM stdin;
1	1	PDF_TEXT	\N	previews/5d2c2a9ad9c64b7ebe8e347eeafc5955.pdf	入党申请书\n敬爱的党组织：\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\n范作用。\n此致\n敬礼！\n申请人：演示学生\n2023年3月15日\n·····	176	[{"text": "入党申请书\\n敬爱的党组织：\\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\\n范作用。\\n此致\\n敬礼！\\n申请人：演示学生\\n2023年3月15日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "入党申请书"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 124.18800354003906, 522.4375, 141.81600952148438], "conf": 1.0, "text": "我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代"}, {"bbox": [49.0, 144.58799743652344, 534.4375, 162.21600341796875], "conf": 1.0, "text": "表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心"}, {"bbox": [49.0, 166.89601135253906, 541.0, 182.5800018310547], "conf": 1.0, "text": "全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模"}, {"bbox": [49.0, 187.29600524902344, 97.0, 202.97999572753906], "conf": 1.0, "text": "范作用。"}, {"bbox": [49.0, 219.6959991455078, 73.0, 235.37998962402344], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 252.09597778320312, 85.0, 267.77996826171875], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 284.4960021972656, 145.0, 300.17999267578125], "conf": 1.0, "text": "申请人：演示学生"}, {"bbox": [49.0, 314.98797607421875, 132.291015625, 332.615966796875], "conf": 1.0, "text": "2023年3月15日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "申请人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"name": "演示学生", "title": "入党申请书", "closing": "敬礼！", "char_count": 166, "salutation": "敬爱的党组织：", "signature_date": "2023-03-15", "signature_name": "演示学生", "signature_date_raw": "2023年3月15日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:15.895359+08	2026-10-17 18:36:15.89536+08
2	2	PDF_TEXT	\N	previews/aa3adeeb527e4175865c74f32bee2d83.pdf	思想汇报\n敬爱的党组织：\n本季度我认真学习党章，对照党员标准查找不足。\n此致\n敬礼！\n汇报人：演示学生\n2024年12月20日\n·····	69	[{"text": "思想汇报\\n敬爱的党组织：\\n本季度我认真学习党章，对照党员标准查找不足。\\n此致\\n敬礼！\\n汇报人：演示学生\\n2024年12月20日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 97.0, 76.9800033569336], "conf": 1.0, "text": "思想汇报"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 126.09600830078125, 313.0, 141.77999877929688], "conf": 1.0, "text": "本季度我认真学习党章，对照党员标准查找不足。"}, {"bbox": [49.0, 158.49600219726562, 73.0, 174.17999267578125], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 190.89601135253906, 85.0, 206.5800018310547], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 223.29600524902344, 145.0, 238.97999572753906], "conf": 1.0, "text": "汇报人：演示学生"}, {"bbox": [49.0, 253.7880096435547, 139.046875, 271.416015625], "conf": 1.0, "text": "2024年12月20日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "汇报人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"title": "思想汇报", "closing": "敬礼！", "char_count": 62, "salutation": "敬爱的党组织：", "signature_date": "2024-12-20", "signature_name": "演示学生", "signature_date_raw": "2024年12月20日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:15.954683+08	2026-10-17 18:36:15.954685+08
3	3	PDF_TEXT	\N	previews/0d92adfe4c124af7aae27c2571babfce.pdf	思想汇报\n敬爱的党组织：\n本季度我认真学习党章，对照党员标准查找不足。\n此致\n敬礼！\n汇报人：演示学生\n2025年3月25日\n·····	68	[{"text": "思想汇报\\n敬爱的党组织：\\n本季度我认真学习党章，对照党员标准查找不足。\\n此致\\n敬礼！\\n汇报人：演示学生\\n2025年3月25日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 97.0, 76.9800033569336], "conf": 1.0, "text": "思想汇报"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 126.09600830078125, 313.0, 141.77999877929688], "conf": 1.0, "text": "本季度我认真学习党章，对照党员标准查找不足。"}, {"bbox": [49.0, 158.49600219726562, 73.0, 174.17999267578125], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 190.89601135253906, 85.0, 206.5800018310547], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 223.29600524902344, 145.0, 238.97999572753906], "conf": 1.0, "text": "汇报人：演示学生"}, {"bbox": [49.0, 253.7880096435547, 132.291015625, 271.416015625], "conf": 1.0, "text": "2025年3月25日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "汇报人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"title": "思想汇报", "closing": "敬礼！", "char_count": 61, "salutation": "敬爱的党组织：", "signature_date": "2025-03-25", "signature_name": "演示学生", "signature_date_raw": "2025年3月25日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:16.011493+08	2026-10-17 18:36:16.011494+08
4	4	PDF_TEXT	\N	previews/26e902bc648e42fdbcf9c66532b3ca26.pdf	思想汇报\n敬爱的党组织：\n本季度我认真学习党章，对照党员标准查找不足。\n此致\n敬礼！\n汇报人：演示学生\n2025年7月1日\n·····	67	[{"text": "思想汇报\\n敬爱的党组织：\\n本季度我认真学习党章，对照党员标准查找不足。\\n此致\\n敬礼！\\n汇报人：演示学生\\n2025年7月1日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 97.0, 76.9800033569336], "conf": 1.0, "text": "思想汇报"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 126.09600830078125, 313.0, 141.77999877929688], "conf": 1.0, "text": "本季度我认真学习党章，对照党员标准查找不足。"}, {"bbox": [49.0, 158.49600219726562, 73.0, 174.17999267578125], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 190.89601135253906, 85.0, 206.5800018310547], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 223.29600524902344, 145.0, 238.97999572753906], "conf": 1.0, "text": "汇报人：演示学生"}, {"bbox": [49.0, 253.7880096435547, 125.53515625, 271.416015625], "conf": 1.0, "text": "2025年7月1日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "汇报人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"title": "思想汇报", "closing": "敬礼！", "char_count": 60, "salutation": "敬爱的党组织：", "signature_date": "2025-07-01", "signature_name": "演示学生", "signature_date_raw": "2025年7月1日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:16.053479+08	2026-10-17 18:36:16.05348+08
5	5	PDF_TEXT	\N	previews/d848156376ee427fa89eab80f8e1abe1.pdf	支委会确定发展对象记录\n经讨论，确定该同志为发展对象。\n2025年8月30日\n???\n??\n·····	51	[{"text": "支委会确定发展对象记录\\n经讨论，确定该同志为发展对象。\\n2025年8月30日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 181.0, 76.9800033569336], "conf": 1.0, "text": "支委会确定发展对象记录"}, {"bbox": [49.0, 93.69600677490234, 229.0, 109.3800048828125], "conf": 1.0, "text": "经讨论，确定该同志为发展对象。"}, {"bbox": [49.0, 124.18800354003906, 132.291015625, 141.81600952148438], "conf": 1.0, "text": "2025年8月30日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "支委会确定发展对象记录", "char_count": 46, "signature_date": "2025-08-30", "signature_date_raw": "2025年8月30日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:16.102811+08	2026-10-17 18:36:16.102812+08
6	6	PDF_TEXT	\N	previews/212346cc243d484aa98cb6619785edff.pdf	自传\n我叫演示学生，出生日期 2003年5月12日。家庭主要成员有父亲、母亲。成长经历方面，我从\n小学起接受集体主义教育。思想演变上，我逐步认识到中国共产党是中国工人阶级的先锋队，\n全心全意为人民服务。\n认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认\n识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识\n深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。\n·····	516	[{"text": "自传\\n我叫演示学生，出生日期 2003年5月12日。家庭主要成员有父亲、母亲。成长经历方面，我从\\n小学起接受集体主义教育。思想演变上，我逐步认识到中国共产党是中国工人阶级的先锋队，\\n全心全意为人民服务。\\n认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认\\n识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识\\n深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 73.0, 76.9800033569336], "conf": 1.0, "text": "自传"}, {"bbox": [49.0, 91.78800201416016, 543.806640625, 109.41600799560547], "conf": 1.0, "text": "我叫演示学生，出生日期 2003年5月12日。家庭主要成员有父亲、母亲。成长经历方面，我从"}, {"bbox": [49.0, 114.09600830078125, 541.0, 129.77999877929688], "conf": 1.0, "text": "小学起接受集体主义教育。思想演变上，我逐步认识到中国共产党是中国工人阶级的先锋队，"}, {"bbox": [49.0, 134.49600219726562, 169.0, 150.17999267578125], "conf": 1.0, "text": "全心全意为人民服务。"}, {"bbox": [49.0, 166.89601135253906, 541.0, 182.5800018310547], "conf": 1.0, "text": "认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认"}, {"bbox": [49.0, 187.29600524902344, 541.0, 202.97999572753906], "conf": 1.0, "text": "识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识"}, {"bbox": [49.0, 207.6959991455078, 541.0, 223.37998962402344], "conf": 1.0, "text": "深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 228.0959930419922, 529.0, 243.7799835205078], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 248.49600219726562, 529.0, 264.17999267578125], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 268.8959655761719, 529.0, 284.5799560546875], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 289.2959899902344, 529.0, 304.97998046875], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 309.6959533691406, 529.0, 325.37994384765625], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 330.095947265625, 529.0, 345.7799377441406], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 350.4959411621094, 493.0, 366.179931640625], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": []}	{"title": "自传", "birth_date": "2003-05-12", "char_count": 502, "signature_date": "2003-05-12", "signature_date_raw": "2003年5月12日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:16.15032+08	2026-10-17 18:36:16.150321+08
7	7	PDF_TEXT	\N	previews/2b2951e975eb44c78e6552a41361b813.pdf	入党申请书\n敬爱的党组织：\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\n全意为人民服务的宗旨。我的入党动机是入党可以评优评奖，也为了好找工作，在学习和工作\n中发挥先锋模范作用。\n此致\n敬礼！\n申请人：演示学生\n2023年3月15日\n·····	182	[{"text": "入党申请书\\n敬爱的党组织：\\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\\n全意为人民服务的宗旨。我的入党动机是入党可以评优评奖，也为了好找工作，在学习和工作\\n中发挥先锋模范作用。\\n此致\\n敬礼！\\n申请人：演示学生\\n2023年3月15日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "入党申请书"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 124.18800354003906, 522.4375, 141.81600952148438], "conf": 1.0, "text": "我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代"}, {"bbox": [49.0, 144.58799743652344, 534.4375, 162.21600341796875], "conf": 1.0, "text": "表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心"}, {"bbox": [49.0, 166.89601135253906, 541.0, 182.5800018310547], "conf": 1.0, "text": "全意为人民服务的宗旨。我的入党动机是入党可以评优评奖，也为了好找工作，在学习和工作"}, {"bbox": [49.0, 187.29600524902344, 169.0, 202.97999572753906], "conf": 1.0, "text": "中发挥先锋模范作用。"}, {"bbox": [49.0, 219.6959991455078, 73.0, 235.37998962402344], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 252.09597778320312, 85.0, 267.77996826171875], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 284.4960021972656, 145.0, 300.17999267578125], "conf": 1.0, "text": "申请人：演示学生"}, {"bbox": [49.0, 314.98797607421875, 132.291015625, 332.615966796875], "conf": 1.0, "text": "2023年3月15日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "申请人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"name": "演示学生", "title": "入党申请书", "closing": "敬礼！", "char_count": 172, "salutation": "敬爱的党组织：", "signature_date": "2023-03-15", "signature_name": "演示学生", "signature_date_raw": "2023年3月15日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:16.212773+08	2026-10-17 18:36:16.212775+08
8	8	PDF_TEXT	\N	previews/2eea6d60dbe94766964664baf835a981.pdf	自传\n我叫演示学生，出生日期 2004年1月1日。我热爱学习。\n签名\n·····	39	[{"text": "自传\\n我叫演示学生，出生日期 2004年1月1日。我热爱学习。\\n签名\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 73.0, 76.9800033569336], "conf": 1.0, "text": "自传"}, {"bbox": [49.0, 91.78800201416016, 345.05078125, 109.41600799560547], "conf": 1.0, "text": "我叫演示学生，出生日期 2004年1月1日。我热爱学习。"}, {"bbox": [49.0, 126.09600830078125, 73.0, 141.77999877929688], "conf": 1.0, "text": "签名"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "签名", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"title": "自传", "birth_date": "2004-01-01", "char_count": 36, "signature_date": "2004-01-01", "signature_date_raw": "2004年1月1日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:16.275733+08	2026-10-17 18:36:16.275734+08
12	12	PDF_TEXT	\N	previews/7fc09c3349b7406abba2d2fbe67f9edc.pdf	支部大会讨论接收预备党员记录\n2025年6月1日\n???\n??\n·····	37	[{"text": "支部大会讨论接收预备党员记录\\n2025年6月1日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 217.0, 76.9800033569336], "conf": 1.0, "text": "支部大会讨论接收预备党员记录"}, {"bbox": [49.0, 91.78800201416016, 125.53515625, 109.41600799560547], "conf": 1.0, "text": "2025年6月1日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "支部大会讨论接收预备党员记录", "char_count": 33, "signature_date": "2025-06-01", "signature_date_raw": "2025年6月1日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:16.471126+08	2026-10-17 18:36:16.471127+08
14	14	PDF_TEXT	\N	previews/acedd1af240549899b0e3fe82c1c1cf4.pdf	集中培训结业证书\n培训时间 2024年7月1日至2024年7月5日，学时 24。\n???\n??\n·····	51	[{"text": "集中培训结业证书\\n培训时间 2024年7月1日至2024年7月5日，学时 24。\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 145.0, 76.9800033569336], "conf": 1.0, "text": "集中培训结业证书"}, {"bbox": [49.0, 91.78800201416016, 330.61328125, 109.41600799560547], "conf": 1.0, "text": "培训时间 2024年7月1日至2024年7月5日，学时 24。"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "集中培训结业证书", "char_count": 47, "signature_date": "2024-07-05", "signature_date_raw": "2024年7月5日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:16.553859+08	2026-10-17 18:36:16.55386+08
9	9	PDF_TEXT	\N	previews/120b8cb7a07346d39e766f5f53625ca1.pdf	思想汇报\n敬爱的党组织：\n本季度我认真学习党章，对照党员标准查找不足。\n此致\n敬礼！\n汇报人：演示学生\n2025年8月1日\n·····	67	[{"text": "思想汇报\\n敬爱的党组织：\\n本季度我认真学习党章，对照党员标准查找不足。\\n此致\\n敬礼！\\n汇报人：演示学生\\n2025年8月1日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 97.0, 76.9800033569336], "conf": 1.0, "text": "思想汇报"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 126.09600830078125, 313.0, 141.77999877929688], "conf": 1.0, "text": "本季度我认真学习党章，对照党员标准查找不足。"}, {"bbox": [49.0, 158.49600219726562, 73.0, 174.17999267578125], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 190.89601135253906, 85.0, 206.5800018310547], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 223.29600524902344, 145.0, 238.97999572753906], "conf": 1.0, "text": "汇报人：演示学生"}, {"bbox": [49.0, 253.7880096435547, 125.53515625, 271.416015625], "conf": 1.0, "text": "2025年8月1日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "汇报人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"title": "思想汇报", "closing": "敬礼！", "char_count": 60, "salutation": "敬爱的党组织：", "signature_date": "2025-08-01", "signature_name": "演示学生", "signature_date_raw": "2025年8月1日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:16.319215+08	2026-10-17 18:36:16.319216+08
10	10	PDF_TEXT	\N	previews/634209f1cd9346ff9792f1783c7f62c5.pdf	入党申请书\n敬爱的党组织：\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\n范作用。\n此致\n敬礼！\n申请人：演示学生\n2023年3月15日\n·····	176	[{"text": "入党申请书\\n敬爱的党组织：\\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\\n范作用。\\n此致\\n敬礼！\\n申请人：演示学生\\n2023年3月15日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "入党申请书"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 124.18800354003906, 522.4375, 141.81600952148438], "conf": 1.0, "text": "我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代"}, {"bbox": [49.0, 144.58799743652344, 534.4375, 162.21600341796875], "conf": 1.0, "text": "表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心"}, {"bbox": [49.0, 166.89601135253906, 541.0, 182.5800018310547], "conf": 1.0, "text": "全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模"}, {"bbox": [49.0, 187.29600524902344, 97.0, 202.97999572753906], "conf": 1.0, "text": "范作用。"}, {"bbox": [49.0, 219.6959991455078, 73.0, 235.37998962402344], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 252.09597778320312, 85.0, 267.77996826171875], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 284.4960021972656, 145.0, 300.17999267578125], "conf": 1.0, "text": "申请人：演示学生"}, {"bbox": [49.0, 314.98797607421875, 132.291015625, 332.615966796875], "conf": 1.0, "text": "2023年3月15日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "申请人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"name": "演示学生", "title": "入党申请书", "closing": "敬礼！", "char_count": 166, "salutation": "敬爱的党组织：", "signature_date": "2023-03-15", "signature_name": "演示学生", "signature_date_raw": "2023年3月15日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:16.374658+08	2026-10-17 18:36:16.374659+08
11	11	PDF_TEXT	\N	previews/0048c3b8b3134e6e805adcccd82e3a53.pdf	入党志愿书\n姓名 演示学生 出生日期 2003年5月12日\n2025年5月20日\n???\n??\n·····	50	[{"text": "入党志愿书\\n姓名 演示学生 出生日期 2003年5月12日\\n2025年5月20日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "入党志愿书"}, {"bbox": [49.0, 91.78800201416016, 262.837890625, 109.41600799560547], "conf": 1.0, "text": "姓名 演示学生 出生日期 2003年5月12日"}, {"bbox": [49.0, 124.18800354003906, 132.291015625, 141.81600952148438], "conf": 1.0, "text": "2025年5月20日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"name": "演示学生", "title": "入党志愿书", "birth_date": "2003-05-12", "char_count": 45, "signature_date": "2025-05-20", "signature_date_raw": "2025年5月20日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:16.427569+08	2026-10-17 18:36:16.42757+08
13	13	PDF_TEXT	\N	previews/e61e6ab1874a42d886518c0f5c775027.pdf	政治审查材料\n政审合格。\n2024年6月1日\n???\n??\n·····	35	[{"text": "政治审查材料\\n政审合格。\\n2024年6月1日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 121.0, 76.9800033569336], "conf": 1.0, "text": "政治审查材料"}, {"bbox": [49.0, 93.69600677490234, 109.0, 109.3800048828125], "conf": 1.0, "text": "政审合格。"}, {"bbox": [49.0, 124.18800354003906, 125.53515625, 141.81600952148438], "conf": 1.0, "text": "2024年6月1日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "政治审查材料", "char_count": 30, "signature_date": "2024-06-01", "signature_date_raw": "2024年6月1日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:16.513358+08	2026-10-17 18:36:16.513359+08
15	15	PDF_TEXT	\N	previews/f96f3a7533f148b89f4e738f5984d69e.pdf	发展对象公示材料\n公示自 2025年4月20 日至 2025年4月26 日。\n???\n??\n·····	47	[{"text": "发展对象公示材料\\n公示自 2025年4月20 日至 2025年4月26 日。\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 145.0, 76.9800033569336], "conf": 1.0, "text": "发展对象公示材料"}, {"bbox": [49.0, 91.78800201416016, 289.64453125, 109.41600799560547], "conf": 1.0, "text": "公示自 2025年4月20 日至 2025年4月26 日。"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "发展对象公示材料", "char_count": 43, "signature_date": "2025-04-26", "signature_date_raw": "2025年4月26日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:16.595288+08	2026-10-17 18:36:16.595289+08
16	16	PDF_TEXT	\N	previews/22527387ee874083bfd40fc2716cf540.pdf	上级党委预审意见\n同意。\n2025年5月10日\n???\n??\n·····	36	[{"text": "上级党委预审意见\\n同意。\\n2025年5月10日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 145.0, 76.9800033569336], "conf": 1.0, "text": "上级党委预审意见"}, {"bbox": [49.0, 93.69600677490234, 85.0, 109.3800048828125], "conf": 1.0, "text": "同意。"}, {"bbox": [49.0, 124.18800354003906, 132.291015625, 141.81600952148438], "conf": 1.0, "text": "2025年5月10日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "上级党委预审意见", "char_count": 31, "signature_date": "2025-05-10", "signature_date_raw": "2025年5月10日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:16.635184+08	2026-10-17 18:36:16.635185+08
17	17	PDF_TEXT	\N	previews/0c5ba3674b0149f7806ce6c2b486e0ea.pdf	转正申请书\n敬爱的党组织：\n我志愿按期转正。\n此致\n敬礼！\n2025年9月20日\n·····	46	[{"text": "转正申请书\\n敬爱的党组织：\\n我志愿按期转正。\\n此致\\n敬礼！\\n2025年9月20日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "转正申请书"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 126.09600830078125, 145.0, 141.77999877929688], "conf": 1.0, "text": "我志愿按期转正。"}, {"bbox": [49.0, 158.49600219726562, 73.0, 174.17999267578125], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 190.89601135253906, 85.0, 206.5800018310547], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 221.38800048828125, 132.291015625, 239.01600646972656], "conf": 1.0, "text": "2025年9月20日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": []}	{"title": "转正申请书", "closing": "敬礼！", "char_count": 40, "salutation": "敬爱的党组织：", "signature_date": "2025-09-20", "signature_date_raw": "2025年9月20日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:16.685705+08	2026-10-17 18:36:16.685707+08
19	19	PDF_TEXT	\N	previews/1746aa17608443d79ed534ddcd7557e0.pdf	转正公示材料\n公示 2025年9月25 日至 2025年10月8 日。\n???\n??\n·····	44	[{"text": "转正公示材料\\n公示 2025年9月25 日至 2025年10月8 日。\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 121.0, 76.9800033569336], "conf": 1.0, "text": "转正公示材料"}, {"bbox": [49.0, 91.78800201416016, 277.64453125, 109.41600799560547], "conf": 1.0, "text": "公示 2025年9月25 日至 2025年10月8 日。"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "转正公示材料", "char_count": 40, "signature_date": "2025-10-08", "signature_date_raw": "2025年10月8日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:16.773999+08	2026-10-17 18:36:16.774+08
20	20	PDF_TEXT	\N	previews/2e49fdc9433d403f91f44011a19691f9.pdf	入党申请书\n敬爱的党组织：\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\n范作用。\n此致\n敬礼！\n申请人：演示学生\n2023年3月15日\n·····	176	[{"text": "入党申请书\\n敬爱的党组织：\\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\\n范作用。\\n此致\\n敬礼！\\n申请人：演示学生\\n2023年3月15日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "入党申请书"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 124.18800354003906, 522.4375, 141.81600952148438], "conf": 1.0, "text": "我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代"}, {"bbox": [49.0, 144.58799743652344, 534.4375, 162.21600341796875], "conf": 1.0, "text": "表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心"}, {"bbox": [49.0, 166.89601135253906, 541.0, 182.5800018310547], "conf": 1.0, "text": "全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模"}, {"bbox": [49.0, 187.29600524902344, 97.0, 202.97999572753906], "conf": 1.0, "text": "范作用。"}, {"bbox": [49.0, 219.6959991455078, 73.0, 235.37998962402344], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 252.09597778320312, 85.0, 267.77996826171875], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 284.4960021972656, 145.0, 300.17999267578125], "conf": 1.0, "text": "申请人：演示学生"}, {"bbox": [49.0, 314.98797607421875, 132.291015625, 332.615966796875], "conf": 1.0, "text": "2023年3月15日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "申请人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"name": "演示学生", "title": "入党申请书", "closing": "敬礼！", "char_count": 166, "salutation": "敬爱的党组织：", "signature_date": "2023-03-15", "signature_name": "演示学生", "signature_date_raw": "2023年3月15日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:16.829815+08	2026-10-17 18:36:16.829816+08
23	23	PDF_TEXT	\N	previews/c6fb658f8d0b4f6da777c4b35817f0a7.pdf	思想汇报\n敬爱的党组织：\n本季度我认真学习党章，对照党员标准查找不足。\n此致\n敬礼！\n汇报人：演示学生\n2024年12月20日\n·····	69	[{"text": "思想汇报\\n敬爱的党组织：\\n本季度我认真学习党章，对照党员标准查找不足。\\n此致\\n敬礼！\\n汇报人：演示学生\\n2024年12月20日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 97.0, 76.9800033569336], "conf": 1.0, "text": "思想汇报"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 126.09600830078125, 313.0, 141.77999877929688], "conf": 1.0, "text": "本季度我认真学习党章，对照党员标准查找不足。"}, {"bbox": [49.0, 158.49600219726562, 73.0, 174.17999267578125], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 190.89601135253906, 85.0, 206.5800018310547], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 223.29600524902344, 145.0, 238.97999572753906], "conf": 1.0, "text": "汇报人：演示学生"}, {"bbox": [49.0, 253.7880096435547, 139.046875, 271.416015625], "conf": 1.0, "text": "2024年12月20日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "汇报人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"title": "思想汇报", "closing": "敬礼！", "char_count": 62, "salutation": "敬爱的党组织：", "signature_date": "2024-12-20", "signature_name": "演示学生", "signature_date_raw": "2024年12月20日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:16.966825+08	2026-10-17 18:36:16.966827+08
18	18	PDF_TEXT	\N	previews/eb939421540242e1940390be6ef20503.pdf	支部大会讨论转正记录\n2025年10月8日\n???\n??\n·····	34	[{"text": "支部大会讨论转正记录\\n2025年10月8日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 169.0, 76.9800033569336], "conf": 1.0, "text": "支部大会讨论转正记录"}, {"bbox": [49.0, 91.78800201416016, 132.291015625, 109.41600799560547], "conf": 1.0, "text": "2025年10月8日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "支部大会讨论转正记录", "char_count": 30, "signature_date": "2025-10-08", "signature_date_raw": "2025年10月8日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:16.732009+08	2026-10-17 18:36:16.73201+08
21	21	PDF_TEXT	\N	previews/8a96b32d3ef94553a404e074785bf4e9.pdf	党组织派人谈话记录\n谈话人已谈话。\n2023年3月28日\n???\n??\n·····	41	[{"text": "党组织派人谈话记录\\n谈话人已谈话。\\n2023年3月28日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 157.0, 76.9800033569336], "conf": 1.0, "text": "党组织派人谈话记录"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "谈话人已谈话。"}, {"bbox": [49.0, 124.18800354003906, 132.291015625, 141.81600952148438], "conf": 1.0, "text": "2023年3月28日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "党组织派人谈话记录", "char_count": 36, "salutation": "党组织派人谈话记录", "signature_date": "2023-03-28", "signature_date_raw": "2023年3月28日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:16.871742+08	2026-10-17 18:36:16.871743+08
22	22	PDF_TEXT	\N	previews/95980ca969a6460ab8499f5d26574bf6.pdf	入党申请书\n敬爱的党组织：\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\n范作用。\n此致\n敬礼！\n申请人：演示学生\n2023年3月15日\n·····	176	[{"text": "入党申请书\\n敬爱的党组织：\\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\\n范作用。\\n此致\\n敬礼！\\n申请人：演示学生\\n2023年3月15日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "入党申请书"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 124.18800354003906, 522.4375, 141.81600952148438], "conf": 1.0, "text": "我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代"}, {"bbox": [49.0, 144.58799743652344, 534.4375, 162.21600341796875], "conf": 1.0, "text": "表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心"}, {"bbox": [49.0, 166.89601135253906, 541.0, 182.5800018310547], "conf": 1.0, "text": "全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模"}, {"bbox": [49.0, 187.29600524902344, 97.0, 202.97999572753906], "conf": 1.0, "text": "范作用。"}, {"bbox": [49.0, 219.6959991455078, 73.0, 235.37998962402344], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 252.09597778320312, 85.0, 267.77996826171875], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 284.4960021972656, 145.0, 300.17999267578125], "conf": 1.0, "text": "申请人：演示学生"}, {"bbox": [49.0, 314.98797607421875, 132.291015625, 332.615966796875], "conf": 1.0, "text": "2023年3月15日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "申请人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"name": "演示学生", "title": "入党申请书", "closing": "敬礼！", "char_count": 166, "salutation": "敬爱的党组织：", "signature_date": "2023-03-15", "signature_name": "演示学生", "signature_date_raw": "2023年3月15日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:16.925326+08	2026-10-17 18:36:16.925327+08
24	24	PDF_TEXT	\N	previews/5d7caa8950e9442b82b36d72c845b6e9.pdf	思想汇报\n敬爱的党组织：\n本季度我认真学习党章，对照党员标准查找不足。\n此致\n敬礼！\n汇报人：演示学生\n2025年3月25日\n·····	68	[{"text": "思想汇报\\n敬爱的党组织：\\n本季度我认真学习党章，对照党员标准查找不足。\\n此致\\n敬礼！\\n汇报人：演示学生\\n2025年3月25日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 97.0, 76.9800033569336], "conf": 1.0, "text": "思想汇报"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 126.09600830078125, 313.0, 141.77999877929688], "conf": 1.0, "text": "本季度我认真学习党章，对照党员标准查找不足。"}, {"bbox": [49.0, 158.49600219726562, 73.0, 174.17999267578125], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 190.89601135253906, 85.0, 206.5800018310547], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 223.29600524902344, 145.0, 238.97999572753906], "conf": 1.0, "text": "汇报人：演示学生"}, {"bbox": [49.0, 253.7880096435547, 132.291015625, 271.416015625], "conf": 1.0, "text": "2025年3月25日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "汇报人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"title": "思想汇报", "closing": "敬礼！", "char_count": 61, "salutation": "敬爱的党组织：", "signature_date": "2025-03-25", "signature_name": "演示学生", "signature_date_raw": "2025年3月25日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.008513+08	2026-10-17 18:36:17.008514+08
26	26	PDF_TEXT	\N	previews/68395a349efb4054aab10559f30ffe94.pdf	支委会确定发展对象记录\n经讨论，确定该同志为发展对象。\n2025年8月30日\n???\n??\n·····	51	[{"text": "支委会确定发展对象记录\\n经讨论，确定该同志为发展对象。\\n2025年8月30日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 181.0, 76.9800033569336], "conf": 1.0, "text": "支委会确定发展对象记录"}, {"bbox": [49.0, 93.69600677490234, 229.0, 109.3800048828125], "conf": 1.0, "text": "经讨论，确定该同志为发展对象。"}, {"bbox": [49.0, 124.18800354003906, 132.291015625, 141.81600952148438], "conf": 1.0, "text": "2025年8月30日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "支委会确定发展对象记录", "char_count": 46, "signature_date": "2025-08-30", "signature_date_raw": "2025年8月30日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.089088+08	2026-10-17 18:36:17.089089+08
25	25	PDF_TEXT	\N	previews/728da1b36ae34f05b98049836b82d628.pdf	思想汇报\n敬爱的党组织：\n本季度我认真学习党章，对照党员标准查找不足。\n此致\n敬礼！\n汇报人：演示学生\n2025年7月1日\n·····	67	[{"text": "思想汇报\\n敬爱的党组织：\\n本季度我认真学习党章，对照党员标准查找不足。\\n此致\\n敬礼！\\n汇报人：演示学生\\n2025年7月1日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 97.0, 76.9800033569336], "conf": 1.0, "text": "思想汇报"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 126.09600830078125, 313.0, 141.77999877929688], "conf": 1.0, "text": "本季度我认真学习党章，对照党员标准查找不足。"}, {"bbox": [49.0, 158.49600219726562, 73.0, 174.17999267578125], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 190.89601135253906, 85.0, 206.5800018310547], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 223.29600524902344, 145.0, 238.97999572753906], "conf": 1.0, "text": "汇报人：演示学生"}, {"bbox": [49.0, 253.7880096435547, 125.53515625, 271.416015625], "conf": 1.0, "text": "2025年7月1日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "汇报人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"title": "思想汇报", "closing": "敬礼！", "char_count": 60, "salutation": "敬爱的党组织：", "signature_date": "2025-07-01", "signature_name": "演示学生", "signature_date_raw": "2025年7月1日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.048578+08	2026-10-17 18:36:17.048579+08
27	27	PDF_TEXT	\N	previews/ccc55420b74346e0a733e235a2bbc87c.pdf	自传\n我叫演示学生，出生日期 2003年5月12日。家庭主要成员有父亲、母亲。成长经历方面，我从\n小学起接受集体主义教育。思想演变上，我逐步认识到中国共产党是中国工人阶级的先锋队，\n全心全意为人民服务。\n认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认\n识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识\n深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。\n·····	516	[{"text": "自传\\n我叫演示学生，出生日期 2003年5月12日。家庭主要成员有父亲、母亲。成长经历方面，我从\\n小学起接受集体主义教育。思想演变上，我逐步认识到中国共产党是中国工人阶级的先锋队，\\n全心全意为人民服务。\\n认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认\\n识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识\\n深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 73.0, 76.9800033569336], "conf": 1.0, "text": "自传"}, {"bbox": [49.0, 91.78800201416016, 543.806640625, 109.41600799560547], "conf": 1.0, "text": "我叫演示学生，出生日期 2003年5月12日。家庭主要成员有父亲、母亲。成长经历方面，我从"}, {"bbox": [49.0, 114.09600830078125, 541.0, 129.77999877929688], "conf": 1.0, "text": "小学起接受集体主义教育。思想演变上，我逐步认识到中国共产党是中国工人阶级的先锋队，"}, {"bbox": [49.0, 134.49600219726562, 169.0, 150.17999267578125], "conf": 1.0, "text": "全心全意为人民服务。"}, {"bbox": [49.0, 166.89601135253906, 541.0, 182.5800018310547], "conf": 1.0, "text": "认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认"}, {"bbox": [49.0, 187.29600524902344, 541.0, 202.97999572753906], "conf": 1.0, "text": "识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识"}, {"bbox": [49.0, 207.6959991455078, 541.0, 223.37998962402344], "conf": 1.0, "text": "深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 228.0959930419922, 529.0, 243.7799835205078], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 248.49600219726562, 529.0, 264.17999267578125], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 268.8959655761719, 529.0, 284.5799560546875], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 289.2959899902344, 529.0, 304.97998046875], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 309.6959533691406, 529.0, 325.37994384765625], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 330.095947265625, 529.0, 345.7799377441406], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 350.4959411621094, 493.0, 366.179931640625], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": []}	{"title": "自传", "birth_date": "2003-05-12", "char_count": 502, "signature_date": "2003-05-12", "signature_date_raw": "2003年5月12日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.130892+08	2026-10-17 18:36:17.130893+08
28	28	PDF_TEXT	\N	previews/6f98d682f24e4a75aef322c35dffe2cd.pdf	入党申请书\n敬爱的党组织：\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\n全意为人民服务的宗旨。我的入党动机是入党可以评优评奖，也为了好找工作，在学习和工作\n中发挥先锋模范作用。\n此致\n敬礼！\n申请人：演示学生\n2023年3月15日\n·····	182	[{"text": "入党申请书\\n敬爱的党组织：\\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\\n全意为人民服务的宗旨。我的入党动机是入党可以评优评奖，也为了好找工作，在学习和工作\\n中发挥先锋模范作用。\\n此致\\n敬礼！\\n申请人：演示学生\\n2023年3月15日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "入党申请书"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 124.18800354003906, 522.4375, 141.81600952148438], "conf": 1.0, "text": "我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代"}, {"bbox": [49.0, 144.58799743652344, 534.4375, 162.21600341796875], "conf": 1.0, "text": "表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心"}, {"bbox": [49.0, 166.89601135253906, 541.0, 182.5800018310547], "conf": 1.0, "text": "全意为人民服务的宗旨。我的入党动机是入党可以评优评奖，也为了好找工作，在学习和工作"}, {"bbox": [49.0, 187.29600524902344, 169.0, 202.97999572753906], "conf": 1.0, "text": "中发挥先锋模范作用。"}, {"bbox": [49.0, 219.6959991455078, 73.0, 235.37998962402344], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 252.09597778320312, 85.0, 267.77996826171875], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 284.4960021972656, 145.0, 300.17999267578125], "conf": 1.0, "text": "申请人：演示学生"}, {"bbox": [49.0, 314.98797607421875, 132.291015625, 332.615966796875], "conf": 1.0, "text": "2023年3月15日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "申请人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"name": "演示学生", "title": "入党申请书", "closing": "敬礼！", "char_count": 172, "salutation": "敬爱的党组织：", "signature_date": "2023-03-15", "signature_name": "演示学生", "signature_date_raw": "2023年3月15日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.183161+08	2026-10-17 18:36:17.183162+08
51	51	PDF_TEXT	\N	previews/a8de1cd74b614422ba3b369885090f16.pdf	思想汇报\n敬爱的党组织：\n本季度我认真学习党章，对照党员标准查找不足。\n此致\n敬礼！\n汇报人：演示学生\n2025年8月1日\n·····	67	[{"text": "思想汇报\\n敬爱的党组织：\\n本季度我认真学习党章，对照党员标准查找不足。\\n此致\\n敬礼！\\n汇报人：演示学生\\n2025年8月1日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 97.0, 76.9800033569336], "conf": 1.0, "text": "思想汇报"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 126.09600830078125, 313.0, 141.77999877929688], "conf": 1.0, "text": "本季度我认真学习党章，对照党员标准查找不足。"}, {"bbox": [49.0, 158.49600219726562, 73.0, 174.17999267578125], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 190.89601135253906, 85.0, 206.5800018310547], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 223.29600524902344, 145.0, 238.97999572753906], "conf": 1.0, "text": "汇报人：演示学生"}, {"bbox": [49.0, 253.7880096435547, 125.53515625, 271.416015625], "conf": 1.0, "text": "2025年8月1日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "汇报人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"title": "思想汇报", "closing": "敬礼！", "char_count": 60, "salutation": "敬爱的党组织：", "signature_date": "2025-08-01", "signature_name": "演示学生", "signature_date_raw": "2025年8月1日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:18.275129+08	2026-10-17 18:36:18.27513+08
52	52	PDF_TEXT	\N	previews/699e59e87b1040a08c0354a195c0baf3.pdf	入党申请书\n敬爱的党组织：\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\n范作用。\n此致\n敬礼！\n申请人：演示学生\n2023年3月15日\n·····	176	[{"text": "入党申请书\\n敬爱的党组织：\\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\\n范作用。\\n此致\\n敬礼！\\n申请人：演示学生\\n2023年3月15日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "入党申请书"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 124.18800354003906, 522.4375, 141.81600952148438], "conf": 1.0, "text": "我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代"}, {"bbox": [49.0, 144.58799743652344, 534.4375, 162.21600341796875], "conf": 1.0, "text": "表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心"}, {"bbox": [49.0, 166.89601135253906, 541.0, 182.5800018310547], "conf": 1.0, "text": "全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模"}, {"bbox": [49.0, 187.29600524902344, 97.0, 202.97999572753906], "conf": 1.0, "text": "范作用。"}, {"bbox": [49.0, 219.6959991455078, 73.0, 235.37998962402344], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 252.09597778320312, 85.0, 267.77996826171875], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 284.4960021972656, 145.0, 300.17999267578125], "conf": 1.0, "text": "申请人：演示学生"}, {"bbox": [49.0, 314.98797607421875, 132.291015625, 332.615966796875], "conf": 1.0, "text": "2023年3月15日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "申请人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"name": "演示学生", "title": "入党申请书", "closing": "敬礼！", "char_count": 166, "salutation": "敬爱的党组织：", "signature_date": "2023-03-15", "signature_name": "演示学生", "signature_date_raw": "2023年3月15日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:18.329538+08	2026-10-17 18:36:18.329538+08
29	29	PDF_TEXT	\N	previews/b8cd588681904cf1b0cb7a8e9d34b4b1.pdf	自传\n我叫演示学生，出生日期 2004年1月1日。我热爱学习。\n签名\n·····	39	[{"text": "自传\\n我叫演示学生，出生日期 2004年1月1日。我热爱学习。\\n签名\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 73.0, 76.9800033569336], "conf": 1.0, "text": "自传"}, {"bbox": [49.0, 91.78800201416016, 345.05078125, 109.41600799560547], "conf": 1.0, "text": "我叫演示学生，出生日期 2004年1月1日。我热爱学习。"}, {"bbox": [49.0, 126.09600830078125, 73.0, 141.77999877929688], "conf": 1.0, "text": "签名"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "签名", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"title": "自传", "birth_date": "2004-01-01", "char_count": 36, "signature_date": "2004-01-01", "signature_date_raw": "2004年1月1日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.231928+08	2026-10-17 18:36:17.231929+08
30	30	PDF_TEXT	\N	previews/236f3bfed5f94c5693d233edcdb18dfc.pdf	思想汇报\n敬爱的党组织：\n本季度我认真学习党章，对照党员标准查找不足。\n此致\n敬礼！\n汇报人：演示学生\n2025年8月1日\n·····	67	[{"text": "思想汇报\\n敬爱的党组织：\\n本季度我认真学习党章，对照党员标准查找不足。\\n此致\\n敬礼！\\n汇报人：演示学生\\n2025年8月1日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 97.0, 76.9800033569336], "conf": 1.0, "text": "思想汇报"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 126.09600830078125, 313.0, 141.77999877929688], "conf": 1.0, "text": "本季度我认真学习党章，对照党员标准查找不足。"}, {"bbox": [49.0, 158.49600219726562, 73.0, 174.17999267578125], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 190.89601135253906, 85.0, 206.5800018310547], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 223.29600524902344, 145.0, 238.97999572753906], "conf": 1.0, "text": "汇报人：演示学生"}, {"bbox": [49.0, 253.7880096435547, 125.53515625, 271.416015625], "conf": 1.0, "text": "2025年8月1日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "汇报人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"title": "思想汇报", "closing": "敬礼！", "char_count": 60, "salutation": "敬爱的党组织：", "signature_date": "2025-08-01", "signature_name": "演示学生", "signature_date_raw": "2025年8月1日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.283449+08	2026-10-17 18:36:17.28345+08
31	31	PDF_TEXT	\N	previews/bb28b994a56e45f8a9e093904fe1dc20.pdf	入党申请书\n敬爱的党组织：\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\n范作用。\n此致\n敬礼！\n申请人：演示学生\n2023年3月15日\n·····	176	[{"text": "入党申请书\\n敬爱的党组织：\\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\\n范作用。\\n此致\\n敬礼！\\n申请人：演示学生\\n2023年3月15日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "入党申请书"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 124.18800354003906, 522.4375, 141.81600952148438], "conf": 1.0, "text": "我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代"}, {"bbox": [49.0, 144.58799743652344, 534.4375, 162.21600341796875], "conf": 1.0, "text": "表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心"}, {"bbox": [49.0, 166.89601135253906, 541.0, 182.5800018310547], "conf": 1.0, "text": "全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模"}, {"bbox": [49.0, 187.29600524902344, 97.0, 202.97999572753906], "conf": 1.0, "text": "范作用。"}, {"bbox": [49.0, 219.6959991455078, 73.0, 235.37998962402344], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 252.09597778320312, 85.0, 267.77996826171875], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 284.4960021972656, 145.0, 300.17999267578125], "conf": 1.0, "text": "申请人：演示学生"}, {"bbox": [49.0, 314.98797607421875, 132.291015625, 332.615966796875], "conf": 1.0, "text": "2023年3月15日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "申请人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"name": "演示学生", "title": "入党申请书", "closing": "敬礼！", "char_count": 166, "salutation": "敬爱的党组织：", "signature_date": "2023-03-15", "signature_name": "演示学生", "signature_date_raw": "2023年3月15日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.352259+08	2026-10-17 18:36:17.35226+08
32	32	PDF_TEXT	\N	previews/65c7aba26f1c45019dcea04bfb4ee71c.pdf	入党志愿书\n姓名 演示学生 出生日期 2003年5月12日\n2025年5月20日\n???\n??\n·····	50	[{"text": "入党志愿书\\n姓名 演示学生 出生日期 2003年5月12日\\n2025年5月20日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "入党志愿书"}, {"bbox": [49.0, 91.78800201416016, 262.837890625, 109.41600799560547], "conf": 1.0, "text": "姓名 演示学生 出生日期 2003年5月12日"}, {"bbox": [49.0, 124.18800354003906, 132.291015625, 141.81600952148438], "conf": 1.0, "text": "2025年5月20日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"name": "演示学生", "title": "入党志愿书", "birth_date": "2003-05-12", "char_count": 45, "signature_date": "2025-05-20", "signature_date_raw": "2025年5月20日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.392197+08	2026-10-17 18:36:17.392198+08
33	33	PDF_TEXT	\N	previews/0f6e970c0f834e1881a6a965b507776e.pdf	支部大会讨论接收预备党员记录\n2025年6月1日\n???\n??\n·····	37	[{"text": "支部大会讨论接收预备党员记录\\n2025年6月1日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 217.0, 76.9800033569336], "conf": 1.0, "text": "支部大会讨论接收预备党员记录"}, {"bbox": [49.0, 91.78800201416016, 125.53515625, 109.41600799560547], "conf": 1.0, "text": "2025年6月1日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "支部大会讨论接收预备党员记录", "char_count": 33, "signature_date": "2025-06-01", "signature_date_raw": "2025年6月1日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.43385+08	2026-10-17 18:36:17.433851+08
34	34	PDF_TEXT	\N	previews/1971e5bb9e084d93b22a9fe508ba83e9.pdf	政治审查材料\n政审合格。\n2024年6月1日\n???\n??\n·····	35	[{"text": "政治审查材料\\n政审合格。\\n2024年6月1日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 121.0, 76.9800033569336], "conf": 1.0, "text": "政治审查材料"}, {"bbox": [49.0, 93.69600677490234, 109.0, 109.3800048828125], "conf": 1.0, "text": "政审合格。"}, {"bbox": [49.0, 124.18800354003906, 125.53515625, 141.81600952148438], "conf": 1.0, "text": "2024年6月1日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "政治审查材料", "char_count": 30, "signature_date": "2024-06-01", "signature_date_raw": "2024年6月1日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.477747+08	2026-10-17 18:36:17.477749+08
36	36	PDF_TEXT	\N	previews/f7504ed38cff4444815af0ece4446fcf.pdf	发展对象公示材料\n公示自 2025年4月20 日至 2025年4月26 日。\n???\n??\n·····	47	[{"text": "发展对象公示材料\\n公示自 2025年4月20 日至 2025年4月26 日。\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 145.0, 76.9800033569336], "conf": 1.0, "text": "发展对象公示材料"}, {"bbox": [49.0, 91.78800201416016, 289.64453125, 109.41600799560547], "conf": 1.0, "text": "公示自 2025年4月20 日至 2025年4月26 日。"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "发展对象公示材料", "char_count": 43, "signature_date": "2025-04-26", "signature_date_raw": "2025年4月26日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.559255+08	2026-10-17 18:36:17.559256+08
39	39	PDF_TEXT	\N	previews/1d4491f30f0742c68f8e8325b820e344.pdf	支部大会讨论转正记录\n2025年10月8日\n???\n??\n·····	34	[{"text": "支部大会讨论转正记录\\n2025年10月8日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 169.0, 76.9800033569336], "conf": 1.0, "text": "支部大会讨论转正记录"}, {"bbox": [49.0, 91.78800201416016, 132.291015625, 109.41600799560547], "conf": 1.0, "text": "2025年10月8日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "支部大会讨论转正记录", "char_count": 30, "signature_date": "2025-10-08", "signature_date_raw": "2025年10月8日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.707456+08	2026-10-17 18:36:17.707456+08
42	42	PDF_TEXT	\N	previews/879a68725e6440c5adaee93a567fd714.pdf	党组织派人谈话记录\n谈话人已谈话。\n2023年3月28日\n???\n??\n·····	41	[{"text": "党组织派人谈话记录\\n谈话人已谈话。\\n2023年3月28日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 157.0, 76.9800033569336], "conf": 1.0, "text": "党组织派人谈话记录"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "谈话人已谈话。"}, {"bbox": [49.0, 124.18800354003906, 132.291015625, 141.81600952148438], "conf": 1.0, "text": "2023年3月28日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "党组织派人谈话记录", "char_count": 36, "salutation": "党组织派人谈话记录", "signature_date": "2023-03-28", "signature_date_raw": "2023年3月28日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.846561+08	2026-10-17 18:36:17.846562+08
43	43	PDF_TEXT	\N	previews/3b444d247e0d42f1b6bcc815df6f4287.pdf	入党申请书\n敬爱的党组织：\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\n范作用。\n此致\n敬礼！\n申请人：演示学生\n2023年3月15日\n·····	176	[{"text": "入党申请书\\n敬爱的党组织：\\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\\n范作用。\\n此致\\n敬礼！\\n申请人：演示学生\\n2023年3月15日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "入党申请书"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 124.18800354003906, 522.4375, 141.81600952148438], "conf": 1.0, "text": "我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代"}, {"bbox": [49.0, 144.58799743652344, 534.4375, 162.21600341796875], "conf": 1.0, "text": "表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心"}, {"bbox": [49.0, 166.89601135253906, 541.0, 182.5800018310547], "conf": 1.0, "text": "全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模"}, {"bbox": [49.0, 187.29600524902344, 97.0, 202.97999572753906], "conf": 1.0, "text": "范作用。"}, {"bbox": [49.0, 219.6959991455078, 73.0, 235.37998962402344], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 252.09597778320312, 85.0, 267.77996826171875], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 284.4960021972656, 145.0, 300.17999267578125], "conf": 1.0, "text": "申请人：演示学生"}, {"bbox": [49.0, 314.98797607421875, 132.291015625, 332.615966796875], "conf": 1.0, "text": "2023年3月15日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "申请人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"name": "演示学生", "title": "入党申请书", "closing": "敬礼！", "char_count": 166, "salutation": "敬爱的党组织：", "signature_date": "2023-03-15", "signature_name": "演示学生", "signature_date_raw": "2023年3月15日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.894424+08	2026-10-17 18:36:17.894425+08
35	35	PDF_TEXT	\N	previews/92baeb9266794689aa569038b33da789.pdf	集中培训结业证书\n培训时间 2024年7月1日至2024年7月5日，学时 24。\n???\n??\n·····	51	[{"text": "集中培训结业证书\\n培训时间 2024年7月1日至2024年7月5日，学时 24。\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 145.0, 76.9800033569336], "conf": 1.0, "text": "集中培训结业证书"}, {"bbox": [49.0, 91.78800201416016, 330.61328125, 109.41600799560547], "conf": 1.0, "text": "培训时间 2024年7月1日至2024年7月5日，学时 24。"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "集中培训结业证书", "char_count": 47, "signature_date": "2024-07-05", "signature_date_raw": "2024年7月5日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.518746+08	2026-10-17 18:36:17.518747+08
37	37	PDF_TEXT	\N	previews/b788609d8ffc40e5a82466d2da277ec2.pdf	上级党委预审意见\n同意。\n2025年5月10日\n???\n??\n·····	36	[{"text": "上级党委预审意见\\n同意。\\n2025年5月10日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 145.0, 76.9800033569336], "conf": 1.0, "text": "上级党委预审意见"}, {"bbox": [49.0, 93.69600677490234, 85.0, 109.3800048828125], "conf": 1.0, "text": "同意。"}, {"bbox": [49.0, 124.18800354003906, 132.291015625, 141.81600952148438], "conf": 1.0, "text": "2025年5月10日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "上级党委预审意见", "char_count": 31, "signature_date": "2025-05-10", "signature_date_raw": "2025年5月10日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.602381+08	2026-10-17 18:36:17.602382+08
38	38	PDF_TEXT	\N	previews/63b589a614754f57979b3573a412514c.pdf	转正申请书\n敬爱的党组织：\n我志愿按期转正。\n此致\n敬礼！\n2025年9月20日\n·····	46	[{"text": "转正申请书\\n敬爱的党组织：\\n我志愿按期转正。\\n此致\\n敬礼！\\n2025年9月20日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "转正申请书"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 126.09600830078125, 145.0, 141.77999877929688], "conf": 1.0, "text": "我志愿按期转正。"}, {"bbox": [49.0, 158.49600219726562, 73.0, 174.17999267578125], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 190.89601135253906, 85.0, 206.5800018310547], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 221.38800048828125, 132.291015625, 239.01600646972656], "conf": 1.0, "text": "2025年9月20日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": []}	{"title": "转正申请书", "closing": "敬礼！", "char_count": 40, "salutation": "敬爱的党组织：", "signature_date": "2025-09-20", "signature_date_raw": "2025年9月20日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.659529+08	2026-10-17 18:36:17.65953+08
40	40	PDF_TEXT	\N	previews/f18e554521a94309a4b9456eead5e7e7.pdf	转正公示材料\n公示 2025年9月25 日至 2025年10月8 日。\n???\n??\n·····	44	[{"text": "转正公示材料\\n公示 2025年9月25 日至 2025年10月8 日。\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 121.0, 76.9800033569336], "conf": 1.0, "text": "转正公示材料"}, {"bbox": [49.0, 91.78800201416016, 277.64453125, 109.41600799560547], "conf": 1.0, "text": "公示 2025年9月25 日至 2025年10月8 日。"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "转正公示材料", "char_count": 40, "signature_date": "2025-10-08", "signature_date_raw": "2025年10月8日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.747388+08	2026-10-17 18:36:17.747389+08
41	41	PDF_TEXT	\N	previews/ad96906669af433e8932265d866b0b3e.pdf	入党申请书\n敬爱的党组织：\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\n范作用。\n此致\n敬礼！\n申请人：演示学生\n2023年3月15日\n·····	176	[{"text": "入党申请书\\n敬爱的党组织：\\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\\n范作用。\\n此致\\n敬礼！\\n申请人：演示学生\\n2023年3月15日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "入党申请书"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 124.18800354003906, 522.4375, 141.81600952148438], "conf": 1.0, "text": "我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代"}, {"bbox": [49.0, 144.58799743652344, 534.4375, 162.21600341796875], "conf": 1.0, "text": "表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心"}, {"bbox": [49.0, 166.89601135253906, 541.0, 182.5800018310547], "conf": 1.0, "text": "全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模"}, {"bbox": [49.0, 187.29600524902344, 97.0, 202.97999572753906], "conf": 1.0, "text": "范作用。"}, {"bbox": [49.0, 219.6959991455078, 73.0, 235.37998962402344], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 252.09597778320312, 85.0, 267.77996826171875], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 284.4960021972656, 145.0, 300.17999267578125], "conf": 1.0, "text": "申请人：演示学生"}, {"bbox": [49.0, 314.98797607421875, 132.291015625, 332.615966796875], "conf": 1.0, "text": "2023年3月15日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "申请人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"name": "演示学生", "title": "入党申请书", "closing": "敬礼！", "char_count": 166, "salutation": "敬爱的党组织：", "signature_date": "2023-03-15", "signature_name": "演示学生", "signature_date_raw": "2023年3月15日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.803993+08	2026-10-17 18:36:17.803994+08
44	44	PDF_TEXT	\N	previews/2f3a0e8d5b1a49ccb68fa5111a3e9ce5.pdf	思想汇报\n敬爱的党组织：\n本季度我认真学习党章，对照党员标准查找不足。\n此致\n敬礼！\n汇报人：演示学生\n2024年12月20日\n·····	69	[{"text": "思想汇报\\n敬爱的党组织：\\n本季度我认真学习党章，对照党员标准查找不足。\\n此致\\n敬礼！\\n汇报人：演示学生\\n2024年12月20日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 97.0, 76.9800033569336], "conf": 1.0, "text": "思想汇报"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 126.09600830078125, 313.0, 141.77999877929688], "conf": 1.0, "text": "本季度我认真学习党章，对照党员标准查找不足。"}, {"bbox": [49.0, 158.49600219726562, 73.0, 174.17999267578125], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 190.89601135253906, 85.0, 206.5800018310547], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 223.29600524902344, 145.0, 238.97999572753906], "conf": 1.0, "text": "汇报人：演示学生"}, {"bbox": [49.0, 253.7880096435547, 139.046875, 271.416015625], "conf": 1.0, "text": "2024年12月20日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "汇报人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"title": "思想汇报", "closing": "敬礼！", "char_count": 62, "salutation": "敬爱的党组织：", "signature_date": "2024-12-20", "signature_name": "演示学生", "signature_date_raw": "2024年12月20日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.946811+08	2026-10-17 18:36:17.946812+08
46	46	PDF_TEXT	\N	previews/fb8e39d361da452484161e8eae46cb9d.pdf	思想汇报\n敬爱的党组织：\n本季度我认真学习党章，对照党员标准查找不足。\n此致\n敬礼！\n汇报人：演示学生\n2025年7月1日\n·····	67	[{"text": "思想汇报\\n敬爱的党组织：\\n本季度我认真学习党章，对照党员标准查找不足。\\n此致\\n敬礼！\\n汇报人：演示学生\\n2025年7月1日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 97.0, 76.9800033569336], "conf": 1.0, "text": "思想汇报"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 126.09600830078125, 313.0, 141.77999877929688], "conf": 1.0, "text": "本季度我认真学习党章，对照党员标准查找不足。"}, {"bbox": [49.0, 158.49600219726562, 73.0, 174.17999267578125], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 190.89601135253906, 85.0, 206.5800018310547], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 223.29600524902344, 145.0, 238.97999572753906], "conf": 1.0, "text": "汇报人：演示学生"}, {"bbox": [49.0, 253.7880096435547, 125.53515625, 271.416015625], "conf": 1.0, "text": "2025年7月1日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "汇报人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"title": "思想汇报", "closing": "敬礼！", "char_count": 60, "salutation": "敬爱的党组织：", "signature_date": "2025-07-01", "signature_name": "演示学生", "signature_date_raw": "2025年7月1日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:18.037954+08	2026-10-17 18:36:18.037955+08
48	48	PDF_TEXT	\N	previews/4e9020ee7d0b412bb2744e635353a8c0.pdf	自传\n我叫演示学生，出生日期 2003年5月12日。家庭主要成员有父亲、母亲。成长经历方面，我从\n小学起接受集体主义教育。思想演变上，我逐步认识到中国共产党是中国工人阶级的先锋队，\n全心全意为人民服务。\n认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认\n识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识\n深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。\n·····	516	[{"text": "自传\\n我叫演示学生，出生日期 2003年5月12日。家庭主要成员有父亲、母亲。成长经历方面，我从\\n小学起接受集体主义教育。思想演变上，我逐步认识到中国共产党是中国工人阶级的先锋队，\\n全心全意为人民服务。\\n认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认\\n识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识\\n深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 73.0, 76.9800033569336], "conf": 1.0, "text": "自传"}, {"bbox": [49.0, 91.78800201416016, 543.806640625, 109.41600799560547], "conf": 1.0, "text": "我叫演示学生，出生日期 2003年5月12日。家庭主要成员有父亲、母亲。成长经历方面，我从"}, {"bbox": [49.0, 114.09600830078125, 541.0, 129.77999877929688], "conf": 1.0, "text": "小学起接受集体主义教育。思想演变上，我逐步认识到中国共产党是中国工人阶级的先锋队，"}, {"bbox": [49.0, 134.49600219726562, 169.0, 150.17999267578125], "conf": 1.0, "text": "全心全意为人民服务。"}, {"bbox": [49.0, 166.89601135253906, 541.0, 182.5800018310547], "conf": 1.0, "text": "认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认"}, {"bbox": [49.0, 187.29600524902344, 541.0, 202.97999572753906], "conf": 1.0, "text": "识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识"}, {"bbox": [49.0, 207.6959991455078, 541.0, 223.37998962402344], "conf": 1.0, "text": "深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 228.0959930419922, 529.0, 243.7799835205078], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 248.49600219726562, 529.0, 264.17999267578125], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 268.8959655761719, 529.0, 284.5799560546875], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 289.2959899902344, 529.0, 304.97998046875], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 309.6959533691406, 529.0, 325.37994384765625], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 330.095947265625, 529.0, 345.7799377441406], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 350.4959411621094, 493.0, 366.179931640625], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": []}	{"title": "自传", "birth_date": "2003-05-12", "char_count": 502, "signature_date": "2003-05-12", "signature_date_raw": "2003年5月12日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:18.126056+08	2026-10-17 18:36:18.126057+08
49	49	PDF_TEXT	\N	previews/58bd8219b2734a1cad24de7929fbec5c.pdf	入党申请书\n敬爱的党组织：\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\n全意为人民服务的宗旨。我的入党动机是入党可以评优评奖，也为了好找工作，在学习和工作\n中发挥先锋模范作用。\n此致\n敬礼！\n申请人：演示学生\n2023年3月15日\n·····	182	[{"text": "入党申请书\\n敬爱的党组织：\\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\\n全意为人民服务的宗旨。我的入党动机是入党可以评优评奖，也为了好找工作，在学习和工作\\n中发挥先锋模范作用。\\n此致\\n敬礼！\\n申请人：演示学生\\n2023年3月15日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "入党申请书"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 124.18800354003906, 522.4375, 141.81600952148438], "conf": 1.0, "text": "我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代"}, {"bbox": [49.0, 144.58799743652344, 534.4375, 162.21600341796875], "conf": 1.0, "text": "表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心"}, {"bbox": [49.0, 166.89601135253906, 541.0, 182.5800018310547], "conf": 1.0, "text": "全意为人民服务的宗旨。我的入党动机是入党可以评优评奖，也为了好找工作，在学习和工作"}, {"bbox": [49.0, 187.29600524902344, 169.0, 202.97999572753906], "conf": 1.0, "text": "中发挥先锋模范作用。"}, {"bbox": [49.0, 219.6959991455078, 73.0, 235.37998962402344], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 252.09597778320312, 85.0, 267.77996826171875], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 284.4960021972656, 145.0, 300.17999267578125], "conf": 1.0, "text": "申请人：演示学生"}, {"bbox": [49.0, 314.98797607421875, 132.291015625, 332.615966796875], "conf": 1.0, "text": "2023年3月15日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "申请人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"name": "演示学生", "title": "入党申请书", "closing": "敬礼！", "char_count": 172, "salutation": "敬爱的党组织：", "signature_date": "2023-03-15", "signature_name": "演示学生", "signature_date_raw": "2023年3月15日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:18.183113+08	2026-10-17 18:36:18.183114+08
50	50	PDF_TEXT	\N	previews/d1cb6c02c545474ba3ef8185dddffa3e.pdf	自传\n我叫演示学生，出生日期 2004年1月1日。我热爱学习。\n签名\n·····	39	[{"text": "自传\\n我叫演示学生，出生日期 2004年1月1日。我热爱学习。\\n签名\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 73.0, 76.9800033569336], "conf": 1.0, "text": "自传"}, {"bbox": [49.0, 91.78800201416016, 345.05078125, 109.41600799560547], "conf": 1.0, "text": "我叫演示学生，出生日期 2004年1月1日。我热爱学习。"}, {"bbox": [49.0, 126.09600830078125, 73.0, 141.77999877929688], "conf": 1.0, "text": "签名"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "签名", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"title": "自传", "birth_date": "2004-01-01", "char_count": 36, "signature_date": "2004-01-01", "signature_date_raw": "2004年1月1日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:18.232999+08	2026-10-17 18:36:18.233+08
45	45	PDF_TEXT	\N	previews/f09b1b68bde44a258127558c2278b7d6.pdf	思想汇报\n敬爱的党组织：\n本季度我认真学习党章，对照党员标准查找不足。\n此致\n敬礼！\n汇报人：演示学生\n2025年3月25日\n·····	68	[{"text": "思想汇报\\n敬爱的党组织：\\n本季度我认真学习党章，对照党员标准查找不足。\\n此致\\n敬礼！\\n汇报人：演示学生\\n2025年3月25日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 97.0, 76.9800033569336], "conf": 1.0, "text": "思想汇报"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 126.09600830078125, 313.0, 141.77999877929688], "conf": 1.0, "text": "本季度我认真学习党章，对照党员标准查找不足。"}, {"bbox": [49.0, 158.49600219726562, 73.0, 174.17999267578125], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 190.89601135253906, 85.0, 206.5800018310547], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 223.29600524902344, 145.0, 238.97999572753906], "conf": 1.0, "text": "汇报人：演示学生"}, {"bbox": [49.0, 253.7880096435547, 132.291015625, 271.416015625], "conf": 1.0, "text": "2025年3月25日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "汇报人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"title": "思想汇报", "closing": "敬礼！", "char_count": 61, "salutation": "敬爱的党组织：", "signature_date": "2025-03-25", "signature_name": "演示学生", "signature_date_raw": "2025年3月25日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:17.992255+08	2026-10-17 18:36:17.992256+08
47	47	PDF_TEXT	\N	previews/2bc8bbe39a54403893e48a567821fc40.pdf	支委会确定发展对象记录\n经讨论，确定该同志为发展对象。\n2025年8月30日\n???\n??\n·····	51	[{"text": "支委会确定发展对象记录\\n经讨论，确定该同志为发展对象。\\n2025年8月30日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 181.0, 76.9800033569336], "conf": 1.0, "text": "支委会确定发展对象记录"}, {"bbox": [49.0, 93.69600677490234, 229.0, 109.3800048828125], "conf": 1.0, "text": "经讨论，确定该同志为发展对象。"}, {"bbox": [49.0, 124.18800354003906, 132.291015625, 141.81600952148438], "conf": 1.0, "text": "2025年8月30日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "支委会确定发展对象记录", "char_count": 46, "signature_date": "2025-08-30", "signature_date_raw": "2025年8月30日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:18.080374+08	2026-10-17 18:36:18.080376+08
53	53	PDF_TEXT	\N	previews/d7879387a99a4e2e98b2693d16c95bd6.pdf	入党志愿书\n姓名 演示学生 出生日期 2003年5月12日\n2025年5月20日\n???\n??\n·····	50	[{"text": "入党志愿书\\n姓名 演示学生 出生日期 2003年5月12日\\n2025年5月20日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "入党志愿书"}, {"bbox": [49.0, 91.78800201416016, 262.837890625, 109.41600799560547], "conf": 1.0, "text": "姓名 演示学生 出生日期 2003年5月12日"}, {"bbox": [49.0, 124.18800354003906, 132.291015625, 141.81600952148438], "conf": 1.0, "text": "2025年5月20日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"name": "演示学生", "title": "入党志愿书", "birth_date": "2003-05-12", "char_count": 45, "signature_date": "2025-05-20", "signature_date_raw": "2025年5月20日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:18.368976+08	2026-10-17 18:36:18.368977+08
55	55	PDF_TEXT	\N	previews/fc182e9d95294bdbaf17b5da80b03041.pdf	政治审查材料\n政审合格。\n2024年6月1日\n???\n??\n·····	35	[{"text": "政治审查材料\\n政审合格。\\n2024年6月1日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 121.0, 76.9800033569336], "conf": 1.0, "text": "政治审查材料"}, {"bbox": [49.0, 93.69600677490234, 109.0, 109.3800048828125], "conf": 1.0, "text": "政审合格。"}, {"bbox": [49.0, 124.18800354003906, 125.53515625, 141.81600952148438], "conf": 1.0, "text": "2024年6月1日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "政治审查材料", "char_count": 30, "signature_date": "2024-06-01", "signature_date_raw": "2024年6月1日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:18.459119+08	2026-10-17 18:36:18.45912+08
57	57	PDF_TEXT	\N	previews/02a2d2236cd64edd9b2f00565e70617f.pdf	发展对象公示材料\n公示自 2025年4月20 日至 2025年4月26 日。\n???\n??\n·····	47	[{"text": "发展对象公示材料\\n公示自 2025年4月20 日至 2025年4月26 日。\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 145.0, 76.9800033569336], "conf": 1.0, "text": "发展对象公示材料"}, {"bbox": [49.0, 91.78800201416016, 289.64453125, 109.41600799560547], "conf": 1.0, "text": "公示自 2025年4月20 日至 2025年4月26 日。"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "发展对象公示材料", "char_count": 43, "signature_date": "2025-04-26", "signature_date_raw": "2025年4月26日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:18.549483+08	2026-10-17 18:36:18.549484+08
60	60	PDF_TEXT	\N	previews/3fbecdc0d7f64d2f86f6578eaac409d7.pdf	支部大会讨论转正记录\n2025年10月8日\n???\n??\n·····	34	[{"text": "支部大会讨论转正记录\\n2025年10月8日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 169.0, 76.9800033569336], "conf": 1.0, "text": "支部大会讨论转正记录"}, {"bbox": [49.0, 91.78800201416016, 132.291015625, 109.41600799560547], "conf": 1.0, "text": "2025年10月8日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "支部大会讨论转正记录", "char_count": 30, "signature_date": "2025-10-08", "signature_date_raw": "2025年10月8日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:18.689657+08	2026-10-17 18:36:18.689659+08
70	70	PDF_TEXT	\N	previews/a4d0f9bd45334fc9a2a2f50202304019.pdf	入党申请书\n敬爱的党组织：\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\n全意为人民服务的宗旨。我的入党动机是入党可以评优评奖，也为了好找工作，在学习和工作\n中发挥先锋模范作用。\n此致\n敬礼！\n申请人：演示学生\n2023年3月15日\n·····	182	[{"text": "入党申请书\\n敬爱的党组织：\\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\\n全意为人民服务的宗旨。我的入党动机是入党可以评优评奖，也为了好找工作，在学习和工作\\n中发挥先锋模范作用。\\n此致\\n敬礼！\\n申请人：演示学生\\n2023年3月15日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "入党申请书"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 124.18800354003906, 522.4375, 141.81600952148438], "conf": 1.0, "text": "我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代"}, {"bbox": [49.0, 144.58799743652344, 534.4375, 162.21600341796875], "conf": 1.0, "text": "表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心"}, {"bbox": [49.0, 166.89601135253906, 541.0, 182.5800018310547], "conf": 1.0, "text": "全意为人民服务的宗旨。我的入党动机是入党可以评优评奖，也为了好找工作，在学习和工作"}, {"bbox": [49.0, 187.29600524902344, 169.0, 202.97999572753906], "conf": 1.0, "text": "中发挥先锋模范作用。"}, {"bbox": [49.0, 219.6959991455078, 73.0, 235.37998962402344], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 252.09597778320312, 85.0, 267.77996826171875], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 284.4960021972656, 145.0, 300.17999267578125], "conf": 1.0, "text": "申请人：演示学生"}, {"bbox": [49.0, 314.98797607421875, 132.291015625, 332.615966796875], "conf": 1.0, "text": "2023年3月15日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "申请人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"name": "演示学生", "title": "入党申请书", "closing": "敬礼！", "char_count": 172, "salutation": "敬爱的党组织：", "signature_date": "2023-03-15", "signature_name": "演示学生", "signature_date_raw": "2023年3月15日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:19.164133+08	2026-10-17 18:36:19.164134+08
54	54	PDF_TEXT	\N	previews/a305e2df98664b97997b38c1c831d205.pdf	支部大会讨论接收预备党员记录\n2025年6月1日\n???\n??\n·····	37	[{"text": "支部大会讨论接收预备党员记录\\n2025年6月1日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 217.0, 76.9800033569336], "conf": 1.0, "text": "支部大会讨论接收预备党员记录"}, {"bbox": [49.0, 91.78800201416016, 125.53515625, 109.41600799560547], "conf": 1.0, "text": "2025年6月1日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "支部大会讨论接收预备党员记录", "char_count": 33, "signature_date": "2025-06-01", "signature_date_raw": "2025年6月1日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:18.415654+08	2026-10-17 18:36:18.415655+08
56	56	PDF_TEXT	\N	previews/aed8693f44934aeaa9d1f20c27a840fc.pdf	集中培训结业证书\n培训时间 2024年7月1日至2024年7月5日，学时 24。\n???\n??\n·····	51	[{"text": "集中培训结业证书\\n培训时间 2024年7月1日至2024年7月5日，学时 24。\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 145.0, 76.9800033569336], "conf": 1.0, "text": "集中培训结业证书"}, {"bbox": [49.0, 91.78800201416016, 330.61328125, 109.41600799560547], "conf": 1.0, "text": "培训时间 2024年7月1日至2024年7月5日，学时 24。"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "集中培训结业证书", "char_count": 47, "signature_date": "2024-07-05", "signature_date_raw": "2024年7月5日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:18.502543+08	2026-10-17 18:36:18.502544+08
58	58	PDF_TEXT	\N	previews/bfa4cda2c4a14580b4ea75a26b0783bf.pdf	上级党委预审意见\n同意。\n2025年5月10日\n???\n??\n·····	36	[{"text": "上级党委预审意见\\n同意。\\n2025年5月10日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 145.0, 76.9800033569336], "conf": 1.0, "text": "上级党委预审意见"}, {"bbox": [49.0, 93.69600677490234, 85.0, 109.3800048828125], "conf": 1.0, "text": "同意。"}, {"bbox": [49.0, 124.18800354003906, 132.291015625, 141.81600952148438], "conf": 1.0, "text": "2025年5月10日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "上级党委预审意见", "char_count": 31, "signature_date": "2025-05-10", "signature_date_raw": "2025年5月10日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:18.592677+08	2026-10-17 18:36:18.592678+08
59	59	PDF_TEXT	\N	previews/c753de1145c2475dbb620f7d54fe8550.pdf	转正申请书\n敬爱的党组织：\n我志愿按期转正。\n此致\n敬礼！\n2025年9月20日\n·····	46	[{"text": "转正申请书\\n敬爱的党组织：\\n我志愿按期转正。\\n此致\\n敬礼！\\n2025年9月20日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "转正申请书"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 126.09600830078125, 145.0, 141.77999877929688], "conf": 1.0, "text": "我志愿按期转正。"}, {"bbox": [49.0, 158.49600219726562, 73.0, 174.17999267578125], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 190.89601135253906, 85.0, 206.5800018310547], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 221.38800048828125, 132.291015625, 239.01600646972656], "conf": 1.0, "text": "2025年9月20日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": []}	{"title": "转正申请书", "closing": "敬礼！", "char_count": 40, "salutation": "敬爱的党组织：", "signature_date": "2025-09-20", "signature_date_raw": "2025年9月20日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:18.645945+08	2026-10-17 18:36:18.645946+08
61	61	PDF_TEXT	\N	previews/2ccb8111e616434c899f16d425c42af6.pdf	转正公示材料\n公示 2025年9月25 日至 2025年10月8 日。\n???\n??\n·····	44	[{"text": "转正公示材料\\n公示 2025年9月25 日至 2025年10月8 日。\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 121.0, 76.9800033569336], "conf": 1.0, "text": "转正公示材料"}, {"bbox": [49.0, 91.78800201416016, 277.64453125, 109.41600799560547], "conf": 1.0, "text": "公示 2025年9月25 日至 2025年10月8 日。"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "转正公示材料", "char_count": 40, "signature_date": "2025-10-08", "signature_date_raw": "2025年10月8日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:18.731849+08	2026-10-17 18:36:18.73185+08
62	62	PDF_TEXT	\N	previews/c460a5667b75489baf9d70c74e227c14.pdf	入党申请书\n敬爱的党组织：\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\n范作用。\n此致\n敬礼！\n申请人：演示学生\n2023年3月15日\n·····	176	[{"text": "入党申请书\\n敬爱的党组织：\\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\\n范作用。\\n此致\\n敬礼！\\n申请人：演示学生\\n2023年3月15日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "入党申请书"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 124.18800354003906, 522.4375, 141.81600952148438], "conf": 1.0, "text": "我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代"}, {"bbox": [49.0, 144.58799743652344, 534.4375, 162.21600341796875], "conf": 1.0, "text": "表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心"}, {"bbox": [49.0, 166.89601135253906, 541.0, 182.5800018310547], "conf": 1.0, "text": "全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模"}, {"bbox": [49.0, 187.29600524902344, 97.0, 202.97999572753906], "conf": 1.0, "text": "范作用。"}, {"bbox": [49.0, 219.6959991455078, 73.0, 235.37998962402344], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 252.09597778320312, 85.0, 267.77996826171875], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 284.4960021972656, 145.0, 300.17999267578125], "conf": 1.0, "text": "申请人：演示学生"}, {"bbox": [49.0, 314.98797607421875, 132.291015625, 332.615966796875], "conf": 1.0, "text": "2023年3月15日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "申请人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"name": "演示学生", "title": "入党申请书", "closing": "敬礼！", "char_count": 166, "salutation": "敬爱的党组织：", "signature_date": "2023-03-15", "signature_name": "演示学生", "signature_date_raw": "2023年3月15日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:18.789041+08	2026-10-17 18:36:18.789042+08
65	65	PDF_TEXT	\N	previews/64a1f15b70f6482a8dbc361d879f08db.pdf	思想汇报\n敬爱的党组织：\n本季度我认真学习党章，对照党员标准查找不足。\n此致\n敬礼！\n汇报人：演示学生\n2024年12月20日\n·····	69	[{"text": "思想汇报\\n敬爱的党组织：\\n本季度我认真学习党章，对照党员标准查找不足。\\n此致\\n敬礼！\\n汇报人：演示学生\\n2024年12月20日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 97.0, 76.9800033569336], "conf": 1.0, "text": "思想汇报"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 126.09600830078125, 313.0, 141.77999877929688], "conf": 1.0, "text": "本季度我认真学习党章，对照党员标准查找不足。"}, {"bbox": [49.0, 158.49600219726562, 73.0, 174.17999267578125], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 190.89601135253906, 85.0, 206.5800018310547], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 223.29600524902344, 145.0, 238.97999572753906], "conf": 1.0, "text": "汇报人：演示学生"}, {"bbox": [49.0, 253.7880096435547, 139.046875, 271.416015625], "conf": 1.0, "text": "2024年12月20日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "汇报人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"title": "思想汇报", "closing": "敬礼！", "char_count": 62, "salutation": "敬爱的党组织：", "signature_date": "2024-12-20", "signature_name": "演示学生", "signature_date_raw": "2024年12月20日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:18.933742+08	2026-10-17 18:36:18.933743+08
67	67	PDF_TEXT	\N	previews/57bb9e1e4890461ebec4c18a6fd51457.pdf	思想汇报\n敬爱的党组织：\n本季度我认真学习党章，对照党员标准查找不足。\n此致\n敬礼！\n汇报人：演示学生\n2025年7月1日\n·····	67	[{"text": "思想汇报\\n敬爱的党组织：\\n本季度我认真学习党章，对照党员标准查找不足。\\n此致\\n敬礼！\\n汇报人：演示学生\\n2025年7月1日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 97.0, 76.9800033569336], "conf": 1.0, "text": "思想汇报"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 126.09600830078125, 313.0, 141.77999877929688], "conf": 1.0, "text": "本季度我认真学习党章，对照党员标准查找不足。"}, {"bbox": [49.0, 158.49600219726562, 73.0, 174.17999267578125], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 190.89601135253906, 85.0, 206.5800018310547], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 223.29600524902344, 145.0, 238.97999572753906], "conf": 1.0, "text": "汇报人：演示学生"}, {"bbox": [49.0, 253.7880096435547, 125.53515625, 271.416015625], "conf": 1.0, "text": "2025年7月1日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "汇报人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"title": "思想汇报", "closing": "敬礼！", "char_count": 60, "salutation": "敬爱的党组织：", "signature_date": "2025-07-01", "signature_name": "演示学生", "signature_date_raw": "2025年7月1日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:19.019159+08	2026-10-17 18:36:19.019161+08
69	69	PDF_TEXT	\N	previews/d0244d767d554219a944dcc13b68e865.pdf	自传\n我叫演示学生，出生日期 2003年5月12日。家庭主要成员有父亲、母亲。成长经历方面，我从\n小学起接受集体主义教育。思想演变上，我逐步认识到中国共产党是中国工人阶级的先锋队，\n全心全意为人民服务。\n认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认\n识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识\n深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。\n·····	516	[{"text": "自传\\n我叫演示学生，出生日期 2003年5月12日。家庭主要成员有父亲、母亲。成长经历方面，我从\\n小学起接受集体主义教育。思想演变上，我逐步认识到中国共产党是中国工人阶级的先锋队，\\n全心全意为人民服务。\\n认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认\\n识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识\\n深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深\\n化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 73.0, 76.9800033569336], "conf": 1.0, "text": "自传"}, {"bbox": [49.0, 91.78800201416016, 543.806640625, 109.41600799560547], "conf": 1.0, "text": "我叫演示学生，出生日期 2003年5月12日。家庭主要成员有父亲、母亲。成长经历方面，我从"}, {"bbox": [49.0, 114.09600830078125, 541.0, 129.77999877929688], "conf": 1.0, "text": "小学起接受集体主义教育。思想演变上，我逐步认识到中国共产党是中国工人阶级的先锋队，"}, {"bbox": [49.0, 134.49600219726562, 169.0, 150.17999267578125], "conf": 1.0, "text": "全心全意为人民服务。"}, {"bbox": [49.0, 166.89601135253906, 541.0, 182.5800018310547], "conf": 1.0, "text": "认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认"}, {"bbox": [49.0, 187.29600524902344, 541.0, 202.97999572753906], "conf": 1.0, "text": "识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识"}, {"bbox": [49.0, 207.6959991455078, 541.0, 223.37998962402344], "conf": 1.0, "text": "深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 228.0959930419922, 529.0, 243.7799835205078], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 248.49600219726562, 529.0, 264.17999267578125], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 268.8959655761719, 529.0, 284.5799560546875], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 289.2959899902344, 529.0, 304.97998046875], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 309.6959533691406, 529.0, 325.37994384765625], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 330.095947265625, 529.0, 345.7799377441406], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深"}, {"bbox": [49.0, 350.4959411621094, 493.0, 366.179931640625], "conf": 1.0, "text": "化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。认识深化。"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": []}	{"title": "自传", "birth_date": "2003-05-12", "char_count": 502, "signature_date": "2003-05-12", "signature_date_raw": "2003年5月12日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:19.105452+08	2026-10-17 18:36:19.105452+08
63	63	PDF_TEXT	\N	previews/e3db237c1154444b935798e9a4ea727d.pdf	党组织派人谈话记录\n谈话人已谈话。\n2023年3月28日\n???\n??\n·····	41	[{"text": "党组织派人谈话记录\\n谈话人已谈话。\\n2023年3月28日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 157.0, 76.9800033569336], "conf": 1.0, "text": "党组织派人谈话记录"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "谈话人已谈话。"}, {"bbox": [49.0, 124.18800354003906, 132.291015625, 141.81600952148438], "conf": 1.0, "text": "2023年3月28日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "党组织派人谈话记录", "char_count": 36, "salutation": "党组织派人谈话记录", "signature_date": "2023-03-28", "signature_date_raw": "2023年3月28日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:18.831316+08	2026-10-17 18:36:18.831317+08
64	64	PDF_TEXT	\N	previews/2e4a786c61e841578163e4ca3014f934.pdf	入党申请书\n敬爱的党组织：\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\n范作用。\n此致\n敬礼！\n申请人：演示学生\n2023年3月15日\n·····	176	[{"text": "入党申请书\\n敬爱的党组织：\\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\\n范作用。\\n此致\\n敬礼！\\n申请人：演示学生\\n2023年3月15日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "入党申请书"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 124.18800354003906, 522.4375, 141.81600952148438], "conf": 1.0, "text": "我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代"}, {"bbox": [49.0, 144.58799743652344, 534.4375, 162.21600341796875], "conf": 1.0, "text": "表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心"}, {"bbox": [49.0, 166.89601135253906, 541.0, 182.5800018310547], "conf": 1.0, "text": "全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模"}, {"bbox": [49.0, 187.29600524902344, 97.0, 202.97999572753906], "conf": 1.0, "text": "范作用。"}, {"bbox": [49.0, 219.6959991455078, 73.0, 235.37998962402344], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 252.09597778320312, 85.0, 267.77996826171875], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 284.4960021972656, 145.0, 300.17999267578125], "conf": 1.0, "text": "申请人：演示学生"}, {"bbox": [49.0, 314.98797607421875, 132.291015625, 332.615966796875], "conf": 1.0, "text": "2023年3月15日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "申请人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"name": "演示学生", "title": "入党申请书", "closing": "敬礼！", "char_count": 166, "salutation": "敬爱的党组织：", "signature_date": "2023-03-15", "signature_name": "演示学生", "signature_date_raw": "2023年3月15日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:18.888238+08	2026-10-17 18:36:18.888239+08
66	66	PDF_TEXT	\N	previews/628837057a1a4956a1cb6160782c285e.pdf	思想汇报\n敬爱的党组织：\n本季度我认真学习党章，对照党员标准查找不足。\n此致\n敬礼！\n汇报人：演示学生\n2025年3月25日\n·····	68	[{"text": "思想汇报\\n敬爱的党组织：\\n本季度我认真学习党章，对照党员标准查找不足。\\n此致\\n敬礼！\\n汇报人：演示学生\\n2025年3月25日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 97.0, 76.9800033569336], "conf": 1.0, "text": "思想汇报"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 126.09600830078125, 313.0, 141.77999877929688], "conf": 1.0, "text": "本季度我认真学习党章，对照党员标准查找不足。"}, {"bbox": [49.0, 158.49600219726562, 73.0, 174.17999267578125], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 190.89601135253906, 85.0, 206.5800018310547], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 223.29600524902344, 145.0, 238.97999572753906], "conf": 1.0, "text": "汇报人：演示学生"}, {"bbox": [49.0, 253.7880096435547, 132.291015625, 271.416015625], "conf": 1.0, "text": "2025年3月25日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "汇报人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"title": "思想汇报", "closing": "敬礼！", "char_count": 61, "salutation": "敬爱的党组织：", "signature_date": "2025-03-25", "signature_name": "演示学生", "signature_date_raw": "2025年3月25日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:18.975044+08	2026-10-17 18:36:18.975045+08
68	68	PDF_TEXT	\N	previews/d69170641663457b9487a68f87d52244.pdf	支委会确定发展对象记录\n经讨论，确定该同志为发展对象。\n2025年8月30日\n???\n??\n·····	51	[{"text": "支委会确定发展对象记录\\n经讨论，确定该同志为发展对象。\\n2025年8月30日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 181.0, 76.9800033569336], "conf": 1.0, "text": "支委会确定发展对象记录"}, {"bbox": [49.0, 93.69600677490234, 229.0, 109.3800048828125], "conf": 1.0, "text": "经讨论，确定该同志为发展对象。"}, {"bbox": [49.0, 124.18800354003906, 132.291015625, 141.81600952148438], "conf": 1.0, "text": "2025年8月30日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "支委会确定发展对象记录", "char_count": 46, "signature_date": "2025-08-30", "signature_date_raw": "2025年8月30日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:19.06144+08	2026-10-17 18:36:19.061442+08
71	71	PDF_TEXT	\N	previews/84ed58e5dff843d29eaa62a21c53fb2e.pdf	自传\n我叫演示学生，出生日期 2004年1月1日。我热爱学习。\n签名\n·····	39	[{"text": "自传\\n我叫演示学生，出生日期 2004年1月1日。我热爱学习。\\n签名\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 73.0, 76.9800033569336], "conf": 1.0, "text": "自传"}, {"bbox": [49.0, 91.78800201416016, 345.05078125, 109.41600799560547], "conf": 1.0, "text": "我叫演示学生，出生日期 2004年1月1日。我热爱学习。"}, {"bbox": [49.0, 126.09600830078125, 73.0, 141.77999877929688], "conf": 1.0, "text": "签名"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "签名", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"title": "自传", "birth_date": "2004-01-01", "char_count": 36, "signature_date": "2004-01-01", "signature_date_raw": "2004年1月1日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:19.211246+08	2026-10-17 18:36:19.211248+08
72	72	PDF_TEXT	\N	previews/c185a52a216240d8aa44adf5f80b649a.pdf	思想汇报\n敬爱的党组织：\n本季度我认真学习党章，对照党员标准查找不足。\n此致\n敬礼！\n汇报人：演示学生\n2025年8月1日\n·····	67	[{"text": "思想汇报\\n敬爱的党组织：\\n本季度我认真学习党章，对照党员标准查找不足。\\n此致\\n敬礼！\\n汇报人：演示学生\\n2025年8月1日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 97.0, 76.9800033569336], "conf": 1.0, "text": "思想汇报"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 126.09600830078125, 313.0, 141.77999877929688], "conf": 1.0, "text": "本季度我认真学习党章，对照党员标准查找不足。"}, {"bbox": [49.0, 158.49600219726562, 73.0, 174.17999267578125], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 190.89601135253906, 85.0, 206.5800018310547], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 223.29600524902344, 145.0, 238.97999572753906], "conf": 1.0, "text": "汇报人：演示学生"}, {"bbox": [49.0, 253.7880096435547, 125.53515625, 271.416015625], "conf": 1.0, "text": "2025年8月1日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "汇报人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"title": "思想汇报", "closing": "敬礼！", "char_count": 60, "salutation": "敬爱的党组织：", "signature_date": "2025-08-01", "signature_name": "演示学生", "signature_date_raw": "2025年8月1日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:19.25463+08	2026-10-17 18:36:19.254631+08
73	73	PDF_TEXT	\N	previews/90e0e307bf854b87b377bef2afe4d79c.pdf	入党申请书\n敬爱的党组织：\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\n范作用。\n此致\n敬礼！\n申请人：演示学生\n2023年3月15日\n·····	176	[{"text": "入党申请书\\n敬爱的党组织：\\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\\n范作用。\\n此致\\n敬礼！\\n申请人：演示学生\\n2023年3月15日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "入党申请书"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 124.18800354003906, 522.4375, 141.81600952148438], "conf": 1.0, "text": "我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代"}, {"bbox": [49.0, 144.58799743652344, 534.4375, 162.21600341796875], "conf": 1.0, "text": "表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心"}, {"bbox": [49.0, 166.89601135253906, 541.0, 182.5800018310547], "conf": 1.0, "text": "全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模"}, {"bbox": [49.0, 187.29600524902344, 97.0, 202.97999572753906], "conf": 1.0, "text": "范作用。"}, {"bbox": [49.0, 219.6959991455078, 73.0, 235.37998962402344], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 252.09597778320312, 85.0, 267.77996826171875], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 284.4960021972656, 145.0, 300.17999267578125], "conf": 1.0, "text": "申请人：演示学生"}, {"bbox": [49.0, 314.98797607421875, 132.291015625, 332.615966796875], "conf": 1.0, "text": "2023年3月15日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "申请人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"name": "演示学生", "title": "入党申请书", "closing": "敬礼！", "char_count": 166, "salutation": "敬爱的党组织：", "signature_date": "2023-03-15", "signature_name": "演示学生", "signature_date_raw": "2023年3月15日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:19.314928+08	2026-10-17 18:36:19.314929+08
75	75	PDF_TEXT	\N	previews/fc63945d3f2940539915cc334215910a.pdf	支部大会讨论接收预备党员记录\n2025年6月1日\n???\n??\n·····	37	[{"text": "支部大会讨论接收预备党员记录\\n2025年6月1日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 217.0, 76.9800033569336], "conf": 1.0, "text": "支部大会讨论接收预备党员记录"}, {"bbox": [49.0, 91.78800201416016, 125.53515625, 109.41600799560547], "conf": 1.0, "text": "2025年6月1日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "支部大会讨论接收预备党员记录", "char_count": 33, "signature_date": "2025-06-01", "signature_date_raw": "2025年6月1日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:19.405083+08	2026-10-17 18:36:19.405084+08
77	77	PDF_TEXT	\N	previews/2f98f718719d48a4ac56dcd7a41599cc.pdf	集中培训结业证书\n培训时间 2024年7月1日至2024年7月5日，学时 24。\n???\n??\n·····	51	[{"text": "集中培训结业证书\\n培训时间 2024年7月1日至2024年7月5日，学时 24。\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 145.0, 76.9800033569336], "conf": 1.0, "text": "集中培训结业证书"}, {"bbox": [49.0, 91.78800201416016, 330.61328125, 109.41600799560547], "conf": 1.0, "text": "培训时间 2024年7月1日至2024年7月5日，学时 24。"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "集中培训结业证书", "char_count": 47, "signature_date": "2024-07-05", "signature_date_raw": "2024年7月5日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:19.493818+08	2026-10-17 18:36:19.493819+08
79	79	PDF_TEXT	\N	previews/259f40b20e02444db4adb38d6c5f8424.pdf	上级党委预审意见\n同意。\n2025年5月10日\n???\n??\n·····	36	[{"text": "上级党委预审意见\\n同意。\\n2025年5月10日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 145.0, 76.9800033569336], "conf": 1.0, "text": "上级党委预审意见"}, {"bbox": [49.0, 93.69600677490234, 85.0, 109.3800048828125], "conf": 1.0, "text": "同意。"}, {"bbox": [49.0, 124.18800354003906, 132.291015625, 141.81600952148438], "conf": 1.0, "text": "2025年5月10日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "上级党委预审意见", "char_count": 31, "signature_date": "2025-05-10", "signature_date_raw": "2025年5月10日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:19.583223+08	2026-10-17 18:36:19.583224+08
74	74	PDF_TEXT	\N	previews/af9660e438cb431dacfebac6812b0e2d.pdf	入党志愿书\n姓名 演示学生 出生日期 2003年5月12日\n2025年5月20日\n???\n??\n·····	50	[{"text": "入党志愿书\\n姓名 演示学生 出生日期 2003年5月12日\\n2025年5月20日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "入党志愿书"}, {"bbox": [49.0, 91.78800201416016, 262.837890625, 109.41600799560547], "conf": 1.0, "text": "姓名 演示学生 出生日期 2003年5月12日"}, {"bbox": [49.0, 124.18800354003906, 132.291015625, 141.81600952148438], "conf": 1.0, "text": "2025年5月20日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"name": "演示学生", "title": "入党志愿书", "birth_date": "2003-05-12", "char_count": 45, "signature_date": "2025-05-20", "signature_date_raw": "2025年5月20日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:19.359526+08	2026-10-17 18:36:19.359528+08
76	76	PDF_TEXT	\N	previews/369c3727e59449ccb2f6ccbb429f2e18.pdf	政治审查材料\n政审合格。\n2024年6月1日\n???\n??\n·····	35	[{"text": "政治审查材料\\n政审合格。\\n2024年6月1日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 121.0, 76.9800033569336], "conf": 1.0, "text": "政治审查材料"}, {"bbox": [49.0, 93.69600677490234, 109.0, 109.3800048828125], "conf": 1.0, "text": "政审合格。"}, {"bbox": [49.0, 124.18800354003906, 125.53515625, 141.81600952148438], "conf": 1.0, "text": "2024年6月1日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "政治审查材料", "char_count": 30, "signature_date": "2024-06-01", "signature_date_raw": "2024年6月1日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:19.448806+08	2026-10-17 18:36:19.448807+08
78	78	PDF_TEXT	\N	previews/e47f1c04745b419c867f8db3193d4aa3.pdf	发展对象公示材料\n公示自 2025年4月20 日至 2025年4月26 日。\n???\n??\n·····	47	[{"text": "发展对象公示材料\\n公示自 2025年4月20 日至 2025年4月26 日。\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 145.0, 76.9800033569336], "conf": 1.0, "text": "发展对象公示材料"}, {"bbox": [49.0, 91.78800201416016, 289.64453125, 109.41600799560547], "conf": 1.0, "text": "公示自 2025年4月20 日至 2025年4月26 日。"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "发展对象公示材料", "char_count": 43, "signature_date": "2025-04-26", "signature_date_raw": "2025年4月26日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:19.537911+08	2026-10-17 18:36:19.537912+08
81	81	PDF_TEXT	\N	previews/18928f4ca46441e1a1cd2087c6c33188.pdf	支部大会讨论转正记录\n2025年10月8日\n???\n??\n·····	34	[{"text": "支部大会讨论转正记录\\n2025年10月8日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 169.0, 76.9800033569336], "conf": 1.0, "text": "支部大会讨论转正记录"}, {"bbox": [49.0, 91.78800201416016, 132.291015625, 109.41600799560547], "conf": 1.0, "text": "2025年10月8日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "支部大会讨论转正记录", "char_count": 30, "signature_date": "2025-10-08", "signature_date_raw": "2025年10月8日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:19.687212+08	2026-10-17 18:36:19.687213+08
80	80	PDF_TEXT	\N	previews/e2208f5e972b4ea198726f4842c32a02.pdf	转正申请书\n敬爱的党组织：\n我志愿按期转正。\n此致\n敬礼！\n2025年9月20日\n·····	46	[{"text": "转正申请书\\n敬爱的党组织：\\n我志愿按期转正。\\n此致\\n敬礼！\\n2025年9月20日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "转正申请书"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 126.09600830078125, 145.0, 141.77999877929688], "conf": 1.0, "text": "我志愿按期转正。"}, {"bbox": [49.0, 158.49600219726562, 73.0, 174.17999267578125], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 190.89601135253906, 85.0, 206.5800018310547], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 221.38800048828125, 132.291015625, 239.01600646972656], "conf": 1.0, "text": "2025年9月20日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": []}	{"title": "转正申请书", "closing": "敬礼！", "char_count": 40, "salutation": "敬爱的党组织：", "signature_date": "2025-09-20", "signature_date_raw": "2025年9月20日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:19.639429+08	2026-10-17 18:36:19.63943+08
82	82	PDF_TEXT	\N	previews/077de8e9b07e4c708accbae522f9d892.pdf	转正公示材料\n公示 2025年9月25 日至 2025年10月8 日。\n???\n??\n·····	44	[{"text": "转正公示材料\\n公示 2025年9月25 日至 2025年10月8 日。\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 121.0, 76.9800033569336], "conf": 1.0, "text": "转正公示材料"}, {"bbox": [49.0, 91.78800201416016, 277.64453125, 109.41600799560547], "conf": 1.0, "text": "公示 2025年9月25 日至 2025年10月8 日。"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "转正公示材料", "char_count": 40, "signature_date": "2025-10-08", "signature_date_raw": "2025年10月8日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:19.74295+08	2026-10-17 18:36:19.742951+08
83	83	PDF_TEXT	\N	previews/acbc63e4b465414f8d3794ae299d98c5.pdf	入党申请书\n敬爱的党组织：\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\n范作用。\n此致\n敬礼！\n申请人：演示学生\n2023年3月15日\n·····	176	[{"text": "入党申请书\\n敬爱的党组织：\\n我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代\\n表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心\\n全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模\\n范作用。\\n此致\\n敬礼！\\n申请人：演示学生\\n2023年3月15日\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 109.0, 76.9800033569336], "conf": 1.0, "text": "入党申请书"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "敬爱的党组织："}, {"bbox": [49.0, 124.18800354003906, 522.4375, 141.81600952148438], "conf": 1.0, "text": "我志愿加入中国共产党。我认真学习马克思列宁主义、毛泽东思想、邓小平理论、“三个代"}, {"bbox": [49.0, 144.58799743652344, 534.4375, 162.21600341796875], "conf": 1.0, "text": "表”重要思想、科学发展观、习近平新时代中国特色社会主义思想，深刻理解党的性质和全心"}, {"bbox": [49.0, 166.89601135253906, 541.0, 182.5800018310547], "conf": 1.0, "text": "全意为人民服务的宗旨。我的入党动机是为了更好地为人民服务，在学习和工作中发挥先锋模"}, {"bbox": [49.0, 187.29600524902344, 97.0, 202.97999572753906], "conf": 1.0, "text": "范作用。"}, {"bbox": [49.0, 219.6959991455078, 73.0, 235.37998962402344], "conf": 1.0, "text": "此致"}, {"bbox": [49.0, 252.09597778320312, 85.0, 267.77996826171875], "conf": 1.0, "text": "敬礼！"}, {"bbox": [49.0, 284.4960021972656, 145.0, 300.17999267578125], "conf": 1.0, "text": "申请人：演示学生"}, {"bbox": [49.0, 314.98797607421875, 132.291015625, 332.615966796875], "conf": 1.0, "text": "2023年3月15日"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [], "signatures": [{"bbox": [327.25, 690.4399999999999, 535.5, 799.9], "slot": "申请人", "page_no": 1, "present": false, "ink_ratio": 0.00022168033695411216}]}	{"name": "演示学生", "title": "入党申请书", "closing": "敬礼！", "char_count": 166, "salutation": "敬爱的党组织：", "signature_date": "2023-03-15", "signature_name": "演示学生", "signature_date_raw": "2023年3月15日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:19.801136+08	2026-10-17 18:36:19.801137+08
84	84	PDF_TEXT	\N	previews/4b927d9c793f4e528d97fafe0a7f001c.pdf	党组织派人谈话记录\n谈话人已谈话。\n2023年3月28日\n???\n??\n·····	41	[{"text": "党组织派人谈话记录\\n谈话人已谈话。\\n2023年3月28日\\n???\\n??\\n·····", "width": 595.0, "blocks": [{"bbox": [49.0, 61.29600143432617, 157.0, 76.9800033569336], "conf": 1.0, "text": "党组织派人谈话记录"}, {"bbox": [49.0, 93.69600677490234, 133.0, 109.3800048828125], "conf": 1.0, "text": "谈话人已谈话。"}, {"bbox": [49.0, 124.18800354003906, 132.291015625, 141.81600952148438], "conf": 1.0, "text": "2023年3月28日"}, {"bbox": [462.4939880371094, 680.0, 477.5059814453125, 692.365966796875], "conf": 1.0, "text": "???"}, {"bbox": [464.9960021972656, 693.29345703125, 475.0039978027344, 705.659423828125], "conf": 1.0, "text": "??"}, {"bbox": [400.0, 788.1749877929688, 415.2900695800781, 803.2890014648438], "conf": 1.0, "text": "·····"}], "height": 842.0, "source": "text", "page_no": 1, "quality": {"dpi": null, "is_blurry": false, "blur_score": null}}]	{"seals": [{"bbox": [418.6592741935484, 678.2777777777778, 521.2247983870968, 780.8290598290598], "conf": 0.8971618017996364, "page_no": 1}], "signatures": []}	{"title": "党组织派人谈话记录", "char_count": 36, "salutation": "党组织派人谈话记录", "signature_date": "2023-03-28", "signature_date_raw": "2023年3月28日"}	{}	[]	\N	\N	\N	\N	2026-10-17 18:36:19.842721+08	2026-10-17 18:36:19.842721+08
\.


--
-- Data for Name: political_terms; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.political_terms (id, term_type, standard_text, wrong_variants, sequence_items, category, severity, note, is_active, updated_by, created_at, updated_at) FROM stdin;
1	SEQUENCE	马克思列宁主义、毛泽东思想、邓小平理论、“三个代表”重要思想、科学发展观、习近平新时代中国特色社会主义思想	[]	["马克思列宁主义", "毛泽东思想", "邓小平理论", "“三个代表”重要思想", "科学发展观", "习近平新时代中国特色社会主义思想"]	指导思想	BLOCK	示例数据，请组织部按学校标准核定后启用	t	\N	2026-10-17 18:29:29.45829+08	2026-10-17 18:29:29.458292+08
2	VARIANT	中国共产党是中国工人阶级的先锋队	["中国共产党是中国人民的先锋队"]	[]	党的性质	WARN	示例数据，完整表述见党章	t	\N	2026-10-17 18:29:29.458339+08	2026-10-17 18:29:29.458339+08
3	VARIANT	全心全意为人民服务	["全心全意为人名服务", "全心全意为人民做贡献"]	[]	宗旨	WARN	示例数据	t	\N	2026-10-17 18:29:29.458356+08	2026-10-17 18:29:29.458356+08
\.


--
-- Data for Name: prompt_templates; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.prompt_templates (id, code, name, system_prompt, user_prompt, output_schema, is_active, updated_by, created_at, updated_at) FROM stdin;
1	CLASSIFY	材料分类	你是高校党员发展材料审核助手。只根据给定文本判断材料类型。必须输出 JSON。	候选类型：{types}\n文本：\n{text}\n请输出 {"type_code":"...","confidence":0-1,"reason":"..."}	{"reason": "string", "type_code": "string", "confidence": "number"}	t	\N	2026-10-17 18:29:29.465175+08	2026-10-17 18:29:29.465176+08
2	EXTRACT	信息抽取	你是材料信息抽取助手。从文本中抽取时间节点与基本信息，不得编造。输出 JSON。	节点定义：{nodes}\n文本：\n{text}\n输出 {"fields":{},"dates":[{"node_code","date","raw_text"}]}	{"dates": "array", "fields": "object"}	t	\N	2026-10-17 18:29:29.465221+08	2026-10-17 18:29:29.465221+08
3	CONTENT_CHECK	内容核查	你是党建材料内容审核助手。只标注疑似不规范表述，不下定性政治结论。涉及意识形态一律标 needs_human_judgement=true。	规则：{rules}\n文本：\n{text}\n输出 {"issues":[{"rule_code","snippet","reason","confidence"}]}	{"issues": "array"}	t	\N	2026-10-17 18:29:29.465236+08	2026-10-17 18:29:29.465237+08
4	SUGGEST	修改建议润色	在给定模板约束下润色修改建议，必须保留模板中的修改要求句，不得改变事实。	模板：{template}\n变量：{vars}\n问题：{issue}\n输出 {"suggestion":"..."}	{"suggestion": "string"}	t	\N	2026-10-17 18:29:29.465249+08	2026-10-17 18:29:29.465249+08
\.


--
-- Data for Name: review_records; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.review_records (id, submission_id, level, action, from_status, to_status, reviewer_id, reviewer_name, reviewer_role, comment, report_id, issue_ids, round_no, is_batch, ip, created_at) FROM stdin;
\.


--
-- Data for Name: revoked_tokens; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.revoked_tokens (jti, user_id, token_type, expires_at, revoked_at) FROM stdin;
f43374e3430244ebb5adec6c59b589c1	5	refresh	2026-10-24 18:52:50+08	2026-10-17 20:52:50.250528+08
\.


--
-- Data for Name: rule_versions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.rule_versions (id, version_no, change_kind, change_action, change_object_id, change_summary, snapshot, created_by, created_at) FROM stdin;
1	1	init	INIT	\N	写入默认规则基线（R-T01–R-T23、R-F01–R-F09、R-C01–R-C10）	{"time_rules": [{"id": 1, "code": "R-T01", "name": "年满十八周岁", "basis": "中国共产党章程", "params": {"checks": [{"at": "T02", "op": "age_at_least", "birth": "T01", "years": 18}]}, "severity": "BLOCK", "is_active": true, "rule_type": "AGE", "sort_order": 1, "applies_stages": [1, 2, 3, 4, 5], "message_template": "递交入党申请书时未满 18 周岁（出生 {T01}，申请 {T02}）", "suggestion_template_id": null}, {"id": 2, "code": "R-T02", "name": "谈话不超过一个月", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"a": "T02", "b": "T03", "op": "within", "max": {"unit": "MONTH", "value": 1}}]}, "severity": "WARN", "is_active": true, "rule_type": "INTERVAL", "sort_order": 2, "applies_stages": [1, 2], "message_template": "党组织派人谈话（{T03}）距递交申请（{T02}）超过一个月", "suggestion_template_id": null}, {"id": 3, "code": "R-T03", "name": "谈话不早于申请", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"a": "T02", "b": "T03", "op": "before", "strict": false}]}, "severity": "BLOCK", "is_active": true, "rule_type": "ORDER", "sort_order": 3, "applies_stages": [1, 2], "message_template": "谈话日期（{T03}）早于递交申请日期（{T02}）", "suggestion_template_id": null}, {"id": 4, "code": "R-T04", "name": "确定积极分子距申请不过久", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"a": "T02", "b": "T04", "op": "within", "max": {"unit": "DAY", "value": 30}}]}, "severity": "WARN", "is_active": true, "rule_type": "INTERVAL", "sort_order": 4, "applies_stages": [2], "message_template": "确定积极分子（{T04}）距递交申请（{T02}）间隔过长", "suggestion_template_id": null}, {"id": 5, "code": "R-T05", "name": "积极分子培养满一年", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"a": "T04", "b": "T08", "op": "at_least", "min": {"unit": "YEAR", "value": 1}}]}, "severity": "BLOCK", "is_active": true, "rule_type": "INTERVAL", "sort_order": 5, "applies_stages": [3, 4, 5], "message_template": "确定积极分子（{T04}）至确定发展对象（{T08}）间隔不足 1 年", "suggestion_template_id": null}, {"id": 6, "code": "R-T06", "name": "思想汇报相邻间隔", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"op": "seq_max_gap", "to": "T08", "max": {"unit": "MONTH", "value": 3}, "seq": "T06[*]", "from": "T04"}]}, "severity": "WARN", "is_active": true, "rule_type": "SEQ_GAP", "sort_order": 6, "applies_stages": [2, 3, 5], "message_template": "思想汇报相邻间隔超过一个季度", "suggestion_template_id": null}, {"id": 7, "code": "R-T07", "name": "思想汇报按期提交", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"op": "seq_period_count", "to": "T08", "seq": "T06[*]", "from": "T04", "period_months": 3, "min_per_period": 1}]}, "severity": "BLOCK", "is_active": true, "rule_type": "SEQ_COUNT", "sort_order": 7, "applies_stages": [2, 3, 5], "message_template": "培养期内思想汇报未按每季度至少一份提交", "suggestion_template_id": null}, {"id": 8, "code": "R-T08", "name": "政审完成于确定发展对象之后", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"a": "T08", "b": "T09", "op": "before", "strict": false}]}, "severity": "BLOCK", "is_active": true, "rule_type": "ORDER", "sort_order": 8, "applies_stages": [3, 4], "message_template": "政治审查完成日期（{T09}）早于确定发展对象（{T08}）", "suggestion_template_id": null}, {"id": 9, "code": "R-T09", "name": "集中培训时长或学时", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"op": "duration_min", "min": {"unit": "DAY", "value": 3}, "node": "T10", "or_hours": 24}]}, "severity": "BLOCK", "is_active": true, "rule_type": "DURATION", "sort_order": 9, "applies_stages": [3, 4], "message_template": "集中培训未满规定时长或学时", "suggestion_template_id": null}, {"id": 10, "code": "R-T10", "name": "公示不少于五个工作日且在预审前", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"a": "T11.end", "b": "T12", "op": "before", "strict": false}, {"op": "duration_min", "min": {"unit": "WORKDAY", "value": 5}, "node": "T11"}]}, "severity": "WARN", "is_active": true, "rule_type": "COMPOSITE", "sort_order": 10, "applies_stages": [4], "message_template": "发展对象公示未满五个工作日或晚于预审", "suggestion_template_id": null}, {"id": 11, "code": "R-T11", "name": "预审在填写志愿书之前", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"a": "T12", "b": "T13", "op": "before", "strict": false}]}, "severity": "BLOCK", "is_active": true, "rule_type": "ORDER", "sort_order": 11, "applies_stages": [4], "message_template": "填写入党志愿书（{T13}）早于上级党委预审（{T12}）", "suggestion_template_id": null}, {"id": 12, "code": "R-T12", "name": "支部大会在预审之后", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"a": "T12", "b": "T14", "op": "before", "strict": true}]}, "severity": "BLOCK", "is_active": true, "rule_type": "ORDER", "sort_order": 12, "applies_stages": [4], "message_template": "支部大会接收日期（{T14}）早于预审（{T12}）", "suggestion_template_id": null}, {"id": 13, "code": "R-T13", "name": "党委派人谈话在支部大会之后", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"a": "T14", "b": "T15", "op": "before", "strict": false}]}, "severity": "BLOCK", "is_active": true, "rule_type": "ORDER", "sort_order": 13, "applies_stages": [4], "message_template": "上级党委派人谈话（{T15}）早于支部大会（{T14}）", "suggestion_template_id": null}, {"id": 14, "code": "R-T14", "name": "审批在谈话之后", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"a": "T15", "b": "T16", "op": "before", "strict": false}]}, "severity": "BLOCK", "is_active": true, "rule_type": "ORDER", "sort_order": 14, "applies_stages": [4], "message_template": "上级党委审批（{T16}）早于派人谈话（{T15}）", "suggestion_template_id": null}, {"id": 15, "code": "R-T15", "name": "党委审批不超过三个月", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"a": "T14", "b": "T16", "op": "within", "max": {"unit": "MONTH", "value": 3}}]}, "severity": "WARN", "is_active": true, "rule_type": "INTERVAL", "sort_order": 15, "applies_stages": [4, 5], "message_template": "上级党委审批（{T16}）距支部大会（{T14}）超过三个月", "suggestion_template_id": null}, {"id": 16, "code": "R-T16", "name": "派生预备期满日", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"op": "derive", "base": "T14", "name": "D01", "offset": {"unit": "YEAR", "value": 1}}]}, "severity": "CALC", "is_active": true, "rule_type": "DERIVED", "sort_order": 16, "applies_stages": [4, 5], "message_template": "预备期满日 = 支部大会接收日 + 1 年", "suggestion_template_id": null}, {"id": 17, "code": "R-T17", "name": "转正申请不晚于预备期满", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"a": "T18", "b": "D01", "op": "before", "strict": false}]}, "severity": "WARN", "is_active": true, "rule_type": "ORDER", "sort_order": 17, "applies_stages": [5], "message_template": "转正申请（{T18}）晚于预备期满日（D01）", "suggestion_template_id": null}, {"id": 18, "code": "R-T18", "name": "转正公示不少于五个工作日", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"op": "duration_min", "min": {"unit": "WORKDAY", "value": 5}, "node": "T19"}]}, "severity": "WARN", "is_active": true, "rule_type": "DURATION", "sort_order": 18, "applies_stages": [5], "message_template": "转正公示不足五个工作日", "suggestion_template_id": null}, {"id": 19, "code": "R-T19", "name": "转正大会在预备期满之后", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"a": "D01", "b": "T20", "op": "before", "strict": false}]}, "severity": "BLOCK", "is_active": true, "rule_type": "ORDER", "sort_order": 19, "applies_stages": [5], "message_template": "支部大会讨论转正（{T20}）早于预备期满日", "suggestion_template_id": null}, {"id": 20, "code": "R-T20", "name": "同一节点多来源一致", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"op": "consistent", "nodes": "*"}]}, "severity": "BLOCK", "is_active": true, "rule_type": "CONSISTENCY", "sort_order": 20, "applies_stages": [1, 2, 3, 4, 5], "message_template": "时间节点在多份材料中取值不一致", "suggestion_template_id": null}, {"id": 21, "code": "R-T21", "name": "日期合法且不晚于上传日", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"op": "valid_date", "nodes": "*"}]}, "severity": "BLOCK", "is_active": true, "rule_type": "VALID_DATE", "sort_order": 21, "applies_stages": [1, 2, 3, 4, 5], "message_template": "抽取日期不完整、不合法或晚于材料上传日", "suggestion_template_id": null}, {"id": 22, "code": "R-T22", "name": "阶段必填节点与单调递增", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"op": "required", "nodes_by_stage": {"1": ["T01", "T02"], "2": ["T02", "T03", "T04"], "3": ["T04", "T08"], "4": ["T08", "T09", "T10", "T11", "T12", "T13", "T14", "T15", "T16"], "5": ["T14", "T16", "T18", "T19", "T20"]}}, {"op": "monotonic", "nodes": ["T02", "T04", "T08", "T14", "T20"]}]}, "severity": "BLOCK", "is_active": true, "rule_type": "REQUIRED_NODES", "sort_order": 22, "applies_stages": [1, 2, 3, 4, 5], "message_template": "当前阶段关键时间节点缺失或顺序颠倒", "suggestion_template_id": null}, {"id": 23, "code": "R-T23", "name": "序列日期落在培养区间", "basis": "中国共产党发展党员工作细则", "params": {"checks": [{"op": "seq_in_range", "to": "T08", "seq": "T06[*]", "from": "T04"}]}, "severity": "WARN", "is_active": true, "rule_type": "IN_RANGE", "sort_order": 23, "applies_stages": [2, 3, 5], "message_template": "思想汇报日期未落在对应培养考察区间内", "suggestion_template_id": null}], "check_rules": [{"id": 1, "code": "R-F01", "name": "文书结构完整", "basis": "学校党员发展材料规范", "engine": "RULE", "params": {"elements": ["title", "salutation", "body", "closing", "signature", "date"]}, "category": "FORMAT", "severity": "WARN", "is_active": true, "applies_to": [], "sort_order": 1, "is_optional": false, "message_template": "材料缺少标题、称谓、正文、结束语、署名或落款日期等文书要素", "needs_human_judgement": false, "suggestion_template_id": null}, {"id": 2, "code": "R-F02", "name": "落款日期格式", "basis": "学校党员发展材料规范", "engine": "RULE", "params": {}, "category": "FORMAT", "severity": "WARN", "is_active": true, "applies_to": [], "sort_order": 2, "is_optional": false, "message_template": "落款日期未按“××××年××月××日”书写", "needs_human_judgement": false, "suggestion_template_id": null}, {"id": 3, "code": "R-F03", "name": "签名齐全", "basis": "学校党员发展材料规范", "engine": "RULE", "params": {}, "category": "FORMAT", "severity": "BLOCK", "is_active": true, "applies_to": [], "sort_order": 3, "is_optional": false, "message_template": "规定签名位未检测到签名", "needs_human_judgement": false, "suggestion_template_id": null}, {"id": 4, "code": "R-F04", "name": "印章齐全", "basis": "学校党员发展材料规范", "engine": "RULE", "params": {}, "category": "FORMAT", "severity": "BLOCK", "is_active": true, "applies_to": [], "sort_order": 4, "is_optional": false, "message_template": "规定盖章位未检测到党组织印章", "needs_human_judgement": false, "suggestion_template_id": null}, {"id": 5, "code": "R-F05", "name": "手写材料可辨识", "basis": "学校党员发展材料规范", "engine": "RULE", "params": {}, "category": "FORMAT", "severity": "WARN", "is_active": true, "applies_to": ["RECORD_BOOK_ACTIVIST", "RECORD_BOOK_CANDIDATE", "RECORD_BOOK_PROBATIONARY"], "sort_order": 5, "is_optional": false, "message_template": "写实簿等手写材料清晰度不足或文本过少", "needs_human_judgement": false, "suggestion_template_id": null}, {"id": 6, "code": "R-F06", "name": "篇幅下限", "basis": "学校党员发展材料规范", "engine": "RULE", "params": {"min_chars": {"AUTOBIOGRAPHY": 3000}}, "category": "FORMAT", "severity": "WARN", "is_active": true, "applies_to": ["AUTOBIOGRAPHY"], "sort_order": 6, "is_optional": false, "message_template": "材料正文字数不足规定篇幅", "needs_human_judgement": false, "suggestion_template_id": null}, {"id": 7, "code": "R-F07", "name": "扫描件清晰度", "basis": "学校党员发展材料规范", "engine": "RULE", "params": {"min_dpi": 150, "blur_threshold": 60}, "category": "FORMAT", "severity": "WARN", "is_active": true, "applies_to": [], "sort_order": 7, "is_optional": false, "message_template": "扫描件分辨率不足或页面模糊", "needs_human_judgement": false, "suggestion_template_id": null}, {"id": 8, "code": "R-F08", "name": "版式规范", "basis": "学校党员发展材料规范", "engine": "RULE", "params": {"docx_layout": {"font": "宋体", "size_pt": 12, "margin_cm": 2.54, "line_spacing": 1.5}}, "category": "FORMAT", "severity": "INFO", "is_active": false, "applies_to": [], "sort_order": 8, "is_optional": true, "message_template": "DOCX 字体、字号、行距或页边距与学校模板不一致", "needs_human_judgement": false, "suggestion_template_id": null}, {"id": 9, "code": "R-F09", "name": "页面方向与装订", "basis": "学校党员发展材料规范", "engine": "RULE", "params": {}, "category": "FORMAT", "severity": "INFO", "is_active": false, "applies_to": [], "sort_order": 9, "is_optional": true, "message_template": "页面方向或装订边距不符合归档要求", "needs_human_judgement": false, "suggestion_template_id": null}, {"id": 10, "code": "R-C01", "name": "政治术语规范", "basis": "党章及发展党员工作细则；学校审核标准", "engine": "RULE", "params": {}, "category": "CONTENT", "severity": "WARN", "is_active": true, "applies_to": [], "sort_order": 10, "is_optional": false, "message_template": "出现不规范政治术语或并列顺序错误", "needs_human_judgement": false, "suggestion_template_id": null}, {"id": 11, "code": "R-C02", "name": "政治表述准确性", "basis": "党章及发展党员工作细则；学校审核标准", "engine": "LLM", "params": {}, "category": "CONTENT", "severity": "WARN", "is_active": true, "applies_to": [], "sort_order": 11, "is_optional": false, "message_template": "政治理论表述疑似不准确，请审核员研判", "needs_human_judgement": true, "suggestion_template_id": null}, {"id": 12, "code": "R-C03", "name": "意识形态表述", "basis": "党章及发展党员工作细则；学校审核标准", "engine": "RULE_LLM", "params": {}, "category": "CONTENT", "severity": "BLOCK", "is_active": true, "applies_to": [], "sort_order": 12, "is_optional": false, "message_template": "疑似存在需研判的意识形态表述", "needs_human_judgement": true, "suggestion_template_id": null}, {"id": 13, "code": "R-C04", "name": "入党动机表述", "basis": "党章及发展党员工作细则；学校审核标准", "engine": "RULE_LLM", "params": {}, "category": "CONTENT", "severity": "WARN", "is_active": true, "applies_to": ["APPLICATION_LETTER", "THOUGHT_REPORT", "REGULARIZATION_LETTER"], "sort_order": 13, "is_optional": false, "message_template": "入党动机表述疑似功利化或要素不足", "needs_human_judgement": true, "suggestion_template_id": null}, {"id": 14, "code": "R-C05", "name": "内容要素完整", "basis": "党章及发展党员工作细则；学校审核标准", "engine": "RULE", "params": {}, "category": "CONTENT", "severity": "WARN", "is_active": true, "applies_to": [], "sort_order": 14, "is_optional": false, "message_template": "材料缺少模板规定的内容要素", "needs_human_judgement": false, "suggestion_template_id": null}, {"id": 15, "code": "R-C06", "name": "基本信息一致", "basis": "党章及发展党员工作细则；学校审核标准", "engine": "RULE", "params": {}, "category": "CONTENT", "severity": "BLOCK", "is_active": true, "applies_to": [], "sort_order": 15, "is_optional": false, "message_template": "姓名、学号、出生日期等基本信息与档案或其他材料不一致", "needs_human_judgement": false, "suggestion_template_id": null}, {"id": 16, "code": "R-C07", "name": "经历与时间线吻合", "basis": "党章及发展党员工作细则；学校审核标准", "engine": "LLM", "params": {}, "category": "CONTENT", "severity": "WARN", "is_active": true, "applies_to": ["AUTOBIOGRAPHY", "APPLICATION_LETTER"], "sort_order": 16, "is_optional": false, "message_template": "自传或申请书经历与时间节点疑似矛盾", "needs_human_judgement": true, "suggestion_template_id": null}, {"id": 17, "code": "R-C08", "name": "思想认识深度", "basis": "党章及发展党员工作细则；学校审核标准", "engine": "LLM", "params": {}, "category": "CONTENT", "severity": "INFO", "is_active": true, "applies_to": ["THOUGHT_REPORT", "AUTOBIOGRAPHY"], "sort_order": 17, "is_optional": false, "message_template": "思想认识表述较空泛，建议结合学习与实践写实", "needs_human_judgement": true, "suggestion_template_id": null}, {"id": 18, "code": "R-C09", "name": "引用原文核对", "basis": "党章及发展党员工作细则；学校审核标准", "engine": "RULE", "params": {}, "category": "CONTENT", "severity": "INFO", "is_active": false, "applies_to": [], "sort_order": 18, "is_optional": true, "message_template": "疑似错误引用党章或重要文献原文", "needs_human_judgement": false, "suggestion_template_id": null}, {"id": 19, "code": "R-C10", "name": "同批次文本高度相似", "basis": "党章及发展党员工作细则；学校审核标准", "engine": "RULE", "params": {"threshold": 0.8}, "category": "CONTENT", "severity": "WARN", "is_active": false, "applies_to": ["THOUGHT_REPORT", "AUTOBIOGRAPHY", "APPLICATION_LETTER"], "sort_order": 19, "is_optional": true, "message_template": "与同批次其他学生材料文本高度相似", "needs_human_judgement": false, "suggestion_template_id": null}], "material_types": [{"id": 1, "code": "APPLICATION_LETTER", "name": "入党申请书", "is_active": true, "sort_order": 1, "description": null, "stage_codes": [1], "date_node_map": {"signature_date": "T02", "field:出生日期": "T01"}, "title_keywords": ["入党申请书"], "element_template": [{"key": "motive", "name": "入党动机", "keywords": ["入党动机", "为什么要入党"], "required": true}, {"key": "theory", "name": "理论认识", "keywords": ["党的性质", "指导思想", "宗旨"], "required": true}], "exclude_keywords": [], "format_requirements": {"seal_slots": [], "doc_elements": ["title", "salutation", "body", "closing", "signature", "date"], "required_fields": ["姓名"], "signature_slots": [{"slot": "本人签名", "keywords": ["签名", "申请人"]}], "handwriting_required": false}}, {"id": 2, "code": "PARTY_TALK_RECORD", "name": "党组织派人谈话记录", "is_active": true, "sort_order": 2, "description": null, "stage_codes": [1], "date_node_map": {"signature_date": "T03"}, "title_keywords": ["谈话记录", "派人谈话"], "element_template": [], "exclude_keywords": [], "format_requirements": {"seal_slots": [{"slot": "党组织印章", "keywords": ["盖章", "党支部"]}], "doc_elements": ["title", "body", "signature", "date"], "required_fields": [], "signature_slots": [{"slot": "谈话人签名", "keywords": ["谈话人", "签名"]}]}}, {"id": 3, "code": "RECOMMENDATION", "name": "推荐/推优材料", "is_active": true, "sort_order": 3, "description": null, "stage_codes": [2], "date_node_map": {}, "title_keywords": ["推荐", "推优", "团组织推优"], "element_template": [], "exclude_keywords": [], "format_requirements": {"seal_slots": [{"slot": "团组织印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "signature", "date"], "signature_slots": [{"slot": "推荐组织签名", "keywords": ["签名"]}]}}, {"id": 4, "code": "ACTIVIST_MEETING_RECORD", "name": "支委会研究确定积极分子记录", "is_active": true, "sort_order": 4, "description": null, "stage_codes": [2], "date_node_map": {"signature_date": "T04"}, "title_keywords": ["确定入党积极分子", "支委会"], "element_template": [], "exclude_keywords": [], "format_requirements": {"seal_slots": [{"slot": "党支部印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "signature", "date"], "signature_slots": [{"slot": "书记签名", "keywords": ["书记", "签名"]}]}}, {"id": 5, "code": "ACTIVIST_FILING", "name": "积极分子备案材料", "is_active": true, "sort_order": 5, "description": null, "stage_codes": [2], "date_node_map": {"signature_date": "T04"}, "title_keywords": ["积极分子", "备案"], "element_template": [], "exclude_keywords": [], "format_requirements": {"seal_slots": [{"slot": "党委印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "date"]}}, {"id": 6, "code": "RECORD_BOOK_ACTIVIST", "name": "写实簿·积极分子培养考察部分", "is_active": true, "sort_order": 6, "description": null, "stage_codes": [2], "date_node_map": {"field:确定积极分子": "T04"}, "title_keywords": ["培养教育考察写实簿", "积极分子"], "element_template": [], "exclude_keywords": [], "format_requirements": {"doc_elements": ["title", "body", "signature"], "handwriting_required": true}}, {"id": 7, "code": "THOUGHT_REPORT", "name": "思想汇报", "is_active": true, "sort_order": 7, "description": null, "stage_codes": [2, 3, 5], "date_node_map": {"signature_date": "T06"}, "title_keywords": ["思想汇报"], "element_template": [{"key": "motive", "name": "入党动机", "keywords": ["入党动机", "为什么要入党"], "required": true}, {"key": "theory", "name": "理论认识", "keywords": ["党的性质", "指导思想", "宗旨"], "required": true}], "exclude_keywords": [], "format_requirements": {"doc_elements": ["title", "salutation", "body", "closing", "signature", "date"], "signature_slots": [{"slot": "本人签名", "keywords": ["汇报人", "签名"]}]}}, {"id": 8, "code": "ACTIVIST_TRAINING_CERT", "name": "积极分子培训结业证明", "is_active": true, "sort_order": 8, "description": null, "stage_codes": [2], "date_node_map": {}, "title_keywords": ["积极分子培训", "结业"], "element_template": [], "exclude_keywords": [], "format_requirements": {"seal_slots": [{"slot": "培训单位印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body"]}}, {"id": 9, "code": "AUTOBIOGRAPHY", "name": "自传", "is_active": true, "sort_order": 9, "description": null, "stage_codes": [3], "date_node_map": {"field:出生日期": "T01"}, "title_keywords": ["自传"], "element_template": [{"key": "family", "name": "家庭主要成员", "keywords": ["家庭主要成员", "家庭成员"], "required": true}, {"key": "growth", "name": "成长经历", "keywords": ["成长", "学习经历"], "required": true}, {"key": "thought", "name": "思想演变", "keywords": ["思想", "认识"], "required": true}], "exclude_keywords": [], "format_requirements": {"min_chars": 3000, "doc_elements": ["title", "body", "signature", "date"], "required_fields": ["姓名", "出生日期", "家庭主要成员"]}}, {"id": 10, "code": "CANDIDATE_MEETING_RECORD", "name": "支委会确定发展对象记录", "is_active": true, "sort_order": 10, "description": null, "stage_codes": [3], "date_node_map": {"signature_date": "T08"}, "title_keywords": ["确定为发展对象"], "element_template": [], "exclude_keywords": [], "format_requirements": {"seal_slots": [{"slot": "党支部印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "signature", "date"]}}, {"id": 11, "code": "POLITICAL_REVIEW", "name": "政治审查材料", "is_active": true, "sort_order": 11, "description": null, "stage_codes": [3], "date_node_map": {"signature_date": "T09"}, "title_keywords": ["政治审查", "政审", "函调"], "element_template": [], "exclude_keywords": [], "format_requirements": {"seal_slots": [{"slot": "审查单位印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "signature", "date"]}}, {"id": 12, "code": "TRAINING_CERT", "name": "集中培训结业证书", "is_active": true, "sort_order": 12, "description": null, "stage_codes": [3], "date_node_map": {"field:学时": "T10", "field:培训起": "T10"}, "title_keywords": ["集中培训", "结业证书"], "element_template": [], "exclude_keywords": [], "format_requirements": {"seal_slots": [{"slot": "党校印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body"]}}, {"id": 13, "code": "RECORD_BOOK_CANDIDATE", "name": "写实簿·发展对象考察部分", "is_active": true, "sort_order": 13, "description": null, "stage_codes": [3], "date_node_map": {}, "title_keywords": ["写实簿", "发展对象"], "element_template": [], "exclude_keywords": [], "format_requirements": {"doc_elements": ["title", "body"], "handwriting_required": true}}, {"id": 14, "code": "CANDIDATE_PUBLICITY", "name": "发展对象公示材料", "is_active": true, "sort_order": 14, "description": null, "stage_codes": [4], "date_node_map": {"field:公示起": "T11"}, "title_keywords": ["公示", "发展对象"], "element_template": [], "exclude_keywords": [], "format_requirements": {"seal_slots": [{"slot": "党支部印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "date"]}}, {"id": 15, "code": "PRE_REVIEW_OPINION", "name": "上级党委预审意见", "is_active": true, "sort_order": 15, "description": null, "stage_codes": [4], "date_node_map": {"signature_date": "T12"}, "title_keywords": ["预审"], "element_template": [], "exclude_keywords": [], "format_requirements": {"seal_slots": [{"slot": "党委印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "signature", "date"]}}, {"id": 16, "code": "APPLICATION_FORM", "name": "入党志愿书", "is_active": true, "sort_order": 16, "description": null, "stage_codes": [4], "date_node_map": {"signature_date": "T13", "field:出生日期": "T01"}, "title_keywords": ["入党志愿书"], "element_template": [], "exclude_keywords": [], "format_requirements": {"seal_slots": [{"slot": "党组织印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "signature", "date"], "signature_slots": [{"slot": "本人签名", "keywords": ["志愿人", "签名"]}]}}, {"id": 17, "code": "ADMISSION_MEETING_RECORD", "name": "支部大会讨论接收记录", "is_active": true, "sort_order": 17, "description": null, "stage_codes": [4], "date_node_map": {"signature_date": "T14"}, "title_keywords": ["支部大会", "接收预备党员"], "element_template": [], "exclude_keywords": [], "format_requirements": {"seal_slots": [{"slot": "党支部印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "signature", "date"]}}, {"id": 18, "code": "COMMITTEE_TALK_RECORD", "name": "上级党委派人谈话记录", "is_active": true, "sort_order": 18, "description": null, "stage_codes": [4], "date_node_map": {"signature_date": "T15"}, "title_keywords": ["上级党委", "谈话"], "element_template": [], "exclude_keywords": [], "format_requirements": {"doc_elements": ["title", "body", "signature", "date"]}}, {"id": 19, "code": "ADMISSION_APPROVAL", "name": "上级党委审批意见", "is_active": true, "sort_order": 19, "description": null, "stage_codes": [4], "date_node_map": {"signature_date": "T16"}, "title_keywords": ["审批", "接收为预备党员"], "element_template": [], "exclude_keywords": [], "format_requirements": {"seal_slots": [{"slot": "党委印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "signature", "date"]}}, {"id": 20, "code": "REGULARIZATION_LETTER", "name": "转正申请书", "is_active": true, "sort_order": 20, "description": null, "stage_codes": [5], "date_node_map": {"signature_date": "T18"}, "title_keywords": ["转正申请"], "element_template": [{"key": "motive", "name": "入党动机", "keywords": ["入党动机", "为什么要入党"], "required": true}, {"key": "theory", "name": "理论认识", "keywords": ["党的性质", "指导思想", "宗旨"], "required": true}], "exclude_keywords": [], "format_requirements": {"doc_elements": ["title", "salutation", "body", "closing", "signature", "date"]}}, {"id": 21, "code": "RECORD_BOOK_PROBATIONARY", "name": "写实簿·预备党员考察部分", "is_active": true, "sort_order": 21, "description": null, "stage_codes": [5], "date_node_map": {}, "title_keywords": ["写实簿", "预备党员"], "element_template": [], "exclude_keywords": [], "format_requirements": {"doc_elements": ["title", "body"], "handwriting_required": true}}, {"id": 22, "code": "REGULARIZATION_PUBLICITY", "name": "转正公示材料", "is_active": true, "sort_order": 22, "description": null, "stage_codes": [5], "date_node_map": {"field:公示起": "T19"}, "title_keywords": ["转正", "公示"], "element_template": [], "exclude_keywords": [], "format_requirements": {"seal_slots": [{"slot": "党支部印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "date"]}}, {"id": 23, "code": "REGULARIZATION_MEETING_RECORD", "name": "支部大会讨论转正记录", "is_active": true, "sort_order": 23, "description": null, "stage_codes": [5], "date_node_map": {"signature_date": "T20"}, "title_keywords": ["支部大会", "转正"], "element_template": [], "exclude_keywords": [], "format_requirements": {"doc_elements": ["title", "body", "signature", "date"]}}, {"id": 24, "code": "REGULARIZATION_APPROVAL", "name": "上级党委审批转正意见", "is_active": true, "sort_order": 24, "description": null, "stage_codes": [5], "date_node_map": {"signature_date": "T21"}, "title_keywords": ["审批", "转为正式党员"], "element_template": [], "exclude_keywords": [], "format_requirements": {"seal_slots": [{"slot": "党委印章", "keywords": ["盖章"]}], "doc_elements": ["title", "body", "signature", "date"]}}], "time_node_defs": [{"id": 1, "code": "T01", "name": "出生日期", "has_hours": false, "is_active": true, "sort_order": 1, "stage_code": 1, "value_kind": "DATE", "derive_expr": null, "extract_keywords": ["出生日期", "生于"], "required_from_stage": 1, "source_material_codes": ["APPLICATION_LETTER", "AUTOBIOGRAPHY", "APPLICATION_FORM"]}, {"id": 2, "code": "T02", "name": "递交入党申请书日期", "has_hours": false, "is_active": true, "sort_order": 2, "stage_code": 1, "value_kind": "DATE", "derive_expr": null, "extract_keywords": ["入党申请", "申请入党"], "required_from_stage": 1, "source_material_codes": ["APPLICATION_LETTER"]}, {"id": 3, "code": "T03", "name": "党组织派人谈话日期", "has_hours": false, "is_active": true, "sort_order": 3, "stage_code": 1, "value_kind": "DATE", "derive_expr": null, "extract_keywords": ["谈话"], "required_from_stage": 2, "source_material_codes": ["PARTY_TALK_RECORD"]}, {"id": 4, "code": "T04", "name": "确定为入党积极分子日期", "has_hours": false, "is_active": true, "sort_order": 4, "stage_code": 2, "value_kind": "DATE", "derive_expr": null, "extract_keywords": ["确定为入党积极分子", "列为入党积极分子"], "required_from_stage": 2, "source_material_codes": ["ACTIVIST_MEETING_RECORD", "ACTIVIST_FILING"]}, {"id": 5, "code": "T05", "name": "指定培养联系人日期", "has_hours": false, "is_active": true, "sort_order": 5, "stage_code": 2, "value_kind": "DATE", "derive_expr": null, "extract_keywords": ["培养联系人"], "required_from_stage": 2, "source_material_codes": ["RECORD_BOOK_ACTIVIST"]}, {"id": 6, "code": "T06", "name": "思想汇报日期", "has_hours": false, "is_active": true, "sort_order": 6, "stage_code": 2, "value_kind": "DATE_SEQ", "derive_expr": null, "extract_keywords": ["思想汇报"], "required_from_stage": 2, "source_material_codes": ["THOUGHT_REPORT"]}, {"id": 7, "code": "T07", "name": "培养考察记录日期", "has_hours": false, "is_active": true, "sort_order": 7, "stage_code": 2, "value_kind": "DATE_SEQ", "derive_expr": null, "extract_keywords": ["考察", "写实"], "required_from_stage": 2, "source_material_codes": ["RECORD_BOOK_ACTIVIST", "RECORD_BOOK_CANDIDATE", "RECORD_BOOK_PROBATIONARY"]}, {"id": 8, "code": "T08", "name": "确定为发展对象日期", "has_hours": false, "is_active": true, "sort_order": 8, "stage_code": 3, "value_kind": "DATE", "derive_expr": null, "extract_keywords": ["确定为发展对象"], "required_from_stage": 3, "source_material_codes": ["CANDIDATE_MEETING_RECORD"]}, {"id": 9, "code": "T09", "name": "政治审查完成日期", "has_hours": false, "is_active": true, "sort_order": 9, "stage_code": 3, "value_kind": "DATE", "derive_expr": null, "extract_keywords": ["政治审查", "政审"], "required_from_stage": 4, "source_material_codes": ["POLITICAL_REVIEW"]}, {"id": 10, "code": "T10", "name": "集中培训起止与学时", "has_hours": true, "is_active": true, "sort_order": 10, "stage_code": 3, "value_kind": "DATE_RANGE", "derive_expr": null, "extract_keywords": ["培训", "学时", "结业"], "required_from_stage": 4, "source_material_codes": ["TRAINING_CERT"]}, {"id": 11, "code": "T11", "name": "发展对象公示起止", "has_hours": false, "is_active": true, "sort_order": 11, "stage_code": 4, "value_kind": "DATE_RANGE", "derive_expr": null, "extract_keywords": ["公示"], "required_from_stage": 4, "source_material_codes": ["CANDIDATE_PUBLICITY"]}, {"id": 12, "code": "T12", "name": "上级党委预审日期", "has_hours": false, "is_active": true, "sort_order": 12, "stage_code": 4, "value_kind": "DATE", "derive_expr": null, "extract_keywords": ["预审"], "required_from_stage": 4, "source_material_codes": ["PRE_REVIEW_OPINION"]}, {"id": 13, "code": "T13", "name": "填写入党志愿书日期", "has_hours": false, "is_active": true, "sort_order": 13, "stage_code": 4, "value_kind": "DATE", "derive_expr": null, "extract_keywords": ["志愿书"], "required_from_stage": 4, "source_material_codes": ["APPLICATION_FORM"]}, {"id": 14, "code": "T14", "name": "支部大会接收预备党员日期", "has_hours": false, "is_active": true, "sort_order": 14, "stage_code": 4, "value_kind": "DATE", "derive_expr": null, "extract_keywords": ["支部大会", "接收为预备党员"], "required_from_stage": 4, "source_material_codes": ["ADMISSION_MEETING_RECORD", "APPLICATION_FORM"]}, {"id": 15, "code": "T15", "name": "上级党委派人谈话日期", "has_hours": false, "is_active": true, "sort_order": 15, "stage_code": 4, "value_kind": "DATE", "derive_expr": null, "extract_keywords": ["谈话"], "required_from_stage": 4, "source_material_codes": ["COMMITTEE_TALK_RECORD"]}, {"id": 16, "code": "T16", "name": "上级党委审批预备党员日期", "has_hours": false, "is_active": true, "sort_order": 16, "stage_code": 4, "value_kind": "DATE", "derive_expr": null, "extract_keywords": ["审批", "预备党员"], "required_from_stage": 4, "source_material_codes": ["ADMISSION_APPROVAL"]}, {"id": 17, "code": "T17", "name": "编入党支部日期", "has_hours": false, "is_active": true, "sort_order": 17, "stage_code": 4, "value_kind": "DATE", "derive_expr": null, "extract_keywords": ["编入"], "required_from_stage": 5, "source_material_codes": ["RECORD_BOOK_PROBATIONARY"]}, {"id": 18, "code": "T18", "name": "递交转正申请书日期", "has_hours": false, "is_active": true, "sort_order": 18, "stage_code": 5, "value_kind": "DATE", "derive_expr": null, "extract_keywords": ["转正申请"], "required_from_stage": 5, "source_material_codes": ["REGULARIZATION_LETTER"]}, {"id": 19, "code": "T19", "name": "转正公示起止", "has_hours": false, "is_active": true, "sort_order": 19, "stage_code": 5, "value_kind": "DATE_RANGE", "derive_expr": null, "extract_keywords": ["转正公示", "公示"], "required_from_stage": 5, "source_material_codes": ["REGULARIZATION_PUBLICITY"]}, {"id": 20, "code": "T20", "name": "支部大会讨论转正日期", "has_hours": false, "is_active": true, "sort_order": 20, "stage_code": 5, "value_kind": "DATE", "derive_expr": null, "extract_keywords": ["转正", "支部大会"], "required_from_stage": 5, "source_material_codes": ["REGULARIZATION_MEETING_RECORD"]}, {"id": 21, "code": "T21", "name": "上级党委审批转正日期", "has_hours": false, "is_active": true, "sort_order": 21, "stage_code": 5, "value_kind": "DATE", "derive_expr": null, "extract_keywords": ["审批", "正式党员"], "required_from_stage": 5, "source_material_codes": ["REGULARIZATION_APPROVAL"]}, {"id": 22, "code": "D01", "name": "预备期满日", "has_hours": false, "is_active": true, "sort_order": 22, "stage_code": 4, "value_kind": "DERIVED", "derive_expr": {"base": "T14", "offset": {"unit": "YEAR", "value": 1}}, "extract_keywords": [], "required_from_stage": 5, "source_material_codes": []}], "checklist_items": [{"id": 1, "is_active": true, "sort_order": 1, "stage_code": 1, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 1, "requirement_text": "本人亲笔或打印后签字的入党申请书", "period_start_node": null}, {"id": 2, "is_active": true, "sort_order": 2, "stage_code": 1, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 2, "requirement_text": "党组织派人谈话记录", "period_start_node": null}, {"id": 3, "is_active": true, "sort_order": 3, "stage_code": 2, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 3, "requirement_text": "党员推荐或团组织推优材料", "period_start_node": null}, {"id": 4, "is_active": true, "sort_order": 4, "stage_code": 2, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 4, "requirement_text": "支委会（支部大会）研究确定积极分子记录", "period_start_node": null}, {"id": 5, "is_active": true, "sort_order": 5, "stage_code": 2, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 5, "requirement_text": "积极分子备案材料", "period_start_node": null}, {"id": 6, "is_active": true, "sort_order": 6, "stage_code": 2, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 6, "requirement_text": "写实簿积极分子培养考察部分", "period_start_node": null}, {"id": 7, "is_active": true, "sort_order": 7, "stage_code": 2, "fixed_count": 0, "is_required": true, "period_months": 3, "quantity_mode": "PER_PERIOD", "period_end_node": "T08", "material_type_id": 7, "requirement_text": "每季度至少一份思想汇报", "period_start_node": "T04"}, {"id": 8, "is_active": true, "sort_order": 8, "stage_code": 2, "fixed_count": 1, "is_required": false, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 8, "requirement_text": "积极分子培训结业证明（可选）", "period_start_node": null}, {"id": 9, "is_active": true, "sort_order": 9, "stage_code": 3, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 9, "requirement_text": "自传", "period_start_node": null}, {"id": 10, "is_active": true, "sort_order": 10, "stage_code": 3, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 10, "requirement_text": "支委会确定发展对象记录", "period_start_node": null}, {"id": 11, "is_active": true, "sort_order": 11, "stage_code": 3, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 11, "requirement_text": "政治审查材料", "period_start_node": null}, {"id": 12, "is_active": true, "sort_order": 12, "stage_code": 3, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 12, "requirement_text": "集中培训结业证书", "period_start_node": null}, {"id": 13, "is_active": true, "sort_order": 13, "stage_code": 3, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 13, "requirement_text": "写实簿发展对象考察部分", "period_start_node": null}, {"id": 14, "is_active": true, "sort_order": 14, "stage_code": 3, "fixed_count": 0, "is_required": true, "period_months": 3, "quantity_mode": "PER_PERIOD", "period_end_node": "T14", "material_type_id": 7, "requirement_text": "每季度至少一份思想汇报", "period_start_node": "T08"}, {"id": 15, "is_active": true, "sort_order": 15, "stage_code": 4, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 14, "requirement_text": "发展对象公示材料", "period_start_node": null}, {"id": 16, "is_active": true, "sort_order": 16, "stage_code": 4, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 15, "requirement_text": "上级党委预审意见", "period_start_node": null}, {"id": 17, "is_active": true, "sort_order": 17, "stage_code": 4, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 16, "requirement_text": "入党志愿书", "period_start_node": null}, {"id": 18, "is_active": true, "sort_order": 18, "stage_code": 4, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 17, "requirement_text": "支部大会讨论接收预备党员记录", "period_start_node": null}, {"id": 19, "is_active": true, "sort_order": 19, "stage_code": 4, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 18, "requirement_text": "上级党委派人谈话记录", "period_start_node": null}, {"id": 20, "is_active": true, "sort_order": 20, "stage_code": 4, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 19, "requirement_text": "上级党委审批意见", "period_start_node": null}, {"id": 21, "is_active": true, "sort_order": 21, "stage_code": 5, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 20, "requirement_text": "转正申请书", "period_start_node": null}, {"id": 22, "is_active": true, "sort_order": 22, "stage_code": 5, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 21, "requirement_text": "写实簿预备党员考察部分", "period_start_node": null}, {"id": 23, "is_active": true, "sort_order": 23, "stage_code": 5, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 22, "requirement_text": "转正公示材料", "period_start_node": null}, {"id": 24, "is_active": true, "sort_order": 24, "stage_code": 5, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 23, "requirement_text": "支部大会讨论转正记录", "period_start_node": null}, {"id": 25, "is_active": true, "sort_order": 25, "stage_code": 5, "fixed_count": 1, "is_required": true, "period_months": null, "quantity_mode": "FIXED", "period_end_node": null, "material_type_id": 24, "requirement_text": "上级党委审批转正意见", "period_start_node": null}, {"id": 26, "is_active": true, "sort_order": 26, "stage_code": 5, "fixed_count": 0, "is_required": true, "period_months": 3, "quantity_mode": "PER_PERIOD", "period_end_node": "T20", "material_type_id": 7, "requirement_text": "预备期每季度至少一份思想汇报", "period_start_node": "T14"}], "political_terms": [{"id": 1, "note": "示例数据，请组织部按学校标准核定后启用", "category": "指导思想", "severity": "BLOCK", "is_active": true, "term_type": "SEQUENCE", "standard_text": "马克思列宁主义、毛泽东思想、邓小平理论、“三个代表”重要思想、科学发展观、习近平新时代中国特色社会主义思想", "sequence_items": ["马克思列宁主义", "毛泽东思想", "邓小平理论", "“三个代表”重要思想", "科学发展观", "习近平新时代中国特色社会主义思想"], "wrong_variants": []}, {"id": 2, "note": "示例数据，完整表述见党章", "category": "党的性质", "severity": "WARN", "is_active": true, "term_type": "VARIANT", "standard_text": "中国共产党是中国工人阶级的先锋队", "sequence_items": [], "wrong_variants": ["中国共产党是中国人民的先锋队"]}, {"id": 3, "note": "示例数据", "category": "宗旨", "severity": "WARN", "is_active": true, "term_type": "VARIANT", "standard_text": "全心全意为人民服务", "sequence_items": [], "wrong_variants": ["全心全意为人名服务", "全心全意为人民做贡献"]}], "prompt_templates": [{"id": 1, "code": "CLASSIFY", "name": "材料分类", "is_active": true, "user_prompt": "候选类型：{types}\\n文本：\\n{text}\\n请输出 {\\"type_code\\":\\"...\\",\\"confidence\\":0-1,\\"reason\\":\\"...\\"}", "output_schema": {"reason": "string", "type_code": "string", "confidence": "number"}, "system_prompt": "你是高校党员发展材料审核助手。只根据给定文本判断材料类型。必须输出 JSON。"}, {"id": 2, "code": "EXTRACT", "name": "信息抽取", "is_active": true, "user_prompt": "节点定义：{nodes}\\n文本：\\n{text}\\n输出 {\\"fields\\":{},\\"dates\\":[{\\"node_code\\",\\"date\\",\\"raw_text\\"}]}", "output_schema": {"dates": "array", "fields": "object"}, "system_prompt": "你是材料信息抽取助手。从文本中抽取时间节点与基本信息，不得编造。输出 JSON。"}, {"id": 3, "code": "CONTENT_CHECK", "name": "内容核查", "is_active": true, "user_prompt": "规则：{rules}\\n文本：\\n{text}\\n输出 {\\"issues\\":[{\\"rule_code\\",\\"snippet\\",\\"reason\\",\\"confidence\\"}]}", "output_schema": {"issues": "array"}, "system_prompt": "你是党建材料内容审核助手。只标注疑似不规范表述，不下定性政治结论。涉及意识形态一律标 needs_human_judgement=true。"}, {"id": 4, "code": "SUGGEST", "name": "修改建议润色", "is_active": true, "user_prompt": "模板：{template}\\n变量：{vars}\\n问题：{issue}\\n输出 {\\"suggestion\\":\\"...\\"}", "output_schema": {"suggestion": "string"}, "system_prompt": "在给定模板约束下润色修改建议，必须保留模板中的修改要求句，不得改变事实。"}], "sensitive_phrases": [{"id": 1, "phrase": "入党可以评优评奖", "category": "MOTIVATION", "is_active": true, "risk_note": "功利化入党动机表述", "match_type": "KEYWORD", "risk_level": "HIGH", "suggestion": "请从理想信念、服务师生、发挥作用等角度重写入党动机。"}, {"id": 2, "phrase": "为了好找工作", "category": "MOTIVATION", "is_active": true, "risk_note": "功利化入党动机表述", "match_type": "KEYWORD", "risk_level": "HIGH", "suggestion": "请结合对党的认识和自身成长经历写明入党动机。"}, {"id": 3, "phrase": "入党有面子", "category": "MOTIVATION", "is_active": true, "risk_note": "功利化入党动机表述", "match_type": "KEYWORD", "risk_level": "MEDIUM", "suggestion": "请删除面子、待遇等表述，聚焦党员义务。"}], "suggestion_templates": [{"id": 1, "code": "SUG_MISSING_MATERIAL", "title": "缺项补交", "is_active": true, "rule_code": null, "example_text": "请补交思想汇报 1 份，写明近期学习与实践收获。", "template_text": "缺少《{材料名}》{缺少份数} 份（应交 {应交份数} 份，已交 {实交份数} 份）。请按要求补交：{提交要求}。截止日期：{截止日期}。"}, {"id": 2, "code": "SUG_TIME_INTERVAL", "title": "培养周期不足", "is_active": true, "rule_code": "R-T05", "example_text": null, "template_text": "《{材料名}》中{节点名}为 {实际值}，不符合“{规则名}”要求（{要求值}）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。"}, {"id": 3, "code": "SUG_DATE_INVALID", "title": "日期不完整", "is_active": true, "rule_code": "R-T21", "example_text": null, "template_text": "《{材料名}》第 {页码} 页日期“{原文}”书写不完整或无效，请按“××××年××月××日”格式补全。"}, {"id": 4, "code": "SUG_TERM", "title": "术语不规范", "is_active": true, "rule_code": "R-C01", "example_text": null, "template_text": "第 {页码} 页“{原文}”表述不规范，标准写法为“{标准写法}”，请修改。"}, {"id": 5, "code": "SUG_SIGNATURE", "title": "缺签名", "is_active": true, "rule_code": "R-F03", "example_text": null, "template_text": "《{材料名}》{签名位} 未检测到签名，请本人（或相关负责人）补签。"}, {"id": 6, "code": "SUG_SEAL", "title": "缺印章", "is_active": true, "rule_code": "R-F04", "example_text": null, "template_text": "《{材料名}》{盖章位} 未检测到党组织印章，请联系相应党组织补盖。"}, {"id": 7, "code": "SUG_JUDGEMENT", "title": "需研判表述", "is_active": true, "rule_code": "R-C03", "example_text": null, "template_text": "第 {页码} 页“{原文}”需审核员研判：{风险说明}。如确有不妥，请结合党章和理论学习修改相关表述。"}, {"id": 8, "code": "SUG_FORMAT", "title": "形式规范", "is_active": true, "rule_code": null, "example_text": null, "template_text": "《{材料名}》{问题描述}。请按学校材料格式要求修改后重新上传。"}, {"id": 9, "code": "SUG_CONTENT", "title": "内容要素", "is_active": true, "rule_code": null, "example_text": null, "template_text": "《{材料名}》缺少要素“{要素名}”，请按模板补写相关内容。"}]}	\N	2026-10-17 18:29:29.479933+08
\.


--
-- Data for Name: schema_meta; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.schema_meta (key, value, updated_at) FROM stdin;
schema_version	1	2026-10-17 21:09:33.748066+08
\.


--
-- Data for Name: sensitive_phrases; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sensitive_phrases (id, phrase, match_type, category, risk_level, risk_note, suggestion, is_active, updated_by, created_at, updated_at) FROM stdin;
1	入党可以评优评奖	KEYWORD	MOTIVATION	HIGH	功利化入党动机表述	请从理想信念、服务师生、发挥作用等角度重写入党动机。	t	\N	2026-10-17 18:29:29.45837+08	2026-10-17 18:29:29.458371+08
2	为了好找工作	KEYWORD	MOTIVATION	HIGH	功利化入党动机表述	请结合对党的认识和自身成长经历写明入党动机。	t	\N	2026-10-17 18:29:29.458397+08	2026-10-17 18:29:29.458397+08
3	入党有面子	KEYWORD	MOTIVATION	MEDIUM	功利化入党动机表述	请删除面子、待遇等表述，聚焦党员义务。	t	\N	2026-10-17 18:29:29.458409+08	2026-10-17 18:29:29.45841+08
\.


--
-- Data for Name: stages; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.stages (code, stage_key, name, sort_order) FROM stdin;
1	APPLICATION	申请入党	1
2	ACTIVIST	确定入党积极分子	2
3	CANDIDATE	确定发展对象	3
4	PROBATIONARY	接收预备党员	4
5	FULL_MEMBER	预备党员转正	5
\.


--
-- Data for Name: submissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.submissions (id, archive_id, stage_code, batch_id, college_id, branch_id, status, return_level, round_no, latest_report_id, ai_status, ai_job_id, submitted_at, level_entered_at, filed_at, filed_by, created_at, updated_at) FROM stdin;
1	1	1	1	2	3	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:04.038094+08	2026-10-17 18:36:04.038096+08	2026-10-17 18:36:04.038096+08	\N	2026-10-17 18:36:04.038096+08	2026-10-17 18:36:04.038096+08
2	1	2	1	2	3	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:05.331598+08	2026-10-17 18:36:05.331601+08	2026-10-17 18:36:05.331601+08	\N	2026-10-17 18:36:05.331602+08	2026-10-17 18:36:05.331602+08
21	7	3	1	2	4	BRANCH_REVIEW	\N	1	6	DONE	33	2026-10-17 18:36:07.965811+08	2026-10-17 18:36:07.965812+08	\N	\N	2026-10-17 18:36:07.965812+08	2026-10-17 18:36:17.099999+08
4	2	1	1	2	3	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:06.48203+08	2026-10-17 18:36:06.482031+08	2026-10-17 18:36:06.482032+08	\N	2026-10-17 18:36:06.482032+08	2026-10-17 18:36:06.482032+08
5	2	2	1	2	3	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:06.483668+08	2026-10-17 18:36:06.48367+08	2026-10-17 18:36:06.48367+08	\N	2026-10-17 18:36:06.48367+08	2026-10-17 18:36:06.48367+08
17	5	5	1	2	4	ORG_FILING	\N	1	4	DONE	23	2026-10-17 18:36:07.45812+08	2026-10-17 18:36:07.458122+08	\N	\N	2026-10-17 18:36:07.458122+08	2026-10-17 18:36:16.743666+08
7	3	1	1	2	3	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:06.712299+08	2026-10-17 18:36:06.712301+08	2026-10-17 18:36:06.712301+08	\N	2026-10-17 18:36:06.712301+08	2026-10-17 18:36:06.712301+08
9	4	1	1	2	3	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:06.796789+08	2026-10-17 18:36:06.79679+08	2026-10-17 18:36:06.79679+08	\N	2026-10-17 18:36:06.79679+08	2026-10-17 18:36:06.79679+08
10	4	2	1	2	3	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:06.798179+08	2026-10-17 18:36:06.798181+08	2026-10-17 18:36:06.798181+08	\N	2026-10-17 18:36:06.798181+08	2026-10-17 18:36:06.798182+08
11	4	3	1	2	3	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:06.798682+08	2026-10-17 18:36:06.798683+08	2026-10-17 18:36:06.798683+08	\N	2026-10-17 18:36:06.798684+08	2026-10-17 18:36:06.798684+08
39	13	3	1	6	7	BRANCH_REVIEW	\N	1	11	DONE	59	2026-10-17 18:36:09.95647+08	2026-10-17 18:36:09.956471+08	\N	\N	2026-10-17 18:36:09.956472+08	2026-10-17 18:36:18.106799+08
13	5	1	1	2	4	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:07.455752+08	2026-10-17 18:36:07.455753+08	2026-10-17 18:36:07.455754+08	\N	2026-10-17 18:36:07.455754+08	2026-10-17 18:36:07.455754+08
14	5	2	1	2	4	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:07.456835+08	2026-10-17 18:36:07.456836+08	2026-10-17 18:36:07.456836+08	\N	2026-10-17 18:36:07.456836+08	2026-10-17 18:36:07.456837+08
15	5	3	1	2	4	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:07.457279+08	2026-10-17 18:36:07.45728+08	2026-10-17 18:36:07.457281+08	\N	2026-10-17 18:36:07.457281+08	2026-10-17 18:36:07.457281+08
16	5	4	1	2	4	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:07.457725+08	2026-10-17 18:36:07.457726+08	2026-10-17 18:36:07.457726+08	\N	2026-10-17 18:36:07.457726+08	2026-10-17 18:36:07.457727+08
24	8	3	1	2	4	RETURNED	BRANCH	1	7	DONE	37	2026-10-17 18:36:08.481897+08	2026-10-17 18:36:08.481898+08	\N	\N	2026-10-17 18:36:08.481898+08	2026-10-17 18:36:17.242455+08
8	3	2	1	2	3	DRAFT	\N	1	21	DONE	105	\N	\N	\N	\N	2026-10-17 18:36:06.713297+08	2026-10-17 18:53:08.549176+08
19	7	1	1	2	4	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:07.964369+08	2026-10-17 18:36:07.964371+08	2026-10-17 18:36:07.964372+08	\N	2026-10-17 18:36:07.964372+08	2026-10-17 18:36:07.964372+08
20	7	2	1	2	4	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:07.965359+08	2026-10-17 18:36:07.96536+08	2026-10-17 18:36:07.965361+08	\N	2026-10-17 18:36:07.965361+08	2026-10-17 18:36:07.965361+08
35	11	5	1	2	5	ORG_FILING	\N	1	9	DONE	49	2026-10-17 18:36:09.474636+08	2026-10-17 18:36:09.474637+08	\N	\N	2026-10-17 18:36:09.474638+08	2026-10-17 18:36:17.718029+08
22	8	1	1	2	4	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:08.480379+08	2026-10-17 18:36:08.48038+08	2026-10-17 18:36:08.48038+08	\N	2026-10-17 18:36:08.48038+08	2026-10-17 18:36:08.480381+08
23	8	2	1	2	4	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:08.481457+08	2026-10-17 18:36:08.481459+08	2026-10-17 18:36:08.481459+08	\N	2026-10-17 18:36:08.481459+08	2026-10-17 18:36:08.48146+08
42	14	3	1	6	7	RETURNED	BRANCH	1	12	DONE	63	2026-10-17 18:36:10.575831+08	2026-10-17 18:36:10.575832+08	\N	\N	2026-10-17 18:36:10.575833+08	2026-10-17 18:36:18.244863+08
25	9	1	1	2	5	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:08.711213+08	2026-10-17 18:36:08.711215+08	2026-10-17 18:36:08.711215+08	\N	2026-10-17 18:36:08.711215+08	2026-10-17 18:36:08.711215+08
26	9	2	1	2	5	DRAFT	\N	1	\N	NONE	\N	\N	\N	\N	\N	2026-10-17 18:36:08.712231+08	2026-10-17 18:36:08.712232+08
27	10	1	1	2	5	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:08.802722+08	2026-10-17 18:36:08.802723+08	2026-10-17 18:36:08.802723+08	\N	2026-10-17 18:36:08.802723+08	2026-10-17 18:36:08.802723+08
28	10	2	1	2	5	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:08.803833+08	2026-10-17 18:36:08.803835+08	2026-10-17 18:36:08.803835+08	\N	2026-10-17 18:36:08.803835+08	2026-10-17 18:36:08.803836+08
29	10	3	1	2	5	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:08.804281+08	2026-10-17 18:36:08.804282+08	2026-10-17 18:36:08.804282+08	\N	2026-10-17 18:36:08.804282+08	2026-10-17 18:36:08.804282+08
36	12	1	1	2	5	FILED	\N	1	10	DONE	52	2026-10-17 18:36:09.76449+08	2026-10-17 18:36:09.764492+08	2026-10-17 18:36:09.764492+08	\N	2026-10-17 18:36:09.764493+08	2026-10-17 18:36:17.816604+08
31	11	1	1	2	5	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:09.472258+08	2026-10-17 18:36:09.472259+08	2026-10-17 18:36:09.472259+08	\N	2026-10-17 18:36:09.47226+08	2026-10-17 18:36:09.47226+08
32	11	2	1	2	5	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:09.473465+08	2026-10-17 18:36:09.473466+08	2026-10-17 18:36:09.473466+08	\N	2026-10-17 18:36:09.473467+08	2026-10-17 18:36:09.473467+08
33	11	3	1	2	5	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:09.473897+08	2026-10-17 18:36:09.473898+08	2026-10-17 18:36:09.473899+08	\N	2026-10-17 18:36:09.473899+08	2026-10-17 18:36:09.473899+08
34	11	4	1	2	5	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:09.47428+08	2026-10-17 18:36:09.474281+08	2026-10-17 18:36:09.474282+08	\N	2026-10-17 18:36:09.474282+08	2026-10-17 18:36:09.474282+08
3	1	3	1	2	3	BRANCH_REVIEW	\N	1	23	DONE	108	2026-10-17 18:36:05.332636+08	2026-10-17 18:36:05.332638+08	\N	\N	2026-10-17 18:36:05.332639+08	2026-10-17 19:17:49.701354+08
37	13	1	1	6	7	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:09.955155+08	2026-10-17 18:36:09.955156+08	2026-10-17 18:36:09.955156+08	\N	2026-10-17 18:36:09.955157+08	2026-10-17 18:36:09.955157+08
38	13	2	1	6	7	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:09.955974+08	2026-10-17 18:36:09.955975+08	2026-10-17 18:36:09.955976+08	\N	2026-10-17 18:36:09.955976+08	2026-10-17 18:36:09.955976+08
40	14	1	1	6	7	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:10.574515+08	2026-10-17 18:36:10.574517+08	2026-10-17 18:36:10.574517+08	\N	2026-10-17 18:36:10.574517+08	2026-10-17 18:36:10.574518+08
41	14	2	1	6	7	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:10.575409+08	2026-10-17 18:36:10.575411+08	2026-10-17 18:36:10.575411+08	\N	2026-10-17 18:36:10.575411+08	2026-10-17 18:36:10.575412+08
43	15	1	1	6	7	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:10.894016+08	2026-10-17 18:36:10.894017+08	2026-10-17 18:36:10.894018+08	\N	2026-10-17 18:36:10.894018+08	2026-10-17 18:36:10.894019+08
18	6	1	1	2	4	FILED	\N	1	5	DONE	26	2026-10-17 18:36:07.761188+08	2026-10-17 18:36:07.761189+08	2026-10-17 18:36:07.761189+08	\N	2026-10-17 18:36:07.761189+08	2026-10-17 18:36:16.840989+08
6	2	3	1	2	3	RETURNED	BRANCH	1	2	DONE	11	2026-10-17 18:36:06.484284+08	2026-10-17 18:36:06.484285+08	\N	\N	2026-10-17 18:36:06.484286+08	2026-10-17 18:36:16.288617+08
30	10	4	1	2	5	COLLEGE_REVIEW	\N	1	8	DONE	45	2026-10-17 18:36:08.804666+08	2026-10-17 18:36:08.804667+08	\N	\N	2026-10-17 18:36:08.804667+08	2026-10-17 18:36:17.570272+08
12	4	4	1	2	3	COLLEGE_REVIEW	\N	1	3	DONE	19	2026-10-17 18:36:06.799123+08	2026-10-17 18:36:06.799124+08	\N	\N	2026-10-17 18:36:06.799125+08	2026-10-17 18:36:16.606171+08
44	15	2	1	6	7	DRAFT	\N	1	\N	NONE	\N	\N	\N	\N	\N	2026-10-17 18:36:10.894959+08	2026-10-17 18:36:10.89496+08
45	16	1	1	6	7	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:11.014695+08	2026-10-17 18:36:11.014696+08	2026-10-17 18:36:11.014696+08	\N	2026-10-17 18:36:11.014696+08	2026-10-17 18:36:11.014696+08
46	16	2	1	6	7	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:11.016068+08	2026-10-17 18:36:11.01607+08	2026-10-17 18:36:11.01607+08	\N	2026-10-17 18:36:11.016071+08	2026-10-17 18:36:11.016071+08
47	16	3	1	6	7	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:11.016646+08	2026-10-17 18:36:11.016648+08	2026-10-17 18:36:11.016648+08	\N	2026-10-17 18:36:11.016649+08	2026-10-17 18:36:11.016649+08
49	17	1	1	6	8	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:12.016512+08	2026-10-17 18:36:12.016513+08	2026-10-17 18:36:12.016514+08	\N	2026-10-17 18:36:12.016514+08	2026-10-17 18:36:12.016514+08
50	17	2	1	6	8	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:12.017495+08	2026-10-17 18:36:12.017496+08	2026-10-17 18:36:12.017497+08	\N	2026-10-17 18:36:12.017497+08	2026-10-17 18:36:12.017498+08
51	17	3	1	6	8	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:12.01799+08	2026-10-17 18:36:12.017991+08	2026-10-17 18:36:12.017992+08	\N	2026-10-17 18:36:12.017992+08	2026-10-17 18:36:12.017992+08
52	17	4	1	6	8	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:12.018785+08	2026-10-17 18:36:12.018787+08	2026-10-17 18:36:12.018787+08	\N	2026-10-17 18:36:12.018788+08	2026-10-17 18:36:12.018788+08
71	23	5	1	6	9	ORG_FILING	\N	1	19	DONE	101	2026-10-17 18:36:14.663292+08	2026-10-17 18:36:14.663293+08	\N	\N	2026-10-17 18:36:14.663293+08	2026-10-17 18:36:19.712915+08
55	19	1	1	6	8	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:12.679783+08	2026-10-17 18:36:12.679784+08	2026-10-17 18:36:12.679784+08	\N	2026-10-17 18:36:12.679785+08	2026-10-17 18:36:12.679785+08
56	19	2	1	6	8	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:12.680773+08	2026-10-17 18:36:12.680775+08	2026-10-17 18:36:12.680775+08	\N	2026-10-17 18:36:12.680775+08	2026-10-17 18:36:12.680776+08
72	24	1	1	6	9	FILED	\N	1	20	DONE	104	2026-10-17 18:36:14.956717+08	2026-10-17 18:36:14.95672+08	2026-10-17 18:36:14.95672+08	\N	2026-10-17 18:36:14.95672+08	2026-10-17 18:36:19.824662+08
58	20	1	1	6	8	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:13.31808+08	2026-10-17 18:36:13.318082+08	2026-10-17 18:36:13.318082+08	\N	2026-10-17 18:36:13.318083+08	2026-10-17 18:36:13.318083+08
59	20	2	1	6	8	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:13.319044+08	2026-10-17 18:36:13.319045+08	2026-10-17 18:36:13.319045+08	\N	2026-10-17 18:36:13.319045+08	2026-10-17 18:36:13.319046+08
61	21	1	1	6	9	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:13.654196+08	2026-10-17 18:36:13.654198+08	2026-10-17 18:36:13.654198+08	\N	2026-10-17 18:36:13.654198+08	2026-10-17 18:36:13.654199+08
62	21	2	1	6	9	DRAFT	\N	1	\N	NONE	\N	\N	\N	\N	\N	2026-10-17 18:36:13.655129+08	2026-10-17 18:36:13.65513+08
63	22	1	1	6	9	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:13.775344+08	2026-10-17 18:36:13.775345+08	2026-10-17 18:36:13.775345+08	\N	2026-10-17 18:36:13.775345+08	2026-10-17 18:36:13.775346+08
64	22	2	1	6	9	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:13.77651+08	2026-10-17 18:36:13.776511+08	2026-10-17 18:36:13.776512+08	\N	2026-10-17 18:36:13.776512+08	2026-10-17 18:36:13.776512+08
65	22	3	1	6	9	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:13.777051+08	2026-10-17 18:36:13.777052+08	2026-10-17 18:36:13.777052+08	\N	2026-10-17 18:36:13.777053+08	2026-10-17 18:36:13.777053+08
67	23	1	1	6	9	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:14.661312+08	2026-10-17 18:36:14.661313+08	2026-10-17 18:36:14.661314+08	\N	2026-10-17 18:36:14.661314+08	2026-10-17 18:36:14.661314+08
68	23	2	1	6	9	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:14.6621+08	2026-10-17 18:36:14.662101+08	2026-10-17 18:36:14.662101+08	\N	2026-10-17 18:36:14.662102+08	2026-10-17 18:36:14.662102+08
69	23	3	1	6	9	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:14.662501+08	2026-10-17 18:36:14.662502+08	2026-10-17 18:36:14.662502+08	\N	2026-10-17 18:36:14.662502+08	2026-10-17 18:36:14.662502+08
70	23	4	1	6	9	FILED	\N	1	\N	NONE	\N	2026-10-17 18:36:14.662894+08	2026-10-17 18:36:14.662895+08	2026-10-17 18:36:14.662896+08	\N	2026-10-17 18:36:14.662896+08	2026-10-17 18:36:14.662896+08
48	16	4	1	6	7	COLLEGE_REVIEW	\N	1	13	DONE	71	2026-10-17 18:36:11.017296+08	2026-10-17 18:36:11.017297+08	\N	\N	2026-10-17 18:36:11.017297+08	2026-10-17 18:36:18.562489+08
53	17	5	1	6	8	ORG_FILING	\N	1	14	DONE	75	2026-10-17 18:36:12.019409+08	2026-10-17 18:36:12.01941+08	\N	\N	2026-10-17 18:36:12.019411+08	2026-10-17 18:36:18.700986+08
54	18	1	1	6	8	FILED	\N	1	15	DONE	78	2026-10-17 18:36:12.428077+08	2026-10-17 18:36:12.428078+08	2026-10-17 18:36:12.428078+08	\N	2026-10-17 18:36:12.428079+08	2026-10-17 18:36:18.8005+08
57	19	3	1	6	8	BRANCH_REVIEW	\N	1	16	DONE	85	2026-10-17 18:36:12.681347+08	2026-10-17 18:36:12.681349+08	\N	\N	2026-10-17 18:36:12.68135+08	2026-10-17 18:36:19.072884+08
60	20	3	1	6	8	RETURNED	BRANCH	1	17	DONE	89	2026-10-17 18:36:13.31953+08	2026-10-17 18:36:13.319531+08	\N	\N	2026-10-17 18:36:13.319532+08	2026-10-17 18:36:19.223569+08
66	22	4	1	6	9	COLLEGE_REVIEW	\N	1	18	DONE	97	2026-10-17 18:36:13.777628+08	2026-10-17 18:36:13.77763+08	\N	\N	2026-10-17 18:36:13.777631+08	2026-10-17 18:36:19.550275+08
\.


--
-- Data for Name: suggestion_templates; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.suggestion_templates (id, code, rule_code, title, template_text, example_text, is_active, updated_by, created_at, updated_at) FROM stdin;
1	SUG_MISSING_MATERIAL	\N	缺项补交	缺少《{材料名}》{缺少份数} 份（应交 {应交份数} 份，已交 {实交份数} 份）。请按要求补交：{提交要求}。截止日期：{截止日期}。	请补交思想汇报 1 份，写明近期学习与实践收获。	t	\N	2026-10-17 18:29:29.409113+08	2026-10-17 18:29:29.409116+08
2	SUG_TIME_INTERVAL	R-T05	培养周期不足	《{材料名}》中{节点名}为 {实际值}，不符合“{规则名}”要求（{要求值}）。请核对原始记录，如为笔误请更正并由相关负责人签字确认；如确实不满足，请联系党支部说明情况。	\N	t	\N	2026-10-17 18:29:29.409204+08	2026-10-17 18:29:29.409204+08
3	SUG_DATE_INVALID	R-T21	日期不完整	《{材料名}》第 {页码} 页日期“{原文}”书写不完整或无效，请按“××××年××月××日”格式补全。	\N	t	\N	2026-10-17 18:29:29.409227+08	2026-10-17 18:29:29.409227+08
4	SUG_TERM	R-C01	术语不规范	第 {页码} 页“{原文}”表述不规范，标准写法为“{标准写法}”，请修改。	\N	t	\N	2026-10-17 18:29:29.409242+08	2026-10-17 18:29:29.409242+08
5	SUG_SIGNATURE	R-F03	缺签名	《{材料名}》{签名位} 未检测到签名，请本人（或相关负责人）补签。	\N	t	\N	2026-10-17 18:29:29.409255+08	2026-10-17 18:29:29.409255+08
6	SUG_SEAL	R-F04	缺印章	《{材料名}》{盖章位} 未检测到党组织印章，请联系相应党组织补盖。	\N	t	\N	2026-10-17 18:29:29.409268+08	2026-10-17 18:29:29.409268+08
7	SUG_JUDGEMENT	R-C03	需研判表述	第 {页码} 页“{原文}”需审核员研判：{风险说明}。如确有不妥，请结合党章和理论学习修改相关表述。	\N	t	\N	2026-10-17 18:29:29.409279+08	2026-10-17 18:29:29.409279+08
8	SUG_FORMAT	\N	形式规范	《{材料名}》{问题描述}。请按学校材料格式要求修改后重新上传。	\N	t	\N	2026-10-17 18:29:29.409289+08	2026-10-17 18:29:29.40929+08
9	SUG_CONTENT	\N	内容要素	《{材料名}》缺少要素“{要素名}”，请按模板补写相关内容。	\N	t	\N	2026-10-17 18:29:29.4093+08	2026-10-17 18:29:29.409301+08
\.


--
-- Data for Name: system_settings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.system_settings (key, value, description, updated_by, updated_at) FROM stdin;
upload	{"max_zip_mb": 500, "allowed_ext": ["pdf", "jpg", "jpeg", "png", "docx"], "max_file_mb": 20}	上传限制	\N	2026-10-17 18:29:20.455516+08
retention	{"export_days": 7, "material_years": 10}	材料与导出文件保留期限	\N	2026-10-17 18:29:20.455516+08
notification	{"sms": false, "email": false, "in_app": true, "deadline_remind_days": [3, 1]}	通知开关	\N	2026-10-17 18:29:20.455516+08
ai	{"model": "", "base_url": "", "timeout_s": 60, "api_key_enc": "", "desensitize": true, "llm_enabled": false, "temperature": 0.1, "max_concurrency": 2, "classify_confidence_threshold": 0.7}	大模型配置（密钥加密存储，不回显）	\N	2026-10-17 18:29:20.455516+08
ocr	{"engine": "auto", "min_dpi": 150, "timeout_s": 120, "blur_threshold": 60}	OCR 配置：auto 表示检测到 PaddleOCR 则启用，否则跳过 OCR 并提示人工核对	\N	2026-10-17 18:29:20.455516+08
security	{"lock_minutes": 15, "max_failed_login": 5, "refresh_token_days": 7, "access_token_minutes": 120}	登录安全参数	\N	2026-10-17 18:29:20.455516+08
worker	{"concurrency": 2, "poll_interval_s": 1, "heartbeat_timeout_s": 300}	后台任务执行参数	\N	2026-10-17 18:29:20.455516+08
calendar	{"holidays": [], "extra_workdays": [], "period_min_tail_days": 30}	工作日计算（默认周一至周五，节假日与调休日 YYYY-MM-DD）；按周期计份时末段不足该天数不计一期	\N	2026-10-17 18:29:20.455516+08
\.


--
-- Data for Name: time_node_defs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.time_node_defs (id, code, name, value_kind, has_hours, stage_code, required_from_stage, source_material_codes, extract_keywords, derive_expr, sort_order, is_active, updated_by, created_at, updated_at) FROM stdin;
1	T01	出生日期	DATE	f	1	1	["APPLICATION_LETTER", "AUTOBIOGRAPHY", "APPLICATION_FORM"]	["出生日期", "生于"]	\N	1	t	\N	2026-10-17 18:29:29.439627+08	2026-10-17 18:29:29.439629+08
2	T02	递交入党申请书日期	DATE	f	1	1	["APPLICATION_LETTER"]	["入党申请", "申请入党"]	\N	2	t	\N	2026-10-17 18:29:29.43968+08	2026-10-17 18:29:29.43968+08
3	T03	党组织派人谈话日期	DATE	f	1	2	["PARTY_TALK_RECORD"]	["谈话"]	\N	3	t	\N	2026-10-17 18:29:29.439698+08	2026-10-17 18:29:29.439698+08
4	T04	确定为入党积极分子日期	DATE	f	2	2	["ACTIVIST_MEETING_RECORD", "ACTIVIST_FILING"]	["确定为入党积极分子", "列为入党积极分子"]	\N	4	t	\N	2026-10-17 18:29:29.439714+08	2026-10-17 18:29:29.439715+08
5	T05	指定培养联系人日期	DATE	f	2	2	["RECORD_BOOK_ACTIVIST"]	["培养联系人"]	\N	5	t	\N	2026-10-17 18:29:29.439729+08	2026-10-17 18:29:29.439729+08
6	T06	思想汇报日期	DATE_SEQ	f	2	2	["THOUGHT_REPORT"]	["思想汇报"]	\N	6	t	\N	2026-10-17 18:29:29.439743+08	2026-10-17 18:29:29.439744+08
7	T07	培养考察记录日期	DATE_SEQ	f	2	2	["RECORD_BOOK_ACTIVIST", "RECORD_BOOK_CANDIDATE", "RECORD_BOOK_PROBATIONARY"]	["考察", "写实"]	\N	7	t	\N	2026-10-17 18:29:29.439758+08	2026-10-17 18:29:29.439758+08
8	T08	确定为发展对象日期	DATE	f	3	3	["CANDIDATE_MEETING_RECORD"]	["确定为发展对象"]	\N	8	t	\N	2026-10-17 18:29:29.439772+08	2026-10-17 18:29:29.439772+08
9	T09	政治审查完成日期	DATE	f	3	4	["POLITICAL_REVIEW"]	["政治审查", "政审"]	\N	9	t	\N	2026-10-17 18:29:29.439785+08	2026-10-17 18:29:29.439785+08
10	T10	集中培训起止与学时	DATE_RANGE	t	3	4	["TRAINING_CERT"]	["培训", "学时", "结业"]	\N	10	t	\N	2026-10-17 18:29:29.439799+08	2026-10-17 18:29:29.4398+08
11	T11	发展对象公示起止	DATE_RANGE	f	4	4	["CANDIDATE_PUBLICITY"]	["公示"]	\N	11	t	\N	2026-10-17 18:29:29.439813+08	2026-10-17 18:29:29.439813+08
12	T12	上级党委预审日期	DATE	f	4	4	["PRE_REVIEW_OPINION"]	["预审"]	\N	12	t	\N	2026-10-17 18:29:29.439827+08	2026-10-17 18:29:29.439827+08
13	T13	填写入党志愿书日期	DATE	f	4	4	["APPLICATION_FORM"]	["志愿书"]	\N	13	t	\N	2026-10-17 18:29:29.43984+08	2026-10-17 18:29:29.43984+08
14	T14	支部大会接收预备党员日期	DATE	f	4	4	["ADMISSION_MEETING_RECORD", "APPLICATION_FORM"]	["支部大会", "接收为预备党员"]	\N	14	t	\N	2026-10-17 18:29:29.439853+08	2026-10-17 18:29:29.439854+08
15	T15	上级党委派人谈话日期	DATE	f	4	4	["COMMITTEE_TALK_RECORD"]	["谈话"]	\N	15	t	\N	2026-10-17 18:29:29.439867+08	2026-10-17 18:29:29.439867+08
16	T16	上级党委审批预备党员日期	DATE	f	4	4	["ADMISSION_APPROVAL"]	["审批", "预备党员"]	\N	16	t	\N	2026-10-17 18:29:29.43988+08	2026-10-17 18:29:29.439881+08
17	T17	编入党支部日期	DATE	f	4	5	["RECORD_BOOK_PROBATIONARY"]	["编入"]	\N	17	t	\N	2026-10-17 18:29:29.439894+08	2026-10-17 18:29:29.439894+08
18	T18	递交转正申请书日期	DATE	f	5	5	["REGULARIZATION_LETTER"]	["转正申请"]	\N	18	t	\N	2026-10-17 18:29:29.439909+08	2026-10-17 18:29:29.439909+08
19	T19	转正公示起止	DATE_RANGE	f	5	5	["REGULARIZATION_PUBLICITY"]	["转正公示", "公示"]	\N	19	t	\N	2026-10-17 18:29:29.439923+08	2026-10-17 18:29:29.439923+08
20	T20	支部大会讨论转正日期	DATE	f	5	5	["REGULARIZATION_MEETING_RECORD"]	["转正", "支部大会"]	\N	20	t	\N	2026-10-17 18:29:29.439936+08	2026-10-17 18:29:29.439936+08
21	T21	上级党委审批转正日期	DATE	f	5	5	["REGULARIZATION_APPROVAL"]	["审批", "正式党员"]	\N	21	t	\N	2026-10-17 18:29:29.439949+08	2026-10-17 18:29:29.43995+08
22	D01	预备期满日	DERIVED	f	4	5	[]	[]	{"base": "T14", "offset": {"unit": "YEAR", "value": 1}}	22	t	\N	2026-10-17 18:29:29.439963+08	2026-10-17 18:29:29.439963+08
\.


--
-- Data for Name: time_node_extractions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.time_node_extractions (id, archive_id, node_code, material_id, material_version_id, seq_index, value_date, value_end_date, hours, raw_text, invalid_reason, page_no, bbox, confidence, method, is_current, created_at) FROM stdin;
1	1	T01	\N	\N	0	2003-05-12	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:06.460501+08
2	1	T02	\N	\N	0	2023-03-15	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:06.460573+08
3	1	T03	\N	\N	0	2023-03-20	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:06.46059+08
4	1	T04	\N	\N	0	2024-09-10	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:06.460604+08
5	1	T08	\N	\N	0	2025-08-30	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:06.460616+08
6	2	T01	\N	\N	0	2003-05-12	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:06.703918+08
7	2	T02	\N	\N	0	2023-03-15	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:06.703957+08
8	2	T04	\N	\N	0	2024-09-10	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:06.703972+08
9	2	T08	\N	\N	0	2025-08-30	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:06.703986+08
10	3	T02	\N	\N	0	2023-03-15	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:06.789709+08
11	3	T04	\N	\N	0	2024-09-10	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:06.789762+08
12	4	T02	\N	\N	0	2022-03-15	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:07.448016+08
13	4	T04	\N	\N	0	2023-04-01	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:07.448068+08
14	4	T08	\N	\N	0	2024-05-01	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:07.448091+08
15	4	T14	\N	\N	0	2025-06-01	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:07.448109+08
16	5	T14	\N	\N	0	2024-10-01	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:07.751879+08
17	5	T16	\N	\N	0	2024-10-20	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:07.751932+08
18	5	T18	\N	\N	0	2025-09-20	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:07.751953+08
19	5	T20	\N	\N	0	2025-10-08	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:07.751971+08
20	6	T01	\N	\N	0	2003-05-12	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:07.956303+08
21	6	T02	\N	\N	0	2023-03-15	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:07.956345+08
22	6	T03	\N	\N	0	2023-03-28	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:07.95636+08
23	7	T01	\N	\N	0	2003-05-12	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:08.473133+08
24	7	T02	\N	\N	0	2023-03-15	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:08.473187+08
25	7	T03	\N	\N	0	2023-03-20	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:08.473209+08
26	7	T04	\N	\N	0	2024-09-10	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:08.473227+08
27	7	T08	\N	\N	0	2025-08-30	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:08.473243+08
28	8	T01	\N	\N	0	2003-05-12	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:08.702846+08
29	8	T02	\N	\N	0	2023-03-15	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:08.702891+08
30	8	T04	\N	\N	0	2024-09-10	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:08.702907+08
31	8	T08	\N	\N	0	2025-08-30	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:08.702921+08
32	9	T02	\N	\N	0	2023-03-15	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:08.796517+08
33	9	T04	\N	\N	0	2024-09-10	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:08.796568+08
34	10	T02	\N	\N	0	2022-03-15	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:09.465628+08
35	10	T04	\N	\N	0	2023-04-01	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:09.465669+08
36	10	T08	\N	\N	0	2024-05-01	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:09.465686+08
37	10	T14	\N	\N	0	2025-06-01	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:09.465699+08
38	11	T14	\N	\N	0	2024-10-01	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:09.754804+08
39	11	T16	\N	\N	0	2024-10-20	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:09.754842+08
40	11	T18	\N	\N	0	2025-09-20	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:09.754857+08
41	11	T20	\N	\N	0	2025-10-08	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:09.754869+08
42	12	T01	\N	\N	0	2003-05-12	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:09.947636+08
43	12	T02	\N	\N	0	2023-03-15	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:09.947673+08
44	12	T03	\N	\N	0	2023-03-28	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:09.947689+08
45	13	T01	\N	\N	0	2003-05-12	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:10.566179+08
46	13	T02	\N	\N	0	2023-03-15	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:10.566217+08
47	13	T03	\N	\N	0	2023-03-20	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:10.566237+08
48	13	T04	\N	\N	0	2024-09-10	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:10.566255+08
49	13	T08	\N	\N	0	2025-08-30	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:10.566272+08
50	14	T01	\N	\N	0	2003-05-12	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:10.885761+08
51	14	T02	\N	\N	0	2023-03-15	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:10.885827+08
52	14	T04	\N	\N	0	2024-09-10	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:10.88585+08
53	14	T08	\N	\N	0	2025-08-30	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:10.885867+08
54	15	T02	\N	\N	0	2023-03-15	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:11.008374+08
55	15	T04	\N	\N	0	2024-09-10	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:11.008429+08
56	16	T02	\N	\N	0	2022-03-15	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:12.008318+08
57	16	T04	\N	\N	0	2023-04-01	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:12.008358+08
58	16	T08	\N	\N	0	2024-05-01	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:12.008379+08
59	16	T14	\N	\N	0	2025-06-01	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:12.008397+08
60	17	T14	\N	\N	0	2024-10-01	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:12.420158+08
61	17	T16	\N	\N	0	2024-10-20	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:12.420218+08
62	17	T18	\N	\N	0	2025-09-20	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:12.420239+08
63	17	T20	\N	\N	0	2025-10-08	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:12.420255+08
64	18	T01	\N	\N	0	2003-05-12	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:12.672392+08
65	18	T02	\N	\N	0	2023-03-15	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:12.672439+08
66	18	T03	\N	\N	0	2023-03-28	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:12.67246+08
67	19	T01	\N	\N	0	2003-05-12	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:13.30932+08
68	19	T02	\N	\N	0	2023-03-15	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:13.309367+08
69	19	T03	\N	\N	0	2023-03-20	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:13.309392+08
70	19	T04	\N	\N	0	2024-09-10	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:13.309411+08
71	19	T08	\N	\N	0	2025-08-30	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:13.30943+08
72	20	T01	\N	\N	0	2003-05-12	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:13.645881+08
73	20	T02	\N	\N	0	2023-03-15	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:13.645925+08
74	20	T04	\N	\N	0	2024-09-10	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:13.645945+08
75	20	T08	\N	\N	0	2025-08-30	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:13.645962+08
76	21	T02	\N	\N	0	2023-03-15	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:13.768513+08
77	21	T04	\N	\N	0	2024-09-10	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:13.768562+08
78	22	T02	\N	\N	0	2022-03-15	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:14.655215+08
79	22	T04	\N	\N	0	2023-04-01	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:14.655251+08
80	22	T08	\N	\N	0	2024-05-01	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:14.655265+08
81	22	T14	\N	\N	0	2025-06-01	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:14.655277+08
82	23	T14	\N	\N	0	2024-10-01	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:14.950203+08
83	23	T16	\N	\N	0	2024-10-20	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:14.95024+08
84	23	T18	\N	\N	0	2025-09-20	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:14.950255+08
85	23	T20	\N	\N	0	2025-10-08	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:14.950268+08
86	24	T01	\N	\N	0	2003-05-12	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:15.149659+08
87	24	T02	\N	\N	0	2023-03-15	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:15.149696+08
88	24	T03	\N	\N	0	2023-03-28	\N	\N	\N	\N	\N	\N	\N	IMPORT	t	2026-10-17 18:36:15.149712+08
89	1	T02	1	1	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.9	RULE	t	2026-10-17 18:36:15.891923+08
90	1	T01	1	1	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:15.891988+08
91	1	T06	1	1	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.85	RULE	t	2026-10-17 18:36:15.892012+08
92	1	T06	2	2	0	2024-12-20	\N	\N	2024年12月20日	\N	1	[49.0, 253.7880096435547, 139.046875, 271.416015625]	0.9	RULE	t	2026-10-17 18:36:15.952588+08
93	1	T06	3	3	0	2025-03-25	\N	\N	2025年3月25日	\N	1	[49.0, 253.7880096435547, 132.291015625, 271.416015625]	0.9	RULE	t	2026-10-17 18:36:16.010986+08
95	1	T08	5	5	0	2025-08-30	\N	\N	2025年8月30日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.9	RULE	t	2026-10-17 18:36:16.102277+08
96	1	T06	5	5	0	2025-08-30	\N	\N	2025年8月30日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:16.102334+08
104	2	T06	9	9	0	2025-08-01	\N	\N	2025年8月1日	\N	1	[49.0, 253.7880096435547, 125.53515625, 271.416015625]	0.9	RULE	t	2026-10-17 18:36:16.3186+08
105	3	T02	10	10	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.9	RULE	t	2026-10-17 18:36:16.374167+08
106	3	T01	10	10	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:16.374221+08
107	3	T06	10	10	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.85	RULE	t	2026-10-17 18:36:16.374245+08
108	4	T13	11	11	0	2025-05-20	\N	\N	2025年5月20日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.9	RULE	t	2026-10-17 18:36:16.42694+08
109	4	T01	11	11	0	2003-05-12	\N	\N	2003-05-12	\N	1	\N	0.9	RULE	t	2026-10-17 18:36:16.42699+08
110	4	T06	11	11	0	2025-05-20	\N	\N	2025年5月20日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:16.427013+08
115	4	T09	13	13	0	2024-06-01	\N	\N	2024年6月1日	\N	1	[49.0, 124.18800354003906, 125.53515625, 141.81600952148438]	0.9	RULE	t	2026-10-17 18:36:16.512953+08
116	4	T06	13	13	0	2024-06-01	\N	\N	2024年6月1日	\N	1	[49.0, 124.18800354003906, 125.53515625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:16.513005+08
120	4	T11	15	15	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:16.594838+08
121	4	T06	15	15	0	2025-04-26	\N	\N	2025年4月26日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:16.594889+08
122	4	T19	15	15	0	2025-04-20	\N	\N	2025年4月20日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:16.594913+08
123	4	T19	15	15	0	2025-04-26	\N	\N	2025年4月26日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:16.594933+08
129	5	T20	18	18	0	2025-10-08	\N	\N	2025年10月8日	\N	1	[49.0, 91.78800201416016, 132.291015625, 109.41600799560547]	0.9	RULE	t	2026-10-17 18:36:16.731517+08
130	5	T06	18	18	0	2025-10-08	\N	\N	2025年10月8日	\N	1	[49.0, 91.78800201416016, 132.291015625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:16.731572+08
131	5	T14	18	18	0	2025-10-08	\N	\N	2025年10月8日	\N	1	[49.0, 91.78800201416016, 132.291015625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:16.731596+08
141	6	T03	21	21	0	2023-03-28	\N	\N	2023年3月28日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.9	RULE	t	2026-10-17 18:36:16.871336+08
142	6	T06	21	21	0	2023-03-28	\N	\N	2023年3月28日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:16.871386+08
143	6	T15	21	21	0	2023-03-28	\N	\N	2023年3月28日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:16.871408+08
144	7	T02	22	22	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.9	RULE	t	2026-10-17 18:36:16.924745+08
145	7	T01	22	22	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:16.924787+08
146	7	T06	22	22	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.85	RULE	t	2026-10-17 18:36:16.92481+08
148	7	T06	24	24	0	2025-03-25	\N	\N	2025年3月25日	\N	1	[49.0, 253.7880096435547, 132.291015625, 271.416015625]	0.9	RULE	t	2026-10-17 18:36:17.008129+08
150	7	T08	26	26	0	2025-08-30	\N	\N	2025年8月30日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.9	RULE	t	2026-10-17 18:36:17.088718+08
151	7	T06	26	26	0	2025-08-30	\N	\N	2025年8月30日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:17.088768+08
157	8	T01	29	29	0	2004-01-01	\N	\N	2004-01-01	\N	1	\N	0.9	RULE	t	2026-10-17 18:36:17.231493+08
158	8	T06	29	29	0	2004-01-01	\N	\N	2004年1月1日	\N	1	[49.0, 91.78800201416016, 345.05078125, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:17.231548+08
163	10	T13	32	32	0	2025-05-20	\N	\N	2025年5月20日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.9	RULE	t	2026-10-17 18:36:17.391807+08
164	10	T01	32	32	0	2003-05-12	\N	\N	2003-05-12	\N	1	\N	0.9	RULE	t	2026-10-17 18:36:17.391857+08
165	10	T06	32	32	0	2025-05-20	\N	\N	2025年5月20日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:17.39188+08
170	10	T09	34	34	0	2024-06-01	\N	\N	2024年6月1日	\N	1	[49.0, 124.18800354003906, 125.53515625, 141.81600952148438]	0.9	RULE	t	2026-10-17 18:36:17.477256+08
171	10	T06	34	34	0	2024-06-01	\N	\N	2024年6月1日	\N	1	[49.0, 124.18800354003906, 125.53515625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:17.47731+08
175	10	T11	36	36	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:17.558794+08
176	10	T06	36	36	0	2025-04-26	\N	\N	2025年4月26日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:17.558846+08
177	10	T19	36	36	0	2025-04-20	\N	\N	2025年4月20日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:17.558868+08
178	10	T19	36	36	0	2025-04-26	\N	\N	2025年4月26日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:17.558887+08
184	11	T20	39	39	0	2025-10-08	\N	\N	2025年10月8日	\N	1	[49.0, 91.78800201416016, 132.291015625, 109.41600799560547]	0.9	RULE	t	2026-10-17 18:36:17.707048+08
185	11	T06	39	39	0	2025-10-08	\N	\N	2025年10月8日	\N	1	[49.0, 91.78800201416016, 132.291015625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:17.707099+08
186	11	T14	39	39	0	2025-10-08	\N	\N	2025年10月8日	\N	1	[49.0, 91.78800201416016, 132.291015625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:17.707121+08
196	12	T03	42	42	0	2023-03-28	\N	\N	2023年3月28日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.9	RULE	t	2026-10-17 18:36:17.846097+08
197	12	T06	42	42	0	2023-03-28	\N	\N	2023年3月28日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:17.846151+08
94	1	T06	4	4	0	2025-07-01	\N	\N	2025年7月1日	\N	1	[49.0, 253.7880096435547, 125.53515625, 271.416015625]	0.9	RULE	t	2026-10-17 18:36:16.052989+08
97	1	T01	6	6	0	2003-05-12	\N	\N	2003-05-12	\N	1	\N	0.9	RULE	t	2026-10-17 18:36:16.149769+08
98	1	T06	6	6	0	2003-05-12	\N	\N	2003年5月12日	\N	1	[49.0, 91.78800201416016, 543.806640625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:16.149825+08
99	2	T02	7	7	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.9	RULE	t	2026-10-17 18:36:16.211337+08
100	2	T01	7	7	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:16.2114+08
101	2	T06	7	7	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.85	RULE	t	2026-10-17 18:36:16.211424+08
102	2	T01	8	8	0	2004-01-01	\N	\N	2004-01-01	\N	1	\N	0.9	RULE	t	2026-10-17 18:36:16.275109+08
103	2	T06	8	8	0	2004-01-01	\N	\N	2004年1月1日	\N	1	[49.0, 91.78800201416016, 345.05078125, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:16.275162+08
111	4	T14	12	12	0	2025-06-01	\N	\N	2025年6月1日	\N	1	[49.0, 91.78800201416016, 125.53515625, 109.41600799560547]	0.9	RULE	t	2026-10-17 18:36:16.470648+08
112	4	T06	12	12	0	2025-06-01	\N	\N	2025年6月1日	\N	1	[49.0, 91.78800201416016, 125.53515625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:16.4707+08
113	4	T16	12	12	0	2025-06-01	\N	\N	2025年6月1日	\N	1	[49.0, 91.78800201416016, 125.53515625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:16.470724+08
114	4	T20	12	12	0	2025-06-01	\N	\N	2025年6月1日	\N	1	[49.0, 91.78800201416016, 125.53515625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:16.470746+08
117	4	T10	14	14	0	2024-07-01	2024-07-05	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:16.553365+08
118	4	T10	14	14	0	2024-07-01	2024-07-05	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:16.553418+08
119	4	T06	14	14	0	2024-07-05	\N	\N	2024年7月5日	\N	1	[49.0, 91.78800201416016, 330.61328125, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:16.553442+08
124	4	T12	16	16	0	2025-05-10	\N	\N	2025年5月10日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.9	RULE	t	2026-10-17 18:36:16.634761+08
125	4	T06	16	16	0	2025-05-10	\N	\N	2025年5月10日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:16.634811+08
126	5	T18	17	17	0	2025-09-20	\N	\N	2025年9月20日	\N	1	[49.0, 221.38800048828125, 132.291015625, 239.01600646972656]	0.9	RULE	t	2026-10-17 18:36:16.685143+08
127	5	T06	17	17	0	2025-09-20	\N	\N	2025年9月20日	\N	1	[49.0, 221.38800048828125, 132.291015625, 239.01600646972656]	0.85	RULE	t	2026-10-17 18:36:16.685191+08
128	5	T20	17	17	0	2025-09-20	\N	\N	2025年9月20日	\N	1	[49.0, 221.38800048828125, 132.291015625, 239.01600646972656]	0.85	RULE	t	2026-10-17 18:36:16.685213+08
132	5	T19	19	19	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:16.773264+08
133	5	T06	19	19	0	2025-10-08	\N	\N	2025年10月8日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:16.77334+08
134	5	T11	19	19	0	2025-09-25	\N	\N	2025年9月25日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:16.773376+08
135	5	T11	19	19	0	2025-10-08	\N	\N	2025年10月8日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:16.773406+08
136	5	T20	19	19	0	2025-09-25	\N	\N	2025年9月25日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:16.773433+08
137	5	T20	19	19	0	2025-10-08	\N	\N	2025年10月8日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:16.773459+08
138	6	T02	20	20	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.9	RULE	t	2026-10-17 18:36:16.82922+08
139	6	T01	20	20	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:16.829265+08
140	6	T06	20	20	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.85	RULE	t	2026-10-17 18:36:16.829288+08
147	7	T06	23	23	0	2024-12-20	\N	\N	2024年12月20日	\N	1	[49.0, 253.7880096435547, 139.046875, 271.416015625]	0.9	RULE	t	2026-10-17 18:36:16.966354+08
149	7	T06	25	25	0	2025-07-01	\N	\N	2025年7月1日	\N	1	[49.0, 253.7880096435547, 125.53515625, 271.416015625]	0.9	RULE	t	2026-10-17 18:36:17.048156+08
152	7	T01	27	27	0	2003-05-12	\N	\N	2003-05-12	\N	1	\N	0.9	RULE	t	2026-10-17 18:36:17.130481+08
153	7	T06	27	27	0	2003-05-12	\N	\N	2003年5月12日	\N	1	[49.0, 91.78800201416016, 543.806640625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:17.130536+08
154	8	T02	28	28	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.9	RULE	t	2026-10-17 18:36:17.182653+08
155	8	T01	28	28	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:17.18271+08
156	8	T06	28	28	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.85	RULE	t	2026-10-17 18:36:17.182735+08
159	8	T06	30	30	0	2025-08-01	\N	\N	2025年8月1日	\N	1	[49.0, 253.7880096435547, 125.53515625, 271.416015625]	0.9	RULE	t	2026-10-17 18:36:17.281127+08
160	9	T02	31	31	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.9	RULE	t	2026-10-17 18:36:17.351529+08
161	9	T01	31	31	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:17.351574+08
162	9	T06	31	31	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.85	RULE	t	2026-10-17 18:36:17.351598+08
166	10	T14	33	33	0	2025-06-01	\N	\N	2025年6月1日	\N	1	[49.0, 91.78800201416016, 125.53515625, 109.41600799560547]	0.9	RULE	t	2026-10-17 18:36:17.433341+08
167	10	T06	33	33	0	2025-06-01	\N	\N	2025年6月1日	\N	1	[49.0, 91.78800201416016, 125.53515625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:17.433391+08
168	10	T16	33	33	0	2025-06-01	\N	\N	2025年6月1日	\N	1	[49.0, 91.78800201416016, 125.53515625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:17.433413+08
169	10	T20	33	33	0	2025-06-01	\N	\N	2025年6月1日	\N	1	[49.0, 91.78800201416016, 125.53515625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:17.433432+08
172	10	T10	35	35	0	2024-07-01	2024-07-05	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:17.518204+08
173	10	T10	35	35	0	2024-07-01	2024-07-05	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:17.518258+08
174	10	T06	35	35	0	2024-07-05	\N	\N	2024年7月5日	\N	1	[49.0, 91.78800201416016, 330.61328125, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:17.518281+08
179	10	T12	37	37	0	2025-05-10	\N	\N	2025年5月10日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.9	RULE	t	2026-10-17 18:36:17.601891+08
180	10	T06	37	37	0	2025-05-10	\N	\N	2025年5月10日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:17.601941+08
181	11	T18	38	38	0	2025-09-20	\N	\N	2025年9月20日	\N	1	[49.0, 221.38800048828125, 132.291015625, 239.01600646972656]	0.9	RULE	t	2026-10-17 18:36:17.658756+08
182	11	T06	38	38	0	2025-09-20	\N	\N	2025年9月20日	\N	1	[49.0, 221.38800048828125, 132.291015625, 239.01600646972656]	0.85	RULE	t	2026-10-17 18:36:17.658807+08
183	11	T20	38	38	0	2025-09-20	\N	\N	2025年9月20日	\N	1	[49.0, 221.38800048828125, 132.291015625, 239.01600646972656]	0.85	RULE	t	2026-10-17 18:36:17.658831+08
187	11	T19	40	40	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:17.746828+08
188	11	T06	40	40	0	2025-10-08	\N	\N	2025年10月8日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:17.746883+08
189	11	T11	40	40	0	2025-09-25	\N	\N	2025年9月25日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:17.746907+08
190	11	T11	40	40	0	2025-10-08	\N	\N	2025年10月8日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:17.746927+08
191	11	T20	40	40	0	2025-09-25	\N	\N	2025年9月25日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:17.746946+08
192	11	T20	40	40	0	2025-10-08	\N	\N	2025年10月8日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:17.746963+08
193	12	T02	41	41	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.9	RULE	t	2026-10-17 18:36:17.803486+08
194	12	T01	41	41	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:17.803531+08
195	12	T06	41	41	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.85	RULE	t	2026-10-17 18:36:17.803555+08
203	13	T06	45	45	0	2025-03-25	\N	\N	2025年3月25日	\N	1	[49.0, 253.7880096435547, 132.291015625, 271.416015625]	0.9	RULE	t	2026-10-17 18:36:17.991729+08
205	13	T08	47	47	0	2025-08-30	\N	\N	2025年8月30日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.9	RULE	t	2026-10-17 18:36:18.079927+08
206	13	T06	47	47	0	2025-08-30	\N	\N	2025年8月30日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:18.079983+08
198	12	T15	42	42	0	2023-03-28	\N	\N	2023年3月28日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:17.846174+08
199	13	T02	43	43	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.9	RULE	t	2026-10-17 18:36:17.893824+08
200	13	T01	43	43	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:17.893876+08
201	13	T06	43	43	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.85	RULE	t	2026-10-17 18:36:17.8939+08
202	13	T06	44	44	0	2024-12-20	\N	\N	2024年12月20日	\N	1	[49.0, 253.7880096435547, 139.046875, 271.416015625]	0.9	RULE	t	2026-10-17 18:36:17.946329+08
204	13	T06	46	46	0	2025-07-01	\N	\N	2025年7月1日	\N	1	[49.0, 253.7880096435547, 125.53515625, 271.416015625]	0.9	RULE	t	2026-10-17 18:36:18.037556+08
207	13	T01	48	48	0	2003-05-12	\N	\N	2003-05-12	\N	1	\N	0.9	RULE	t	2026-10-17 18:36:18.125528+08
208	13	T06	48	48	0	2003-05-12	\N	\N	2003年5月12日	\N	1	[49.0, 91.78800201416016, 543.806640625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:18.125596+08
209	14	T02	49	49	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.9	RULE	t	2026-10-17 18:36:18.182345+08
210	14	T01	49	49	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:18.182403+08
211	14	T06	49	49	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.85	RULE	t	2026-10-17 18:36:18.182427+08
212	14	T01	50	50	0	2004-01-01	\N	\N	2004-01-01	\N	1	\N	0.9	RULE	t	2026-10-17 18:36:18.232582+08
213	14	T06	50	50	0	2004-01-01	\N	\N	2004年1月1日	\N	1	[49.0, 91.78800201416016, 345.05078125, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:18.232632+08
218	16	T13	53	53	0	2025-05-20	\N	\N	2025年5月20日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.9	RULE	t	2026-10-17 18:36:18.36844+08
219	16	T01	53	53	0	2003-05-12	\N	\N	2003-05-12	\N	1	\N	0.9	RULE	t	2026-10-17 18:36:18.368492+08
220	16	T06	53	53	0	2025-05-20	\N	\N	2025年5月20日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:18.368516+08
225	16	T09	55	55	0	2024-06-01	\N	\N	2024年6月1日	\N	1	[49.0, 124.18800354003906, 125.53515625, 141.81600952148438]	0.9	RULE	t	2026-10-17 18:36:18.458697+08
226	16	T06	55	55	0	2024-06-01	\N	\N	2024年6月1日	\N	1	[49.0, 124.18800354003906, 125.53515625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:18.458751+08
230	16	T11	57	57	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:18.549015+08
231	16	T06	57	57	0	2025-04-26	\N	\N	2025年4月26日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:18.54907+08
232	16	T19	57	57	0	2025-04-20	\N	\N	2025年4月20日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:18.549096+08
233	16	T19	57	57	0	2025-04-26	\N	\N	2025年4月26日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:18.549118+08
239	17	T20	60	60	0	2025-10-08	\N	\N	2025年10月8日	\N	1	[49.0, 91.78800201416016, 132.291015625, 109.41600799560547]	0.9	RULE	t	2026-10-17 18:36:18.689168+08
240	17	T06	60	60	0	2025-10-08	\N	\N	2025年10月8日	\N	1	[49.0, 91.78800201416016, 132.291015625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:18.689221+08
241	17	T14	60	60	0	2025-10-08	\N	\N	2025年10月8日	\N	1	[49.0, 91.78800201416016, 132.291015625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:18.689243+08
251	18	T03	63	63	0	2023-03-28	\N	\N	2023年3月28日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.9	RULE	t	2026-10-17 18:36:18.830792+08
252	18	T06	63	63	0	2023-03-28	\N	\N	2023年3月28日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:18.830846+08
253	18	T15	63	63	0	2023-03-28	\N	\N	2023年3月28日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:18.83087+08
254	19	T02	64	64	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.9	RULE	t	2026-10-17 18:36:18.88773+08
255	19	T01	64	64	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:18.887775+08
256	19	T06	64	64	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.85	RULE	t	2026-10-17 18:36:18.887798+08
258	19	T06	66	66	0	2025-03-25	\N	\N	2025年3月25日	\N	1	[49.0, 253.7880096435547, 132.291015625, 271.416015625]	0.9	RULE	t	2026-10-17 18:36:18.974572+08
260	19	T08	68	68	0	2025-08-30	\N	\N	2025年8月30日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.9	RULE	t	2026-10-17 18:36:19.060778+08
261	19	T06	68	68	0	2025-08-30	\N	\N	2025年8月30日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:19.060863+08
267	20	T01	71	71	0	2004-01-01	\N	\N	2004-01-01	\N	1	\N	0.9	RULE	t	2026-10-17 18:36:19.210574+08
268	20	T06	71	71	0	2004-01-01	\N	\N	2004年1月1日	\N	1	[49.0, 91.78800201416016, 345.05078125, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:19.210652+08
273	22	T13	74	74	0	2025-05-20	\N	\N	2025年5月20日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.9	RULE	t	2026-10-17 18:36:19.358973+08
274	22	T01	74	74	0	2003-05-12	\N	\N	2003-05-12	\N	1	\N	0.9	RULE	t	2026-10-17 18:36:19.35903+08
275	22	T06	74	74	0	2025-05-20	\N	\N	2025年5月20日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:19.359054+08
280	22	T09	76	76	0	2024-06-01	\N	\N	2024年6月1日	\N	1	[49.0, 124.18800354003906, 125.53515625, 141.81600952148438]	0.9	RULE	t	2026-10-17 18:36:19.448246+08
281	22	T06	76	76	0	2024-06-01	\N	\N	2024年6月1日	\N	1	[49.0, 124.18800354003906, 125.53515625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:19.448316+08
285	22	T11	78	78	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:19.537388+08
286	22	T06	78	78	0	2025-04-26	\N	\N	2025年4月26日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:19.537446+08
287	22	T19	78	78	0	2025-04-20	\N	\N	2025年4月20日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:19.53747+08
288	22	T19	78	78	0	2025-04-26	\N	\N	2025年4月26日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:19.537491+08
214	14	T06	51	51	0	2025-08-01	\N	\N	2025年8月1日	\N	1	[49.0, 253.7880096435547, 125.53515625, 271.416015625]	0.9	RULE	t	2026-10-17 18:36:18.274737+08
215	15	T02	52	52	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.9	RULE	t	2026-10-17 18:36:18.329082+08
216	15	T01	52	52	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:18.329131+08
217	15	T06	52	52	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.85	RULE	t	2026-10-17 18:36:18.329156+08
221	16	T14	54	54	0	2025-06-01	\N	\N	2025年6月1日	\N	1	[49.0, 91.78800201416016, 125.53515625, 109.41600799560547]	0.9	RULE	t	2026-10-17 18:36:18.415081+08
222	16	T06	54	54	0	2025-06-01	\N	\N	2025年6月1日	\N	1	[49.0, 91.78800201416016, 125.53515625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:18.41514+08
223	16	T16	54	54	0	2025-06-01	\N	\N	2025年6月1日	\N	1	[49.0, 91.78800201416016, 125.53515625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:18.415165+08
224	16	T20	54	54	0	2025-06-01	\N	\N	2025年6月1日	\N	1	[49.0, 91.78800201416016, 125.53515625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:18.415187+08
227	16	T10	56	56	0	2024-07-01	2024-07-05	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:18.502108+08
228	16	T10	56	56	0	2024-07-01	2024-07-05	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:18.502159+08
229	16	T06	56	56	0	2024-07-05	\N	\N	2024年7月5日	\N	1	[49.0, 91.78800201416016, 330.61328125, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:18.502182+08
234	16	T12	58	58	0	2025-05-10	\N	\N	2025年5月10日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.9	RULE	t	2026-10-17 18:36:18.592289+08
235	16	T06	58	58	0	2025-05-10	\N	\N	2025年5月10日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:18.592341+08
236	17	T18	59	59	0	2025-09-20	\N	\N	2025年9月20日	\N	1	[49.0, 221.38800048828125, 132.291015625, 239.01600646972656]	0.9	RULE	t	2026-10-17 18:36:18.645389+08
237	17	T06	59	59	0	2025-09-20	\N	\N	2025年9月20日	\N	1	[49.0, 221.38800048828125, 132.291015625, 239.01600646972656]	0.85	RULE	t	2026-10-17 18:36:18.645435+08
238	17	T20	59	59	0	2025-09-20	\N	\N	2025年9月20日	\N	1	[49.0, 221.38800048828125, 132.291015625, 239.01600646972656]	0.85	RULE	t	2026-10-17 18:36:18.645458+08
242	17	T19	61	61	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:18.731262+08
243	17	T06	61	61	0	2025-10-08	\N	\N	2025年10月8日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:18.731318+08
244	17	T11	61	61	0	2025-09-25	\N	\N	2025年9月25日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:18.731341+08
245	17	T11	61	61	0	2025-10-08	\N	\N	2025年10月8日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:18.731363+08
246	17	T20	61	61	0	2025-09-25	\N	\N	2025年9月25日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:18.731391+08
247	17	T20	61	61	0	2025-10-08	\N	\N	2025年10月8日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:18.731421+08
248	18	T02	62	62	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.9	RULE	t	2026-10-17 18:36:18.788598+08
249	18	T01	62	62	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:18.788646+08
250	18	T06	62	62	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.85	RULE	t	2026-10-17 18:36:18.788669+08
257	19	T06	65	65	0	2024-12-20	\N	\N	2024年12月20日	\N	1	[49.0, 253.7880096435547, 139.046875, 271.416015625]	0.9	RULE	t	2026-10-17 18:36:18.933314+08
259	19	T06	67	67	0	2025-07-01	\N	\N	2025年7月1日	\N	1	[49.0, 253.7880096435547, 125.53515625, 271.416015625]	0.9	RULE	t	2026-10-17 18:36:19.018531+08
262	19	T01	69	69	0	2003-05-12	\N	\N	2003-05-12	\N	1	\N	0.9	RULE	t	2026-10-17 18:36:19.105008+08
263	19	T06	69	69	0	2003-05-12	\N	\N	2003年5月12日	\N	1	[49.0, 91.78800201416016, 543.806640625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:19.105066+08
264	20	T02	70	70	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.9	RULE	t	2026-10-17 18:36:19.160262+08
265	20	T01	70	70	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:19.160314+08
266	20	T06	70	70	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.85	RULE	t	2026-10-17 18:36:19.160337+08
269	20	T06	72	72	0	2025-08-01	\N	\N	2025年8月1日	\N	1	[49.0, 253.7880096435547, 125.53515625, 271.416015625]	0.9	RULE	t	2026-10-17 18:36:19.254244+08
270	21	T02	73	73	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.9	RULE	t	2026-10-17 18:36:19.314269+08
271	21	T01	73	73	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:19.314313+08
272	21	T06	73	73	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.85	RULE	t	2026-10-17 18:36:19.314337+08
276	22	T14	75	75	0	2025-06-01	\N	\N	2025年6月1日	\N	1	[49.0, 91.78800201416016, 125.53515625, 109.41600799560547]	0.9	RULE	t	2026-10-17 18:36:19.404658+08
277	22	T06	75	75	0	2025-06-01	\N	\N	2025年6月1日	\N	1	[49.0, 91.78800201416016, 125.53515625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:19.404713+08
278	22	T16	75	75	0	2025-06-01	\N	\N	2025年6月1日	\N	1	[49.0, 91.78800201416016, 125.53515625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:19.404735+08
279	22	T20	75	75	0	2025-06-01	\N	\N	2025年6月1日	\N	1	[49.0, 91.78800201416016, 125.53515625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:19.404755+08
282	22	T10	77	77	0	2024-07-01	2024-07-05	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:19.493342+08
283	22	T10	77	77	0	2024-07-01	2024-07-05	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:19.493396+08
284	22	T06	77	77	0	2024-07-05	\N	\N	2024年7月5日	\N	1	[49.0, 91.78800201416016, 330.61328125, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:19.49342+08
289	22	T12	79	79	0	2025-05-10	\N	\N	2025年5月10日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.9	RULE	t	2026-10-17 18:36:19.582682+08
290	22	T06	79	79	0	2025-05-10	\N	\N	2025年5月10日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:19.58274+08
291	23	T18	80	80	0	2025-09-20	\N	\N	2025年9月20日	\N	1	[49.0, 221.38800048828125, 132.291015625, 239.01600646972656]	0.9	RULE	t	2026-10-17 18:36:19.638931+08
292	23	T06	80	80	0	2025-09-20	\N	\N	2025年9月20日	\N	1	[49.0, 221.38800048828125, 132.291015625, 239.01600646972656]	0.85	RULE	t	2026-10-17 18:36:19.638983+08
293	23	T20	80	80	0	2025-09-20	\N	\N	2025年9月20日	\N	1	[49.0, 221.38800048828125, 132.291015625, 239.01600646972656]	0.85	RULE	t	2026-10-17 18:36:19.639005+08
297	23	T19	82	82	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:19.742493+08
298	23	T06	82	82	0	2025-10-08	\N	\N	2025年10月8日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:19.742543+08
299	23	T11	82	82	0	2025-09-25	\N	\N	2025年9月25日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:19.742566+08
300	23	T11	82	82	0	2025-10-08	\N	\N	2025年10月8日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:19.742585+08
301	23	T20	82	82	0	2025-09-25	\N	\N	2025年9月25日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:19.742604+08
302	23	T20	82	82	0	2025-10-08	\N	\N	2025年10月8日	\N	1	\N	0.85	RULE	t	2026-10-17 18:36:19.742622+08
303	24	T02	83	83	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.9	RULE	t	2026-10-17 18:36:19.800405+08
304	24	T01	83	83	0	\N	\N	\N	\N	未抽取到	\N	\N	0.4	RULE	t	2026-10-17 18:36:19.800462+08
305	24	T06	83	83	0	2023-03-15	\N	\N	2023年3月15日	\N	1	[49.0, 314.98797607421875, 132.291015625, 332.615966796875]	0.85	RULE	t	2026-10-17 18:36:19.800486+08
294	23	T20	81	81	0	2025-10-08	\N	\N	2025年10月8日	\N	1	[49.0, 91.78800201416016, 132.291015625, 109.41600799560547]	0.9	RULE	t	2026-10-17 18:36:19.686738+08
295	23	T06	81	81	0	2025-10-08	\N	\N	2025年10月8日	\N	1	[49.0, 91.78800201416016, 132.291015625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:19.686801+08
296	23	T14	81	81	0	2025-10-08	\N	\N	2025年10月8日	\N	1	[49.0, 91.78800201416016, 132.291015625, 109.41600799560547]	0.85	RULE	t	2026-10-17 18:36:19.686825+08
306	24	T03	84	84	0	2023-03-28	\N	\N	2023年3月28日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.9	RULE	t	2026-10-17 18:36:19.842291+08
307	24	T06	84	84	0	2023-03-28	\N	\N	2023年3月28日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:19.842342+08
308	24	T15	84	84	0	2023-03-28	\N	\N	2023年3月28日	\N	1	[49.0, 124.18800354003906, 132.291015625, 141.81600952148438]	0.85	RULE	t	2026-10-17 18:36:19.842364+08
\.


--
-- Data for Name: time_rules; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.time_rules (id, code, name, rule_type, params, applies_stages, severity, basis, message_template, suggestion_template_id, is_active, sort_order, updated_by, created_at, updated_at) FROM stdin;
1	R-T01	年满十八周岁	AGE	{"checks": [{"at": "T02", "op": "age_at_least", "birth": "T01", "years": 18}]}	[1, 2, 3, 4, 5]	BLOCK	中国共产党章程	递交入党申请书时未满 18 周岁（出生 {T01}，申请 {T02}）	\N	t	1	\N	2026-10-17 18:29:29.445666+08	2026-10-17 18:29:29.445667+08
2	R-T02	谈话不超过一个月	INTERVAL	{"checks": [{"a": "T02", "b": "T03", "op": "within", "max": {"unit": "MONTH", "value": 1}}]}	[1, 2]	WARN	中国共产党发展党员工作细则	党组织派人谈话（{T03}）距递交申请（{T02}）超过一个月	\N	t	2	\N	2026-10-17 18:29:29.445719+08	2026-10-17 18:29:29.445719+08
3	R-T03	谈话不早于申请	ORDER	{"checks": [{"a": "T02", "b": "T03", "op": "before", "strict": false}]}	[1, 2]	BLOCK	中国共产党发展党员工作细则	谈话日期（{T03}）早于递交申请日期（{T02}）	\N	t	3	\N	2026-10-17 18:29:29.445737+08	2026-10-17 18:29:29.445738+08
4	R-T04	确定积极分子距申请不过久	INTERVAL	{"checks": [{"a": "T02", "b": "T04", "op": "within", "max": {"unit": "DAY", "value": 30}}]}	[2]	WARN	中国共产党发展党员工作细则	确定积极分子（{T04}）距递交申请（{T02}）间隔过长	\N	t	4	\N	2026-10-17 18:29:29.445753+08	2026-10-17 18:29:29.445753+08
5	R-T05	积极分子培养满一年	INTERVAL	{"checks": [{"a": "T04", "b": "T08", "op": "at_least", "min": {"unit": "YEAR", "value": 1}}]}	[3, 4, 5]	BLOCK	中国共产党发展党员工作细则	确定积极分子（{T04}）至确定发展对象（{T08}）间隔不足 1 年	\N	t	5	\N	2026-10-17 18:29:29.445767+08	2026-10-17 18:29:29.445767+08
6	R-T06	思想汇报相邻间隔	SEQ_GAP	{"checks": [{"op": "seq_max_gap", "to": "T08", "max": {"unit": "MONTH", "value": 3}, "seq": "T06[*]", "from": "T04"}]}	[2, 3, 5]	WARN	中国共产党发展党员工作细则	思想汇报相邻间隔超过一个季度	\N	t	6	\N	2026-10-17 18:29:29.44578+08	2026-10-17 18:29:29.445781+08
7	R-T07	思想汇报按期提交	SEQ_COUNT	{"checks": [{"op": "seq_period_count", "to": "T08", "seq": "T06[*]", "from": "T04", "period_months": 3, "min_per_period": 1}]}	[2, 3, 5]	BLOCK	中国共产党发展党员工作细则	培养期内思想汇报未按每季度至少一份提交	\N	t	7	\N	2026-10-17 18:29:29.445794+08	2026-10-17 18:29:29.445794+08
8	R-T08	政审完成于确定发展对象之后	ORDER	{"checks": [{"a": "T08", "b": "T09", "op": "before", "strict": false}]}	[3, 4]	BLOCK	中国共产党发展党员工作细则	政治审查完成日期（{T09}）早于确定发展对象（{T08}）	\N	t	8	\N	2026-10-17 18:29:29.445808+08	2026-10-17 18:29:29.445808+08
9	R-T09	集中培训时长或学时	DURATION	{"checks": [{"op": "duration_min", "min": {"unit": "DAY", "value": 3}, "node": "T10", "or_hours": 24}]}	[3, 4]	BLOCK	中国共产党发展党员工作细则	集中培训未满规定时长或学时	\N	t	9	\N	2026-10-17 18:29:29.445822+08	2026-10-17 18:29:29.445822+08
10	R-T10	公示不少于五个工作日且在预审前	COMPOSITE	{"checks": [{"a": "T11.end", "b": "T12", "op": "before", "strict": false}, {"op": "duration_min", "min": {"unit": "WORKDAY", "value": 5}, "node": "T11"}]}	[4]	WARN	中国共产党发展党员工作细则	发展对象公示未满五个工作日或晚于预审	\N	t	10	\N	2026-10-17 18:29:29.445836+08	2026-10-17 18:29:29.445836+08
11	R-T11	预审在填写志愿书之前	ORDER	{"checks": [{"a": "T12", "b": "T13", "op": "before", "strict": false}]}	[4]	BLOCK	中国共产党发展党员工作细则	填写入党志愿书（{T13}）早于上级党委预审（{T12}）	\N	t	11	\N	2026-10-17 18:29:29.445849+08	2026-10-17 18:29:29.445849+08
12	R-T12	支部大会在预审之后	ORDER	{"checks": [{"a": "T12", "b": "T14", "op": "before", "strict": true}]}	[4]	BLOCK	中国共产党发展党员工作细则	支部大会接收日期（{T14}）早于预审（{T12}）	\N	t	12	\N	2026-10-17 18:29:29.445862+08	2026-10-17 18:29:29.445862+08
13	R-T13	党委派人谈话在支部大会之后	ORDER	{"checks": [{"a": "T14", "b": "T15", "op": "before", "strict": false}]}	[4]	BLOCK	中国共产党发展党员工作细则	上级党委派人谈话（{T15}）早于支部大会（{T14}）	\N	t	13	\N	2026-10-17 18:29:29.445875+08	2026-10-17 18:29:29.445875+08
14	R-T14	审批在谈话之后	ORDER	{"checks": [{"a": "T15", "b": "T16", "op": "before", "strict": false}]}	[4]	BLOCK	中国共产党发展党员工作细则	上级党委审批（{T16}）早于派人谈话（{T15}）	\N	t	14	\N	2026-10-17 18:29:29.445888+08	2026-10-17 18:29:29.445888+08
15	R-T15	党委审批不超过三个月	INTERVAL	{"checks": [{"a": "T14", "b": "T16", "op": "within", "max": {"unit": "MONTH", "value": 3}}]}	[4, 5]	WARN	中国共产党发展党员工作细则	上级党委审批（{T16}）距支部大会（{T14}）超过三个月	\N	t	15	\N	2026-10-17 18:29:29.445901+08	2026-10-17 18:29:29.445901+08
16	R-T16	派生预备期满日	DERIVED	{"checks": [{"op": "derive", "base": "T14", "name": "D01", "offset": {"unit": "YEAR", "value": 1}}]}	[4, 5]	CALC	中国共产党发展党员工作细则	预备期满日 = 支部大会接收日 + 1 年	\N	t	16	\N	2026-10-17 18:29:29.445914+08	2026-10-17 18:29:29.445914+08
17	R-T17	转正申请不晚于预备期满	ORDER	{"checks": [{"a": "T18", "b": "D01", "op": "before", "strict": false}]}	[5]	WARN	中国共产党发展党员工作细则	转正申请（{T18}）晚于预备期满日（D01）	\N	t	17	\N	2026-10-17 18:29:29.445931+08	2026-10-17 18:29:29.445931+08
18	R-T18	转正公示不少于五个工作日	DURATION	{"checks": [{"op": "duration_min", "min": {"unit": "WORKDAY", "value": 5}, "node": "T19"}]}	[5]	WARN	中国共产党发展党员工作细则	转正公示不足五个工作日	\N	t	18	\N	2026-10-17 18:29:29.445944+08	2026-10-17 18:29:29.445944+08
19	R-T19	转正大会在预备期满之后	ORDER	{"checks": [{"a": "D01", "b": "T20", "op": "before", "strict": false}]}	[5]	BLOCK	中国共产党发展党员工作细则	支部大会讨论转正（{T20}）早于预备期满日	\N	t	19	\N	2026-10-17 18:29:29.445956+08	2026-10-17 18:29:29.445957+08
20	R-T20	同一节点多来源一致	CONSISTENCY	{"checks": [{"op": "consistent", "nodes": "*"}]}	[1, 2, 3, 4, 5]	BLOCK	中国共产党发展党员工作细则	时间节点在多份材料中取值不一致	\N	t	20	\N	2026-10-17 18:29:29.44597+08	2026-10-17 18:29:29.44597+08
21	R-T21	日期合法且不晚于上传日	VALID_DATE	{"checks": [{"op": "valid_date", "nodes": "*"}]}	[1, 2, 3, 4, 5]	BLOCK	中国共产党发展党员工作细则	抽取日期不完整、不合法或晚于材料上传日	\N	t	21	\N	2026-10-17 18:29:29.445982+08	2026-10-17 18:29:29.445983+08
22	R-T22	阶段必填节点与单调递增	REQUIRED_NODES	{"checks": [{"op": "required", "nodes_by_stage": {"1": ["T01", "T02"], "2": ["T02", "T03", "T04"], "3": ["T04", "T08"], "4": ["T08", "T09", "T10", "T11", "T12", "T13", "T14", "T15", "T16"], "5": ["T14", "T16", "T18", "T19", "T20"]}}, {"op": "monotonic", "nodes": ["T02", "T04", "T08", "T14", "T20"]}]}	[1, 2, 3, 4, 5]	BLOCK	中国共产党发展党员工作细则	当前阶段关键时间节点缺失或顺序颠倒	\N	t	22	\N	2026-10-17 18:29:29.445996+08	2026-10-17 18:29:29.445996+08
23	R-T23	序列日期落在培养区间	IN_RANGE	{"checks": [{"op": "seq_in_range", "to": "T08", "seq": "T06[*]", "from": "T04"}]}	[2, 3, 5]	WARN	中国共产党发展党员工作细则	思想汇报日期未落在对应培养考察区间内	\N	t	23	\N	2026-10-17 18:29:29.446008+08	2026-10-17 18:29:29.446009+08
\.


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_roles (id, user_id, role, org_id, created_at) FROM stdin;
1	1	SYS_ADMIN	1	2026-10-17 18:29:29.6533+08
2	1	ORG_ADMIN	1	2026-10-17 18:29:29.653347+08
3	2	ORG_ADMIN	1	2026-10-17 18:35:58.650564+08
4	3	COLLEGE_REVIEWER	2	2026-10-17 18:35:58.817015+08
5	4	COLLEGE_REVIEWER	6	2026-10-17 18:35:58.982058+08
6	5	BRANCH_REVIEWER	3	2026-10-17 18:35:59.152056+08
7	5	CROSS_REVIEWER	3	2026-10-17 18:35:59.152113+08
8	6	BRANCH_REVIEWER	4	2026-10-17 18:35:59.31892+08
9	6	CROSS_REVIEWER	4	2026-10-17 18:35:59.318976+08
10	7	BRANCH_REVIEWER	5	2026-10-17 18:35:59.48299+08
11	7	CROSS_REVIEWER	5	2026-10-17 18:35:59.48303+08
12	8	BRANCH_REVIEWER	7	2026-10-17 18:35:59.646536+08
13	8	CROSS_REVIEWER	7	2026-10-17 18:35:59.646576+08
14	9	BRANCH_REVIEWER	8	2026-10-17 18:35:59.816129+08
15	9	CROSS_REVIEWER	8	2026-10-17 18:35:59.816167+08
16	10	BRANCH_REVIEWER	9	2026-10-17 18:35:59.981216+08
17	10	CROSS_REVIEWER	9	2026-10-17 18:35:59.981261+08
18	11	STUDENT	3	2026-10-17 18:36:00.157368+08
19	12	STUDENT	3	2026-10-17 18:36:00.324035+08
20	13	STUDENT	3	2026-10-17 18:36:00.491559+08
21	14	STUDENT	3	2026-10-17 18:36:00.660279+08
22	15	STUDENT	4	2026-10-17 18:36:00.824671+08
23	16	STUDENT	4	2026-10-17 18:36:00.992313+08
24	17	STUDENT	4	2026-10-17 18:36:01.157904+08
25	18	STUDENT	4	2026-10-17 18:36:01.321767+08
26	19	STUDENT	5	2026-10-17 18:36:01.486673+08
27	20	STUDENT	5	2026-10-17 18:36:01.651455+08
28	21	STUDENT	5	2026-10-17 18:36:01.823202+08
29	22	STUDENT	5	2026-10-17 18:36:01.98997+08
30	23	STUDENT	7	2026-10-17 18:36:02.154647+08
31	24	STUDENT	7	2026-10-17 18:36:02.325093+08
32	25	STUDENT	7	2026-10-17 18:36:02.49359+08
33	26	STUDENT	7	2026-10-17 18:36:02.661649+08
34	27	STUDENT	8	2026-10-17 18:36:02.831261+08
35	28	STUDENT	8	2026-10-17 18:36:03.000672+08
36	29	STUDENT	8	2026-10-17 18:36:03.169991+08
37	30	STUDENT	8	2026-10-17 18:36:03.340787+08
38	31	STUDENT	9	2026-10-17 18:36:03.506679+08
39	32	STUDENT	9	2026-10-17 18:36:03.669574+08
40	33	STUDENT	9	2026-10-17 18:36:03.837435+08
41	34	STUDENT	9	2026-10-17 18:36:04.035165+08
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, username, password_hash, real_name, gender, org_id, email, phone_enc, phone_masked, is_active, must_change_password, failed_login_count, locked_until, token_version, last_login_at, last_login_ip, is_demo, created_at, updated_at) FROM stdin;
11	demo_stu01	$2b$12$MFf6M35m40qDWhl3ym.pQ.Gf.y2Hp2kGXONx4X59MFQZTWnYkyc8y	演示学生01	\N	3	\N	\N	\N	t	f	0	\N	0	2026-10-17 19:11:25.93086+08	127.0.0.1	t	2026-10-17 18:36:00.148616+08	2026-10-17 19:11:25.771454+08
3	demo_college1	$2b$12$aX77lZmNdvk3WbemndwEDe.bgJG.ydvnC20yjpR2nTiMXEZ6rIHOG	演示学院审核员01	\N	2	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:35:58.81417+08	2026-10-17 18:35:58.814174+08
4	demo_college2	$2b$12$832AkUNJm18bQj89IhQlN.BoTJ86UBUrLqTKITF0HeIC8tdolt67G	演示学院审核员02	\N	6	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:35:58.979723+08	2026-10-17 18:35:58.979726+08
6	demo_branch2	$2b$12$t5SeH09yxTHhDCDFL80bPer36.INsK6hHyHkrCXdcGmhl68zzYLuG	演示支部书记02	\N	4	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:35:59.315597+08	2026-10-17 18:35:59.315601+08
7	demo_branch3	$2b$12$Y1MWARDWNjjH1hIh28POJeMaBKP1LfhGm4hw4NG9rVAb5ACzcgp7S	演示支部书记03	\N	5	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:35:59.480748+08	2026-10-17 18:35:59.480753+08
8	demo_branch4	$2b$12$pOtD4uOkVagbjJwY6NSCxO6bwG7QtNCGNTKx8zXV3IAsuLW1y4PFy	演示支部书记04	\N	7	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:35:59.6448+08	2026-10-17 18:35:59.644803+08
9	demo_branch5	$2b$12$fyrpggBKmFQ3SDroZIvmzuC9QbXdBMedJpz/ZrA3J4Phw.J1EjtbK	演示支部书记05	\N	8	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:35:59.814233+08	2026-10-17 18:35:59.814237+08
10	demo_branch6	$2b$12$SO0a3tLwnrMuEF1B7MPyaOMBN9OFL.VyXiZ0POzrg7t.q91N66Gy.	演示支部书记06	\N	9	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:35:59.979349+08	2026-10-17 18:35:59.979353+08
12	demo_stu02	$2b$12$cpoxWpVlFUQXZokcJwixzOuBK1ykadDk.ZzI8bofhs.ESZ/IPcika	演示学生02	\N	3	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:00.322868+08	2026-10-17 18:36:00.322872+08
13	demo_stu03	$2b$12$qvfOx2zuPcLZvRD0ciaBqe8kAThZe4p68eWRfVgYJudYBezVvPSeq	演示学生03	\N	3	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:00.490628+08	2026-10-17 18:36:00.490631+08
14	demo_stu04	$2b$12$TrgA4ohx.RtzSUlJ4IvSgecINEI/n9dboXxsdqHJ8q5mPxulcQ/jm	演示学生04	\N	3	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:00.659023+08	2026-10-17 18:36:00.659026+08
15	demo_stu05	$2b$12$GsIAVrjjCOaansZgf.FAIOZL8jIU87gORaGrxuGRlzdYJYAqWiV1S	演示学生05	\N	4	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:00.823758+08	2026-10-17 18:36:00.823762+08
16	demo_stu06	$2b$12$LZdj6cWsnJngq6.eXV3vmuLJNfUEt4y8uOeD0jCTgZY/Hl.eMp9Gy	演示学生06	\N	4	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:00.991363+08	2026-10-17 18:36:00.991368+08
17	demo_stu07	$2b$12$jy49GnFZ8h2ibvJgCNGYoOD0ND8g3Ox6X9TutGV2sxt5iiQT5NhrK	演示学生07	\N	4	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:01.156928+08	2026-10-17 18:36:01.156931+08
18	demo_stu08	$2b$12$8nuVeQXn9lwhGDm2oNgz1eaHouG.HoWrDGmww.qHtHT4D1unfFEd.	演示学生08	\N	4	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:01.320841+08	2026-10-17 18:36:01.320845+08
19	demo_stu09	$2b$12$PFSLFt4g3DrtK8OxV1nWlOcsQoUOmqcfPQ5dwsW3w9Zl55zWpMXtS	演示学生09	\N	5	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:01.485611+08	2026-10-17 18:36:01.485615+08
20	demo_stu10	$2b$12$fDkfxZxJTWFgLerPJ4yOTOEmZRkYCLjrAXCFXJSW2o52a7dPSNXJ2	演示学生10	\N	5	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:01.650491+08	2026-10-17 18:36:01.650495+08
21	demo_stu11	$2b$12$9/YBlOemKch0f/g2Ra7oD.n6N76EYkD7.j6V9izrVL2gjLtZbq2US	演示学生11	\N	5	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:01.821881+08	2026-10-17 18:36:01.821886+08
22	demo_stu12	$2b$12$tYrc9TFGRV2EC1ZuhasZA.FfvRgnP1AAzEm.H01kUm/0MxmPsPyZK	演示学生12	\N	5	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:01.988763+08	2026-10-17 18:36:01.988766+08
23	demo_stu13	$2b$12$wVn/Wadw97lw8wYRtg.eLOvRQPtemmrrXxYrznW.6hmEoIJ/UXDZW	演示学生13	\N	7	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:02.153712+08	2026-10-17 18:36:02.153716+08
24	demo_stu14	$2b$12$es0IG.MXfVhuTpHLbhR2suFzLqdlCedfynknhk.goOPDsx0kh7FdO	演示学生14	\N	7	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:02.324159+08	2026-10-17 18:36:02.324163+08
25	demo_stu15	$2b$12$XkgO/AoibX7fQRIvZZjCAuwaYGkDvOtOvwVAOqJYNYgY8NGXnFNa2	演示学生15	\N	7	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:02.492445+08	2026-10-17 18:36:02.492449+08
26	demo_stu16	$2b$12$.F0b3zsy9BH5OgdLgfvtDuLmChQAhGlFs3l3rL4W2L7K6NyQC7gqu	演示学生16	\N	7	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:02.660578+08	2026-10-17 18:36:02.660582+08
27	demo_stu17	$2b$12$e/.8.CQdKUWEE/k42prCt.J7SB.D3IXmTap4zbQb75la.9PbLsjsO	演示学生17	\N	8	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:02.830174+08	2026-10-17 18:36:02.830177+08
28	demo_stu18	$2b$12$.JvRh/UKKFZW6DjQRVuuoujNHdgCOeVtCG9pV7VAvTZcRGMP6Eaua	演示学生18	\N	8	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:02.999612+08	2026-10-17 18:36:02.999616+08
29	demo_stu19	$2b$12$fjyZqJj.D//DkHyyKLXAZO8KeZLlBeLdjenx1RIlO3ZGMX8oYv8MG	演示学生19	\N	8	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:03.168858+08	2026-10-17 18:36:03.168863+08
30	demo_stu20	$2b$12$TTp83KyYs0Rwa9/c53OMXOEZJWW4y5LOOs0ugRB/4m2MupKPGPHoe	演示学生20	\N	8	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:03.339672+08	2026-10-17 18:36:03.339676+08
31	demo_stu21	$2b$12$eRMywQlQstS8LyBBNefIB.7kgCbLMhJ/mpeKvkODGnEVDCBndbHrC	演示学生21	\N	9	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:03.505709+08	2026-10-17 18:36:03.505713+08
32	demo_stu22	$2b$12$DOxmBjH8jaJK1GkDIwA0rubmsIIl5QN19vdC1HSUeDCbT1Kb1iDYy	演示学生22	\N	9	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:03.668292+08	2026-10-17 18:36:03.668296+08
33	demo_stu23	$2b$12$J.fJyoJ1abDxJNrUUmIN0OdMc2TNvwrXIMr3mHfPz1ksTw0kQpy4e	演示学生23	\N	9	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:03.836448+08	2026-10-17 18:36:03.836451+08
34	demo_stu24	$2b$12$41akZ7pQMVM7.hAgYEKSGuZmmlPCPuh3AxBkmW4bMi1y0.Llqa0Su	演示学生24	\N	9	\N	\N	\N	t	f	0	\N	0	\N	\N	t	2026-10-17 18:36:04.034083+08	2026-10-17 18:36:04.034086+08
1	admin	!RESET_REQUIRED_AFTER_RESTORE!	系统管理员	\N	1	\N	\N	\N	f	t	0	\N	0	2026-10-17 19:18:42.046942+08	127.0.0.1	f	2026-10-17 18:29:29.650569+08	2026-10-17 19:18:41.882329+08
5	demo_branch1	$2b$12$mqv.xpBP1Kb12phUtb8WDebfjj3Za1JVmlMi6hpAPXm8fvLQTokz6	演示支部书记01	\N	3	\N	\N	\N	t	f	0	\N	0	2026-10-17 19:19:06.545552+08	127.0.0.1	t	2026-10-17 18:35:59.150146+08	2026-10-17 19:19:06.386543+08
2	demo_org	$2b$12$Zr9zw4zAlc2OUor2hZZsF.1wbm6Fex5fN9vcJ3B.LprXqzYa3dbp6	演示组织部管理员	\N	1	\N	\N	\N	t	f	0	\N	0	2026-10-17 19:30:26.917136+08	127.0.0.1	t	2026-10-17 18:35:58.648426+08	2026-10-17 19:30:26.730658+08
\.


--
-- Name: ai_reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ai_reports_id_seq', 23, true);


--
-- Name: archive_time_nodes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.archive_time_nodes_id_seq', 528, true);


--
-- Name: archives_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.archives_id_seq', 24, true);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 59, true);


--
-- Name: batch_upload_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.batch_upload_items_id_seq', 1, false);


--
-- Name: batches_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.batches_id_seq', 1, true);


--
-- Name: check_rules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.check_rules_id_seq', 19, true);


--
-- Name: checklist_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.checklist_items_id_seq', 26, true);


--
-- Name: cross_review_pairs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.cross_review_pairs_id_seq', 6, true);


--
-- Name: export_files_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.export_files_id_seq', 1, false);


--
-- Name: handover_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.handover_records_id_seq', 1, false);


--
-- Name: issues_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.issues_id_seq', 329, true);


--
-- Name: jobs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.jobs_id_seq', 108, true);


--
-- Name: material_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.material_types_id_seq', 24, true);


--
-- Name: material_versions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.material_versions_id_seq', 84, true);


--
-- Name: materials_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.materials_id_seq', 84, true);


--
-- Name: messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.messages_id_seq', 108, true);


--
-- Name: notices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.notices_id_seq', 1, false);


--
-- Name: orgs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.orgs_id_seq', 9, true);


--
-- Name: parse_results_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.parse_results_id_seq', 84, true);


--
-- Name: political_terms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.political_terms_id_seq', 3, true);


--
-- Name: prompt_templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.prompt_templates_id_seq', 4, true);


--
-- Name: review_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.review_records_id_seq', 1, false);


--
-- Name: rule_versions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.rule_versions_id_seq', 1, true);


--
-- Name: sensitive_phrases_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sensitive_phrases_id_seq', 3, true);


--
-- Name: submissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.submissions_id_seq', 72, true);


--
-- Name: suggestion_templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.suggestion_templates_id_seq', 9, true);


--
-- Name: time_node_defs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.time_node_defs_id_seq', 22, true);


--
-- Name: time_node_extractions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.time_node_extractions_id_seq', 308, true);


--
-- Name: time_rules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.time_rules_id_seq', 23, true);


--
-- Name: user_roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.user_roles_id_seq', 41, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 34, true);


--
-- Name: ai_reports ai_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_reports
    ADD CONSTRAINT ai_reports_pkey PRIMARY KEY (id);


--
-- Name: archive_time_nodes archive_time_nodes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.archive_time_nodes
    ADD CONSTRAINT archive_time_nodes_pkey PRIMARY KEY (id);


--
-- Name: archives archives_anon_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.archives
    ADD CONSTRAINT archives_anon_code_key UNIQUE (anon_code);


--
-- Name: archives archives_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.archives
    ADD CONSTRAINT archives_pkey PRIMARY KEY (id);


--
-- Name: archives archives_student_no_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.archives
    ADD CONSTRAINT archives_student_no_key UNIQUE (student_no);


--
-- Name: archives archives_student_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.archives
    ADD CONSTRAINT archives_student_user_id_key UNIQUE (student_user_id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: batch_upload_items batch_upload_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.batch_upload_items
    ADD CONSTRAINT batch_upload_items_pkey PRIMARY KEY (id);


--
-- Name: batches batches_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.batches
    ADD CONSTRAINT batches_name_key UNIQUE (name);


--
-- Name: batches batches_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.batches
    ADD CONSTRAINT batches_pkey PRIMARY KEY (id);


--
-- Name: check_rules check_rules_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.check_rules
    ADD CONSTRAINT check_rules_code_key UNIQUE (code);


--
-- Name: check_rules check_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.check_rules
    ADD CONSTRAINT check_rules_pkey PRIMARY KEY (id);


--
-- Name: checklist_items checklist_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checklist_items
    ADD CONSTRAINT checklist_items_pkey PRIMARY KEY (id);


--
-- Name: cross_review_pairs cross_review_pairs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cross_review_pairs
    ADD CONSTRAINT cross_review_pairs_pkey PRIMARY KEY (id);


--
-- Name: export_files export_files_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.export_files
    ADD CONSTRAINT export_files_pkey PRIMARY KEY (id);


--
-- Name: handover_records handover_records_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.handover_records
    ADD CONSTRAINT handover_records_pkey PRIMARY KEY (id);


--
-- Name: issues issues_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.issues
    ADD CONSTRAINT issues_pkey PRIMARY KEY (id);


--
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (id);


--
-- Name: material_types material_types_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.material_types
    ADD CONSTRAINT material_types_code_key UNIQUE (code);


--
-- Name: material_types material_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.material_types
    ADD CONSTRAINT material_types_pkey PRIMARY KEY (id);


--
-- Name: material_versions material_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.material_versions
    ADD CONSTRAINT material_versions_pkey PRIMARY KEY (id);


--
-- Name: material_versions material_versions_stored_path_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.material_versions
    ADD CONSTRAINT material_versions_stored_path_key UNIQUE (stored_path);


--
-- Name: materials materials_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_pkey PRIMARY KEY (id);


--
-- Name: messages messages_dedup_key_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_dedup_key_key UNIQUE (dedup_key);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: notices notices_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notices
    ADD CONSTRAINT notices_pkey PRIMARY KEY (id);


--
-- Name: orgs orgs_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orgs
    ADD CONSTRAINT orgs_code_key UNIQUE (code);


--
-- Name: orgs orgs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orgs
    ADD CONSTRAINT orgs_pkey PRIMARY KEY (id);


--
-- Name: parse_results parse_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parse_results
    ADD CONSTRAINT parse_results_pkey PRIMARY KEY (id);


--
-- Name: parse_results parse_results_version_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parse_results
    ADD CONSTRAINT parse_results_version_id_key UNIQUE (version_id);


--
-- Name: political_terms political_terms_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.political_terms
    ADD CONSTRAINT political_terms_pkey PRIMARY KEY (id);


--
-- Name: political_terms political_terms_standard_text_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.political_terms
    ADD CONSTRAINT political_terms_standard_text_key UNIQUE (standard_text);


--
-- Name: prompt_templates prompt_templates_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prompt_templates
    ADD CONSTRAINT prompt_templates_code_key UNIQUE (code);


--
-- Name: prompt_templates prompt_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prompt_templates
    ADD CONSTRAINT prompt_templates_pkey PRIMARY KEY (id);


--
-- Name: review_records review_records_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.review_records
    ADD CONSTRAINT review_records_pkey PRIMARY KEY (id);


--
-- Name: revoked_tokens revoked_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.revoked_tokens
    ADD CONSTRAINT revoked_tokens_pkey PRIMARY KEY (jti);


--
-- Name: rule_versions rule_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rule_versions
    ADD CONSTRAINT rule_versions_pkey PRIMARY KEY (id);


--
-- Name: rule_versions rule_versions_version_no_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rule_versions
    ADD CONSTRAINT rule_versions_version_no_key UNIQUE (version_no);


--
-- Name: schema_meta schema_meta_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schema_meta
    ADD CONSTRAINT schema_meta_pkey PRIMARY KEY (key);


--
-- Name: sensitive_phrases sensitive_phrases_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sensitive_phrases
    ADD CONSTRAINT sensitive_phrases_pkey PRIMARY KEY (id);


--
-- Name: stages stages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stages
    ADD CONSTRAINT stages_pkey PRIMARY KEY (code);


--
-- Name: stages stages_stage_key_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stages
    ADD CONSTRAINT stages_stage_key_key UNIQUE (stage_key);


--
-- Name: submissions submissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_pkey PRIMARY KEY (id);


--
-- Name: suggestion_templates suggestion_templates_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suggestion_templates
    ADD CONSTRAINT suggestion_templates_code_key UNIQUE (code);


--
-- Name: suggestion_templates suggestion_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suggestion_templates
    ADD CONSTRAINT suggestion_templates_pkey PRIMARY KEY (id);


--
-- Name: system_settings system_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_settings
    ADD CONSTRAINT system_settings_pkey PRIMARY KEY (key);


--
-- Name: time_node_defs time_node_defs_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_node_defs
    ADD CONSTRAINT time_node_defs_code_key UNIQUE (code);


--
-- Name: time_node_defs time_node_defs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_node_defs
    ADD CONSTRAINT time_node_defs_pkey PRIMARY KEY (id);


--
-- Name: time_node_extractions time_node_extractions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_node_extractions
    ADD CONSTRAINT time_node_extractions_pkey PRIMARY KEY (id);


--
-- Name: time_rules time_rules_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_rules
    ADD CONSTRAINT time_rules_code_key UNIQUE (code);


--
-- Name: time_rules time_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_rules
    ADD CONSTRAINT time_rules_pkey PRIMARY KEY (id);


--
-- Name: ai_reports uq_ai_reports_no; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_reports
    ADD CONSTRAINT uq_ai_reports_no UNIQUE (submission_id, report_no);


--
-- Name: archive_time_nodes uq_archive_time_nodes; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.archive_time_nodes
    ADD CONSTRAINT uq_archive_time_nodes UNIQUE (archive_id, node_code);


--
-- Name: checklist_items uq_checklist; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checklist_items
    ADD CONSTRAINT uq_checklist UNIQUE (stage_code, material_type_id);


--
-- Name: cross_review_pairs uq_cross_pairs; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cross_review_pairs
    ADD CONSTRAINT uq_cross_pairs UNIQUE (batch_id, target_branch_id);


--
-- Name: material_versions uq_material_versions; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.material_versions
    ADD CONSTRAINT uq_material_versions UNIQUE (material_id, version_no);


--
-- Name: sensitive_phrases uq_sensitive; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sensitive_phrases
    ADD CONSTRAINT uq_sensitive UNIQUE (phrase, category);


--
-- Name: submissions uq_submissions_stage; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT uq_submissions_stage UNIQUE (archive_id, stage_code);


--
-- Name: user_roles uq_user_roles; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT uq_user_roles UNIQUE (user_id, role, org_id);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: ix_ai_reports_submission; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ai_reports_submission ON public.ai_reports USING btree (submission_id, report_no DESC);


--
-- Name: ix_archives_batch; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_archives_batch ON public.archives USING btree (batch_id);


--
-- Name: ix_archives_branch; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_archives_branch ON public.archives USING btree (branch_id, current_stage);


--
-- Name: ix_archives_college; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_archives_college ON public.archives USING btree (college_id);


--
-- Name: ix_audit_logs_action; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_audit_logs_action ON public.audit_logs USING btree (action, created_at DESC);


--
-- Name: ix_audit_logs_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_audit_logs_time ON public.audit_logs USING btree (created_at DESC);


--
-- Name: ix_audit_logs_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_audit_logs_user ON public.audit_logs USING btree (user_id, created_at DESC);


--
-- Name: ix_batch_upload_items_job; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_batch_upload_items_job ON public.batch_upload_items USING btree (job_id, status);


--
-- Name: ix_cross_pairs_reviewer; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_cross_pairs_reviewer ON public.cross_review_pairs USING btree (reviewer_branch_id, batch_id);


--
-- Name: ix_extractions_archive_node; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_extractions_archive_node ON public.time_node_extractions USING btree (archive_id, node_code, is_current);


--
-- Name: ix_extractions_version; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_extractions_version ON public.time_node_extractions USING btree (material_version_id);


--
-- Name: ix_handover_records_report; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_handover_records_report ON public.handover_records USING btree (report_id, decided_at DESC);


--
-- Name: ix_issues_fingerprint; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_issues_fingerprint ON public.issues USING btree (submission_id, fingerprint);


--
-- Name: ix_issues_report; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_issues_report ON public.issues USING btree (report_id);


--
-- Name: ix_issues_rule; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_issues_rule ON public.issues USING btree (rule_code, review_status);


--
-- Name: ix_issues_submission; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_issues_submission ON public.issues USING btree (submission_id, is_active, severity);


--
-- Name: ix_jobs_parent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_jobs_parent ON public.jobs USING btree (parent_id);


--
-- Name: ix_jobs_queue; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_jobs_queue ON public.jobs USING btree (status, created_at);


--
-- Name: ix_jobs_target; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_jobs_target ON public.jobs USING btree (target_type, target_id);


--
-- Name: ix_material_versions_sha; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_material_versions_sha ON public.material_versions USING btree (sha256);


--
-- Name: ix_materials_archive; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_materials_archive ON public.materials USING btree (archive_id, stage_code);


--
-- Name: ix_materials_submission; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_materials_submission ON public.materials USING btree (submission_id, status);


--
-- Name: ix_messages_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_messages_user ON public.messages USING btree (user_id, is_read, created_at DESC);


--
-- Name: ix_notices_student; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_notices_student ON public.notices USING btree (student_user_id, created_at DESC);


--
-- Name: ix_notices_submission; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_notices_submission ON public.notices USING btree (submission_id);


--
-- Name: ix_orgs_parent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_orgs_parent ON public.orgs USING btree (parent_id);


--
-- Name: ix_review_records_reviewer; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_review_records_reviewer ON public.review_records USING btree (reviewer_id, created_at);


--
-- Name: ix_review_records_submission; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_review_records_submission ON public.review_records USING btree (submission_id, created_at);


--
-- Name: ix_revoked_tokens_exp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_revoked_tokens_exp ON public.revoked_tokens USING btree (expires_at);


--
-- Name: ix_submissions_batch; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_submissions_batch ON public.submissions USING btree (batch_id, status);


--
-- Name: ix_submissions_college; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_submissions_college ON public.submissions USING btree (college_id, status);


--
-- Name: ix_submissions_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_submissions_status ON public.submissions USING btree (status, branch_id);


--
-- Name: ix_user_roles_role_org; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_roles_role_org ON public.user_roles USING btree (role, org_id);


--
-- Name: ix_users_org; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_org ON public.users USING btree (org_id);


--
-- Name: archive_time_nodes trg_archive_time_nodes_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_archive_time_nodes_updated_at BEFORE UPDATE ON public.archive_time_nodes FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: archives trg_archives_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_archives_updated_at BEFORE UPDATE ON public.archives FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: audit_logs trg_audit_logs_append_only; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_audit_logs_append_only BEFORE DELETE OR UPDATE ON public.audit_logs FOR EACH ROW EXECUTE FUNCTION public.forbid_change();


--
-- Name: batch_upload_items trg_batch_upload_items_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_batch_upload_items_updated_at BEFORE UPDATE ON public.batch_upload_items FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: batches trg_batches_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_batches_updated_at BEFORE UPDATE ON public.batches FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: check_rules trg_check_rules_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_check_rules_updated_at BEFORE UPDATE ON public.check_rules FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: checklist_items trg_checklist_items_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_checklist_items_updated_at BEFORE UPDATE ON public.checklist_items FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: issues trg_issues_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_issues_updated_at BEFORE UPDATE ON public.issues FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: material_types trg_material_types_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_material_types_updated_at BEFORE UPDATE ON public.material_types FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: material_versions trg_material_versions_guard; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_material_versions_guard BEFORE DELETE ON public.material_versions FOR EACH ROW EXECUTE FUNCTION public.guard_purge_only();


--
-- Name: materials trg_materials_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_materials_updated_at BEFORE UPDATE ON public.materials FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: notices trg_notices_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_notices_updated_at BEFORE UPDATE ON public.notices FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: orgs trg_orgs_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_orgs_updated_at BEFORE UPDATE ON public.orgs FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: parse_results trg_parse_results_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_parse_results_updated_at BEFORE UPDATE ON public.parse_results FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: political_terms trg_political_terms_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_political_terms_updated_at BEFORE UPDATE ON public.political_terms FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: prompt_templates trg_prompt_templates_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_prompt_templates_updated_at BEFORE UPDATE ON public.prompt_templates FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: review_records trg_review_records_guard; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_review_records_guard BEFORE DELETE OR UPDATE ON public.review_records FOR EACH ROW EXECUTE FUNCTION public.guard_purge_only();


--
-- Name: schema_meta trg_schema_meta_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_schema_meta_updated_at BEFORE UPDATE ON public.schema_meta FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: sensitive_phrases trg_sensitive_phrases_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_sensitive_phrases_updated_at BEFORE UPDATE ON public.sensitive_phrases FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: submissions trg_submissions_filed_guard; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_submissions_filed_guard BEFORE DELETE OR UPDATE ON public.submissions FOR EACH ROW EXECUTE FUNCTION public.guard_filed_submission();


--
-- Name: submissions trg_submissions_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_submissions_updated_at BEFORE UPDATE ON public.submissions FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: suggestion_templates trg_suggestion_templates_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_suggestion_templates_updated_at BEFORE UPDATE ON public.suggestion_templates FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: system_settings trg_system_settings_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_system_settings_updated_at BEFORE UPDATE ON public.system_settings FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: time_node_defs trg_time_node_defs_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_time_node_defs_updated_at BEFORE UPDATE ON public.time_node_defs FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: time_rules trg_time_rules_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_time_rules_updated_at BEFORE UPDATE ON public.time_rules FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: users trg_users_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: ai_reports ai_reports_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_reports
    ADD CONSTRAINT ai_reports_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.jobs(id) ON DELETE SET NULL;


--
-- Name: ai_reports ai_reports_recheck_of_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_reports
    ADD CONSTRAINT ai_reports_recheck_of_report_id_fkey FOREIGN KEY (recheck_of_report_id) REFERENCES public.ai_reports(id) ON DELETE SET NULL;


--
-- Name: ai_reports ai_reports_rule_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_reports
    ADD CONSTRAINT ai_reports_rule_version_id_fkey FOREIGN KEY (rule_version_id) REFERENCES public.rule_versions(id) ON DELETE RESTRICT;


--
-- Name: ai_reports ai_reports_submission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_reports
    ADD CONSTRAINT ai_reports_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES public.submissions(id) ON DELETE CASCADE;


--
-- Name: ai_reports ai_reports_triggered_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_reports
    ADD CONSTRAINT ai_reports_triggered_by_fkey FOREIGN KEY (triggered_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: archive_time_nodes archive_time_nodes_archive_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.archive_time_nodes
    ADD CONSTRAINT archive_time_nodes_archive_id_fkey FOREIGN KEY (archive_id) REFERENCES public.archives(id) ON DELETE CASCADE;


--
-- Name: archive_time_nodes archive_time_nodes_corrected_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.archive_time_nodes
    ADD CONSTRAINT archive_time_nodes_corrected_by_fkey FOREIGN KEY (corrected_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: archive_time_nodes archive_time_nodes_locked_stage_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.archive_time_nodes
    ADD CONSTRAINT archive_time_nodes_locked_stage_fkey FOREIGN KEY (locked_stage) REFERENCES public.stages(code);


--
-- Name: archive_time_nodes archive_time_nodes_source_extraction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.archive_time_nodes
    ADD CONSTRAINT archive_time_nodes_source_extraction_id_fkey FOREIGN KEY (source_extraction_id) REFERENCES public.time_node_extractions(id) ON DELETE SET NULL;


--
-- Name: archives archives_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.archives
    ADD CONSTRAINT archives_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES public.batches(id) ON DELETE SET NULL;


--
-- Name: archives archives_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.archives
    ADD CONSTRAINT archives_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.orgs(id) ON DELETE RESTRICT;


--
-- Name: archives archives_college_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.archives
    ADD CONSTRAINT archives_college_id_fkey FOREIGN KEY (college_id) REFERENCES public.orgs(id) ON DELETE RESTRICT;


--
-- Name: archives archives_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.archives
    ADD CONSTRAINT archives_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: archives archives_current_stage_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.archives
    ADD CONSTRAINT archives_current_stage_fkey FOREIGN KEY (current_stage) REFERENCES public.stages(code);


--
-- Name: archives archives_student_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.archives
    ADD CONSTRAINT archives_student_user_id_fkey FOREIGN KEY (student_user_id) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: batch_upload_items batch_upload_items_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.batch_upload_items
    ADD CONSTRAINT batch_upload_items_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.jobs(id) ON DELETE CASCADE;


--
-- Name: batch_upload_items batch_upload_items_matched_archive_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.batch_upload_items
    ADD CONSTRAINT batch_upload_items_matched_archive_id_fkey FOREIGN KEY (matched_archive_id) REFERENCES public.archives(id) ON DELETE SET NULL;


--
-- Name: batch_upload_items batch_upload_items_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.batch_upload_items
    ADD CONSTRAINT batch_upload_items_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(id) ON DELETE SET NULL;


--
-- Name: batch_upload_items batch_upload_items_material_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.batch_upload_items
    ADD CONSTRAINT batch_upload_items_material_type_id_fkey FOREIGN KEY (material_type_id) REFERENCES public.material_types(id) ON DELETE SET NULL;


--
-- Name: batches batches_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.batches
    ADD CONSTRAINT batches_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: check_rules check_rules_suggestion_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.check_rules
    ADD CONSTRAINT check_rules_suggestion_template_id_fkey FOREIGN KEY (suggestion_template_id) REFERENCES public.suggestion_templates(id) ON DELETE SET NULL;


--
-- Name: check_rules check_rules_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.check_rules
    ADD CONSTRAINT check_rules_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: checklist_items checklist_items_material_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checklist_items
    ADD CONSTRAINT checklist_items_material_type_id_fkey FOREIGN KEY (material_type_id) REFERENCES public.material_types(id) ON DELETE RESTRICT;


--
-- Name: checklist_items checklist_items_stage_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checklist_items
    ADD CONSTRAINT checklist_items_stage_code_fkey FOREIGN KEY (stage_code) REFERENCES public.stages(code);


--
-- Name: checklist_items checklist_items_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checklist_items
    ADD CONSTRAINT checklist_items_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: cross_review_pairs cross_review_pairs_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cross_review_pairs
    ADD CONSTRAINT cross_review_pairs_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES public.batches(id) ON DELETE CASCADE;


--
-- Name: cross_review_pairs cross_review_pairs_college_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cross_review_pairs
    ADD CONSTRAINT cross_review_pairs_college_id_fkey FOREIGN KEY (college_id) REFERENCES public.orgs(id) ON DELETE RESTRICT;


--
-- Name: cross_review_pairs cross_review_pairs_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cross_review_pairs
    ADD CONSTRAINT cross_review_pairs_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: cross_review_pairs cross_review_pairs_reviewer_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cross_review_pairs
    ADD CONSTRAINT cross_review_pairs_reviewer_branch_id_fkey FOREIGN KEY (reviewer_branch_id) REFERENCES public.orgs(id) ON DELETE RESTRICT;


--
-- Name: cross_review_pairs cross_review_pairs_reviewer_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cross_review_pairs
    ADD CONSTRAINT cross_review_pairs_reviewer_user_id_fkey FOREIGN KEY (reviewer_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: cross_review_pairs cross_review_pairs_target_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cross_review_pairs
    ADD CONSTRAINT cross_review_pairs_target_branch_id_fkey FOREIGN KEY (target_branch_id) REFERENCES public.orgs(id) ON DELETE RESTRICT;


--
-- Name: export_files export_files_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.export_files
    ADD CONSTRAINT export_files_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: materials fk_materials_current_version; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT fk_materials_current_version FOREIGN KEY (current_version_id) REFERENCES public.material_versions(id) ON DELETE SET NULL;


--
-- Name: submissions fk_submissions_ai_job; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT fk_submissions_ai_job FOREIGN KEY (ai_job_id) REFERENCES public.jobs(id) ON DELETE SET NULL;


--
-- Name: submissions fk_submissions_latest_report; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT fk_submissions_latest_report FOREIGN KEY (latest_report_id) REFERENCES public.ai_reports(id) ON DELETE SET NULL;


--
-- Name: handover_records handover_records_assignee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.handover_records
    ADD CONSTRAINT handover_records_assignee_id_fkey FOREIGN KEY (assignee_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: handover_records handover_records_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.handover_records
    ADD CONSTRAINT handover_records_report_id_fkey FOREIGN KEY (report_id) REFERENCES public.ai_reports(id) ON DELETE CASCADE;


--
-- Name: handover_records handover_records_submission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.handover_records
    ADD CONSTRAINT handover_records_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES public.submissions(id) ON DELETE CASCADE;


--
-- Name: issues issues_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.issues
    ADD CONSTRAINT issues_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: issues issues_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.issues
    ADD CONSTRAINT issues_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(id) ON DELETE SET NULL;


--
-- Name: issues issues_material_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.issues
    ADD CONSTRAINT issues_material_version_id_fkey FOREIGN KEY (material_version_id) REFERENCES public.material_versions(id) ON DELETE SET NULL;


--
-- Name: issues issues_prev_issue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.issues
    ADD CONSTRAINT issues_prev_issue_id_fkey FOREIGN KEY (prev_issue_id) REFERENCES public.issues(id) ON DELETE SET NULL;


--
-- Name: issues issues_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.issues
    ADD CONSTRAINT issues_report_id_fkey FOREIGN KEY (report_id) REFERENCES public.ai_reports(id) ON DELETE CASCADE;


--
-- Name: issues issues_resolved_by_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.issues
    ADD CONSTRAINT issues_resolved_by_report_id_fkey FOREIGN KEY (resolved_by_report_id) REFERENCES public.ai_reports(id) ON DELETE SET NULL;


--
-- Name: issues issues_response_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.issues
    ADD CONSTRAINT issues_response_version_id_fkey FOREIGN KEY (response_version_id) REFERENCES public.material_versions(id) ON DELETE SET NULL;


--
-- Name: issues issues_reviewed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.issues
    ADD CONSTRAINT issues_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: issues issues_submission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.issues
    ADD CONSTRAINT issues_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES public.submissions(id) ON DELETE CASCADE;


--
-- Name: jobs jobs_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: jobs jobs_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.jobs(id) ON DELETE CASCADE;


--
-- Name: material_types material_types_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.material_types
    ADD CONSTRAINT material_types_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: material_versions material_versions_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.material_versions
    ADD CONSTRAINT material_versions_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(id) ON DELETE CASCADE;


--
-- Name: material_versions material_versions_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.material_versions
    ADD CONSTRAINT material_versions_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: materials materials_archive_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_archive_id_fkey FOREIGN KEY (archive_id) REFERENCES public.archives(id) ON DELETE CASCADE;


--
-- Name: materials materials_declared_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_declared_type_id_fkey FOREIGN KEY (declared_type_id) REFERENCES public.material_types(id) ON DELETE SET NULL;


--
-- Name: materials materials_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: materials materials_stage_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_stage_code_fkey FOREIGN KEY (stage_code) REFERENCES public.stages(code);


--
-- Name: materials materials_submission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES public.submissions(id) ON DELETE CASCADE;


--
-- Name: materials materials_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.material_types(id) ON DELETE SET NULL;


--
-- Name: materials materials_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: messages messages_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: notices notices_archive_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notices
    ADD CONSTRAINT notices_archive_id_fkey FOREIGN KEY (archive_id) REFERENCES public.archives(id) ON DELETE CASCADE;


--
-- Name: notices notices_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notices
    ADD CONSTRAINT notices_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: notices notices_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notices
    ADD CONSTRAINT notices_report_id_fkey FOREIGN KEY (report_id) REFERENCES public.ai_reports(id) ON DELETE SET NULL;


--
-- Name: notices notices_student_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notices
    ADD CONSTRAINT notices_student_user_id_fkey FOREIGN KEY (student_user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: notices notices_submission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notices
    ADD CONSTRAINT notices_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES public.submissions(id) ON DELETE CASCADE;


--
-- Name: orgs orgs_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orgs
    ADD CONSTRAINT orgs_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.orgs(id) ON DELETE RESTRICT;


--
-- Name: parse_results parse_results_corrected_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parse_results
    ADD CONSTRAINT parse_results_corrected_by_fkey FOREIGN KEY (corrected_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: parse_results parse_results_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parse_results
    ADD CONSTRAINT parse_results_version_id_fkey FOREIGN KEY (version_id) REFERENCES public.material_versions(id) ON DELETE CASCADE;


--
-- Name: political_terms political_terms_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.political_terms
    ADD CONSTRAINT political_terms_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: prompt_templates prompt_templates_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prompt_templates
    ADD CONSTRAINT prompt_templates_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: review_records review_records_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.review_records
    ADD CONSTRAINT review_records_report_id_fkey FOREIGN KEY (report_id) REFERENCES public.ai_reports(id) ON DELETE SET NULL;


--
-- Name: review_records review_records_reviewer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.review_records
    ADD CONSTRAINT review_records_reviewer_id_fkey FOREIGN KEY (reviewer_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: review_records review_records_submission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.review_records
    ADD CONSTRAINT review_records_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES public.submissions(id) ON DELETE CASCADE;


--
-- Name: rule_versions rule_versions_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rule_versions
    ADD CONSTRAINT rule_versions_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: sensitive_phrases sensitive_phrases_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sensitive_phrases
    ADD CONSTRAINT sensitive_phrases_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: submissions submissions_archive_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_archive_id_fkey FOREIGN KEY (archive_id) REFERENCES public.archives(id) ON DELETE CASCADE;


--
-- Name: submissions submissions_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES public.batches(id) ON DELETE SET NULL;


--
-- Name: submissions submissions_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.orgs(id) ON DELETE RESTRICT;


--
-- Name: submissions submissions_college_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_college_id_fkey FOREIGN KEY (college_id) REFERENCES public.orgs(id) ON DELETE RESTRICT;


--
-- Name: submissions submissions_filed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_filed_by_fkey FOREIGN KEY (filed_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: submissions submissions_stage_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_stage_code_fkey FOREIGN KEY (stage_code) REFERENCES public.stages(code);


--
-- Name: suggestion_templates suggestion_templates_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suggestion_templates
    ADD CONSTRAINT suggestion_templates_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: system_settings system_settings_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_settings
    ADD CONSTRAINT system_settings_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: time_node_defs time_node_defs_required_from_stage_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_node_defs
    ADD CONSTRAINT time_node_defs_required_from_stage_fkey FOREIGN KEY (required_from_stage) REFERENCES public.stages(code);


--
-- Name: time_node_defs time_node_defs_stage_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_node_defs
    ADD CONSTRAINT time_node_defs_stage_code_fkey FOREIGN KEY (stage_code) REFERENCES public.stages(code);


--
-- Name: time_node_defs time_node_defs_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_node_defs
    ADD CONSTRAINT time_node_defs_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: time_node_extractions time_node_extractions_archive_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_node_extractions
    ADD CONSTRAINT time_node_extractions_archive_id_fkey FOREIGN KEY (archive_id) REFERENCES public.archives(id) ON DELETE CASCADE;


--
-- Name: time_node_extractions time_node_extractions_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_node_extractions
    ADD CONSTRAINT time_node_extractions_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(id) ON DELETE CASCADE;


--
-- Name: time_node_extractions time_node_extractions_material_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_node_extractions
    ADD CONSTRAINT time_node_extractions_material_version_id_fkey FOREIGN KEY (material_version_id) REFERENCES public.material_versions(id) ON DELETE CASCADE;


--
-- Name: time_rules time_rules_suggestion_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_rules
    ADD CONSTRAINT time_rules_suggestion_template_id_fkey FOREIGN KEY (suggestion_template_id) REFERENCES public.suggestion_templates(id) ON DELETE SET NULL;


--
-- Name: time_rules time_rules_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_rules
    ADD CONSTRAINT time_rules_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: user_roles user_roles_org_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_org_id_fkey FOREIGN KEY (org_id) REFERENCES public.orgs(id) ON DELETE RESTRICT;


--
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: users users_org_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_org_id_fkey FOREIGN KEY (org_id) REFERENCES public.orgs(id) ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

\unrestrict d0phDmaZdf0gLSTcuYfKJMuMWmtLFAimPwHAkEpt2wybWERVbVFYkiOuntZ9Ons

