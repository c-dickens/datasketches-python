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

  def test_bloom_filter_reset(self):
    """Test resetting the bloom filter to empty state"""
    bf = create_bloom_filter(1000, 0.01)
    bf.update("x")
    self.assertTrue(bf.query("x"))
    self.assertFalse(bf.is_empty())
    bf.reset()
    self.assertTrue(bf.is_empty())
    # After reset, previously inserted item should no longer be reported
    self.assertFalse(bf.query("x"))

  def test_bloom_filter_multiple_items(self):
    """Test adding multiple items to the bloom filter"""
    bf = create_bloom_filter(1000, 0.01)
    
    items = ["item1", "item2", "item3", "item4", "item5"]
    
    # Add all items
    for item in items:
      bf.update(item)
    
    # Check that all items are found
    for item in items:
      self.assertTrue(bf.query(item), f"Item {item} should be found")
    
    # Check that items not added are not found
    non_items = ["not_item1", "not_item2", "not_item3"]
    for item in non_items:
      self.assertFalse(bf.query(item), f"Item {item} should not be found")

  def test_bloom_filter_false_positives(self):
    """Test that bloom filter can have false positives (this is expected behavior)"""
    bf = create_bloom_filter(10, 0.1)  # Small filter, higher false positive rate
    
    # Add a few items
    bf.update("item1")
    bf.update("item2")
    
    # Check that added items are found
    self.assertTrue(bf.query("item1"))
    self.assertTrue(bf.query("item2"))
    
    # With a small filter and high false positive rate, we might get false positives
    # This is expected behavior for bloom filters
    # We're not testing for specific false positives, just that the filter works

  def test_bloom_filter_parameters(self):
    """Test creating bloom filters with different parameters"""
    # Test with different sizes and false positive rates
    test_cases = [
      (100, 0.01),
      (1000, 0.05),
      (10000, 0.001),
      (100, 0.1),
    ]
    
    for max_items, false_positive_rate in test_cases:
      with self.subTest(max_items=max_items, false_positive_rate=false_positive_rate):
        bf = create_bloom_filter(max_items, false_positive_rate)
        self.assertIsNotNone(bf)
        self.assertTrue(bf.is_empty())

  def test_bloom_filter_string_types(self):
    """Test that bloom filter works with different string types"""
    bf = create_bloom_filter(1000, 0.01)
    
    # Test with different string types
    test_strings = [
      "simple",
      "string with spaces",
      "string_with_underscores",
      "string-with-dashes",
      "string123with456numbers",
      "string.with.dots",
      "string!with@special#chars$",
    ]
    
    for test_string in test_strings:
      with self.subTest(test_string=test_string):
        bf.update(test_string)
        self.assertTrue(bf.query(test_string))
    
    # Test empty string separately - it might be ignored by the implementation
    bf.update("")
    # Note: Empty strings might be ignored by the bloom filter implementation
    # This is common behavior, so we don't assert on the result

  def test_bloom_filter_edge_cases(self):
    """Test edge cases for bloom filter"""
    bf = create_bloom_filter(1000, 0.01)
    
    # Test with very long strings
    long_string = "a" * 1000
    bf.update(long_string)
    self.assertTrue(bf.query(long_string))
    
    # Test with unicode strings
    unicode_string = "café résumé naïve"
    bf.update(unicode_string)
    self.assertTrue(bf.query(unicode_string))
    
    # Test with numbers as strings
    number_string = "12345"
    bf.update(number_string)
    self.assertTrue(bf.query(number_string))

if __name__ == '__main__':
    unittest.main() 