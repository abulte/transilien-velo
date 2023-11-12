# transilien-velo

This uses [the Navitia API](https://navitia.io) to compute itineraries in Ile-de-France while travelling with a bike.

Typical use case: I go from my home to the nearest Transilien station via bike, take the train to Paris with my bike and then do the last on the bike.

This is done by tweaking with allowed transportation modes and first and last modes for a journey.

Currently, the Navitia API does not seem to support a last leg via bike, so we're using bike sharing as a fallback.
