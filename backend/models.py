from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    SmallInteger,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Stage(Base):
    __tablename__ = "stages"
    code: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    stage_key: Mapped[str] = mapped_column(Text, unique=True)
    name: Mapped[str] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(SmallInteger)


class Org(Base):
    __tablename__ = "orgs"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("orgs.id", ondelete="RESTRICT"))
    org_type: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    code: Mapped[Optional[str]] = mapped_column(Text, unique=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    parent: Mapped[Optional["Org"]] = relationship(remote_side="Org.id")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(Text, unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    real_name: Mapped[str] = mapped_column(Text)
    gender: Mapped[Optional[str]] = mapped_column(Text)
    org_id: Mapped[Optional[int]] = mapped_column(ForeignKey("orgs.id", ondelete="RESTRICT"))
    email: Mapped[Optional[str]] = mapped_column(Text)
    phone_enc: Mapped[Optional[str]] = mapped_column(Text)
    phone_masked: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=True)
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    token_version: Mapped[int] = mapped_column(Integer, default=0)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_login_ip: Mapped[Optional[str]] = mapped_column(Text)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    org: Mapped[Optional[Org]] = relationship()
    roles: Mapped[list["UserRole"]] = relationship(back_populates="user")


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role", "org_id", name="uq_user_roles"),)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(Text)
    org_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="RESTRICT"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    user: Mapped[User] = relationship(back_populates="roles")
    org: Mapped[Org] = relationship()


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"
    jti: Mapped[str] = mapped_column(Text, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    token_type: Mapped[str] = mapped_column(Text)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Batch(Base):
    __tablename__ = "batches"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True)
    year: Mapped[int] = mapped_column(SmallInteger)
    term: Mapped[str] = mapped_column(Text, default="FULL_YEAR")
    stage_codes: Mapped[Any] = mapped_column(JSONB, default=list)
    description: Mapped[Optional[str]] = mapped_column(Text)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    self_deadline: Mapped[Optional[date]] = mapped_column(Date)
    branch_deadline: Mapped[Optional[date]] = mapped_column(Date)
    cross_deadline: Mapped[Optional[date]] = mapped_column(Date)
    college_deadline: Mapped[Optional[date]] = mapped_column(Date)
    org_deadline: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(Text, default="ACTIVE")
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class CrossReviewPair(Base):
    __tablename__ = "cross_review_pairs"
    __table_args__ = (UniqueConstraint("batch_id", "target_branch_id", name="uq_cross_pairs"),)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id", ondelete="CASCADE"))
    college_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="RESTRICT"))
    target_branch_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="RESTRICT"))
    reviewer_branch_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="RESTRICT"))
    reviewer_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    target_branch: Mapped[Org] = relationship(foreign_keys=[target_branch_id])
    reviewer_branch: Mapped[Org] = relationship(foreign_keys=[reviewer_branch_id])
    reviewer_user: Mapped[Optional[User]] = relationship(foreign_keys=[reviewer_user_id])


class RuleVersion(Base):
    __tablename__ = "rule_versions"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    version_no: Mapped[int] = mapped_column(Integer, unique=True)
    change_kind: Mapped[str] = mapped_column(Text)
    change_action: Mapped[str] = mapped_column(Text)
    change_object_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    change_summary: Mapped[str] = mapped_column(Text)
    snapshot: Mapped[Any] = mapped_column(JSONB)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MaterialType(Base):
    __tablename__ = "material_types"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(Text, unique=True)
    name: Mapped[str] = mapped_column(Text)
    stage_codes: Mapped[Any] = mapped_column(JSONB, default=list)
    title_keywords: Mapped[Any] = mapped_column(JSONB, default=list)
    exclude_keywords: Mapped[Any] = mapped_column(JSONB, default=list)
    element_template: Mapped[Any] = mapped_column(JSONB, default=list)
    format_requirements: Mapped[Any] = mapped_column(JSONB, default=dict)
    date_node_map: Mapped[Any] = mapped_column(JSONB, default=dict)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ChecklistItem(Base):
    __tablename__ = "checklist_items"
    __table_args__ = (UniqueConstraint("stage_code", "material_type_id", name="uq_checklist"),)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    stage_code: Mapped[int] = mapped_column(ForeignKey("stages.code"))
    material_type_id: Mapped[int] = mapped_column(ForeignKey("material_types.id", ondelete="RESTRICT"))
    quantity_mode: Mapped[str] = mapped_column(Text, default="FIXED")
    fixed_count: Mapped[int] = mapped_column(Integer, default=1)
    period_months: Mapped[Optional[int]] = mapped_column(Integer)
    period_start_node: Mapped[Optional[str]] = mapped_column(Text)
    period_end_node: Mapped[Optional[str]] = mapped_column(Text)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    requirement_text: Mapped[Optional[str]] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    material_type: Mapped[MaterialType] = relationship()


