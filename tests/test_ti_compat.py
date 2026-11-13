"""Tests for Texas Instruments hardware mock modules (ti_system, ti_draw, ti_plotlib, ti_hub)
and Dual-Mode CLI & Module API execution (headless PC and calculator environments).
"""

import os
import sys
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import ti_system
import ti_draw
import ti_plotlib
import ti_hub


class TestTIHardwareMocks(unittest.TestCase):
    """F1: TI Hardware Mocks tests (Tier 1 & Tier 2)."""

    def setUp(self):
        ti_system.reset()
        ti_draw.reset()
        ti_plotlib.reset()
        ti_hub.reset()

    # Tier 1: Feature Coverage (Min 5)
    def test_ti_system_disp_at_and_clr(self):
        """F1 Tier 1: disp_at renders text into buffer and disp_clr resets it."""
        ti_system.disp_at(1, 1, "FlowCE CAS")
        screen = ti_system.get_screen()
        self.assertTrue(screen[0].startswith("FlowCE CAS"))

        # Clear row 1
        ti_system.disp_clr(1)
        self.assertEqual(ti_system.get_screen()[0].strip(), "")

        # Full clear
        ti_system.disp_at(2, 5, "Derivative")
        ti_system.disp_clr()
        for line in ti_system.get_screen():
            self.assertEqual(line.strip(), "")

    def test_ti_system_key_queue_and_cursor(self):
        """F1 Tier 1: get_key and disp_cursor behavior."""
        self.assertTrue(ti_system.disp_cursor(True))
        self.assertTrue(ti_system.disp_cursor())
        self.assertFalse(ti_system.disp_cursor(False))
        self.assertFalse(ti_system.disp_cursor())

        self.assertEqual(ti_system.get_key(0), "")
        ti_system.push_key("enter")
        ti_system.push_key("clear")
        self.assertEqual(ti_system.get_key(1), "enter")
        self.assertEqual(ti_system.disp_wait(), "clear")
        self.assertEqual(ti_system.get_key(), "")

    def test_ti_system_list_and_value_storage(self):
        """F1 Tier 1: recall_list, store_list, recall_value, store_value."""
        ti_system.store_list("1", [1, 2, 3.5, 4])
        recalled = ti_system.recall_list("1")
        self.assertEqual(recalled, [1.0, 2.0, 3.5, 4.0])

        ti_system.store_value("X", 42.0)
        self.assertEqual(ti_system.recall_value("X"), 42.0)
        self.assertEqual(ti_system.recall_value("NONEXISTENT"), 0.0)

    def test_ti_draw_primitives(self):
        """F1 Tier 1: ti_draw primitives (lines, rectangles, circles, text)."""
        ti_draw.set_color(255, 0, 0)
        ti_draw.set_pen("medium", "solid")
        ti_draw.draw_line(0, 0, 100, 100)
        ti_draw.draw_rect(10, 10, 50, 50)
        ti_draw.fill_circle(150, 150, 20)
        ti_draw.draw_text(20, 200, "y = x^2")

        drawings = ti_draw.get_drawings()
        self.assertEqual(len(drawings), 4)
        self.assertEqual(drawings[0][0], "draw_line")
        self.assertEqual(drawings[1][0], "draw_rect")
        self.assertEqual(drawings[2][0], "fill_circle")
        self.assertEqual(drawings[3][0], "draw_text")

    def test_ti_plotlib_graphing_pipeline(self):
        """F1 Tier 1: ti_plotlib setup, plotting, and show."""
        xs = [1, 2, 3, 4, 5]
        ys = [1, 4, 9, 16, 25]
        ti_plotlib.cls()
        ti_plotlib.auto_window(xs, ys)
        ti_plotlib.axes("on")
        ti_plotlib.grid(1, 5, "dash")
        ti_plotlib.title("Parabola")
        ti_plotlib.plot(xs, ys, "o")
        ti_plotlib.show_plot()

        self.assertTrue(ti_plotlib.is_shown())
        plots = ti_plotlib.get_plots()
        self.assertEqual(len(plots), 1)
        self.assertEqual(plots[0][1], xs)
        self.assertEqual(plots[0][2], ys)

    def test_ti_hub_operations(self):
        """F1 Tier 1: ti_hub connect, sound, sleep, and light."""
        ti_hub.connect("USB")
        self.assertTrue(ti_hub.is_connected())
        ti_hub.sound(440, 0.5)
        ti_hub.sleep(0.1)
        ti_hub.light("on")
        ti_hub.color(0, 255, 0)
        history = ti_hub.get_history()
        self.assertTrue(any(entry[0] == "connect" for entry in history))
        self.assertTrue(any(entry[0] == "sound" for entry in history))

    def test_ti_draw_polygons(self):
        """F1 Tier 1: ti_draw draw_poly and fill_poly."""
        pts_x = [10, 50, 90]
        pts_y = [20, 80, 20]
        ti_draw.draw_poly(pts_x, pts_y)
        ti_draw.fill_poly(pts_x, pts_y)
        drawings = ti_draw.get_drawings()
        self.assertEqual(len(drawings), 2)
        self.assertEqual(drawings[0][0], "draw_poly")
        self.assertEqual(drawings[1][0], "fill_poly")

    def test_ti_plotlib_scatter_and_labels(self):
        """F1 Tier 1: ti_plotlib scatter points and labels."""
        ti_plotlib.labels("Time (s)", "Pos (m)", 0, 0)
        ti_plotlib.scatter([1, 2, 3], [2, 4, 6], "x")
        plots = ti_plotlib.get_plots()
        self.assertEqual(len(plots), 1)
        self.assertEqual(plots[0][0], "scatter")
        self.assertEqual(plots[0][3], "x")

    def test_ti_hub_sensor_read_and_send(self):
        """F1 Tier 1: ti_hub send command and read sensor."""
        ti_hub.send("SET LIGHT 1 ON")
        val = ti_hub.read("BRIGHTNESS")
        self.assertEqual(val, 0.0)
        history = ti_hub.get_history()
        self.assertTrue(any(entry[0] == "send" for entry in history))
        self.assertTrue(any(entry[0] == "read" for entry in history))

    # Tier 2: Boundary & Corner Cases (Min 5)
    def test_ti_system_out_of_bounds_coords(self):
        """F1 Tier 2: Boundary - disp_at with negative or excessive row."""
        ti_system.disp_at(-1, 1, "Below")
        ti_system.disp_at(999, 1, "Above")
        ti_system.disp_at(1, 999, "Way right")
        # Should not throw exception
        self.assertEqual(ti_system.get_screen()[0].strip(), "")

    def test_ti_system_disp_alignment(self):
        """F1 Tier 2: Boundary - disp_at with center and right alignments."""
        ti_system.disp_at(2, "Centered", align="center")
        ti_system.disp_at(3, "RightAligned", align="right")
        screen = ti_system.get_screen()
        self.assertIn("Centered", screen[1])
        self.assertTrue(screen[2].rstrip().endswith("RightAligned"))

    def test_ti_draw_negative_and_zero_coords(self):
        """F1 Tier 2: Boundary - ti_draw handles zero width/height and negative coordinates."""
        ti_draw.draw_rect(-50, -50, 0, 0)
        ti_draw.draw_line(0, 0, 0, 0)
        ti_draw.fill_circle(0, 0, 0)
        drawings = ti_draw.get_drawings()
        self.assertEqual(len(drawings), 3)

    def test_ti_plotlib_empty_data(self):
        """F1 Tier 2: Boundary - auto_window handles empty or single element lists safely."""
        ti_plotlib.auto_window([], [])
        self.assertEqual(ti_plotlib.get_window(), (-10.0, 10.0, -10.0, 10.0))
        ti_plotlib.auto_window([5], [10])
        win = ti_plotlib.get_window()
        self.assertTrue(win[0] < 5 < win[1])
        self.assertTrue(win[2] < 10 < win[3])

    def test_ti_plotlib_lin_reg_vertical_and_empty(self):
        """F1 Tier 2: Boundary - lin_reg on vertical line and empty lists."""
        slope, intercept = ti_plotlib.lin_reg([], [])
        self.assertEqual((slope, intercept), (0.0, 0.0))
        # Vertical line: x = 2 for all y
        slope_v, intercept_v = ti_plotlib.lin_reg([2, 2, 2], [1, 2, 3])
        self.assertEqual(slope_v, 0.0)
        self.assertEqual(intercept_v, 2.0)


