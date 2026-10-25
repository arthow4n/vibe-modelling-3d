"""Composable CAD inspection recipes; rendering is never product acceptance."""
from .spec import Camera, Anchor, Region, Frame, Section, Label, Arrow, Highlight, View, Inspection
from .render import render, sheet
from .checks import pair_inspection, motion_inspection

__all__ = ['Camera', 'Anchor', 'Region', 'Frame', 'Section', 'Label', 'Arrow', 'Highlight',
           'View', 'Inspection', 'render', 'sheet', 'pair_inspection', 'motion_inspection']