class TimeNodeDef(Base):
    __tablename__ = "time_node_defs"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(Text, unique=True)
    name: Mapped[str] = mapped_column(Text)
    value_kind: Mapped[str] = mapped_column(Text)
    has_hours: Mapped[bool] = mapped_column(Boolean, default=False)
    stage_code: Mapped[Optional[int]] = mapped_column(ForeignKey("stages.code"))
    required_from_stage: Mapped[Optional[int]] = mapped_column(ForeignKey("stages.code"))
    source_material_codes: Mapped[Any] = mapped_column(JSONB, default=list)
    extract_keywords: Mapped[Any] = mapped_column(JSONB, default=list)
    derive_expr: Mapped[Optional[Any]] = mapped_column(JSONB(none_as_null=True))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SuggestionTemplate(Base):
    __tablename__ = "suggestion_templates"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(Text, unique=True)
    rule_code: Mapped[Optional[str]] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    template_text: Mapped[str] = mapped_column(Text)
    example_text: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class TimeRule(Base):
    __tablename__ = "time_rules"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(Text, unique=True)
    name: Mapped[str] = mapped_column(Text)
    rule_type: Mapped[str] = mapped_column(Text)
    params: Mapped[Any] = mapped_column(JSONB, default=dict)
    applies_stages: Mapped[Any] = mapped_column(JSONB, default=list)
    severity: Mapped[str] = mapped_column(Text)
    basis: Mapped[Optional[str]] = mapped_column(Text)
    message_template: Mapped[str] = mapped_column(Text)
    suggestion_template_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("suggestion_templates.id", ondelete="SET NULL")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class CheckRule(Base):
    __tablename__ = "check_rules"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(Text, unique=True)
    category: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    engine: Mapped[str] = mapped_column(Text)
    applies_to: Mapped[Any] = mapped_column(JSONB, default=list)
    params: Mapped[Any] = mapped_column(JSONB, default=dict)
    severity: Mapped[str] = mapped_column(Text)
    needs_human_judgement: Mapped[bool] = mapped_column(Boolean, default=False)
    basis: Mapped[Optional[str]] = mapped_column(Text)
    message_template: Mapped[str] = mapped_column(Text)
    suggestion_template_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("suggestion_templates.id", ondelete="SET NULL")
    )
    is_optional: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PoliticalTerm(Base):
    __tablename__ = "political_terms"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    term_type: Mapped[str] = mapped_column(Text, default="VARIANT")
    standard_text: Mapped[str] = mapped_column(Text, unique=True)
    wrong_variants: Mapped[Any] = mapped_column(JSONB, default=list)
    sequence_items: Mapped[Any] = mapped_column(JSONB, default=list)
    category: Mapped[Optional[str]] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(Text, default="WARN")
    note: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SensitivePhrase(Base):
    __tablename__ = "sensitive_phrases"
    __table_args__ = (UniqueConstraint("phrase", "category", name="uq_sensitive"),)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    phrase: Mapped[str] = mapped_column(Text)
    match_type: Mapped[str] = mapped_column(Text, default="KEYWORD")
    category: Mapped[str] = mapped_column(Text)
    risk_level: Mapped[str] = mapped_column(Text, default="MEDIUM")
    risk_note: Mapped[Optional[str]] = mapped_column(Text)
    suggestion: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(Text, unique=True)
    name: Mapped[str] = mapped_column(Text)
    system_prompt: Mapped[str] = mapped_column(Text)
    user_prompt: Mapped[str] = mapped_column(Text)
    output_schema: Mapped[Any] = mapped_column(JSONB, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Archive(Base):
    __tablename__ = "archives"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    student_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), unique=True)
    student_no: Mapped[str] = mapped_column(Text, unique=True)
    real_name: Mapped[str] = mapped_column(Text)
    gender: Mapped[Optional[str]] = mapped_column(Text)
    ethnicity: Mapped[Optional[str]] = mapped_column(Text)
    birth_date: Mapped[Optional[date]] = mapped_column(Date)
    native_place: Mapped[Optional[str]] = mapped_column(Text)
    id_card_enc: Mapped[Optional[str]] = mapped_column(Text)
    id_card_masked: Mapped[Optional[str]] = mapped_column(Text)
    major: Mapped[Optional[str]] = mapped_column(Text)
    class_name: Mapped[Optional[str]] = mapped_column(Text)
    college_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="RESTRICT"))
    branch_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="RESTRICT"))
    batch_id: Mapped[Optional[int]] = mapped_column(ForeignKey("batches.id", ondelete="SET NULL"))
    current_stage: Mapped[int] = mapped_column(SmallInteger, default=1)
    status: Mapped[str] = mapped_column(Text, default="ACTIVE")
    profile_extra: Mapped[Any] = mapped_column(JSONB, default=dict)
    anon_code: Mapped[str] = mapped_column(Text, unique=True)
    data_source: Mapped[str] = mapped_column(Text, default="MANUAL")
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    timeline_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    student: Mapped[User] = relationship(foreign_keys=[student_user_id])
    college: Mapped[Org] = relationship(foreign_keys=[college_id])
    branch: Mapped[Org] = relationship(foreign_keys=[branch_id])
    batch: Mapped[Optional[Batch]] = relationship()


