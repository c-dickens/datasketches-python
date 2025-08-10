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
from datasketches import bloom_filter

class BloomFilterTest(unittest.TestCase):
    def test_bloom_filter_accuracy_constructor(self):
        # Test the accuracy-based constructor (max_distinct_items, target_false_positive_prob, seed)
        max_distinct_items = 1000
        target_false_positive_prob = 0.01
        
        # Create bloom filter using accuracy parameters
        bf = bloom_filter.create_by_accuracy(max_distinct_items, target_false_positive_prob)
        self.assertTrue(bf.is_empty())
        
        # Add some items
        test_items = ["item1", "item2", "item3", "item4", "item5"]
        for item in test_items:
            bf.update(item)
        
        self.assertFalse(bf.is_empty())
        
        # Query items that were added
        for item in test_items:
            self.assertTrue(bf.query(item))
        
        # Query items that were not added (should mostly return False, but may have false positives)
        non_existent_items = ["not_item1", "not_item2", "not_item3"]
        for item in non_existent_items:
            # We can't assert False here due to false positive possibility
            # Just verify the method works
            result = bf.query(item)
            self.assertIsInstance(result, bool)

    def test_bloom_filter_size_constructor(self):
        # Test the size-based constructor (num_bits, num_hashes, seed)
        num_bits = 8192  # 8KB in bits
        num_hashes = 5
        
        # Create bloom filter using size parameters
        bf = bloom_filter.create_by_size(num_bits, num_hashes)
        self.assertTrue(bf.is_empty())
        
        # Add some items
        test_items = ["item1", "item2", "item3"]
        for item in test_items:
            bf.update(item)
        
        self.assertFalse(bf.is_empty())
        
        # Query items that were added
        for item in test_items:
            self.assertTrue(bf.query(item))

    def test_bloom_filter_static_methods(self):
        # Test the static helper methods
        max_distinct_items = 1000
        target_false_positive_prob = 0.01
        
        # Test suggest_num_hashes_by_probability
        num_hashes = bloom_filter.suggest_num_hashes_by_probability(target_false_positive_prob)
        self.assertIsInstance(num_hashes, int)
        self.assertGreater(num_hashes, 0)
        
        # Test suggest_num_filter_bits
        num_bits = bloom_filter.suggest_num_filter_bits(max_distinct_items, target_false_positive_prob)
        self.assertIsInstance(num_bits, int)
        self.assertGreater(num_bits, 0)
        
        # Test suggest_num_hashes with both parameters
        num_hashes_alt = bloom_filter.suggest_num_hashes(max_distinct_items, num_bits)
        self.assertIsInstance(num_hashes_alt, int)
        self.assertGreater(num_hashes_alt, 0)

    def test_bloom_filter_serialization(self):
        # Test serialization and deserialization
        bf = bloom_filter.create_by_accuracy(1000, 0.01)
        
        # Add some items
        test_items = ["item1", "item2", "item3"]
        for item in test_items:
            bf.update(item)
        
        # Serialize
        bf_bytes = bf.serialize()
        self.assertEqual(bf.get_serialized_size_bytes(), len(bf_bytes))
        
        # Deserialize
        new_bf = bloom_filter.deserialize(bf_bytes)
        
        # Verify the deserialized filter has the same behavior
        for item in test_items:
            self.assertTrue(new_bf.query(item))
        
        # Verify it's not empty
        self.assertFalse(new_bf.is_empty())

if __name__ == '__main__':
    unittest.main() 