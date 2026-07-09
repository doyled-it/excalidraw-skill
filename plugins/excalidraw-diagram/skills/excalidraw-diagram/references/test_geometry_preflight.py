import unittest

import geometry


class GeometryPreflightTests(unittest.TestCase):
    def test_infer_text_ownership_prefers_smallest_container(self) -> None:
        elements = [
            {
                "id": "bg2",
                "type": "rectangle",
                "x": 0,
                "y": 0,
                "width": 1000,
                "height": 1000,
            },
            {
                "id": "lane_browser_header",
                "type": "rectangle",
                "x": 80,
                "y": 140,
                "width": 260,
                "height": 62,
            },
            {
                "id": "lane_browser_title",
                "type": "text",
                "x": 98,
                "y": 160,
                "width": 101,
                "height": 45,
                "text": "Browser",
                "fontSize": 16,
                "fontFamily": 3,
                "lineHeight": 1.25,
            },
        ]

        text_elements = {
            element["id"]: element
            for element in elements
            if element.get("type") == "text"
        }
        owners, _ = geometry._infer_text_ownership(elements, text_elements)

        self.assertEqual(owners["lane_browser_title"], "lane_browser_header")

    def test_zone_issue_reports_text_crossing_divider(self) -> None:
        elements = [
            {
                "id": "card",
                "type": "rectangle",
                "x": 0,
                "y": 0,
                "width": 220,
                "height": 140,
            },
            {
                "id": "card_title",
                "type": "text",
                "x": 16,
                "y": 12,
                "width": 150,
                "height": 42,
                "text": "Container +\nPTY",
                "fontSize": 16,
                "fontFamily": 3,
                "lineHeight": 1.25,
            },
            {
                "id": "card_divider",
                "type": "line",
                "x": 14,
                "y": 40,
                "width": 180,
                "height": 0,
                "points": [[0, 0], [180, 0]],
                "strokeWidth": 1,
            },
            {
                "id": "card_body",
                "type": "text",
                "x": 16,
                "y": 62,
                "width": 180,
                "height": 32,
                "text": "Body text",
                "fontSize": 10,
                "fontFamily": 3,
                "lineHeight": 1.25,
            },
        ]

        report = geometry.analyze_excalidraw(elements)
        issues = {
            (item["textId"], item["containerId"], item["issue"])
            for item in report["zone_issues"]
        }

        self.assertIn(("card_title", "card", "text_crosses_divider"), issues)


if __name__ == "__main__":
    unittest.main()
