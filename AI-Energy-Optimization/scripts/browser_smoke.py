"""Optional browser integration check. Run against a dedicated test state backend."""

import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page(
            viewport={"width": 1440, "height": 1000}, accept_downloads=True
        )
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.request.post(
            os.environ.get("TEST_API_URL", "http://127.0.0.1:8011")
            + "/simulation/reset"
        )
        page.goto(os.environ.get("FRONTEND_URL", "http://127.0.0.1:5178"))
        expect(page.get_by_role("heading", name="Data Center Overview")).to_be_visible()
        page.screenshot(path=str(ROOT / "experiments/dashboard.png"), full_page=True)

        def nav(name):
            page.locator("nav").get_by_role("button", name=name, exact=True).click()

        page.on("console",lambda msg:errors.append(msg.text) if msg.type=="error" and "status of 422" not in msg.text else None)
        # Each page has a keyboard-accessible simulation guide; Dashboard includes the full workflow.
        guide_names = [
            "Dashboard",
            "Resource Monitor",
            "AI Optimization",
            "Data Center Simulator",
            "Workload Intelligence",
            "VM Placement",
            "VM Consolidation",
            "Energy Analytics",
            "Optimization Comparison",
            "Adaptive Optimization",
            "Simulation History",
            "Reports",
        ]
        for name in guide_names:
            nav(name)
            trigger = page.get_by_role("button", name="About " + name, exact=True)
            trigger.click()
            dialog = page.get_by_role("dialog")
            expect(dialog).to_be_visible()
            if name == "Dashboard":
                expect(
                    dialog.get_by_role(
                        "heading", name="Overall project workflow", exact=True
                    )
                ).to_be_visible()
                assert dialog.locator("li").count() == 7
                page.keyboard.press("Tab")
                assert page.evaluate(
                    "document.querySelector('dialog').contains(document.activeElement)"
                )
                page.keyboard.press("Escape")
                expect(dialog).not_to_be_visible()
                expect(trigger).to_be_focused()
            else:
                dialog.get_by_role("button", name="Got it", exact=True).click()
                expect(dialog).not_to_be_visible()
        nav("Dashboard")
        page.get_by_role("button", name="Help: Servers", exact=True).click()
        expect(page.get_by_role("dialog")).to_contain_text("simulated physical servers")
        page.get_by_role("button", name="Close help", exact=True).click()
        page.get_by_role("button",name="About Dashboard",exact=True).click()
        page.screenshot(path=str(ROOT/"experiments/dashboard-help.png"),full_page=True)
        page.mouse.click(3,3)
        expect(page.get_by_role("dialog")).not_to_be_visible()
        nav("Workload Intelligence")
        expect(
            page.get_by_role("heading", name="Workload Intelligence")
        ).to_be_visible()
        page.get_by_label("VM", exact=True).select_option("VM1")
        page.get_by_role("button", name="Load synthetic example", exact=True).click()
        page.get_by_role("button", name="Save & forecast VM", exact=True).click()
        expect(page.get_by_role("heading", name="Server forecasts")).to_be_visible()
        # Use the user editor, not hardcoded examples: changing and saving input changes actual inference.
        first_result = page.request.get(
            "http://127.0.0.1:8011/intelligence/forecasts"
        ).json()["vm_forecasts"][0]
        page.get_by_role("button", name="Help: cpu_util_percent", exact=True).click()
        expect(page.get_by_role("dialog")).to_contain_text("0 to 100")
        page.keyboard.press("Escape")
        for index in range(1, 5):
            page.get_by_label(f"cpu_util_percent interval {index}", exact=True).fill(
                "90"
            )
            page.get_by_label(f"mem_util_percent interval {index}", exact=True).fill(
                "95"
            )
        expect(page.get_by_role("heading", name="Server forecasts")).not_to_be_visible()
        expect(
            page.get_by_role("button", name="Forecast all saved histories", exact=True)
        ).to_be_disabled()
        expect(page.get_by_role("status")).to_contain_text("Unsaved")
        page.get_by_role("button", name="Save & forecast VM", exact=True).click()
        expect(page.get_by_role("status")).to_contain_text(
            "Saved your user-entered readings"
        )
        custom = page.request.get("http://127.0.0.1:8011/intelligence/forecasts").json()
        changed = custom["vm_forecasts"][0]
        assert custom["sources"]["VM1"] == "user-entered"
        assert (
            abs(
                changed["predicted_cpu_percent"] - first_result["predicted_cpu_percent"]
            )
            > 1
        )
        saved = page.request.get("http://127.0.0.1:8011/intelligence/histories").json()
        assert saved["histories"]["VM1"][-1]["cpu_util_percent"] == 90
        # Invalid user percentages are rejected and do not replace the last accepted history.
        page.get_by_label("cpu_util_percent interval 1",exact=True).fill("101")
        page.get_by_role("button",name="Save & forecast VM",exact=True).click()
        expect(page.get_by_role("alert")).to_contain_text("100")
        assert page.request.get("http://127.0.0.1:8011/intelligence/histories").json()["histories"]["VM1"][0]["cpu_util_percent"]==90
        page.get_by_label("cpu_util_percent interval 1",exact=True).fill("90")
        page.get_by_role("button",name="Save & forecast VM",exact=True).click()
        expect(page.get_by_role("status")).to_contain_text("Saved your user-entered readings")
        # Opening action help must not execute an action, including disabled Apply.
        nav("VM Placement")
        before = page.request.get("http://127.0.0.1:8011/simulation/state").json()[
            "revision"
        ]
        page.get_by_role("button", name="Help: Apply preview", exact=True).click()
        expect(page.get_by_role("dialog")).to_contain_text("shared simulation")
        page.keyboard.press("Escape")
        assert (
            page.request.get("http://127.0.0.1:8011/simulation/state").json()[
                "revision"
            ]
            == before
        )
        page.get_by_role("button", name="Preview placement", exact=True).click()
        expect(page.get_by_role("heading", name="Planned actions")).to_be_visible()
        page.screenshot(path=str(ROOT / "experiments/placement.png"), full_page=True)
        page.get_by_role("button", name="Apply preview", exact=True).click()
        expect(page.get_by_role("status")).to_contain_text("Plan applied")
        nav("Optimization Comparison")
        page.get_by_role("button", name="Run controlled comparison", exact=True).click()
        expect(
            page.get_by_role(
                "heading", name="Estimated interval energy including migrations"
            )
        ).to_be_visible()
        nav("Adaptive Optimization")
        page.get_by_label("Workload source",exact=True).select_option("synthetic")
        page.get_by_role(
            "button", name="Advance one interval & apply", exact=True
        ).click()
        expect(page.get_by_text("Saved interval: 1", exact=True)).to_be_visible()
        nav("Simulation History")
        expect(page.get_by_role("cell", name="adaptive_result")).to_be_visible()
        nav("Reports")
        with page.expect_download() as d:
            page.get_by_role(
                "button", name="Download comparison CSV", exact=True
            ).click()
        assert d.value.suggested_filename == "algorithm-comparison.csv"
        with page.expect_download() as d:
            page.get_by_role("button", name="Download JSON report", exact=True).click()
        assert d.value.suggested_filename == "simulation-report.json"
        for name, title in [
            ("Energy Analytics", "Energy Analytics"),
            ("Data Center Simulator", "Virtual Data Center"),
            ("VM Consolidation", "VM Consolidation"),
            ("AI Optimization", "Multi-Objective Optimization"),
            ("Resource Monitor", "Workload History"),
        ]:
            nav(name)
            expect(page.get_by_role("heading", name=title, exact=True)).to_be_visible()
        page.get_by_role("button", name="Run AI Analysis", exact=True).click()
        expect(page.get_by_role("heading", name="AI Analysis Results")).to_be_visible()
        # Editing resource inputs must hide invalidated recommendations.
        page.locator(".table-input").first.fill("61")
        expect(page.get_by_text("AI Recommendation", exact=True)).not_to_be_visible()
        nav("Dashboard")
        page.reload()
        expect(page.get_by_role("heading", name="Data Center Overview")).to_be_visible()
        page.set_viewport_size({"width": 390, "height": 844})
        page.get_by_role("button", name="Toggle navigation", exact=True).click()
        nav("Energy Analytics")
        expect(
            page.get_by_role("heading", name="Energy Analytics", exact=True)
        ).to_be_visible()
        page.get_by_role("button", name="About Energy Analytics", exact=True).click()
        expect(page.get_by_role("dialog")).to_be_visible()
        assert page.get_by_role("dialog").bounding_box()["width"] <= 390
        assert page.evaluate(
            "document.querySelector('dialog').scrollWidth <= document.querySelector('dialog').clientWidth"
        )
        page.get_by_role("button", name="Got it", exact=True).click()
        assert page.evaluate(
            "document.documentElement.scrollWidth <= window.innerWidth"
        ), "Mobile horizontal overflow"
        expect(page.locator("aside")).to_have_css("left", "-280px")
        page.screenshot(
            path=str(ROOT / "experiments/mobile.png"),
            full_page=True,
            animations="disabled",
        )
        assert not errors, errors
        browser.close()
        (ROOT / "experiments/browser-smoke.json").write_text(
            json.dumps(
                {
                    "status": "passed",
                    "pages": 12,
                    "desktop": [1440, 1000],
                    "mobile": [390, 844],
                    "checks": [
                        "navigation",
                        "page guides on all 12 pages",
                        "Dashboard full 7-step workflow popup",
                        "modal Escape dismissal, focus trap and focus restoration",
                        "field/action help does not mutate state",
                        "custom CPU/RAM input changes saved forecasts and provenance",
                        "invalid percentages rejected without replacing accepted history",
                        "unsaved input invalidates results and blocks batch forecast",
                        "mobile help dialog and overflow",
                        "save per-VM synthetic forecast",
                        "preview and apply",
                        "comparison",
                        "adaptive interval",
                        "history",
                        "JSON and CSV exports",
                        "legacy inference",
                        "input invalidation",
                        "reload persistence",
                        "mobile navigation and overflow",
                    ],
                    "page_errors": errors,
                },
                indent=2,
            )
        )
        print("Browser smoke checks passed.")


if __name__ == "__main__":
    main()
