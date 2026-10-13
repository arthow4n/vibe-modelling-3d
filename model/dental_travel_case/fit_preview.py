"""Open loaded inspection with measured-item proxies; never print the proxies."""
from design import build
from components import compound
from reference_items import reference_items
result = compound(build()["opened"], *reference_items().values())
