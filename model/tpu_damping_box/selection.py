"""Current quietness-priority print selection; historical A–F stays available."""
SELECTED_NAMES = ('A', 'E', 'H', 'I')


def selected_layout():
    from design import liner_layout
    return liner_layout(SELECTED_NAMES, columns=2)
