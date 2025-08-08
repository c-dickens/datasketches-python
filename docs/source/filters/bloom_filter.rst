Bloom Filter
============

A Bloom filter provides fast probabilistic set membership checks with configurable false
positive probabilities.

Creating and using a Bloom filter::

    from datasketches import create_bloom_filter

    bf = create_bloom_filter(1000, 0.01)
    bf.update("item")
    bf.query("item")

The binding also supports integers and raw bytes as inputs, merging with other filters,
serialization, and creation by explicit size using ``create_bloom_filter_by_size``.
