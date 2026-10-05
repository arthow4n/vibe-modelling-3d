"""Named Q1/Q1F configurations using authoritative, unchanged part builders.

Assembly frame: base floor Z0, module centred on X/Y0; opening is world +Z.
References are analysis-only subsets/envelopes, never printable components.
No native constraint solve is needed for these prescribed rigid placements.
"""
import cadquery as cq
from assembly_geometry import Configuration
import quiet_q1_flush as default_model
import archive_corner_proposals as old_archive
import cap_j4_base_5 as old_display


def fixture(name, components, *, kind='intermediate', parameters=None):
    """Object-owned analysis fixture; callers declare each proxy's meaning."""
    assembly = cq.Assembly(name='quiet_fixture')
    for label, shape in components.items():
        assembly.add(shape, name=label)
    return Configuration.explicit(assembly, name=name, kind=kind, parameters=parameters)


class QuietAssembly:
    """One evaluation's actual parts, shared by checks, poses and inspection.

    Keep distinct candidate builders in distinct instances. This is local geometry
    reuse, not a persistent cache or a second component/constraint representation.
    """
    def __init__(self, model=default_model):
        self.model = model
        self.base = model.base().val()
        self.insert = model.jacket().val()
        self.hood = model.hood().val()
        self._cards = None
        self._guides = None
        self._neighbours = {}

    @property
    def cards(self):
        if self._cards is None:
            self._cards = [part.val() for part in self.model.cards()]
        return self._cards

    @property
    def guides(self):
        """Actual insert builder with retention beads omitted; analysis only."""
        if self._guides is None:
            self._guides = self.model.jacket(include_beads=False).val()
        return self._guides

    def operating(self, *, lift_mm=0, offset_xy=(0, 0), include_cards=False):
        q = self.model
        assembly = (cq.Assembly(name='quiet_box').add(self.base, name='base')
                    .add(self.insert, name='insert').add(self.hood, name='hood',
                        loc=cq.Location((*offset_xy, lift_mm))))
        if include_cards:
            cards = cq.Assembly(name='cards')
            for i, card in enumerate(self.cards):
                cards.add(card, name=f'card_{i:02d}')
            assembly.add(cards)
        return Configuration.explicit(assembly,
            name='closed' if lift_mm == 0 and offset_xy == (0, 0) else 'hood_displaced',
            parameters={'variant': q.__name__, 'hood_lift_mm': lift_mm,
                        'hood_offset_x_mm': offset_xy[0], 'hood_offset_y_mm': offset_xy[1]})

    def print_job(self, component):
        """One component per material/job, preserving the existing print placement."""
        q = self.model
        if component == 'base':
            shape, location = self.base, cq.Location(q.PRINT_CENTRE)
        elif component == 'insert':
            shape = self.insert
            location = cq.Location((q.PRINT_CENTRE[0], q.PRINT_CENTRE[1], -q.FOOT_TOP))
        elif component == 'hood':
            # Q1F uses the retained G hood job; Q1 has its own print-centre rule.
            centre = ((q.g.PRINT_ANCHOR[0]+q.g.HOOD_SHIFT, q.g.PRINT_ANCHOR[1], 0)
                      if q is default_model else q.PRINT_CENTRE)
            shape, location = q.g.hood_print(cq.Workplane().newObject([self.hood])).val(), cq.Location(centre)
        else:
            raise ValueError(f'Unknown printable component: {component}')
        return Configuration.explicit(cq.Assembly(name='quiet_print').add(
            shape, name=component, loc=location), name=f'print_{component}', kind='print')

    def neighbour(self, name):
        q = self.model
        if name == 'new':
            return self.base, q.FOOT_Y, self.hood
        if name not in self._neighbours:
            if name == 'archive_A':
                base = old_archive.base('continuous').val()
            elif name == 'display_J4':
                base = old_display.base().val()
            else:
                raise ValueError(f'Unknown neighbour: {name}')
            self._neighbours[name] = base, q.g.FOOT_DEPTH, q.g.cap().val()
        return self._neighbours[name]

    def joined(self, neighbour='archive_A', *, end=1):
        """Butted feet on a Y seam at zero; actual I3 key remains at the seam.

        Explicit hierarchy preserves new/old identities, including both hoods.
        Key-head overlap with base capture flanks is intentional.
        """
        if end not in (-1, 1):
            raise ValueError('Joining end must be -1 or 1')
        q = self.model
        other, depth, cover = self.neighbour(neighbour)
        new = (cq.Assembly(name='new').add(self.base, name='base')
               .add(self.insert, name='insert').add(self.hood, name='hood'))
        adjacent = cq.Assembly(name='neighbour').add(other, name='base').add(cover, name='hood')
        row = (cq.Assembly(name='quiet_row')
               .add(new, loc=cq.Location((0, -end*q.FOOT_Y/2, 0)))
               .add(adjacent, loc=cq.Location((0, end*depth/2, 0)))
               .add(q.keys.seated_key(3), name='key'))
        return Configuration.explicit(row, name=f'joined_{neighbour}_{end:+d}',
            parameters={'neighbour': neighbour, 'joining_end': end, 'seam_gap_mm': 0})

    def inspection(self):
        """Same mixed-row/open-box/detached-insert arrangement as the old view."""
        scene = cq.Assembly(name='quiet_inspection')
        q = self.model
        scene.add(self.joined('archive_A', end=-1).assembly(), name='mixed_row')
        opened = cq.Assembly(name='open_box').add(self.base, name='base').add(self.insert, name='insert')
        for i in range(0, len(self.cards), 7):
            opened.add(self.cards[i], name=f'card_{i:02d}')
        scene.add(opened, loc=cq.Location((90, 0, 0)))
        scene.add(self.insert, name='detached_insert', loc=cq.Location((165, 0, -q.FOOT_TOP)))
        return Configuration.explicit(scene, name='mixed_row_open_and_detached', kind='intermediate')
