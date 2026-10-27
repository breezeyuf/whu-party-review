"""Validate the persisted time-rule DSL before publishing or previewing it."""
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from errors import unprocessable


Ref = Annotated[str, Field(min_length=1)]
Refs = list[Ref]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Duration(StrictModel):
    # Bounded configuration prevents unbounded workday iteration. Arithmetic
    # near the civil-calendar limits is also guarded by the evaluator.
    value: Annotated[int, Field(ge=0, le=10000)]
    unit: Literal["DAY", "WORKDAY", "MONTH", "YEAR"]


class Age(StrictModel):
    op: Literal["age_at_least"]
    birth: Ref
    at: Ref
    years: Annotated[int, Field(ge=0, le=150)]


class Before(StrictModel):
    op: Literal["before"]
    a: Ref
    b: Ref
    strict: bool = True
    min_gap: Duration | None = None
    max_gap: Duration | None = None


class Between(StrictModel):
    op: Literal["between"]
    x: Ref
    lower: Ref
    upper: Ref


class Within(StrictModel):
    op: Literal["within"]
    a: Ref
    b: Ref
    max: Duration


class AtLeast(StrictModel):
    op: Literal["at_least"]
    a: Ref
    b: Ref
    min: Duration


class DurationMin(StrictModel):
    op: Literal["duration_min"]
    node: Ref
    min: Duration
    or_hours: Annotated[float, Field(ge=0, allow_inf_nan=False)] | None = None


class SequenceRange(StrictModel):
    op: Literal["seq_in_range"]
    seq: Ref
    start: Ref = Field(alias="from")
    to: Ref


class SequenceGap(SequenceRange):
    op: Literal["seq_max_gap"]
    max: Duration


class SequenceCount(SequenceRange):
    op: Literal["seq_period_count"]
    period_months: Annotated[int, Field(gt=0, le=120000)]
    min_per_period: Annotated[int, Field(ge=0)] = 1


class SelectedNodes(StrictModel):
    op: Literal["consistent", "valid_date"]
    nodes: Literal["*"] | Annotated[Refs, Field(min_length=1)] = "*"


class Required(StrictModel):
    op: Literal["required"]
    nodes_by_stage: Annotated[dict[Literal["1", "2", "3", "4", "5"], Refs], Field(min_length=1)]


class Monotonic(StrictModel):
    op: Literal["monotonic"]
    nodes: Annotated[Refs, Field(min_length=1)]


class Derive(StrictModel):
    op: Literal["derive"]
    name: Ref
    base: Ref
    offset: Duration


Check = Annotated[
    Union[Age, Before, Between, Within, AtLeast, DurationMin, SequenceRange,
          SequenceGap, SequenceCount, SelectedNodes, Required, Monotonic, Derive],
    Field(discriminator="op"),
]


class TimeParams(StrictModel):
    checks: Annotated[list[Check], Field(min_length=1)]


def validate_time_params(params, node_codes) -> dict:
    try:
        validated = TimeParams.model_validate(params).model_dump(by_alias=True, exclude_none=True)
    except ValidationError as exc:
        raise unprocessable("时间规则参数无效", [
            {"field": ".".join(map(str, err["loc"])), "message": err["msg"]}
            for err in exc.errors(include_input=False, include_url=False)
        ]) from None
    codes = set(node_codes)
    errors = []
    for index, check in enumerate(validated["checks"]):
        refs = []
        for key in ("a", "b", "x", "lower", "upper", "birth", "at", "from", "to", "base"):
            if key in check:
                refs.append((key, check[key], "date"))
        for key in ("node", "name", "seq"):
            if key in check:
                refs.append((key, check[key], "sequence" if key == "seq" else "node"))
        if isinstance(check.get("nodes"), list):
            refs.extend((f"nodes.{i}", ref, "node") for i, ref in enumerate(check["nodes"]))
        for stage, values in check.get("nodes_by_stage", {}).items():
            refs.extend((f"nodes_by_stage.{stage}.{i}", ref, "node") for i, ref in enumerate(values))
        for key, ref, kind in refs:
            if kind == "date" and ref in ("$today", "$upload_date"):
                continue
            code = ref
            if kind == "date" and ref.endswith(".end"):
                code = ref[:-4]
            elif kind == "sequence" and ref.endswith("[*]"):
                code = ref[:-3]
            if code not in codes:
                errors.append({"field": f"checks.{index}.{key}", "message": f"节点引用不存在或不适用于该参数：{ref}"})
    if errors:
        raise unprocessable("时间规则引用了无效节点", errors)
    return validated


def validate_published_time_params(db, params) -> dict:
    from models import TimeNodeDef
    return validate_time_params(params, (row.code for row in db.query(TimeNodeDef).all()))
