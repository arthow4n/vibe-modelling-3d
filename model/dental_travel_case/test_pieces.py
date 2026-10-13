"""Optional combined production mechanism and handle-fit tests."""
from design import build
from samples import samples
result = samples(build())["test_pieces"]
