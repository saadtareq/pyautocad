#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    pyautocad.utils
    ~~~~~~~~~~~~~~~

    Utility functions for work with texts, tables, etc.

    :copyright: (c) 2012 by Roman Haritonov.
    :license: BSD, see LICENSE.txt for more details.
"""
from __future__ import print_function

import sys
import re
import time
from contextlib import contextmanager


def unformat_mtext(s, exclude_list=('P', 'S')):
    """Returns string with removed format information

    :param s: string with multitext
    :param exclude_list: don't touch tags from this list. Default ('P', 'S') for
                         newline and fractions

    ::

        >>> text = ur'{\\fGOST type A|b0|i0|c204|p34;TEST\\fGOST type A|b0|i0|c0|p34;123}'
        >>> unformat_mtext(text)
        u'TEST123'

    """
    s = re.sub(r'\{?\\[^%s][^;]+;' % ''.join(exclude_list), '', s)
    s = re.sub(r'\}', '', s)
    return s



def mtext_to_string(s):
    """
    Returns string with removed format innformation as :func:`unformat_mtext` and
    `\\P` (paragraphs) replaced with newlines

    ::

        >>> text = ur'{\\fGOST type A|b0|i0|c204|p34;TEST\\fGOST type A|b0|i0|c0|p34;123}\\Ptest321'
        >>> mtext_to_string(text)
        u'TEST123\\ntest321'

    """

    return unformat_mtext(s).replace(u'\\P', u'\n')


def string_to_mtext(s):
    """Returns string in Autocad multitext format

    Replaces newllines `\\\\n` with `\\\\P`, etc.
    """
    return s.replace('\\', '\\\\').replace(u'\n', u'\P')


def text_width(text_item):
    """Returns width of Autocad `Text` or `MultiText` object
    """
    bbox_min, bbox_max = text_item.GetBoundingbox()
    return bbox_max[0] - bbox_min[0]


@contextmanager
def suppressed_regeneration_of(table):
    """ .. versionadded:: 0.1.2

    Context manager. Suppresses table regeneration to dramatically speedup table operations

    :param table: table object

    ::

        with suppressed_regeneration_of(table):
            populate(table)  # or change its properties

    """
    # TODO: find the way to suppress regeneration of other objects
    table.RegenerateTableSuppressed = True
    try:
        yield
    finally:
        table.RegenerateTableSuppressed = False

@contextmanager
def timing(message=u'Elapsed'):
    """ Context manager for timing execution

    :param message: message to print

    Usage::

        with timing('some operation'):
            do_some_actions()

    Will print::

        some operation: 1.000 s  # where 1.000 is actual execution time

    """
    begin = time.time()
    try:
        yield begin
    finally:
        elapsed = (time.time() - begin)
        print(u'%s: %.3f s' % (message, elapsed))


def dynamic_print(text):
    """Prints text dynamically in one line

    Used for printing something like animations, or progress
    """
    sys.stdout.write('\r%s' % text)
    sys.stdout.flush()

def insert_block(doc, block_name, insertion_point, scale=1.0, rotation=0.0):
    """Inserts a block reference into the drawing."""
    block = doc.Blocks.Item(block_name)
    return doc.ModelSpace.InsertBlock(insertion_point, block_name, scale, scale, scale, rotation)


def ensure_layer(doc, layer_name, color_index=256):
    """Creates a layer if it doesn't exist."""
    layers = doc.Layers
    if not layers.Item(layer_name):
        layer = layers.Add(layer_name)
        layer.Color = color_index
    return layers.Item(layer_name)

def create_text(doc, text_string, insertion_point, height=2.5, rotation=0.0):
    """Creates a single-line text object."""
    text_obj = doc.ModelSpace.AddText(text_string, insertion_point, height)
    text_obj.Rotation = rotation
    return text_obj

def create_polyline(doc, points, closed=True):
    """Creates a polyline from a list of (x, y, z) tuples."""
    pline = doc.ModelSpace.AddPolyline(points)
    if closed:
        pline.Closed = True
    return pline

def get_bounding_box(entity):
    """Returns the bounding box of an entity as (min_point, max_point)."""
    return entity.GetBoundingbox()

def filter_entities(doc, entity_type):
    """Returns a list of entities of a specific type from ModelSpace."""
    return [e for e in doc.ModelSpace if e.ObjectName.endswith(entity_type)]

def delete_entities_by_layer(doc, layer_name):
    """Deletes all entities on a specified layer."""
    for entity in doc.ModelSpace:
        if entity.Layer == layer_name:
            entity.Delete()




