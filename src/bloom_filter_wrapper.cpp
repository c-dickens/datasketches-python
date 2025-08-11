/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>

#include "bloom_filter.hpp"
#include "common_defs.hpp"

namespace nb = nanobind;

template<typename A>
void bind_bloom_filter(nb::module_ &m, const char* name) {
  using namespace datasketches;
  using bloom_filter_type = bloom_filter_alloc<A>;

  // Bind the class with static factory methods only
  nb::class_<bloom_filter_type>(m, name)
    .def("is_empty", &bloom_filter_type::is_empty,
         "Returns True if the filter has seen no items, otherwise False")
    .def("update", static_cast<void (bloom_filter_type::*)(const std::string&)>(&bloom_filter_type::update), 
         nb::arg("item"),
         "Updates the filter with the given string")
    .def("query", static_cast<bool (bloom_filter_type::*)(const std::string&) const>(&bloom_filter_type::query), 
         nb::arg("item"),
         "Queries the filter for the given string")
    .def("reset", &bloom_filter_type::reset,
         "Resets the Bloom filter to its original empty state")
    .def("get_serialized_size_bytes", 
         [](const bloom_filter_type& sk) { return sk.get_serialized_size_bytes(); },
         "Returns the size in bytes of the serialized image of the filter")
    .def("serialize",
        [](const bloom_filter_type& sk) {
            auto v = sk.serialize(); // vector_bytes (std::vector<uint8_t, Allocator>)
            return nb::bytes(reinterpret_cast<const char*>(v.data()), v.size());
        },
        "Serialize the filter to a cross-language compatible byte string")
    .def_static(
        "deserialize",
        [](const nb::bytes& bytes) {
            return bloom_filter_type::deserialize(bytes.c_str(), bytes.size());
        },
        nb::arg("bytes"),
        "Reads a bytes object and returns the corresponding bloom_filter")
    .def_static("suggest_num_hashes", 
                static_cast<uint16_t (*)(uint64_t, uint64_t)>(&bloom_filter_type::builder::suggest_num_hashes),
                nb::arg("max_distinct_items"), nb::arg("num_filter_bits"),
                "Suggests the optimal number of hash functions for given target numbers of distinct items and filter size")
    .def_static("suggest_num_hashes_by_probability", 
                static_cast<uint16_t (*)(double)>(&bloom_filter_type::builder::suggest_num_hashes),
                nb::arg("target_false_positive_prob"),
                "Suggests the optimal number of hash functions to achieve a target false positive probability")
    .def_static("suggest_num_filter_bits", 
                &bloom_filter_type::builder::suggest_num_filter_bits,
                nb::arg("max_distinct_items"), nb::arg("target_false_positive_prob"),
                "Suggests the optimal number of bits for given target numbers of distinct items and false positive probability")
    .def_static("create_by_accuracy",
                [](uint64_t max_distinct_items, double target_false_positive_prob, uint64_t seed) {
                  return bloom_filter_type::builder::create_by_accuracy(max_distinct_items, target_false_positive_prob, seed);
                },
                nb::arg("max_distinct_items"), nb::arg("target_false_positive_prob"), nb::arg("seed")=bloom_filter_type::builder::generate_random_seed(),
                "Creates a Bloom filter with optimal parameters for the given accuracy requirements\n\n"
                ":param max_distinct_items: Maximum expected number of distinct items to add to the filter\n:type max_distinct_items: int\n"
                ":param target_false_positive_prob: Desired false positive probability per item\n:type target_false_positive_prob: float\n"
                ":param seed: Hash seed to use (default: random)\n:type seed: int, optional"
                )
    .def_static("create_by_size",
                [](uint64_t num_bits, uint16_t num_hashes, uint64_t seed) {
                  return bloom_filter_type::builder::create_by_size(num_bits, num_hashes, seed);
                },
                nb::arg("num_bits"), nb::arg("num_hashes"), nb::arg("seed")=bloom_filter_type::builder::generate_random_seed(),
                "Creates a Bloom filter with specified size parameters\n\n"
                ":param num_bits: Size of the Bloom filter in bits\n:type num_bits: int\n"
                ":param num_hashes: Number of hash functions to apply to items\n:type num_hashes: int\n"
                ":param seed: Hash seed to use (default: random)\n:type seed: int, optional"
                )
    .def_prop_ro(
        "num_bits_used",
        &bloom_filter_type::get_bits_used,
        "Number of bits set to 1 in the Bloom filter"
        )
    .def_prop_ro(
        "capacity",
        &bloom_filter_type::get_capacity,
        "Number of bits in the Bloom filter's bit array"
        )
    .def_prop_ro(
        "num_hashes",
        &bloom_filter_type::get_num_hashes,
        "Number of hash functions used by this Bloom filter"
        )
    .def_prop_ro(
        "seed",
        &bloom_filter_type::get_seed,
        "Hash seed used by this Bloom filter"
        );
}

void init_bloom_filter(nb::module_ &m) {
  bind_bloom_filter<std::allocator<uint8_t>>(m, "bloom_filter");
} 