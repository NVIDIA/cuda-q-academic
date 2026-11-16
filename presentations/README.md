# Presentations

Extra HTML materials used in talks and presentations, separate from the official
Visualization Gallery widgets. Keep them out of `visualization-gallery.html`,
`curriculum.json`, and the `interactive_widgets` directory.

Open `index.html` for the presentation list. With the `widgets-as-html` branch
published at the existing CUDA-Q Academic site, the public paths are:

- `/cuda-q-academic/presentations/`
- `/cuda-q-academic/presentations/quantum-computing-basics.html`
- `/cuda-q-academic/presentations/bernstein-vazirani-classical-versus-quantum.html`

These are static pages and need no build step. Quantum Computing Basics uses
Three.js 0.160.0 and OrbitControls from jsDelivr and requires WebGL. Both
presentations load Google Fonts and provide system font fallbacks. They contain
no analytics or application data submission code; the external providers receive
ordinary browser requests when their resources load.

## Publication review (2026-11-16)

- PASS: reviewed both supplied HTML sources, including inline JavaScript, for
  credentials, private data, internal links, embedded files, tracking, and data
  submission. No sensitive material found. The Bernstein–Vazirani `secret` is
  the educational algorithm input.
- PASS: Chromium checks for initialization, tab and keyboard navigation, qubit
  measurement, interference, correlated shots, classical candidate elimination
  at lengths 2–4, quantum steps, the illustrative noise toggle, and Escape reset.
  No JavaScript errors observed. Outbound requests were GET requests to Google
  Fonts and jsDelivr only.
- PASS (source inspection): existing presentation styles include shared colors,
  instructions, skip links, green focus outlines, slider labels, SVG circuit
  classes, live status regions, and reduced motion support. This is not a full
  accessibility certification; comprehensive contrast and screen reader testing
  are NOT VERIFIED.
- NEEDS WORK: the supplied Basics layout overflows at a 390 px viewport on the
  Two qubits and Entanglement tabs. The presentation index and Bernstein–Vazirani
  page passed the same overflow check.

Import changes are limited to presentation footer navigation and correcting the
Bernstein–Vazirani Escape reset so the selected step matches the reset diagram.
The official gallery and curriculum catalog are unchanged.
