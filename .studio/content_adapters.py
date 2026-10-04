"""Offline normalization of the five Douyin single-publication XLSX exports."""
from abc import ABC, abstractmethod
from datetime import date, timedelta
import hashlib
import math
from pathlib import Path
import posixpath
import re
import xml.etree.ElementTree as ET
from zipfile import BadZipFile, ZipFile

VERSION = "douyin-xlsx/1"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
POINT_LABELS = {
    "封面点击率": "cover_click_rate", "2s跳出率": "bounce_2s", "2秒跳出率": "bounce_2s",
    "5s完播率": "completion_5s", "5秒完播率": "completion_5s", "完播率": "completion_rate",
    "平均播放时长": "average_watch_seconds", "平均播放占比": "average_watch_ratio",
    "点赞率": "like_rate", "评论率": "comment_rate", "分享率": "share_rate",
    "收藏率": "favorite_rate", "弹幕量": "danmaku_count", "涨粉量": "followers",
    "涨粉率": "follower_rate", "脱粉量": "unfollows", "脱粉率": "unfollow_rate",
    "不感兴趣量": "uninterested_count", "不感兴趣率": "uninterested_rate",
}
POINT_KEYS = tuple(dict.fromkeys(POINT_LABELS.values()))
DAILY_KEYS = ("posts", "plays", "likes", "shares", "comments", "completion_5s",
              "bounce_2s", "cover_click_rate", "average_watch_seconds")
TABLE_LABELS = {
    **POINT_LABELS, "时间": "time", "日期": "date", "跳过率": "skip_rate",
    "回看率": "rewatch_rate", "当前作品": "danmaku", "同类作品": "peer_danmaku",
    "总播放量": "plays", "播放量": "plays", "投稿量": "posts", "总点赞量": "likes",
    "总分享量": "shares", "总评论量": "comments", "抖音": "douyin",
    "抖音精选": "douyin_selected", "来源": "source", "来源占比": "share",
    "对比7日": "comparison_7d",
}


def _label(value):
    return re.sub(r"\s+", "", str(value if value is not None else "")).lower()


def _number(value):
    if value is None or str(value).strip() in ("", "--", "-", "—", "未提供"):
        return None
    if isinstance(value, (int, float)):
        result = value
    else:
        text = str(value).strip().replace(",", "").replace("，", "")
        percentage = text.endswith(("%", "％"))
        text = re.sub(r"(?:秒|s|%|％)$", "", text, flags=re.I).strip()
        result = float(text) / (100 if percentage else 1)
    if not math.isfinite(result):
        raise ValueError("指标不是有限数值")
    return result


def _interval(value):
    match = re.fullmatch(r"\s*(\d+):(\d{2}(?:\.\d+)?)\s*[-–—]\s*(\d+):(\d{2}(?:\.\d+)?)\s*", str(value))
    if not match:
        raise ValueError(f"无法解析分段时间：{value}")
    a, b, c, d = map(float, match.groups())
    if b >= 60 or d >= 60 or c * 60 + d <= a * 60 + b:
        raise ValueError(f"无效分段时间：{value}")
    return a * 60 + b, c * 60 + d


def _date(value):
    if isinstance(value, (int, float)):
        return (date(1899, 12, 30) + timedelta(days=value)).isoformat()
    text = str(value).strip().replace("/", "-")
    return date.fromisoformat(text[:10]).isoformat()


def _sheets(path):
    """Resolve workbook relationships; sparse cell references retain column positions.

    Excel numeric percent cells already hold fractions. Styles must not multiply
    those values; the normalized representation is the stored numeric value.
    """
    with ZipFile(path) as archive:
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            strings = ["".join(node.itertext()) for node in root.findall("m:si", NS)]
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {node.attrib["Id"]: node.attrib["Target"] for node in relationships
                   if node.attrib.get("TargetMode") != "External"}
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        for sheet in workbook.findall("m:sheets/m:sheet", NS):
            target = targets[sheet.attrib[REL]]
            member = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join("xl", target))
            root = ET.fromstring(archive.read(member))
            rows = []
            for row in root.findall("m:sheetData/m:row", NS):
                values = []
                for cell in row.findall("m:c", NS):
                    letters = re.match(r"[A-Z]+", cell.attrib.get("r", ""))
                    column = 0
                    for letter in letters.group() if letters else "":
                        column = column * 26 + ord(letter) - ord("A") + 1
                    column = column - 1 if column else len(values)
                    while len(values) <= column:
                        values.append(None)
                    value = cell.findtext("m:v", namespaces=NS)
                    kind = cell.attrib.get("t")
                    if kind == "inlineStr":
                        value = "".join(node.text or "" for node in cell.findall("m:is//m:t", NS))
                    elif kind == "s" and value is not None:
                        value = strings[int(value)]
                    elif kind not in ("str", "e", "d") and value is not None:
                        value = _number(value)
                    values[column] = value
                if any(value is not None for value in values):
                    rows.append(values)
            yield sheet.attrib["name"], rows


