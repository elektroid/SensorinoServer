#!/usr/bin/python

import random
import unittest
import common
import coreEngine
import sensorino

class TestX(unittest.TestCase):


    # assertEqual(a, b)   a == b   
    # assertNotEqual(a, b)    a != b   
    # assertTrue(x)   bool(x) is True      
    # assertFalse(x)  bool(x) is False     
    # assertIs(a, b)  a is b  2.7
    # assertIsNot(a, b)   a is not b  2.7
    # assertIsNone(x)     x is None   2.7
    # assertIsNotNone(x)  x is not None   2.7
    # assertIn(a, b)  a in b  2.7
    # assertNotIn(a, b)   a not in b  2.7
    # assertIsInstance(a, b)  isinstance(a, b)    2.7
    # assertNotIsInstance(a, b)   not isinstance(a, b)    2.7
    # assertRaises(SomeException)
    # self.assertRaisesRegexp(ValueError, "invalid literal for.*XYZ'$", int, 'XYZ')


    def setUp(self):
        common.Config.setConfigFile("sensorino_unittests.ini")
        self.engine=coreEngine.Core()

    def test_sensorino_creation_deletion(self):
        self.assertTrue(self.engine.addSensorino(sensorino.Sensorino("tokenSensorino", "1234")))
        self.assertIsNone(self.engine.addSensorino(sensorino.Sensorino("tokenSensorino", "1234")))
        sens=self.engine.findSensorino(address="1234")
        self.assertIsNotNone(sens)
        self.assertTrue(self.engine.delSensorino(sens.sid))

    def test_findMissingSensorino(self):
        self.assertIsNone(self.engine.findSensorino(address="666")
        self.assertIsNone(self.engine.findSensorino(sid="666")

#    def test_createService(self):
        
        

if __name__ == '__main__':
    unittest.main()