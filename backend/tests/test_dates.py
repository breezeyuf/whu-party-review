from datetime import date

from ai.dates import age_years, describe_interval, duration_meets, find_dates, parse_date


def test_parse_iso_and_cn():
    d, raw, err = parse_date("2024年3月15日")
    assert d == date(2024, 3, 15) and err is None
    d, _, err = parse_date("2024.3.15")
    assert d == date(2024, 3, 15)
    d, _, err = parse_date("二〇二四年三月十五日")
    assert d == date(2024, 3, 15)
    d, raw, err = parse_date("2024年3月")
    assert d is None and err


def test_find_dates_in_text():
    hits = find_dates("汇报于2025年3月25日提交，此前2024-09-10确定。")
    assert len(hits) >= 2
    assert hits[0]["date"] is not None


def test_fullwidth_digits_from_ocr():
    d, _, err = parse_date("2０2５年３月１日")
    assert d == date(2025, 3, 1) and err is None
    text = "申请人：演示学生\n２０２５年３月１日"
    hits = find_dates(text)
    assert hits and hits[0]["date"] == date(2025, 3, 1)
    assert text[hits[0]["start"]:hits[0]["end"]] == "２０２５年３月１日"


def test_age_and_duration():
    assert age_years(date(2003, 5, 12), date(2021, 5, 12)) == 18
    assert age_years(date(2003, 5, 12), date(2021, 5, 11)) == 17
    assert duration_meets(date(2024, 9, 10), date(2025, 9, 10), 1, "YEAR")
    assert not duration_meets(date(2024, 9, 10), date(2025, 8, 30), 1, "YEAR")
    assert "个月" in describe_interval(date(2024, 9, 10), date(2025, 8, 30))