class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (UniqueConstraint("archive_id", "stage_code", name="uq_submissions_stage"),)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    archive_id: Mapped[int] = mapped_column(ForeignKey("archives.id", ondelete="CASCADE"))
    stage_code: Mapped[int] = mapped_column(SmallInteger)
    batch_id: Mapped[Optional[int]] = mapped_column(ForeignKey("batches.id", ondelete="SET NULL"))
    college_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="RESTRICT"))
    branch_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="RESTRICT"))
    status: Mapped[str] = mapped_column(Text, default="DRAFT")
    return_level: Mapped[Optional[str]] = mapped_column(Text)
    round_no: Mapped[int] = mapped_column(Integer, default=1)
    latest_report_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    ai_status: Mapped[str] = mapped_column(Text, default="NONE")
    ai_job_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    level_entered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    filed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    filed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    archive: Mapped[Archive] = relationship()


class Material(Base):
    __tablename__ = "materials"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    archive_id: Mapped[int] = mapped_column(ForeignKey("archives.id", ondelete="CASCADE"))
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"))
    stage_code: Mapped[int] = mapped_column(SmallInteger)
    title: Mapped[str] = mapped_column(Text)
    declared_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("material_types.id", ondelete="SET NULL"))
    type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("material_types.id", ondelete="SET NULL"))
    type_source: Mapped[Optional[str]] = mapped_column(Text)
    type_confidence: Mapped[Optional[float]] = mapped_column(Float)
    type_status: Mapped[str] = mapped_column(Text, default="PENDING")
    current_version_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    version_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(Text, default="ACTIVE")
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    deleted_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    uploaded_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    declared_type: Mapped[Optional[MaterialType]] = relationship(foreign_keys=[declared_type_id])
    type: Mapped[Optional[MaterialType]] = relationship(foreign_keys=[type_id])
    archive: Mapped[Archive] = relationship()
    submission: Mapped[Submission] = relationship()


class MaterialVersion(Base):
    __tablename__ = "material_versions"
    __table_args__ = (UniqueConstraint("material_id", "version_no", name="uq_material_versions"),)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id", ondelete="CASCADE"))
    version_no: Mapped[int] = mapped_column(Integer)
    original_filename: Mapped[str] = mapped_column(Text)
    stored_path: Mapped[str] = mapped_column(Text, unique=True)
    file_ext: Mapped[str] = mapped_column(Text)
    mime_type: Mapped[str] = mapped_column(Text)
    file_size: Mapped[int] = mapped_column(BigInteger)
    sha256: Mapped[str] = mapped_column(Text)
    page_count: Mapped[Optional[int]] = mapped_column(Integer)
    change_note: Mapped[Optional[str]] = mapped_column(Text)
    parse_status: Mapped[str] = mapped_column(Text, default="PENDING")
    parse_error: Mapped[Optional[str]] = mapped_column(Text)
    parsed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_frozen: Mapped[bool] = mapped_column(Boolean, default=False)
    uploaded_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    material: Mapped[Material] = relationship()


