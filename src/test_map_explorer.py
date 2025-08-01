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
        self.assertTrue(mex.current_room.description[0].startswith("As you begin to leave"))
        self.assertFalse(mex.already_visited())

    def test_search_step(self):
        mex = map_explorer.MapExplorer()
        mex.search_step()
        mex.search_step()
        mex.search_step()
        self.assertEqual(len(mex.rooms), 2)



if __name__ == '__main__':
    unittest.main()
