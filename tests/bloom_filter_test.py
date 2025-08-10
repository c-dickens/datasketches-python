# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
  
import unittest
from datasketches import create_bloom_filter

class BloomFilterTest(unittest.TestCase):
  def test_create_bloom_filter(self):
    """Test that we can create a bloom filter with basic parameters"""
    bf = create_bloom_filter(1000, 0.01)
    self.assertIsNotNone(bf)
    self.assertTrue(bf.is_empty())

  def test_bloom_filter_empty_state(self):
    """Test that newly created bloom filter is empty"""
    bf = create_bloom_filter(100, 0.05)
    self.assertTrue(bf.is_empty())

  def test_bloom_filter_update_and_query(self):
    """Test basic update and query functionality"""
    bf = create_bloom_filter(1000, 0.01)
    
    # Initially empty
    self.assertTrue(bf.is_empty())
    self.assertFalse(bf.query("test_item"))
    
    # Add an item
    bf.update("test_item")
    self.assertFalse(bf.is_empty())
    self.assertTrue(bf.query("test_item"))
    
    # Query for item not in filter
    self.assertFalse(bf.query("other_item"))

  def test_bloom_filter_serialize_deserialize(self):
    """Test that we can serialize a bloom filter and restore it afterwards"""
    bf = create_bloom_filter(1000, 0.01)
    bf.update("test_item")
    serialized = bf.serialize()
    self.assertIsNotNone(serialized)
    self.assertTrue(len(serialized) > 0)

    bf = create_bloom_filter(1000, 0.01)
    items = ["alpha", "beta", "gamma"]
    for it in items:
        bf.update(it)

    payload = bf.serialize()
    self.assertTrue(len(payload) > 0)

    restored = bf.deserialize(payload)
    self.assertFalse(restored.is_empty())

    # Inserted items should come back as "might be present" (very high probability true)
    for it in items:
        self.assertTrue(restored.query(it), f"Expected present after round-trip: {it}")

    # A not-inserted key should usually be absent (Bloom could FP, but unlikely here)
    self.assertFalse(restored.query("not_inserted"))


if __name__ == '__main__':
    unittest.main() 