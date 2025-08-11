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
    def test_standard_constructors(self):
        """Test standard constructors with exact validation."""
        num_items = 4000
        fpp = 0.01

        num_bits = bloom_filter.suggest_num_filter_bits(num_items, fpp)
        num_hashes = bloom_filter.suggest_num_hashes(num_items, num_bits)
        seed = 89023

        bf = bloom_filter.create_by_size(num_bits, num_hashes, seed)
        # C++ rounds up to nearest multiple of 64
        adjusted_num_bits = (num_bits + 63) & ~0x3F
        self.assertEqual(bf.capacity, adjusted_num_bits)
        self.assertEqual(bf.num_hashes, num_hashes)
        self.assertEqual(bf.seed, seed)
        self.assertTrue(bf.is_empty())

        # Should match above
        bf2 = bloom_filter.create_by_accuracy(num_items, fpp, seed)
        self.assertEqual(bf2.capacity, adjusted_num_bits)
        self.assertEqual(bf2.num_hashes, num_hashes)
        self.assertEqual(bf2.seed, seed)
        self.assertTrue(bf2.is_empty())

    def test_basic_operations(self):
        """Test basic operations with validation."""
        num_items = 5000
        fpp = 0.01
        seed = 4897301548054

        bf = bloom_filter.create_by_accuracy(num_items, fpp, seed)
        self.assertTrue(bf.is_empty())
        self.assertEqual(bf.num_bits_used, 0)

        # Add items
        for i in range(num_items):
            bf.update(str(i))

        self.assertFalse(bf.is_empty())
        self.assertGreater(bf.num_bits_used, 0)
        self.assertLessEqual(bf.num_bits_used, bf.capacity)

        # Count false positives
        false_positives = 0
        for i in range(num_items, min(num_items + 1000, bf.capacity)):
            if bf.query(str(i)):
                false_positives += 1
        
        self.assertGreater(false_positives, 0)
        self.assertLess(false_positives, 100)

        # Test serialization
        bf_bytes = bf.serialize()
        self.assertEqual(bf.get_serialized_size_bytes(), len(bf_bytes))

        new_bf = bloom_filter.deserialize(bf_bytes)
        self.assertEqual(bf.capacity, new_bf.capacity)
        self.assertEqual(bf.num_hashes, new_bf.num_hashes)
        self.assertEqual(bf.seed, new_bf.seed)
        self.assertEqual(bf.num_bits_used, new_bf.num_bits_used)

        # Verify all original items are still found
        for i in range(num_items):
            self.assertTrue(new_bf.query(str(i)))

    def test_update_types(self):
        """Test update and query with different data types."""
        bf = bloom_filter.create_by_accuracy(1000, 0.01)

        # Test integers (positive and negative)
        for v in [0, 1, 2**40, -1, -2**40]:
            bf.update(v)
            self.assertTrue(bf.query(v))

        # Test floats
        for v in [0.5, -3.25]:
            bf.update(v)
            self.assertTrue(bf.query(v))

        # Test strings
        bf.update("hello")
        self.assertTrue(bf.query("hello"))

        # Test bytes
        b = b"abc\x00def"
        bf.update(b)
        self.assertTrue(bf.query(b))

    def test_reset_method(self):
        """Test the reset method functionality."""
        bf = bloom_filter.create_by_accuracy(1000, 0.01)
        
        # Initially empty
        self.assertTrue(bf.is_empty())
        self.assertEqual(bf.num_bits_used, 0)
        
        # Add some items
        test_items = ["item1", "item2", "item3", "item4", "item5"]
        for item in test_items:
            bf.update(item)
        
        # Verify items were added
        self.assertFalse(bf.is_empty())
        self.assertGreater(bf.num_bits_used, 0)
        
        for item in test_items:
            self.assertTrue(bf.query(item))
        
        # Reset the filter
        bf.reset()
        
        # Verify filter is back to empty state
        self.assertTrue(bf.is_empty())
        self.assertEqual(bf.num_bits_used, 0)
        
        # Verify none of the original items are found
        for item in test_items:
            self.assertFalse(bf.query(item))
        
        # Verify properties are preserved
        self.assertGreater(bf.capacity, 0)
        self.assertGreater(bf.num_hashes, 0)
        self.assertIsInstance(bf.seed, int)
        
        # Can add new items after reset
        bf.update("new_item")
        self.assertFalse(bf.is_empty())
        self.assertTrue(bf.query("new_item"))

    def test_bloom_filter_accuracy_constructor(self):
        """Test the accuracy-based constructor."""
        max_distinct_items = 1000
        target_false_positive_prob = 0.01
        
        bf = bloom_filter.create_by_accuracy(max_distinct_items, target_false_positive_prob)
        self.assertTrue(bf.is_empty())
        
        test_items = ["item1", "item2", "item3", "item4", "item5"]
        for item in test_items:
            bf.update(item)
        
        self.assertFalse(bf.is_empty())
        
        for item in test_items:
            self.assertTrue(bf.query(item))

    def test_bloom_filter_size_constructor(self):
        """Test the size-based constructor."""
        num_bits = 8192
        num_hashes = 5
        
        bf = bloom_filter.create_by_size(num_bits, num_hashes)
        self.assertTrue(bf.is_empty())
        self.assertEqual(bf.capacity, num_bits)
        self.assertEqual(bf.num_hashes, num_hashes)
        
        test_items = ["item1", "item2", "item3"]
        for item in test_items:
            bf.update(item)
        
        self.assertFalse(bf.is_empty())
        
        for item in test_items:
            self.assertTrue(bf.query(item))

    def test_bloom_filter_static_methods(self):
        """Test the static helper methods."""
        max_distinct_items = 1000
        target_false_positive_prob = 0.01
        
        num_hashes = bloom_filter.suggest_num_hashes_by_probability(target_false_positive_prob)
        self.assertIsInstance(num_hashes, int)
        self.assertGreater(num_hashes, 0)
        
        num_bits = bloom_filter.suggest_num_filter_bits(max_distinct_items, target_false_positive_prob)
        self.assertIsInstance(num_bits, int)
        self.assertGreater(num_bits, 0)
        
        num_hashes_alt = bloom_filter.suggest_num_hashes(max_distinct_items, num_bits)
        self.assertIsInstance(num_hashes_alt, int)
        self.assertGreater(num_hashes_alt, 0)

    def test_bloom_filter_serialization(self):
        """Test serialization and deserialization."""
        bf = bloom_filter.create_by_accuracy(1000, 0.01)
        
        test_items = ["item1", "item2", "item3"]
        for item in test_items:
            bf.update(item)
        
        bf_bytes = bf.serialize()
        self.assertEqual(bf.get_serialized_size_bytes(), len(bf_bytes))
        
        new_bf = bloom_filter.deserialize(bf_bytes)
        
        for item in test_items:
            self.assertTrue(new_bf.query(item))
        
        self.assertFalse(new_bf.is_empty())
        self.assertEqual(bf.capacity, new_bf.capacity)
        self.assertEqual(bf.num_hashes, new_bf.num_hashes)
        self.assertEqual(bf.seed, new_bf.seed)
        self.assertEqual(bf.num_bits_used, new_bf.num_bits_used)

    def test_empty_serialization(self):
        """Test serialization of empty bloom filter."""
        bf = bloom_filter.create_by_accuracy(1000, 0.01)
        self.assertTrue(bf.is_empty())
        
        bf_bytes = bf.serialize()
        self.assertEqual(bf.get_serialized_size_bytes(), len(bf_bytes))
        
        new_bf = bloom_filter.deserialize(bf_bytes)
        self.assertTrue(new_bf.is_empty())
        self.assertEqual(bf.capacity, new_bf.capacity)
        self.assertEqual(bf.num_hashes, new_bf.num_hashes)
        self.assertEqual(bf.seed, new_bf.seed)

    def test_bits_used_properties(self):
        """Test that bits_used behaves correctly."""
        bf = bloom_filter.create_by_accuracy(1000, 0.01)

        self.assertEqual(bf.num_bits_used, 0)

        bf.update("alpha")
        bits1 = bf.num_bits_used
        self.assertIsInstance(bits1, int)
        self.assertGreater(bits1, 0)

        # Idempotent
        bits1_again = bf.num_bits_used
        self.assertEqual(bits1_again, bits1)

        # Same item shouldn't change bits_used
        bf.update("alpha")
        bits_dup = bf.num_bits_used
        self.assertEqual(bits_dup, bits1)

        # Additional items should be non-decreasing
        for s in ["beta", "gamma", "delta"]:
            bf.update(s)
            new_bits = bf.num_bits_used
            self.assertGreaterEqual(new_bits, bits1)
            bits1 = new_bits

    def test_capacity_properties(self):
        """Test that capacity is positive and constant."""
        bf = bloom_filter.create_by_accuracy(1000, 0.01)
        cap1 = bf.capacity
        self.assertIsInstance(cap1, int)
        self.assertGreater(cap1, 0)

        cap2 = bf.capacity
        self.assertEqual(cap1, cap2)

        bf.update("alpha")
        bf.update("beta")
        self.assertEqual(cap1, bf.capacity)

    def test_num_hashes_properties(self):
        """Test that num_hashes is consistent."""
        bf = bloom_filter.create_by_accuracy(1000, 0.01)
        k1 = bf.num_hashes
        self.assertIsInstance(k1, int)
        self.assertGreaterEqual(k1, 1)
        bf.update("alpha")
        self.assertEqual(k1, bf.num_hashes)

        bf2 = bloom_filter.create_by_size(10000, 3)
        k2 = bf2.num_hashes
        self.assertIsInstance(k2, int)
        self.assertEqual(k2, 3)
        bf2.update("beta")
        self.assertEqual(k2, bf2.num_hashes)

    def test_seed_properties(self):
        """Test that seed is consistent."""
        bf = bloom_filter.create_by_accuracy(1000, 0.01)
        s1 = bf.seed
        self.assertIsInstance(s1, int)

        bf.update("alpha")
        self.assertEqual(s1, bf.seed)

        explicit_seed = 12345
        bf2 = bloom_filter.create_by_accuracy(1000, 0.01, explicit_seed)
        s2 = bf2.seed
        self.assertIsInstance(s2, int)
        self.assertEqual(s2, explicit_seed)

    def test_deterministic_behavior(self):
        """Test that bloom filters with the same seed behave deterministically."""
        seed = 12345
        max_distinct_items = 1000
        target_fpp = 0.01
        
        bf1 = bloom_filter.create_by_accuracy(max_distinct_items, target_fpp, seed)
        bf2 = bloom_filter.create_by_accuracy(max_distinct_items, target_fpp, seed)
        
        test_items = [f"item_{i}" for i in range(100)]
        for item in test_items:
            bf1.update(item)
            bf2.update(item)
        
        self.assertEqual(bf1.capacity, bf2.capacity)
        self.assertEqual(bf1.num_hashes, bf2.num_hashes)
        self.assertEqual(bf1.seed, bf2.seed)
        self.assertEqual(bf1.num_bits_used, bf2.num_bits_used)
        
        for item in test_items:
            self.assertEqual(bf1.query(item), bf2.query(item))

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        bf_small = bloom_filter.create_by_size(64, 1)
        self.assertEqual(bf_small.capacity, 64)
        self.assertEqual(bf_small.num_hashes, 1)
        
        bf_many_hashes = bloom_filter.create_by_size(1000, 20)
        self.assertEqual(bf_many_hashes.num_hashes, 20)
        
        bf_low_fpp = bloom_filter.create_by_accuracy(100, 1e-6)
        self.assertGreater(bf_low_fpp.num_hashes, 1)

    def test_mathematical_properties(self):
        """Test mathematical properties of bloom filters."""
        bf = bloom_filter.create_by_size(100, 5)
        self.assertEqual(bf.capacity % 64, 0)
        
        bf.update("test_item")
        self.assertLessEqual(bf.num_bits_used, bf.capacity)
        
        self.assertGreater(bf.num_hashes, 0)
        self.assertIsInstance(bf.seed, int)

    def test_union_operation(self):
        """Test union operation between compatible bloom filters."""
        # Create two compatible bloom filters
        bf1 = bloom_filter.create_by_size(1024, 5, seed=12345)
        bf2 = bloom_filter.create_by_size(1024, 5, seed=12345)
        
        # Verify they are compatible
        self.assertTrue(bf1.is_compatible(bf2))
        self.assertTrue(bf2.is_compatible(bf1))
        
        # Add items to first filter
        items1 = ["item1", "item2", "item3", "item4", "item5"]
        for item in items1:
            bf1.update(item)
        
        # Add different items to second filter
        items2 = ["item6", "item7", "item8", "item9", "item10"]
        for item in items2:
            bf2.update(item)
        
        # Add one common item to both
        common_item = "common_item"
        bf1.update(common_item)
        bf2.update(common_item)
        
        # Record initial state
        initial_bits1 = bf1.num_bits_used
        initial_bits2 = bf2.num_bits_used
        
        # Perform union operation
        bf1.union_with(bf2)
        
        # Verify all items from both filters are now in bf1
        all_items = items1 + items2 + [common_item]
        for item in all_items:
            self.assertTrue(bf1.query(item))
        
        # Verify bits used increased (union should have more bits set)
        self.assertGreaterEqual(bf1.num_bits_used, initial_bits1)
        self.assertGreaterEqual(bf1.num_bits_used, initial_bits2)
        
        # Verify bf2 is unchanged
        for item in items2 + [common_item]:
            self.assertTrue(bf2.query(item))
        for item in items1:
            self.assertFalse(bf2.query(item))

    def test_intersection_operation(self):
        """Test intersection operation between compatible bloom filters."""
        # Create two compatible bloom filters
        bf1 = bloom_filter.create_by_size(1024, 5, seed=12345)
        bf2 = bloom_filter.create_by_size(1024, 5, seed=12345)
        
        # Verify they are compatible
        self.assertTrue(bf1.is_compatible(bf2))
        
        # Add items to first filter
        items1 = ["item1", "item2", "item3", "item4", "item5"]
        for item in items1:
            bf1.update(item)
        
        # Add different items to second filter
        items2 = ["item6", "item7", "item8", "item9", "item10"]
        for item in items2:
            bf2.update(item)
        
        # Add common items to both
        common_items = ["common1", "common2", "common3"]
        for item in common_items:
            bf1.update(item)
            bf2.update(item)
        
        # Record initial state
        initial_bits1 = bf1.num_bits_used
        initial_bits2 = bf2.num_bits_used
        
        # Perform intersection operation
        bf1.intersect(bf2)
        
        # Verify only common items remain in bf1
        for item in common_items:
            self.assertTrue(bf1.query(item))
        
        # Verify items unique to each filter are no longer in bf1
        for item in items1:
            self.assertFalse(bf1.query(item))
        for item in items2:
            self.assertFalse(bf1.query(item))
        
        # Verify bits used decreased (intersection should have fewer bits set)
        self.assertLessEqual(bf1.num_bits_used, initial_bits1)
        
        # Verify bf2 is unchanged
        for item in items2 + common_items:
            self.assertTrue(bf2.query(item))
        for item in items1:
            self.assertFalse(bf2.query(item))

    def test_incompatible_filters(self):
        """Test that union and intersection fail with incompatible filters."""
        # Create filters with different capacities
        bf1 = bloom_filter.create_by_size(1024, 5, seed=12345)
        bf2 = bloom_filter.create_by_size(2048, 5, seed=12345)
        
        self.assertFalse(bf1.is_compatible(bf2))
        self.assertFalse(bf2.is_compatible(bf1))
        
        # Should raise exception for union
        with self.assertRaises(Exception):
            bf1.union_with(bf2)
        
        # Should raise exception for intersection
        with self.assertRaises(Exception):
            bf1.intersect(bf2)
        
        # Create filters with different number of hashes
        bf3 = bloom_filter.create_by_size(1024, 3, seed=12345)
        self.assertFalse(bf1.is_compatible(bf3))
        
        # Create filters with different seeds
        bf4 = bloom_filter.create_by_size(1024, 5, seed=54321)
        self.assertFalse(bf1.is_compatible(bf4))

    def test_union_intersection_edge_cases(self):
        """Test edge cases for union and intersection operations."""
        # Test with empty filters
        bf1 = bloom_filter.create_by_size(1024, 5, seed=12345)
        bf2 = bloom_filter.create_by_size(1024, 5, seed=12345)
        
        # Union of empty filters should remain empty
        bf1.union_with(bf2)
        self.assertTrue(bf1.is_empty())
        self.assertEqual(bf1.num_bits_used, 0)
        
        # Intersection of empty filters should remain empty
        bf1.reset()
        bf1.intersect(bf2)
        self.assertTrue(bf1.is_empty())
        self.assertEqual(bf1.num_bits_used, 0)
        
        # Test union with self
        bf1.update("test_item")
        initial_bits = bf1.num_bits_used
        bf1.union_with(bf1)
        self.assertEqual(bf1.num_bits_used, initial_bits)
        self.assertTrue(bf1.query("test_item"))
        
        # Test intersection with self
        bf1.intersect(bf1)
        self.assertEqual(bf1.num_bits_used, initial_bits)
        self.assertTrue(bf1.query("test_item"))

if __name__ == '__main__':
    unittest.main() 