# Portfolio maintenance

Preserve the established Webflow appearance. Do not introduce a redesign, generated imagery, new typography, or a framework without the user's request.

Edit source files in site/. Never hand-edit generated dist/.
Run python scripts/build.py after changes. Inspect migration-audit.json for missing references and the publication size budget.
Keep media on the homepage and its featured project pages at original quality; archive image optimization belongs in the build, leaving source recoverable.
Do not change DNS, cancel Webflow, or publish a new GitHub repository unless requested. The local Pages workflow is prepared for a future deployment.
