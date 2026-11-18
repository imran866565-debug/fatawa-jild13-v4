#!/usr/bin/env python3
"""Merge Fatawa Razviya Jild 13 easy-Urdu tashreeh v4 chunks into jild-13.json.

Reads the 14 leaf chunk files listed in chunks-manifest-v4-jild13.json,
concatenates them in order 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 ->
08 -> 09 -> 10 -> 11a -> 11b -> 11c -> 11d, derives start_page =
min(pages) where the field is absent, normalises page markers,
validates, and writes {"masail": [...]} to jild-13.json.

ORDER -- chunk order is the order:
  The v3 merged file ~/workspace/fatawa-app/content/tashreeh/jild-13.json
  has ID order == concatenation order of the v4 leaf chunks (verified
  locally by the coordinator: all 966 ids match the v3 sequence exactly).
  Do NOT sort or reorder. Within each chunk, items keep file order.
  CHUNK_ORDER is an explicit list because leaves 11a/11b/11c/11d
  break the numeric range pattern.

BOUNDARY DEDUP / FOLD (4 masail — the Jild 10 masala-87 / Jild 11 /
Jild 12 pattern):
  the v3 chunk files overlap by one item at 4 boundaries; the merged
  v3 has each ONCE with combined pages + combined notes. Each boundary
  masala is written ONCE, in the EARLIER leaf, combining both halves'
  tashreeh into one flowing passage with ALL notes from both halves:
  masala-11 (leaf 02, [197-201]), masala-94 (leaf 04, [323, 325] —
  the second half was v3 chunk 05's temporary item jild13-p325),
  masala-168 (leaf 06, [445-451]), masala-214 (leaf 08, [511-574] —
  the tail was v3 chunk 09's five temporary page items jild13-p563 /
  p564 / p566 / p569 / p571). The LATER leaf EXCLUDES the boundary
  masala (leaf 03 excludes masala-11, leaf 05 excludes jild13-p325,
  leaf 07 excludes masala-168, leaf 09 excludes the five page items).
  Leaf page ranges overlap at 7 shared pages (201, 325, 451, 574,
  664, 672, 679 — consecutive items sharing a page), so per-leaf
  present pages sum to 587 while the merged file has 580 UNIQUE
  pages. Those are v3 ids, kept exactly — they are NOT merge renames.

NO RENAME QUIRK in Jild 13: the v3 merged file has 966 UNIQUE ids — the
  book numbers no masala twice in this jild (unlike Jild 5, which had
  two masail 263 and two masail 304, and Jild 6, which had two masail
  774). Chunk ids are used exactly as written; the merge asserts
  duplicate-free ids instead of renaming anything.
  NOTE: v3 has split files 10a/10b in Jild 12, NOT Jild 13 — Jild 13's
  v3 has 11 chunk files (01-11); leaf 11 (715 maakhiz items, all empty
  sawal) was split by the coordinator into 11a/11b/11c/11d (~179 items
  each) to stay within proven file sizes. Leaf 01 has only 56 pages
  present in pp.4-152 (big source gaps). Leaf 08 is a SINGLE mega-
  masala (masala-214, 64 pages).

START_PAGE: every one of the 14 v4 leaf chunks carries start_page ==
  min(pages) for all its items (verified by the coordinator). The
  derivation code below stays as a safety net; it is expected to
  derive 0 items.

MARKER NORMALISATION (the only text transformation): page markers, if
  present, are normalised to the single form [safha N] written with the
  Urdu word for page:
  - lenticular-bracket form (U+3010/U+3011 around the Urdu word for
    page + number) -> [safha N]
  - [short form] -> [safha N]
  - [safha N] stays as-is
  Applied to every string field of every item (jawab, sawal, title,
  notes). The 14 v4 chunks contain ZERO markers of any form (verified
  locally), so normalisation is expected to be a no-op here; the code
  stays so the merge is robust and the "none remain" assertions still
  run. No other text is touched and no markers are invented.
  NOTE: the literal lenticular-bracket characters are written here only
  as U+3010/U+3011 escapes, never as literal characters in this file.

VALIDATION (fails loudly on any violation):
  966 items; ID sequence EXACTLY == the v3 merged file's ID sequence
  (embedded below as V3_IDS, copied verbatim from
  ~/workspace/fatawa-app/content/tashreeh/jild-13.json); pages per item
  identical to v3 (embedded as V3_PAGES, same source, verified against
  the v3 file before pushing); 580 unique pages (min 4, max 688);
  volume_ids == {56}; start_page == min(pages) for every item (after
  derivation); zero empty tashreeh_jawab; no lenticular / short markers
  remain; first id jild13-pesh-lafz, last id jild13-maakhiz-damima-143.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = "chunks-manifest-v4-jild13.json"

# Concatenation order: chunk files 01 -> 18, in order.
CHUNK_ORDER = ["jild-13-chunk-01.json", "jild-13-chunk-02.json", "jild-13-chunk-03.json", "jild-13-chunk-04.json", "jild-13-chunk-05.json", "jild-13-chunk-06.json", "jild-13-chunk-07.json", "jild-13-chunk-08.json", "jild-13-chunk-09.json", "jild-13-chunk-10.json", "jild-13-chunk-11a.json", "jild-13-chunk-11b.json", "jild-13-chunk-11c.json", "jild-13-chunk-11d.json"]

EXPECTED_ITEMS = 966
EXPECTED_PAGES = 580
EXPECTED_MIN_PAGE = 4
EXPECTED_MAX_PAGE = 688
EXPECTED_VOLUME_IDS = {56}
EXPECTED_FIRST_ID = "jild13-pesh-lafz"
EXPECTED_LAST_ID = "jild13-maakhiz-damima-143"

# v3 ID sequence, verbatim from content/tashreeh/jild-13.json.
V3_IDS = ['jild13-pesh-lafz', 'jild13-masala-1', 'jild13-masala-2-4', 'jild13-masala-5', 'jild13-masala-6', 'jild13-masala-7', 'jild13-masala-8', 'jild13-masala-9', 'jild13-masala-10', 'jild13-masala-11', 'jild13-masala-12', 'jild13-masala-13', 'jild13-masala-14', 'jild13-masala-15', 'jild13-masala-16', 'jild13-masala-17', 'jild13-masala-18', 'jild13-masala-19', 'jild13-masala-20', 'jild13-masala-21', 'jild13-masala-22', 'jild13-masala-23', 'jild13-masala-24', 'jild13-masala-25', 'jild13-masala-26', 'jild13-masala-27', 'jild13-masala-28', 'jild13-masala-29', 'jild13-masala-30', 'jild13-masala-31', 'jild13-masala-32', 'jild13-masala-33-34', 'jild13-masala-35', 'jild13-masala-36', 'jild13-masala-37', 'jild13-masala-38', 'jild13-masala-39', 'jild13-masala-40', 'jild13-masala-41', 'jild13-masala-42', 'jild13-masala-43', 'jild13-masala-44', 'jild13-masala-45', 'jild13-masala-46', 'jild13-masala-47', 'jild13-masala-48', 'jild13-masala-49', 'jild13-masala-50', 'jild13-masala-51', 'jild13-masala-52', 'jild13-masala-53', 'jild13-masala-54', 'jild13-masala-55', 'jild13-masala-56', 'jild13-masala-57', 'jild13-masala-58', 'jild13-masala-59', 'jild13-masala-60', 'jild13-masala-61', 'jild13-masala-62', 'jild13-masala-63', 'jild13-masala-64', 'jild13-masala-65', 'jild13-masala-66', 'jild13-masala-67-73', 'jild13-masala-74', 'jild13-masala-75', 'jild13-masala-76', 'jild13-masala-77', 'jild13-masala-78', 'jild13-masala-79', 'jild13-masala-80', 'jild13-masala-81', 'jild13-masala-82', 'jild13-masala-83', 'jild13-masala-84', 'jild13-masala-85', 'jild13-masala-86', 'jild13-masala-87', 'jild13-masala-88', 'jild13-masala-89', 'jild13-masala-90', 'jild13-masala-91', 'jild13-masala-92', 'jild13-masala-93', 'jild13-masala-94', 'jild13-masala-95', 'jild13-p327', 'jild13-masala-97', 'jild13-masala-98', 'jild13-masala-99', 'jild13-masala-100', 'jild13-masala-101', 'jild13-masala-102', 'jild13-masala-103', 'jild13-masala-104', 'jild13-masala-105', 'jild13-masala-106', 'jild13-masala-107', 'jild13-masala-108', 'jild13-masala-109', 'jild13-masala-110', 'jild13-masala-111', 'jild13-masala-113', 'jild13-masala-114', 'jild13-masala-115', 'jild13-masala-116', 'jild13-masala-117', 'jild13-masala-118', 'jild13-masala-119', 'jild13-masala-120', 'jild13-masala-121', 'jild13-masala-125', 'jild13-masala-126', 'jild13-masala-127', 'jild13-masala-128', 'jild13-masala-129', 'jild13-masala-131', 'jild13-masala-132', 'jild13-masala-133', 'jild13-masala-134', 'jild13-masala-135', 'jild13-masala-136', 'jild13-masala-137', 'jild13-masala-138', 'jild13-masala-139', 'jild13-masala-140', 'jild13-masala-141', 'jild13-masala-142', 'jild13-masala-143', 'jild13-masala-144', 'jild13-masala-145', 'jild13-masala-146', 'jild13-masala-147', 'jild13-masala-148', 'jild13-masala-149', 'jild13-masala-150', 'jild13-masala-151', 'jild13-masala-152', 'jild13-masala-153', 'jild13-masala-154', 'jild13-masala-155', 'jild13-masala-156', 'jild13-masala-157', 'jild13-masala-158', 'jild13-masala-159', 'jild13-masala-160', 'jild13-masala-161', 'jild13-masala-162', 'jild13-masala-163', 'jild13-masala-164', 'jild13-masala-165', 'jild13-masala-166', 'jild13-masala-167', 'jild13-masala-168', 'jild13-masala-169', 'jild13-masala-170', 'jild13-masala-172', 'jild13-masala-173', 'jild13-masala-174', 'jild13-masala-175', 'jild13-masala-176', 'jild13-masala-177', 'jild13-masala-178', 'jild13-masala-179', 'jild13-masala-180', 'jild13-masala-181', 'jild13-masala-182', 'jild13-masala-183', 'jild13-masala-184', 'jild13-masala-185', 'jild13-masala-186', 'jild13-masala-187', 'jild13-masala-188', 'jild13-masala-189', 'jild13-masala-194', 'jild13-masala-196', 'jild13-masala-197', 'jild13-masala-198', 'jild13-masala-199', 'jild13-masala-200', 'jild13-masala-201', 'jild13-masala-202', 'jild13-masala-203', 'jild13-masala-204', 'jild13-masala-205', 'jild13-masala-206', 'jild13-masala-207', 'jild13-masala-210', 'jild13-masala-211', 'jild13-masala-212', 'jild13-masala-213', 'jild13-masala-214', 'jild13-masala-215', 'jild13-masala-216', 'jild13-masala-217', 'jild13-masala-218', 'jild13-masala-219', 'jild13-masala-222', 'jild13-masala-223', 'jild13-masala-224', 'jild13-masala-225', 'jild13-masala-226', 'jild13-masala-227', 'jild13-masala-228', 'jild13-masala-229', 'jild13-masala-231', 'jild13-masala-232', 'jild13-masala-233', 'jild13-masala-234', 'jild13-masala-235', 'jild13-masala-236', 'jild13-masala-237', 'jild13-masala-240', 'jild13-masala-241', 'jild13-masala-242', 'jild13-masala-243', 'jild13-masala-244', 'jild13-masala-248', 'jild13-masala-249', 'jild13-masala-250', 'jild13-masala-251', 'jild13-masala-252', 'jild13-masala-253', 'jild13-masala-254', 'jild13-masala-255-264', 'jild13-masala-265', 'jild13-masala-266', 'jild13-masala-267', 'jild13-masala-268', 'jild13-masala-269', 'jild13-masala-270', 'jild13-masala-271', 'jild13-masala-272', 'jild13-masala-273', 'jild13-masala-274', 'jild13-masala-275', 'jild13-masala-276', 'jild13-masala-277', 'jild13-masala-278', 'jild13-masala-279', 'jild13-masala-280', 'jild13-masala-281', 'jild13-masala-282-284', 'jild13-masala-285', 'jild13-masala-286', 'jild13-masala-287', 'jild13-masala-288', 'jild13-masala-289-290', 'jild13-masala-291-292', 'jild13-masala-293', 'jild13-maakhiz-heading-657', 'jild13-maakhiz-heading-657-alif', 'jild13-maakhiz-01', 'jild13-maakhiz-02', 'jild13-maakhiz-03', 'jild13-maakhiz-04', 'jild13-maakhiz-05', 'jild13-maakhiz-06', 'jild13-maakhiz-07', 'jild13-maakhiz-08', 'jild13-maakhiz-09', 'jild13-maakhiz-10', 'jild13-maakhiz-11', 'jild13-maakhiz-12', 'jild13-maakhiz-13', 'jild13-maakhiz-14', 'jild13-maakhiz-15', 'jild13-maakhiz-16', 'jild13-maakhiz-17', 'jild13-maakhiz-18', 'jild13-maakhiz-19', 'jild13-maakhiz-20', 'jild13-maakhiz-21', 'jild13-maakhiz-22', 'jild13-maakhiz-23', 'jild13-maakhiz-24', 'jild13-maakhiz-25', 'jild13-maakhiz-26', 'jild13-maakhiz-27', 'jild13-maakhiz-28', 'jild13-maakhiz-29', 'jild13-maakhiz-30', 'jild13-maakhiz-31', 'jild13-maakhiz-32', 'jild13-maakhiz-33', 'jild13-maakhiz-34', 'jild13-maakhiz-35', 'jild13-maakhiz-36', 'jild13-maakhiz-37', 'jild13-maakhiz-38', 'jild13-maakhiz-39', 'jild13-maakhiz-heading-659-ba', 'jild13-maakhiz-40', 'jild13-maakhiz-41', 'jild13-maakhiz-42', 'jild13-maakhiz-43', 'jild13-maakhiz-44', 'jild13-maakhiz-45', 'jild13-maakhiz-46', 'jild13-maakhiz-47', 'jild13-maakhiz-48', 'jild13-maakhiz-49', 'jild13-maakhiz-50', 'jild13-maakhiz-heading-659-ta', 'jild13-maakhiz-51', 'jild13-maakhiz-52', 'jild13-maakhiz-53', 'jild13-maakhiz-54', 'jild13-maakhiz-55', 'jild13-maakhiz-56', 'jild13-maakhiz-57', 'jild13-maakhiz-58', 'jild13-maakhiz-59', 'jild13-maakhiz-60', 'jild13-maakhiz-61', 'jild13-maakhiz-62', 'jild13-maakhiz-63', 'jild13-maakhiz-64', 'jild13-maakhiz-65', 'jild13-maakhiz-66', 'jild13-maakhiz-67', 'jild13-maakhiz-68', 'jild13-maakhiz-69', 'jild13-maakhiz-70', 'jild13-maakhiz-71', 'jild13-maakhiz-72', 'jild13-maakhiz-73', 'jild13-maakhiz-74', 'jild13-maakhiz-75', 'jild13-maakhiz-76', 'jild13-maakhiz-77', 'jild13-maakhiz-78', 'jild13-maakhiz-79', 'jild13-maakhiz-80', 'jild13-maakhiz-81', 'jild13-maakhiz-82', 'jild13-maakhiz-83', 'jild13-maakhiz-84', 'jild13-maakhiz-85', 'jild13-maakhiz-86', 'jild13-maakhiz-87', 'jild13-maakhiz-88', 'jild13-maakhiz-89', 'jild13-maakhiz-90', 'jild13-maakhiz-91', 'jild13-maakhiz-92', 'jild13-maakhiz-93', 'jild13-maakhiz-94', 'jild13-maakhiz-95', 'jild13-maakhiz-96', 'jild13-maakhiz-97', 'jild13-maakhiz-98', 'jild13-maakhiz-heading-661-tha', 'jild13-maakhiz-99', 'jild13-maakhiz-100', 'jild13-maakhiz-heading-661-jim', 'jild13-maakhiz-101', 'jild13-maakhiz-102', 'jild13-maakhiz-103', 'jild13-maakhiz-104', 'jild13-maakhiz-105', 'jild13-maakhiz-106', 'jild13-maakhiz-107', 'jild13-maakhiz-108', 'jild13-maakhiz-109', 'jild13-maakhiz-110', 'jild13-maakhiz-111', 'jild13-maakhiz-112', 'jild13-maakhiz-113', 'jild13-maakhiz-114', 'jild13-maakhiz-115', 'jild13-maakhiz-116', 'jild13-maakhiz-117', 'jild13-maakhiz-118', 'jild13-maakhiz-119', 'jild13-maakhiz-120', 'jild13-maakhiz-121', 'jild13-maakhiz-122', 'jild13-maakhiz-123', 'jild13-maakhiz-124', 'jild13-maakhiz-125', 'jild13-maakhiz-heading-662-ha', 'jild13-maakhiz-126', 'jild13-maakhiz-127', 'jild13-maakhiz-128', 'jild13-maakhiz-129', 'jild13-maakhiz-130', 'jild13-maakhiz-131', 'jild13-maakhiz-132', 'jild13-maakhiz-133', 'jild13-maakhiz-134', 'jild13-maakhiz-135', 'jild13-maakhiz-136', 'jild13-maakhiz-137', 'jild13-maakhiz-138', 'jild13-maakhiz-139', 'jild13-maakhiz-140', 'jild13-maakhiz-141', 'jild13-maakhiz-142', 'jild13-maakhiz-143', 'jild13-maakhiz-144', 'jild13-maakhiz-145', 'jild13-maakhiz-146', 'jild13-maakhiz-147', 'jild13-maakhiz-148', 'jild13-maakhiz-149', 'jild13-maakhiz-150', 'jild13-maakhiz-heading-663-kha', 'jild13-maakhiz-151', 'jild13-maakhiz-152', 'jild13-maakhiz-153', 'jild13-maakhiz-154', 'jild13-maakhiz-155', 'jild13-maakhiz-156', 'jild13-maakhiz-157', 'jild13-maakhiz-158', 'jild13-maakhiz-159', 'jild13-maakhiz-heading-664-dal', 'jild13-maakhiz-160', 'jild13-maakhiz-161', 'jild13-maakhiz-162', 'jild13-maakhiz-163', 'jild13-maakhiz-164', 'jild13-maakhiz-heading-664-dhal', 'jild13-maakhiz-165', 'jild13-maakhiz-166', 'jild13-maakhiz-167', 'jild13-maakhiz-heading-664-ra', 'jild13-maakhiz-168', 'jild13-maakhiz-169', 'jild13-maakhiz-170', 'jild13-maakhiz-171', 'jild13-maakhiz-172', 'jild13-maakhiz-173', 'jild13-maakhiz-174', 'jild13-maakhiz-175', 'jild13-maakhiz-176', 'jild13-maakhiz-177', 'jild13-maakhiz-178', 'jild13-maakhiz-179', 'jild13-maakhiz-180', 'jild13-maakhiz-181', 'jild13-maakhiz-182', 'jild13-maakhiz-183', 'jild13-maakhiz-184', 'jild13-maakhiz-185', 'jild13-maakhiz-186', 'jild13-maakhiz-187', 'jild13-maakhiz-188', 'jild13-maakhiz-189', 'jild13-maakhiz-heading-665-za', 'jild13-maakhiz-190', 'jild13-maakhiz-191', 'jild13-maakhiz-192', 'jild13-maakhiz-193', 'jild13-maakhiz-194', 'jild13-maakhiz-195', 'jild13-maakhiz-196', 'jild13-maakhiz-197', 'jild13-maakhiz-198', 'jild13-maakhiz-199', 'jild13-maakhiz-heading-666-sin', 'jild13-maakhiz-200', 'jild13-maakhiz-201', 'jild13-maakhiz-202', 'jild13-maakhiz-203', 'jild13-maakhiz-204', 'jild13-maakhiz-205', 'jild13-maakhiz-206', 'jild13-maakhiz-207', 'jild13-maakhiz-208', 'jild13-maakhiz-209', 'jild13-maakhiz-210', 'jild13-maakhiz-211', 'jild13-maakhiz-212', 'jild13-maakhiz-213', 'jild13-maakhiz-214', 'jild13-maakhiz-215', 'jild13-maakhiz-216', 'jild13-maakhiz-217', 'jild13-maakhiz-heading-667-shin', 'jild13-maakhiz-218', 'jild13-maakhiz-219', 'jild13-maakhiz-220', 'jild13-maakhiz-221', 'jild13-maakhiz-222', 'jild13-maakhiz-223', 'jild13-maakhiz-224', 'jild13-maakhiz-225', 'jild13-maakhiz-226', 'jild13-maakhiz-227', 'jild13-maakhiz-228', 'jild13-maakhiz-229', 'jild13-maakhiz-230', 'jild13-maakhiz-231', 'jild13-maakhiz-232', 'jild13-maakhiz-233', 'jild13-maakhiz-234', 'jild13-maakhiz-235', 'jild13-maakhiz-236', 'jild13-maakhiz-237', 'jild13-maakhiz-238', 'jild13-maakhiz-239', 'jild13-maakhiz-240', 'jild13-maakhiz-241', 'jild13-maakhiz-242', 'jild13-maakhiz-243', 'jild13-maakhiz-244', 'jild13-maakhiz-245', 'jild13-maakhiz-246', 'jild13-maakhiz-247', 'jild13-maakhiz-248', 'jild13-maakhiz-249', 'jild13-maakhiz-250', 'jild13-maakhiz-251', 'jild13-maakhiz-252', 'jild13-maakhiz-253', 'jild13-maakhiz-254', 'jild13-maakhiz-255', 'jild13-maakhiz-256', 'jild13-maakhiz-257', 'jild13-maakhiz-258', 'jild13-maakhiz-259', 'jild13-maakhiz-260', 'jild13-maakhiz-261', 'jild13-maakhiz-262', 'jild13-maakhiz-263', 'jild13-maakhiz-264', 'jild13-maakhiz-265', 'jild13-maakhiz-266', 'jild13-maakhiz-267', 'jild13-maakhiz-268', 'jild13-maakhiz-heading-669-sad', 'jild13-maakhiz-269', 'jild13-maakhiz-270', 'jild13-maakhiz-271', 'jild13-maakhiz-272', 'jild13-maakhiz-273', 'jild13-maakhiz-274', 'jild13-maakhiz-275', 'jild13-maakhiz-heading-669-tah', 'jild13-maakhiz-276', 'jild13-maakhiz-277', 'jild13-maakhiz-278', 'jild13-maakhiz-279', 'jild13-maakhiz-280', 'jild13-maakhiz-281', 'jild13-maakhiz-heading-669-ain', 'jild13-maakhiz-282', 'jild13-maakhiz-283', 'jild13-maakhiz-284', 'jild13-maakhiz-285', 'jild13-maakhiz-286', 'jild13-maakhiz-287', 'jild13-maakhiz-288', 'jild13-maakhiz-289', 'jild13-maakhiz-290', 'jild13-maakhiz-291', 'jild13-maakhiz-292', 'jild13-maakhiz-293', 'jild13-maakhiz-294', 'jild13-maakhiz-heading-670-ghain', 'jild13-maakhiz-295', 'jild13-maakhiz-296', 'jild13-maakhiz-297', 'jild13-maakhiz-298', 'jild13-maakhiz-299', 'jild13-maakhiz-300', 'jild13-maakhiz-301', 'jild13-maakhiz-heading-670-fa', 'jild13-maakhiz-302', 'jild13-maakhiz-303', 'jild13-maakhiz-304', 'jild13-maakhiz-305', 'jild13-maakhiz-306', 'jild13-maakhiz-307', 'jild13-maakhiz-308', 'jild13-maakhiz-309', 'jild13-maakhiz-310', 'jild13-maakhiz-311', 'jild13-maakhiz-312', 'jild13-maakhiz-313', 'jild13-maakhiz-314', 'jild13-maakhiz-315', 'jild13-maakhiz-316', 'jild13-maakhiz-317', 'jild13-maakhiz-318', 'jild13-maakhiz-319', 'jild13-maakhiz-320', 'jild13-maakhiz-321', 'jild13-maakhiz-322', 'jild13-maakhiz-323', 'jild13-maakhiz-324', 'jild13-maakhiz-325', 'jild13-maakhiz-326', 'jild13-maakhiz-327', 'jild13-maakhiz-328', 'jild13-maakhiz-329', 'jild13-maakhiz-330', 'jild13-maakhiz-331', 'jild13-maakhiz-332', 'jild13-maakhiz-333', 'jild13-maakhiz-334', 'jild13-maakhiz-335', 'jild13-maakhiz-336', 'jild13-maakhiz-337', 'jild13-maakhiz-338', 'jild13-maakhiz-339', 'jild13-maakhiz-340', 'jild13-maakhiz-341', 'jild13-maakhiz-342', 'jild13-maakhiz-343', 'jild13-maakhiz-heading-672-qaf', 'jild13-maakhiz-344', 'jild13-maakhiz-345', 'jild13-maakhiz-346', 'jild13-maakhiz-347', 'jild13-maakhiz-348', 'jild13-maakhiz-349', 'jild13-maakhiz-350', 'jild13-maakhiz-351', 'jild13-maakhiz-352', 'jild13-maakhiz-353', 'jild13-maakhiz-heading-673-kaf', 'jild13-maakhiz-354', 'jild13-maakhiz-355', 'jild13-maakhiz-356', 'jild13-maakhiz-357', 'jild13-maakhiz-358', 'jild13-maakhiz-359', 'jild13-maakhiz-360', 'jild13-maakhiz-361', 'jild13-maakhiz-362', 'jild13-maakhiz-363', 'jild13-maakhiz-364', 'jild13-maakhiz-365', 'jild13-maakhiz-366', 'jild13-maakhiz-367', 'jild13-maakhiz-368', 'jild13-maakhiz-369', 'jild13-maakhiz-370', 'jild13-maakhiz-371', 'jild13-maakhiz-372', 'jild13-maakhiz-373', 'jild13-maakhiz-374', 'jild13-maakhiz-375', 'jild13-maakhiz-376', 'jild13-maakhiz-377', 'jild13-maakhiz-378', 'jild13-maakhiz-379', 'jild13-maakhiz-380', 'jild13-maakhiz-381', 'jild13-maakhiz-382', 'jild13-maakhiz-383', 'jild13-maakhiz-384', 'jild13-maakhiz-385', 'jild13-maakhiz-386', 'jild13-maakhiz-387', 'jild13-maakhiz-388', 'jild13-maakhiz-389', 'jild13-maakhiz-390', 'jild13-maakhiz-391', 'jild13-maakhiz-392', 'jild13-maakhiz-393', 'jild13-maakhiz-394', 'jild13-maakhiz-395', 'jild13-maakhiz-396', 'jild13-maakhiz-heading-674-lam', 'jild13-maakhiz-397', 'jild13-maakhiz-398', 'jild13-maakhiz-399', 'jild13-maakhiz-400', 'jild13-maakhiz-401', 'jild13-maakhiz-heading-675-mim', 'jild13-maakhiz-402', 'jild13-maakhiz-403', 'jild13-maakhiz-404', 'jild13-maakhiz-405', 'jild13-maakhiz-406', 'jild13-maakhiz-407', 'jild13-maakhiz-408', 'jild13-maakhiz-409', 'jild13-maakhiz-410', 'jild13-maakhiz-411', 'jild13-maakhiz-412', 'jild13-maakhiz-413', 'jild13-maakhiz-414', 'jild13-maakhiz-415', 'jild13-maakhiz-416', 'jild13-maakhiz-417', 'jild13-maakhiz-418', 'jild13-maakhiz-419', 'jild13-maakhiz-420', 'jild13-maakhiz-421', 'jild13-maakhiz-422', 'jild13-maakhiz-423', 'jild13-maakhiz-424', 'jild13-maakhiz-425', 'jild13-maakhiz-426', 'jild13-maakhiz-427', 'jild13-maakhiz-428', 'jild13-maakhiz-429', 'jild13-maakhiz-430', 'jild13-maakhiz-431', 'jild13-maakhiz-432', 'jild13-maakhiz-433', 'jild13-maakhiz-434', 'jild13-maakhiz-435', 'jild13-maakhiz-436', 'jild13-maakhiz-437', 'jild13-maakhiz-438', 'jild13-maakhiz-439', 'jild13-maakhiz-440', 'jild13-maakhiz-441', 'jild13-maakhiz-442', 'jild13-maakhiz-443', 'jild13-maakhiz-444', 'jild13-maakhiz-445', 'jild13-maakhiz-446', 'jild13-maakhiz-447', 'jild13-maakhiz-448', 'jild13-maakhiz-449', 'jild13-maakhiz-450', 'jild13-maakhiz-451', 'jild13-maakhiz-452', 'jild13-maakhiz-453', 'jild13-maakhiz-454', 'jild13-maakhiz-455', 'jild13-maakhiz-456', 'jild13-maakhiz-457', 'jild13-maakhiz-458', 'jild13-maakhiz-459', 'jild13-maakhiz-460', 'jild13-maakhiz-461', 'jild13-maakhiz-462', 'jild13-maakhiz-463', 'jild13-maakhiz-464', 'jild13-maakhiz-465', 'jild13-maakhiz-466', 'jild13-maakhiz-467', 'jild13-maakhiz-468', 'jild13-maakhiz-469', 'jild13-maakhiz-470', 'jild13-maakhiz-471', 'jild13-maakhiz-472', 'jild13-maakhiz-473', 'jild13-maakhiz-474', 'jild13-maakhiz-475', 'jild13-maakhiz-476', 'jild13-maakhiz-477', 'jild13-maakhiz-478', 'jild13-maakhiz-479', 'jild13-maakhiz-480', 'jild13-maakhiz-481', 'jild13-maakhiz-482', 'jild13-maakhiz-483', 'jild13-maakhiz-484', 'jild13-maakhiz-485', 'jild13-maakhiz-486', 'jild13-maakhiz-487', 'jild13-maakhiz-488', 'jild13-maakhiz-489', 'jild13-maakhiz-490', 'jild13-maakhiz-491', 'jild13-maakhiz-492', 'jild13-maakhiz-493', 'jild13-maakhiz-494', 'jild13-maakhiz-495', 'jild13-maakhiz-496', 'jild13-maakhiz-497', 'jild13-maakhiz-498', 'jild13-maakhiz-499', 'jild13-maakhiz-500', 'jild13-maakhiz-501', 'jild13-maakhiz-502', 'jild13-maakhiz-503', 'jild13-maakhiz-504', 'jild13-maakhiz-heading-679-nun', 'jild13-maakhiz-505', 'jild13-maakhiz-506', 'jild13-maakhiz-507', 'jild13-maakhiz-508', 'jild13-maakhiz-509', 'jild13-maakhiz-510', 'jild13-maakhiz-511', 'jild13-maakhiz-512', 'jild13-maakhiz-513', 'jild13-maakhiz-514', 'jild13-maakhiz-heading-679-waw', 'jild13-maakhiz-515', 'jild13-maakhiz-516', 'jild13-maakhiz-517', 'jild13-maakhiz-518', 'jild13-maakhiz-heading-680-ha2', 'jild13-maakhiz-519', 'jild13-maakhiz-heading-680-ya', 'jild13-maakhiz-520', 'jild13-maakhiz-521', 'jild13-maakhiz-heading-681-damima', 'jild13-maakhiz-heading-681-alif', 'jild13-maakhiz-damima-01', 'jild13-maakhiz-damima-02', 'jild13-maakhiz-damima-03', 'jild13-maakhiz-damima-04', 'jild13-maakhiz-damima-05', 'jild13-maakhiz-damima-06', 'jild13-maakhiz-damima-07', 'jild13-maakhiz-damima-08', 'jild13-maakhiz-damima-09', 'jild13-maakhiz-damima-10', 'jild13-maakhiz-damima-11', 'jild13-maakhiz-damima-12', 'jild13-maakhiz-damima-13', 'jild13-maakhiz-damima-14', 'jild13-maakhiz-damima-15', 'jild13-maakhiz-damima-16', 'jild13-maakhiz-damima-17', 'jild13-maakhiz-damima-18', 'jild13-maakhiz-damima-19', 'jild13-maakhiz-damima-20', 'jild13-maakhiz-heading-682-ta', 'jild13-maakhiz-damima-21', 'jild13-maakhiz-damima-22', 'jild13-maakhiz-damima-23', 'jild13-maakhiz-damima-24', 'jild13-maakhiz-damima-25', 'jild13-maakhiz-damima-26', 'jild13-maakhiz-damima-27', 'jild13-maakhiz-damima-28', 'jild13-maakhiz-damima-29', 'jild13-maakhiz-damima-30', 'jild13-maakhiz-heading-682-tha', 'jild13-maakhiz-damima-31', 'jild13-maakhiz-damima-32', 'jild13-maakhiz-heading-682-jim', 'jild13-maakhiz-damima-33', 'jild13-maakhiz-damima-34', 'jild13-maakhiz-damima-35', 'jild13-maakhiz-heading-683-ha', 'jild13-maakhiz-damima-36', 'jild13-maakhiz-damima-37', 'jild13-maakhiz-damima-38', 'jild13-maakhiz-damima-39', 'jild13-maakhiz-damima-40', 'jild13-maakhiz-heading-683-kha', 'jild13-maakhiz-damima-41', 'jild13-maakhiz-heading-683-dal', 'jild13-maakhiz-damima-42', 'jild13-maakhiz-damima-43', 'jild13-maakhiz-damima-44', 'jild13-maakhiz-damima-45', 'jild13-maakhiz-damima-46', 'jild13-maakhiz-damima-47', 'jild13-maakhiz-damima-48', 'jild13-maakhiz-heading-683-dhal', 'jild13-maakhiz-damima-49', 'jild13-maakhiz-heading-684-ra', 'jild13-maakhiz-damima-50', 'jild13-maakhiz-heading-684-sin', 'jild13-maakhiz-damima-51', 'jild13-maakhiz-damima-52', 'jild13-maakhiz-damima-53', 'jild13-maakhiz-damima-54', 'jild13-maakhiz-heading-684-shin', 'jild13-maakhiz-damima-55', 'jild13-maakhiz-damima-56', 'jild13-maakhiz-damima-57', 'jild13-maakhiz-damima-58', 'jild13-maakhiz-damima-59', 'jild13-maakhiz-damima-60', 'jild13-maakhiz-damima-61', 'jild13-maakhiz-damima-62', 'jild13-maakhiz-heading-684-sad', 'jild13-maakhiz-damima-63', 'jild13-maakhiz-damima-64', 'jild13-maakhiz-damima-65', 'jild13-maakhiz-heading-685-tah', 'jild13-maakhiz-damima-66', 'jild13-maakhiz-heading-685-ghain', 'jild13-maakhiz-damima-67', 'jild13-maakhiz-damima-68', 'jild13-maakhiz-damima-69', 'jild13-maakhiz-damima-70', 'jild13-maakhiz-heading-685-fa', 'jild13-maakhiz-damima-71', 'jild13-maakhiz-damima-72', 'jild13-maakhiz-damima-73', 'jild13-maakhiz-damima-74', 'jild13-maakhiz-damima-75', 'jild13-maakhiz-damima-76', 'jild13-maakhiz-damima-77', 'jild13-maakhiz-damima-78', 'jild13-maakhiz-damima-79', 'jild13-maakhiz-damima-80', 'jild13-maakhiz-damima-81', 'jild13-maakhiz-heading-685-qaf', 'jild13-maakhiz-damima-82', 'jild13-maakhiz-heading-686-kaf', 'jild13-maakhiz-damima-83', 'jild13-maakhiz-damima-84', 'jild13-maakhiz-damima-85', 'jild13-maakhiz-damima-86', 'jild13-maakhiz-damima-87', 'jild13-maakhiz-damima-88', 'jild13-maakhiz-damima-89', 'jild13-maakhiz-damima-90', 'jild13-maakhiz-damima-91', 'jild13-maakhiz-damima-92', 'jild13-maakhiz-damima-93', 'jild13-maakhiz-damima-94', 'jild13-maakhiz-damima-95', 'jild13-maakhiz-damima-96', 'jild13-maakhiz-heading-686-lam', 'jild13-maakhiz-damima-97', 'jild13-maakhiz-heading-686-mim', 'jild13-maakhiz-damima-98', 'jild13-maakhiz-damima-majmua-khani', 'jild13-maakhiz-damima-99', 'jild13-maakhiz-damima-100', 'jild13-maakhiz-damima-101', 'jild13-maakhiz-damima-102', 'jild13-maakhiz-damima-103', 'jild13-maakhiz-damima-104', 'jild13-maakhiz-damima-105', 'jild13-maakhiz-damima-106', 'jild13-maakhiz-damima-107', 'jild13-maakhiz-damima-108', 'jild13-maakhiz-damima-109', 'jild13-maakhiz-damima-110', 'jild13-maakhiz-damima-111', 'jild13-maakhiz-damima-112', 'jild13-maakhiz-damima-113', 'jild13-maakhiz-damima-114', 'jild13-maakhiz-damima-115', 'jild13-maakhiz-damima-116', 'jild13-maakhiz-damima-117', 'jild13-maakhiz-damima-118', 'jild13-maakhiz-damima-119', 'jild13-maakhiz-damima-120', 'jild13-maakhiz-damima-121', 'jild13-maakhiz-damima-122', 'jild13-maakhiz-damima-123', 'jild13-maakhiz-heading-687-nun', 'jild13-maakhiz-damima-124', 'jild13-maakhiz-damima-125', 'jild13-maakhiz-damima-126', 'jild13-maakhiz-damima-127', 'jild13-maakhiz-damima-128', 'jild13-maakhiz-damima-129', 'jild13-maakhiz-damima-130', 'jild13-maakhiz-damima-131', 'jild13-maakhiz-damima-132', 'jild13-maakhiz-damima-133', 'jild13-maakhiz-damima-134', 'jild13-maakhiz-damima-135', 'jild13-maakhiz-damima-136', 'jild13-maakhiz-damima-137', 'jild13-maakhiz-damima-138', 'jild13-maakhiz-heading-688-waw', 'jild13-maakhiz-damima-139', 'jild13-maakhiz-damima-140', 'jild13-maakhiz-damima-141', 'jild13-maakhiz-heading-688-ha2', 'jild13-maakhiz-damima-142', 'jild13-maakhiz-damima-143']

# v3 pages per item id, verbatim from content/tashreeh/jild-13.json.
V3_PAGES = {
"jild13-pesh-lafz": [4, 5, 6],
"jild13-masala-1": [100, 101],
"jild13-masala-2-4": [102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
"jild13-masala-5": [111],
"jild13-masala-6": [111, 112, 113, 114],
"jild13-masala-7": [114, 115],
"jild13-masala-8": [116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135],
"jild13-masala-9": [135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152],
"jild13-masala-10": [155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 191, 192, 193, 194, 195, 196, 197],
"jild13-masala-11": [197, 198, 199, 200, 201],
"jild13-masala-12": [201, 202],
"jild13-masala-13": [202, 203],
"jild13-masala-14": [203, 204, 205],
"jild13-masala-15": [206],
"jild13-masala-16": [206, 207],
"jild13-masala-17": [207, 208],
"jild13-masala-18": [208, 209, 210, 211, 212, 213],
"jild13-masala-19": [213, 214],
"jild13-masala-20": [214, 215, 216, 217],
"jild13-masala-21": [217, 218, 219, 220, 221, 222],
"jild13-masala-22": [222, 223, 224, 225],
"jild13-masala-23": [225, 226, 227, 228, 229, 230],
"jild13-masala-24": [230, 231, 232],
"jild13-masala-25": [232, 233],
"jild13-masala-26": [233, 234],
"jild13-masala-27": [234, 235, 236],
"jild13-masala-28": [236, 237, 238, 239],
"jild13-masala-29": [239, 240],
"jild13-masala-30": [240, 241, 242],
"jild13-masala-31": [242, 243],
"jild13-masala-32": [243, 244],
"jild13-masala-33-34": [244, 245, 246],
"jild13-masala-35": [246, 247, 248, 249, 250, 251, 252, 253, 255, 256],
"jild13-masala-36": [257, 258, 259, 261],
"jild13-masala-37": [261, 262],
"jild13-masala-38": [263, 265],
"jild13-masala-39": [265, 266],
"jild13-masala-40": [267, 268, 269, 270],
"jild13-masala-41": [270, 271, 272, 273, 274, 275, 276, 277, 278, 279],
"jild13-masala-42": [279, 280, 281],
"jild13-masala-43": [281, 282, 283],
"jild13-masala-44": [283, 284, 285, 286],
"jild13-masala-45": [286, 287],
"jild13-masala-46": [287, 288],
"jild13-masala-47": [288, 289],
"jild13-masala-48": [289],
"jild13-masala-49": [289],
"jild13-masala-50": [289, 290],
"jild13-masala-51": [291, 292, 293],
"jild13-masala-52": [293, 294],
"jild13-masala-53": [294],
"jild13-masala-54": [294, 295],
"jild13-masala-55": [295],
"jild13-masala-56": [295, 296],
"jild13-masala-57": [296],
"jild13-masala-58": [296, 297, 298],
"jild13-masala-59": [298, 299],
"jild13-masala-60": [299],
"jild13-masala-61": [299, 300],
"jild13-masala-62": [300, 301],
"jild13-masala-63": [302, 303],
"jild13-masala-64": [303, 304],
"jild13-masala-65": [304, 305],
"jild13-masala-66": [305, 306],
"jild13-masala-67-73": [306, 307],
"jild13-masala-74": [307, 308],
"jild13-masala-75": [308, 309],
"jild13-masala-76": [309, 310],
"jild13-masala-77": [310, 311, 312],
"jild13-masala-78": [312, 313],
"jild13-masala-79": [313],
"jild13-masala-80": [314, 315],
"jild13-masala-81": [315, 316],
"jild13-masala-82": [316, 317],
"jild13-masala-83": [317],
"jild13-masala-84": [317],
"jild13-masala-85": [317, 318],
"jild13-masala-86": [318],
"jild13-masala-87": [318, 319],
"jild13-masala-88": [319],
"jild13-masala-89": [319],
"jild13-masala-90": [320],
"jild13-masala-91": [320, 321],
"jild13-masala-92": [321, 322],
"jild13-masala-93": [322, 323],
"jild13-masala-94": [323, 325],
"jild13-masala-95": [325, 326],
"jild13-p327": [327, 328],
"jild13-masala-97": [328, 329],
"jild13-masala-98": [329, 330],
"jild13-masala-99": [330],
"jild13-masala-100": [330, 331],
"jild13-masala-101": [331],
"jild13-masala-102": [331, 332],
"jild13-masala-103": [332],
"jild13-masala-104": [332, 333],
"jild13-masala-105": [333, 334],
"jild13-masala-106": [335, 336, 337, 338, 339, 340, 341],
"jild13-masala-107": [341, 342, 343],
"jild13-masala-108": [343, 344, 345],
"jild13-masala-109": [345, 346],
"jild13-masala-110": [346, 347],
"jild13-masala-111": [347, 348],
"jild13-masala-113": [349, 350, 351, 352],
"jild13-masala-114": [352, 353, 354, 355],
"jild13-masala-115": [355, 356, 357],
"jild13-masala-116": [357, 358, 359],
"jild13-masala-117": [359, 360],
"jild13-masala-118": [360, 361],
"jild13-masala-119": [361],
"jild13-masala-120": [361, 362, 363, 364, 365, 366],
"jild13-masala-121": [366, 367],
"jild13-masala-125": [367, 368, 369, 370, 371, 372, 373, 374, 375],
"jild13-masala-126": [375, 376],
"jild13-masala-127": [376, 377],
"jild13-masala-128": [376, 377],
"jild13-masala-129": [377, 378],
"jild13-masala-131": [378, 379],
"jild13-masala-132": [379],
"jild13-masala-133": [379, 381],
"jild13-masala-134": [381, 382],
"jild13-masala-135": [383, 384, 385],
"jild13-masala-136": [385, 386, 387],
"jild13-masala-137": [387, 388],
"jild13-masala-138": [388, 389],
"jild13-masala-139": [389, 390, 391],
"jild13-masala-140": [391, 392, 393, 394],
"jild13-masala-141": [394, 395, 396],
"jild13-masala-142": [396, 397],
"jild13-masala-143": [397],
"jild13-masala-144": [397, 398, 399],
"jild13-masala-145": [399, 400],
"jild13-masala-146": [401, 402, 403, 404, 405, 406],
"jild13-masala-147": [406, 407, 408],
"jild13-masala-148": [408, 409],
"jild13-masala-149": [409, 410],
"jild13-masala-150": [410, 411],
"jild13-masala-151": [413],
"jild13-masala-152": [413, 414],
"jild13-masala-153": [415],
"jild13-masala-154": [415, 416, 417, 418, 419, 420, 421],
"jild13-masala-155": [421],
"jild13-masala-156": [422, 423, 424, 425, 426, 427],
"jild13-masala-157": [427, 428, 429],
"jild13-masala-158": [430, 431, 432],
"jild13-masala-159": [432],
"jild13-masala-160": [432, 433],
"jild13-masala-161": [433, 434, 435],
"jild13-masala-162": [435],
"jild13-masala-163": [436, 437],
"jild13-masala-164": [437],
"jild13-masala-165": [438, 439, 440, 441, 442, 443],
"jild13-masala-166": [443, 444],
"jild13-masala-167": [444, 445],
"jild13-masala-168": [445, 446, 447, 448, 449, 450, 451],
"jild13-masala-169": [451, 452, 453],
"jild13-masala-170": [453, 454],
"jild13-masala-172": [454, 455, 456, 457],
"jild13-masala-173": [457, 458],
"jild13-masala-174": [458, 459],
"jild13-masala-175": [459, 460],
"jild13-masala-176": [460, 461],
"jild13-masala-177": [461],
"jild13-masala-178": [461, 462, 463],
"jild13-masala-179": [463, 464],
"jild13-masala-180": [465, 466, 467, 468, 469, 470, 471, 472, 473],
"jild13-masala-181": [474, 475],
"jild13-masala-182": [475],
"jild13-masala-183": [476],
"jild13-masala-184": [476, 477, 478],
"jild13-masala-185": [478],
"jild13-masala-186": [478, 479],
"jild13-masala-187": [480],
"jild13-masala-188": [480, 481],
"jild13-masala-189": [482, 483],
"jild13-masala-194": [483, 484],
"jild13-masala-196": [484, 485],
"jild13-masala-197": [485, 486, 487, 488, 489, 490, 491, 492],
"jild13-masala-198": [492, 493],
"jild13-masala-199": [495, 496, 497],
"jild13-masala-200": [497, 498],
"jild13-masala-201": [498, 499],
"jild13-masala-202": [499, 500],
"jild13-masala-203": [500, 501, 502],
"jild13-masala-204": [502, 503],
"jild13-masala-205": [503, 504],
"jild13-masala-206": [504],
"jild13-masala-207": [504, 505, 506],
"jild13-masala-210": [506, 507],
"jild13-masala-211": [507],
"jild13-masala-212": [507, 508],
"jild13-masala-213": [508, 509],
"jild13-masala-214": [511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574],
"jild13-masala-215": [574],
"jild13-masala-216": [574, 575],
"jild13-masala-217": [575, 576, 577],
"jild13-masala-218": [577, 578],
"jild13-masala-219": [578, 579],
"jild13-masala-222": [579],
"jild13-masala-223": [579, 580],
"jild13-masala-224": [581],
"jild13-masala-225": [582],
"jild13-masala-226": [582, 583],
"jild13-masala-227": [583],
"jild13-masala-228": [583, 584],
"jild13-masala-229": [584, 585],
"jild13-masala-231": [585],
"jild13-masala-232": [585, 586],
"jild13-masala-233": [585, 586],
"jild13-masala-234": [586],
"jild13-masala-235": [586, 587],
"jild13-masala-236": [587, 588, 589],
"jild13-masala-237": [589, 590],
"jild13-masala-240": [590],
"jild13-masala-241": [590, 591, 592, 593],
"jild13-masala-242": [593, 594],
"jild13-masala-243": [594],
"jild13-masala-244": [594, 595, 596],
"jild13-masala-248": [597],
"jild13-masala-249": [597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608],
"jild13-masala-250": [609, 610, 611],
"jild13-masala-251": [611],
"jild13-masala-252": [612, 613],
"jild13-masala-253": [613, 614],
"jild13-masala-254": [614, 615],
"jild13-masala-255-264": [615, 616, 617, 618],
"jild13-masala-265": [618, 619],
"jild13-masala-266": [619, 620],
"jild13-masala-267": [620, 621, 622],
"jild13-masala-268": [623],
"jild13-masala-269": [623, 624],
"jild13-masala-270": [624],
"jild13-masala-271": [624, 625],
"jild13-masala-272": [625, 626],
"jild13-masala-273": [626],
"jild13-masala-274": [626, 627],
"jild13-masala-275": [628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643],
"jild13-masala-276": [643, 644],
"jild13-masala-277": [644, 645],
"jild13-masala-278": [645],
"jild13-masala-279": [645],
"jild13-masala-280": [645, 646],
"jild13-masala-281": [646, 647],
"jild13-masala-282-284": [647, 648],
"jild13-masala-285": [648, 649],
"jild13-masala-286": [649, 650],
"jild13-masala-287": [650],
"jild13-masala-288": [650, 651],
"jild13-masala-289-290": [652, 653],
"jild13-masala-291-292": [654, 655],
"jild13-masala-293": [655],
"jild13-maakhiz-heading-657": [657],
"jild13-maakhiz-heading-657-alif": [657],
"jild13-maakhiz-01": [657],
"jild13-maakhiz-02": [657],
"jild13-maakhiz-03": [657],
"jild13-maakhiz-04": [657],
"jild13-maakhiz-05": [657],
"jild13-maakhiz-06": [657],
"jild13-maakhiz-07": [657],
"jild13-maakhiz-08": [657],
"jild13-maakhiz-09": [657],
"jild13-maakhiz-10": [657],
"jild13-maakhiz-11": [657],
"jild13-maakhiz-12": [657],
"jild13-maakhiz-13": [657],
"jild13-maakhiz-14": [657],
"jild13-maakhiz-15": [657],
"jild13-maakhiz-16": [658],
"jild13-maakhiz-17": [658],
"jild13-maakhiz-18": [658],
"jild13-maakhiz-19": [658],
"jild13-maakhiz-20": [658],
"jild13-maakhiz-21": [658],
"jild13-maakhiz-22": [658],
"jild13-maakhiz-23": [658],
"jild13-maakhiz-24": [658],
"jild13-maakhiz-25": [658],
"jild13-maakhiz-26": [658],
"jild13-maakhiz-27": [658],
"jild13-maakhiz-28": [658],
"jild13-maakhiz-29": [658],
"jild13-maakhiz-30": [658],
"jild13-maakhiz-31": [658],
"jild13-maakhiz-32": [658],
"jild13-maakhiz-33": [658],
"jild13-maakhiz-34": [658],
"jild13-maakhiz-35": [658],
"jild13-maakhiz-36": [658],
"jild13-maakhiz-37": [658],
"jild13-maakhiz-38": [658],
"jild13-maakhiz-39": [658, 659],
"jild13-maakhiz-heading-659-ba": [659],
"jild13-maakhiz-40": [659],
"jild13-maakhiz-41": [659],
"jild13-maakhiz-42": [659],
"jild13-maakhiz-43": [659],
"jild13-maakhiz-44": [659],
"jild13-maakhiz-45": [659],
"jild13-maakhiz-46": [659],
"jild13-maakhiz-47": [659],
"jild13-maakhiz-48": [659],
"jild13-maakhiz-49": [659],
"jild13-maakhiz-50": [659],
"jild13-maakhiz-heading-659-ta": [659],
"jild13-maakhiz-51": [659],
"jild13-maakhiz-52": [659],
"jild13-maakhiz-53": [659],
"jild13-maakhiz-54": [659],
"jild13-maakhiz-55": [659],
"jild13-maakhiz-56": [659],
"jild13-maakhiz-57": [659],
"jild13-maakhiz-58": [659],
"jild13-maakhiz-59": [659],
"jild13-maakhiz-60": [659],
"jild13-maakhiz-61": [660],
"jild13-maakhiz-62": [660],
"jild13-maakhiz-63": [660],
"jild13-maakhiz-64": [660],
"jild13-maakhiz-65": [660],
"jild13-maakhiz-66": [660],
"jild13-maakhiz-67": [660],
"jild13-maakhiz-68": [660],
"jild13-maakhiz-69": [660],
"jild13-maakhiz-70": [660],
"jild13-maakhiz-71": [660],
"jild13-maakhiz-72": [660],
"jild13-maakhiz-73": [660],
"jild13-maakhiz-74": [660],
"jild13-maakhiz-75": [660],
"jild13-maakhiz-76": [660],
"jild13-maakhiz-77": [660],
"jild13-maakhiz-78": [660],
"jild13-maakhiz-79": [660],
"jild13-maakhiz-80": [660],
"jild13-maakhiz-81": [660],
"jild13-maakhiz-82": [660],
"jild13-maakhiz-83": [660],
"jild13-maakhiz-84": [660],
"jild13-maakhiz-85": [660],
"jild13-maakhiz-86": [661],
"jild13-maakhiz-87": [661],
"jild13-maakhiz-88": [661],
"jild13-maakhiz-89": [661],
"jild13-maakhiz-90": [661],
"jild13-maakhiz-91": [661],
"jild13-maakhiz-92": [661],
"jild13-maakhiz-93": [661],
"jild13-maakhiz-94": [661],
"jild13-maakhiz-95": [661],
"jild13-maakhiz-96": [661],
"jild13-maakhiz-97": [661],
"jild13-maakhiz-98": [661],
"jild13-maakhiz-heading-661-tha": [661],
"jild13-maakhiz-99": [661],
"jild13-maakhiz-100": [661],
"jild13-maakhiz-heading-661-jim": [661],
"jild13-maakhiz-101": [661],
"jild13-maakhiz-102": [661],
"jild13-maakhiz-103": [661],
"jild13-maakhiz-104": [661],
"jild13-maakhiz-105": [661],
"jild13-maakhiz-106": [661],
"jild13-maakhiz-107": [662],
"jild13-maakhiz-108": [662],
"jild13-maakhiz-109": [662],
"jild13-maakhiz-110": [662],
"jild13-maakhiz-111": [662],
"jild13-maakhiz-112": [662],
"jild13-maakhiz-113": [662],
"jild13-maakhiz-114": [662],
"jild13-maakhiz-115": [662],
"jild13-maakhiz-116": [662],
"jild13-maakhiz-117": [662],
"jild13-maakhiz-118": [662],
"jild13-maakhiz-119": [662],
"jild13-maakhiz-120": [662],
"jild13-maakhiz-121": [662],
"jild13-maakhiz-122": [662],
"jild13-maakhiz-123": [662],
"jild13-maakhiz-124": [662],
"jild13-maakhiz-125": [662],
"jild13-maakhiz-heading-662-ha": [662],
"jild13-maakhiz-126": [662],
"jild13-maakhiz-127": [662],
"jild13-maakhiz-128": [662],
"jild13-maakhiz-129": [662],
"jild13-maakhiz-130": [663],
"jild13-maakhiz-131": [663],
"jild13-maakhiz-132": [663],
"jild13-maakhiz-133": [663],
"jild13-maakhiz-134": [663],
"jild13-maakhiz-135": [663],
"jild13-maakhiz-136": [663],
"jild13-maakhiz-137": [663],
"jild13-maakhiz-138": [663],
"jild13-maakhiz-139": [663],
"jild13-maakhiz-140": [663],
"jild13-maakhiz-141": [663],
"jild13-maakhiz-142": [663],
"jild13-maakhiz-143": [663],
"jild13-maakhiz-144": [663],
"jild13-maakhiz-145": [663],
"jild13-maakhiz-146": [663],
"jild13-maakhiz-147": [663],
"jild13-maakhiz-148": [663],
"jild13-maakhiz-149": [663],
"jild13-maakhiz-150": [663],
"jild13-maakhiz-heading-663-kha": [663],
"jild13-maakhiz-151": [663],
"jild13-maakhiz-152": [663],
"jild13-maakhiz-153": [664],
"jild13-maakhiz-154": [664],
"jild13-maakhiz-155": [664],
"jild13-maakhiz-156": [664],
"jild13-maakhiz-157": [664],
"jild13-maakhiz-158": [664],
"jild13-maakhiz-159": [664],
"jild13-maakhiz-heading-664-dal": [664],
"jild13-maakhiz-160": [664],
"jild13-maakhiz-161": [664],
"jild13-maakhiz-162": [664],
"jild13-maakhiz-163": [664],
"jild13-maakhiz-164": [664],
"jild13-maakhiz-heading-664-dhal": [664],
"jild13-maakhiz-165": [664],
"jild13-maakhiz-166": [664],
"jild13-maakhiz-167": [664],
"jild13-maakhiz-heading-664-ra": [664],
"jild13-maakhiz-168": [664],
"jild13-maakhiz-169": [664],
"jild13-maakhiz-170": [664],
"jild13-maakhiz-171": [664],
"jild13-maakhiz-172": [665],
"jild13-maakhiz-173": [665],
"jild13-maakhiz-174": [665],
"jild13-maakhiz-175": [665],
"jild13-maakhiz-176": [665],
"jild13-maakhiz-177": [665],
"jild13-maakhiz-178": [665],
"jild13-maakhiz-179": [665],
"jild13-maakhiz-180": [665],
"jild13-maakhiz-181": [665],
"jild13-maakhiz-182": [665],
"jild13-maakhiz-183": [665],
"jild13-maakhiz-184": [665],
"jild13-maakhiz-185": [665],
"jild13-maakhiz-186": [665],
"jild13-maakhiz-187": [665],
"jild13-maakhiz-188": [665],
"jild13-maakhiz-189": [665],
"jild13-maakhiz-heading-665-za": [665],
"jild13-maakhiz-190": [665],
"jild13-maakhiz-191": [665],
"jild13-maakhiz-192": [665],
"jild13-maakhiz-193": [665],
"jild13-maakhiz-194": [665],
"jild13-maakhiz-195": [666],
"jild13-maakhiz-196": [666],
"jild13-maakhiz-197": [666],
"jild13-maakhiz-198": [666],
"jild13-maakhiz-199": [666],
"jild13-maakhiz-heading-666-sin": [666],
"jild13-maakhiz-200": [666],
"jild13-maakhiz-201": [666],
"jild13-maakhiz-202": [666],
"jild13-maakhiz-203": [666],
"jild13-maakhiz-204": [666],
"jild13-maakhiz-205": [666],
"jild13-maakhiz-206": [666],
"jild13-maakhiz-207": [666],
"jild13-maakhiz-208": [666],
"jild13-maakhiz-209": [666],
"jild13-maakhiz-210": [666],
"jild13-maakhiz-211": [666],
"jild13-maakhiz-212": [666],
"jild13-maakhiz-213": [666],
"jild13-maakhiz-214": [666],
"jild13-maakhiz-215": [666],
"jild13-maakhiz-216": [666],
"jild13-maakhiz-217": [666],
"jild13-maakhiz-heading-667-shin": [667],
"jild13-maakhiz-218": [667],
"jild13-maakhiz-219": [667],
"jild13-maakhiz-220": [667],
"jild13-maakhiz-221": [667],
"jild13-maakhiz-222": [667],
"jild13-maakhiz-223": [667],
"jild13-maakhiz-224": [667],
"jild13-maakhiz-225": [667],
"jild13-maakhiz-226": [667],
"jild13-maakhiz-227": [667],
"jild13-maakhiz-228": [667],
"jild13-maakhiz-229": [667],
"jild13-maakhiz-230": [667],
"jild13-maakhiz-231": [667],
"jild13-maakhiz-232": [667],
"jild13-maakhiz-233": [667],
"jild13-maakhiz-234": [667],
"jild13-maakhiz-235": [667],
"jild13-maakhiz-236": [667],
"jild13-maakhiz-237": [667],
"jild13-maakhiz-238": [667],
"jild13-maakhiz-239": [667],
"jild13-maakhiz-240": [667, 668],
"jild13-maakhiz-241": [668],
"jild13-maakhiz-242": [668],
"jild13-maakhiz-243": [668],
"jild13-maakhiz-244": [668],
"jild13-maakhiz-245": [668],
"jild13-maakhiz-246": [668],
"jild13-maakhiz-247": [668],
"jild13-maakhiz-248": [668],
"jild13-maakhiz-249": [668],
"jild13-maakhiz-250": [668],
"jild13-maakhiz-251": [668],
"jild13-maakhiz-252": [668],
"jild13-maakhiz-253": [668],
"jild13-maakhiz-254": [668],
"jild13-maakhiz-255": [668],
"jild13-maakhiz-256": [668],
"jild13-maakhiz-257": [668],
"jild13-maakhiz-258": [668],
"jild13-maakhiz-259": [668],
"jild13-maakhiz-260": [668],
"jild13-maakhiz-261": [668],
"jild13-maakhiz-262": [668],
"jild13-maakhiz-263": [668],
"jild13-maakhiz-264": [668],
"jild13-maakhiz-265": [668],
"jild13-maakhiz-266": [669],
"jild13-maakhiz-267": [669],
"jild13-maakhiz-268": [669],
"jild13-maakhiz-heading-669-sad": [669],
"jild13-maakhiz-269": [669],
"jild13-maakhiz-270": [669],
"jild13-maakhiz-271": [669],
"jild13-maakhiz-272": [669],
"jild13-maakhiz-273": [669],
"jild13-maakhiz-274": [669],
"jild13-maakhiz-275": [669],
"jild13-maakhiz-heading-669-tah": [669],
"jild13-maakhiz-276": [669],
"jild13-maakhiz-277": [669],
"jild13-maakhiz-278": [669],
"jild13-maakhiz-279": [669],
"jild13-maakhiz-280": [669],
"jild13-maakhiz-281": [669],
"jild13-maakhiz-heading-669-ain": [669],
"jild13-maakhiz-282": [669],
"jild13-maakhiz-283": [669],
"jild13-maakhiz-284": [669],
"jild13-maakhiz-285": [670],
"jild13-maakhiz-286": [670],
"jild13-maakhiz-287": [670],
"jild13-maakhiz-288": [670],
"jild13-maakhiz-289": [670],
"jild13-maakhiz-290": [670],
"jild13-maakhiz-291": [670],
"jild13-maakhiz-292": [670],
"jild13-maakhiz-293": [670],
"jild13-maakhiz-294": [670],
"jild13-maakhiz-heading-670-ghain": [670],
"jild13-maakhiz-295": [670],
"jild13-maakhiz-296": [670],
"jild13-maakhiz-297": [670],
"jild13-maakhiz-298": [670],
"jild13-maakhiz-299": [670],
"jild13-maakhiz-300": [670],
"jild13-maakhiz-301": [670],
"jild13-maakhiz-heading-670-fa": [670],
"jild13-maakhiz-302": [670],
"jild13-maakhiz-303": [670],
"jild13-maakhiz-304": [670],
"jild13-maakhiz-305": [670],
"jild13-maakhiz-306": [671],
"jild13-maakhiz-307": [671],
"jild13-maakhiz-308": [671],
"jild13-maakhiz-309": [671],
"jild13-maakhiz-310": [671],
"jild13-maakhiz-311": [671],
"jild13-maakhiz-312": [671],
"jild13-maakhiz-313": [671],
"jild13-maakhiz-314": [671],
"jild13-maakhiz-315": [671],
"jild13-maakhiz-316": [671],
"jild13-maakhiz-317": [671],
"jild13-maakhiz-318": [671],
"jild13-maakhiz-319": [671],
"jild13-maakhiz-320": [671],
"jild13-maakhiz-321": [671],
"jild13-maakhiz-322": [671],
"jild13-maakhiz-323": [671],
"jild13-maakhiz-324": [671],
"jild13-maakhiz-325": [671],
"jild13-maakhiz-326": [671],
"jild13-maakhiz-327": [671],
"jild13-maakhiz-328": [671],
"jild13-maakhiz-329": [671],
"jild13-maakhiz-330": [671],
"jild13-maakhiz-331": [672],
"jild13-maakhiz-332": [672],
"jild13-maakhiz-333": [672],
"jild13-maakhiz-334": [672],
"jild13-maakhiz-335": [672],
"jild13-maakhiz-336": [672],
"jild13-maakhiz-337": [672],
"jild13-maakhiz-338": [672],
"jild13-maakhiz-339": [672],
"jild13-maakhiz-340": [672],
"jild13-maakhiz-341": [672],
"jild13-maakhiz-342": [672],
"jild13-maakhiz-343": [672],
"jild13-maakhiz-heading-672-qaf": [672],
"jild13-maakhiz-344": [672],
"jild13-maakhiz-345": [672],
"jild13-maakhiz-346": [672],
"jild13-maakhiz-347": [672],
"jild13-maakhiz-348": [672],
"jild13-maakhiz-349": [672],
"jild13-maakhiz-350": [672],
"jild13-maakhiz-351": [672],
"jild13-maakhiz-352": [672],
"jild13-maakhiz-353": [672],
"jild13-maakhiz-heading-673-kaf": [673],
"jild13-maakhiz-354": [673],
"jild13-maakhiz-355": [673],
"jild13-maakhiz-356": [673],
"jild13-maakhiz-357": [673],
"jild13-maakhiz-358": [673],
"jild13-maakhiz-359": [673],
"jild13-maakhiz-360": [673],
"jild13-maakhiz-361": [673],
"jild13-maakhiz-362": [673],
"jild13-maakhiz-363": [673],
"jild13-maakhiz-364": [673],
"jild13-maakhiz-365": [673],
"jild13-maakhiz-366": [673],
"jild13-maakhiz-367": [673],
"jild13-maakhiz-368": [673],
"jild13-maakhiz-369": [673],
"jild13-maakhiz-370": [673],
"jild13-maakhiz-371": [673],
"jild13-maakhiz-372": [673],
"jild13-maakhiz-373": [673],
"jild13-maakhiz-374": [673],
"jild13-maakhiz-375": [673],
"jild13-maakhiz-376": [673],
"jild13-maakhiz-377": [674],
"jild13-maakhiz-378": [674],
"jild13-maakhiz-379": [674],
"jild13-maakhiz-380": [674],
"jild13-maakhiz-381": [674],
"jild13-maakhiz-382": [674],
"jild13-maakhiz-383": [674],
"jild13-maakhiz-384": [674],
"jild13-maakhiz-385": [674],
"jild13-maakhiz-386": [674],
"jild13-maakhiz-387": [674],
"jild13-maakhiz-388": [674],
"jild13-maakhiz-389": [674],
"jild13-maakhiz-390": [674],
"jild13-maakhiz-391": [674],
"jild13-maakhiz-392": [674],
"jild13-maakhiz-393": [674],
"jild13-maakhiz-394": [674],
"jild13-maakhiz-395": [674],
"jild13-maakhiz-396": [674],
"jild13-maakhiz-heading-674-lam": [674],
"jild13-maakhiz-397": [674],
"jild13-maakhiz-398": [674],
"jild13-maakhiz-399": [675],
"jild13-maakhiz-400": [675],
"jild13-maakhiz-401": [675],
"jild13-maakhiz-heading-675-mim": [675],
"jild13-maakhiz-402": [675],
"jild13-maakhiz-403": [675],
"jild13-maakhiz-404": [675],
"jild13-maakhiz-405": [675],
"jild13-maakhiz-406": [675],
"jild13-maakhiz-407": [675],
"jild13-maakhiz-408": [675],
"jild13-maakhiz-409": [675],
"jild13-maakhiz-410": [675],
"jild13-maakhiz-411": [675],
"jild13-maakhiz-412": [675],
"jild13-maakhiz-413": [675],
"jild13-maakhiz-414": [675],
"jild13-maakhiz-415": [675],
"jild13-maakhiz-416": [675],
"jild13-maakhiz-417": [675],
"jild13-maakhiz-418": [675],
"jild13-maakhiz-419": [675],
"jild13-maakhiz-420": [675],
"jild13-maakhiz-421": [675],
"jild13-maakhiz-422": [676],
"jild13-maakhiz-423": [676],
"jild13-maakhiz-424": [676],
"jild13-maakhiz-425": [676],
"jild13-maakhiz-426": [676],
"jild13-maakhiz-427": [676],
"jild13-maakhiz-428": [676],
"jild13-maakhiz-429": [676],
"jild13-maakhiz-430": [676],
"jild13-maakhiz-431": [676],
"jild13-maakhiz-432": [676],
"jild13-maakhiz-433": [676],
"jild13-maakhiz-434": [676],
"jild13-maakhiz-435": [676],
"jild13-maakhiz-436": [676],
"jild13-maakhiz-437": [676],
"jild13-maakhiz-438": [676],
"jild13-maakhiz-439": [676],
"jild13-maakhiz-440": [676],
"jild13-maakhiz-441": [676],
"jild13-maakhiz-442": [676],
"jild13-maakhiz-443": [676],
"jild13-maakhiz-444": [676],
"jild13-maakhiz-445": [676],
"jild13-maakhiz-446": [676],
"jild13-maakhiz-447": [677],
"jild13-maakhiz-448": [677],
"jild13-maakhiz-449": [677],
"jild13-maakhiz-450": [677],
"jild13-maakhiz-451": [677],
"jild13-maakhiz-452": [677],
"jild13-maakhiz-453": [677],
"jild13-maakhiz-454": [677],
"jild13-maakhiz-455": [677],
"jild13-maakhiz-456": [677],
"jild13-maakhiz-457": [677],
"jild13-maakhiz-458": [677],
"jild13-maakhiz-459": [677],
"jild13-maakhiz-460": [677],
"jild13-maakhiz-461": [677],
"jild13-maakhiz-462": [677],
"jild13-maakhiz-463": [677],
"jild13-maakhiz-464": [677],
"jild13-maakhiz-465": [677],
"jild13-maakhiz-466": [677],
"jild13-maakhiz-467": [677],
"jild13-maakhiz-468": [677],
"jild13-maakhiz-469": [677],
"jild13-maakhiz-470": [677],
"jild13-maakhiz-471": [677],
"jild13-maakhiz-472": [678],
"jild13-maakhiz-473": [678],
"jild13-maakhiz-474": [678],
"jild13-maakhiz-475": [678],
"jild13-maakhiz-476": [678],
"jild13-maakhiz-477": [678],
"jild13-maakhiz-478": [678],
"jild13-maakhiz-479": [678],
"jild13-maakhiz-480": [678],
"jild13-maakhiz-481": [678],
"jild13-maakhiz-482": [678],
"jild13-maakhiz-483": [678],
"jild13-maakhiz-484": [678],
"jild13-maakhiz-485": [678],
"jild13-maakhiz-486": [678],
"jild13-maakhiz-487": [678],
"jild13-maakhiz-488": [678],
"jild13-maakhiz-489": [678],
"jild13-maakhiz-490": [678],
"jild13-maakhiz-491": [678],
"jild13-maakhiz-492": [678],
"jild13-maakhiz-493": [678],
"jild13-maakhiz-494": [678],
"jild13-maakhiz-495": [678],
"jild13-maakhiz-496": [678],
"jild13-maakhiz-497": [679],
"jild13-maakhiz-498": [679],
"jild13-maakhiz-499": [679],
"jild13-maakhiz-500": [679],
"jild13-maakhiz-501": [679],
"jild13-maakhiz-502": [679],
"jild13-maakhiz-503": [679],
"jild13-maakhiz-504": [679],
"jild13-maakhiz-heading-679-nun": [679],
"jild13-maakhiz-505": [679],
"jild13-maakhiz-506": [679],
"jild13-maakhiz-507": [679],
"jild13-maakhiz-508": [679],
"jild13-maakhiz-509": [679],
"jild13-maakhiz-510": [679],
"jild13-maakhiz-511": [679],
"jild13-maakhiz-512": [679],
"jild13-maakhiz-513": [679],
"jild13-maakhiz-514": [679],
"jild13-maakhiz-heading-679-waw": [679],
"jild13-maakhiz-515": [679],
"jild13-maakhiz-516": [679],
"jild13-maakhiz-517": [679],
"jild13-maakhiz-518": [680],
"jild13-maakhiz-heading-680-ha2": [680],
"jild13-maakhiz-519": [680],
"jild13-maakhiz-heading-680-ya": [680],
"jild13-maakhiz-520": [680],
"jild13-maakhiz-521": [680],
"jild13-maakhiz-heading-681-damima": [681],
"jild13-maakhiz-heading-681-alif": [681],
"jild13-maakhiz-damima-01": [681],
"jild13-maakhiz-damima-02": [681],
"jild13-maakhiz-damima-03": [681],
"jild13-maakhiz-damima-04": [681],
"jild13-maakhiz-damima-05": [681],
"jild13-maakhiz-damima-06": [681],
"jild13-maakhiz-damima-07": [681],
"jild13-maakhiz-damima-08": [681],
"jild13-maakhiz-damima-09": [681],
"jild13-maakhiz-damima-10": [681],
"jild13-maakhiz-damima-11": [681],
"jild13-maakhiz-damima-12": [681],
"jild13-maakhiz-damima-13": [681],
"jild13-maakhiz-damima-14": [682],
"jild13-maakhiz-damima-15": [682],
"jild13-maakhiz-damima-16": [682],
"jild13-maakhiz-damima-17": [682],
"jild13-maakhiz-damima-18": [682],
"jild13-maakhiz-damima-19": [682],
"jild13-maakhiz-damima-20": [682],
"jild13-maakhiz-heading-682-ta": [682],
"jild13-maakhiz-damima-21": [682],
"jild13-maakhiz-damima-22": [682],
"jild13-maakhiz-damima-23": [682],
"jild13-maakhiz-damima-24": [682],
"jild13-maakhiz-damima-25": [682],
"jild13-maakhiz-damima-26": [682],
"jild13-maakhiz-damima-27": [682],
"jild13-maakhiz-damima-28": [682],
"jild13-maakhiz-damima-29": [682],
"jild13-maakhiz-damima-30": [682],
"jild13-maakhiz-heading-682-tha": [682],
"jild13-maakhiz-damima-31": [682],
"jild13-maakhiz-damima-32": [682],
"jild13-maakhiz-heading-682-jim": [682],
"jild13-maakhiz-damima-33": [682, 683],
"jild13-maakhiz-damima-34": [683],
"jild13-maakhiz-damima-35": [683],
"jild13-maakhiz-heading-683-ha": [683],
"jild13-maakhiz-damima-36": [683],
"jild13-maakhiz-damima-37": [683],
"jild13-maakhiz-damima-38": [683],
"jild13-maakhiz-damima-39": [683],
"jild13-maakhiz-damima-40": [683],
"jild13-maakhiz-heading-683-kha": [683],
"jild13-maakhiz-damima-41": [683],
"jild13-maakhiz-heading-683-dal": [683],
"jild13-maakhiz-damima-42": [683],
"jild13-maakhiz-damima-43": [683],
"jild13-maakhiz-damima-44": [683],
"jild13-maakhiz-damima-45": [683],
"jild13-maakhiz-damima-46": [683],
"jild13-maakhiz-damima-47": [683],
"jild13-maakhiz-damima-48": [683],
"jild13-maakhiz-heading-683-dhal": [683],
"jild13-maakhiz-damima-49": [683],
"jild13-maakhiz-heading-684-ra": [684],
"jild13-maakhiz-damima-50": [684],
"jild13-maakhiz-heading-684-sin": [684],
"jild13-maakhiz-damima-51": [684],
"jild13-maakhiz-damima-52": [684],
"jild13-maakhiz-damima-53": [684],
"jild13-maakhiz-damima-54": [684],
"jild13-maakhiz-heading-684-shin": [684],
"jild13-maakhiz-damima-55": [684],
"jild13-maakhiz-damima-56": [684],
"jild13-maakhiz-damima-57": [684],
"jild13-maakhiz-damima-58": [684],
"jild13-maakhiz-damima-59": [684],
"jild13-maakhiz-damima-60": [684],
"jild13-maakhiz-damima-61": [684],
"jild13-maakhiz-damima-62": [684],
"jild13-maakhiz-heading-684-sad": [684],
"jild13-maakhiz-damima-63": [684],
"jild13-maakhiz-damima-64": [684],
"jild13-maakhiz-damima-65": [684, 685],
"jild13-maakhiz-heading-685-tah": [685],
"jild13-maakhiz-damima-66": [685],
"jild13-maakhiz-heading-685-ghain": [685],
"jild13-maakhiz-damima-67": [685],
"jild13-maakhiz-damima-68": [685],
"jild13-maakhiz-damima-69": [685],
"jild13-maakhiz-damima-70": [685],
"jild13-maakhiz-heading-685-fa": [685],
"jild13-maakhiz-damima-71": [685],
"jild13-maakhiz-damima-72": [685],
"jild13-maakhiz-damima-73": [685],
"jild13-maakhiz-damima-74": [685],
"jild13-maakhiz-damima-75": [685],
"jild13-maakhiz-damima-76": [685],
"jild13-maakhiz-damima-77": [685],
"jild13-maakhiz-damima-78": [685],
"jild13-maakhiz-damima-79": [685],
"jild13-maakhiz-damima-80": [685],
"jild13-maakhiz-damima-81": [685],
"jild13-maakhiz-heading-685-qaf": [685],
"jild13-maakhiz-damima-82": [685],
"jild13-maakhiz-heading-686-kaf": [686],
"jild13-maakhiz-damima-83": [686],
"jild13-maakhiz-damima-84": [686],
"jild13-maakhiz-damima-85": [686],
"jild13-maakhiz-damima-86": [686],
"jild13-maakhiz-damima-87": [686],
"jild13-maakhiz-damima-88": [686],
"jild13-maakhiz-damima-89": [686],
"jild13-maakhiz-damima-90": [686],
"jild13-maakhiz-damima-91": [686],
"jild13-maakhiz-damima-92": [686],
"jild13-maakhiz-damima-93": [686],
"jild13-maakhiz-damima-94": [686],
"jild13-maakhiz-damima-95": [686],
"jild13-maakhiz-damima-96": [686],
"jild13-maakhiz-heading-686-lam": [686],
"jild13-maakhiz-damima-97": [686],
"jild13-maakhiz-heading-686-mim": [686],
"jild13-maakhiz-damima-98": [686],
"jild13-maakhiz-damima-majmua-khani": [686],
"jild13-maakhiz-damima-99": [686],
"jild13-maakhiz-damima-100": [686],
"jild13-maakhiz-damima-101": [687],
"jild13-maakhiz-damima-102": [687],
"jild13-maakhiz-damima-103": [687],
"jild13-maakhiz-damima-104": [687],
"jild13-maakhiz-damima-105": [687],
"jild13-maakhiz-damima-106": [687],
"jild13-maakhiz-damima-107": [687],
"jild13-maakhiz-damima-108": [687],
"jild13-maakhiz-damima-109": [687],
"jild13-maakhiz-damima-110": [687],
"jild13-maakhiz-damima-111": [687],
"jild13-maakhiz-damima-112": [687],
"jild13-maakhiz-damima-113": [687],
"jild13-maakhiz-damima-114": [687],
"jild13-maakhiz-damima-115": [687],
"jild13-maakhiz-damima-116": [687],
"jild13-maakhiz-damima-117": [687],
"jild13-maakhiz-damima-118": [687],
"jild13-maakhiz-damima-119": [687],
"jild13-maakhiz-damima-120": [687],
"jild13-maakhiz-damima-121": [687],
"jild13-maakhiz-damima-122": [687],
"jild13-maakhiz-damima-123": [687],
"jild13-maakhiz-heading-687-nun": [687],
"jild13-maakhiz-damima-124": [687],
"jild13-maakhiz-damima-125": [688],
"jild13-maakhiz-damima-126": [688],
"jild13-maakhiz-damima-127": [688],
"jild13-maakhiz-damima-128": [688],
"jild13-maakhiz-damima-129": [688],
"jild13-maakhiz-damima-130": [688],
"jild13-maakhiz-damima-131": [688],
"jild13-maakhiz-damima-132": [688],
"jild13-maakhiz-damima-133": [688],
"jild13-maakhiz-damima-134": [688],
"jild13-maakhiz-damima-135": [688],
"jild13-maakhiz-damima-136": [688],
"jild13-maakhiz-damima-137": [688],
"jild13-maakhiz-damima-138": [688],
"jild13-maakhiz-heading-688-waw": [688],
"jild13-maakhiz-damima-139": [688],
"jild13-maakhiz-damima-140": [688],
"jild13-maakhiz-damima-141": [688],
"jild13-maakhiz-heading-688-ha2": [688],
"jild13-maakhiz-damima-142": [688],
"jild13-maakhiz-damima-143": [688],
}

# The Urdu word for "page" is safha; the canonical marker is [safha N].
# Lenticular brackets are U+3010 (open) and U+3011 (close); the short
# form is "[safha-initial N]" with the single-letter abbreviation.
# All three patterns are built from escapes so this file never contains
# a literal lenticular-bracket pair.
SAFHA = "\u0635\u0641\u062d\u06c1"  # the Urdu word for page
RE_LENTICULAR = re.compile("\u3010" + SAFHA + " (\\d+)\u3011")
RE_SHORT = re.compile("\\[\u0635 (\\d+)\\]")
RE_FULL = re.compile("\\[" + SAFHA + " \\d+\\]")
LENTICULAR_PREFIX = "\u3010" + SAFHA  # for the "none remain" check
SHORT_PREFIX_RE = re.compile("\\[\u0635 \\d+\\]")

# Canonical output key order for every item (the JSON contract).
ITEM_KEYS = ["id", "title", "volume_id", "pages", "start_page",
             "tashreeh_sawal", "tashreeh_jawab", "notes"]


def normalise_markers(text):
    """Normalise page markers in one string. Returns (new_text, counts)."""
    counts = {"lenticular": 0, "short": 0, "full_before": 0}
    counts["full_before"] = len(RE_FULL.findall(text))
    text, n1 = RE_LENTICULAR.subn("[" + SAFHA + " \\1]", text)
    counts["lenticular"] = n1
    text, n2 = RE_SHORT.subn("[" + SAFHA + " \\1]", text)
    counts["short"] = n2
    return text, counts


def normalise_item(item):
    """Normalise markers in every string field of one item (recursively
    through lists/dicts). Returns per-form counts for this item."""
    totals = {"lenticular": 0, "short": 0, "full_before": 0}

    def walk(value):
        if isinstance(value, str):
            new, c = normalise_markers(value)
            for k in totals:
                totals[k] += c[k]
            return new
        if isinstance(value, list):
            return [walk(v) for v in value]
        if isinstance(value, dict):
            return {k: walk(v) for k, v in value.items()}
        return value

    for key in list(item.keys()):
        item[key] = walk(item[key])
    return totals


def main():
    assert len(V3_IDS) == EXPECTED_ITEMS, "embedded V3_IDS length mismatch"
    assert set(V3_PAGES) == set(V3_IDS), "embedded V3_PAGES keys != V3_IDS"
    assert sum(len(v) for v in V3_PAGES.values()) >= EXPECTED_PAGES

    manifest = json.load(open(os.path.join(BASE, MANIFEST), encoding="utf-8"))
    entries = manifest["chunks"]
    assert len(entries) == 14, f"expected 14 manifest entries, got {len(entries)}"
    assert all(e.get("status") == "done" for e in entries), "not all chunks done"
    by_file = {e["file"]: e for e in entries}
    assert set(by_file) == set(CHUNK_ORDER), (
        f"manifest files != CHUNK_ORDER: "
        f"missing={set(CHUNK_ORDER) - set(by_file)} "
        f"extra={set(by_file) - set(CHUNK_ORDER)}"
    )

    all_items = []
    derived = []
    for fname in CHUNK_ORDER:
        path = os.path.join(BASE, fname)
        d = json.load(open(path, encoding="utf-8"))
        items = d["masail"]
        entry = by_file[fname]
        assert len(items) == entry["items"], (
            f"{fname}: {len(items)} items, manifest says {entry['items']}"
        )
        # Marker normalisation, with before/after counts per chunk.
        before = {"lenticular": 0, "short": 0, "full_before": 0}
        for it in items:
            c = normalise_item(it)
            for k in before:
                before[k] += c[k]
        after_full = sum(
            len(RE_FULL.findall(json.dumps(it, ensure_ascii=False)))
            for it in items
        )
        print(
            f"{fname}: {len(items)} items | markers before: "
            f"lenticular={before['lenticular']} short={before['short']} "
            f"full={before['full_before']} | after: full={after_full}"
        )
        assert after_full == (
            before["lenticular"] + before["short"] + before["full_before"]
        ), f"{fname}: marker count changed by normalisation!"
        # Derive start_page = min(pages) where absent (none expected: all chunks carry start_page).
        for it in items:
            if "start_page" not in it:
                it["start_page"] = min(it["pages"])
                derived.append(it["id"])
        all_items.extend(items)

    # NO RENAME QUIRK in Jild 13: the v3 merged file has 966 UNIQUE
    # ids — the book numbers no masala twice in this jild. Chunk ids
    # are used exactly as written.
    assert len(all_items) == len({it["id"] for it in all_items}), (
        f"DUPLICATE IDS before validation: "
        f"{[i for i in [it['id'] for it in all_items] if [it['id'] for it in all_items].count(i) > 1]}"
    )
    print("renames applied: [] (no duplicate masala numbers in Jild 13)")

    print(f"concatenated: {len(all_items)} items")
    print(f"start_page derived for {len(derived)} items (expected 0: all chunks carry start_page)")
    assert len(all_items) == EXPECTED_ITEMS, (
        f"expected {EXPECTED_ITEMS} items, got {len(all_items)}"
    )

    # Rebuild each item in the canonical key order (the JSON contract).
    canonical = []
    for it in all_items:
        assert set(it.keys()) == set(ITEM_KEYS), (
            f"{it.get('id')}: keys {sorted(it.keys())} != {sorted(ITEM_KEYS)}"
        )
        canonical.append({k: it[k] for k in ITEM_KEYS})
    all_items = canonical

    # Validation.
    ids = [it["id"] for it in all_items]
    assert ids == V3_IDS, (
        f"ID sequence != v3: first diff at "
        f"{next((i for i, (a, b) in enumerate(zip(ids, V3_IDS)) if a != b), min(len(ids), len(V3_IDS)))}"
    )
    assert len(ids) == len(set(ids)), (
        f"DUPLICATE IDS: {[i for i in ids if ids.count(i) > 1]}"
    )
    empty = [it["id"] for it in all_items if not it.get("tashreeh_jawab")]
    assert not empty, f"EMPTY JAWAB: {empty}"
    vols = set(it.get("volume_id") for it in all_items)
    assert vols == EXPECTED_VOLUME_IDS, f"volume_ids {vols} != {EXPECTED_VOLUME_IDS}"
    pages = set()
    for it in all_items:
        assert it["pages"] == V3_PAGES[it["id"]], (
            f"{it['id']}: pages {it['pages']} != v3 {V3_PAGES[it['id']]}"
        )
        pages.update(it["pages"])
    assert len(pages) == EXPECTED_PAGES, (
        f"expected {EXPECTED_PAGES} unique pages, got {len(pages)}"
    )
    assert min(pages) == EXPECTED_MIN_PAGE, f"min page {min(pages)}"
    assert max(pages) == EXPECTED_MAX_PAGE, f"max page {max(pages)}"
    exceptions = {
        it["id"] for it in all_items if it["start_page"] != min(it["pages"])
    }
    assert not exceptions, f"start_page != min(pages): {sorted(exceptions)}"
    assert ids[0] == EXPECTED_FIRST_ID, f"first id {ids[0]}"
    assert ids[-1] == EXPECTED_LAST_ID, f"last id {ids[-1]}"

    out = {"masail": all_items}
    out_text = json.dumps(out, ensure_ascii=False, indent=1)
    assert LENTICULAR_PREFIX not in out_text, "lenticular markers remain in output!"
    assert not SHORT_PREFIX_RE.search(out_text), "short markers remain in output!"
    total_markers = len(RE_FULL.findall(out_text))
    print(
        f"VALIDATION PASSED: {len(all_items)} items, {len(pages)} unique pages "
        f"(min {min(pages)}, max {max(pages)}), volume_ids {sorted(vols)}, "
        f"first {ids[0]}, last {ids[-1]}, start_page == min(pages) for all, "
        f"derived start_page for {len(derived)} items, markers {total_markers}"
    )

    with open(os.path.join(BASE, "jild-13.json"), "w", encoding="utf-8") as f:
        f.write(out_text)
    print(f"WROTE jild-13.json: {len(out_text.encode('utf-8'))} bytes")


if __name__ == "__main__":
    main()
