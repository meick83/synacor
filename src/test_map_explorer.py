import map_explorer
import unittest

class MapExplorerTest(unittest.TestCase):

    def test_search_room(self):
        mex = map_explorer.MapExplorer()
        mex.search_room()
        self.assertEqual(mex.current_room.name, "Foothills") 
        self.assertListEqual(mex.current_room.items, ["tablet"])
        self.assertDictEqual(mex.current_room.exits, {"doorway": None, "south": None})

    def test_process_findings(self):
        mex = map_explorer.MapExplorer()
        mex.search_room()
        mex.process_findings()
        self.assertSetEqual(mex.rooms, {mex.current_room})
        self.assertEqual(len(mex.search_stack), 2)

    def test_next_room(self):
        mex = map_explorer.MapExplorer()
        mex.search_room()
        mex.process_findings()
        mex.next_room()
        mex.search_room()
        self.assertEqual(mex.current_room.name, "Foothills") 
        self.assertTrue(mex.current_room.description[1].startswith("As you begin to leave"))
        self.assertFalse(mex.already_visited())

    def test_search_step(self):
        mex = map_explorer.MapExplorer()
        self.assertTrue(mex.search_step())
        self.assertTrue(mex.search_step())
        self.assertTrue(mex.search_step())
        self.assertEqual(len(mex.rooms), 2)

    def test_write_dot(self):
        mex = map_explorer.MapExplorer()
        self.assertTrue(mex.search_step())
        self.assertTrue(mex.search_step())
        self.assertTrue(mex.search_step())
        mex.write_dot("test_map.dot")

    def test_loop_break(self):
        mex = map_explorer.MapExplorer()
        mex.explore(4)
        self.assertEqual(len(mex.search_stack), 1)

    def test_initial_explore(self):
        mex = map_explorer.MapExplorer("after_selftest")
        mex.explore(35)
        mex.write_map("init_map")
        mex.write_item_list("init_items.txt")

    def test_explore_with_tablet(self):
        mex = map_explorer.MapExplorer("after_tablet_use")
        mex.explore(35, item_to_find="empty lantern")
        mex.write_map("tablet_map")
        mex.write_item_list("tablet_items.txt")
        mex.take_item("empty lantern")
        mex.save_state("after_lantern_taken")

    def test_explore_with_empty_lantern(self):
        mex = map_explorer.MapExplorer("after_lantern_taken")
        mex.explore(35, item_to_find="can")
        mex.take_item("can")
        mex.use_item("can")
        mex.use_item("lantern")
        mex.write_map("lantern_map")
        mex.write_item_list("lantern_items.txt")
        mex.save_state("after_lantern_filled")

    def test_explore_with_filled_lantern(self):
        mex = map_explorer.MapExplorer("after_lantern_filled")
        mex.explore(100)
        mex.write_map("filled_lantern_map")
        mex.write_item_list("filled_lantern_items.txt")



if __name__ == '__main__':
    unittest.main()