class ContentAdapter(ABC):
    @abstractmethod
    def normalize(self, files, *, cutoff_date, imported_at):
        """Return points, segments, daily, traffic_sources and provenance."""


class ApiAdapter(ContentAdapter):
    def normalize(self, files=None, *, cutoff_date=None, imported_at=None):
        raise NotImplementedError("API 适配器未实现")


class XlsxAdapter(ContentAdapter):
    def normalize(self, files, *, cutoff_date, imported_at):
        cutoff_date = _date(cutoff_date)
        result = {"points": dict.fromkeys(POINT_KEYS), "segments": [], "daily": [],
                  "traffic_sources": [], "plays": None, "cutoff_date": cutoff_date,
                  "warnings": [], "unknown_columns": [],
                  "provenance": {"adapter_version": VERSION, "imported_at": imported_at,
                                 "cutoff_date": cutoff_date, "files": []}}
        segments, daily, daily_plays = {}, {}, {}
        datasets, sources = set(), set()

        def identify(keys):
            keys = set(keys)
            if "date" in keys:
                if "plays" in keys or (keys.intersection(DAILY_KEYS) and not keys.intersection({"followers", "douyin", "douyin_selected"})):
                    datasets.add("daily_plays")
                elif keys.intersection({"followers", "douyin", "douyin_selected"}):
                    datasets.add("audience")
                return
            if "source" in keys:
                datasets.add("traffic")
            if keys.intersection({"cover_click_rate", "average_watch_seconds", "bounce_2s", "completion_5s",
                                  "completion_rate", "average_watch_ratio", "skip_rate", "rewatch_rate"}):
                datasets.add("attraction")
            if keys.intersection({"like_rate", "comment_rate", "share_rate", "favorite_rate", "danmaku_count", "danmaku", "peer_danmaku"}):
                datasets.add("engagement")
            if keys.intersection({"followers", "follower_rate", "unfollows", "unfollow_rate", "uninterested_count"}):
                datasets.add("audience")

        def convert(value, context):
            try:
                return _number(value)
            except (TypeError, ValueError):
                result["warnings"].append(f"{context}：无法解析数值 {value!r}")
                return None

        def unknown(path, sheet, column, values):
            result["unknown_columns"].append({"file": path.name, "sheet": sheet,
                                               "column": column, "values": values})

        paths = files.values() if isinstance(files, dict) else files
        for filename in paths:
            path = Path(filename)
            result["provenance"]["files"].append({"name": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
            try:
                sheets = list(_sheets(path))
            except (BadZipFile, ET.ParseError, KeyError, IndexError) as error:
                raise ValueError(f"无效 XLSX 文件 {path.name}：{error}") from error
            for sheet, rows in sheets:
                if not rows:
                    continue
                # Export summary sheets may be metric/value rows or one horizontal row.
                first = [_label(v) for v in rows[0]]
                if not isinstance(rows[0][0], str) or not first[0]:
                    raise ValueError(f"{sheet}：首列表头必须是非空文字")
                vertical = first[0] in ("指标", "指标名称", "指标数据") or (
                    first[0] in POINT_LABELS and len(rows[0]) > 1 and first[1] not in TABLE_LABELS)
                if vertical:
                    metric_rows = rows[1:] if first[0] not in POINT_LABELS else rows
                    identify(POINT_LABELS.get(_label(row[0])) for row in metric_rows)
                    for row in metric_rows:
                        key = POINT_LABELS.get(_label(row[0]))
                        value = row[1] if len(row) > 1 else None
                        if key:
                            result["points"][key] = convert(value, f"{sheet}/{row[0]}")
                        else:
                            unknown(path, sheet, row[0], row[1:])
                    continue
                keys = [TABLE_LABELS.get(label) for label in first]
                identify(keys)
                full_daily = "date" in keys and ("plays" in keys or (
                    set(keys).intersection(DAILY_KEYS) and not set(keys).intersection({"followers", "douyin", "douyin_selected"})))
                known = [key for key in keys if key is not None]
                if len(known) != len(set(known)):
                    raise ValueError(f"{sheet}：重复指标列")
                body = rows[1:]
                seen_rows = set()
                for index, key in enumerate(keys):
                    if key is None:
                        unknown(path, sheet, rows[0][index], [row[index] if index < len(row) else None for row in body])
                for row in body:
                    raw = {key: row[i] if i < len(row) else None for i, key in enumerate(keys) if key}
                    if "date" in keys:
                        if raw.get("date") is None:
                            result["warnings"].append(f"{sheet}：缺日期，跳过行")
                            continue
                        day = _date(raw.pop("date"))
                        if day in seen_rows or (full_daily and day in daily_plays):
                            raise ValueError(f"{sheet}：重复日期 {day}")
                        seen_rows.add(day)
                        record = daily.setdefault(day, {"date": day, "plays": None})
                        if full_daily:
                            for key in DAILY_KEYS:
                                record[key] = convert(raw.get(key), f"{sheet}/{key}")
                                if record[key] is None:
                                    result["warnings"].append(f"daily.{day}.{key}：缺失，记 null")
                            daily_plays[day] = record["plays"]
                        else:
                            # Audience trends cannot overwrite full-export daily rates.
                            trends = {key: convert(value, f"{sheet}/{key}") for key, value in raw.items()}
                            existing = record.setdefault("audience_trends", {})
                            if set(existing).intersection(trends):
                                raise ValueError(f"{sheet}：重复每日趋势 {day}")
                            existing.update(trends)
                            for key in ("followers", "douyin", "douyin_selected"):
                                if key in trends:
                                    record[key] = trends[key]
                    elif "time" in keys:
                        start, end = _interval(raw.pop("time"))
                        if (start, end) in seen_rows:
                            raise ValueError(f"{sheet}：重复分段 {start}-{end}")
                        seen_rows.add((start, end))
                        record = segments.setdefault((start, end), {"start": start, "end": end, "skip_rate": None,
                                                   "rewatch_rate": None, "danmaku": None, "peer_danmaku": None})
                        record.update({key: convert(value, f"{sheet}/{key}") for key, value in raw.items()})
                    elif "source" in keys:
                        source = raw.get("source")
                        if not isinstance(source, str) or not source.strip():
                            raise ValueError(f"{sheet}：无效流量来源 {source!r}")
                        source = source.strip()
                        if source in sources:
                            raise ValueError(f"{sheet}：重复流量来源 {source}")
                        sources.add(source)
                        raw["source"] = source
                        result["traffic_sources"].append({"source": raw.get("source"), "share": convert(raw.get("share"), sheet),
                            "comparison_7d": convert(raw.get("comparison_7d"), sheet), "status": "已列出"})
                        for key in ("share", "comparison_7d"):
                            if result["traffic_sources"][-1][key] is None:
                                result["warnings"].append(f"traffic_sources.{raw.get('source')}.{key}：缺失，记 null")
                    else:
                        for key, value in raw.items():
                            if key in result["points"]:
                                result["points"][key] = convert(value, f"{sheet}/{key}")
        result["segments"] = [segments[key] for key in sorted(segments)]
        result["datasets"] = sorted(datasets)
        result["daily"] = [daily[key] for key in sorted(daily)]
        plays = [value for day, value in daily_plays.items() if day <= cutoff_date]
        if plays and all(value is not None for value in plays):
            result["plays"] = sum(plays)
        for key, value in result["points"].items():
            if value is None:
                result["warnings"].append(f"points.{key}：缺失，记 null")
        for index, segment in enumerate(result["segments"]):
            for key in ("skip_rate", "rewatch_rate", "danmaku", "peer_danmaku"):
                if segment[key] is None:
                    result["warnings"].append(f"segments[{index}].{key}：缺失，记 null")
        if result["plays"] is None:
            result["warnings"].append("plays：缺每日播放量，记 null")
        for source in ("搜索", "个人主页"):
            if not any(row["source"] == source for row in result["traffic_sources"]):
                result["traffic_sources"].append({"source": source, "share": None, "comparison_7d": None, "status": "未列出"})
        return result


DouyinXlsxAdapter = XlsxAdapter


def normalize(files, *, cutoff_date, imported_at):
    return XlsxAdapter().normalize(files, cutoff_date=cutoff_date, imported_at=imported_at)