class ParseResult(Base):
    __tablename__ = "parse_results"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    version_id: Mapped[int] = mapped_column(ForeignKey("material_versions.id", ondelete="CASCADE"), unique=True)
    parser: Mapped[str] = mapped_column(Text)
    ocr_engine: Mapped[Optional[str]] = mapped_column(Text)
    preview_pdf_path: Mapped[Optional[str]] = mapped_column(Text)
    full_text: Mapped[str] = mapped_column(Text, default="")
    char_count: Mapped[int] = mapped_column(Integer, default=0)
    pages: Mapped[Any] = mapped_column(JSONB, default=list)
    visual_marks: Mapped[Any] = mapped_column(JSONB, default=dict)
    extracted_fields: Mapped[Any] = mapped_column(JSONB, default=dict)
    format_features: Mapped[Any] = mapped_column(JSONB, default=dict)
    warnings: Mapped[Any] = mapped_column(JSONB, default=list)
    corrected_text: Mapped[Optional[str]] = mapped_column(Text)
    corrected_fields: Mapped[Optional[Any]] = mapped_column(JSONB(none_as_null=True))
    corrected_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    corrected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    version: Mapped[MaterialVersion] = relationship()


class TimeNodeExtraction(Base):
    __tablename__ = "time_node_extractions"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    archive_id: Mapped[int] = mapped_column(ForeignKey("archives.id", ondelete="CASCADE"))
    node_code: Mapped[str] = mapped_column(Text)
    material_id: Mapped[Optional[int]] = mapped_column(ForeignKey("materials.id", ondelete="CASCADE"))
    material_version_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("material_versions.id", ondelete="CASCADE")
    )
    seq_index: Mapped[int] = mapped_column(Integer, default=0)
    value_date: Mapped[Optional[date]] = mapped_column(Date)
    value_end_date: Mapped[Optional[date]] = mapped_column(Date)
    hours: Mapped[Optional[float]] = mapped_column(Float)
    raw_text: Mapped[Optional[str]] = mapped_column(Text)
    invalid_reason: Mapped[Optional[str]] = mapped_column(Text)
    page_no: Mapped[Optional[int]] = mapped_column(Integer)
    bbox: Mapped[Optional[Any]] = mapped_column(JSONB(none_as_null=True))
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    method: Mapped[str] = mapped_column(Text)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ArchiveTimeNode(Base):
    __tablename__ = "archive_time_nodes"
    __table_args__ = (UniqueConstraint("archive_id", "node_code", name="uq_archive_time_nodes"),)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    archive_id: Mapped[int] = mapped_column(ForeignKey("archives.id", ondelete="CASCADE"))
    node_code: Mapped[str] = mapped_column(Text)
    value_date: Mapped[Optional[date]] = mapped_column(Date)
    value_end_date: Mapped[Optional[date]] = mapped_column(Date)
    hours: Mapped[Optional[float]] = mapped_column(Float)
    seq_count: Mapped[int] = mapped_column(Integer, default=0)
    source_extraction_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("time_node_extractions.id", ondelete="SET NULL")
    )
    source_count: Mapped[int] = mapped_column(Integer, default=0)
    has_conflict: Mapped[bool] = mapped_column(Boolean, default=False)
    corrected_date: Mapped[Optional[date]] = mapped_column(Date)
    corrected_end_date: Mapped[Optional[date]] = mapped_column(Date)
    corrected_hours: Mapped[Optional[float]] = mapped_column(Float)
    correction_reason: Mapped[Optional[str]] = mapped_column(Text)
    corrected_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    corrected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    locked: Mapped[bool] = mapped_column(Boolean, default=False)
    locked_stage: Mapped[Optional[int]] = mapped_column(SmallInteger)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    job_type: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, default="QUEUED")
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"))
    target_type: Mapped[Optional[str]] = mapped_column(Text)
    target_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    params: Mapped[Any] = mapped_column(JSONB, default=dict)
    total: Mapped[int] = mapped_column(Integer, default=1)
    done_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    stage_text: Mapped[Optional[str]] = mapped_column(Text)
    result: Mapped[Optional[Any]] = mapped_column(JSONB(none_as_null=True))
    error: Mapped[Optional[str]] = mapped_column(Text)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    heartbeat_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    creator: Mapped[Optional[User]] = relationship()


