# Test routines for the simpleline framework
#
# Copyright (C) (2012)  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.  Any Red Hat trademarks that are incorporated in the
# source code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission of
# Red Hat, Inc.
#
# Red Hat Author(s): Martin Sivak <msivak@redhat.com>
#
import base
import unittest

### dummy translation
def _(t):
    return t
__builtins__._ = _


class DummyScreen(base.UIScreen):
    def refresh(self, args):
        self._window = []
        return True

class TestApp(base.App):
    def __init__(self, *args, **kwargs):
        self.simulate_input = []
        base.App.__init__(self, *args, **kwargs)

    def simulate(self, input):
        self.simulate_input.append(input)

    def raw_input(self, prompt):
        if not self.simulate_input:
            raise Exception("No further input, the app probably failed the test")
        return self.simulate_input.pop(0)

class OKException(Exception):
    pass

def raiseOK():
    raise OKException()

class AppTests(unittest.TestCase):
    def setUp(self):
        self.app = TestApp("title")
        self.screen = DummyScreen(self.app)

    def test_schedule_adds_to_beginning_when_empty(self):
        self.app.schedule_screen(base.UIScreen(self.app))
        assert len(self.app._screens) == 1

    def test_schedule_adds_to_beginning_when_not_empty(self):
        self.app.schedule_screen(None)
        self.app.schedule_screen(base.UIScreen(self.app))
        assert len(self.app._screens) == 2
        assert self.app._screens[0][0] is not None

    def test_modal_starts_mainloop(self):
        self.app._mainloop = raiseOK
        self.assertRaises(OKException, self.app.switch_screen_modal, (self.screen,))

    def test_exits_modal_screen(self):
        self.app.simulate("c")
        self.app.switch_screen_modal(self.screen)

class WidgetTests(unittest.TestCase):
    TEXT = u"test1\ntesting line\nte"
    BLOCK = u"xxy\nxxx\nxxx"
    BLOCK_TEXT = u"test1xxy\ntestixxxline\nte   xxx"

    def setUp(self):
        self.widget = base.Widget(default = self.TEXT)

    def test_height(self):
        self.assertEquals(self.widget.height, 3)

    def test_width(self):
        self.assertEquals(self.widget.width, 12)

    def test_clear(self):
        self.widget.clear()
        self.assertEquals(self.widget.content, [])
        self.assertEquals(self.widget.cursor, (0, 0))

    def test_rendering(self):
        self.assertEqual(unicode(self.widget), self.TEXT)

    def test_draw(self):
        target = base.Widget()
        target.draw(self.widget)
        self.assertEqual(unicode(target), self.TEXT)

    def test_write(self):
        self.widget.clear()
        self.widget.write(self.TEXT)
        self.assertEqual(unicode(self.widget), self.TEXT)

    def test_block_write(self):
        self.widget.setxy(0, 5)
        self.widget.write(self.BLOCK, block = True)
        self.assertEqual(unicode(self.widget), self.BLOCK_TEXT)

    def test_block_draw(self):
        source = base.Widget()
        source.write(self.BLOCK)
        self.widget.draw(source, row = 0, col = 5)
        self.assertEqual(unicode(self.widget), self.BLOCK_TEXT)


if __name__ == '__main__':
    unittest.main()