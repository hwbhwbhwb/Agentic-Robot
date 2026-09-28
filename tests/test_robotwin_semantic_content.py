import csv
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import build


ROOT = Path(__file__).resolve().parents[1]
PROJECT_SLUG = "robotwin-semantic-success"
POST_SLUG = "robotwin-rsi-semantic-success"


class RobotwinSemanticContentTest(unittest.TestCase):
    def test_project_and_post_are_registered(self):
        projects = json.loads((ROOT / "content/projects.json").read_text())
        posts = json.loads((ROOT / "content/posts.json").read_text())

        project = next(item for item in projects if item["slug"] == PROJECT_SLUG)
        post = next(item for item in posts if item["slug"] == POST_SLUG)

        self.assertEqual(project["number"], "03")
        self.assertIn(PROJECT_SLUG, post["projects"])
        self.assertEqual(project["results_path"], f"/posts/{POST_SLUG}/")
        self.assertEqual(project["article_results_path"], f"/projects/{PROJECT_SLUG}/")
        self.assertEqual(post["results_path"], f"/projects/{PROJECT_SLUG}/")

    def test_home_uses_the_selected_semantic_success_video_for_the_rsi_blog(self):
        video = "robotwin-semantic/adjust-bottle-seed-000-semantic-only-hd.mp4"
        poster = "robotwin-semantic/adjust-bottle-seed-000-semantic-only-hd.jpg"

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build.build(output_dir=output)
            home_page = (output / "index.html").read_text()
            blogs_page = (output / "blogs/index.html").read_text()

        self.assertIn(f'<source src="/assets/{video}" type="video/mp4">', home_page)
        self.assertIn(f'poster="/assets/{poster}"', home_page)
        self.assertIn("adjust_bottle · seed 000 · Semantic-only success", home_page)
        self.assertNotIn(f'<source src="/assets/{video}"', blogs_page)
        self.assertIn(
            'src="/assets/robotwin-domain-randomization.png"', blogs_page
        )

        ffprobe = shutil.which("ffprobe")
        self.assertIsNotNone(ffprobe)
        probe = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=codec_name,pix_fmt,width,height",
                "-of",
                "json",
                str(ROOT / "assets" / video),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        stream = json.loads(probe.stdout)["streams"][0]
        self.assertEqual(stream["codec_name"], "h264")
        self.assertEqual(stream["pix_fmt"], "yuv420p")
        self.assertEqual((stream["width"], stream["height"]), (960, 720))

    def test_rsi_authors_are_intentionally_blank(self):
        posts = json.loads((ROOT / "content/posts.json").read_text())
        post = next(item for item in posts if item["slug"] == POST_SLUG)

        self.assertEqual(post["authors"], [])

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build.build(output_dir=output)
            post_page = (output / f"posts/{POST_SLUG}/index.html").read_text()

        self.assertIn(
            '<span class="author-label">Authors</span><div class="author-list"></div>',
            post_page,
        )
        self.assertNotIn('<span class="author-name">Wenbo Huang</span>', post_page)
        self.assertNotIn("author = {}", post_page)
        self.assertNotIn(
            '<p class="citation-reference">. When Success Means the Task',
            post_page,
        )

    def test_rsi_article_follows_the_robodojo_narrative_order(self):
        article = (ROOT / "content/articles/robotwin-rsi-semantic-success.html").read_text()
        headings = re.findall(r'<h2 id="([^"]+)">([^<]+)</h2>', article)

        self.assertEqual(
            headings,
            [
                ("summary", "1. From Reaching a Target to Completing the Task"),
                ("rsi", "2. RSI: Develop the Policy, Then Freeze the Evaluation"),
                ("why", "3. Why Zero-Shot Evaluation Needs a Semantic Fix"),
                ("method", "4. What Semantic Success Checks"),
                ("setup", "5. Experimental Setup and Results Across 50 Tasks"),
                ("cases", "6. Case Studies"),
                ("implications", "7. Implications for RSI and Benchmark Design"),
                ("conclusion", "8. Conclusion"),
            ],
        )

    def test_rsi_flow_uses_the_interactive_node_map(self):
        article = (ROOT / "content/articles/robotwin-rsi-semantic-success.html").read_text()
        script = (ROOT / "assets/app.js").read_text()
        styles = (ROOT / "assets/sidebar.css").read_text()

        self.assertNotIn('class="flow-strip"', article)
        self.assertIn('<figure class="rsi-flow-map" data-rsi-flow>', article)
        self.assertIn('class="rsi-flow-svg"', article)
        self.assertEqual(article.count('data-rsi-stage='), 4)
        for stage in ["generate", "iterate", "freeze", "evaluate"]:
            self.assertIn(f'data-rsi-stage="{stage}"', article)
        self.assertIn('aria-live="polite" aria-atomic="true"', article)
        self.assertIn("Feedback can revise code during development", article)
        self.assertIn("Stop agent edits", article)
        self.assertIn("Locked evaluation input", script)
        self.assertIn("new evaluation seeds without coding-agent intervention", script)
        self.assertIn("same rollout", script)
        self.assertIn("const rsiFlow = document.querySelector('[data-rsi-flow]');", script)
        self.assertIn("querySelectorAll('[data-rsi-stage]')", script)
        self.assertIn(".rsi-flow-map", styles)
        self.assertIn(".rsi-flow-node.selected", styles)
        self.assertIn(
            ".rsi-flow-map{margin:26px 0 31px;border:1px solid var(--line);"
            "background:var(--card-surface)",
            styles,
        )
        self.assertIn(".rsi-flow-edges{color:#7b876d}", styles)
        self.assertIn(
            ".rsi-flow-node rect{fill:var(--paper);stroke:#bbc4b0;stroke-width:1.2}",
            styles,
        )
        self.assertIn(".rsi-flow-output{fill:#354531}", styles)

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build.build(output_dir=output)
            post_page = (output / f"posts/{POST_SLUG}/index.html").read_text()
        self.assertIn('data-rsi-flow', post_page)
        self.assertEqual(post_page.count('data-rsi-stage='), 4)

    def test_setup_and_results_are_merged_into_one_prose_section(self):
        article = (ROOT / "content/articles/robotwin-rsi-semantic-success.html").read_text()
        setup = article.split(
            '<h2 id="setup">5. Experimental Setup and Results Across 50 Tasks</h2>',
            1,
        )[1].split('<div class="result-legend">', 1)[0]

        self.assertNotIn("<ul>", setup)
        self.assertNotIn('<h2 id="results">', article)
        self.assertNotIn("Counting rule:", article)
        self.assertNotIn("The snapshot is stored under", article)
        self.assertNotIn("parallel_summary.json", article)
        self.assertIn("20 rollouts per task and 1,000 rollouts overall", setup)
        self.assertIn("Origin and Semantic evaluated the same rollout", setup)
        self.assertNotIn("<h3>5.1", article)
        self.assertNotIn("<h3>5.2", article)
        self.assertNotIn("<h3>5.3", article)
        insights = article.split('<ul class="result-insights">', 1)[1].split(
            "</ul>", 1
        )[0]
        self.assertEqual(insights.count("<li>"), 3)
        self.assertIn(
            "<strong>Semantic is higher when Origin binds success to the wrong endpoint.</strong>",
            insights,
        )
        self.assertIn(
            "<strong>Origin is higher when a transient state is mistaken for a complete behavior.</strong>",
            insights,
        )
        self.assertIn(
            "<strong>When both scores are low, the policy is the first place to look.</strong>",
            insights,
        )

    def test_article_uses_a_shared_gate_with_two_predicate_cards(self):
        article = (ROOT / "content/articles/robotwin-rsi-semantic-success.html").read_text()
        styles = (ROOT / "assets/styles.css").read_text()

        self.assertIn('<figure class="code-card predicate-logic-card"', article)
        self.assertIn("Origin success predicate", article)
        self.assertIn('<code class="code-task">adjust_bottle</code>', article)
        self.assertIn('class="predicate-gate"', article)
        predicate_gate_rule = styles.split(".predicate-gate{", 1)[1].split("}", 1)[0]
        self.assertNotIn("background:", predicate_gate_rule)
        self.assertEqual(article.count('class="predicate-branch '), 2)
        self.assertIn("Shared height gate", article)
        self.assertIn("qpose_tag == 0", article)
        self.assertIn("qpose_tag == 1", article)
        self.assertNotIn('class="code-line"', article)
        self.assertIn("--mono:", styles)
        self.assertIn(".prose :where(p,li) code", styles)
        self.assertIn(".predicate-branches{display:grid", styles)
        self.assertIn(".predicate-branch.left{border-top-color:#237569}", styles)
        self.assertIn(".predicate-branch.right{border-top-color:#c26a40}", styles)

    def test_summary_numbers_follow_the_robodojo_metric_palette(self):
        styles = (ROOT / "assets/styles.css").read_text()

        self.assertIn(".semantic-hero-card.origin strong{color:#237569}", styles)
        self.assertIn(".semantic-hero-card.semantic strong{color:#c26a40}", styles)
        self.assertIn(".semantic-hero-card.both strong{color:#9b7658}", styles)

    def test_article_preserves_semantic_evidence_boundary(self):
        article = (ROOT / "content/articles/robotwin-rsi-semantic-success.html").read_text()

        self.assertIn("terminal JSON", article)
        self.assertIn("Origin-SR", article)
        self.assertIn("Semantic-SR", article)
        self.assertIn("Semantic has 18 more successful seeds", article)
        self.assertIn("stack_bowls_three", article)
        self.assertIn("adjust_bottle", article)
        for asset in [
            "adjust-bottle-seed-000-semantic-only.mp4",
            "grab-roller-seed-000-semantic-only.mp4",
            "pick-dual-bottles-seed-005-semantic-only.mp4",
            "shake-bottle-horizontal-seed-004-origin-only.mp4",
            "stack-blocks-two-seed-000-both-fail.mp4",
        ]:
            self.assertIn(asset, article)
            self.assertTrue((ROOT / "assets/robotwin-semantic" / asset).exists())

    def test_article_uses_playable_h264_videos_with_unique_posters(self):
        article = (ROOT / "content/articles/robotwin-rsi-semantic-success.html").read_text()
        videos = re.findall(
            r'<video controls playsinline preload="metadata" poster="/assets/robotwin-semantic/([^"]+\.jpg)"[^>]*>\s*'
            r'<source src="/assets/robotwin-semantic/([^"]+\.mp4)" type="video/mp4">',
            article,
        )

        self.assertEqual(len(videos), 5)
        self.assertEqual(len({poster for poster, _ in videos}), 5)
        self.assertNotIn('poster="/assets/robotwin-domain-randomization.png"', article)
        self.assertNotIn("{{ARTICLE_VIDEO}}", article)

        ffprobe = shutil.which("ffprobe")
        self.assertIsNotNone(ffprobe)
        for poster, video in videos:
            poster_path = ROOT / "assets/robotwin-semantic" / poster
            video_path = ROOT / "assets/robotwin-semantic" / video
            self.assertTrue(poster_path.is_file())
            self.assertGreater(poster_path.stat().st_size, 0)
            probe = subprocess.run(
                [
                    ffprobe,
                    "-v",
                    "error",
                    "-select_streams",
                    "v:0",
                    "-show_entries",
                    "stream=codec_name,pix_fmt,width,height:format=duration",
                    "-of",
                    "json",
                    str(video_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            metadata = json.loads(probe.stdout)
            stream = metadata["streams"][0]
            self.assertEqual(stream["codec_name"], "h264")
            self.assertEqual(stream["pix_fmt"], "yuv420p")
            self.assertGreater(stream["width"], 0)
            self.assertGreater(stream["height"], 0)
            self.assertGreater(float(metadata["format"]["duration"]), 0)

    def test_rsi_article_owns_its_media_instead_of_repeating_the_cover(self):
        posts = json.loads((ROOT / "content/posts.json").read_text())
        post = next(item for item in posts if item["slug"] == POST_SLUG)

        self.assertIs(post["article_media"], False)

    def test_rsi_article_does_not_promote_the_project_below_its_title(self):
        posts = json.loads((ROOT / "content/posts.json").read_text())
        post = next(item for item in posts if item["slug"] == POST_SLUG)

        self.assertIs(post["promote_results"], False)

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build.build(output_dir=output)
            article_page = (output / f"posts/{POST_SLUG}/index.html").read_text()
            blogs_page = (output / "blogs/index.html").read_text()
            project_page = (
                output / f"projects/{PROJECT_SLUG}/index.html"
            ).read_text()
            robodojo_page = (
                output / "posts/robodojo-offline-policy-zero-shot/index.html"
            ).read_text()

        header = article_page.split('<header class="wrap article-header">', 1)[1].split(
            "</header>", 1
        )[0]
        robotwin_card = blogs_page.split(
            f'<h3><a href="/posts/{POST_SLUG}/">', 1
        )[1].split("</article>", 1)[0]

        self.assertNotIn("Interactive Webpage", header)
        self.assertNotIn('class="article-header-actions"', header)
        self.assertNotIn("Interactive Webpage", robotwin_card)
        self.assertIn("Read Blog", robotwin_card)
        project_card = project_page.split(
            f'<h3><a href="/posts/{POST_SLUG}/">', 1
        )[1].split("</article>", 1)[0]
        self.assertNotIn("Interactive Webpage", project_card)
        self.assertIn("Read Blog", project_card)
        self.assertNotIn("From the story to the evidence", article_page)
        self.assertNotIn("Inspect the experiment.", article_page)
        self.assertNotIn("Open interactive report", article_page)
        self.assertNotIn('class="article-cta"', article_page)
        article_aside = article_page.split(
            '<aside class="article-aside">', 1
        )[1].split("</aside>", 1)[0]
        self.assertIn('class="toc"', article_aside)
        self.assertNotIn("Interactive report", article_aside)
        self.assertNotIn('class="aside-project"', article_aside)
        self.assertIn('class="article-citation"', article_page)
        robodojo_header = robodojo_page.split(
            '<header class="wrap article-header">', 1
        )[1].split("</header>", 1)[0]
        self.assertIn("Interactive Webpage", robodojo_header)
        self.assertIn('class="article-header-actions"', robodojo_header)
        self.assertIn("From the story to the evidence", robodojo_page)
        self.assertIn("Open interactive report", robodojo_page)
        self.assertIn("Interactive report", robodojo_page)
        self.assertIn('class="aside-project"', robodojo_page)

    def test_article_has_all_50_tasks_and_delta_column(self):
        article = (ROOT / "content/articles/robotwin-rsi-semantic-success.html").read_text()

        self.assertEqual(article.count('data-task-row'), 50)
        self.assertIn(
            '<tr class="summary-row"><th scope="row">Total</th>'
            '<td><strong>164 / 1,000</strong></td>'
            '<td><strong>182 / 1,000</strong></td>'
            '<td><strong>124 / 1,000</strong></td>'
            '<td><strong>+18 / 1,000</strong></td></tr>',
            article,
        )
        self.assertIn("Semantic − Origin", article)
        self.assertIn("164", article)
        self.assertIn("182", article)
        self.assertIn("124", article)

    def test_results_table_progressively_enhances_into_an_accessible_dashboard(self):
        article = (ROOT / "content/articles/robotwin-rsi-semantic-success.html").read_text()
        styles = (ROOT / "assets/styles.css").read_text()
        script = (ROOT / "assets/app.js").read_text()

        self.assertIn(
            '<section class="results-dashboard" data-results-dashboard hidden',
            article,
        )
        self.assertIn('data-results-search', article)
        self.assertEqual(article.count('data-results-filter='), 5)
        self.assertIn('data-results-sort', article)
        self.assertIn('data-results-chart', article)
        self.assertIn('aria-live="polite"', article)
        self.assertIn('<details class="results-table-detail" data-results-table-detail>', article)
        self.assertIn(
            '<table class="semantic-results-table" id="results-table" data-results-table>',
            article,
        )
        self.assertIn(".results-dashboard", styles)
        self.assertIn(".dashboard-task-bars", styles)
        self.assertIn("const resultsDashboard = document.querySelector('[data-results-dashboard]');", script)
        self.assertIn("querySelectorAll('[data-task-row]')", script)
        self.assertIn("semantic - both", script)
        self.assertIn("origin - both", script)
        self.assertIn("denominator - origin - semantic + both", script)
        self.assertIn("the dashboard uses row-derived totals", script)
        self.assertIn("cell.textContent.split('/')[0]", script)
        self.assertNotIn("grab_roller", script)

        rows = [
            tuple(map(int, match.groups()))
            for match in re.finditer(
                r'<tr data-task-row><td><code>[^<]+</code></td>'
                r'<td>(\d+)</td><td>(\d+)</td><td>(\d+)</td>',
                article,
            )
        ]
        origin, semantic, both = [sum(row[index] for row in rows) for index in range(3)]
        self.assertEqual((origin, semantic, both), (164, 182, 124))
        self.assertEqual((both, semantic - both, origin - both, 1000 - origin - semantic + both), (124, 58, 40, 778))
        self.assertEqual(sum(origin == 0 and semantic == 0 for origin, semantic, _ in rows), 16)
        for origin_count, semantic_count, both_count in rows:
            self.assertLessEqual(origin_count, 20)
            self.assertLessEqual(semantic_count, 20)
            self.assertLessEqual(both_count, min(origin_count, semantic_count))

        summary = re.search(
            r'<tr class="summary-row">.*?<td><strong>([^<]+)</strong></td>'
            r'<td><strong>([^<]+)</strong></td><td><strong>([^<]+)</strong></td>',
            article,
        )
        stated_totals = tuple(int(value.split("/")[0].strip()) for value in summary.groups())
        self.assertEqual(stated_totals, (origin, semantic, both))

    def test_built_article_keeps_the_dashboard_and_static_table_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build.build(output_dir=output)
            post_page = (output / f"posts/{POST_SLUG}/index.html").read_text()

        self.assertIn('data-results-dashboard hidden', post_page)
        self.assertIn('data-results-chart', post_page)
        self.assertIn('id="results-table" data-results-table', post_page)
        self.assertIn('src="/assets/app.js"', post_page)

    def test_measured_rows_match_the_source_snapshot(self):
        article = (ROOT / "content/articles/robotwin-rsi-semantic-success.html").read_text()
        source = (
            ROOT.parent
            / "data_notes/2026-09-24-robotwin50-origin-vs-semantic-progress.md"
        ).read_text()
        source_rows = {
            match.group(1): tuple(map(int, match.groups()[1:]))
            for match in re.finditer(
                r"\| `([^`]+)`\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|",
                source,
            )
        }
        article_rows = {
            match.group(1): tuple(map(int, match.groups()[1:]))
            for match in re.finditer(
                r'<tr data-task-row><td><code>([^<]+)</code></td><td>(\d+)</td><td>(\d+)</td><td>(\d+)</td>',
                article,
            )
        }

        self.assertEqual(len(source_rows), 50)
        self.assertEqual(article_rows, source_rows)

    def test_development_counts_match_the_50_task_archive(self):
        with (ROOT.parent / "robotwin50_final_evidence_20260924/tasks.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            rows = list(csv.DictReader(handle))
        status_counts = {
            "native": sum(row["status_code"] == "native" for row in rows),
            "manual": sum(row["status_code"] == "manual" for row in rows),
            "failed": sum(row["status_code"] == "failed" for row in rows),
        }
        article = (ROOT / "content/articles/robotwin-rsi-semantic-success.html").read_text()
        projects = json.loads((ROOT / "content/projects.json").read_text())
        project = next(item for item in projects if item["slug"] == PROJECT_SLUG)

        self.assertEqual(len(rows), 50)
        self.assertEqual(status_counts, {"native": 25, "manual": 8, "failed": 17})
        self.assertNotIn("25 native + 8 manual", article)
        self.assertEqual(project["metrics"][0]["value"], str(len(rows)))
        self.assertEqual(project["metrics"][1]["value"], "164 / 182")
        self.assertEqual(project["metrics"][2]["value"], "124")

    def test_build_keeps_internal_project_and_post_links_on_site(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build.build(output_dir=output)

            project_page = (output / f"projects/{PROJECT_SLUG}/index.html").read_text()
            post_page = (output / f"posts/{POST_SLUG}/index.html").read_text()

        self.assertIn(f'href="/posts/{POST_SLUG}/"', project_page)
        aside = post_page.split('<aside class="article-aside">', 1)[1].split(
            "</aside>", 1
        )[0]
        self.assertNotIn(f'href="/projects/{PROJECT_SLUG}/"', aside)
        self.assertNotIn(f'href="/posts/{POST_SLUG}/"', aside)
        self.assertNotIn("robodojo-evaluation-atlas", project_page)

    def test_robotwin_project_page_uses_a_paired_comparison_story(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build.build(output_dir=output)
            project_page = (
                output / f"projects/{PROJECT_SLUG}/index.html"
            ).read_text()

        self.assertIn('class="semantic-project-page"', project_page)
        self.assertIn("Origin meets Semantic.", project_page)
        self.assertIn("Different meanings of success.", project_page)
        for class_name in [
            "semantic-project-comparison",
            "semantic-project-outcomes",
            "semantic-project-divergence",
            "semantic-project-flow",
            "semantic-project-evidence",
        ]:
            self.assertRegex(
                project_page,
                rf'class="[^"]*\b{class_name}\b[^"]*"',
            )

        for value in ["164", "182", "124", "58", "40", "778"]:
            self.assertIn(f">{value}<", project_page)
        self.assertIn("16.4%", project_page)
        self.assertIn("18.2%", project_page)
        self.assertIn("50 tasks", project_page)
        self.assertIn("20 seeds per task", project_page)
        self.assertIn("same frozen policy", project_page)
        self.assertIn("evaluator disagreement", project_page)

        self.assertIn("grab_roller", project_page)
        self.assertIn("shake_bottle_horizontally", project_page)
        self.assertEqual(
            project_page.count(
                '<video controls playsinline preload="metadata"'
            ),
            3,
        )
        self.assertIn(f'href="/posts/{POST_SLUG}/"', project_page)
        self.assertNotIn("A closer look at the results.", project_page)
        self.assertNotIn('class="project-overview"', project_page)

        origin_total = int(
            re.search(
                r'<article class="semantic-project-score origin">.*?'
                r'<strong>(\d+)<small>',
                project_page,
                re.DOTALL,
            ).group(1)
        )
        semantic_total = int(
            re.search(
                r'<article class="semantic-project-score semantic">.*?'
                r'<strong>(\d+)<small>',
                project_page,
                re.DOTALL,
            ).group(1)
        )
        outcomes = {
            label: int(value)
            for label, value in re.findall(
                r'<article class="(both|semantic-only|origin-only|neither)">'
                r'.*?<strong>(\d+)</strong>',
                project_page,
                re.DOTALL,
            )
        }
        self.assertEqual((origin_total, semantic_total), (164, 182))
        self.assertEqual(
            outcomes,
            {"both": 124, "semantic-only": 58, "origin-only": 40, "neither": 778},
        )

    def test_robotwin_project_layout_collapses_before_the_sidebar_gets_tight(self):
        styles = (ROOT / "assets/styles.css").read_text()

        tablet_rules = styles.split("@media(max-width:900px){", 1)[1].split(
            "@media(max-width:760px){", 1
        )[0]
        self.assertIn(
            ".semantic-project-hero-grid,.semantic-project-section-head,.semantic-project-reading{grid-template-columns:1fr",
            tablet_rules,
        )
        self.assertIn(
            ".divergence-columns,.semantic-project-video-grid{grid-template-columns:1fr}",
            tablet_rules,
        )
        self.assertIn("overflow-wrap:anywhere", tablet_rules)
        self.assertIn("white-space:normal", tablet_rules)

    def test_robotwin_project_page_preserves_subpath_media_links(self):
        base_path = "/agentic-robot"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build.build(output_dir=output, base_path=base_path)
            project_page = (
                output / f"projects/{PROJECT_SLUG}/index.html"
            ).read_text()

        self.assertIn(
            f'poster="{base_path}/assets/robotwin-semantic/', project_page
        )
        self.assertIn(
            f'src="{base_path}/assets/robotwin-semantic/', project_page
        )
        self.assertIn(
            f'href="{base_path}/posts/{POST_SLUG}/"', project_page
        )

    def test_build_preserves_article_videos_and_result_totals(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build.build(output_dir=output)
            post_page = (output / f"posts/{POST_SLUG}/index.html").read_text()

        article = post_page.split('<article class="prose">', 1)[1].split(
            "</article>", 1
        )[0]
        videos = re.findall(
            r'<video controls playsinline preload="metadata" '
            r'poster="(/assets/robotwin-semantic/[^"]+\.jpg)"[^>]*>\s*'
            r'<source src="(/assets/robotwin-semantic/[^"]+\.mp4)" '
            r'type="video/mp4">',
            article,
        )

        self.assertEqual(len(videos), 5)
        self.assertEqual(len({poster for poster, _ in videos}), 5)
        self.assertNotIn('class="article-figure', article)
        self.assertNotIn("{{ARTICLE_VIDEO}}", article)
        self.assertNotIn("robotwin-domain-randomization", article)
        for _, video in videos:
            self.assertIn(f'<a href="{video}">Open the recording</a>', article)

        rows = [
            tuple(map(int, match.groups()))
            for match in re.finditer(
                r'<tr data-task-row><td><code>[^<]+</code></td>'
                r'<td>(\d+)</td><td>(\d+)</td><td>(\d+)</td>'
                r'<td>[+-]\d+</td></tr>',
                article,
            )
        ]
        overview = [
            int(value)
            for value in re.findall(
                r'<div class="semantic-hero-card [^"]+">.*?<strong>(\d+)</strong>',
                article,
            )
        ]

        self.assertEqual(len(rows), 50)
        self.assertEqual(overview, [164, 182, 124])
        self.assertEqual([sum(row[index] for row in rows) for index in range(3)], overview)

        rendered_insights = article.split('<ul class="result-insights">', 1)[1].split(
            "</ul>", 1
        )[0]
        self.assertEqual(rendered_insights.count("<li>"), 3)
        self.assertNotIn("<h3>5.1", article)
        self.assertNotIn("<h3>5.2", article)
        self.assertNotIn("<h3>5.3", article)

        toc = post_page.split('<nav class="toc" aria-label="Table of contents">', 1)[
            1
        ].split("</nav>", 1)[0]
        self.assertIn(
            '<a href="#setup">5. Experimental Setup and Results Across 50 Tasks</a>',
            toc,
        )
        self.assertIn('<a href="#cases">6. Case Studies</a>', toc)
        self.assertIn(
            '<a href="#implications">7. Implications for RSI and Benchmark Design</a>',
            toc,
        )
        self.assertIn('<a href="#conclusion">8. Conclusion</a>', toc)
        self.assertNotIn('href="#results"', toc)

    def test_build_prefixes_article_video_urls_for_subpath_deployments(self):
        base_path = "/agentic-robot"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build.build(output_dir=output, base_path=base_path)
            post_page = (output / f"posts/{POST_SLUG}/index.html").read_text()

        article = post_page.split('<article class="prose">', 1)[1].split(
            "</article>", 1
        )[0]
        videos = re.findall(
            r'<video controls playsinline preload="metadata" '
            rf'poster="({base_path}/assets/robotwin-semantic/[^"]+\.jpg)"[^>]*>\s*'
            rf'<source src="({base_path}/assets/robotwin-semantic/[^"]+\.mp4)" '
            r'type="video/mp4">',
            article,
        )

        self.assertEqual(len(videos), 5)
        for _, video in videos:
            self.assertIn(f'<a href="{video}">Open the recording</a>', article)


if __name__ == "__main__":
    unittest.main()
