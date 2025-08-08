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

  // Start with just one simple function
  m.def("create_bloom_filter", 
         [](uint64_t max_distinct_items, double target_false_positive_prob) {
           return bloom_filter_type::builder::create_by_accuracy(max_distinct_items, target_false_positive_prob);
         },
         nb::arg("max_distinct_items"), nb::arg("target_false_positive_prob"),
         "Creates a Bloom filter with optimal parameters for the given accuracy requirements");

  // Bind the class with minimal methods
  nb::class_<bloom_filter_type>(m, name)
    .def("is_empty", &bloom_filter_type::is_empty,
         "Returns True if the filter has seen no items, otherwise False")
    .def("reset", &bloom_filter_type::reset,
         "Resets the filter to its original empty state")
    .def("update", static_cast<void (bloom_filter_type::*)(const std::string&)>(&bloom_filter_type::update), 
         nb::arg("item"),
         "Updates the filter with the given string")
    .def("query", static_cast<bool (bloom_filter_type::*)(const std::string&) const>(&bloom_filter_type::query), 
         nb::arg("item"),
         "Queries the filter for the given string");
}

void init_bloom_filter(nb::module_ &m) {
  bind_bloom_filter<std::allocator<uint8_t>>(m, "bloom_filter");
} 