class BatchUploadItem(Base):
    __tablename__ = "batch_upload_items"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"))
    entry_path: Mapped[str] = mapped_column(Text)
    temp_path: Mapped[Optional[str]] = mapped_column(Text)
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger)
    parsed_student_no: Mapped[Optional[str]] = mapped_column(Text)
    parsed_type_hint: Mapped[Optional[str]] = mapped_column(Text)
    matched_archive_id: Mapped[Optional[int]] = mapped_column(ForeignKey("archives.id", ondelete="SET NULL"))
    match_method: Mapped[Optional[str]] = mapped_column(Text)
    material_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("material_types.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(Text, default="UNMATCHED")
    material_id: Mapped[Optional[int]] = mapped_column(ForeignKey("materials.id", ondelete="SET NULL"))
    error: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    matched_archive: Mapped[Optional[Archive]] = relationship()
    material_type: Mapped[Optional[MaterialType]] = relationship()


class AiReport(Base):
    __tablename__ = "ai_reports"
    __table_args__ = (UniqueConstraint("submission_id", "report_no", name="uq_ai_reports_no"),)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"))
    report_no: Mapped[int] = mapped_column(Integer)
    trigger_type: Mapped[str] = mapped_column(Text)
    triggered_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    job_id: Mapped[Optional[int]] = mapped_column(ForeignKey("jobs.id", ondelete="SET NULL"))
    rule_version_id: Mapped[int] = mapped_column(ForeignKey("rule_versions.id", ondelete="RESTRICT"))
    mode: Mapped[str] = mapped_column(Text)
    llm_model: Mapped[Optional[str]] = mapped_column(Text)
    ocr_engine: Mapped[Optional[str]] = mapped_column(Text)
    degrade_reason: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, default="RUNNING")
    material_versions: Mapped[Any] = mapped_column(JSONB, default=list)
    changed_materials: Mapped[Any] = mapped_column(JSONB, default=list)
    classification: Mapped[Any] = mapped_column(JSONB, default=list)
    completeness: Mapped[Any] = mapped_column(JSONB, default=dict)
    timeline_snapshot: Mapped[Any] = mapped_column(JSONB, default=dict)
    rule_results: Mapped[Any] = mapped_column(JSONB, default=list)
    summary: Mapped[Any] = mapped_column(JSONB, default=dict)
    recommendation: Mapped[Optional[str]] = mapped_column(Text)
    handover_status: Mapped[Optional[str]] = mapped_column(Text)
    effective_recommendation: Mapped[Optional[str]] = mapped_column(Text)
    handover_reasons: Mapped[Any] = mapped_column(JSONB, default=list)
    recheck_of_report_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ai_reports.id", ondelete="SET NULL"))
    recheck_summary: Mapped[Optional[Any]] = mapped_column(JSONB(none_as_null=True))
    error: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    rule_version: Mapped[RuleVersion] = relationship()
    submission: Mapped[Submission] = relationship()


class HandoverRecord(Base):
    __tablename__ = "handover_records"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("ai_reports.id", ondelete="CASCADE"))
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"))
    assignee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    assignee_name: Mapped[str] = mapped_column(Text)
    assignee_role: Mapped[str] = mapped_column(Text)
    reason_codes: Mapped[Any] = mapped_column(JSONB, default=list)
    handover_reason: Mapped[Optional[str]] = mapped_column(Text)
    ai_recommendation: Mapped[Optional[str]] = mapped_column(Text)
    human_decision: Mapped[str] = mapped_column(Text)
    effective_recommendation: Mapped[str] = mapped_column(Text)
    issue_ids: Mapped[Any] = mapped_column(JSONB, default=list)
    material_ids: Mapped[Any] = mapped_column(JSONB, default=list)
    confidence_snapshot: Mapped[Any] = mapped_column(JSONB, default=dict)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ip: Mapped[Optional[str]] = mapped_column(Text)


