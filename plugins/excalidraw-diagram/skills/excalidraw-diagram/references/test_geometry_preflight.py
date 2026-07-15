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

    def test_inferred_overflow_flags_free_floating_text_wider_than_box(self) -> None:
        # Free-floating text (no containerId) sitting inside a box, but the text
        # is far wider than the box interior -> it visibly runs over the box.
        elements = [
            {
                "id": "box",
                "type": "rectangle",
                "x": 0,
                "y": 0,
                "width": 120,
                "height": 80,
            },
            {
                "id": "label",
                "type": "text",
                "x": 10,
                "y": 30,
                "width": 100,
                "height": 20,
                "text": "This label is far too long to ever fit inside that little box",
                "fontSize": 16,
                "fontFamily": 3,
                "lineHeight": 1.25,
            },
        ]
        report = geometry.analyze_excalidraw(elements)
        overflow_containers = {item["containerId"] for item in report["text_overflows"]}
        self.assertIn("box", overflow_containers)

    def test_oversized_container_flagged_for_empty_space(self) -> None:
        # A leaf content box far larger than the tiny text it holds -> wasted space.
        elements = [
            {
                "id": "roomy",
                "type": "rectangle",
                "x": 0,
                "y": 0,
                "width": 420,
                "height": 320,
            },
            {
                "id": "tiny",
                "type": "text",
                "x": 20,
                "y": 20,
                "width": 60,
                "height": 20,
                "text": "Hi",
                "fontSize": 16,
                "fontFamily": 3,
                "lineHeight": 1.25,
                "containerId": "roomy",
            },
        ]
        report = geometry.analyze_excalidraw(elements)
        oversized = {item["containerId"] for item in report["oversized_containers"]}
        self.assertIn("roomy", oversized)

    def test_oversized_flagged_even_when_panel_holds_a_child_shape(self) -> None:
        # Full-width row: content (a chip) crammed on the left, big empty gutter
        # on the right. The old check skipped any panel enclosing a child shape.
        elements = [
            {"id": "row", "type": "rectangle", "x": 0, "y": 0, "width": 1000, "height": 80},
            {"id": "chip", "type": "rectangle", "x": 20, "y": 25, "width": 220, "height": 30},
        ]
        report = geometry.analyze_excalidraw(elements)
        oversized = {item["containerId"] for item in report["oversized_containers"]}
        self.assertIn("row", oversized)

    def test_cramped_flagged_when_padding_below_text_too_small(self) -> None:
        elements = [
            {"id": "box", "type": "rectangle", "x": 0, "y": 0, "width": 120, "height": 40},
            {
                "id": "lbl",
                "type": "text",
                "x": 20,
                "y": 16,
                "width": 40,
                "height": 20,
                "text": "Hi",
                "fontSize": 16,
                "fontFamily": 3,
                "lineHeight": 1.25,
            },
        ]
        report = geometry.analyze_excalidraw(elements)
        cramped = {item["containerId"] for item in report["cramped_containers"]}
        self.assertIn("box", cramped)

    def test_well_proportioned_box_is_clean(self) -> None:
        measurement = geometry.measure_text_block("Hello world", 3, 16, padding_x=0, padding_y=0)
        pad = 12
        elements = [
            {
                "id": "box",
                "type": "rectangle",
                "x": 0,
                "y": 0,
                "width": measurement.text_width + pad * 2,
                "height": measurement.text_height + pad * 2,
            },
            {
                "id": "lbl",
                "type": "text",
                "x": pad,
                "y": pad,
                "width": measurement.text_width,
                "height": measurement.text_height,
                "text": "Hello world",
                "fontSize": 16,
                "fontFamily": 3,
                "lineHeight": 1.25,
            },
        ]
        report = geometry.analyze_excalidraw(elements)
        self.assertEqual(report["oversized_containers"], [])
        self.assertEqual(report["cramped_containers"], [])

    def test_snug_chip_hugging_its_own_label_is_not_cramped(self) -> None:
        # A pill/chip that tightly wraps its own bound label is correct, not cramped.
        measurement = geometry.measure_text_block("inflate", 3, 12, padding_x=0, padding_y=0)
        elements = [
            {
                "id": "chip",
                "type": "rectangle",
                "x": 0,
                "y": 0,
                "width": measurement.text_width + 8,
                "height": measurement.text_height + 8,
            },
            {
                "id": "chiptext",
                "type": "text",
                "x": 4,
                "y": 4,
                "width": measurement.text_width,
                "height": measurement.text_height,
                "text": "inflate",
                "fontSize": 12,
                "fontFamily": 3,
                "lineHeight": 1.25,
                "containerId": "chip",
            },
        ]
        report = geometry.analyze_excalidraw(elements)
        cramped = {item["containerId"] for item in report["cramped_containers"]}
        self.assertNotIn("chip", cramped)

    def test_grouping_issue_flagged_for_ungrouped_cluster(self) -> None:
        elements = [
            {"id": "panel", "type": "rectangle", "x": 0, "y": 0, "width": 300, "height": 200, "groupIds": []},
            {"id": "inner", "type": "rectangle", "x": 20, "y": 20, "width": 100, "height": 50, "groupIds": []},
        ]
        report = geometry.analyze_excalidraw(elements)
        panels = {item["containerId"] for item in report["grouping_issues"]}
        self.assertIn("panel", panels)

    def test_grouped_cluster_is_clean(self) -> None:
        elements = [
            {"id": "panel", "type": "rectangle", "x": 0, "y": 0, "width": 300, "height": 200, "groupIds": ["g1"]},
            {"id": "inner", "type": "rectangle", "x": 20, "y": 20, "width": 100, "height": 50, "groupIds": ["g1"]},
        ]
        report = geometry.analyze_excalidraw(elements)
        self.assertEqual(report["grouping_issues"], [])


if __name__ == "__main__":
    unittest.main()