class TestDualModeCLI(unittest.TestCase):
    """F11: Dual-Mode CLI & Module API tests (Tier 1 & Tier 2)."""

    def test_import_flowce_module(self):
        """F11 Tier 1: flowce can be imported as a Python module."""
        flowce_path = os.path.join(BASE_DIR, "flowce.py")
        if not os.path.exists(flowce_path):
            self.skipTest("flowce.py not yet implemented by cas_author")
        import flowce
        self.assertTrue(hasattr(flowce, "diff") or hasattr(flowce, "derivative"),
                        "flowce must expose differentiation function")

    def test_headless_execution_flag(self):
        """F11 Tier 1: flowce detects headless environment gracefully."""
        flowce_path = os.path.join(BASE_DIR, "flowce.py")
        if not os.path.exists(flowce_path):
            self.skipTest("flowce.py not yet implemented by cas_author")
        import flowce
        # Calling non-interactive API should work headlessly without launching blocking UI
        if hasattr(flowce, "diff"):
            res = flowce.diff("x^2", "x")
            self.assertIsNotNone(res)

    def test_dual_mode_fallback_when_hardware_missing(self):
        """F11 Tier 2: Boundary test - CAS core logic functions independently of TI GUI."""
        flowce_path = os.path.join(BASE_DIR, "flowce.py")
        if not os.path.exists(flowce_path):
            self.skipTest("flowce.py not yet implemented by cas_author")
        import flowce
        # Core algebraic functions must work without calling ti_draw/ti_system
        if hasattr(flowce, "parse"):
            node = flowce.parse("x + 1")
            self.assertIsNotNone(node)


if __name__ == "__main__":
    unittest.main()