class Issue(Base):
    __tablename__ = "issues"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"))
    report_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ai_reports.id", ondelete="CASCADE"))
    material_id: Mapped[Optional[int]] = mapped_column(ForeignKey("materials.id", ondelete="SET NULL"))
    material_version_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("material_versions.id", ondelete="SET NULL")
    )
    source: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(Text)
    rule_code: Mapped[Optional[str]] = mapped_column(Text)
    rule_basis: Mapped[Optional[str]] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    location: Mapped[Any] = mapped_column(JSONB, default=dict)
    actual_value: Mapped[Optional[str]] = mapped_column(Text)
    expected_value: Mapped[Optional[str]] = mapped_column(Text)
    suggestion: Mapped[Optional[str]] = mapped_column(Text)
    suggestion_example: Mapped[Optional[str]] = mapped_column(Text)
    needs_human_judgement: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    fingerprint: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    review_status: Mapped[str] = mapped_column(Text, default="PENDING")
    review_level: Mapped[Optional[str]] = mapped_column(Text)
    reviewed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    review_note: Mapped[Optional[str]] = mapped_column(Text)
    original_snapshot: Mapped[Optional[Any]] = mapped_column(JSONB(none_as_null=True))
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_level: Mapped[Optional[str]] = mapped_column(Text)
    response_type: Mapped[Optional[str]] = mapped_column(Text)
    response_text: Mapped[Optional[str]] = mapped_column(Text)
    response_version_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("material_versions.id", ondelete="SET NULL")
    )
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    resolution: Mapped[str] = mapped_column(Text, default="OPEN")
    resolved_by_report_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ai_reports.id", ondelete="SET NULL"))
    prev_issue_id: Mapped[Optional[int]] = mapped_column(ForeignKey("issues.id", ondelete="SET NULL"))
    is_new_in_recheck: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    material: Mapped[Optional[Material]] = relationship(foreign_keys=[material_id])


class ReviewRecord(Base):
    __tablename__ = "review_records"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"))
    level: Mapped[str] = mapped_column(Text)
    action: Mapped[str] = mapped_column(Text)
    from_status: Mapped[str] = mapped_column(Text)
    to_status: Mapped[str] = mapped_column(Text)
    reviewer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    reviewer_name: Mapped[str] = mapped_column(Text)
    reviewer_role: Mapped[str] = mapped_column(Text)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    report_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ai_reports.id", ondelete="SET NULL"))
    issue_ids: Mapped[Any] = mapped_column(JSONB, default=list)
    round_no: Mapped[int] = mapped_column(Integer)
    is_batch: Mapped[bool] = mapped_column(Boolean, default=False)
    ip: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Notice(Base):
    __tablename__ = "notices"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    notice_type: Mapped[str] = mapped_column(Text)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"))
    archive_id: Mapped[int] = mapped_column(ForeignKey("archives.id", ondelete="CASCADE"))
    student_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    report_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ai_reports.id", ondelete="SET NULL"))
    round_no: Mapped[int] = mapped_column(Integer, default=1)
    title: Mapped[str] = mapped_column(Text)
    content: Mapped[Any] = mapped_column(JSONB)
    deadline: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(Text, default="DRAFT")
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    archive: Mapped[Archive] = relationship()
    creator: Mapped[Optional[User]] = relationship(foreign_keys=[created_by])


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    msg_type: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text, default="")
    link_type: Mapped[Optional[str]] = mapped_column(Text)
    link_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    dedup_key: Mapped[Optional[str]] = mapped_column(Text, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    username: Mapped[Optional[str]] = mapped_column(Text)
    role: Mapped[Optional[str]] = mapped_column(Text)
    action: Mapped[str] = mapped_column(Text)
    object_type: Mapped[Optional[str]] = mapped_column(Text)
    object_id: Mapped[Optional[str]] = mapped_column(Text)
    detail: Mapped[Any] = mapped_column(JSONB, default=dict)
    ip: Mapped[Optional[str]] = mapped_column(Text)
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SystemSetting(Base):
    __tablename__ = "system_settings"
    key: Mapped[str] = mapped_column(Text, primary_key=True)
    value: Mapped[Any] = mapped_column(JSONB)
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ExportFile(Base):
    __tablename__ = "export_files"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    export_type: Mapped[str] = mapped_column(Text)
    params: Mapped[Any] = mapped_column(JSONB, default=dict)
    file_name: Mapped[str] = mapped_column(Text)
    stored_path: Mapped[str] = mapped_column(Text)
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ImportPasswordFile(Base):
    __tablename__ = "import_password_files"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    encrypted_payload: Mapped[Optional[str]] = mapped_column(Text)
    file_name: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    consumed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class SchemaMeta(Base):
    __tablename__ = "schema_meta"
    key: Mapped[str] = mapped_column(Text, primary_key=True)
    value: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

