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
#include <nanobind/bytes.h>

#include "bloom_filter.hpp"
#include "common_defs.hpp"

namespace nb = nanobind;

template<typename A>
void bind_bloom_filter(nb::module_ &m, const char* name) {
  using namespace datasketches;
  using bloom_filter_type = bloom_filter_alloc<A>;

  // Creation helpers
  m.def(
      "create_bloom_filter",
      [](uint64_t max_distinct_items, double target_false_positive_prob) {
        return bloom_filter_type::builder::create_by_accuracy(max_distinct_items, target_false_positive_prob);
      },
      nb::arg("max_distinct_items"), nb::arg("target_false_positive_prob"),
      "Creates a Bloom filter with optimal parameters for the given accuracy requirements");
  m.def(
      "create_bloom_filter_by_size",
      [](uint64_t num_bits, uint8_t num_hashes) {
        return bloom_filter_type::builder::create_by_size(num_bits, num_hashes);
      },
      nb::arg("num_bits"), nb::arg("num_hashes"),
      "Creates a Bloom filter with explicit size and number of hash functions");

  // Bind the class with expanded methods
  nb::class_<bloom_filter_type>(m, name)
    .def("is_empty", &bloom_filter_type::is_empty,
         "Returns True if the filter has seen no items, otherwise False")
    .def("reset", &bloom_filter_type::reset,
         "Resets the filter to its original empty state")
    .def("update", static_cast<void (bloom_filter_type::*)(const std::string&)>(&bloom_filter_type::update),
         nb::arg("item"),
         "Updates the filter with the given string")
    .def("update", static_cast<void (bloom_filter_type::*)(uint64_t)>(&bloom_filter_type::update),
         nb::arg("item"),
         "Updates the filter with the given 64-bit integer")
    .def("update",
         [](bloom_filter_type& bf, const nb::bytes& bytes) {
           bf.update(bytes.c_str(), bytes.size());
         },
         nb::arg("item"),
         "Updates the filter with the given bytes")
    .def("query", static_cast<bool (bloom_filter_type::*)(const std::string&) const>(&bloom_filter_type::query),
         nb::arg("item"),
         "Queries the filter for the given string")
    .def("query", static_cast<bool (bloom_filter_type::*)(uint64_t) const>(&bloom_filter_type::query),
         nb::arg("item"),
         "Queries the filter for the given 64-bit integer")
    .def("query",
         [](const bloom_filter_type& bf, const nb::bytes& bytes) {
           return bf.query(bytes.c_str(), bytes.size());
         },
         nb::arg("item"),
         "Queries the filter for the given bytes")
    .def("merge", &bloom_filter_type::merge, nb::arg("other"),
         "Merges the provided bloom filter into this one")
    .def("get_serialized_size_bytes", &bloom_filter_type::get_serialized_size_bytes,
         "Returns the size of the serialized filter, in bytes")
    .def(
        "serialize",
        [](const bloom_filter_type& bf) {
          auto bytes = bf.serialize();
          return nb::bytes(reinterpret_cast<const char*>(bytes.data()), bytes.size());
        },
        "Serializes the filter into a bytes object")
    .def_static(
        "deserialize",
        [](const nb::bytes& bytes) {
          return bloom_filter_type::deserialize(bytes.c_str(), bytes.size());
        },
        nb::arg("bytes"),
        "Creates a bloom filter from the provided bytes");
}

void init_bloom_filter(nb::module_ &m) {
  bind_bloom_filter<std::allocator<uint8_t>>(m, "bloom_filter");
}
