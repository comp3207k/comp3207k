


import unittest

import importer_cineworld

class TestCineWorldImporter(unittest.TestCase):
    
    def setUp(self):
        self.i = importer_cineworld.CineWorldImporter()
    
    def test__get_dom(self):
        d = self.i._get_dom(self.i.BASE_URL + self.i.CINEMAS)
        self.assertEqual(d.childNodes[0].localName, 'cinemas')
    
    def test__get_cinemas(self):
        c, f = self.i._get_cinemas()
        
        self.assertTrue(len(c) > 0)
        self.assertTrue('name' in c[0].keys())
        self.assertTrue('address' in c[0].keys())
        self.assertTrue('url' in c[0].keys())
        self.assertTrue('api_id' in c[0].keys())
        self.assertTrue('films' in c[0].keys())
        self.assertTrue(type(c[0]['films'][0]) == dict)
        
        self.assertTrue(len(f) > 0)
        self.assertTrue('name' in f[0].keys())
        self.assertTrue('rating' in f[0].keys())
        self.assertTrue('director' in f[0].keys())



if __name__ == '__main__':
    unittest.main()

